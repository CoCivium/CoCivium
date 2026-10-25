#!/usr/bin/env python3
"""CoOmni Context Compiler R0: offline, public-only, source-verified demonstration.

No network, subprocesses, writes, authentication, model calls, or device control.
Actual security decisions must happen outside this candidate compiler.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = 'CoAll.ContextSources.R0'
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_RECORDS = 128
MAX_TEXT_CHARS = 65536
ALLOWED_ROLES = {'SOURCE', 'CHALLENGE', 'BASELINE'}
ALLOWED_VISIBILITY = {'PUBLIC', 'LOCAL_ONLY', 'RESTRICTED'}
ALLOWED_EPISTEMIC = {'OBSERVED', 'MEASURED', 'INFERRED', 'HYPOTHESIS', 'SIMULATION', 'METAPHOR', 'UNKNOWN'}
ID_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,63}$')


def canonical_json(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def source_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def words(value):
    return set(re.findall(r'[a-z0-9]{3,}', str(value).lower()))


def validate_snapshot(snapshot):
    if type(snapshot) is not dict or snapshot.get('schema') != SCHEMA:
        raise ValueError('INVALID_SCHEMA')
    if not isinstance(snapshot.get('work_id'), str) or not ID_RE.fullmatch(snapshot['work_id']):
        raise ValueError('INVALID_WORK_ID')
    if not isinstance(snapshot.get('intent'), str) or not (1 <= len(snapshot['intent']) <= 500):
        raise ValueError('INVALID_INTENT')
    source_records = snapshot.get('sources')
    if type(source_records) is not list or not (1 <= len(source_records) <= MAX_RECORDS):
        raise ValueError('INVALID_SOURCE_SET')
    used_ids = set()
    for src in source_records:
        if type(src) is not dict:
            raise ValueError('INVALID_SOURCE_OBJECT')
        sid = src.get('id')
        if not isinstance(sid, str) or not ID_RE.fullmatch(sid) or sid in used_ids:
            raise ValueError('DUPLICATE_OR_INVALID_ID')
        used_ids.add(sid)
        if src.get('visibility') not in ALLOWED_VISIBILITY:
            raise ValueError('UNKNOWN_VISIBILITY_FAIL_CLOSED')
        if src.get('role') not in ALLOWED_ROLES:
            raise ValueError('UNKNOWN_ROLE_FAIL_CLOSED')
        if src.get('epistemic') not in ALLOWED_EPISTEMIC:
            raise ValueError('UNKNOWN_EPISTEMIC_FAIL_CLOSED')
        body = src.get('text')
        if not isinstance(body, str) or len(body) > MAX_TEXT_CHARS:
            raise ValueError('INVALID_SOURCE_TEXT')
        if src.get('sha256') != source_sha(body):
            raise ValueError('SOURCE_DIGEST_MISMATCH')
    return source_records


def short_entry(src, intent):
    raw = src['text']
    needle = words(intent)
    hay = words(raw[:4096])
    relevance = len(needle & hay)
    return {
        'id': src['id'],
        'sha256': src['sha256'],
        'role': src['role'],
        'epistemic': src['epistemic'],
        'excerpt': raw[:160],
        'truncated': len(raw) > 160,
        'excerpt_is_not_full_source': True,
        '_relevance': relevance,
    }


def compile_packet(snapshot, max_bytes=2400):
    """Finite public packet; no restricted source titles or bytes are exposed."""
    if type(max_bytes) is not int or not (600 <= max_bytes <= 100000):
        raise ValueError('INVALID_BYTE_BUDGET')
    records = validate_snapshot(snapshot)
    public = [x for x in records if x['visibility'] == 'PUBLIC']
    private_count = len(records) - len(public)
    ranked = [short_entry(s, snapshot['intent']) for s in public]
    ranked.sort(key=lambda x: (x['role'] != 'CHALLENGE', x['role'] != 'SOURCE', -x['_relevance'], x['id']))
    for x in ranked:
        del x['_relevance']
    candidate = {
        'schema': 'CoAll.CompiledContext.R0',
        'work_id': snapshot['work_id'],
        'intent': snapshot['intent'],
        'scope': 'PUBLIC_ONLY_NO_EXTERNAL_EFFECTS',
        'status': 'HELD',
        'missing': [],
        'sources': [],
        'omitted_public': len(ranked),
        'withheld_nonpublic': private_count,
        'notes': ['Source digests identify UTF-8 bytes of text, not truth.', 'Excerpts are not full originals.'],
        'nonclaims': ['COMPILATION_NE_SEMANTIC_VALIDATION', 'PACKET_NE_INFINITE_CONTEXT', 'SOURCE_POINTER_NE_RECEIVER_ACK'],
    }
    if not any(x['role'] == 'CHALLENGE' for x in ranked):
        candidate['missing'].append('NO_PUBLIC_CHALLENGE')
    if not any(x['role'] == 'SOURCE' for x in ranked):
        candidate['missing'].append('NO_PUBLIC_SOURCE')
    must = [next((x for x in ranked if x['role'] == role), None) for role in ('CHALLENGE', 'SOURCE')]
    must = [x for x in must if x is not None]
    def length(packet):
        return len(canonical_json(packet))
    if length(candidate) > max_bytes:
        raise ValueError('PACKET_OVERHEAD_EXCEEDS_BUDGET')
    # The first source and first challenge are mandatory when visible. Fail closed on too-small budget.
    for src in must:
        candidate['sources'].append(src)
        candidate['omitted_public'] -= 1
        if length(candidate) > max_bytes:
            candidate['sources'].pop()
            candidate['omitted_public'] += 1
            candidate['missing'].append('BUDGET_CANNOT_PRESERVE_CORE_AND_CHALLENGE')
            candidate['status'] = 'HELD'
            return candidate
    used = {s['id'] for s in candidate['sources']}
    for src in ranked:
        if src['id'] in used:
            continue
        candidate['sources'].append(src)
        candidate['omitted_public'] -= 1
        if length(candidate) > max_bytes:
            candidate['sources'].pop()
            candidate['omitted_public'] += 1
        else:
            used.add(src['id'])
    candidate['status'] = 'PASS_BOUNDED' if not candidate['missing'] else 'HELD'
    return candidate


def rehydrate_public(snapshot, source_id, expected_sha):
    """Exact source recovery from the same supplied snapshot, not durable independent custody."""
    records = validate_snapshot(snapshot)
    if not isinstance(source_id, str) or not isinstance(expected_sha, str):
        raise ValueError('INVALID_REHYDRATION_REQUEST')
    for src in records:
        if src['id'] == source_id:
            if src['visibility'] != 'PUBLIC':
                raise PermissionError('NONPUBLIC_SOURCE_NOT_REHYDRATABLE')
            if src['sha256'] != expected_sha:
                raise ValueError('STALE_DIGEST')
            return src['text']
    raise KeyError('SOURCE_NOT_IN_SNAPSHOT')


def main():
    p = argparse.ArgumentParser(description='Offline public-only CoOmni context compiler')
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--budget-bytes', type=int, default=2400)
    args = p.parse_args()
    if args.input.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError('INPUT_TOO_LARGE')
    doc = json.loads(args.input.read_text(encoding='utf-8'))
    packet = compile_packet(doc, args.budget_bytes)
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if packet['status'] == 'PASS_BOUNDED' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, PermissionError, KeyError, OSError, json.JSONDecodeError) as exc:
        print('HELD: ' + str(exc), file=sys.stderr)
        sys.exit(2)
