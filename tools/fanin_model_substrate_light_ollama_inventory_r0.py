#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    files = sorted(Path(args.input_root).rglob("ollama-inventory-receipt.json"))
    if len(files) != 3:
        fail(f"FAIL_RECEIPT_COUNT:{len(files)}")
    receipts = [json.loads(p.read_text(encoding="utf-8")) for p in files]

    for r in receipts:
        if r["STATE"] != "PASS_LOCAL_OLLAMA_INVENTORY_READBACK":
            fail("FAIL_RECEIVER_STATE")
        if r["effect_executions"] != 0:
            fail("FAIL_EFFECT_EXECUTED")
        if r["model_selection_state"] != "UNBOUND_REQUIRES_EXACT_NAME_AND_DIGEST_SELECTION":
            fail("FAIL_SELECTION_STATE")

    invariant_fields = [
        "checked_out_head_sha",
        "model_count",
        "models",
        "inventory_semantic_sha256",
        "model_selection_state",
        "effect_executions"
    ]
    for field in invariant_fields:
        vals = {json.dumps(r[field], sort_keys=True) for r in receipts}
        if len(vals) != 1:
            fail("FAIL_CROSS_RECEIVER_DIVERGENCE:" + field)

    os_set = {r["runner_os"] for r in receipts}
    if os_set != {"Linux", "Windows", "macOS"}:
        fail("FAIL_RUNNER_OS_SET:" + ",".join(sorted(os_set)))

    out_obj = {
        "schema": "CoModelSubstrateLight.OllamaInventoryFanin.v0.1",
        "STATE": "PASS_DISTINCT_RUNNER_OLLAMA_INVENTORY_PREFLIGHT_CONVERGENCE",
        "receiver_count": 3,
        "runner_os_set": sorted(os_set),
        "checked_out_head_sha": receipts[0]["checked_out_head_sha"],
        "model_count": receipts[0]["model_count"],
        "inventory_semantic_sha256": receipts[0]["inventory_semantic_sha256"],
        "model_selection_state": receipts[0]["model_selection_state"],
        "effect_executions": 0,
        "receipt_set_semantic_sha256": canonical_sha([
            {
                "runner_os": r["runner_os"],
                "runner_arch": r["runner_arch"],
                "platform_machine": r["platform_machine"],
                "inventory_semantic_sha256": r["inventory_semantic_sha256"]
            }
            for r in sorted(receipts, key=lambda x: x["runner_os"])
        ]),
        "coverage_boundary": [
            "DETERMINISTIC_LOOPBACK_TAGS_RECEIVER",
            "THREE_GITHUB_HOSTED_RUNNER_OS_CLASSES",
            "NO_REAL_OLLAMA_RUNTIME",
            "NO_MODEL_EXECUTION",
            "NO_MODEL_PULL_OR_INSTALL"
        ],
        "nonclaims": [
            "MOCK_INVENTORY_NE_X2_INVENTORY",
            "INVENTORY_PROTOCOL_PASS_NE_REAL_OLLAMA_RUNTIME",
            "MODEL_LISTING_NE_MODEL_QUALITY",
            "VALIDATION_IS_NOT_ACCEPTANCE"
        ]
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": out_obj["STATE"],
        "receiver_count": 3,
        "runner_os_set": out_obj["runner_os_set"],
        "checked_out_head_sha": out_obj["checked_out_head_sha"],
        "model_count": out_obj["model_count"],
        "inventory_semantic_sha256": out_obj["inventory_semantic_sha256"],
        "receipt_set_semantic_sha256": out_obj["receipt_set_semantic_sha256"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
