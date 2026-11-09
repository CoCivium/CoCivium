#!/usr/bin/env python3
"""Read-only, exact-object CoPre seed/path verifier. A read receipt is not delivery ACK."""
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ALLOWED = re.compile(
    r"^https://raw\.githubusercontent\.com/CoCivium/CoCivium/"
    r"([a-f0-9]{40})/ai/copre-seed-path-handoff-r0-20261109\.json$"
)

def verify_bytes(raw: bytes, expected_git_blob: str, expected_work_id: str):
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if git_blob != expected_git_blob:
        raise ValueError("FAIL_CLOSED_GIT_BLOB_MISMATCH")
    packet = json.loads(raw.decode("utf-8"))
    if not isinstance(packet, dict) or packet.get("work_id") != expected_work_id:
        raise ValueError("FAIL_CLOSED_WORK_ID_MISMATCH")
    if packet.get("state") != "PUBLIC_SAFE_SOURCE_RECORD_NOT_RECEIVER_PICKUP_NOT_INTEGRATION_NOT_CANON":
        raise ValueError("FAIL_CLOSED_PACKET_STATE_MISMATCH")
    if not isinstance(packet.get("paths"), list) or not packet["paths"]:
        raise ValueError("FAIL_CLOSED_MISSING_COPATH")
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_sha": git_blob,
        "work_id": expected_work_id,
        "cop_path_count": len(packet["paths"]),
    }

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-url", required=True)
    p.add_argument("--expected-git-blob", required=True)
    p.add_argument("--expected-work-id", required=True)
    p.add_argument("--reader-id", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)
    if not ALLOWED.fullmatch(args.source_url):
        raise SystemExit("HELD_UNPINNED_OR_UNAPPROVED_SOURCE")
    if not re.fullmatch(r"[a-f0-9]{40}", args.expected_git_blob):
        raise SystemExit("HELD_INVALID_EXPECTED_SHA")
    if not args.reader_id.strip() or not args.expected_work_id.strip():
        raise SystemExit("HELD_MISSING_ID")
    output = Path(args.output)
    if output.exists():
        raise SystemExit("HELD_OUTPUT_EXISTS_NO_CLOBBER")
    req = urllib.request.Request(args.source_url, headers={"User-Agent":"CoPre-Readproof-R0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise SystemExit("HELD_OVERSIZED_SOURCE")
    try:
        result = verify_bytes(raw, args.expected_git_blob, args.expected_work_id)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise SystemExit(str(e)) from e
    record = {
        "schema":"CoPreIndependentReaderR0.candidate",
        "state":"EXACT_SOURCE_READBACK_ONLY_NOT_INDEPENDENT_FAILURE_DOMAIN_PROOF",
        "reader_id":args.reader_id,
        "source_url":args.source_url,
        **result,
        "receiver_disposition":"READ_ONLY_SOURCE_INSPECTION",
        "pickup_state":"NOT_CLAIMED",
        "integration_state":"UNPROVEN",
        "nonclaims":["NO_OTHER_SESSION_ACK","NO_AUTO_SYNC","NO_24H_SURVIVAL_PROOF","NO_COEX"]
    }
    # Exclusive creation prevents overwriting an earlier receipt.
    with output.open("x", encoding="utf-8") as f:
        json.dump(record, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"state":record["state"],"output":str(output),"sha256":result["sha256"]}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
