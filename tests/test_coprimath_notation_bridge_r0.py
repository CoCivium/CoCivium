"""CoPriMath/CoMeasure R0: exact meaning and safe notation tests.

Synthetic fixtures only. No certified instrument reading or external effect.
"""
from copy import deepcopy
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "CoPriMathNotationBridgeR0.py"
spec = importlib.util.spec_from_file_location("coprimath_bridge", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CoPriMathBridgeTests(unittest.TestCase):
    def get(self, kind="duration", unit="min", n=2, d=1, status="OBSERVED_CLAIM"):
        return mod.fixture(kind, unit, n, d, status)

    def test_duration_two_minutes_exact_120_seconds(self):
        m = mod.convert(self.get(), "s")
        self.assertEqual(m["value"], {"n": 120, "d": 1})

    def test_same_duration_units_produce_same_semantic_digest(self):
        a = self.get("duration", "min", 1)
        b = self.get("duration", "s", 60)
        self.assertEqual(mod.canonical_digest(a), mod.canonical_digest(b))

    def test_kilometers_to_meters(self):
        a = self.get("length", "km", 3)
        self.assertEqual(mod.convert(a, "m")["value"], {"n": 3000, "d": 1})

    def test_speed_exact_kmh_to_mps(self):
        a = self.get("speed", "km/h", 18)
        self.assertEqual(mod.convert(a, "m/s")["value"], {"n": 5, "d": 1})

    def test_speed_fraction_is_exact(self):
        a = self.get("speed", "km/h", 1)
        self.assertEqual(mod.convert(a, "m/s")["value"], {"n": 5, "d": 18})

    def test_ratio_percent_to_unitless(self):
        a = self.get("ratio", "%", 25)
        self.assertEqual(mod.convert(a, "1")["value"], {"n": 1, "d": 4})

    def test_probability_percent_to_unitless(self):
        a = self.get("probability", "%", 25)
        self.assertEqual(mod.convert(a, "1")["value"], {"n": 1, "d": 4})

    def test_probability_and_ratio_are_not_same_kind(self):
        a = self.get("ratio", "%", 20)
        b = self.get("probability", "%", 20)
        with self.assertRaisesRegex(mod.Hold, "KIND_MISMATCH"):
            mod.derive("ADD", a, b)

    def test_two_durations_add_exactly(self):
        a = self.get("duration", "min", 2)
        b = self.get("duration", "s", 30)
        got = mod.derive("ADD", a, b)
        self.assertEqual(got["exact_base_value"], {"n": 150, "d": 1})
        self.assertEqual(got["base_unit"], "s")

    def test_mismatched_physical_kind_refuses_addition(self):
        with self.assertRaisesRegex(mod.Hold, "KIND_MISMATCH"):
            mod.derive("ADD", self.get(), self.get("length", "m", 7))

    def test_speed_times_duration_is_length(self):
        x = mod.derive("MULTIPLY", self.get("speed", "km/h", 18), self.get())
        self.assertEqual(x["result_kind"], "length")
        self.assertEqual(x["exact_base_value"], {"n": 600, "d": 1})

    def test_duration_times_speed_same_exact_length(self):
        x = mod.derive("MULTIPLY", self.get(), self.get("speed", "km/h", 18))
        self.assertEqual(x["exact_base_value"], {"n": 600, "d": 1})

    def test_reject_unregistered_multiplication(self):
        with self.assertRaisesRegex(mod.Hold, "MULTIPLY_SIGNATURE_UNSUPPORTED"):
            mod.derive("MULTIPLY", self.get("length", "m", 2),
                       self.get("duration", "s", 3))

    def test_reject_arbitrary_operator_and_code_eval(self):
        with self.assertRaisesRegex(mod.Hold, "OPERATOR_NOT_REGISTERED"):
            mod.derive("__import__('os').system('exit 9')", self.get(), self.get())

    def test_reject_affine_temperature_without_definition(self):
        with self.assertRaisesRegex(mod.Hold, "UNSUPPORTED_KIND"):
            mod.canonical(self.get("temperature", "degC", 20))

    def test_no_cross_kind_unit_conversion(self):
        with self.assertRaisesRegex(mod.Hold, "INCOMPATIBLE_UNIT"):
            mod.convert(self.get("duration", "s", 2), "m")

    def test_zero_differs_from_unknown(self):
        exact = mod.canonical(self.get("length", "m", 0, status="EXACT_ZERO_CLAIM"))
        unknown = mod.canonical(self.get("length", "m", None, status="UNKNOWN"))
        self.assertEqual(exact["exact_base_value"], {"n": 0, "d": 1})
        self.assertIsNone(unknown["exact_base_value"])
        self.assertNotEqual(exact, unknown)

    def test_missing_is_not_a_convertible_numeric_zero(self):
        with self.assertRaisesRegex(mod.Hold, "NON_NUMERIC_STATE_HOLD"):
            mod.convert(self.get("duration", "s", None, status="UNKNOWN"), "min")

    def test_null_categories_remain_distinct(self):
        a = mod.canonical(self.get("duration", "s", None, status="UNKNOWN"))
        b = mod.canonical(self.get("duration", "s", None, status="NOT_TESTED"))
        c = mod.canonical(self.get("duration", "s", None, status="WITHHELD"))
        self.assertEqual(len({a["epistemic_state"], b["epistemic_state"],
                              c["epistemic_state"]}), 3)

    def test_below_detection_not_assumed_zero(self):
        x = mod.canonical(self.get("length", "m", None, status="BELOW_DETECTION"))
        self.assertIsNone(x["exact_base_value"])

    def test_not_applicable_not_assumed_missing(self):
        a = mod.canonical(self.get("length", "m", None, status="NOT_APPLICABLE"))
        b = mod.canonical(self.get("length", "m", None, status="UNKNOWN"))
        self.assertNotEqual(a["epistemic_state"], b["epistemic_state"])

    def test_refuse_numeric_value_in_null_state(self):
        with self.assertRaisesRegex(mod.Hold, "MISSING_STATE_CANNOT_CARRY_NUMBER"):
            mod.canonical(self.get("length", "m", 7, status="UNKNOWN"))

    def test_refuse_false_exact_zero_claim(self):
        with self.assertRaisesRegex(mod.Hold, "EXACT_ZERO_REQUIRES_ZERO"):
            mod.canonical(self.get("length", "m", 1, status="EXACT_ZERO_CLAIM"))

    def test_observed_zero_and_exact_zero_state_not_equated(self):
        a = self.get("length", "m", 0, status="OBSERVED_CLAIM")
        b = self.get("length", "m", 0, status="EXACT_ZERO_CLAIM")
        self.assertNotEqual(mod.canonical_digest(a), mod.canonical_digest(b))

    def test_probability_more_than_one_refused(self):
        with self.assertRaisesRegex(mod.Hold, "PROBABILITY_OUT_OF_RANGE"):
            mod.canonical(self.get("probability", "%", 120))

    def test_negative_probability_refused(self):
        with self.assertRaisesRegex(mod.Hold, "PROBABILITY_OUT_OF_RANGE"):
            mod.canonical(self.get("probability", "1", -1, 10))

    def test_ratio_may_exceed_one_without_becoming_probability(self):
        v = mod.canonical(self.get("ratio", "1", 3, 2))
        self.assertEqual(v["exact_base_value"], {"n": 3, "d": 2})

    def test_fraction_denominator_zero_refused(self):
        with self.assertRaisesRegex(mod.Hold, "INVALID_DENOMINATOR"):
            mod.canonical(self.get(d=0))

    def test_boolean_rational_refused(self):
        with self.assertRaisesRegex(mod.Hold, "NON_INTEGER_RATIONAL"):
            mod.canonical(self.get(n=True))

    def test_float_rational_refused(self):
        with self.assertRaisesRegex(mod.Hold, "NON_INTEGER_RATIONAL"):
            mod.canonical(self.get(n=0.1))

    def test_untrusted_time_zone_refused(self):
        a = self.get()
        a["observed_at_utc"] = "2026-11-10T22:00:00-05:00"
        with self.assertRaisesRegex(mod.Hold, "UTC_TIMESTAMP_REQUIRED"):
            mod.canonical(a)

    def test_impossible_date_refused(self):
        a = self.get()
        a["observed_at_utc"] = "2026-99-44T22:00:00Z"
        with self.assertRaisesRegex(mod.Hold, "INVALID_OBSERVATION_TIME"):
            mod.canonical(a)

    def test_empty_source_ref_refused(self):
        a = self.get()
        a["source_ref"] = ""
        with self.assertRaisesRegex(mod.Hold, "SOURCE_REF_REQUIRED"):
            mod.canonical(a)

    def test_source_change_changes_identity(self):
        a = self.get()
        b = deepcopy(a)
        b["source_ref"] = "fixture:another-source"
        self.assertNotEqual(mod.canonical_digest(a), mod.canonical_digest(b))

    def test_observation_time_change_changes_identity(self):
        a = self.get()
        b = deepcopy(a)
        b["observed_at_utc"] = "2026-11-11T22:00:00Z"
        self.assertNotEqual(mod.canonical_digest(a), mod.canonical_digest(b))

    def test_no_addition_of_null_value(self):
        with self.assertRaisesRegex(mod.Hold, "NO_VALUE_TO_DERIVE"):
            mod.derive("ADD", self.get(n=None, status="NOT_TESTED"), self.get())

    def test_source_claim_not_promoted_to_independent_proof(self):
        x = mod.canonical(self.get())
        self.assertEqual(x["source_truth"], "CLAIM_ONLY")
        self.assertEqual(x["independent_calibration"], "NOT_TESTED")

    def test_derived_value_has_unverified_provenance(self):
        result = mod.derive("MULTIPLY", self.get("speed", "km/h", 18), self.get())
        self.assertEqual(result["evidence_status"], "DERIVED_FROM_UNVERIFIED_SOURCE_CLAIMS")
        self.assertEqual(result["effect_authority"], "NONE")
        self.assertEqual(result["receiver_ack"], "NOT_OBSERVED")
        self.assertEqual(len(result["input_semantic_digests"]), 2)

    def test_ascii_projection_readable_and_typed(self):
        self.assertEqual(mod.ascii_projection(self.get()), "2 min [duration; OBSERVED_CLAIM]")

    def test_ascii_projection_null_keeps_missing_state(self):
        self.assertEqual(mod.ascii_projection(self.get(n=None,status="WITHHELD")),
                         "WITHHELD [duration]")

    def test_mathml_is_xml_presentation_not_unverified_content_mathml(self):
        xml = mod.mathml_presentation(self.get("length", "km", 1, 2))
        node = ET.fromstring(xml)
        self.assertEqual(node.tag, "{" + mod.NS + "}math")
        self.assertIsNotNone(node.find(".//{" + mod.NS + "}mfrac"))
        self.assertNotIn("<apply>", xml)

    def test_mathml_null_is_not_numeric_zero(self):
        xml = mod.mathml_presentation(self.get(n=None,status="UNKNOWN"))
        self.assertIn("UNKNOWN", xml)
        self.assertNotIn("<mn>", xml)

    def test_extra_fields_refused(self):
        a = self.get()
        a["special_effect"] = "RUN"
        with self.assertRaisesRegex(mod.Hold, "INVALID_FIELDS"):
            mod.canonical(a)

    def test_missing_schema_refused(self):
        a = self.get()
        a["schema"] = "CoPriMath.Other"
        with self.assertRaisesRegex(mod.Hold, "BAD_SCHEMA"):
            mod.canonical(a)


if __name__ == "__main__":
    unittest.main(verbosity=2)
