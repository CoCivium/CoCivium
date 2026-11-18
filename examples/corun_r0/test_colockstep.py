"""CoLockStep R0 source-qualified compatibility checks and falsifiers.

Source coherence cannot certify a deployable product or a human receiver.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

try:
    from .colockstep import (assess, canonical, source_components,
                            compatible_edges, write_report)
except ImportError:
    from colockstep import (assess, canonical, source_components,
                           compatible_edges, write_report)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = HERE / "colockstep_fixture.json"


def source():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class SourceIslandTests(unittest.TestCase):
    def test_both_pinned_source_snapshots_read_back(self):
        v = source()
        old, errors, evidence = source_components(v["baseline"], ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(len(evidence), 2)
        self.assertEqual(len(old), 2)
        _, new_errors, new_evidence = source_components(v["candidate"], ROOT)
        self.assertEqual(new_errors, [])
        self.assertEqual(len(new_evidence), 3)

    def test_compatible_candidate_cannot_claim_mvp(self):
        out = assess(source(), ROOT)
        self.assertEqual(out["result"], "SOURCE_COHERENT__NOT_MVP")
        self.assertTrue(out["candidate_source_compatible"])
        self.assertTrue(out["baseline_source_verified"])
        self.assertTrue(out["previous_baseline_preserved"])
        self.assertFalse(out["qualified_mvp"])
        self.assertFalse(out["claimed_receiver_readproof_accepted"])
        self.assertEqual(out["release_actuator"], "NONE")
        self.assertEqual(out["runtime_activation"], "NOT_ATTEMPTED")

    def test_candidate_interface_regression_held(self):
        v = source()
        v["candidate"]["components"][0]["provides"]["case-audit"] = 2
        out = assess(v, ROOT)
        self.assertEqual(out["result"], "CANDIDATE_HELD_BASELINE_PRESERVED")
        self.assertIn("BROKE_BASELINE_PUBLIC_CONTRACT:dag-runner",
                      out["candidate_holds"])
        self.assertIn("INCOMPATIBLE_INTERFACE:differential-check:dag-runner",
                      out["candidate_holds"])
        self.assertTrue(out["previous_baseline_preserved"])

    def test_dropped_or_renamed_predecessor_held(self):
        v = source()
        v["candidate"]["components"] = [
            c for c in v["candidate"]["components"]
            if c["id"] != "reference-oracle"
        ]
        out = assess(v, ROOT)
        self.assertIn("REMOVED_BASELINE_COMPONENT:reference-oracle",
                      out["candidate_holds"])
        self.assertFalse(out["candidate_source_compatible"])

    def test_unproven_source_change_held(self):
        v = source()
        v["candidate"]["components"][0]["git_blob_sha1"] = "0" * 40
        out = assess(v, ROOT)
        self.assertIn("SOURCE_DRIFT:dag-runner", out["candidate_holds"])
        self.assertFalse(out["candidate_source_compatible"])

    def test_old_failure_records_must_survive(self):
        v = source()
        v["candidate"]["historical_fail_ids"].remove("COFLOW_F04")
        out = assess(v, ROOT)
        self.assertIn("DROPPED_HISTORICAL_FAILURE_LINEAGE",
                      out["candidate_holds"])

    def test_unknown_runtime_and_receiver_claim_never_promote(self):
        v = source()
        v["candidate"]["qualified_mvp"] = True
        v["candidate"]["receiver_ack"] = "VERIFIED_BY_CANDIDATE"
        out = assess(v, ROOT)
        self.assertFalse(out["qualified_mvp"])
        self.assertFalse(out["claimed_receiver_readproof_accepted"])

    def test_candidate_serving_claim_held(self):
        v = source()
        v["candidate"]["scope"] = "RUNNING_ON_X2"
        out = assess(v, ROOT)
        self.assertIn("CLAIMED_SERVING_WITHOUT_RECEIVER_PROOF",
                      out["candidate_holds"])

    def test_authority_scope_cannot_expand(self):
        v = source()
        v["candidate"]["components"][2]["effect_scope"] = "SEND_EMAIL"
        out = assess(v, ROOT)
        self.assertIn("effect scope must be read-only",
                      " ".join(out["candidate_holds"]))
        self.assertFalse(out["qualified_mvp"])

    def test_dependency_cycle_blocks_candidate(self):
        v = source()
        v["candidate"]["dependencies"].append({
            "consumer": "dag-runner",
            "provider": "differential-check",
            "interface": "compare-report",
            "major": 1,
        })
        out = assess(v, ROOT)
        self.assertIn("DEPENDENCY_CYCLE", out["candidate_holds"])

    def test_mismatched_dependency_major_held(self):
        v = source()
        v["candidate"]["dependencies"][0]["major"] = 2
        out = assess(v, ROOT)
        self.assertIn("INCOMPATIBLE_INTERFACE:differential-check:dag-runner",
                      out["candidate_holds"])

    def test_candidate_missing_pin_is_held(self):
        v = source()
        del v["candidate"]["components"][2]["git_blob_sha1"]
        out = assess(v, ROOT)
        self.assertIn("invalid source pin", " ".join(out["candidate_holds"]))

    def test_baseline_drift_fails_closed_not_held(self):
        v = source()
        v["baseline"]["components"][0]["git_blob_sha1"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "BASELINE_SOURCE_NOT_RECOVERABLE"):
            assess(v, ROOT)

    def test_does_not_modify_inputs(self):
        v = source()
        old_bytes = canonical(v)
        assess(v, ROOT)
        self.assertEqual(old_bytes, canonical(v))

    def test_receipt_exact_and_no_overwrite(self):
        v = assess(source(), ROOT)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "run"
            report, rec = write_report(dest, v)
            proof = json.loads(rec.read_text(encoding="utf-8"))
            self.assertEqual(proof["report_sha256"],
                             hashlib.sha256(report.read_bytes()).hexdigest())
            self.assertFalse(proof["qualified_mvp"])
            self.assertFalse(proof["real_receiver_ack"])
            with self.assertRaises(FileExistsError):
                write_report(dest, v)


if __name__ == "__main__":
    unittest.main()
