#!/usr/bin/env python3
"""Matched-withdrawal single-step counterfactual, NOT an economic field result.

Reuses the public simulate.py's demand/productivity streams and allocations.
Paired scenes use identical seed, step, stock and feasible extraction budget.
A normalized policy allocation is an analysis-only reweighting, NOT an actual
policy re-optimization at a new budget. No stock is carried between steps:
ecology, recovery, shocks and causal welfare claims are outside this test.
"""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import simulate

STOCKS = (350.0, 600.0, 1000.0)
BASE_FACTORS = {"demand": 1.0, "supply": 1.0, "hybrid": 0.92,
                "gdside": 0.84, "random": 1.0}
SCOPED_METRICS = ("mean_satisfaction", "mean_step_min", "mean_output",
                  "mean_extraction", "groups_below_half_per_step")


def require(condition, reason):
    if not condition:
        raise ValueError("HOLD_BUDGET_MATCH: " + reason)


def compare_one_scene(policy, world, stock, rng):
    """Return paired baseline and matched one-step outcomes with shared RNG."""
    require(policy in simulate.POLICIES, "UNKNOWN_POLICY")
    require(type(stock) in (float, int) and math.isfinite(stock) and stock > 0,
            "INVALID_STOCK")
    needs = [n * x for n, x in zip(simulate.NEEDS, world["demand"])]
    efficiency = [e * x for e, x in zip(simulate.EFF, world["productivity"])]
    require(all(math.isfinite(n) and n > 0 for n in needs), "INVALID_NEED")
    require(all(math.isfinite(e) and e > 0 for e in efficiency),
            "INVALID_EFFICIENCY")
    feasible = min(0.14 * stock, sum(n / e for n, e in zip(needs, efficiency)))

    raw = simulate.policy_action(policy, needs, efficiency,
                                 simulate.WEALTH, stock, rng)
    raw_total = simulate.checked_extraction(raw, stock, len(needs))
    require(abs(raw_total - feasible * BASE_FACTORS[policy]) <= 1e-6,
            "SIMULATOR_BUDGET_FACTORS_CHANGED_REVIEW_REQUIRED")
    if feasible == 0:
        matched = [0.0] * len(needs)
    else:
        require(raw_total > 0, "ZERO_RAW_WITH_POSITIVE_FEASIBLE")
        matched = [x * (feasible / raw_total) for x in raw]
    matched_total = simulate.checked_extraction(matched, stock, len(needs))
    require(abs(matched_total - feasible) <= 1e-6,
            "MATCHED_WITHDRAWAL_MISMATCH")

    def summarize(alloc, extraction):
        produced = [a * e for a, e in zip(alloc, efficiency)]
        satisfaction = [min(1.0, p / n) for p, n in zip(produced, needs)]
        return {
            "extraction": extraction,
            "satisfaction": satisfaction,
            "output": sum(produced),
            "groups_below_half": sum(x < 0.5 for x in satisfaction),
        }

    return {"baseline": summarize(raw, raw_total),
            "matched": summarize(matched, matched_total),
            "feasible": feasible,
            "raw_allocation": raw, "matched_allocation": matched}


