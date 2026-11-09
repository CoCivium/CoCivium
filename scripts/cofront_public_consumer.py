#!/usr/bin/env python3
"""CoFront public source verifier. Read-only; Python standard library."""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request

RAW = "https://raw.githubusercontent.com/CoCivium/CoCivium/main/"
MANIFEST = "docs/Evolution/COPREGENERIC_SESSION_POINTERS_R0.json"

def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()

def verify(manifest, fetch):
    receipts = []
    for item in manifest["source_refs"]:
        path = item["path"]
        expected = item["blob_sha"]
        if not path.startswith(("docs/Evolution/", "scripts/")) or ".." in path or path.startswith("/"):
            raise ValueError("unsafe path: " + path)
        data = fetch(path)
        actual = git_blob_sha(data)
        receipts.append({"id": item["id"], "path": path, "expected_git_blob_sha": expected,
                         "observed_git_blob_sha": actual, "matched": actual == expected,
                         "bytes": len(data)})
    return {"schema": "cocivium.cofront.public_ingestion_receipt.r0",
            "source_manifest": MANIFEST, "sources": receipts,
            "passed": bool(receipts) and all(x["matched"] for x in receipts),
            "claim_scope": "read_only_public_source_identity_check_not_runtime_adoption"}

def remote_fetch(path):
    with urllib.request.urlopen(RAW + path, timeout=20) as response:
        return response.read()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    try:
        manifest_bytes = remote_fetch(args.manifest)
        manifest = json.loads(manifest_bytes)
        result = verify(manifest, remote_fetch)
        result["manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
        payload = json.dumps(result, sort_keys=True, indent=2) + "\\n"
        if args.output == "-":
            print(payload, end="")
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(payload)
        return 0 if result["passed"] else 2
    except (ValueError, KeyError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print("HOLD: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
