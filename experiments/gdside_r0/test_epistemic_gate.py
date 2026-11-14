"""Negative controls for nonmaterial, anomalous and recursive claims."""
import unittest

from epistemic_gate import Claim, REVIEW_CONTROLS, assess, bounded_meta_walk


def claim(name, referent, epistemic, **kw):
    return Claim(name, referent, epistemic, "fixture:public-synthetic", **kw)


class TestEpistemicBoundary(unittest.TestCase):
    def test_experience_preserved_not_external_signal(self):
        result = assess(claim("felt-presence", "EXPERIENTIAL", "HUMAN_REPORT",
                              asserts_external_cause=True))
        self.assertTrue(result["interpretation_preserved"])
        self.assertEqual(result["causal_status"],
                         "EXTERNAL_CAUSATION_NOT_ESTABLISHED")
        self.assertEqual(result["effect_authority"], "NONE")

    def test_spooky_hypothesis_not_proven_or_erased(self):
        result = assess(claim("unusual-event", "CLAIMED_NONMATERIAL",
                              "HYPOTHESIS", asserts_external_cause=True))
        self.assertEqual(result["causal_status"],
                         "EXTERNAL_CAUSATION_NOT_ESTABLISHED")
        self.assertTrue(result["interpretation_preserved"])

    def test_abstract_proof_not_mistaken_for_physical_force(self):
        result = assess(claim("theorem", "ABSTRACT", "FORMAL_DERIVATION"))
        self.assertEqual(result["causal_status"], "NOT_ASSERTED")
        self.assertEqual(result["referent"], "ABSTRACT")

    def test_social_obligation_can_matter_without_external_causation(self):
        result = assess(claim("promise", "SOCIAL_NORMATIVE", "HUMAN_REPORT"))
        self.assertEqual(result["causal_status"], "NOT_ASSERTED")
        self.assertTrue(result["interpretation_preserved"])
        self.assertEqual(result["effect_authority"], "NONE")

    def test_instrument_correlation_not_anomalous_origin_proof(self):
        result = assess(claim("sensor-pattern", "PHYSICAL",
                              "INSTRUMENT_OBSERVATION",
                              asserts_external_cause=True))
        self.assertEqual(result["causal_status"],
                         "EXTERNAL_CAUSATION_NOT_ESTABLISHED")

    def test_inverse_causal_story_is_not_measurement(self):
        result = assess(claim("reverse-time-story", "PHYSICAL",
                              "MODEL_INFERENCE", asserts_external_cause=True))
        self.assertEqual(result["causal_status"],
                         "EXTERNAL_CAUSATION_NOT_ESTABLISHED")

    def test_unknown_carrier_label_cannot_become_a_sensor(self):
        result = assess(claim("unexpanded-carrier", "UNKNOWN",
                              "HYPOTHESIS", asserts_external_cause=True))
        self.assertEqual(result["causal_status"],
                         "EXTERNAL_CAUSATION_NOT_ESTABLISHED")
        self.assertFalse(result["source_authenticated"])

    def test_null_not_observed_ne_negative_with_sensitivity(self):
        a = assess(claim("unseen", "UNKNOWN", "UNKNOWN",
                         null_state="NOT_OBSERVED"))
        b = assess(claim("bounded-negative", "PHYSICAL",
                         "INSTRUMENT_OBSERVATION",
                         null_state="NEGATIVE_WITH_DEFINED_SENSITIVITY"))
        self.assertNotEqual(a["null_state"], b["null_state"])
        self.assertEqual(a["causal_status"], "NOT_ASSERTED")
        self.assertEqual(b["causal_status"], "NOT_ASSERTED")

    def test_missing_claim_provenance_is_held(self):
        with self.assertRaisesRegex(ValueError, "CLAIM_SOURCE_REQUIRED"):
            assess(Claim("claim", "UNKNOWN", "HYPOTHESIS", ""))

    def test_symbolic_gdside_cannot_authorize_action(self):
        with self.assertRaisesRegex(ValueError, "NO_EFFECT_AUTHORITY"):
            assess(claim("symbol", "SYMBOLIC",
                         "METAPHYSICAL_INTERPRETATION",
                         effect_authority="EXECUTE"))

    def test_synthetic_full_controls_only_make_review_eligible(self):
        result = assess(claim(
            "synthetic-physical", "PHYSICAL",
            "CALIBRATED_INDEPENDENT_REPLICATION",
            asserts_external_cause=True, controls=REVIEW_CONTROLS,
        ))
        self.assertEqual(result["causal_status"],
                         "STRUCTURALLY_REVIEW_ELIGIBLE_NOT_VERIFIED")
        self.assertFalse(result["source_authenticated"])
        self.assertEqual(result["effect_authority"], "NONE")

    def test_meta_cycle_stops_without_execution(self):
        result = bounded_meta_walk({"a": ("b",), "b": ("a",)}, "a")
        self.assertEqual(result["visited"], ("a", "b"))
        self.assertTrue(result["cycle_seen"])
        self.assertFalse(result["truncated"])
        self.assertEqual(result["effect_authority"], "NONE")

    def test_meta_budget_stops_turtles_preserves_unvisited(self):
        result = bounded_meta_walk(
            {"a": ("b",), "b": ("c",), "c": ("d",)}, "a",
            max_depth=1,
        )
        self.assertEqual(result["visited"], ("a", "b"))
        self.assertTrue(result["truncated"])
        self.assertFalse(result["cycle_seen"])

    def test_shared_descendant_is_not_a_cycle(self):
        result = bounded_meta_walk(
            {"a": ("b", "c"), "b": ("d",), "c": ("d",)}, "a",
        )
        self.assertFalse(result["cycle_seen"])
        self.assertEqual(set(result["visited"]), {"a", "b", "c", "d"})

    def test_invalid_meta_budget_is_held(self):
        with self.assertRaisesRegex(ValueError, "META_BUDGET_INVALID"):
            bounded_meta_walk({"a": ("b",)}, "a", max_depth=100)


if __name__ == "__main__":
    unittest.main()
