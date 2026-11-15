"""Bounded negative controls: no artificial exemption, no automatic authority."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from coevoall_universal_change_r0 import load_policy, evaluate


class UniversalChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_policy()

    def subject(self, scope="interface"):
        return {"object_id": "synthetic:x", "scope": scope,
                "revision_sha256": "a" * 64, "last_tick": 1}

    def proposal(self, **extra):
        data = {"based_on_sha256": "a" * 64,
                "successor_sha256": "b" * 64,
                "overwrites_history": False,
                "requests_effect": False,
                "falsifier": "Reject if independent test does not replicate",
                "synthetic_expected_gain": 5,
                "synthetic_expected_cost": 1,
                "independent_review_requested": True}
        data.update(extra)
        return data

    def decide(self, scope="interface", proposal=None, tick=2):
        return evaluate(self.subject(scope), self.proposal() if proposal is None else proposal,
                        tick, self.policy)

    def test_every_known_and_meta_scope_eligible(self):
        for scope in ("identity", "safety", "authority", "privacy", "consent",
                      "deletion", "proof", "measurement", "governance",
                      "evolution_rule", "model", "language", "interface", "cohysteris"):
            with self.subTest(scope=scope):
                result = self.decide(scope)
                self.assertEqual(result["state"], "CANDIDATE_FOR_INDEPENDENT_REVIEW")
                self.assertTrue(result["scope_change_eligible"])
                self.assertFalse(result["external_authority"])

    def test_unknown_future_scope_also_eligible(self):
        self.assertEqual(self.decide("strange_future_thing")["state"],
                         "CANDIDATE_FOR_INDEPENDENT_REVIEW")

    def test_time_tick_advances_observation_not_payload(self):
        result = evaluate(self.subject(), None, 2, self.policy)
        self.assertEqual(result["state"], "OBSERVATION_REFRESH_ONLY")
        self.assertFalse(result["object_mutated"])
        self.assertEqual(result["observation_tick"], 2)

    def test_stale_time_fails_closed(self):
        self.assertEqual(evaluate(self.subject(), None, 1, self.policy)["reason"],
                         "NON_MONOTONIC_OBSERVATION")

    def test_duplicate_no_new_material_work(self):
        self.assertEqual(self.decide(proposal=self.proposal(successor_sha256="a"*64))["state"],
                         "NO_MATERIAL_DELTA")

    def test_stale_predecessor_rejected(self):
        self.assertEqual(self.decide(proposal=self.proposal(based_on_sha256="c"*64))["reason"],
                         "STALE_OR_CONFLICTING_PREDECESSOR")

    def test_history_rewrite_rejected(self):
        self.assertEqual(self.decide(proposal=self.proposal(overwrites_history=True))["reason"],
                         "HISTORY_OVERWRITE_NOT_PERMITTED")

    def test_authority_escalation_rejected(self):
        self.assertEqual(self.decide(proposal=self.proposal(requests_effect=True))["reason"],
                         "EFFECT_REQUIRES_SEPARATE_AUTHORITY")

    def test_random_novelty_without_gain_rejected(self):
        self.assertEqual(self.decide(proposal=self.proposal(synthetic_expected_gain=1,
                                                          synthetic_expected_cost=3))["reason"],
                         "NET_USEFUL_GAIN_UNQUALIFIED")

    def test_no_falsifier_rejected(self):
        self.assertEqual(self.decide(proposal=self.proposal(falsifier=""))["reason"],
                         "FALSIFIER_MISSING")

    def test_sensitive_rule_change_without_review_request_held(self):
        result = self.decide("evolution_rule",
                             self.proposal(independent_review_requested=False))
        self.assertEqual(result["reason"], "SENSITIVE_SCOPE_REVIEW_NOT_REQUESTED")

    def test_no_permanent_exclusion_in_policy(self):
        self.assertEqual(self.policy["permanent_exempt_scopes"], [])
        self.assertTrue(self.policy["domains_are_open_world"])

    def test_all_proposals_no_real_effects(self):
        for candidate in (None, self.proposal(),
                          self.proposal(requests_effect=True),
                          self.proposal(successor_sha256="a"*64)):
            with self.subTest(candidate=str(candidate)[:40]):
                output = evaluate(self.subject(), candidate, 2, self.policy)
                self.assertEqual(output["effect_count"], 0)
                self.assertFalse(output["object_mutated"])
                self.assertFalse(output["receiver_ack"])


if __name__ == "__main__":
    unittest.main()
