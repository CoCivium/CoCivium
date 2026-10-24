#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


def fail(code):
    raise SystemExit(code)


def canonical_sha(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    root = Path(args.input_root)
    files = sorted(root.rglob("portable-model-receipt.json"))
    if len(files) != 3:
        fail(f"FAIL_RECEIPT_COUNT:{len(files)}")

    receipts = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    for r in receipts:
        if r["STATE"] != "PASS_PORTABLE_PARAMETERIZED_MODEL_RECONSTRUCTION":
            fail("FAIL_RECEIVER_STATE")

    invariant_fields = [
        "checked_out_head_sha",
        "logical_model_id",
        "model_kind",
        "model_version",
        "model_pack_sha256",
        "parameter_semantic_sha256",
        "inference_semantic_sha256",
        "inference_case_count",
        "identity_invariants_sha256"
    ]
    for field in invariant_fields:
        values = {json.dumps(r[field], sort_keys=True) for r in receipts}
        if len(values) != 1:
            fail("FAIL_CROSS_RECEIVER_DIVERGENCE:" + field)

    os_set = {r["runner_os"] for r in receipts}
    if os_set != {"Linux", "Windows", "macOS"}:
        fail("FAIL_RUNNER_OS_SET:" + ",".join(sorted(os_set)))

    receiver_ids = {
        f"{r['runner_os']}:{r['runner_arch']}:{r['platform_machine']}"
        for r in receipts
    }
    if len(receiver_ids) != 3:
        fail("FAIL_RECEIVER_IDENTITY_COLLISION")

    fanin_receipt = {
        "schema": "CoModelSubstrateLight.PortabilityFanin.v0.1",
        "STATE": "PASS_DISTINCT_RUNNER_MODEL_RECONSTRUCTION_CONVERGENCE",
        "receiver_count": len(receipts),
        "runner_os_set": sorted(os_set),
        "receiver_ids": sorted(receiver_ids),
        "checked_out_head_sha": receipts[0]["checked_out_head_sha"],
        "logical_model_id": receipts[0]["logical_model_id"],
        "model_pack_sha256": receipts[0]["model_pack_sha256"],
        "parameter_semantic_sha256": receipts[0]["parameter_semantic_sha256"],
        "inference_semantic_sha256": receipts[0]["inference_semantic_sha256"],
        "inference_case_count": receipts[0]["inference_case_count"],
        "receipt_set_semantic_sha256": canonical_sha([
            {
                "runner_os": r["runner_os"],
                "runner_arch": r["runner_arch"],
                "platform_system": r["platform_system"],
                "platform_machine": r["platform_machine"],
                "model_pack_sha256": r["model_pack_sha256"],
                "inference_semantic_sha256": r["inference_semantic_sha256"]
            }
            for r in sorted(receipts, key=lambda x: x["runner_os"])
        ]),
        "coverage_boundary": [
            "THREE_GITHUB_HOSTED_RUNNER_OS_CLASSES",
            "SMALL_INTEGER_PARAMETERIZED_MODEL_ONLY",
            "RECONSTRUCTION_FROM_IDENTICAL_DURABLE_MODEL_PACK",
            "NO_HARDWARE_IDENTITY_CLAIM",
            "NO_LLM_WEIGHT_MIGRATION"
        ],
        "nonclaims": [
            "RUNNER_OS_DIVERSITY_NE_HARDWARE_DIVERSITY",
            "PORTABLE_INFERENCE_NE_WEIGHT_MIGRATION_SOLVED",
            "SAME_OUTPUT_NE_SAME_INTERNAL_EXECUTION",
            "PORTABILITY_PASS_NE_RUNTIME_INTEGRATION",
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "PORTABILITY_PASS_NE_COEX"
        ]
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fanin_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": fanin_receipt["STATE"],
        "receiver_count": fanin_receipt["receiver_count"],
        "runner_os_set": fanin_receipt["runner_os_set"],
        "checked_out_head_sha": fanin_receipt["checked_out_head_sha"],
        "model_pack_sha256": fanin_receipt["model_pack_sha256"],
        "inference_semantic_sha256": fanin_receipt["inference_semantic_sha256"],
        "receipt_set_semantic_sha256": fanin_receipt["receipt_set_semantic_sha256"]
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
