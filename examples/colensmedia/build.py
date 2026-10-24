#!/usr/bin/env python3
"""Deterministic offline CoLens R0 builder; no network or device effects."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def load():
    return json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))

def build():
    template = (HERE / 'template.html').read_text(encoding='utf-8')
    assert template.count('__MANIFEST_JSON__') == 1
    obj = load()
    data = json.dumps(obj, separators=(',', ':'), sort_keys=True, ensure_ascii=True)
    return template.replace('__MANIFEST_JSON__', data + '\n')

def donor_verification(root):
    checks=[]
    for entry in load()['public_donors']:
        p = root / entry['path']
        if not p.is_file():
            checks.append((entry['path'],'MISSING_FILE'))
            continue
        blob=p.read_bytes()
        observed=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
        checks.append((entry['path'],'MATCH' if observed==entry['git_blob'] else 'DRIFT'))
    return checks

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--check',action='store_true')
    p.add_argument('--check-donors',action='store_true')
    p.add_argument('--repo-root',default=str(HERE.parents[1]))
    args=p.parse_args()
    out=build().encode('utf-8')
    file=HERE/'index.html'
    if args.check:
        if not file.exists() or file.read_bytes()!=out: raise SystemExit('FAIL: generated HTML differs from current typed manifest')
        print('PASS: HTML bytes match manifest-backed deterministic renderer',hashlib.sha256(out).hexdigest())
    else:
        file.write_bytes(out)
        print('WRITTEN: manifest-backed HTML',hashlib.sha256(out).hexdigest())
    if args.check_donors:
        result=donor_verification(Path(args.repo_root))
        for name,status in result: print('DONOR:',status,name)
        if not all(status=='MATCH' for _,status in result): raise SystemExit('HOLD: named public donor changed or missing; requires review')
        print('PASS: 4 public donor exact Git blob identities match')

if __name__=='__main__': main()
