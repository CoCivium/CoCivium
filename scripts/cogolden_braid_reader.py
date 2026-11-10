#!/usr/bin/env python3
"""Read-only CoGolden public contract reader. Python standard library only."""
import argparse
import hashlib
import json
import sys
import urllib.request

ROOT = "https://raw.githubusercontent.com/CoCivium/CoCivium/main/"
CONTRACT = "docs/Evolution/COGOLDEN_BRAID_FRONT_CONTINUITY_R0.json"
EXPECTED_BLOB = "a740aedef136103e1f24345d119ae92dee3c4979"
REQUIRED = ("front_identity", "golden_thread", "braid", "fray", "continuity", "tests")

def blob_sha(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()

def check(payload, expected=EXPECTED_BLOB):
    actual = blob_sha(payload)
    result = {"schema": "cocivium.cogolden_braid.reader_receipt.r0",
              "source": CONTRACT, "expected_blob_sha": expected,
              "observed_blob_sha": actual, "sha_match": actual == expected,
              "passed": False, "claim_scope": "public_contract_readback_only"}
    if actual != expected:
        result["hold_reason"] = "contract_hash_mismatch"
        return result
    try:
        doc = json.loads(payload)
        result["schema_match"] = doc.get("schema") == "cocivium.cogolden_braid.front_continuity.r0"
        result["required_sections_present"] = all(k in doc for k in REQUIRED)
        result["no_runtime_claim"] = "NOT_AUTONOMOUS_RUNTIME" in doc.get("status", "")
        result["passed"] = all((result["schema_match"], result["required_sections_present"],
                                result["no_runtime_claim"]))
        if not result["passed"]:
            result["hold_reason"] = "contract_structure_or_status_invalid"
    except (ValueError, TypeError) as exc:
        result["hold_reason"] = "invalid_json: " + str(exc)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="local contract file; otherwise read public GitHub")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    try:
        if args.input:
            with open(args.input, "rb") as fh:
                payload = fh.read()
        else:
            with urllib.request.urlopen(ROOT + CONTRACT, timeout=20) as response:
                payload = response.read()
        receipt = check(payload)
    except (OSError, ValueError) as exc:
        receipt = {"schema": "cocivium.cogolden_braid.reader_receipt.r0",
                   "passed": False, "hold_reason": "fetch_failed: " + str(exc)}
    output = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output == "-":
        print(output, end="")
    else:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
    return 0 if receipt["passed"] else 2

if __name__ == "__main__":
    sys.exit(main())
