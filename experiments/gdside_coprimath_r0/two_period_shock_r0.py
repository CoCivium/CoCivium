#!/usr/bin/env python3
"""Two-period paired ecological-shock falsifier. Toy model, not economics.

Uses the existing matched-budget allocator and stock transition from simulate.
All policies see identical exogenous shocks and stock on the matched arm.
The source stock law depends only on withdrawal, not which group receives it:
equal withdrawal therefore cannot create an ecological advantage by policy.
"""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import mean

import simulate
from budget_matched_probe_r0 import compare_one_scene

SCENARIOS = ("no_shock", "shock_second_period")
ARMS = ("original_unequal_budget", "matched_budget")
METRICS = ("mean_satisfaction", "mean_step_min", "worst_group_mean",
           "mean_output", "mean_extraction", "toy_below_half_per_step",
           "stock_after_first", "final_stock")
SHOCK_UNITS = -70.0


def require(ok, message):
    if not ok:
        raise ValueError("HOLD_TWO_PERIOD: " + message)


def run_paired(seed, scenario, initial_stock=600.0,
               policy_order=simulate.POLICIES):
    require(type(seed) is int and seed >= 1, "INVALID_SEED")
    require(scenario in SCENARIOS, "UNKNOWN_SCENARIO")
    require(type(initial_stock) in (float, int) and
            math.isfinite(initial_stock) and 0 < initial_stock <= simulate.K,
            "INVALID_INITIAL_STOCK")
    require(type(policy_order) in (list, tuple) and
            len(policy_order) == len(simulate.POLICIES) and
            set(policy_order) == set(simulate.POLICIES),
            "INVALID_POLICY_SET")

    world = simulate.conditions(seed, 2)
    stocks = {arm: {policy: float(initial_stock) for policy in policy_order}
              for arm in ARMS}
    rng = {arm: {policy: random.Random(seed + 991832)
                 for policy in policy_order} for arm in ARMS}
    traces = {arm: {policy: [] for policy in policy_order} for arm in ARMS}
    matched_stock_gaps = []

    for t in range(2):
        scene = dict(world[t])
        scene["shock"] = scenario == "shock_second_period" and t == 1
        for arm in ARMS:
            for policy in policy_order:
                stock = stocks[arm][policy]
                matched = compare_one_scene(policy, scene, stock,
                                            rng[arm][policy])
                outcome = matched["matched" if arm == "matched_budget"
                                  else "baseline"]
                withdrawal = outcome["extraction"]
                simulate.checked_extraction(
                    matched["matched_allocation" if arm == "matched_budget"
                            else "raw_allocation"], stock, len(simulate.NEEDS))
                regeneration = 0.27 * stock * (1 - stock / simulate.K)
                disruption = (SHOCK_UNITS if scene["shock"] else 0.0) + scene["replenishment"]
                updated_stock = max(0.0, min(simulate.K,
                                            stock + regeneration - withdrawal + disruption))
                require(math.isfinite(updated_stock), "NONFINITE_STOCK")
                stocks[arm][policy] = updated_stock
                traces[arm][policy].append({
                    "stock_before": stock,
                    "stock_after": updated_stock,
                    "withdrawal": withdrawal,
                    "satisfaction": outcome["satisfaction"],
                    "output": outcome["output"],
                    "toy_below_half": outcome["groups_below_half"],
                })
        row = list(stocks["matched_budget"].values())
        gap = max(row) - min(row)
        require(gap <= 1e-7, "POLICY_STOCK_DIFFERENCE_UNDER_EQUAL_WITHDRAWAL")
        matched_stock_gaps.append(gap)

    scores = {}
    for arm in ARMS:
        scores[arm] = {}
        for policy in policy_order:
            periods = traces[arm][policy]
            groups = len(simulate.NEEDS)
            group_means = [mean(row["satisfaction"][i] for row in periods)
                           for i in range(groups)]
            scores[arm][policy] = {
                "mean_satisfaction": mean(mean(row["satisfaction"]) for row in periods),
                "mean_step_min": mean(min(row["satisfaction"]) for row in periods),
                "worst_group_mean": min(group_means),
                "mean_output": mean(row["output"] for row in periods),
                "mean_extraction": mean(row["withdrawal"] for row in periods),
                "toy_below_half_per_step": mean(row["toy_below_half"] for row in periods),
                "stock_after_first": periods[0]["stock_after"],
                "final_stock": periods[1]["stock_after"],
            }

    # Explicitly check the matched budget at the same time and stock.
    require(all(max(scores["matched_budget"][p]["final_stock"]
                    for p in policy_order) -
                min(scores["matched_budget"][p]["final_stock"]
                    for p in policy_order) <= 1e-7 for _ in (0,)),
            "FINAL_STOCK_NOT_MATCHED")
    return {
        "seed": seed, "scenario": scenario,
        "matched_stock_gap_each_period": matched_stock_gaps,
        "arms": scores,
    }


