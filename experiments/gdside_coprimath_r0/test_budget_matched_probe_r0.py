"""Adversarial budget-matched counterfactual tests; ordinary and optimized Python."""
import copy
import math
import random
import unittest

import simulate
from budget_matched_probe_r0 import compare_one_scene, summarize, STOCKS


class MatchedBudgetTests(unittest.TestCase):
    def world(self):
        return simulate.conditions(1, 1)[0]

    def test_same_budget_across_all_policies(self):
        world = self.world()
        outcomes = [
            compare_one_scene(policy, world, 600.0, random.Random(100))
            for policy in simulate.POLICIES
        ]
        budgets = [x["matched"]["extraction"] for x in outcomes]
        self.assertLess(max(budgets) - min(budgets), 1e-6)
        self.assertTrue(all(x["matched"]["extraction"] <= 84.0 + 1e-6
                            for x in outcomes))

    def test_original_budget_inequality_exposed(self):
        world = self.world()
        result = {policy: compare_one_scene(policy, world, 600.0, random.Random(100))
                  for policy in simulate.POLICIES}
        self.assertLess(result["gdside"]["baseline"]["extraction"],
                        result["hybrid"]["baseline"]["extraction"])
        self.assertLess(result["hybrid"]["baseline"]["extraction"],
                        result["supply"]["baseline"]["extraction"])

    def test_normalization_preserves_policy_shares(self):
        result = compare_one_scene("gdside", self.world(), 600.0,
                                   random.Random(100))
        a, b = result["raw_allocation"], result["matched_allocation"]
        self.assertEqual(len(a), len(b))
        scales = [y/x for x, y in zip(a, b) if x > 0]
        self.assertTrue(scales)
        self.assertLess(max(scales)-min(scales), 1e-8)

    def test_no_impossible_satisfaction(self):
        result = summarize(3, 3, (350.0, 1000.0))
        for case in result["cases"].values():
            self.assertLessEqual(case["max_matched_budget_difference"], 1e-6)
            for mode in ("baseline", "matched"):
                for scores in case["policies"][mode].values():
                    for key in ("mean_satisfaction", "mean_step_min", "worst_group_mean"):
                        self.assertTrue(0 <= scores[key] <= 1)

    def test_deterministic_with_same_seed_and_budget(self):
        self.assertEqual(summarize(2, 3, (350.0,)), summarize(2, 3, (350.0,)))

    def test_zero_or_invalid_parameters_fail_closed(self):
        for kwargs in ({"seed_count":0}, {"seed_count":True},
                       {"steps":0}, {"steps":True}, {"stocks":()},
                       {"stocks":(350.0, 350.0)}, {"stocks":(float("nan"),)},
                       {"stocks":(float("inf"),)}, {"stocks":(-1.0,)}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    summarize(**kwargs)

    def test_unknown_policy_rejected_even_optimized(self):
        with self.assertRaises(ValueError):
            compare_one_scene("magic", self.world(), 600.0, random.Random(1))

    def test_negative_world_data_rejected(self):
        bad = copy.deepcopy(self.world())
        bad["productivity"][0] = float("nan")
        with self.assertRaisesRegex(ValueError, "INVALID_EFFICIENCY"):
            compare_one_scene("hybrid", bad, 600.0, random.Random(1))

    def test_cross_model_not_fabricated_numeric_comparison(self):
        report = summarize(2, 2, (600.0,))
        cross = report["cross_model"]
        self.assertEqual(cross["status"],
                         "QUALITATIVE_CROSSWALK_ONLY_NOT_NUMERICALLY_COMPARABLE")
        self.assertIn("NO_REAL_ECONOMIC_DATA", report["nonclaims"])
        self.assertIn("NO_INDEPENDENT_RECEIVER_ACK", report["nonclaims"])

    def test_shared_exogenous_world_seed(self):
        self.assertEqual(simulate.conditions(7, 5), simulate.conditions(7, 5))
        self.assertNotEqual(simulate.conditions(7, 5), simulate.conditions(8, 5))


if __name__ == "__main__":
    unittest.main()
