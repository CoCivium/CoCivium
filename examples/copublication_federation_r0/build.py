#!/usr/bin/env python3
"""Deterministic no-network build: pinned manifest -> accessible HTML projection."""
from pathlib import Path
import argparse
import json
root = Path(__file__).resolve().parent

def load_manifest():
    return json.loads((root / "manifest.json").read_text(encoding="utf-8"))

def decode_index(index: int, axes: dict) -> dict:
    if type(index) is not int or index < 0 or index >= 10**len(axes):
        raise ValueError("index must be inside the finite addressable space")
    result = {}
    for axis, alternatives in reversed(list(axes.items())):
        if len(alternatives) != 10:
            raise ValueError("all syntactic axes must have 10 choices")
        index, digit = divmod(index, 10)
        result[axis] = alternatives[digit]
    return dict(reversed(list(result.items())))

def validate(m):
    assert m['status'].startswith('STATIC_INTERACTIVE_CANDIDATE')
    assert m['source']['status'] == 'PUBLIC_ARCHITECTURE_CANDIDATE_NOT_RUNTIME'
    assert len(m['source']['git_blob_sha1']) == 40
    assert len(m['routes']) == 6
    assert len(m['claims']) == 6
    assert len({r['id'] for r in m['routes']}) == 6
    assert len({c['id'] for c in m['claims']}) == 6
    assert {c['id'] for c in m['claims']} == set(m['claim_ids_required_in_every_route'])
    for r in m['routes']:
        assert r['claims'] == m['claim_ids_required_in_every_route']
        assert r['action_url'].startswith('https://github.com/CoCivium/CoCivium/')
        assert r['task'] and r['counterpoint']
    assert len(m['logical_axes']) == 12
    assert all(len(v) == 10 and len(set(v)) == 10 for v in m['logical_axes'].values())
    assert 10**len(m['logical_axes']) == int(m['logical_candidate_space'])
    assert [v['id'] for v in m['edition_history']] == ['r0.1', 'r0.2']
    assert m['edition_history'][1]['predecessor'] == 'r0.1'
    assert m['current_edition'] == 'r0.2'
    assert m['actual_substack_posts_created'] == 0 and m['external_sends'] == 0
    assert m['tracking'] is False and m['interest_inference'] is False
    assert m['urgency']['countdowns'] is False and m['urgency']['deliberately_expiring_links'] is False
    assert m['reader_feedback_writeback'] == 'NONE_LOCAL_PREVIEW_ONLY'
    return True

def build(m):
    validate(m)
    data=json.dumps(m,ensure_ascii=True,sort_keys=True,separators=(',',':'))
    data=data.replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')
    template=(root/'template.html').read_text(encoding='utf-8')
    return template.replace('__MANIFEST_JSON__',data)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    output=build(load_manifest())
    p=root/'index.html'
    if args.check:
        if not p.exists() or p.read_text(encoding='utf-8')!=output:
            raise SystemExit('FAIL: generated HTML drift')
        print('PASS: exact deterministic HTML parity')
    else:
        p.write_text(output,encoding='utf-8')
        print('built',p,p.stat().st_size,'bytes')
if __name__ == '__main__':main()
