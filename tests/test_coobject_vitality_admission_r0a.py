"""Synthetic CoObject R0A active-evidence admission regressions.

The fixture and these tests make no runtime, observer, receiver, or ACK claims.
"""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "CoObjectVitalityR0", ROOT / "scripts" / "CoObjectVitalityR0.py"
)
vitality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vitality)
FIXTURE = json.loads(
    (ROOT / "ai" / "vitality" / "coobject-vitality-fixture-r0.json").read_text()
)
POLICY = json.loads(
    (ROOT / "ai" / "vitality" / "coobject-vitality-policy-r0.json").read_text()
)


class VitalityAdmissionR0ATests(unittest.TestCase):
    def test_original_fixture_remains_qualified(self):
        report = vitality.run(copy.deepcopy(FIXTURE), copy.deepcopy(POLICY))
        self.assertEqual(
            report["state"],
            "PASS_THREE_OBJECT_METABOLIC_INTERFACE__EVENT_DRIVEN_HEARTBEAT",
        )
        self.assertEqual(
            report["results"][0]["disposition"],
            "EXTEND_ONE_BOUNDED_DEBT_REDUCTION",
        )
        self.assertEqual(report["held_active_ids"], [])

    def assert_active_held_and_dormant_preserved(self, currentness, health):
        fixture = copy.deepcopy(FIXTURE)
        fixture["objects"][0]["currentness_state"] = currentness
        fixture["objects"][0]["health_state"] = health
        report = vitality.run(fixture, copy.deepcopy(POLICY))
        self.assertEqual(report["state"], "HOLD_ACTIVE_EVIDENCE_REQUALIFICATION")
        self.assertEqual(report["held_active_ids"], ["cobaseline-frontier-r0"])
        self.assertEqual(
            report["results"][0]["disposition"], "HOLD_REQUALIFY_ACTIVE_EVIDENCE"
        )
        self.assertEqual(
            report["results"][0]["heartbeat_mode"], "QUIET_UNTIL_MATERIAL_DELTA"
        )
        self.assertEqual(
            report["results"][1]["disposition"], "SLEEP_KEEP_ADDRESSABLE"
        )
        self.assertEqual(
            report["results"][2]["disposition"], "REMAIN_DORMANT_WITH_EXACT_WAKE"
        )
        self.assertNotIn(
            "SOFTWARE_DEBT_ELECTS_ONE_BOUNDED_EXTENSION",
            report["useful_findings"],
        )
        self.assertTrue(all(v == 0 for v in report["effects"].values()))
        self.assertTrue(
            all(all(v == 0 for v in r["effects"].values()) for r in report["results"])
        )

    def test_stale_active_is_held(self):
        self.assert_active_held_and_dormant_preserved("STALE", "UNKNOWN")

    def test_unknown_currentness_is_held(self):
        self.assert_active_held_and_dormant_preserved(
            "UNKNOWN_CURRENTNESS", "DEGRADED_UNVERIFIED"
        )

    def test_current_but_unverified_health_is_held(self):
        self.assert_active_held_and_dormant_preserved("CURRENT", "HEALTH_UNKNOWN")

    def test_stale_even_when_health_looks_good_is_held(self):
        self.assert_active_held_and_dormant_preserved(
            "STALE", "HEALTHY_BOUNDED_SYNTHETIC"
        )

    def test_dormant_candidate_remains_quiet(self):
        report = vitality.run(copy.deepcopy(FIXTURE), copy.deepcopy(POLICY))
        self.assertEqual(
            report["results"][2]["disposition"], "REMAIN_DORMANT_WITH_EXACT_WAKE"
        )
        self.assertEqual(
            report["results"][2]["heartbeat_mode"], "QUIET_UNTIL_MATERIAL_DELTA"
        )

    def test_missing_policy_allowlist_fails_closed(self):
        policy = copy.deepcopy(POLICY)
        del policy["active_health_allowlist"]
        with self.assertRaisesRegex(ValueError, "active_health_allowlist"):
            vitality.run(copy.deepcopy(FIXTURE), policy)

    def test_empty_policy_allowlist_fails_closed(self):
        policy = copy.deepcopy(POLICY)
        policy["active_currentness_allowlist"] = []
        with self.assertRaisesRegex(ValueError, "active_currentness_allowlist"):
            vitality.run(copy.deepcopy(FIXTURE), policy)

    def test_invalid_policy_allowlist_type_fails_closed(self):
        policy = copy.deepcopy(POLICY)
        policy["active_health_allowlist"] = "HEALTHY"
        with self.assertRaisesRegex(ValueError, "active_health_allowlist"):
            vitality.run(copy.deepcopy(FIXTURE), policy)


if __name__ == "__main__":
    unittest.main()
