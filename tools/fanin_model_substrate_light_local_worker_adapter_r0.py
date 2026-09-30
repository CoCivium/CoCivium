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

    files = sorted(Path(args.input_root).rglob("local-worker-receipt.json"))
    if len(files) != 3:
        fail(f"FAIL_RECEIPT_COUNT:{len(files)}")
    receipts = [json.loads(p.read_text(encoding="utf-8")) for p in files]

    for r in receipts:
        if r["STATE"] != "PASS_LOCAL_WORKER_LOOPBACK_ADAPTER_R0":
            fail("FAIL_RECEIVER_STATE")
        if r["effect_execution_total"] != 0:
            fail("FAIL_EFFECT_EXECUTED")
        if r["network_scope"] != "LOOPBACK_ONLY":
            fail("FAIL_NETWORK_SCOPE")

    invariants = [
        "checked_out_head_sha",
        "worker_blob_sha",
        "worker_doc_blob_sha",
        "contract_sha256",
        "worker_output_sha256",
        "worker_result_semantic_sha256",
        "effect_execution_total",
        "network_scope",
        "receiver_class",
    ]
    for field in invariants:
        vals = {json.dumps(r[field], sort_keys=True) for r in receipts}
        if len(vals) != 1:
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

    out_obj = {
        "schema": "CoModelSubstrateLight.LocalWorkerAdapterFanin.v0.1",
        "STATE": "PASS_DISTINCT_RUNNER_LOCAL_WORKER_ADAPTER_CONVERGENCE",
        "receiver_count": 3,
        "runner_os_set": sorted(os_set),
        "receiver_ids": sorted(receiver_ids),
        "checked_out_head_sha": receipts[0]["checked_out_head_sha"],
        "worker_blob_sha": receipts[0]["worker_blob_sha"],
        "contract_sha256": receipts[0]["contract_sha256"],
        "worker_output_sha256": receipts[0]["worker_output_sha256"],
        "worker_result_semantic_sha256": receipts[0]["worker_result_semantic_sha256"],
        "effect_execution_total": 0,
        "network_scope": "LOOPBACK_ONLY",
        "receipt_set_semantic_sha256": canonical_sha([
            {
                "runner_os": r["runner_os"],
                "runner_arch": r["runner_arch"],
                "platform_system": r["platform_system"],
                "platform_machine": r["platform_machine"],
                "worker_output_sha256": r["worker_output_sha256"],
            }
            for r in sorted(receipts, key=lambda x: x["runner_os"])
        ]),
        "coverage_boundary": [
            "EXISTING_COLOCALMODELWORKERR3_ADAPTER",
            "THREE_GITHUB_HOSTED_RUNNER_OS_CLASSES",
            "DETERMINISTIC_LOOPBACK_OLLAMA_PROTOCOL_MOCK",
            "NO_REAL_OLLAMA_MODEL",
            "NO_X2_RUNTIME_CANARY"
        ],
        "nonclaims": [
            "MOCK_OLLAMA_NE_REAL_OLLAMA_RUNTIME",
            "ADAPTER_PROTOCOL_PASS_NE_REAL_MODEL_MATERIALIZATION",
            "RUNNER_OS_DIVERSITY_NE_HARDWARE_DIVERSITY",
            "CROSS_OS_ADAPTER_PASS_NE_MODEL_MIGRATION",
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "ADAPTER_PASS_NE_COEX"
        ],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": out_obj["STATE"],
        "receiver_count": out_obj["receiver_count"],
        "runner_os_set": out_obj["runner_os_set"],
        "checked_out_head_sha": out_obj["checked_out_head_sha"],
        "worker_blob_sha": out_obj["worker_blob_sha"],
        "contract_sha256": out_obj["contract_sha256"],
        "worker_output_sha256": out_obj["worker_output_sha256"],
        "worker_result_semantic_sha256": out_obj["worker_result_semantic_sha256"],
        "receipt_set_semantic_sha256": out_obj["receipt_set_semantic_sha256"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
