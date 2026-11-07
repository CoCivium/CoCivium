"""Public, repeatable negative controls for an exploratory mathematical fragment."""
import unittest

from model_r0 import (
    NullKind, QualifiedObservation, authorized_transform,
    count_failure_domains, decision_preserving, distinguishable_by,
    gauge_equivalent, likelihood_evidence_bits, numeric_residual,
    three_binary_inequalities_globally_satisfiable,
)


class CoAlienMathR0Tests(unittest.TestCase):
    def test_indistinguishable_images_cannot_identify_cause(self):
        self.assertFalse(distinguishable_by("live", "replay", lambda _: "green pixel"))

    def test_intervention_can_separate_candidate_worlds(self):
        self.assertTrue(distinguishable_by("live", "replay", lambda world: world == "live"))

    def test_unknown_not_equivalent_to_numeric_zero(self):
        self.assertNotEqual(NullKind.UNKNOWN, NullKind.OBSERVED_ZERO)

    def test_null_cannot_be_subtracted_from_measurement(self):
        forecast = QualifiedObservation("X", "seconds", "s", 2)
        unseen = QualifiedObservation("X", "seconds", "s", None, NullKind.NOT_OBSERVED)
        with self.assertRaises(ValueError):
            numeric_residual(forecast, unseen)

    def test_numeric_residual_preserves_unit(self):
        forecast = QualifiedObservation("X", "seconds", "s", 2.0)
        observed = QualifiedObservation("X", "seconds", "s", 3.2)
        self.assertAlmostEqual(numeric_residual(forecast, observed), 1.2)

    def test_mismatched_units_fail_closed(self):
        with self.assertRaises(ValueError):
            numeric_residual(QualifiedObservation("X", "duration", "s", 2),
                             QualifiedObservation("X", "duration", "ms", 2000))

    def test_false_permission_promotion_is_rejected(self):
        self.assertFalse(authorized_transform(frozenset({"read"}), frozenset({"read", "publish"})))

    def test_restrictive_projection_is_admissible(self):
        self.assertTrue(authorized_transform(frozenset({"read", "publish"}), frozenset({"read"})))

    def test_decision_preserving_compression(self):
        states = [0, 1, 2, 3]
        self.assertTrue(decision_preserving(states, lambda x: x % 2, lambda x: x % 2))

    def test_lossy_compression_cannot_preserve_distinct_decisions(self):
        states = ["UNKNOWN", "NOT_AUTHORIZED"]
        self.assertFalse(decision_preserving(states, lambda _: "NULL", lambda x: x))

    def test_three_mirrored_feeds_are_one_failure_domain(self):
        self.assertEqual(count_failure_domains(["one-controller"] * 3), 1)

    def test_missing_failure_domain_blocks_inference(self):
        with self.assertRaises(ValueError):
            count_failure_domains(["one-controller", ""])

    def test_likelihood_ratio_not_magic_truth_probability(self):
        self.assertAlmostEqual(likelihood_evidence_bits(0.8, 0.2), 2.0)

    def test_likelihood_of_zero_denominator_cannot_be_assumed(self):
        with self.assertRaises(ValueError):
            likelihood_evidence_bits(0.5, 0)

    def test_unknown_null_refuses_numeric_payload(self):
        with self.assertRaises(ValueError):
            QualifiedObservation("X", "seconds", "s", 0, NullKind.UNKNOWN)

    def test_boolean_measurement_rejected(self):
        with self.assertRaises(ValueError):
            QualifiedObservation("X", "seconds", "s", True)

    def test_observed_zero_typed_exactly(self):
        self.assertEqual(QualifiedObservation("X", "seconds", "s", 0, NullKind.OBSERVED_ZERO).value, 0)

    def test_gauge_nonidentifiability(self):
        self.assertTrue(gauge_equivalent(2, (3, 5, 7), 4))

    def test_odd_cycle_not_jointly_satisfiable(self):
        self.assertFalse(three_binary_inequalities_globally_satisfiable())


if __name__ == "__main__":
    unittest.main()
