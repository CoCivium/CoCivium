#!/usr/bin/env python3
"""CoAll R0: a zero-dependency, read-only, exact-source retrieval adapter.

No network, model calls, writes to sources, authority changes, or training.
Retrieved text is untrusted data, never instructions.
"""
import argparse
import hashlib
import json
import math
import pathlib
import re
import statistics
import sys
import time
from collections import Counter

DEFAULT_MANIFEST_PIN = 'e9b834f93455012c703eeb8ba9b6585778ea3464'
ALLOWED_REPO = 'CoCivium/CoCivium'
ALLOWED_PUBLIC_URL = 'https://github.com/CoCivium/CoCivium/blob/main/'
WORD_RE = re.compile(r"[a-z][a-z0-9+_/-]{1,}", re.I)
STOP = frozenset('the and for with from that this those their into where what how which does can you our its are was were has have without not one all these why who when where who the is an of to in by on as or be it at a if do from we me your'.split())
BLOCKED_FETCH_POLICY = 'PUBLIC_READ_ONLY_CANDIDATE_NOT_GLOBAL_ADOPTION'
MAX_FILE_BYTES = 350_000
MAX_CHUNKS = 6000


class Refuse(RuntimeError):
    """A hard source/authority gate refused the projection."""


def gitblob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def checked_root(root):
    base = pathlib.Path(root).resolve(strict=True)
    if not base.is_dir():
        raise Refuse('NOT_A_REPOSITORY_DIR')
    return base


def verify_manifest(manifest, expected_pin=DEFAULT_MANIFEST_PIN):
    raw = pathlib.Path(manifest).read_bytes()
    if not re.fullmatch(r'[0-9a-f]{40}', expected_pin or ''):
        raise Refuse('MISSING_TRUSTED_MANIFEST_PIN')
    if gitblob(raw) != expected_pin:
        raise Refuse('MANIFEST_EDITION_MISMATCH')
    obj = json.loads(raw)
    if obj.get('source_repo') != ALLOWED_REPO or obj.get('state') != BLOCKED_FETCH_POLICY:
        raise Refuse('MANIFEST_AUTHORITY_STATE_MISMATCH')
    if obj.get('authorized_effects_from_this_manifest') != []:
        raise Refuse('EFFECT_AUTHORITY_REQUESTED')
    cu = obj.get('content_use', {})
    if cu.get('training') != 'NOT_GRANTED_BY_THIS_MANIFEST' or cu.get('fine_tuning') != 'NOT_GRANTED_BY_THIS_MANIFEST':
        raise Refuse('TRAINING_RIGHT_UNVERIFIED')
    iface = obj.get('agent_interface', {})
    if any(iface.get(k) != 'NOT_DEPLOYED' for k in ('mcp_resources', 'mcp_tools', 'a2a_agent_card')):
        raise Refuse('INVENTED_AGENT_ENDPOINT')
    if iface.get('endpoint_urls') != [] or obj.get('default_verified_receiver_ladder') != 'DISCOVERABLE_SOURCE_ONLY_NOT_REMOTE_RECEIVER_PICKUP':
        raise Refuse('UNVERIFIED_AGENT_REACH')
    sources = obj.get('source_index', [])
    if len(sources) != obj.get('source_paths_count') or not sources:
        raise Refuse('SOURCE_COUNT_MISMATCH')
    ids, paths = set(), set()
    for source in sources:
        sid, path, url = source.get('id'), source.get('path'), source.get('url')
        if not isinstance(sid, str) or not sid or sid in ids:
            raise Refuse('DUPLICATE_OR_EMPTY_ID')
        if not isinstance(path, str) or not path or '\\' in path or path.startswith('/'):
            raise Refuse('UNSAFE_SOURCE_PATH')
        if any(p in ('.', '..', '') for p in path.split('/')) or path in paths:
            raise Refuse('DUPLICATE_OR_TRAVERSING_PATH')
        if url != ALLOWED_PUBLIC_URL + path:
            raise Refuse('UNEXPECTED_SOURCE_URL')
        if not re.fullmatch(r'[0-9a-f]{40}', source.get('git_blob_sha1') or ''):
            raise Refuse('BAD_SOURCE_PIN')
        ids.add(sid); paths.add(path)
    return obj


def read_pinned_sources(manifest, root):
    base = checked_root(root)
    sources = []
    for entry in manifest['source_index']:
        rel = pathlib.PurePosixPath(entry['path'])
        target = base.joinpath(*rel.parts)
        try:
            resolved = target.resolve(strict=True)
        except (FileNotFoundError, OSError):
            raise Refuse('PINNED_SOURCE_MISSING:' + entry['id'])
        if not resolved.is_relative_to(base) or target.is_symlink():
            raise Refuse('SOURCE_PATH_ESCAPES_ROOT:' + entry['id'])
        if not resolved.is_file() or resolved.stat().st_size > MAX_FILE_BYTES:
            raise Refuse('SOURCE_NOT_REGULAR_OR_TOO_LARGE:' + entry['id'])
        raw = resolved.read_bytes()
        if gitblob(raw) != entry['git_blob_sha1']:
            raise Refuse('SOURCE_BLOB_CHANGED_HOLD:' + entry['id'])
        try:
            txt = raw.decode('utf-8')
        except UnicodeDecodeError:
            raise Refuse('SOURCE_NOT_UTF8:' + entry['id'])
        sources.append({'entry': entry, 'text': txt})
    return sources


