#!/usr/bin/env python3
"""Verify local Git blob identities of adopted public sources; never fetch URLs.

This validates an exact checkout for a read-only R0 source edition. It does not
validate source truth, rights, recipient uptake, or model-weight changes.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_MANIFEST_BLOB = 'e9b834f93455012c703eeb8ba9b6585778ea3464'


def blob_sha1(data):
    return hashlib.sha1(('blob %s\0' % len(data)).encode() + data).hexdigest()


def verify(manifest_bytes, repo_root, expected_manifest_blob):
    if blob_sha1(manifest_bytes) != expected_manifest_blob:
        raise ValueError('MANIFEST_BLOB_MISMATCH')
    manifest = json.loads(manifest_bytes)
    if manifest.get('source_repo') != 'CoCivium/CoCivium':
        raise ValueError('SOURCE_REPO_MISMATCH')
    sources = manifest.get('source_index')
    if not isinstance(sources, list) or len(sources) != manifest.get('source_paths_count'):
        raise ValueError('MALFORMED_SOURCE_LIST')
    repo = Path(repo_root).resolve()
    details = []
    seen = set()
    for source in sources:
        path = source.get('path')
        if not isinstance(path, str) or not path or path.startswith('/') or '..' in path.split('/'):
            raise ValueError('UNSAFE_SOURCE_PATH')
        if path in seen:
            raise ValueError('DUPLICATE_SOURCE_PATH')
        seen.add(path)
        expected = source.get('git_blob_sha1', '')
        if not isinstance(expected, str) or len(expected) != 40 or any(c not in '0123456789abcdef' for c in expected):
            raise ValueError('INVALID_SOURCE_HASH')
        p = (repo / path).resolve()
        if not p.is_relative_to(repo):
            raise ValueError('SOURCE_ESCAPES_CHECKOUT')
        if not p.is_file():
            raise ValueError('SOURCE_FILE_MISSING:' + path)
        actual = blob_sha1(p.read_bytes())
        if actual != expected:
            raise ValueError('SOURCE_BLOB_MISMATCH:' + path)
        details.append({'id': source.get('id'), 'path': path, 'git_blob_sha1': actual, 'matched': True})
    return {'state':'SOURCE_CHECKOUT_BLOBS_MATCH_PINNED_EDITION_ONLY',
            'manifest_git_blob_sha1': expected_manifest_blob,
            'sources_count':len(details), 'source_checks': details,
            'external_receiver_ack':'NOT_OBSERVED','model_training':'NOT_OBSERVED',
            'runtime_effects':0}


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--manifest', required=True)
    a.add_argument('--repo-root', required=True)
    a.add_argument('--expected-manifest-git-blob', default=EXPECTED_MANIFEST_BLOB)
    a.add_argument('--output', required=True)
    args=a.parse_args()
    try:
        result=verify(Path(args.manifest).read_bytes(), args.repo_root, args.expected_manifest_git_blob)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as e:
        print(json.dumps({'state':'HOLD_SOURCE_PIN_FAILURE', 'reason':str(e)}))
        return 2
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'state':result['state'],'count':result['sources_count']}))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