def summarize(seed_count=80, initial_stock=600.0):
    require(type(seed_count) is int and 1 <= seed_count <= 200, "SEED_BUDGET")
    trials = {scenario: [run_paired(seed, scenario, initial_stock)
                         for seed in range(1, seed_count + 1)]
              for scenario in SCENARIOS}
    summaries = {}
    for scenario, rows in trials.items():
        arms = {}
        for arm in ARMS:
            arms[arm] = {}
            for policy in simulate.POLICIES:
                arms[arm][policy] = {
                    key: round(mean(row["arms"][arm][policy][key]
                                    for row in rows), 6)
                    for key in METRICS
                }
        matched_range = max(
            x["final_stock"] for x in arms["matched_budget"].values()
        ) - min(
            x["final_stock"] for x in arms["matched_budget"].values()
        )
        require(matched_range <= 1e-6,
                "AGGREGATE_MATCHED_STOCK_DIFFERENCE")
        summaries[scenario] = {
            "arms": arms,
            "max_per_seed_stock_gap": round(max(
                max(row["matched_stock_gap_each_period"]) for row in rows), 12),
            "mean_final_stock_range_matched": round(matched_range, 9),
            "baseline_gdside_minus_supply_final_stock": round(
                arms["original_unequal_budget"]["gdside"]["final_stock"] -
                arms["original_unequal_budget"]["supply"]["final_stock"], 6),
        }

    paired_deltas = {
        policy: round(
            summaries["shock_second_period"]["arms"]["matched_budget"][policy]["final_stock"] -
            summaries["no_shock"]["arms"]["matched_budget"][policy]["final_stock"], 6)
        for policy in simulate.POLICIES
    }
    require(all(x < 0 for x in paired_deltas.values()),
            "SHOCK_CONTROL_DID_NOT_LOWER_STOCK")
    return {
        "schema": "CoAll.GdSide.TwoPeriodShockMatchedR0",
        "scope": "SYNTHETIC_TWO_PERIOD_PAIRED_COUNTERFACTUAL_ONLY",
        "simulator_sha256": hashlib.sha256(
            Path(simulate.__file__).read_bytes()).hexdigest(),
        "budget_probe_sha256": hashlib.sha256(
            Path(compare_one_scene.__code__.co_filename).read_bytes()).hexdigest(),
        "source_contract": "Original model stock(t+1) depends on total withdrawal and exogenous disturbance only",
        "seed_count": seed_count, "periods": 2,
        "initial_stock": initial_stock, "step_2_shock_units": SHOCK_UNITS,
        "policy_order": list(simulate.POLICIES),
        "arms": list(ARMS), "scenarios": summaries,
        "shock_minus_control_final_stock_matched": paired_deltas,
        "falsifiable_conclusion": (
            "In this declared simulator equal policy withdrawals produce identical ecological "
            "stock in each scenario, even under shared period-2 shocks. The prior "
            "ecological advantage is not evidence that allocation shares cause stock gain."
        ),
        "cross_branch": {
            "candidate": "CoCivium/CoCivium PR #379 @ 3f84bb821e59300d2a11b5363ce2a9fd5a74059a",
            "comparison": "QUALITATIVE_ONLY_NOT_COMMON_METRIC_SPACE",
            "reason": "Pareto/rights fixture outcomes are exogenous toy vectors, not mappings from these stock/satisfaction variables.",
        },
        "nonclaims": ["NO_FIELD_ECONOMICS", "NO_CAUSAL_VALIDATION",
                      "NO_REAL_RIGHTS_OR_WELFARE_MEASUREMENT",
                      "NO_RECEIVER_ACK", "NO_DEPLOYMENT", "NO_DIVINE_OR_NORMATIVE_AUTHORITY"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=80)
    parser.add_argument("--initial-stock", type=float, default=600.0)
    args = parser.parse_args()
    print(json.dumps(summarize(args.seeds, args.initial_stock),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