def summarize(seed_count=80, steps=36, stocks=STOCKS):
    require(type(seed_count) is int and 1 <= seed_count <= 500,
            "INVALID_SEED_COUNT")
    require(type(steps) is int and 1 <= steps <= 366, "INVALID_STEPS")
    require(type(stocks) in (tuple, list) and bool(stocks), "NO_STOCKS")
    require(len(set(stocks)) == len(stocks), "DUPLICATE_STOCK")
    for stock in stocks:
        require(type(stock) in (float, int) and math.isfinite(stock) and stock > 0,
                "INVALID_STOCK")
    result = {}
    for stock in stocks:
        totals = {
            mode: {
                policy: {"count": 0, "satisfaction_sum": 0.0, "min_sum": 0.0,
                         "output_sum": 0.0, "extraction_sum": 0.0,
                         "below_sum": 0, "group_sums": [0.0] * len(simulate.NEEDS)}
                for policy in simulate.POLICIES
            } for mode in ("baseline", "matched")
        }
        max_budget_difference = 0.0
        for seed in range(1, seed_count + 1):
            worlds = simulate.conditions(seed, steps)
            rngs = {p: random.Random(seed + 991832) for p in simulate.POLICIES}
            for world in worlds:
                per_policy_budgets = []
                for policy in simulate.POLICIES:
                    paired = compare_one_scene(policy, world, stock, rngs[policy])
                    per_policy_budgets.append(paired["matched"]["extraction"])
                    for mode in ("baseline", "matched"):
                        val = paired[mode]
                        acc = totals[mode][policy]
                        acc["count"] += 1
                        acc["satisfaction_sum"] += sum(val["satisfaction"]) / len(val["satisfaction"])
                        acc["min_sum"] += min(val["satisfaction"])
                        acc["output_sum"] += val["output"]
                        acc["extraction_sum"] += val["extraction"]
                        acc["below_sum"] += val["groups_below_half"]
                        for i, score in enumerate(val["satisfaction"]):
                            acc["group_sums"][i] += score
                gap = max(per_policy_budgets) - min(per_policy_budgets)
                max_budget_difference = max(max_budget_difference, gap)
                require(gap <= 1e-6, "POLICIES_DID_NOT_RECEIVE_MATCHED_BUDGET")
        case = {}
        for mode, policies in totals.items():
            case[mode] = {}
            for policy, t in policies.items():
                n = t["count"]
                require(n == seed_count * steps, "FRAME_COUNT")
                case[mode][policy] = {
                    "mean_satisfaction": round(t["satisfaction_sum"] / n, 6),
                    "mean_step_min": round(t["min_sum"] / n, 6),
                    "mean_output": round(t["output_sum"] / n, 6),
                    "mean_extraction": round(t["extraction_sum"] / n, 6),
                    "groups_below_half_per_step": round(t["below_sum"] / n, 6),
                    "worst_group_mean": round(min(t["group_sums"]) / n, 6),
                }
        result[str(int(stock) if float(stock).is_integer() else stock)] = {
            "fixed_source_stock": stock,
            "paired_frames_per_policy": seed_count * steps,
            "max_matched_budget_difference": round(max_budget_difference, 12),
            "policies": case,
            "gdside_minus_hybrid_matched": {
                metric: round(case["matched"]["gdside"][metric] -
                              case["matched"]["hybrid"][metric], 6)
                for metric in SCOPED_METRICS
            },
        }
    return {
        "schema": "CoAll.GdSide.FixedStockMatchedBudgetProbe.R0",
        "scope": "SYNTHETIC_SINGLE_STEP_PAIRED_ALLOCATION_ONLY",
        "simulator_sha256": hashlib.sha256(
            Path(simulate.__file__).read_bytes()).hexdigest(),
        "seeds": seed_count, "steps": steps, "stock_levels": list(stocks),
        "baseline_policy_budget_factors": BASE_FACTORS,
        "cases": result,
        "interpretation": [
            "Original policy factors are unequal; matching extraction isolates the allocation-shares question.",
            "Input worlds are paired, but this is not a matched-compute-time or learned-policy comparison.",
            "Fixed stock is reset every step. Ecology, dynamic resilience, rights and future welfare are not scored.",
            "Synthetic satisfaction is defined by the fixture, not an observed human outcome.",
            "No universal winning policy, causal proof or choice of societal values follows.",
        ],
        "cross_model": {
            "other_source": "CoCivium/CoCivium PR #379 @ 3f84bb821e59300d2a11b5363ce2a9fd5a74059a",
            "status": "QUALITATIVE_CROSSWALK_ONLY_NOT_NUMERICALLY_COMPARABLE",
            "unobserved_axes": ["knowledge", "optionality", "harm", "rights/consent"],
        },
        "nonclaims": ["NO_REAL_ECONOMIC_DATA", "NO_ECOLOGICAL_TIME_SERIES",
                      "NO_INDEPENDENT_RECEIVER_ACK", "NO_CAUSAL_EFFECT",
                      "NO_GDSIDE_PRIVILEGE", "NO_CANON", "NO_RUNTIME"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=80)
    parser.add_argument("--steps", type=int, default=36)
    args = parser.parse_args()
    print(json.dumps(summarize(args.seeds, args.steps), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
