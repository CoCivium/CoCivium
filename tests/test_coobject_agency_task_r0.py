"""CoObject trusted one-task adapter: exact source, scope and cross-job replay."""
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.CoObjectAgencyTaskR0 import (
    CAPABILITY, FIXTURE, POLICY, Held, canonical, check_readback,
    digest, execute_one, source_sha, _read_json
)

ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40
WORK_ID = "CoObject.PolicyReview.1234.a1"


def now():
    return datetime.now(timezone.utc).isoformat()


class CoObjectOneTaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in (POLICY, FIXTURE):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / name).read_bytes())

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, **overrides):
        data = {"root": self.root, "work_id": WORK_ID, "source_head": HEAD,
                "observed_at": now(), "policy_sha": source_sha(self.root, POLICY),
                "fixture_sha": source_sha(self.root, FIXTURE)}
        data.update(overrides)
        return execute_one(**data)

    def test_real_existing_validator_executes(self):
        receipt = self.make()
        self.assertEqual(receipt["state"], "TRUSTED_READ_ONLY_VALIDATOR_EXECUTED_IN_CI")
        self.assertEqual(receipt["objects_validated"], 3)
        self.assertEqual(receipt["source_effect_class"], "READ_ONLY_VALIDATION_RECEIPT")
        self.assertFalse(receipt["external_receiver_ack"])
        self.assertFalse(receipt["product_mvp_qualified"])
        self.assertEqual(receipt["rights_review"], "NOT_PERFORMED")

    def test_separate_reader_recomputes_exact_validation(self):
        receipt = self.make()
        observed = check_readback(self.root, receipt, expected_work_id=WORK_ID,
                                  expected_source_head=HEAD)
        self.assertEqual(observed["state"],
                         "SECOND_CI_JOB_RECOMPUTED_SOURCE_AND_VALIDATION")
        self.assertTrue(observed["actual_local_validation"])
        self.assertFalse(observed["external_receiver_ack"])
        self.assertEqual(observed["provider_domain"], "SAME_GITHUB_ACTIONS")

    def test_source_tampering_blocks_proposal(self):
        original = source_sha(self.root, POLICY)
        (self.root / POLICY).write_text('{"changed":true}')
        with self.assertRaisesRegex(Held, "SOURCE_SHA256_MISMATCH"):
            self.make(policy_sha=original)

    def test_fixture_changed_after_receipt_blocks_readback(self):
        receipt = self.make()
        (self.root / FIXTURE).write_bytes(b'{"changed":true}')
        with self.assertRaisesRegex(Held, "SOURCE_SHA256_MISMATCH"):
            check_readback(self.root, receipt,
                           expected_work_id=WORK_ID, expected_source_head=HEAD)

    def test_wrong_id_not_accepted(self):
        with self.assertRaisesRegex(Held, "WORK_ID_NOT_BOUNDED"):
            self.make(work_id="another-work")

    def test_wrong_commit_not_accepted(self):
        with self.assertRaisesRegex(Held, "INVALID_SOURCE_HEAD"):
            self.make(source_head="main")

    def test_unregistered_capability_cannot_execute(self):
        with self.assertRaisesRegex(Held, "UNREGISTERED_CAPABILITY"):
            self.make(capability="RUN_ARBITRARY_PYTHON")

    def test_future_task_timestamp_not_accepted(self):
        with self.assertRaisesRegex(Held, "FUTURE_TASK_TIME"):
            self.make(observed_at="2030-01-01T00:00:00Z")

    def test_tampered_receipt_detected(self):
        receipt = self.make()
        receipt["objects_validated"] = 99
        with self.assertRaisesRegex(Held, "RECEIPT_TAMPERED"):
            check_readback(self.root, receipt, expected_work_id=WORK_ID,
                           expected_source_head=HEAD)

    def test_forged_ack_rehashed_detected_by_second_job(self):
        receipt = self.make()
        receipt["external_receiver_ack"] = True
        receipt["receipt_sha256"] = digest(canonical(
            {k:v for k,v in receipt.items() if k != "receipt_sha256"}))
        with self.assertRaisesRegex(Held, "RECEIPT_CONTENT_NOT_REPRODUCIBLE"):
            check_readback(self.root, receipt, expected_work_id=WORK_ID,
                           expected_source_head=HEAD)

    def test_forged_rights_review_rehashed_detected(self):
        receipt = self.make()
        receipt["rights_review"] = "PASSED"
        receipt["receipt_sha256"] = digest(canonical(
            {k:v for k,v in receipt.items() if k != "receipt_sha256"}))
        with self.assertRaisesRegex(Held, "RECEIPT_CONTENT_NOT_REPRODUCIBLE"):
            check_readback(self.root, receipt, expected_work_id=WORK_ID,
                           expected_source_head=HEAD)

    def test_wrong_runner_head_rejected(self):
        receipt = self.make()
        with self.assertRaisesRegex(Held, "RECEIPT_WRONG_RUN"):
            check_readback(self.root, receipt, expected_work_id=WORK_ID,
                           expected_source_head="b"*40)

    def test_invalid_policy_json_cannot_run_validator(self):
        (self.root / POLICY).write_bytes(b"{not-json")
        with self.assertRaisesRegex(Held, "POLICY_OR_FIXTURE_JSON_INVALID"):
            self.make()

    def test_symlinked_policy_rejected(self):
        path = self.root / POLICY
        target = path.with_name("policy-target.json")
        target.write_bytes(path.read_bytes())
        path.unlink()
        try:
            path.symlink_to(target)
        except OSError:
            self.skipTest("no symlink support")
        with self.assertRaisesRegex(Held, "SYMLINK_NOT_ALLOWED"):
            self.make()

    def test_malformed_receipt_file_denied(self):
        bad = self.root / "bad.json"
        bad.write_bytes(b"not-json")
        with self.assertRaisesRegex(Held, "INVALID_RECEIPT_JSON"):
            _read_json(bad)

    def test_produce_cli_requires_host_owned_context(self):
        script = ROOT / "scripts" / "CoObjectAgencyTaskR0.py"
        env = dict(os.environ)
        env.pop("GITHUB_ACTIONS", None)
        env.pop("GITHUB_JOB", None)
        proc = subprocess.run([sys.executable, "-B", str(script), "produce",
                               "--root", str(self.root),
                               "--receipt", str(self.root / "out.json")],
                              env=env, capture_output=True, text=True,
                              check=False, timeout=8)
        self.assertEqual(proc.returncode, 3)
        self.assertEqual(json.loads(proc.stdout)["reason"], "CI_JOB_IDENTITY_REQUIRED")

    def test_create_only_produce_replay_not_overwrite(self):
        script = ROOT / "scripts" / "CoObjectAgencyTaskR0.py"
        env = dict(os.environ, GITHUB_ACTIONS="true",
                   GITHUB_JOB="object-task", GITHUB_RUN_ID="1234",
                   GITHUB_RUN_ATTEMPT="1", GITHUB_SHA=HEAD)
        cmd = [sys.executable, "-B", str(script), "produce",
               "--root", str(self.root), "--receipt", str(self.root/"receipt.json")]
        first = subprocess.run(cmd, env=env, capture_output=True,
                               text=True, check=False, timeout=8)
        self.assertEqual(first.returncode, 0, first.stdout+first.stderr)
        second = subprocess.run(cmd, env=env, capture_output=True,
                                text=True, check=False, timeout=8)
        self.assertEqual(second.returncode, 3)
        self.assertEqual(json.loads(second.stdout)["state"], "HOLD")


if __name__ == "__main__":
    unittest.main(verbosity=2)
