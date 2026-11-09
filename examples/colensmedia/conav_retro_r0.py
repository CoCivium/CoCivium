#!/usr/bin/env python3
"""CoNav retro-public media index, source-only graph of diagrams.

Bounded public repository pointers; no media-byte harvesting, account access,
mail sending, browser control or cross-session broadcast. Private captures are
never accepted for publication by this tool.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote

SCHEMA = 'CoAll.CoNavRetroMedia.R0'
GROUPS = {'CoMap': 'Maps and relational diagrams',
          'CoMedia': 'Media and interactive views',
          'CoLUE': 'Outreach views and drafts'}
KINDS = {'DIAGRAM', 'INTERACTIVE_VIEW', 'SOURCE_LINK_VIEW', 'OUTREACH_DEMO'}
ID = re.compile(r'[A-Za-z0-9_.:-]{1,96}\Z')
BLOB = re.compile(r'[0-9a-f]{40}\Z')
LABEL = re.compile(r'[A-Za-z0-9 ()+.,:/_-]{1,80}\Z')
PATH = re.compile(r'[A-Za-z0-9_./-]{1,240}\Z')


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def read_manifest(path):
    x = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(x, dict) or x.get('schema') != SCHEMA:
        raise ValueError('INVALID_MANIFEST_SCHEMA')
    items = x.get('candidates')
    if not isinstance(items, list) or not 1 <= len(items) <= 40:
        raise ValueError('INVALID_BOUNDED_CANDIDATES')
    seen_ids, seen_paths = set(), set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            'id', 'label', 'group', 'kind', 'source_path', 'git_blob',
            'visibility', 'rights_state', 'status', 'next_gate'}:
            raise ValueError('INVALID_CANDIDATE_FIELDS')
        if not isinstance(item['id'], str) or not ID.fullmatch(item['id']):
            raise ValueError('INVALID_CANDIDATE_ID')
        if not isinstance(item['label'], str) or not LABEL.fullmatch(item['label']):
            raise ValueError('UNSAFE_CANDIDATE_LABEL')
        if item['group'] not in GROUPS or item['kind'] not in KINDS:
            raise ValueError('INVALID_CANDIDATE_CLASS')
        if item['visibility'] != 'PUBLIC_REPO_SOURCE':
            raise ValueError('PRIVATE_CANDIDATE_IN_PUBLIC_EXPORT')
        if item['rights_state'] != 'METADATA_LINK_ONLY' or item['status'] != 'RETRO_INSPIRATION_CANDIDATE_UNREVIEWED':
            raise ValueError('UNAUTHORIZED_MEDIA_PROMOTION')
        if item['next_gate'] != 'HUMAN_OR_AUTHORIZED_SEMANTIC_RIGHTS_REVIEW':
            raise ValueError('MISSING_REVIEW_GATE')
        path = item['source_path']
        if (not isinstance(path, str) or not PATH.fullmatch(path) or '\\' in path or ':' in path or
            path.startswith('/') or any(p in ('', '.', '..') for p in path.split('/')) or
            PurePosixPath(path).is_absolute()):
            raise ValueError('UNSAFE_SOURCE_PATH')
        if not isinstance(item['git_blob'], str) or not BLOB.fullmatch(item['git_blob']):
            raise ValueError('INVALID_BLOB_ID')
        if item['id'] in seen_ids or path in seen_paths:
            raise ValueError('DUPLICATE_RETRO_CANDIDATE')
        seen_ids.add(item['id']); seen_paths.add(path)
    return x


def audit_sources(data, root):
    root = Path(root).resolve()
    bad = []
    for item in data['candidates']:
        target = (root / item['source_path']).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            bad.append((item['id'], 'MISSING_OR_OUTSIDE_REPO'))
        elif git_blob(target.read_bytes()) != item['git_blob']:
            bad.append((item['id'], 'PINNED_SOURCE_BLOB_MISMATCH'))
    return bad


def projection_id(data):
    value = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def render_markdown(data):
    pin = projection_id(data)
    out = ['# CoNav+ Retro Media: diagram of diagrams R0', '',
           '**PUBLIC SOURCE-POINTER CANDIDATES ONLY. No media copied, no receiver ACK.**', '',
           'Projection SHA-256: `' + pin + '`', '',
           '```mermaid', 'flowchart TD',
           '    C["CoAll source navigation"]']
    for i, (name, caption) in enumerate(GROUPS.items()):
        out.extend(['    C --> G' + str(i),
                    '    G' + str(i) + '["' + name + ' / ' + caption + '"]'])
    out.extend(['```', '',
                'Each group below is another small diagram. Open the linked HTML navigator for expandable boxes.', ''])
    for i, (name, caption) in enumerate(GROUPS.items()):
        subset = [x for x in data['candidates'] if x['group'] == name]
        out.extend(['## ' + name + ': ' + caption, '', '```mermaid', 'flowchart TD',
                    '    G["' + name + '"]'])
        for j, item in enumerate(subset):
            out.extend(['    G --> N' + str(j),
                        '    N' + str(j) + '["' + item['label'] + '"]'])
        out.extend(['```', ''])
        for item in subset:
            path = item['source_path']
            url = 'https://github.com/CoCivium/CoCivium/blob/main/' + quote(path, safe='/')
            out.append('- [' + item['label'] + '](' + url + '): `' + path + '`; blob `' +
                       item['git_blob'] + '`; **review pending**, no adopted inspiration claim')
        out.append('')
    out.extend(['## Evidence boundary', '',
                '- These five public-source pointers are a bounded retroactive candidate set, not the complete history.',
                '- A rendered image or email draft is not automatically licensed, consented, semantically adopted, or public.',
                '- Unavailable/private prior media remain in separate restricted custody; not exposed through public graph.',
                '- No server-to-server pickup, X2 installation, media reproduction, or live CoOrb sync is established.', ''])
    return '\n'.join(out)


def render_html(data):
    pin = projection_id(data)
    lines = ['<!doctype html>', '<html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">',
             '<title>CoNav retro source map</title>', '<style>',
             ':root{color-scheme:dark;font-family:system-ui,sans-serif;background:#121a25;color:#e8eff8}',
             'body{max-width:56rem;margin:auto;padding:1.2rem;line-height:1.5}',
             '.node{border:1px solid #5a8aa9;border-radius:12px;padding:1rem;margin:.75rem 0;background:#182435}',
             '.branch{border-left:2px solid #5a8aa9;margin-left:1.25rem;padding-left:1.25rem}',
             'details{padding:.4rem}summary{cursor:pointer;font-weight:700}',
             'a{color:#90deff}a:focus-visible,summary:focus-visible{outline:3px solid #fbd482}',
             'small{display:block;color:#b1c2d4}code{word-wrap:anywhere}',
             '</style></head><body>',
             '<h1>CoNav+: one map, many small diagrams</h1>',
             '<p>' + str(len(data['candidates'])) + ' public source-pointer candidates. Metadata only, no harvested images or email content.</p>',
             '<div class="node"><strong>CoAll source navigation</strong>',
             '<small>Projection SHA-256: <code>' + pin + '</code></small></div>',
             '<div class="branch">']
    for name, caption in GROUPS.items():
        subset = [x for x in data['candidates'] if x['group'] == name]
        lines.append('<details class="node"><summary>' + html.escape(name + ': ' + caption) +
                     ' (' + str(len(subset)) + ')</summary><div class="branch">')
        for item in subset:
            url = 'https://github.com/CoCivium/CoCivium/blob/main/' + quote(item['source_path'], safe='/')
            lines.extend(['<div class="node"><a href="' + html.escape(url, quote=True) + '">' +
                          html.escape(item['label']) + '</a>',
                          '<small>' + html.escape(item['kind']) + ' | RETRO CANDIDATE, NOT ADOPTED</small>',
                          '<small>Source pin: <code>' + item['git_blob'] + '</code></small></div>'])
        lines.append('</div></details>')
    lines.extend(['</div><h2>Evidence and accessibility</h2>',
                  '<p>The boxes are semantic source links, not verified causal or operational connections. Expand or collapse with keyboard or touch.</p>',
                  '<p>New evidence can trigger a versioned candidate review. No automatic media copying, rights assumption, outreach or cross-session broadcast.</p>',
                  '<p>Private retro candidates stay in restricted custody outside this page. An unreviewed candidate does not change the Orb version or another session.</p>',
                  '</body></html>', ''])
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--root', type=Path, default=Path('.'))
    ap.add_argument('--diagram', type=Path, required=True)
    ap.add_argument('--html', type=Path, required=True)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    data = read_manifest(args.manifest)
    errors = audit_sources(data, args.root)
    if errors:
        raise SystemExit('HOLD_PUBLIC_SOURCE_PINS: ' + repr(errors))
    expected = {args.diagram: render_markdown(data), args.html: render_html(data)}
    for path, value in expected.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != value:
                raise SystemExit('HOLD_STALE_CONAV_VIEW: ' + str(path))
        else:
            if path.exists():
                raise SystemExit('HOLD_NO_OVERWRITE: ' + str(path))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding='utf-8')
    print(json.dumps({'status':'PUBLIC_SOURCE_CANDIDATES_ONLY', 'candidates':len(data['candidates']),
                      'source_pins':'MATCHED', 'projection_sha256':projection_id(data),
                      'no_external_effects':True}, sort_keys=True))


if __name__ == '__main__':
    main()
