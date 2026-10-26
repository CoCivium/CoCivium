"""Verify this public demo's package after extraction."""
import hashlib,json
from pathlib import Path
from verify_ledger import verify
ROOT=Path(__file__).resolve().parent

def check():
    manifest=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text())
    for item in manifest['files']:
        path=ROOT/item['path']
        assert path.resolve().is_relative_to(ROOT.resolve()),'ESCAPE_ROOT'
        assert path.is_file(),'MISSING_FILE:'+item['path']
        assert path.stat().st_size==item['bytes'],'WRONG_SIZE:'+item['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],'WRONG_SHA:'+item['path']
    verify(ROOT)
    return len(manifest['files'])

if __name__=='__main__':print('PASS',check(),'content hashes + pinned 13-event ledger')
