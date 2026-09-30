#!/usr/bin/env python3
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_metabolism_loop_r0.json")


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


def yield_fraction(obj):
    deeds = obj["verified_deeds"]
    benefit = obj["qualified_benefit_units"]
    if not isinstance(deeds, int) or deeds <= 0:
        fail("FAIL_VERIFIED_DEEDS")
    if not isinstance(benefit, int) or benefit < 0:
        fail("FAIL_QUALIFIED_BENEFIT")
    return Fraction(benefit, deeds)


def hard_budget_reasons(observed, budgets):
    mapping = [
        ("receiver_pressure", "receiver_pressure_max", "RECEIVER_PRESSURE_BUDGET_EXCEEDED"),
        ("proof_debt", "proof_debt_max", "PROOF_DEBT_BUDGET_EXCEEDED"),
        ("collision_risk", "collision_risk_max", "COLLISION_RISK_BUDGET_EXCEEDED"),
        ("human_attention_cost", "human_attention_cost_max", "HUMAN_ATTENTION_BUDGET_EXCEEDED"),
        ("compute_cost", "compute_cost_max", "COMPUTE_COST_BUDGET_EXCEEDED"),
    ]
    return [
        reason
        for metric, limit, reason in mapping
        if observed[metric] > budgets[limit]
    ]


def valid_sha256_hex(value):
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def step(state, wave, policy):
    before = dict(state)
    single_yield = yield_fraction(wave["single"])
    observed_yield = yield_fraction(wave["observed"])
    hard_reasons = hard_budget_reasons(wave["observed"], policy["hard_budgets"])

    if state["physical_width"] == policy["parallel_physical_width"] and hard_reasons:
        state["physical_width"] = policy["single_physical_width"]
        state["widen_streak"] = 0
        state["contract_streak"] = 0
        state["cooldown_remaining"] = policy["transition_cooldown_cycles"]
        action = "CONTRACT_TO_1_HARD_BUDGET"
    elif state["cooldown_remaining"] > 0:
        state["cooldown_remaining"] -= 1
        state["widen_streak"] = 0
        state["contract_streak"] = 0
        action = "HOLD_TRANSITION_COOLDOWN"
    elif wave["observed"]["counterfactual_confidence_bp"] < policy["counterfactual_confidence_floor_bp"]:
        state["widen_streak"] = 0
        state["contract_streak"] = 0
        action = "HOLD_LOW_COUNTERFACTUAL_CONFIDENCE"
    elif state["physical_width"] == policy["single_physical_width"]:
        strong_gain = (
            observed_yield * 10000
            >= single_yield * policy["widen_min_gain_bp"]
        )
        if strong_gain and not hard_reasons:
            state["widen_streak"] += 1
            state["contract_streak"] = 0
            if state["widen_streak"] >= policy["widen_consecutive_required"]:
                state["physical_width"] = policy["parallel_physical_width"]
                state["widen_streak"] = 0
                state["cooldown_remaining"] = policy["transition_cooldown_cycles"]
                action = "WIDEN_TO_3"
            else:
                action = (
                    f"HOLD_WIDEN_STREAK_{state['widen_streak']}"
                    f"_OF_{policy['widen_consecutive_required']}"
                )
        else:
            state["widen_streak"] = 0
            state["contract_streak"] = 0
            action = "HOLD_PHYSICAL_1_NO_WIDEN"
    else:
        if observed_yield <= single_yield:
            state["contract_streak"] += 1
            state["widen_streak"] = 0
            if state["contract_streak"] >= policy["contract_no_gain_consecutive_required"]:
                state["physical_width"] = policy["single_physical_width"]
                state["contract_streak"] = 0
                state["cooldown_remaining"] = policy["transition_cooldown_cycles"]
                action = "CONTRACT_TO_1_NO_GAIN_STREAK"
            else:
                action = (
                    f"HOLD_CONTRACT_STREAK_{state['contract_streak']}"
                    f"_OF_{policy['contract_no_gain_consecutive_required']}"
                )
        else:
            state["contract_streak"] = 0
            state["widen_streak"] = 0
            action = "HOLD_PHYSICAL_3_HYSTERESIS_BAND"

    state["logical_branch_count"] = policy["logical_branch_count"]
    return {
        "before": before,
        "after": dict(state),
        "action": action,
        "single_yield": single_yield,
        "observed_yield": observed_yield,
        "hard_budget_reasons": hard_reasons,
    }


