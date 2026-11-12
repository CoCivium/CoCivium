"""Adversarial source-only CoGoAll due-WorkID handoff tests.

Run against the actual checked-out CoObject validator and policy/fixture.
Use a temporary SQLite store and no external effects. Git checkout identity
is mocked ONLY for fixture tests; the workflow canary checks it for real.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import scripts.CoGoAllDueWorkSourceCanaryR0 as sut
from scripts.CoObjectAgencyBridgeR0 import Held

ROOT = Path(__file__).resolve().parent
CTX = {"run_id": "1234567", "attempt": "1", "head": "a" * 40,
       "event": "push"}
PRODUCER = {"GITHUB_ACTIONS": "true", "GITHUB_JOB": "task-producer"}
RECEIVER = {"GITHUB_ACTIONS": "true", "GITHUB_JOB": "task-receiver"}


class BoundedCanaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bundle = Path(self.tmp.name) / "bounded"
        self.pin = patch.object(sut, "_require_checkout", return_value=CTX)
        self.pin.start()
        self.addCleanup(self.pin.stop)
        self.produced = sut.produce(ROOT, self.bundle, PRODUCER)

    def read(self):
        return sut.readback(ROOT, self.bundle, RECEIVER)

    def test_one_due_real_read_only_validation_and_separate_readback(self):
        result = self.read()
        self.assertEqual(result["state"],
                         "SAME_PROVIDER_SOURCE_VALIDATION_AND_FENCED_QUEUE_READBACK")
        self.assertTrue(result["due_work_selected"])
        self.assertTrue(result["fenced_local_completion"])
        self.assertTrue(result["read_only_validation_recomputed"])
        self.assertFalse(result["external_receiver_ack"])
        self.assertFalse(result["x2_runtime_qualified"])
        self.assertFalse(result["persistent_24h_seed_qualified"])
        self.assertEqual(result["checkpoint_scope"], "RUN_SCOPED_ARTIFACT_ONLY")

    def test_reject_duplicate_create_only_bundle(self):
        with self.assertRaisesRegex(Held, "HOLD_CREATE_ONLY_BUNDLE"):
            sut.produce(ROOT, self.bundle, PRODUCER)

    def test_reject_tampered_receipt_bytes(self):
        p = self.bundle / "task-receipt.json"
        p.write_text(p.read_text().replace("LOCAL_FIXTURE_POLICY_CONTRACT_PASS",
                                           "FORGED_QUALIFIED_USER_MVP"))
        with self.assertRaisesRegex(Held, "HOLD_RECEIPT_BYTES_DRIFT"):
            self.read()

    def test_reject_tampered_queue_bytes(self):
        p = self.bundle / "queue.sqlite"
        with p.open("ab") as f:
            f.write(b"forged")
        with self.assertRaisesRegex(Held, "HOLD_QUEUE_BYTES_DRIFT"):
            self.read()

    def test_reject_absent_queue(self):
        (self.bundle / "queue.sqlite").unlink()
        with self.assertRaisesRegex(Held, "HOLD_MISSING_OR_SYMLINK_ARTIFACT"):
            self.read()

    def test_reject_source_commit_drift(self):
        p = self.bundle / "checkpoint.json"
        obj = json.loads(p.read_text())
        obj["source_commit"] = "b" * 40
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(Held, "HOLD_WRONG_RUN_OR_SOURCE"):
            self.read()

    def test_reject_external_ack_inflation(self):
        p = self.bundle / "checkpoint.json"
        obj = json.loads(p.read_text())
        obj["external_receiver_ack"] = True
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(Held, "HOLD_EFFECT_OR_AUTHORITY_INFLATION"):
            self.read()

    def test_reject_wrong_event_claim(self):
        p = self.bundle / "checkpoint.json"
        obj = json.loads(p.read_text())
        obj["event"] = "schedule"
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(Held, "HOLD_WRONG_RUN_OR_SOURCE"):
            self.read()

    def test_reject_policy_digest_drift(self):
        p = self.bundle / "checkpoint.json"
        obj = json.loads(p.read_text())
        obj["policy_sha256"] = "0" * 64
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(Held, "HOLD_CHANGED_TASK_SOURCE"):
            self.read()

    def test_reject_lease_epoch_inflation(self):
        p = self.bundle / "checkpoint.json"
        obj = json.loads(p.read_text())
        obj["lease_epoch"] = 999
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(Held, "HOLD_QUEUE_COMMIT_MISMATCH"):
            self.read()

    def test_reject_result_sha_mismatch_even_if_file_hash_rebound(self):
        p = self.bundle / "task-receipt.json"
        obj = json.loads(p.read_text())
        obj["validation_result_sha256"] = "f" * 64
        p.write_text(json.dumps(obj) + "\n")
        cp = self.bundle / "checkpoint.json"
        chk = json.loads(cp.read_text())
        chk["receipt_file_sha256"] = sut._sha(p.read_bytes())
        cp.write_text(json.dumps(chk))
        with self.assertRaisesRegex(Held, "RECEIPT_TAMPERED"):
            self.read()

    def test_reject_unexpected_checkpoint_field(self):
        p = self.bundle / "checkpoint.json"
        obj = json.loads(p.read_text())
        obj["implied_canon"] = True
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(Held, "HOLD_CHECKPOINT_SCHEMA"):
            self.read()

    def test_queue_cannot_be_silently_replaced_even_if_valid_shape(self):
        p = self.bundle / "queue.sqlite"
        original = p.read_bytes()
        p.write_bytes(original + b"!")
        with self.assertRaisesRegex(Held, "HOLD_QUEUE_BYTES_DRIFT"):
            self.read()

    def test_symlink_receipt_fails_closed(self):
        p = self.bundle / "task-receipt.json"
        link_target = self.bundle / "receipt-copy.json"
        shutil.copyfile(p, link_target)
        p.unlink()
        try:
            p.symlink_to(link_target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unsupported")
        with self.assertRaisesRegex(Held, "HOLD_MISSING_OR_SYMLINK_ARTIFACT"):
            self.read()


class ContextDenialTests(unittest.TestCase):
    def test_absent_workflow_identity_fails(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(Held, "HOLD_UNTRUSTED_JOB_CONTEXT"):
                sut._require_checkout(Path(root), {}, "task-producer")

    def test_reject_malformed_sha_before_git(self):
        with tempfile.TemporaryDirectory() as root:
            env = {"GITHUB_ACTIONS": "true", "GITHUB_JOB": "task-producer",
                   "GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "1",
                   "GITHUB_SHA": "not-a-commit", "GITHUB_EVENT_NAME": "push"}
            with self.assertRaisesRegex(Held, "HOLD_SOURCE_COMMIT"):
                sut._require_checkout(Path(root), env, "task-producer")


    def test_pr_event_allowed_only_with_bound_checkout(self):
        from types import SimpleNamespace
        env = {"GITHUB_ACTIONS": "true", "GITHUB_JOB": "task-producer",
               "GITHUB_RUN_ID": "11", "GITHUB_RUN_ATTEMPT": "1",
               "GITHUB_SHA": "a" * 40, "GITHUB_EVENT_NAME": "pull_request"}
        with patch.object(sut.subprocess, "run",
                          return_value=SimpleNamespace(returncode=0, stdout="a" * 40 + "\n")):
            with tempfile.TemporaryDirectory() as root:
                ctx = sut._require_checkout(Path(root), env, "task-producer")
        self.assertEqual(ctx["event"], "pull_request")

    def test_pr_event_with_wrong_checkout_fails_closed(self):
        from types import SimpleNamespace
        env = {"GITHUB_ACTIONS": "true", "GITHUB_JOB": "task-producer",
               "GITHUB_RUN_ID": "11", "GITHUB_RUN_ATTEMPT": "1",
               "GITHUB_SHA": "a" * 40, "GITHUB_EVENT_NAME": "pull_request"}
        with patch.object(sut.subprocess, "run",
                          return_value=SimpleNamespace(returncode=0, stdout="b" * 40 + "\n")):
            with tempfile.TemporaryDirectory() as root:
                with self.assertRaisesRegex(Held, "HOLD_CHECKOUT_HEAD_MISMATCH"):
                    sut._require_checkout(Path(root), env, "task-producer")


if __name__ == "__main__":
    unittest.main(verbosity=2)
