#!/usr/bin/env python3
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_benefit_oomph_r0.json")


def fail(code):
    raise SystemExit(code)


def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def git_blob(ref, path):
    return subprocess.check_output(
        ["git", "rev-parse", f"{ref}:{path}"], text=True
    ).strip()


def yield_fraction(candidate):
    deeds = candidate["verified_deeds"]
    if not isinstance(deeds, int) or deeds <= 0:
        fail("FAIL_VERIFIED_DEEDS")
    benefit = candidate["qualified_benefit_units"]
    if not isinstance(benefit, int) or benefit < 0:
        fail("FAIL_QUALIFIED_BENEFIT")
    return Fraction(benefit, deeds)


def budget_reasons(parallel, budgets):
    reasons = []
    checks = [
        ("receiver_pressure", "receiver_pressure_max", "RECEIVER_PRESSURE_BUDGET_EXCEEDED"),
        ("proof_debt", "proof_debt_max", "PROOF_DEBT_BUDGET_EXCEEDED"),
        ("collision_risk", "collision_risk_max", "COLLISION_RISK_BUDGET_EXCEEDED"),
        ("human_attention_cost", "human_attention_cost_max", "HUMAN_ATTENTION_BUDGET_EXCEEDED"),
        ("compute_cost", "compute_cost_max", "COMPUTE_COST_BUDGET_EXCEEDED"),
    ]
    for metric, limit, reason in checks:
        if parallel[metric] > budgets[limit]:
            reasons.append(reason)
    return reasons


def decide(scenario, policy):
    single_yield = yield_fraction(scenario["single"])
    parallel_yield = yield_fraction(scenario["parallel"])
    confidence = scenario["parallel"]["counterfactual_confidence_bp"]

    if confidence < policy["min_counterfactual_confidence_bp"]:
        return {
            "decision": "HOLD_MEASURE_MORE_ON_PHYSICAL_1",
            "physical_width": policy["single_physical_width"],
            "logical_branch_count": policy["logical_branch_count"],
            "single_yield": single_yield,
            "parallel_yield": parallel_yield,
            "reasons": ["COUNTERFACTUAL_CONFIDENCE_BELOW_FLOOR"],
        }

    if parallel_yield <= single_yield:
        return {
            "decision": "SERIALIZE_LOGICAL_3_ON_PHYSICAL_1",
            "physical_width": policy["single_physical_width"],
            "logical_branch_count": policy["logical_branch_count"],
            "single_yield": single_yield,
            "parallel_yield": parallel_yield,
            "reasons": ["NO_STRICT_VERIFIED_BENEFIT_YIELD_GAIN"],
        }

    reasons = budget_reasons(scenario["parallel"], policy["hard_budgets"])
    if reasons:
        return {
            "decision": "SERIALIZE_LOGICAL_3_ON_PHYSICAL_1",
            "physical_width": policy["single_physical_width"],
            "logical_branch_count": policy["logical_branch_count"],
            "single_yield": single_yield,
            "parallel_yield": parallel_yield,
            "reasons": reasons,
        }

    return {
        "decision": "WIDEN_PHYSICAL_TO_3",
        "physical_width": policy["parallel_physical_width"],
        "logical_branch_count": policy["logical_branch_count"],
        "single_yield": single_yield,
        "parallel_yield": parallel_yield,
        "reasons": ["VERIFIED_BENEFIT_YIELD_GAIN", "ALL_HARD_BUDGETS_PASS"],
    }


def frac_obj(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def main():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    src = doc["source_bindings"]

    exact_sources = [
        ("HEAD", src["participant_edge_doc_path"], src["participant_edge_doc_blob_sha"]),
        ("HEAD", src["dynamic_wave_delta_path"], src["dynamic_wave_delta_blob_sha"]),
        ("HEAD", src["multi_embodiment_fixture_path"], src["multi_embodiment_fixture_blob_sha"]),
    ]
    for ref, path, expected in exact_sources:
        actual = git_blob(ref, path)
        if actual != expected:
            fail("FAIL_SOURCE_BLOB_DRIFT:" + path)

    policy = doc["policy"]
    observed = []
    widened = 0
    serialized = 0
    held = 0

    for scenario in doc["scenarios"]:
        got = decide(scenario, policy)
        exp = scenario["expected"]
        if got["decision"] != exp["decision"]:
            fail("FAIL_DECISION:" + scenario["id"])
        if got["physical_width"] != exp["physical_width"]:
            fail("FAIL_PHYSICAL_WIDTH:" + scenario["id"])
        if got["logical_branch_count"] != exp["logical_branch_count"]:
            fail("FAIL_LOGICAL_BRANCH_COUNT:" + scenario["id"])
        if got["reasons"] != exp["reasons"]:
            fail("FAIL_REASONS:" + scenario["id"])

        if got["logical_branch_count"] != policy["logical_branch_count"]:
            fail("FAIL_LOGICAL_PARALLELITY_COLLAPSED:" + scenario["id"])

        widened += int(got["decision"] == "WIDEN_PHYSICAL_TO_3")
        serialized += int(got["decision"] == "SERIALIZE_LOGICAL_3_ON_PHYSICAL_1")
        held += int(got["decision"] == "HOLD_MEASURE_MORE_ON_PHYSICAL_1")
        observed.append({
            "id": scenario["id"],
            "decision": got["decision"],
            "physical_width": got["physical_width"],
            "logical_branch_count": got["logical_branch_count"],
            "single_benefit_yield": frac_obj(got["single_yield"]),
            "parallel_benefit_yield": frac_obj(got["parallel_yield"]),
            "reasons": got["reasons"],
        })

    if (widened, serialized, held) != (1, 4, 1):
        fail("FAIL_DECISION_CLASS_COUNTS")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_SUBSTRATE_LIGHT_BENEFIT_OOMPH_PARALLELISM_R0",
        "checked_out_head_sha": head,
        "scenario_count": len(observed),
        "widened_count": widened,
        "serialized_count": serialized,
        "held_for_measurement_count": held,
        "logical_branch_count_preserved": policy["logical_branch_count"],
        "fixture_semantic_sha256": canonical_sha(doc),
        "observed": observed,
        "rails": [
            "BENEFIT_OBSERVED_NE_BENEFIT_CAUSED",
            "BENEFIT_NE_AUTHORITY",
            "COOOMPH_NE_MAX_COMPUTE",
            "MASSIVE_PARALLELITY_NE_MASSIVE_SIMULTANEOUS_MATERIALIZATION",
            "SOURCE_EMISSION_RATE_NE_RECEIVER_CAPACITY",
            "LOGICAL_LANE_NE_WORKER",
            "ACCELERATION_NE_PROGRESS",
        ],
    }
    print(json.dumps(receipt, separators=(",", ":")))


if __name__ == "__main__":
    main()