def tokens(s):
    return [m.group(0).lower() for m in WORD_RE.finditer(s) if m.group(0).lower() not in STOP]


def chunks_from_source(source, width=16):
    """Chunk source by original numbered lines; preserve exact byte lineage.

    Stable line windows deliberately don't pretend to parse all claim semantics.
    """
    entry, txt = source['entry'], source['text']
    lines = txt.splitlines()
    if not lines:
        return []
    out = []
    for pos in range(0, len(lines), width):
        excerpt = '\n'.join(lines[pos:pos+width])
        if not excerpt.strip():
            continue
        start, end = pos+1, min(pos+width, len(lines))
        out.append({'source_id':entry['id'],'path':entry['path'],'source_url':entry['url'],
                    'git_blob_sha1':entry['git_blob_sha1'], 'source_state':entry['source_state'],
                    'line_start':start,'line_end':end,
                    'citation':f'{entry["path"]}#L{start}-L{end}', 'text':excerpt})
    return out


def index_source(manifest, root):
    sources = read_pinned_sources(manifest, root)
    chunks = [c for source in sources for c in chunks_from_source(source)]
    if len(chunks) > MAX_CHUNKS:
        raise Refuse('CHUNK_BUDGET_EXCEEDED')
    counters = [Counter(tokens(c['text'])) for c in chunks]
    doc_freq = Counter()
    for counter in counters:
        doc_freq.update(counter.keys())
    lengths = [sum(c.values()) for c in counters]
    return {'chunks':chunks,'counters':counters,'doc_freq':doc_freq,
            'avg_len':(sum(lengths)/len(lengths) if lengths else 1),
            'lengths':lengths,'sources':sources}


def search(index, query, top_k=5):
    if not isinstance(query, str) or len(query) > 500 or not query.strip():
        raise Refuse('INVALID_QUERY')
    if type(top_k) is not int or not 1 <= top_k <= 10:
        raise Refuse('INVALID_TOP_K')
    query_words = tokens(query)
    if not query_words:
        raise Refuse('NO_SEARCHABLE_TERMS')
    N = len(index['chunks'])
    k1, b = 1.5, .75
    results=[]
    for i,(chunk,count,doclen) in enumerate(zip(index['chunks'],index['counters'],index['lengths'])):
        score = 0.0
        for w in set(query_words):
            f = count.get(w, 0)
            if f:
                df=index['doc_freq'][w]
                idf=math.log(1 + (N-df+.5)/(df+.5))
                score += idf * (f*(k1+1))/(f+k1*(1-b+b*doclen/index['avg_len']))
        if score>0:
            # A match in a whole pinned source gets the exact line range, not fabricated fact status.
            results.append((score,i,chunk))
    results.sort(key=lambda r:(-r[0],r[2]['path'],r[2]['line_start']))
    matches=[]
    for score,i,c in results[:top_k]:
        m=dict(c); m['rank_score_lexical_only']=round(score,6)
        # No generated instructions or grant. Always keep claim and authority classes explicit.
        matches.append(m)
    return {'schema':'CoAll.SourcePinnedRetrieval.R0',
            'state':'SOURCE_PINNED_LEXICAL_RETRIEVAL_ONLY_NOT_MODEL_LEARNING',
            'source_edition_verified':True, 'retrieval_method':'BM25_STYLE_STDLIB_LEXICAL',
            'query':query, 'result_count':len(matches),'results':matches,
            'content_trust':'UNTRUSTED_SOURCE_DATA_NOT_AGENT_INSTRUCTIONS',
            'authorized_effects':[], 'training_rights':'NOT_GRANTED_BY_DISCOVERY_MANIFEST',
            'receiver_ack':'NOT_OBSERVED', 'model_invoked':False,
            'nonclaims':['RETRIEVAL_NE_COMPREHENSION','CITATION_NE_TRUTH','SEARCH_RANK_NE_AUTHORITY','INDEXED_NE_TRAINED']}


def cli(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True)
    p.add_argument('--repo-root',required=True)
    p.add_argument('--manifest-pin',default=DEFAULT_MANIFEST_PIN)
    p.add_argument('--query',required=True)
    p.add_argument('--top-k',type=int,default=5)
    p.add_argument('--output')
    a=p.parse_args(argv)
    try:
        manifest=verify_manifest(a.manifest,a.manifest_pin)
        idx=index_source(manifest,a.repo_root)
        result=search(idx,a.query,a.top_k)
        result['source_count']=len(idx['sources']);result['indexed_chunk_count']=len(idx['chunks'])
        result['manifest_git_blob_sha1']=a.manifest_pin
        output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if a.output: pathlib.Path(a.output).write_text(output,encoding='utf-8')
        else: print(output,end='')
    except (Refuse,ValueError,KeyError,TypeError,UnicodeError) as e:
        print(json.dumps({'state':'HOLD','reason':str(e),'authorized_effects':[]}),file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(cli())
