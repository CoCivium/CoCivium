"""Fail-closed, no-network, synthetic tests for CounterContagion+ R0."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from counter_contagion_r0 import Held, validate_pair, evaluate, scenario

P = Path(__file__).parent
BASE = json.loads((P / "counter_contagion_fixture.json").read_text(encoding="utf-8"))


class CounterContagionR0(unittest.TestCase):
    def test_fixture_binds(self):
        self.assertIsNone(validate_pair(BASE))

    def test_deterministic(self):
        self.assertEqual(evaluate(BASE), evaluate(copy.deepcopy(BASE)))

    def test_source_copy_ne_independence(self):
        x = evaluate(BASE)
        self.assertEqual(x["source_copies"], 3)
        self.assertEqual(x["distinct_source_families"], 1)
        self.assertIsNone(x["independent_source_verification"])

    def test_three_baselines(self):
        x = evaluate(BASE)
        self.assertEqual([x[k]["uncorrected_exposure_ticks"] for k in (
            "baseline_without_correction", "scheduled_correction", "early_correction")], [27, 12, 2])

    def test_receiver_lag(self):
        x = evaluate(BASE)
        self.assertEqual(x["scheduled_correction"]["receiver_notice_lag_ticks"], 2)
        self.assertEqual(x["early_correction"]["receiver_notice_lag_ticks"], 0)
        self.assertIsNone(x["baseline_without_correction"]["receiver_notice_lag_ticks"])

    def test_unknown_benefit_and_ack(self):
        x = evaluate(BASE)
        for name in ("baseline_without_correction", "scheduled_correction", "early_correction"):
            self.assertIsNone(x[name]["correction_truth_independently_verified"])
            self.assertIsNone(x[name]["correction_receiver_acknowledged"])
            self.assertIsNone(x[name]["real_world_harm_reduced"])
        self.assertIsNone(x["speedo_shadow_projection"]["verified_receiver_benefit"])

    def test_no_auto_oomph_effect(self):
        x = evaluate(BASE)
        self.assertFalse(x["oomph_shadow_projection"]["automatic_acceleration"])
        self.assertEqual(x["oomph_shadow_projection"]["effect_class"], "NONE")

    def test_claim_history_remains(self):
        x = evaluate(BASE)
        for key in ("baseline_without_correction", "scheduled_correction", "early_correction"):
            self.assertEqual(x[key]["claim_exposure_ids"], ["hub", "mirror_a", "mirror_b", "origin", "receiver"])
            self.assertTrue(x[key]["historical_exposures_retained"])

    def test_barred_node_cannot_receive_claim_or_notice(self):
        x = evaluate(BASE)
        for key in ("baseline_without_correction", "scheduled_correction", "early_correction"):
            self.assertNotIn("barred", x[key]["claim_exposure_ids"])
            self.assertNotIn("barred", x[key]["correction_notice_ids"])

    def test_no_retroactive_activity(self):
        x = evaluate(BASE)["scheduled_correction"]
        self.assertEqual(x["series"][0]["cumulative_synthetic_correction_notices"], 0)
        self.assertEqual(x["series"][1]["cumulative_synthetic_correction_notices"], 0)

    def test_graph_order_independent(self):
        x = copy.deepcopy(BASE)
        for key in ("claim_graph", "correction_graph"):
            x[key]["nodes"].reverse()
            x[key]["edges"].reverse()
        self.assertEqual(evaluate(BASE), evaluate(x))

    def test_late_start_over_horizon_rejected(self):
        x = copy.deepcopy(BASE); x["correction_start_tick"] = 99
        with self.assertRaises(Held): validate_pair(x)

    def test_boolean_start_rejected(self):
        x = copy.deepcopy(BASE); x["correction_start_tick"] = True
        with self.assertRaises(Held): validate_pair(x)

    def test_effect_class_rejected(self):
        x = copy.deepcopy(BASE); x["external_effects"] = "SEND"
        with self.assertRaises(Held): validate_pair(x)

    def test_nested_effect_rejected(self):
        x = copy.deepcopy(BASE); x["correction_graph"]["external_effects"] = "WRITE"
        with self.assertRaises(Held): validate_pair(x)

    def test_unknown_top_level_effect_field_rejected(self):
        x = copy.deepcopy(BASE); x["send_message"] = "yes"
        with self.assertRaises(Held): validate_pair(x)

    def test_unknown_graph_effect_field_rejected(self):
        x = copy.deepcopy(BASE); x["correction_graph"]["effect_command"] = "SEND"
        with self.assertRaises(Held): validate_pair(x)

    def test_wrong_source_type_rejected(self):
        x = copy.deepcopy(BASE); x["source_copies"][0]["source_family"] = None
        with self.assertRaises(Held): validate_pair(x)

    def test_duplicate_copy_rejected(self):
        x = copy.deepcopy(BASE); x["source_copies"].append(copy.deepcopy(x["source_copies"][0]))
        with self.assertRaises(Held): validate_pair(x)

    def test_corrupted_rights_rejected(self):
        x = copy.deepcopy(BASE); x["correction_graph"]["nodes"][0]["allow_synthetic_exposure"] = False
        with self.assertRaises(Held): validate_pair(x)

    def test_disallowed_critic_seed_rejected(self):
        x = copy.deepcopy(BASE)
        next(n for n in x["correction_graph"]["nodes"] if n["id"] == "critic")["allow_synthetic_exposure"] = False
        with self.assertRaises(Held): validate_pair(x)

    def test_shared_origin_not_independent_correction(self):
        x = copy.deepcopy(BASE); x["correction_graph"]["seeds"] = ["origin"]
        with self.assertRaises(Held): validate_pair(x)

    def test_pretend_causal_edge_rejected(self):
        x = copy.deepcopy(BASE); x["claim_graph"]["edges"][0]["relation_type"] = "PROVEN_CAUSE"
        with self.assertRaises(Held): validate_pair(x)

    def test_false_truth_input_rejected(self):
        x = copy.deepcopy(BASE); x["synthetic_unverified_claim_class"] = "FACT"
        with self.assertRaises(Held): validate_pair(x)

    def test_cross_graph_node_drift_rejected(self):
        x = copy.deepcopy(BASE); x["correction_graph"]["nodes"].pop()
        with self.assertRaises(Held): validate_pair(x)

    def test_correction_off_baseline(self):
        x = scenario(BASE, None)
        self.assertEqual(x["exposed_with_notice_at_horizon"], [])
        self.assertIsNone(x["receiver_correction_notice_tick"])

    def test_no_claim_reach_when_blocked_receiver(self):
        x = copy.deepcopy(BASE)
        for key in ("claim_graph", "correction_graph"):
            next(n for n in x[key]["nodes"] if n["id"] == "receiver")["allow_synthetic_exposure"] = False
        v = evaluate(x)
        self.assertNotIn("receiver", v["baseline_without_correction"]["claim_exposure_ids"])
        self.assertNotIn("receiver", v["scheduled_correction"]["correction_notice_ids"])

    def test_no_automatic_spread_when_correction_edges_removed(self):
        x = copy.deepcopy(BASE); x["correction_graph"]["edges"] = []
        v = evaluate(x)
        self.assertNotIn("receiver", v["scheduled_correction"]["correction_notice_ids"])
        self.assertIsNone(v["scheduled_correction"]["receiver_notice_lag_ticks"])

    def test_cli_roundtrip(self):
        p = subprocess.run([sys.executable, str(P / "counter_contagion_r0.py"), str(P / "counter_contagion_fixture.json")], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(p.stdout), evaluate(BASE))


if __name__ == "__main__":
    unittest.main()