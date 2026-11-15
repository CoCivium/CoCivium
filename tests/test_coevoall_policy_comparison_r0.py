"""Falsify simplistic CoEvo policy-comparison universal-winner claims."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from coevoall_policy_comparison_r0 import fixture_read, project, validate


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = fixture_read()
        cls.report = project(cls.fixture)

    def test_frozen_wins_quiet_bounded_noise(self):
        record = next(x for x in self.report["records"] if x["scenario"] == "quiet")
        self.assertEqual(record["winner_by_toy_score"], "frozen")

    def test_qualified_wins_mixed_evidence(self):
        record = next(x for x in self.report["records"] if x["scenario"] == "mixed")
        self.assertEqual(record["winner_by_toy_score"], "evidence_qualified")
        self.assertGreater(record["strategies"]["evidence_qualified"]["counterfactual_utility"],
                           record["strategies"]["forced"]["counterfactual_utility"])

    def test_forced_wins_deliberately_underestimated_fixture(self):
        record = next(x for x in self.report["records"] if x["scenario"] == "underdetected")
        self.assertEqual(record["winner_by_toy_score"], "forced")
        self.assertEqual(record["strategies"]["forced"]["unreviewed_projected_changes"], 0)
        self.assertEqual(record["strategies"]["evidence_qualified"]["projected_changes"], 0)

    def test_frozen_wins_adversarial_false_suggested_gains(self):
        record = next(x for x in self.report["records"] if x["scenario"] == "adversarial")
        self.assertEqual(record["winner_by_toy_score"], "frozen")
        self.assertEqual(record["strategies"]["evidence_qualified"]["projected_changes"], 0)
        self.assertEqual(record["strategies"]["evidence_qualified"]["mock_review_rejections"], 4)

    def test_no_universal_winner_encoded(self):
        winners={x["winner_by_toy_score"] for x in self.report["records"]}
        self.assertEqual(winners, {"frozen", "forced", "evidence_qualified"})

    def test_all_effect_claims_are_zero(self):
        self.assertEqual(self.report["real_effect_count"], 0)
        self.assertFalse(self.report["external_receiver_ack"])
        for row in self.report["records"]:
            self.assertEqual(row["real_effect_count"], 0)
            for result in row["strategies"].values():
                self.assertEqual(result["real_effect_count"], 0)

    def test_unreviewed_forced_changes_surface(self):
        r=next(x for x in self.report["records"] if x["scenario"] == "adversarial")
        self.assertEqual(r["strategies"]["forced"]["unreviewed_projected_changes"], 4)
        self.assertEqual(r["strategies"]["evidence_qualified"]["unreviewed_projected_changes"], 0)

    def test_quiet_qualified_only_observes(self):
        r=next(x for x in self.report["records"] if x["scenario"] == "quiet")
        self.assertEqual(r["strategies"]["evidence_qualified"]["projected_changes"], 0)
        self.assertLess(r["strategies"]["evidence_qualified"]["counterfactual_utility"], 0)

    def test_reject_duplicate_event_id(self):
        f=copy.deepcopy(self.fixture)
        f["scenarios"][0]["events"][1]["id"]=f["scenarios"][0]["events"][0]["id"]
        with self.assertRaisesRegex(ValueError, "EVENT_ID_CONFLICT"):
            validate(f)

    def test_reject_claimed_effect_scope(self):
        f=copy.deepcopy(self.fixture)
        f["scope"]="REAL_DELETE_AND_EXECUTE"
        with self.assertRaisesRegex(ValueError, "EFFECT_SCOPE_MUST_BE_SYNTHETIC"):
            project(f)

    def test_reject_nonfinite_or_negative_cost(self):
        f=copy.deepcopy(self.fixture)
        f["scenarios"][0]["events"][0]["change_cost"]=-1
        with self.assertRaisesRegex(ValueError, "INVALID_COST_OR_REVIEW"):
            validate(f)
        f=copy.deepcopy(self.fixture)
        f["scenarios"][0]["events"][0]["estimated_gain"]=float("nan")
        with self.assertRaisesRegex(ValueError, "INVALID_QUANTITY"):
            validate(f)

    def test_reject_changed_nonclaim_set(self):
        f=copy.deepcopy(self.fixture)
        f["nonclaims"]=[]
        with self.assertRaisesRegex(ValueError, "NONCLAIMS_NOT_PINNED"):
            validate(f)

    def test_no_forced_real_action_even_in_forced_scenario(self):
        for r in self.report["records"]:
            self.assertEqual(r["strategies"]["forced"]["real_effect_count"], 0)
        self.assertIn("FORCED_MUTATION_IS_SIMULATED_ONLY", self.report["nonclaims"])


if __name__ == "__main__":
    unittest.main()
