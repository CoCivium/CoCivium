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

    files = sorted(Path(args.input_root).rglob("bound-ollama-receipt.json"))
    if len(files) != 3:
        fail(f"FAIL_RECEIPT_COUNT:{len(files)}")
    receipts = [json.loads(p.read_text(encoding="utf-8")) for p in files]

    for r in receipts:
        if r["STATE"] != "PASS_BOUND_LOCAL_OLLAMA_MODEL_RUN":
            fail("FAIL_RECEIVER_STATE")
        if r["effect_execution_total"] != 0:
            fail("FAIL_EFFECT_EXECUTED")
        if r["model_pull_or_install_performed"] is not False:
            fail("FAIL_PULL_INSTALL_FLAG")
        if r["inventory_stable"] is not True:
            fail("FAIL_INVENTORY_STABILITY")

    invariant_fields = [
        "checked_out_head_sha",
        "selected_model",
        "pre_inventory_semantic_sha256",
        "post_inventory_semantic_sha256",
        "contract_sha256",
        "worker_output_sha256",
        "worker_result_semantic_sha256",
        "effect_execution_total",
        "model_pull_or_install_performed"
    ]
    for field in invariant_fields:
        vals = {json.dumps(r[field], sort_keys=True) for r in receipts}
        if len(vals) != 1:
            fail("FAIL_CROSS_RECEIVER_DIVERGENCE:" + field)

    out_obj = {
        "schema": "CoModelSubstrateLight.BoundOllamaFanin.v0.1",
        "STATE": "PASS_DISTINCT_RUNNER_BOUND_OLLAMA_PROTOCOL_CONVERGENCE",
        "receiver_count": 3,
        "checked_out_head_sha": receipts[0]["checked_out_head_sha"],
        "selected_model": receipts[0]["selected_model"],
        "inventory_semantic_sha256": receipts[0]["pre_inventory_semantic_sha256"],
        "contract_sha256": receipts[0]["contract_sha256"],
        "worker_output_sha256": receipts[0]["worker_output_sha256"],
        "worker_result_semantic_sha256": receipts[0]["worker_result_semantic_sha256"],
        "effect_execution_total": 0,
        "model_pull_or_install_performed": False,
        "receipt_set_semantic_sha256": canonical_sha([
            {
                "selected_model": r["selected_model"],
                "inventory_semantic_sha256": r["pre_inventory_semantic_sha256"],
                "worker_output_sha256": r["worker_output_sha256"],
                "worker_result_semantic_sha256": r["worker_result_semantic_sha256"]
            }
            for r in receipts
        ]),
        "coverage_boundary": [
            "EXACT_NAME_PLUS_DIGEST_BIND",
            "PRE_POST_INVENTORY_STABILITY",
            "DETERMINISTIC_LOOPBACK_OLLAMA_PROTOCOL",
            "NO_REAL_MODEL_INFERENCE",
            "NO_MODEL_PULL_OR_INSTALL"
        ],
        "nonclaims": [
            "MOCK_OLLAMA_NE_REAL_OLLAMA_RUNTIME",
            "OLLAMA_REPORTED_DIGEST_NE_UNIVERSAL_MODEL_IDENTITY",
            "DIGEST_STABILITY_NE_MODEL_QUALITY",
            "BOUND_PROTOCOL_PASS_NE_X2_MODEL_RUN",
            "VALIDATION_IS_NOT_ACCEPTANCE"
        ]
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": out_obj["STATE"],
        "receiver_count": 3,
        "checked_out_head_sha": out_obj["checked_out_head_sha"],
        "model_name": out_obj["selected_model"]["name"],
        "model_digest": out_obj["selected_model"]["digest"],
        "inventory_semantic_sha256": out_obj["inventory_semantic_sha256"],
        "worker_output_sha256": out_obj["worker_output_sha256"],
        "worker_result_semantic_sha256": out_obj["worker_result_semantic_sha256"],
        "receipt_set_semantic_sha256": out_obj["receipt_set_semantic_sha256"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
