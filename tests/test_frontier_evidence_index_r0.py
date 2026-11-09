"""Negative controls for the existing public CoAll frontier continuity index.

Temporary fixtures are source-shape checks, not receiver/effect certification.
"""
import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_frontier_evidence_index_r0 import (
    Hold, INITIAL_FRONTS, INDEX, validate, validate_continuity
)


class FrontierIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        for name in (
            "tests/gs_receiver/contract.py",
            ".github/workflows/receiver-reconciliation.yml",
            "docs/Evolution/GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md",
        ):
            file = self.root / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("public synthetic\n", encoding="utf-8")
        self.original = json.loads((ROOT / INDEX).read_text(encoding="utf-8"))
        self.doc = copy.deepcopy(self.original)

    def test_real_current_index_is_valid_under_repo_root(self):
        self.assertEqual(validate(self.original, ROOT)["front_count"],
                         len(self.original["fronts"]))

    def test_initial_front_set_preserved(self):
        self.assertEqual(
            {f["id"] for f in self.doc["fronts"]}, INITIAL_FRONTS
        )
        self.assertEqual(validate(self.doc, self.root)["baseline_count"], 7)

    def test_front_removal_fails_closed(self):
        self.doc["fronts"].pop()
        with self.assertRaisesRegex(Hold, "HOLD_BASELINE_FRONT_DROPPED"):
            validate(self.doc, self.root)

    def test_duplicate_front_fails_closed(self):
        self.doc["fronts"].append(copy.deepcopy(self.doc["fronts"][0]))
        with self.assertRaisesRegex(Hold, "HOLD_DUPLICATE_FRONT"):
            validate(self.doc, self.root)

    def test_missing_next_gate_fails_closed(self):
        self.doc["fronts"][0]["next_gate"] = ""
        with self.assertRaisesRegex(Hold, "HOLD_MISSING_NEXT_GATE"):
            validate(self.doc, self.root)

    def test_blocker_removed_from_current_without_prior_comparison_is_not_global_proof(self):
        # Local shape validation alone cannot certify history. The CI
        # predecessor comparison is essential.
        self.doc["fronts"][0]["blocked_claims"].pop()
        self.assertEqual(
            validate(self.doc, self.root)["real_receiver_acceptance"],
            "NOT_EVALUATED"
        )

    def test_silent_blocker_removal_detected_by_predecessor(self):
        previous = copy.deepcopy(self.doc)
        self.doc["fronts"][0]["blocked_claims"].remove("CI_PASS")
        validate(self.doc, self.root)
        with self.assertRaisesRegex(Hold, "HOLD_SILENT_BLOCKER_REMOVAL"):
            validate_continuity(previous, self.doc)

    def test_valid_resolution_pointer_only_proves_structure(self):
        previous = copy.deepcopy(self.doc)
        self.doc["fronts"][0]["blocked_claims"].remove("CI_PASS")
        self.doc["fronts"][0]["claim_resolutions"] = [{
            "claim": "CI_PASS",
            "evidence_ref": "github-actions-run:1234",
            "verifier_ref": "independent-review:1234",
            "observed_at": "2026-11-09T20:01:00Z",
        }]
        self.assertEqual(
            validate_continuity(previous, self.doc)["verified_external_effects"],
            "NOT_EVALUATED"
        )

    def test_predecessor_dropped_front_fails_even_for_new_front(self):
        previous = copy.deepcopy(self.doc)
        previous["fronts"].append({
            "id": "new-lane", "status": "proposed",
            "next_gate": "one observation",
            "blocked_claims": ["NOT_DONE"]
        })
        with self.assertRaisesRegex(Hold, "HOLD_SILENT_FRONT_REMOVAL"):
            validate_continuity(previous, self.doc)

    def test_new_front_is_allowed_when_gate_present(self):
        self.doc["fronts"].append({
            "id": "novel-lane", "status": "proposed",
            "next_gate": "run one public-safe test",
            "blocked_claims": ["NOT_TESTED"],
        })
        self.assertEqual(validate(self.doc, self.root)["front_count"], 8)

    def test_unknown_status_rejected(self):
        self.doc["fronts"][0]["status"] = "FULLY_LIVE"
        with self.assertRaisesRegex(Hold, "HOLD_UNKNOWN_PROMOTION_STATE"):
            validate(self.doc, self.root)

    def test_tested_promotion_needs_real_run_ref_shape(self):
        self.doc["fronts"][0]["status"] = "tests_executed"
        with self.assertRaisesRegex(Hold, "HOLD_UNGROUNDED_TEST_STATUS"):
            validate(self.doc, self.root)

    def test_structured_test_ref_does_not_claim_live_receiver(self):
        f = self.doc["fronts"][0]
        f["status"] = "tests_executed"
        f["test_receipt"] = {
            "run_id": 12345, "source_sha": "a"*40,
            "conclusion": "success", "scope": "synthetic_source_only"
        }
        self.assertEqual(validate(self.doc, self.root)["cross_session_sync"],
                         "NOT_EVALUATED")

    def test_receiver_promotion_needs_separate_readproof(self):
        f = self.doc["fronts"][0]
        f["status"] = "independently_observed"
        f["test_receipt"] = {
            "run_id": 12345, "source_sha": "a"*40,
            "conclusion": "success", "scope": "synthetic_source_only"
        }
        with self.assertRaisesRegex(Hold, "HOLD_NO_INDEPENDENT_READPROOF"):
            validate(self.doc, self.root)

    def test_release_requires_receiver_acceptance(self):
        f = self.doc["fronts"][0]
        f["status"] = "released"
        f["test_receipt"] = {
            "run_id": 12345, "source_sha": "a"*40,
            "conclusion": "success", "scope": "synthetic_source_only"
        }
        f["receiver_readproof"] = {
            "observer": "separate", "source_ref": "source:1",
            "readproof_ref": "receiver:1"
        }
        with self.assertRaisesRegex(Hold, "HOLD_NO_RELEASE_ACCEPTANCE"):
            validate(self.doc, self.root)

    def test_source_path_traversal_rejected(self):
        self.doc["fronts"][0]["source"] = "../../private-key"
        with self.assertRaisesRegex(Hold, "HOLD_INVALID_SOURCE_POINTER"):
            validate(self.doc, self.root)

    def test_missing_workflow_rejected(self):
        self.doc["fronts"][0]["workflow"] = ".github/workflows/nonexistent.yml"
        with self.assertRaisesRegex(Hold, "HOLD_INVALID_WORKFLOW_POINTER"):
            validate(self.doc, self.root)

    def test_duplicate_blocker_rejected(self):
        self.doc["fronts"][0]["blocked_claims"].append("CI_PASS")
        with self.assertRaisesRegex(Hold, "HOLD_BLOCKED_CLAIMS"):
            validate(self.doc, self.root)

    def test_trust_rules_cannot_silently_change(self):
        self.doc["rules"]["no_self_certified_effect"] = False
        with self.assertRaisesRegex(Hold, "HOLD_TRUST_RAILS"):
            validate(self.doc, self.root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
