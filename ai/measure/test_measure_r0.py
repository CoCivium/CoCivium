#!/usr/bin/env python3
"""Read-only adversarial CoMeasure tests, no network or user data."""
from __future__ import annotations

import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import measure_r0 as m


def registry():
    return json.loads((HERE / "registry-r0.json").read_text(encoding="utf-8"))


def observations():
    return json.loads((HERE / "observations-synthetic-r0.json").read_text(encoding="utf-8"))


class RegistryAndUnitTests(unittest.TestCase):
    def setUp(self):
        self.reg = registry()
        self.fx = observations()

    def reject_conversion(self, source, target):
        with self.assertRaises(m.MeasureError):
            m.convert("1", source, target, self.reg)

    def reject_ratio(self, mutation, derived="human_seconds_per_verified_effect", fixture=None):
        f = copy.deepcopy(fixture or self.fx)
        mutation(f)
        with self.assertRaises(m.MeasureError):
            m.derive_ratio(derived, f["numerator"], f["denominator"], self.reg)

    def test_validates_registry(self):
        m.validate_registry(self.reg)

    def test_exact_seven_si_base_units(self):
        self.assertEqual({u["si_unit"] for u in self.reg["si_base_dimensions"]},
                         {"m","kg","s","A","K","mol","cd"})

    def test_registry_has_distinct_semantic_kinds(self):
        kinds = {u["quantity_kind"] for u in self.reg["unit_registry"]}
        self.assertIn("temperature_point", kinds)
        self.assertIn("temperature_difference", kinds)
        self.assertIn("model_token", kinds)
        self.assertIn("manual_relay_event", kinds)

    def test_seconds_to_minutes(self):
        self.assertEqual(m.convert("120", "s", "min", self.reg)["converted_value"], "2")

    def test_hours_to_seconds(self):
        self.assertEqual(m.convert("2", "h", "s", self.reg)["converted_value"], "7200")

    def test_meters_to_kilometers(self):
        self.assertEqual(m.convert("1234", "m", "km", self.reg)["converted_value"], "1.234")

    def test_kilometers_to_meters(self):
        self.assertEqual(m.convert("2.5", "km", "m", self.reg)["converted_value"], "2500")

    def test_celsius_point_to_kelvin(self):
        self.assertEqual(m.convert("20", "degC", "K", self.reg)["converted_value"], "293.15")

    def test_kelvin_point_to_celsius(self):
        self.assertEqual(m.convert("273.15", "K", "degC", self.reg)["converted_value"], "0")

    def test_celsius_difference_to_kelvin_difference(self):
        self.assertEqual(m.convert("-4", "delta_degC", "delta_K", self.reg)["converted_value"], "-4")

    def test_celsius_point_cannot_convert_to_delta(self):
        self.reject_conversion("degC","delta_degC")

    def test_kelvin_point_cannot_convert_to_delta(self):
        self.reject_conversion("K","delta_K")

    def test_human_seconds_not_physical_seconds_same_dimension(self):
        self.reject_conversion("human_s","s")

    def test_human_minutes_to_human_seconds(self):
        self.assertEqual(m.convert("2.5", "human_min", "human_s", self.reg)["converted_value"], "150")

    def test_energy_to_power_fails(self):
        self.reject_conversion("Joule", "W")

    def test_wh_to_joules(self):
        self.assertEqual(m.convert("1", "Wh", "Joule", self.reg)["converted_value"], "3600")

    def test_bits_to_bytes(self):
        self.assertEqual(m.convert("8192", "bit", "B", self.reg)["converted_value"], "1024")

    def test_bytes_to_kib(self):
        self.assertEqual(m.convert("1024", "B", "KiB", self.reg)["converted_value"], "1")

    def test_model_tokens_cannot_convert_to_bytes(self):
        self.reject_conversion("model_token", "B")

    def test_contextual_same_unit_not_a_physical_conversion(self):
        self.reject_conversion("model_token", "model_token")

    def test_cad_usd_without_exchange_rate_fails(self):
        self.reject_conversion("CAD", "USD")

    def test_timestamp_not_duration(self):
        self.reject_conversion("UTC_instant", "s")

    def test_emission_equivalence_not_kg(self):
        self.reject_conversion("kgCO2e", "kg")

    def test_outcome_count_not_human_touch(self):
        self.reject_conversion("verified_effect", "human_touch")

    def test_percentage_to_bounded_fraction(self):
        self.assertEqual(m.convert("25", "percent", "one", self.reg)["converted_value"], "0.25")

    def test_nonfinite_number_fails(self):
        with self.assertRaises(m.MeasureError):
            m.convert("NaN", "m", "km", self.reg)

    def test_boolean_number_fails(self):
        with self.assertRaises(m.MeasureError):
            m.convert(True, "m", "km", self.reg)

    def test_huge_number_fails(self):
        with self.assertRaises(m.MeasureError):
            m.convert("9"*81, "m", "km", self.reg)

    def test_unknown_unit_fails(self):
        self.reject_conversion("hyperdimension", "m")

    def test_duplicate_unit_rejected(self):
        x=copy.deepcopy(self.reg)
        x["unit_registry"].append(copy.deepcopy(x["unit_registry"][0]))
        with self.assertRaisesRegex(m.MeasureError, "DUPLICATE_UNIT_ID"):
            m.validate_registry(x)

    def test_bad_dimension_rejected(self):
        x=copy.deepcopy(self.reg)
        x["unit_registry"][0]["dimension"]={"Hyper":1}
        with self.assertRaisesRegex(m.MeasureError,"UNKNOWN_DIMENSION"):
            m.validate_registry(x)

    def test_si_base_dimension_missing_rejected(self):
        x=copy.deepcopy(self.reg)
        x["si_base_dimensions"].pop()
        with self.assertRaisesRegex(m.MeasureError,"SI_BASE_DIMENSIONS"):
            m.validate_registry(x)

    def test_offset_on_duration_rejected(self):
        x=copy.deepcopy(self.reg)
        x["unit_registry"][2]["offset_to_reference"]="1"
        with self.assertRaisesRegex(m.MeasureError,"OFFSET_ON_NONPOINT"):
            m.validate_registry(x)

    def test_negative_scale_rejected(self):
        x=copy.deepcopy(self.reg)
        x["unit_registry"][0]["scale_to_reference"]="-1"
        with self.assertRaisesRegex(m.MeasureError,"NONPOSITIVE_SCALE"):
            m.validate_registry(x)

    def test_false_canon_state_rejected(self):
        x=copy.deepcopy(self.reg)
        x["status"]="CANON_RUNTIME"
        with self.assertRaisesRegex(m.MeasureError,"FALSE_RUNTIME_OR_CANON"):
            m.validate_registry(x)

    def test_ordinal_metric_lacks_numeric_unit(self):
        o=next(x for x in self.reg["measure_registry"] if x["interpretation"]=="ORDINAL")
        self.assertIsNone(o["unit_id"])

    def test_derived_match_and_unit_conversion(self):
        out=m.derive_ratio("human_seconds_per_verified_effect",
                           self.fx["numerator"],self.fx["denominator"],self.reg)
        self.assertEqual(out["value"], "400")
        self.assertEqual(out["unit_label"], "human_s/verified_effect")
        self.assertEqual(out["epistemic"], "SYNTHETIC")

    def test_derived_zero_effects_is_undefined(self):
        self.reject_ratio(lambda x:x["denominator"].update(value="0",status="OBSERVED_ZERO"))

    def test_derived_negative_effects_is_undefined(self):
        self.reject_ratio(lambda x:x["denominator"].update(value="-1",status="OBSERVED"))

    def test_derived_unknown_numerator_is_not_zero(self):
        self.reject_ratio(lambda x:x["numerator"].update(value=None,status="UNKNOWN"))

    def test_null_state_must_not_have_a_numeric_value(self):
        self.reject_ratio(lambda x:x["numerator"].update(value="0",status="UNKNOWN"))

    def test_observed_zero_requires_zero(self):
        self.reject_ratio(lambda x:x["numerator"].update(value="9",status="OBSERVED_ZERO"))

    def test_derived_incompatible_scope_rejected(self):
        self.reject_ratio(lambda x:x["numerator"].update(scope_id="different"))

    def test_derived_incompatible_window_rejected(self):
        self.reject_ratio(lambda x:x["denominator"].update(window_id="different"))

    def test_derived_incompatible_method_rev_rejected(self):
        self.reject_ratio(lambda x:x["numerator"].update(method_revision="r1"))

    def test_derived_missing_evidence_rejected(self):
        self.reject_ratio(lambda x:x["numerator"].update(evidence_ref=""))

    def test_derived_mixed_epistemic_class_rejected(self):
        self.reject_ratio(lambda x:x["denominator"].update(epistemic="OBSERVED_REAL"))

    def test_derived_wrong_measure_type_rejected(self):
        self.reject_ratio(lambda x:x["numerator"].update(measure_id="comeasure.ops.energy.r0"))

    def test_derived_wrong_unit_type_rejected(self):
        self.reject_ratio(lambda x:x["denominator"].update(unit_id="human_touch"))

    def test_derived_unknown_measure_rejected(self):
        self.reject_ratio(lambda x:x["numerator"].update(measure_id="unknown"))

    def test_derived_extra_hidden_data_rejected(self):
        self.reject_ratio(lambda x:x["numerator"].update(secret="unscoped data"))

    def test_derived_recovery_success_ratio(self):
        fx=copy.deepcopy(self.fx["optional_recovery_fixture"])
        out=m.derive_ratio("independent_cold_restore_success_ratio",
                           fx["numerator"],fx["denominator"],self.reg)
        self.assertEqual(out["value"],"0.8")
        self.assertEqual(out["epistemic"],"SYNTHETIC")

    def test_success_exceeding_trials_rejected(self):
        fx=copy.deepcopy(self.fx["optional_recovery_fixture"])
        fx["numerator"]["value"]="11"
        with self.assertRaisesRegex(m.MeasureError,"SUCCESS_EXCEEDS_TRIALS"):
            m.derive_ratio("independent_cold_restore_success_ratio",
                           fx["numerator"],fx["denominator"],self.reg)

    def test_zero_recovery_success_valid(self):
        fx=copy.deepcopy(self.fx["optional_recovery_fixture"])
        fx["numerator"].update(value="0",status="OBSERVED_ZERO")
        out=m.derive_ratio("independent_cold_restore_success_ratio",
                           fx["numerator"],fx["denominator"],self.reg)
        self.assertEqual(out["value"],"0")

    def test_ratio_reports_uncertainty_not_propagated(self):
        out=m.derive_ratio("human_seconds_per_verified_effect",
                           self.fx["numerator"],self.fx["denominator"],self.reg)
        self.assertEqual(out["uncertainty"],"NOT_PROPAGATED__REQUIRES_MODEL")

    def test_ratio_zero_effects(self):
        out=m.derive_ratio("human_seconds_per_verified_effect",
                           self.fx["numerator"],self.fx["denominator"],self.reg)
        self.assertTrue(all(v == 0 for v in out["effects"].values()))

    def test_cli_validates_and_does_not_mutate_files(self):
        cmd=[sys.executable, "-B", str(HERE/"measure_r0.py"),"validate"]
        result=subprocess.run(cmd,capture_output=True,text=True,check=False)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"],"PASS_STRUCTURE_ONLY")

    def test_cli_converts_celsius(self):
        cmd=[sys.executable, "-B", str(HERE/"measure_r0.py"),"convert",
             "--value","20","--from-unit","degC","--to-unit","K"]
        result=subprocess.run(cmd,capture_output=True,text=True,check=False)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)["converted_value"],"293.15")

    def test_cli_synthetic_derive(self):
        cmd=[sys.executable, "-B", str(HERE/"measure_r0.py"),"derive",
             "--observations",str(HERE/"observations-synthetic-r0.json")]
        result=subprocess.run(cmd,capture_output=True,text=True,check=False)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)["value"],"400")

    def test_rejected_foreign_input_on_cli(self):
        cmd=[sys.executable, "-B", str(HERE/"measure_r0.py"),"convert",
             "--value","1","--from-unit","model_token","--to-unit","B"]
        result=subprocess.run(cmd,capture_output=True,text=True,check=False)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("FAIL_SCOPED",result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
