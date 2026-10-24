#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_controlled_counterfactual_r0.json")


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
    files = sorted(Path(args.input_root).rglob("counterfactual-receiver.json"))
    if len(files) != 4:
        fail(f"FAIL_RECEIPT_COUNT:{len(files)}")

    records = []
    for path in files:
        raw = path.read_bytes()
        receipt = json.loads(raw.decode("utf-8"))
        if receipt.get("STATE") != "PASS_CONTROLLED_COUNTERFACTUAL_RECEIVER_R0":
            fail("FAIL_RECEIVER_STATE")
        if receipt.get("effect_execution_total") != 0:
            fail("FAIL_EFFECT_EXECUTED")
        records.append((path, raw, receipt))

    singles = [x for x in records if x[2]["counterfactual_mode"] == "SINGLE"]
    parallels = [x for x in records if x[2]["counterfactual_mode"] == "PARALLEL"]
    if len(singles) != 1 or len(parallels) != 3:
        fail("FAIL_MODE_COUNTS")

    all_receipts = [x[2] for x in records]
    invariant_fields = [
        "checked_out_head_sha",
        "logical_work_id",
        "runner_class",
        "fixture_sha256",
        "logical_model_id",
        "model_pack_sha256",
        "parameter_semantic_sha256",
        "inference_semantic_sha256",
        "inference_case_count",
        "verified_case_ids",
        "qualified_benefit_units",
        "verified_deeds",
        "portable_output_semantic_sha256",
    ]
    for field in invariant_fields:
        vals = {json.dumps(r[field], sort_keys=True) for r in all_receipts}
        if len(vals) != 1:
            fail("FAIL_COUNTERFACTUAL_INVARIANT_DRIFT:" + field)

    replica_ids = [r["replica_id"] for r in all_receipts]
    if set(replica_ids) != {"S0", "P0", "P1", "P2"}:
        fail("FAIL_REPLICA_SET")
    if len(replica_ids) != len(set(replica_ids)):
        fail("FAIL_DUPLICATE_REPLICA")

    if any(r.get("runner_os") != "Linux" for r in all_receipts):
        fail("FAIL_RUNNER_OS_CLASS")
    if any(r.get("runner_arch") != "X64" for r in all_receipts):
        fail("FAIL_RUNNER_ARCH_CLASS")

    single = singles[0][2]
    unique_parallel_case_ids = sorted({
        cid for _, _, r in parallels for cid in r["verified_case_ids"]
    })
    expected_cases = fx["scoring"]["expected_unique_case_count"]
    if len(unique_parallel_case_ids) != expected_cases:
        fail("FAIL_PARALLEL_UNIQUE_CASE_COUNT")

    single_benefit = fx["scoring"]["expected_single_benefit_units"]
    parallel_benefit = fx["scoring"]["expected_parallel_benefit_units"]
    single_deeds = fx["scoring"]["expected_single_verified_deeds"]
    parallel_deeds = fx["scoring"]["expected_parallel_verified_deeds"]
    if single["qualified_benefit_units"] != single_benefit:
        fail("FAIL_SINGLE_BENEFIT")
    if single["verified_deeds"] != single_deeds:
        fail("FAIL_SINGLE_VERIFIED_DEEDS")
    if len(unique_parallel_case_ids) != parallel_benefit:
        fail("FAIL_PARALLEL_BENEFIT")
    if len(unique_parallel_case_ids) != parallel_deeds:
        fail("FAIL_PARALLEL_VERIFIED_DEEDS")

    single_cost = sum(r["execution_cost_units"] for _, _, r in singles)
    parallel_cost = sum(r["execution_cost_units"] for _, _, r in parallels)
    if single_cost != fx["scoring"]["expected_single_execution_cost_units"]:
        fail("FAIL_SINGLE_COST")
    if parallel_cost != fx["scoring"]["expected_parallel_execution_cost_units"]:
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
    if strict_gain != exp["parallel_strict_benefit_yield_gain"]:
        fail("FAIL_STRICT_GAIN_EXPECTATION")

    decision = (
        "ADVISE_PARALLEL_WIDTH_3_VERIFIED_BENEFIT_GAIN"
        if strict_gain
        else "ADVISE_PHYSICAL_WIDTH_1_NO_STRICT_VERIFIED_BENEFIT_GAIN"
    )
    if decision != exp["advisory_decision"]:
        fail("FAIL_ADVISORY_DECISION")

    readproofs = []
    for path, raw, r in sorted(records, key=lambda x: x[2]["replica_id"]):
        readproofs.append({
            "replica_id": r["replica_id"],
            "counterfactual_mode": r["counterfactual_mode"],
            "receipt_content_sha256": sha256(raw),
            "checked_out_head_sha": r["checked_out_head_sha"],
            "logical_work_id": r["logical_work_id"],
            "inference_semantic_sha256": r["inference_semantic_sha256"],
            "receiver_readproof": "PASS_EXACT_OBJECT_READBACK",
            "source_artifact_relative_path": str(path),
        })

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoModelSubstrateLight.ControlledCounterfactualFanin.v0.1",
        "STATE": "PASS_CONTROLLED_SINGLE_VS_PARALLEL_COUNTERFACTUAL_R0",
        "checked_out_head_sha": head,
        "logical_work_id": fx["logical_work_id"],
        "same_exact_work_object": True,
        "same_runner_class": fx["runner_class"],
        "single": {
            "physical_width": 1,
            "receiver_count": 1,
            "qualified_benefit_units": single_benefit,
            "verified_deeds": single_deeds,
            "benefit_yield": frac_obj(single_yield),
            "execution_cost_units": single_cost,
        },
        "parallel": {
            "physical_width": 3,
            "receiver_count": 3,
            "qualified_benefit_units": parallel_benefit,
            "verified_deeds": parallel_deeds,
            "benefit_yield": frac_obj(parallel_yield),
            "execution_cost_units": parallel_cost,
            "redundant_correct_case_validations": sum(
                r["inference_case_count"] for _, _, r in parallels
            ),
            "unique_correct_cases": len(unique_parallel_case_ids),
        },
        "parallel_strict_benefit_yield_gain": strict_gain,
        "advisory_width_decision": decision,
        "physical_width_change_authorized": exp["physical_width_change_authorized"],
        "picked_up_receiver_receipt_count": len(readproofs),
        "readproofs": readproofs,
        "receipt_set_semantic_sha256": canonical_sha(readproofs),
        "coverage_boundary": fx["coverage_boundary"],
        "nonclaims": fx["nonclaims"] + [
            "PICKED_UP_BY_COUNTERFACTUAL_COMPILER_NE_INTEGRATED",
            "CONTROLLED_COUNTERFACTUAL_NE_CAUSAL_GENERALIZATION",
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
        "single_benefit_yield": receipt["single"]["benefit_yield"],
        "parallel_benefit_yield": receipt["parallel"]["benefit_yield"],
        "single_execution_cost_units": single_cost,
        "parallel_execution_cost_units": parallel_cost,
        "parallel_strict_benefit_yield_gain": strict_gain,
        "advisory_width_decision": decision,
        "physical_width_change_authorized": receipt["physical_width_change_authorized"],
        "receipt_set_semantic_sha256": receipt["receipt_set_semantic_sha256"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
