#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_complementary_search_counterfactual_r0.json")


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["SINGLE", "PARALLEL"], required=True)
    ap.add_argument("--replica-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    raw = FIXTURE.read_bytes()
    fx = json.loads(raw.decode("utf-8"))
    mode = fx["single_mode"] if args.mode == "SINGLE" else fx["parallel_mode"]
    assignments = mode["assignments"]

    if args.replica_id not in assignments:
        fail("FAIL_REPLICA_ASSIGNMENT")
    shard_id = assignments[args.replica_id]

    shards = {s["shard_id"]: s for s in fx["dataset"]["shards"]}
    if shard_id not in shards:
        fail("FAIL_SHARD_BIND")
    values = shards[shard_id]["values"]
    rule = fx["search_rule"]

    if len(values) > rule["max_records_per_receiver_lease"]:
        fail("FAIL_RECORD_BUDGET")
    if rule["max_shards_per_receiver_lease"] != 1:
        fail("FAIL_SHARD_BUDGET_POLICY")

    found = [v for v in values if v % 7 == 0]
    expected_all = set(fx["dataset"]["expected_targets"])
    if any(v not in expected_all for v in found):
        fail("FAIL_FALSE_POSITIVE")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoModelSubstrateLight.ComplementarySearchReceiver.v0.1",
        "STATE": "PASS_COMPLEMENTARY_SEARCH_RECEIVER_R0",
        "checked_out_head_sha": head,
        "logical_work_id": fx["logical_work_id"],
        "counterfactual_mode": args.mode,
        "physical_width_declared": mode["physical_width"],
        "replica_id": args.replica_id,
        "assigned_shard_id": shard_id,
        "fixture_sha256": sha256(raw),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "records_inspected": len(values),
        "record_budget": rule["max_records_per_receiver_lease"],
        "found_targets": found,
        "found_target_semantic_sha256": canonical_sha(found),
        "receiver_lease_count": 1,
        "effect_execution_total": 0,
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
        "assigned_shard_id": shard_id,
        "records_inspected": receipt["records_inspected"],
        "found_targets": found
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