def frac_obj(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def main():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    src = doc["source_bindings"]
    if git_blob("HEAD", src["benefit_oomph_fixture_path"]) != src["benefit_oomph_fixture_blob_sha"]:
        fail("FAIL_BENEFIT_OOMPH_SOURCE_DRIFT")

    policy = doc["policy"]
    state = dict(doc["initial_state"])
    receipts = []
    ledger = []

    counts = {
        "widen_transition_count": 0,
        "contract_transition_count": 0,
        "hard_budget_contract_count": 0,
        "cooldown_hold_count": 0,
        "low_confidence_hold_count": 0,
    }

    for wave in doc["waves"]:
        receipt = wave["wave_receipt_sha256"]
        if not valid_sha256_hex(receipt):
            fail("FAIL_WAVE_RECEIPT_SHA:" + wave["wave_id"])
        receipts.append(receipt)

        result = step(state, wave, policy)
        exp = wave["expected"]
        after = result["after"]

        checks = [
            ("physical_width_after", after["physical_width"]),
            ("widen_streak_after", after["widen_streak"]),
            ("contract_streak_after", after["contract_streak"]),
            ("cooldown_remaining_after", after["cooldown_remaining"]),
            ("action", result["action"]),
        ]
        for key, got in checks:
            if exp[key] != got:
                fail(f"FAIL_EXPECTED:{wave['wave_id']}:{key}:{got}")

        if after["logical_branch_count"] != policy["logical_branch_count"]:
            fail("FAIL_LOGICAL_PARALLELITY_COLLAPSED:" + wave["wave_id"])

        counts["widen_transition_count"] += int(result["action"] == "WIDEN_TO_3")
        is_contract = result["action"].startswith("CONTRACT_TO_1")
        counts["contract_transition_count"] += int(is_contract)
        counts["hard_budget_contract_count"] += int(result["action"] == "CONTRACT_TO_1_HARD_BUDGET")
        counts["cooldown_hold_count"] += int(result["action"] == "HOLD_TRANSITION_COOLDOWN")
        counts["low_confidence_hold_count"] += int(result["action"] == "HOLD_LOW_COUNTERFACTUAL_CONFIDENCE")

        ledger.append({
            "wave_id": wave["wave_id"],
            "wave_receipt_sha256": receipt,
            "before": result["before"],
            "after": result["after"],
            "action": result["action"],
            "single_benefit_yield": frac_obj(result["single_yield"]),
            "observed_benefit_yield": frac_obj(result["observed_yield"]),
            "hard_budget_reasons": result["hard_budget_reasons"],
        })

    summary = {
        "wave_count": len(doc["waves"]),
        **counts,
        "final_physical_width": state["physical_width"],
        "logical_branch_count_preserved": state["logical_branch_count"],
        "receipt_count": len(receipts),
        "unique_receipt_count": len(set(receipts)),
    }
    if summary != doc["expected_summary"]:
        fail("FAIL_SUMMARY:" + json.dumps({"observed": summary, "expected": doc["expected_summary"]}, sort_keys=True))

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_SUBSTRATE_LIGHT_CLOSED_LOOP_METABOLISM_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(doc),
        "summary": summary,
        "transition_ledger": ledger,
        "final_state": state,
        "rails": [
            "RECEIPT_BACKED_OBSERVATION_BEFORE_WIDTH_REVISION",
            "HARD_BUDGET_BREACH_CONTRACTS_IMMEDIATELY",
            "HYSTERESIS_BEFORE_NONSAFETY_WIDTH_TRANSITION",
            "TRANSITION_COOLDOWN_BLOCKS_NONSAFETY_REVERSAL",
            "LOGICAL_PARALLELITY_NE_PHYSICAL_WIDTH",
            "BENEFIT_OBSERVED_NE_BENEFIT_CAUSED",
            "BENEFIT_NE_AUTHORITY",
            "VALIDATION_IS_NOT_ACCEPTANCE",
        ],
    }
    print(json.dumps(receipt, separators=(",", ":")))


if __name__ == "__main__":
    main()
