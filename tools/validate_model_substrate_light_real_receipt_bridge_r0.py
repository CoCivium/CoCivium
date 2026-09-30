#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

MANIFEST = Path("evidence/substrate/receiver-receipts-r0/manifest.json")
LANDED_ROOT = MANIFEST.parent


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().lower()


def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def api_get(path, token):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CoCivium-PR135-real-receipt-bridge-r0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--download-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        fail("FAIL_GITHUB_TOKEN_MISSING")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    root = Path(args.download_root)
    readproofs = []
    total_source_receivers = 0

    path_by_identity = {
        "receipt:portability-fanin-r0": "portability/model-substrate-light-portability-fanin-r0.json",
        "receipt:local-worker-adapter-fanin-r0": "local-worker/local-worker-adapter-fanin-r0.json",
        "receipt:bound-ollama-fanin-r0": "bound-ollama/bound-ollama-fanin-r0.json",
    }
    expected_states = {
        "receipt:portability-fanin-r0": "PASS_DISTINCT_RUNNER_MODEL_RECONSTRUCTION_CONVERGENCE",
        "receipt:local-worker-adapter-fanin-r0": "PASS_DISTINCT_RUNNER_LOCAL_WORKER_ADAPTER_CONVERGENCE",
        "receipt:bound-ollama-fanin-r0": "PASS_DISTINCT_RUNNER_BOUND_OLLAMA_PROTOCOL_CONVERGENCE",
    }

    for obj in manifest["objects"]:
        identity = obj["Identity"]
        prov = obj["Provenance"]
        landed_name = {
            "receipt:portability-fanin-r0": "portability-fanin-r0.json",
            "receipt:local-worker-adapter-fanin-r0": "local-worker-adapter-fanin-r0.json",
            "receipt:bound-ollama-fanin-r0": "bound-ollama-fanin-r0.json",
        }[identity]
        landed_path = LANDED_ROOT / landed_name
        downloaded_path = root / path_by_identity[identity]

        landed_raw = landed_path.read_bytes()
        source_raw = downloaded_path.read_bytes()
        expected_hash = obj["ContentHash"].split(":", 1)[1].lower()

        if sha256(landed_raw) != expected_hash:
            fail("FAIL_LANDED_CONTENT_HASH:" + identity)
        if sha256(source_raw) != expected_hash:
            fail("FAIL_SOURCE_CONTENT_HASH:" + identity)
        if source_raw != landed_raw:
            fail("FAIL_SOURCE_NE_LANDED_BYTES:" + identity)

        receipt = json.loads(source_raw.decode("utf-8"))
        if receipt.get("STATE") != expected_states[identity]:
            fail("FAIL_SOURCE_RECEIPT_STATE:" + identity)
        if receipt.get("checked_out_head_sha") != prov["source_head_sha"]:
            fail("FAIL_SOURCE_HEAD_BIND:" + identity)
        if receipt.get("receiver_count") != 3:
            fail("FAIL_SOURCE_RECEIVER_COUNT:" + identity)

        meta = api_get(
            f"/repos/CoCivium/CoCivium/actions/artifacts/{prov['artifact_id']}",
            token,
        )
        if meta.get("id") != prov["artifact_id"]:
            fail("FAIL_ARTIFACT_ID:" + identity)
        if meta.get("name") != prov["artifact_name"]:
            fail("FAIL_ARTIFACT_NAME:" + identity)
        if meta.get("digest") != prov["artifact_archive_digest"]:
            fail("FAIL_ARTIFACT_ARCHIVE_DIGEST:" + identity)
        if meta.get("expired") is not False:
            fail("FAIL_ARTIFACT_EXPIRED:" + identity)
        wr = meta.get("workflow_run") or {}
        if wr.get("id") != prov["workflow_run_id"]:
            fail("FAIL_ARTIFACT_RUN_ID:" + identity)
        if wr.get("head_sha") != prov["source_head_sha"]:
            fail("FAIL_ARTIFACT_HEAD_SHA:" + identity)

        total_source_receivers += receipt["receiver_count"]
        readproofs.append({
            "Identity": identity,
            "ContentHash": obj["ContentHash"],
            "source_workflow_run_id": prov["workflow_run_id"],
            "source_artifact_id": prov["artifact_id"],
            "source_artifact_archive_digest": prov["artifact_archive_digest"],
            "source_receipt_state": receipt["STATE"],
            "source_receiver_count": receipt["receiver_count"],
            "source_head_sha": receipt["checked_out_head_sha"],
            "exact_source_bytes_equal_landed_bytes": True,
            "receiver_readproof": "PASS_EXACT_OBJECT_READBACK",
            "coverage_boundary": receipt.get("coverage_boundary", []),
        })

    policy = manifest["advisory_policy"]
    if policy["same_task_controlled_single_width_baseline_present"]:
        fail("FAIL_FIXTURE_FALSELY_CLAIMS_SINGLE_BASELINE")
    if policy["same_task_parallel_receipt_present"]:
        fail("FAIL_FIXTURE_FALSELY_CLAIMS_PAIRED_PARALLEL")
    if policy["measured_receiver_pressure_present"]:
        fail("FAIL_FIXTURE_FALSELY_CLAIMS_RECEIVER_PRESSURE")
    if policy["measured_real_world_benefit_present"]:
        fail("FAIL_FIXTURE_FALSELY_CLAIMS_REAL_BENEFIT")
    if policy["required_decision"] != "HOLD_NO_CONTROLLED_COUNTERFACTUAL_BASELINE":
        fail("FAIL_ADVISORY_POLICY_DECISION")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out_obj = {
        "schema": "CoModelSubstrateLight.RealReceiverReceiptAdvisoryReadproof.v0.1",
        "STATE": "PASS_REAL_RECEIVER_RECEIPT_BRIDGE_R0",
        "checked_out_head_sha": head,
        "receiver_identity": manifest["receiver"]["identity"],
        "landed_object_count": len(readproofs),
        "picked_up_by_advisory_compiler_count": len(readproofs),
        "source_receiver_count_total": total_source_receivers,
        "readproofs": readproofs,
        "advisory_width_decision": "HOLD_NO_CONTROLLED_COUNTERFACTUAL_BASELINE",
        "physical_width_change_authorized": False,
        "integration_state": "UNPROVEN",
        "manifest_semantic_sha256": canonical_sha(manifest),
        "coverage_boundary": manifest["coverage_boundary"],
        "nonclaims": manifest["nonclaims"] + [
            "LANDED_NE_INTEGRATED",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "HISTORICAL_CI_RECEIPT_NE_CONTROLLED_COUNTERFACTUAL",
        ],
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": out_obj["STATE"],
        "checked_out_head_sha": head,
        "landed_object_count": out_obj["landed_object_count"],
        "picked_up_by_advisory_compiler_count": out_obj["picked_up_by_advisory_compiler_count"],
        "source_receiver_count_total": out_obj["source_receiver_count_total"],
        "advisory_width_decision": out_obj["advisory_width_decision"],
        "physical_width_change_authorized": out_obj["physical_width_change_authorized"],
        "integration_state": out_obj["integration_state"],
        "manifest_semantic_sha256": out_obj["manifest_semantic_sha256"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
