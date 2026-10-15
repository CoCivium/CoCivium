#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_complementary_search_counterfactual_r0.json")


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def frac_obj(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    files = sorted(Path(args.input_root).rglob("complementary-search-receiver.json"))
    if len(files) != 4:
        fail(f"FAIL_RECEIPT_COUNT:{len(files)}")

    records = []
    for path in files:
        raw = path.read_bytes()
        r = json.loads(raw.decode("utf-8"))
        if r.get("STATE") != "PASS_COMPLEMENTARY_SEARCH_RECEIVER_R0":
            fail("FAIL_RECEIVER_STATE")
        if r.get("effect_execution_total") != 0:
            fail("FAIL_EFFECT_EXECUTED")
        records.append((path, raw, r))

    singles = [x for x in records if x[2]["counterfactual_mode"] == "SINGLE"]
    parallels = [x for x in records if x[2]["counterfactual_mode"] == "PARALLEL"]
    if len(singles) != 1 or len(parallels) != 3:
        fail("FAIL_MODE_COUNTS")

    invariant_fields = [
        "checked_out_head_sha",
        "logical_work_id",
        "fixture_sha256",
        "record_budget",
    ]
    for field in invariant_fields:
        vals = {json.dumps(x[2][field], sort_keys=True) for x in records}
        if len(vals) != 1:
            fail("FAIL_COUNTERFACTUAL_INVARIANT_DRIFT:" + field)

    if any(r["runner_os"] != "Linux" for _, _, r in records):
        fail("FAIL_RUNNER_OS_CLASS")
    if any(r["runner_arch"] != "X64" for _, _, r in records):
        fail("FAIL_RUNNER_ARCH_CLASS")

    if singles[0][2]["replica_id"] != "S0" or singles[0][2]["assigned_shard_id"] != "A":
        fail("FAIL_SINGLE_ASSIGNMENT")

    parallel_assignment = {
        r["replica_id"]: r["assigned_shard_id"] for _, _, r in parallels
    }
    if parallel_assignment != {"P0": "A", "P1": "B", "P2": "C"}:
        fail("FAIL_PARALLEL_ASSIGNMENTS")

    single_targets = sorted(set(singles[0][2]["found_targets"]))
    parallel_targets = sorted({
        v for _, _, r in parallels for v in r["found_targets"]
    })
    scoring = fx["scoring"]

    if single_targets != scoring["expected_single_unique_targets"]:
        fail("FAIL_SINGLE_TARGET_SET")
    if parallel_targets != scoring["expected_parallel_unique_targets"]:
        fail("FAIL_PARALLEL_TARGET_SET")

    all_expected = sorted(fx["dataset"]["expected_targets"])
    if parallel_targets != all_expected:
        fail("FAIL_PARALLEL_DID_NOT_COVER_EXPECTED_TARGETS")

    single_benefit = len(single_targets)
    parallel_benefit = len(parallel_targets)
    single_deeds = scoring["expected_single_verified_deeds"]
    parallel_deeds = scoring["expected_parallel_verified_deeds"]
    single_cost = sum(r["receiver_lease_count"] for _, _, r in singles)
    parallel_cost = sum(r["receiver_lease_count"] for _, _, r in parallels)

    if single_benefit != scoring["expected_single_benefit_units"]:
        fail("FAIL_SINGLE_BENEFIT")
    if parallel_benefit != scoring["expected_parallel_benefit_units"]:
        fail("FAIL_PARALLEL_BENEFIT")
    if single_cost != scoring["expected_single_execution_cost_units"]:
        fail("FAIL_SINGLE_COST")
    if parallel_cost != scoring["expected_parallel_execution_cost_units"]:
        fail("FAIL_PARALLEL_COST")

    single_yield = Fraction(single_benefit, single_deeds)
    parallel_yield = Fraction(parallel_benefit, parallel_deeds)
    strict_gain = parallel_yield > single_yield
    exp = fx["expected"]

    if frac_obj(single_yield) != {
        "numerator": exp["single_benefit_yield_numerator"],
        "denominator": exp["single_benefit_yield_denominator"],
    }:
        fail("FAIL_SINGLE_YIELD")
    if frac_obj(parallel_yield) != {
        "numerator": exp["parallel_benefit_yield_numerator"],
        "denominator": exp["parallel_benefit_yield_denominator"],
    }:
        fail("FAIL_PARALLEL_YIELD")
    if strict_gain != exp["parallel_strict_verified_benefit_gain"]:
        fail("FAIL_STRICT_GAIN")
    if parallel_cost != single_cost * exp["parallel_execution_cost_multiplier"]:
        fail("FAIL_COST_MULTIPLIER")
    if exp["parallel_efficiency_gain_claimed"] is not False:
        fail("FAIL_FIXTURE_EFFICIENCY_CLAIM")

    readproofs = []
    for path, raw, r in sorted(records, key=lambda x: x[2]["replica_id"]):
        readproofs.append({
            "replica_id": r["replica_id"],
            "counterfactual_mode": r["counterfactual_mode"],
            "assigned_shard_id": r["assigned_shard_id"],
            "receipt_content_sha256": sha256(raw),
            "checked_out_head_sha": r["checked_out_head_sha"],
            "found_targets": r["found_targets"],
            "receiver_readproof": "PASS_EXACT_OBJECT_READBACK",
            "source_artifact_relative_path": str(path),
        })

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoModelSubstrateLight.ComplementarySearchCounterfactualFanin.v0.1",
        "STATE": "PASS_CONTROLLED_COMPLEMENTARY_SEARCH_COUNTERFACTUAL_R0",
        "checked_out_head_sha": head,
        "logical_work_id": fx["logical_work_id"],
        "same_exact_logical_work_object": True,
        "single": {
            "physical_width": 1,
            "receiver_count": 1,
            "covered_shards": ["A"],
            "unique_verified_targets": single_targets,
            "qualified_benefit_units": single_benefit,
            "verified_deeds": single_deeds,
            "benefit_yield": frac_obj(single_yield),
            "execution_cost_units": single_cost,
        },
        "parallel": {
            "physical_width": 3,
            "receiver_count": 3,
            "covered_shards": ["A", "B", "C"],
            "unique_verified_targets": parallel_targets,
            "qualified_benefit_units": parallel_benefit,
            "verified_deeds": parallel_deeds,
            "benefit_yield": frac_obj(parallel_yield),
            "execution_cost_units": parallel_cost,
        },
        "parallel_strict_verified_benefit_gain": strict_gain,
        "parallel_efficiency_gain_claimed": False,
        "pressure_metrics_present": False,
        "advisory_width_decision": exp["advisory_decision"],
        "physical_width_change_authorized": exp["physical_width_change_authorized"],
        "picked_up_receiver_receipt_count": len(readproofs),
        "readproofs": readproofs,
        "receipt_set_semantic_sha256": canonical_sha(readproofs),
        "next_gate": "MEASURE_RECEIVER_PRESSURE_PROOF_DEBT_COLLISION_ATTENTION_AND_COMPUTE_BUDGETS_BEFORE_POSITIVE_WIDENING_ADVISORY",
        "coverage_boundary": fx["coverage_boundary"],
        "nonclaims": fx["nonclaims"] + [
            "PICKED_UP_BY_COMPLEMENTARY_COUNTERFACTUAL_COMPILER_NE_INTEGRATED",
            "POSITIVE_COVERAGE_GAIN_NE_RUNTIME_WIDEN_PERMISSION",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
        ],
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_head_sha": head,
        "picked_up_receiver_receipt_count": receipt["picked_up_receiver_receipt_count"],
        "single_unique_verified_targets": single_targets,
        "parallel_unique_verified_targets": parallel_targets,
        "single_benefit_yield": receipt["single"]["benefit_yield"],
        "parallel_benefit_yield": receipt["parallel"]["benefit_yield"],
        "single_execution_cost_units": single_cost,
        "parallel_execution_cost_units": parallel_cost,
        "parallel_strict_verified_benefit_gain": strict_gain,
        "parallel_efficiency_gain_claimed": False,
        "pressure_metrics_present": False,
        "advisory_width_decision": receipt["advisory_width_decision"],
        "physical_width_change_authorized": receipt["physical_width_change_authorized"],
        "receipt_set_semantic_sha256": receipt["receipt_set_semantic_sha256"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
