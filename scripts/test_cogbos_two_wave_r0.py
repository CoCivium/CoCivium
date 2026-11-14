#!/usr/bin/env python3
import unittest
from cogbos_two_wave_r0 import Proposal, SOURCE_BLOB_SHA, digest, elect, run_demo

class TwoWaveProofTests(unittest.TestCase):
    def setUp(self):
        self.baseline = digest({"version": "baseline"})

    def test_duplicate_input_is_deterministic(self):
        self.assertEqual(run_demo(), run_demo())

    def test_two_waves_have_distinct_methods(self):
        r = run_demo()
        self.assertEqual(r["wave_count"], 2)
        self.assertGreaterEqual(len(r["distinct_strategies"]), 4)

    def test_source_collision_rejected_even_with_high_score(self):
        p = [Proposal("impostor", 1, "probe", "0"*40, True, 999, "a")]
        r = elect(p, {"a"}, self.baseline)
        self.assertIsNone(r["winner"])
        self.assertIn("SOURCE_MISMATCH", r["rejected"][0]["reasons"])

    def test_missing_consent_rejected(self):
        p = [Proposal("no_permission", 1, "probe", SOURCE_BLOB_SHA, False, 999, "a")]
        self.assertIn("CONSENT_MISSING", elect(p, {"a"}, self.baseline)["rejected"][0]["reasons"])

    def test_unapproved_writer_rejected(self):
        p = [Proposal("rogue", 1, "probe", SOURCE_BLOB_SHA, True, 999, "rogue")]
        self.assertIn("WRITER_UNAUTHORIZED", elect(p, {"a"}, self.baseline)["rejected"][0]["reasons"])

    def test_single_elected_actuator_even_with_tie(self):
        p = [Proposal("b", 1, "probe", SOURCE_BLOB_SHA, True, 2, "b"),
             Proposal("a", 1, "probe", SOURCE_BLOB_SHA, True, 2, "a")]
        r = elect(p, {"a", "b"}, self.baseline)
        self.assertEqual(r["winner"], "a")
        self.assertEqual(r["actuator"], "a")

    def test_failure_preserves_previous_state(self):
        r = run_demo()
        self.assertEqual(r["wave2"]["disposition"], "ROLLBACK_TO_BASELINE")
        self.assertEqual(r["wave2"]["selected_state"], r["wave1"]["selected_state"])

    def test_not_receiver_ack(self):
        r = run_demo()
        self.assertIsNone(r["receiver"]["ack"])
        self.assertEqual(r["deployment"], "NONE")
        self.assertIn("NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF", r["nonclaims"])

    def test_no_eligible_preserves_initial_baseline(self):
        r = elect([], {"a"}, self.baseline)
        self.assertEqual(r["selected_state"], self.baseline)
        self.assertIsNone(r["actuator"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
