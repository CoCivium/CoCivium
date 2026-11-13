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

AUTONOMY_RECEIPT = "ai/currentness/cotalkitout-publication-r1-20261112.json"
AUTONOMY_STEM = "CoTalkItOut_Headless_Screenless_Autonomy_R1_20261112"
AUTONOMY_SUFFIXES = (".xlsx", ".csv", "_PUBLIC_README.md", "_MANIFEST.json")
AUTONOMY_MAX_BYTES = 1048576


def verify_autonomy_publication(fetch):
    """Exact receiver-origin public byte readback. Never a semantic/workflow ACK.

    Returns only public paths, hashes, lengths and proof state; no asset bytes.
    The preflight MANIFEST's historical AWAITING_GIT_COMMIT is not a currentness
    claim. Post-landing status comes from the separate pinned publication receipt.
    """
    raw = fetch(AUTONOMY_RECEIPT)
    if not isinstance(raw, bytes) or len(raw) > AUTONOMY_MAX_BYTES:
        raise ValueError("HOLD_AUTONOMY_RECEIPT_SIZE")
    receipt = json.loads(raw)
    if (not isinstance(receipt, dict) or
        receipt.get("schema") != "CoAll.CoTalkItOut.PublicationReadbackReceipt.R1" or
        receipt.get("state") != "LANDED_PUBLIC_GIT_WITH_SAME_PROVIDER_READBACK" or
        receipt.get("version_stem") != AUTONOMY_STEM or
        receipt.get("publication_preflight", {}).get("public_safe_only") is not True or
        receipt.get("lifecycle", {}).get("git_landing") != "LANDED_PUBLIC" or
        receipt.get("lifecycle", {}).get("independently_operated_receiver_pickup") != "NOT_ATTESTED"):
        raise ValueError("HOLD_AUTONOMY_RECEIPT_IDENTITY_OR_PUBLIC_SCOPE")
    expected_paths = tuple("docs/CoLocal/" + AUTONOMY_STEM + s for s in AUTONOMY_SUFFIXES)
    files = receipt.get("public_files")
    if not isinstance(files, list) or len(files) != len(expected_paths):
        raise ValueError("HOLD_AUTONOMY_FILE_COUNT")
    if set((f.get("path") for f in files if isinstance(f, dict))) != set(expected_paths):
        raise ValueError("HOLD_AUTONOMY_SOURCE_PATH_SET")
    checks = []
    for item in files:
        path, n = item["path"], item.get("bytes")
        sha1, sha256 = item.get("git_blob_sha1"), item.get("sha256")
        if (item.get("name") != path.split("/")[-1] or
            type(n) is not int or not 0 < n <= AUTONOMY_MAX_BYTES or
            not isinstance(sha1, str) or not isinstance(sha256, str) or
            len(sha1) != 40 or len(sha256) != 64 or
            any(c not in "0123456789abcdef" for c in sha1+sha256)):
            raise ValueError("HOLD_AUTONOMY_FILE_DESCRIPTOR")
        data = fetch(path)
        if not isinstance(data, bytes) or len(data) > AUTONOMY_MAX_BYTES:
            raise ValueError("HOLD_AUTONOMY_ASSET_SIZE")
        observed_sha256 = hashlib.sha256(data).hexdigest()
        observed_blob = git_blob_sha(data)
        checks.append({
            "path": path, "bytes": len(data),
            "expected_sha256": sha256, "observed_sha256": observed_sha256,
            "expected_git_blob_sha1": sha1, "observed_git_blob_sha1": observed_blob,
            "matched": n == len(data) and sha256 == observed_sha256 and sha1 == observed_blob,
        })
    return {
        "schema": "CoAll.CoTalkItOut.AutonomyPublicReadback.R0",
        "receiver": "CoFront_GitHub_Actions_PUBLIC_CONSUMER",
        "status": "PUBLIC_SOURCE_IDENTITY_READBACK_ONLY",
        "receipt_path": AUTONOMY_RECEIPT,
        "receipt_sha256": hashlib.sha256(raw).hexdigest(),
        "work_id": receipt["work_id"],
        "public_files": checks,
        "passed": len(checks) == len(expected_paths) and all(c["matched"] for c in checks),
        "private_data_accessed": False,
        "semantic_workbook_reviewed": False,
        "native_x2_runtime": False,
        "independent_costead_receiver_ack": False,
        "interactive_sessions_notified": False,
        "coex_or_canon": False,
    }


def remote_fetch_bounded(path):
    """Only the explicitly pinned publication bundle and receipt are eligible."""
    allowed = {"docs/CoLocal/" + AUTONOMY_STEM + s for s in AUTONOMY_SUFFIXES}
    allowed.add(AUTONOMY_RECEIPT)
    if path not in allowed:
        raise ValueError("HOLD_UNAUTHORIZED_PUBLIC_FETCH")
    req = urllib.request.Request(RAW + path, headers={"User-Agent": "CoFrontPublicConsumer/1.1"})
    with urllib.request.urlopen(req, timeout=20) as response:
        result = response.read(AUTONOMY_MAX_BYTES + 1)
    if len(result) > AUTONOMY_MAX_BYTES:
        raise ValueError("HOLD_REMOTE_PUBLIC_OBJECT_TOO_LARGE")
    return result


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

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
        # Reuse the existing scheduled CoFront consumer as an actual public
        # workbook byte receiver; not a new workflow or X2 process.
        result["cotalkitout_autonomy_publication"] = verify_autonomy_publication(remote_fetch_bounded)
        result["passed"] = bool(result["passed"] and result["cotalkitout_autonomy_publication"]["passed"])
        result["receiver_scope"] = "PUBLIC_GITHUB_ACTIONS_SOURCE_ONLY_NO_EXTERNAL_COSTEAD_ACK"
        payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
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
