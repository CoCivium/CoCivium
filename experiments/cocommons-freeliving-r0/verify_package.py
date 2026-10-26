#!/usr/bin/env python3
"""Verify packaged source bytes against their included public manifest."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
expected={row['path']:row for row in manifest['files']}
actual={str(p.relative_to(ROOT)).replace('\\','/') for p in ROOT.rglob('*') if p.is_file() and p.name!='PACKAGE_MANIFEST.json' and '__pycache__' not in p.parts}
assert actual==set(expected), f'MANIFEST_SET_MISMATCH added={actual-set(expected)} missing={set(expected)-actual}'
for name,row in expected.items():
    data=(ROOT/name).read_bytes()
    assert len(data)==row['bytes'], 'WRONG_LENGTH '+name
    assert hashlib.sha256(data).hexdigest()==row['sha256'], 'WRONG_HASH '+name
print('PASS',len(expected),'packaged source hashes; does not prove recipient adoption')
