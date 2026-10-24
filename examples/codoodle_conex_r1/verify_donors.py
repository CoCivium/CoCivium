"""Read-only exact Git blob verification of public source donors in a checkout."""
import argparse
import hashlib
import json
from pathlib import Path


def git_blob(data):
    return hashlib.sha1(("blob %d\0" % len(data)).encode() + data).hexdigest()


def verify_manifest(manifest, root):
    if manifest.get("schema") != "CoDoodle.CoNex.PinnedPublicDonors.R1":
        raise ValueError("HOLD_SCHEMA")
    result = []
    root = root.resolve()
    for ref in manifest.get("donors", []):
        loc = Path(ref["path"])
        if loc.is_absolute() or ".." in loc.parts:
            raise ValueError("HOLD_PATH_ESCAPE")
        dest = root / loc
        if not dest.is_file() or dest.is_symlink() or not dest.resolve().is_relative_to(root):
            raise ValueError("HOLD_MISSING_OR_SYMLINK_SOURCE:" + ref["path"])
        actual = git_blob(dest.read_bytes())
        if actual != ref["git_blob"]:
            raise ValueError("HOLD_DONOR_DRIFT:" + ref["path"])
        result.append({"path": ref["path"], "status": "PASS_EXACT_GIT_BLOB", "git_blob": actual})
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    p.add_argument("--manifest", default=str(Path(__file__).with_name("source_donors.json")))
    a = p.parse_args()
    data = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    result = verify_manifest(data, Path(a.repo_root))
    print(json.dumps({"status": "PASS_DONORS", "count": len(result), "sources": result}))
