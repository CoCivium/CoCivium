"""Negative controls for the proof-bounded walk-away status projector."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from walkaway_projection_r0 import DEFAULT_INPUT, GATES, SCHEMA, project

class WalkAwayReadinessTests(unittest.TestCase):
    def fixture(self):
        return deepcopy(DEFAULT_INPUT)

    def test_current_case_never_claims_ready(self):
        result = project(self.fixture())
        self.assertEqual(result["state"], "HOLD_NOT_WALKAWAY_READY")
        self.assertEqual(result["reported_observation_count"], 2)
        self.assertEqual(result["qualified_live_gate_count"], 0)
        self.assertEqual(result["next_safe_action"], "RECEIVER_ORIGIN_EXACT_OBJECT_READBACK_ISSUE_317")
        self.assertEqual(result["next_owner"], "#317")
        self.assertTrue(result["cobar"]["action_is_read_only"])

    def test_synthetic_and_local_not_receiver(self):
        f = self.fixture()
        f["observations"]["receiver"] = {"scope": "CI_SYNTHETIC", "source_ref": "test"}
        with self.assertRaisesRegex(ValueError, "SCOPE_CONFLICT_receiver"):
            project(f)

    def test_self_asserted_receiver_ack_rejected(self):
        f = self.fixture()
        f["observations"]["receiver"] = {
            "scope": "RECEIVER_ORIGIN", "source_ref": "self-asserted",
            "receiver_ack": True
        }
        with self.assertRaisesRegex(ValueError, "INVALID_OBSERVATION_receiver"):
            project(f)

    def test_full_claims_still_not_certified(self):
        f = self.fixture()
        for gate, _, scope in GATES:
            f["observations"][gate] = {"scope": scope, "source_ref": "SELF_CLAIM_NO_AUTH"}
        result = project(f)
        self.assertEqual(result["state"], "HOLD_EXTERNAL_EVIDENCE_AUTHENTICATION_REQUIRED")
        self.assertEqual(result["qualified_live_gate_count"], 0)

    def test_missing_provenance_rejected(self):
        f = self.fixture()
        f["observations"]["receiver"] = {"scope": "RECEIVER_ORIGIN"}
        with self.assertRaisesRegex(ValueError, "MISSING_PROVENANCE_receiver"):
            project(f)

    def test_extra_gate_rejected(self):
        f = self.fixture()
        f["observations"]["secret_new_scheduler"] = {"scope": "UNOBSERVED"}
        with self.assertRaisesRegex(ValueError, "MISSING_OR_UNKNOWN_GATES"):
            project(f)

    def test_reference_without_observation_rejected(self):
        f = self.fixture()
        f["observations"]["receiver"] = {"scope": "UNOBSERVED", "source_ref": "bogus"}
        with self.assertRaisesRegex(ValueError, "REF_WITHOUT_OBSERVATION_receiver"):
            project(f)

    def test_no_workid_rejected(self):
        f = self.fixture()
        f["work_id"] = ""
        with self.assertRaisesRegex(ValueError, "INVALID_WORKID"):
            project(f)

    def test_cli_default_is_pure_and_hold(self):
        module = Path(__file__).with_name("walkaway_projection_r0.py")
        with tempfile.TemporaryDirectory() as base:
            before = list(Path(base).iterdir())
            run = subprocess.run([sys.executable, "-B", str(module)],
                                 cwd=base, capture_output=True, text=True,
                                 timeout=10, check=True)
            result = json.loads(run.stdout)
            self.assertEqual(result["state"], "HOLD_NOT_WALKAWAY_READY")
            self.assertEqual(list(Path(base).iterdir()), before)
            self.assertTrue(result["cobar"]["action_is_read_only"])
            self.assertEqual(result["human_relay_required_for_this_projection"], False)

    def test_invalid_input_is_held_not_crash(self):
        module = Path(__file__).with_name("walkaway_projection_r0.py")
        with tempfile.TemporaryDirectory() as base:
            path = Path(base) / "bad.json"
            path.write_text(json.dumps({"schema": SCHEMA}), encoding="utf-8")
            run = subprocess.run([sys.executable, "-B", str(module), "--input", str(path)],
                                 cwd=base, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)["state"], "HOLD_INVALID_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
