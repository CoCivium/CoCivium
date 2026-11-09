"""Verify CoPre ready gate fails closed on incomplete, stale or fake receipts."""
from copy import deepcopy
from pathlib import Path
import json
import unittest
from copre_readiness_gate_r0 import evaluate, REQUIRED_TARGETS

CURRENT = json.loads(Path(__file__).with_name("copre_ready_cycle_observed_r0.json").read_text())

def fully_qualified():
    e = deepcopy(CURRENT)
    for t in REQUIRED_TARGETS:
        e["targets"][t] = {
            "owner_authorized": True, "independent_fetch": True,
            "privacy_review": True, "http_success": True,
            "sha256": "a" * 64,
        }
    e["receiver"] = dict(independent_actor=True, exact_digest_match=True,
                         durable_ack=True, recovery_after_restart=True)
    e["seed_survival"] = dict(verified_hours=25)
    e["system_automation"] = dict(system_owned=True,human_interventions=0,
                                   observed_run=True)
    return e

class ReadinessTests(unittest.TestCase):
    def test_observed_is_held(self):
        result = evaluate(CURRENT)
        self.assertFalse(result["ready"])
        self.assertEqual(result["status"], "DRAFT_HELD")
        self.assertTrue(any("CoPreGeneric" in x for x in result["holds"]))

    def test_all_synthetic_receipts_clear_only_readiness_gate(self):
        result = evaluate(fully_qualified())
        self.assertTrue(result["ready"])
        self.assertFalse(result["coex_proven"])
        self.assertFalse(result["governing_canon_proven"])
        self.assertFalse(result["effective_runtime_proven"])

    def test_only_two_mirrors_not_ready(self):
        e = fully_qualified()
        del e["targets"][REQUIRED_TARGETS[2]]
        self.assertFalse(evaluate(e)["ready"])

    def test_mismatched_sha_rejected(self):
        e = fully_qualified()
        e["targets"][REQUIRED_TARGETS[1]]["sha256"] = "b"*64
        self.assertIn("THREE_MIRROR_IDENTICAL_PAYLOAD_UNPROVEN", evaluate(e)["holds"])

    def test_invalid_digest_rejected(self):
        e = fully_qualified()
        e["targets"][REQUIRED_TARGETS[0]]["sha256"] = "abc"
        self.assertFalse(evaluate(e)["ready"])

    def test_24_hours_not_enough(self):
        e = fully_qualified()
        e["seed_survival"]["verified_hours"] = 24
        self.assertIn("SEED_SURVIVAL_GT_24H_UNPROVEN",evaluate(e)["holds"])

    def test_single_human_relay_breaks_goal(self):
        e = fully_qualified()
        e["system_automation"]["human_interventions"] = 1
        self.assertFalse(evaluate(e)["ready"])

    def test_receiver_claim_without_durable_ack_not_ready(self):
        e = fully_qualified()
        e["receiver"]["durable_ack"] = False
        self.assertIn("INDEPENDENT_RECEIVER_HANDOFF_UNPROVEN",evaluate(e)["holds"])

    def test_public_source_pr_success_insufficient_alone(self):
        e = deepcopy(CURRENT)
        self.assertTrue(e["candidate_source"]["readback"])
        self.assertFalse(evaluate(e)["ready"])

if __name__ == "__main__":
    unittest.main()
