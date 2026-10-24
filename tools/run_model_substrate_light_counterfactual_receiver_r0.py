#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_controlled_counterfactual_r0.json")
PORTABLE_RUNNER = Path("tools/run_model_substrate_light_portable_r0.py")


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def git_blob(ref, path):
    return subprocess.check_output(["git", "rev-parse", f"{ref}:{path}"], text=True).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["SINGLE", "PARALLEL"], required=True)
    ap.add_argument("--replica-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    fx_raw = FIXTURE.read_bytes()
    fx = json.loads(fx_raw.decode("utf-8"))
    src = fx["source_bindings"]

    if git_blob("HEAD", src["portable_model_path"]) != src["portable_model_blob_sha"]:
        fail("FAIL_PORTABLE_MODEL_BLOB_DRIFT")
    if git_blob("HEAD", src["portable_runner_path"]) != src["portable_runner_blob_sha"]:
        fail("FAIL_PORTABLE_RUNNER_BLOB_DRIFT")

    mode_spec = fx["single_mode"] if args.mode == "SINGLE" else fx["parallel_mode"]
    if args.replica_id not in mode_spec["replica_ids"]:
        fail("FAIL_REPLICA_ID_NOT_IN_MODE")

    with tempfile.TemporaryDirectory() as td:
        portable_path = Path(td) / "portable-model-receipt.json"
        p = subprocess.run(
            [sys.executable, str(PORTABLE_RUNNER), "--output", str(portable_path)],
            text=True,
            capture_output=True,
        )
        if p.returncode != 0:
            fail("FAIL_PORTABLE_RUNNER:" + p.stderr[-1000:])
        portable_raw = portable_path.read_bytes()
        portable = json.loads(portable_raw.decode("utf-8"))

    if portable.get("STATE") != "PASS_PORTABLE_PARAMETERIZED_MODEL_RECONSTRUCTION":
        fail("FAIL_PORTABLE_RECEIPT_STATE")
    expected_cases = fx["scoring"]["expected_unique_case_count"]
    if portable.get("inference_case_count") != expected_cases:
        fail("FAIL_INFERENCE_CASE_COUNT")

    outputs = portable.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != expected_cases:
        fail("FAIL_OUTPUT_SET")
    case_ids = [x.get("id") for x in outputs]
    if len(case_ids) != len(set(case_ids)):
        fail("FAIL_DUPLICATE_CASE_ID")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoModelSubstrateLight.ControlledCounterfactualReceiver.v0.1",
        "STATE": "PASS_CONTROLLED_COUNTERFACTUAL_RECEIVER_R0",
        "checked_out_head_sha": head,
        "logical_work_id": fx["logical_work_id"],
        "counterfactual_mode": args.mode,
        "physical_width_declared": mode_spec["physical_width"],
        "replica_id": args.replica_id,
        "runner_class": fx["runner_class"],
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "fixture_sha256": sha256(fx_raw),
        "portable_receipt_sha256": sha256(portable_raw),
        "logical_model_id": portable["logical_model_id"],
        "model_pack_sha256": portable["model_pack_sha256"],
        "parameter_semantic_sha256": portable["parameter_semantic_sha256"],
        "inference_semantic_sha256": portable["inference_semantic_sha256"],
        "inference_case_count": portable["inference_case_count"],
        "verified_case_ids": sorted(case_ids),
        "qualified_benefit_units": portable["inference_case_count"],
        "verified_deeds": portable["inference_case_count"],
        "execution_cost_units": 1,
        "effect_execution_total": 0,
        "portable_output_semantic_sha256": canonical_sha(outputs),
        "coverage_boundary": fx["coverage_boundary"],
        "nonclaims": fx["nonclaims"],
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_head_sha": head,
        "mode": args.mode,
        "replica_id": args.replica_id,
        "qualified_benefit_units": receipt["qualified_benefit_units"],
        "verified_deeds": receipt["verified_deeds"],
        "execution_cost_units": receipt["execution_cost_units"],
        "inference_semantic_sha256": receipt["inference_semantic_sha256"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
