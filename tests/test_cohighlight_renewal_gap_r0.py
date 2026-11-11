#!/usr/bin/env python3
"""Source-scoped, deterministic CoHighlight return-gap tests. No effectful calls."""
import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "scripts" / "CoHighlightRenewalGapR0.py"
spec = importlib.util.spec_from_file_location("highlight_gap_r0", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class HighlightReturnGapR0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = json.loads((ROOT / mod.REGISTRY_PATH).read_text())
        cls.pilot = json.loads((ROOT / mod.PILOT_PATH).read_text())
        cls.report = mod.build_from_root()

    def test_bounded_inputs_and_correct_provenance(self):
        r = self.report
        self.assertEqual(r["flat_registry_asset_count"], len(self.reg["assets"]))
        self.assertEqual(r["pilot_declared_role_count"], len(self.pilot["assets"]))
        self.assertEqual(len(r["input_refs"]), 2)
        self.assertTrue(all(len(x["sha256"]) == 64 for x in r["input_refs"]))
        self.assertIn("ONLY_TWO_PINNED", r["scope"])

    def test_registry_gaps_are_metadata_only_not_global_absence(self):
        for a in self.report["flat_registry_asset_gaps"]:
            self.assertTrue(a["not_a_global_absence_claim"])
            self.assertFalse(a["source_currentness_verified"])
            self.assertFalse(a["receiver_origin_accepted"])
            self.assertFalse(a["runtime_control_granted"])
            self.assertEqual(
                len(a["missing_from_flat_registry"]) + len(a["declared_metadata"]),
                len(mod.FIELD_KEYS)
            )
        self.assertIn("MISSING_FIELD_IN_INDEX_NE_ABSENT_SOMEWHERE_ELSE",
                      self.report["nonclaims"])

    def test_pilot_return_categories_do_not_become_ack(self):
        r = self.report
        self.assertGreaterEqual(r["pilot_declared_role_count"], 3)
        for view in r["pilot_role_declarations"]:
            self.assertTrue(view["return_signal_categories_not_receipts"])
            self.assertTrue(view["receiver_role_named_not_consent"])
            self.assertFalse(view["real_receiver_accepted"])
            self.assertFalse(view["verified_external_effect"])
        self.assertEqual(r["real_reader_receipts"], 0)

    def test_source_fields_can_evolve_without_automatic_truth_promotion(self):
        reg = copy.deepcopy(self.reg)
        a = reg["assets"][0]
        a["qualified_receiver_ref"] = "CANDIDATE:novice-opt-in"
        a["source_refs"] = ["github:example:proposed"]
        a["receiver_origin_receipt"] = "UNVERIFIED_STRING_DO_NOT_ACCEPT"
        report = mod.build_report(reg, self.pilot)
        entry = next(x for x in report["flat_registry_asset_gaps"]
                     if x["asset_id"] == a["id"])
        self.assertIn("source_binding", entry["declared_metadata"])
        self.assertIn("receiver_route", entry["declared_metadata"])
        self.assertIn("independent_receiver_result", entry["declared_metadata"])
        self.assertFalse(entry["receiver_origin_accepted"])
        self.assertEqual(report["real_reader_receipts"], 0)

    def test_duplicate_registry_identity_fails_closed(self):
        reg = copy.deepcopy(self.reg)
        reg["assets"].append(copy.deepcopy(reg["assets"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            mod.build_report(reg, self.pilot)

    def test_malformed_or_unbounded_inputs_fail_closed(self):
        reg = copy.deepcopy(self.reg)
        reg["assets"] = reg["assets"] * (mod.MAX_ASSETS + 1)
        with self.assertRaisesRegex(ValueError, "unbounded"):
            mod.build_report(reg, self.pilot)
        reg = copy.deepcopy(self.reg)
        reg["assets"][0].pop("readiness")
        with self.assertRaisesRegex(ValueError, "identifier"):
            mod.build_report(reg, self.pilot)
        pilot = copy.deepcopy(self.pilot)
        pilot["schema"] = "WRONG"
        with self.assertRaisesRegex(ValueError, "unrecognized"):
            mod.build_report(self.reg, pilot)

    def test_deterministic_report_independent_of_input_asset_order(self):
        a = mod.build_report(self.reg, self.pilot)
        reg = copy.deepcopy(self.reg)
        pilot = copy.deepcopy(self.pilot)
        reg["assets"].reverse()
        pilot["assets"].reverse()
        b = mod.build_report(reg, pilot)
        self.assertEqual(a, b)

    def test_no_background_worker_permission_or_runaway_promises(self):
        report = self.report
        self.assertEqual(report["external_effects"], 0)
        self.assertEqual(report["new_autonomous_workers"], 0)
        self.assertIn("does not poll", report["future_wake_rule"])
        self.assertIn("WAKE_RULE_TEXT_NE_SCHEDULER_INSTALLED", report["nonclaims"])
        self.assertIn("LARGER_CATALOG_NE_MORE_VALUE", report["nonclaims"])

    def test_existing_registry_is_not_reclassified_as_stale_or_dying(self):
        report = self.report
        self.assertEqual(report["flat_registry_updated_utc"], self.reg["updated_utc"])
        for x in report["flat_registry_asset_gaps"]:
            self.assertEqual(
                x["original_status_label"],
                next(a["status"] for a in self.reg["assets"]
                     if a["id"] == x["asset_id"])
            )
            self.assertNotIn("STALENESS_CERTIFIED", x)
            self.assertNotIn("DEAD_ASSET", x)


if __name__ == "__main__":
    unittest.main(verbosity=2)
