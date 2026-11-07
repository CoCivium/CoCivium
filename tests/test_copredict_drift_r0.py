"""Deterministic local-order/global-drift counterfactual, no live system effects."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai" / "measurement"))
from copredict_drift_r0 import (
    RULES, compare_sorting, decision_from_evidence, qualify_hypothesis,
    validate_proposals,
)

FIX = ROOT / "ai" / "measurement" / "copredict_drift_fixture_r0.json"
EARLY = "2026-11-07T20:36:00Z"
LATE = "2026-11-10T20:12:14Z"


class CoPredictDriftR0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIX.read_text(encoding="utf-8"))

    def clone(self):
        return copy.deepcopy(self.fixture)

    def assert_bad(self, p, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            validate_proposals(p)

    def test_valid_synthetic_only(self):
        p = self.clone()["proposals"]
        sessions = validate_proposals(p)
        self.assertEqual(set(sessions), {"A", "B"})
        self.assertEqual([len(v) for v in sessions.values()], [6, 6])

    def test_local_fifo_does_not_imply_global_semantic_alignment(self):
        r = compare_sorting(self.clone()["proposals"])
        self.assertTrue(r["local_queue_sequences_ordered"])
        self.assertEqual(r["name_only_false_merge_count"], 3)
        self.assertEqual(r["name_only_false_merge_labels"],
                         ["conull", "copixel", "cotick"])
        self.assertEqual(r["typed_conflict_holds"], 3)
        self.assertEqual(r["name_only_alias_split_count"], 3)
        self.assertEqual(r["typed_aliases_preserved"], 3)

    def test_all_three_alias_pairs_remain_inspectable(self):
        r = compare_sorting(self.clone()["proposals"])
        self.assertEqual(r["same_definition_different_label_aliases"], [
            ["CoGauge", "Gauge"],
            ["CoReceipt", "Receipt"],
            ["CoSeed", "Seed"],
        ])

    def test_two_source_claims_dont_become_proof_or_canon(self):
        r = compare_sorting(self.clone()["proposals"])
        self.assertEqual(r["independent_receiver_ack_count"], 0)
        self.assertEqual(r["accepted_canonical_units"], 0)
        self.assertEqual(r["auto_executed_changes"], 0)
        self.assertEqual(r["outcome"], "HOLD_CONFLICTS_PRESERVE_ALIASES")

    def test_no_80_20_or_os_removal_claim(self):
        r = compare_sorting(self.clone()["proposals"])
        self.assertIn("NO_AUTOMATIC_OS_FALLBACK_REMOVAL", r["nonclaims"])
        self.assertIn("LOCAL_FIFO_NE_GLOBAL_CONSENSUS", RULES)
        self.assertIn("NO_NEW_SCHEDULER", RULES)
        self.assertIn("NOT_80_20_MEASURED",
                      self.fixture["nonclaims"])

    def test_malformed_real_session_claim_is_rejected(self):
        p = self.clone()["proposals"]
        p[0]["evidence_class"] = "ACTUAL_LIVE_AI"
        self.assert_bad(p, "UNVERIFIED_REAL_SESSION_CLAIM")

    def test_no_duplicate_claim_or_session_sequence(self):
        p = self.clone()["proposals"]
        p[1]["claim_id"] = p[0]["claim_id"]
        self.assert_bad(p, "DUPLICATE_CLAIM_ID")
        p = self.clone()["proposals"]
        p[1]["sequence"] = p[0]["sequence"]
        self.assert_bad(p, "LOCAL_SEQUENCE_NOT_ORDERED")

    def test_missing_method_cannot_be_deduped(self):
        p = self.clone()["proposals"]
        p[0]["method_id"] = ""
        self.assert_bad(p, "IDENTITY_OR_SCOPE_REQUIRED:method_id")

    def test_forecast_is_falsifiable_conditional_not_probability(self):
        f = self.clone()["hypothesis"]
        self.assertIn("At least two independently authenticated",
                      f["exposure_condition"])
        self.assertIn("paired proposal", f["event_definition"])
        self.assertIsNone(f["probability"])
        self.assertEqual(qualify_hypothesis(f, EARLY),
                         "PENDING_HYPOTHESIS_NOT_SCORED")

    def test_no_unsourced_numeric_confidence(self):
        f = self.clone()["hypothesis"]
        f["probability"] = 0.8
        with self.assertRaisesRegex(ValueError, "UNSOURCED_NUMERIC_CONFIDENCE"):
            qualify_hypothesis(f, EARLY)

    def test_no_predeclared_hit_or_miss(self):
        f = self.clone()["hypothesis"]
        f["actual_outcome"] = "HIT"
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_HIT_OR_MISS"):
            qualify_hypothesis(f, EARLY)

    def test_no_false_resolution_by_renaming_status(self):
        f = self.clone()["hypothesis"]
        f["status"] = "PASS_FOR_FORECAST"
        with self.assertRaisesRegex(ValueError, "NO_FALSE_FORECAST_RESOLUTION"):
            qualify_hypothesis(f, EARLY)

    def test_no_advance_hard_fail_rules(self):
        f = self.clone()["hypothesis"]
        f["no_preemptive_actuation"] = False
        with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_PREEMPTIVE_CONTROL"):
            qualify_hypothesis(f, EARLY)

    def test_current_review_carrier_cannot_be_replaced(self):
        f = self.clone()["hypothesis"]
        f["review_carrier"] = "ANOTHER_NEW_SCHEDULER"
        with self.assertRaisesRegex(ValueError, "DUPLICATE_REVIEW_CARRIER"):
            qualify_hypothesis(f, EARLY)

    def test_deadline_without_eligible_observations_is_censored(self):
        f = self.clone()["hypothesis"]
        self.assertEqual(qualify_hypothesis(f, LATE),
                         "HOLD_CENSORED_OR_REQUIRES_INDEPENDENT_OUTCOME_AUDIT")
        self.assertEqual(decision_from_evidence(f, [], LATE),
                         "CENSORED_NO_INDEPENDENT_OBSERVATIONS")

    def test_claimed_receipts_not_independently_authenticated_here(self):
        f = self.clone()["hypothesis"]
        forged = [{"session": "A", "result": "HIT"},
                  {"session": "B", "result": "HIT"}]
        self.assertEqual(decision_from_evidence(f, forged, LATE),
                         "HOLD_EXTERNAL_RECEIVER_ATTESTATION_REQUIRED")
        self.assertEqual(decision_from_evidence(f, forged, EARLY),
                         "PENDING_HYPOTHESIS_NOT_SCORED")

    def test_future_observation_cannot_claim_earlier_issue_date(self):
        f = self.clone()["hypothesis"]
        f["issued_date"] = "2026-11-12"
        with self.assertRaisesRegex(ValueError, "ISSUE_DATE_NOT_FIXED"):
            qualify_hypothesis(f, EARLY)

    def test_fan_in_deadline_is_explicit_utc(self):
        f = self.clone()["hypothesis"]
        self.assertEqual(f["target_deadline_utc"], "2026-11-10T20:12:13Z")
        f["target_deadline_utc"] = "2026-11-10 20:12 local"
        with self.assertRaisesRegex(ValueError, "UTC_TIMESTAMP_REQUIRED"):
            qualify_hypothesis(f, EARLY)


if __name__ == "__main__":
    unittest.main()
