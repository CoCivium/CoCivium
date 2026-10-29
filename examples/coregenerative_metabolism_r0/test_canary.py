#!/usr/bin/env python3
"""Evidence-bound tests for CoMetabolism's first twelve-asset and feedback canary."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from canary import (SCHEMA, STEPS, bounded_regeneration, decay_only,
                    execute, uncorrected_feedback)

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def validate_cohort(data, verify_bytes=False):
    assert data["schema"] == "CoAll.CoMetabolismAssetCohort.R0"
    assert data["asset_count"] == len(data["assets"]) == 12
    assert data["source_ref"] == "main"
    assert data["sampling"].endswith("NOT_A_REPRESENTATIVE_INVENTORY")
    assert len(set(a["id"] for a in data["assets"])) == 12
    assert len(set(a["family"] for a in data["assets"])) == 12
    assert len(set(a["source"]["path"] for a in data["assets"])) == 12
    assert data["default_unknown_state"] == "HELD_UNASSESSED"
    assert data["effects"]["external_sends"] == 0
    assert data["effects"]["asset_mutations"] == 0
    assert data["effects"]["live_workers"] == 0
    for asset in data["assets"]:
        assert asset["lifecycle"] == "UNASSESSED"
        assert asset["receiver_use"] == "UNVERIFIED"
        assert asset["maintenance_input"] == "UNKNOWN"
        assert asset["edge_return"] == "UNKNOWN"
        assert asset["resource_cost"] == "UNKNOWN"
        assert asset["independent_recovery"] == "UNVERIFIED"
        assert asset["verified_outcome"] is False
        assert len(asset["candidate_question"]) > 25
        assert asset["source"]["proof"] == "SOURCE_GIT_BLOB_READBACK_AT_OBSERVATION"
        if verify_bytes:
            p = REPO / asset["source"]["path"]
            assert p.is_file(), asset["source"]["path"]
            assert git_blob_sha(p.read_bytes()) == asset["source"]["git_blob_sha1"], str(p)
    return True


class CoMetabolismCanary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cohort = json.loads((ROOT / "cohort.json").read_text(encoding="utf-8"))
        cls.receipt = execute()

    def test_cohort_exact_pinned_source_bytes(self):
        self.assertTrue(validate_cohort(self.cohort, verify_bytes=True))

    def test_source_is_not_lifecycle_or_use_proof(self):
        self.assertTrue(all(a["lifecycle"] == "UNASSESSED" for a in self.cohort["assets"]))
        self.assertTrue(all(a["receiver_use"] == "UNVERIFIED" for a in self.cohort["assets"]))

    def test_reject_false_receiver_adoption(self):
        invalid = copy.deepcopy(self.cohort)
        invalid["assets"][0]["verified_outcome"] = True
        with self.assertRaises(AssertionError):
            validate_cohort(invalid)

    def test_reject_fake_freshness_label(self):
        invalid = copy.deepcopy(self.cohort)
        invalid["assets"][0]["lifecycle"] = "ACTIVE_REGENERATIVE"
        with self.assertRaises(AssertionError):
            validate_cohort(invalid)

    def test_reject_duplicate_evidence_family(self):
        invalid = copy.deepcopy(self.cohort)
        invalid["assets"][1]["source"]["path"] = invalid["assets"][0]["source"]["path"]
        with self.assertRaises(AssertionError):
            validate_cohort(invalid)

    def test_exact_four_synthetic_scenarios(self):
        self.assertEqual(self.receipt["schema"], SCHEMA)
        self.assertEqual(self.receipt["source_cohort_count"], 12)
        self.assertEqual(len(self.receipt["scenarios"]), 4)
        for scenario in self.receipt["scenarios"]:
            self.assertEqual(len(scenario["series"]), STEPS)
            self.assertEqual(scenario["evidence_class"], "SYNTHETIC")

    def test_passive_decay_is_measurable(self):
        s = decay_only()["series"]
        self.assertLess(s[-1]["activity"], 0.05)
        self.assertTrue(all(s[i + 1]["activity"] < s[i]["activity"] for i in range(len(s) - 1)))

    def test_runaway_shows_activity_without_safety(self):
        s = uncorrected_feedback()["series"]
        self.assertGreater(s[-1]["activity"], 2.1)
        self.assertTrue(any(x["beyond_safe_activity_limit"] for x in s))
        self.assertGreater(s[-1]["error_proxy"], s[0]["error_proxy"])
        self.assertAlmostEqual(s[-1]["useful_proxy"], 0.0, places=7)

    def test_bounded_keeps_activity_and_resources_within_limits(self):
        scenario = bounded_regeneration()
        s = scenario["series"]
        self.assertGreater(s[-1]["useful_proxy"], decay_only()["series"][-1]["useful_proxy"])
        self.assertTrue(all(0 <= x["activity"] <= 2.1 for x in s))
        self.assertTrue(all(x["available_budget"] >= 1.0 for x in s))
        self.assertTrue(all(0 <= x["error_proxy"] <= 1 for x in s))
        self.assertTrue(all(x["drive_spend"] <= x["funded_input"] for x in s))

    def test_budget_conservation_reconciles_without_free_input(self):
        scenario = bounded_regeneration()
        s = scenario["series"]
        initial = scenario["inputs"]["initial_budget"]
        inflow = sum(x["funded_input"] for x in s)
        spent = sum(x["drive_spend"] + x["maintenance_spend"] for x in s)
        ending = s[-1]["available_budget"]
        self.assertAlmostEqual(initial + inflow - spent, ending, places=5)

    def test_error_shock_triggers_correction_not_extra_gain(self):
        s = bounded_regeneration(shock_cycle=8)["series"]
        shocked = s[7]
        self.assertEqual(shocked["correction_mode"], "EXPLICIT_ERROR_DAMPING")
        self.assertEqual(shocked["drive_spend"], 0.0)
        self.assertLess(s[-1]["error_proxy"], shocked["error_proxy"])
        self.assertTrue(all(x["available_budget"] >= 1.0 for x in s))

    def test_idempotent_reproducibility(self):
        self.assertEqual(bounded_regeneration(), bounded_regeneration())
        self.assertEqual(execute(), execute())

    def test_never_claims_runtime_receiver_or_cosmic_mechanism(self):
        rails = set(self.receipt["nonclaims"])
        for x in ("SYNTHETIC_READER_FEEDBACK_NE_ACTUAL_RECEIVER_USE",
                  "REGENERATION_NE_UNLIMITED_ENERGY",
                  "MODEL_PASS_NE_PHYSICS_GD_ET_PROOF",
                  "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF"):
            self.assertIn(x, rails)

    def test_no_intrusive_outbound_code(self):
        raw = (ROOT / "canary.py").read_text(encoding="utf-8")
        for forbidden in ("requests.", "urllib.request", "subprocess.", "socket.", "selenium", "os.system"):
            self.assertNotIn(forbidden, raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
