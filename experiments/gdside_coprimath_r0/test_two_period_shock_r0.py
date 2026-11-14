"""Falsifiers for two-period paired synthetic ecological shock trial.

All checks run in ordinary and optimized Python. No external data or effects.
"""
import math
import unittest

import simulate
from two_period_shock_r0 import run_paired, summarize, ARMS, SCENARIOS


class TwoPeriodTests(unittest.TestCase):
    def test_two_arms_two_scenarios_all_policies(self):
        x = run_paired(1, "no_shock")
        self.assertEqual(set(x["arms"]), set(ARMS))
        for arm in ARMS:
            self.assertEqual(set(x["arms"][arm]), set(simulate.POLICIES))

    def test_matched_withdrawal_yields_same_ecological_stock(self):
        for seed in (1, 3, 11):
            for scenario in SCENARIOS:
                x = run_paired(seed, scenario)
                self.assertTrue(all(z <= 1e-7
                                    for z in x["matched_stock_gap_each_period"]))
                values = [x["arms"]["matched_budget"][p]["final_stock"]
                          for p in simulate.POLICIES]
                self.assertLess(max(values)-min(values), 1e-7)

    def test_same_exogenous_shock_reduces_stock(self):
        for policy in simulate.POLICIES:
            a = run_paired(7, "no_shock")["arms"]["matched_budget"][policy]
            b = run_paired(7, "shock_second_period")["arms"]["matched_budget"][policy]
            self.assertAlmostEqual(a["stock_after_first"], b["stock_after_first"])
            self.assertAlmostEqual(a["final_stock"]-b["final_stock"], 70.0, places=5)

    def test_baseline_ecological_budget_advantage_not_allocations(self):
        x = run_paired(1, "no_shock")["arms"]["original_unequal_budget"]
        self.assertGreater(x["gdside"]["final_stock"], x["supply"]["final_stock"])

    def test_policy_order_independent(self):
        first=run_paired(2, "shock_second_period")
        last=run_paired(2, "shock_second_period",
                        policy_order=tuple(reversed(simulate.POLICIES)))
        self.assertEqual(first["arms"], last["arms"])

    def test_deterministic(self):
        self.assertEqual(summarize(3), summarize(3))

    def test_rights_and_real_benefit_not_claimed(self):
        x=summarize(2)
        self.assertIn("NO_RECEIVER_ACK", x["nonclaims"])
        self.assertIn("NO_FIELD_ECONOMICS", x["nonclaims"])
        self.assertEqual(x["cross_branch"]["comparison"],
                         "QUALITATIVE_ONLY_NOT_COMMON_METRIC_SPACE")

    def test_invalid_parameters_fail_closed(self):
        for case in (
            {"seed":0,"scenario":"no_shock"},
            {"seed":True,"scenario":"no_shock"},
            {"seed":1,"scenario":"unknown"},
            {"seed":1,"scenario":"no_shock","initial_stock":float("nan")},
            {"seed":1,"scenario":"no_shock","initial_stock":-1},
            {"seed":1,"scenario":"no_shock","initial_stock":simulate.K+1},
            {"seed":1,"scenario":"no_shock","policy_order":("gdside",)},
        ):
            with self.subTest(case=str(case)):
                with self.assertRaises(ValueError):
                    run_paired(**case)
        for value in (0,-1,True,201):
            with self.subTest(seed_count=value):
                with self.assertRaises(ValueError):
                    summarize(seed_count=value)

    def test_satisfaction_bounded(self):
        x=run_paired(1, "shock_second_period")
        for arm in ARMS:
            for scores in x["arms"][arm].values():
                for field in ("mean_satisfaction", "mean_step_min", "worst_group_mean"):
                    self.assertGreaterEqual(scores[field],0)
                    self.assertLessEqual(scores[field],1)

    def test_shock_only_second_period(self):
        x=run_paired(3, "shock_second_period")
        y=run_paired(3, "no_shock")
        for arm in ARMS:
            for p in simulate.POLICIES:
                self.assertAlmostEqual(x["arms"][arm][p]["stock_after_first"],
                                       y["arms"][arm][p]["stock_after_first"])


if __name__ == "__main__":
    unittest.main()
