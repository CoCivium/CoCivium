"""Negative-first test of unfinished read-only WorkID reconstitution across fresh processes.

Only synthetic virtual clock and same-provider SQLite/artifact fixture. No real X2.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import CoGoAllUnfinishedCanaryR0 as sut
from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue


class UnfinishedCanary(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / sut.SOURCE
        self.source.write_text("public, artificial sample; never external action\n")
        self.bundle = self.root / "artifact"
        self.receipt = self.root / "readback.json"
        self.context = {"run_id": "12345", "attempt": "1", "source_commit": "a"*40}

    def test_seed_then_new_python_process_recovers_exactly_once(self):
        sut.seed(self.root, self.bundle, self.context)
        command = """import json,sys
from pathlib import Path
from scripts.CoGoAllUnfinishedCanaryR0 import recover
root,bundle,receipt,ctx=sys.argv[1],sys.argv[2],sys.argv[3],json.loads(sys.argv[4])
print(json.dumps(recover(Path(root),Path(bundle),Path(receipt),ctx),sort_keys=True))
"""
        # A distinct Python process reopens the persisted SQLite database.
        result = subprocess.run([sys.executable, "-c", command,
                                 str(self.root), str(self.bundle), str(self.receipt),
                                 json.dumps(self.context)],
                                cwd=str(Path(__file__).resolve().parent),
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["recovered_epoch"], 2)
        self.assertTrue(parsed["old_worker_fenced"])
        self.assertEqual(parsed["completed_work_ids"], 1)
        self.assertEqual(parsed["external_effects"], 0)
        self.assertFalse(parsed["external_receiver_ack"])
        self.assertFalse(parsed["distinct_workflow_run"])
        self.assertEqual(json.loads(self.receipt.read_text()), parsed)
        q = DueWorkQueue(str(self.bundle / "queue.sqlite"))
        try:
            self.assertEqual(q.snapshot(1000)["complete"], 1)
            self.assertEqual(q.claim_due(now=1000, owner="third"), [])
        finally:
            q.close()
        with self.assertRaisesRegex(sut.Held, "HOLD_RECEIPT_EXISTS"):
            sut.recover(self.root, self.bundle, self.receipt, self.context)

    def test_seed_leaves_eligible_work_unfinished(self):
        info = sut.seed(self.root, self.bundle, self.context)
        self.assertFalse(info["effect_executed"])
        q = DueWorkQueue(str(self.bundle / "queue.sqlite"))
        try:
            self.assertEqual(q.snapshot(110)["complete"], 0)
            self.assertEqual(q.snapshot(129)["expired_leases"], 0)
            self.assertEqual(q.snapshot(130)["expired_leases"], 1)
        finally:
            q.close()

    def test_fail_closed_on_tampered_queue(self):
        sut.seed(self.root, self.bundle, self.context)
        with (self.bundle / "queue.sqlite").open("ab") as f:
            f.write(b"tamper")
        with self.assertRaisesRegex(sut.Held, "HOLD_QUEUE_TAMPER"):
            sut.recover(self.root, self.bundle, self.receipt, self.context)
        self.assertFalse(self.receipt.exists())

    def test_fail_closed_on_tampered_manifest(self):
        sut.seed(self.root, self.bundle, self.context)
        info = json.loads((self.bundle / "manifest.json").read_text())
        info["external_receiver_ack"] = True
        (self.bundle / "manifest.json").write_text(json.dumps(info))
        with self.assertRaisesRegex(sut.Held, "HOLD_AUTHORITY_INFLATION"):
            sut.recover(self.root, self.bundle, self.receipt, self.context)

    def test_source_drift_is_not_silently_accepted(self):
        sut.seed(self.root, self.bundle, self.context)
        self.source.write_text("changed\n")
        with self.assertRaisesRegex(sut.Held, "HOLD_SOURCE_DRIFT"):
            sut.recover(self.root, self.bundle, self.receipt, self.context)

    def test_other_run_or_commit_cannot_pick_up(self):
        sut.seed(self.root, self.bundle, self.context)
        for changed in ({**self.context,"run_id":"67890"},
                        {**self.context,"source_commit":"b"*40},
                        {**self.context,"attempt":"2"}):
            with self.assertRaisesRegex(sut.Held, "HOLD_CROSS_RUN_OR_SOURCE"):
                sut.recover(self.root, self.bundle, self.receipt, changed)

    def test_duplicate_seed_does_not_recreate_queue(self):
        sut.seed(self.root, self.bundle, self.context)
        with self.assertRaisesRegex(sut.Held,"HOLD_CREATE_ONLY_BUNDLE"):
            sut.seed(self.root, self.bundle, self.context)

    def test_symlink_queue_rejected(self):
        sut.seed(self.root, self.bundle, self.context)
        source = self.bundle / "queue.sqlite"
        foreign = self.root / "other.sqlite"
        source.rename(foreign)
        try:
            source.symlink_to(foreign)
        except (NotImplementedError, OSError):
            self.skipTest("No symlink support")
        with self.assertRaisesRegex(sut.Held,"HOLD_BUNDLE_FILE"):
            sut.recover(self.root, self.bundle, self.receipt, self.context)

    def test_context_requires_qualified_job_identity(self):
        env={"GITHUB_ACTIONS":"true","GITHUB_JOB":"unfinished-seed",
             "GITHUB_EVENT_NAME":"pull_request","GITHUB_SHA":"a"*40,
             "GITHUB_RUN_ID":"12345","GITHUB_RUN_ATTEMPT":"1"}
        with patch.object(sut.subprocess,"run",return_value=type("R",(),{"returncode":0,"stdout":"a"*40+"\n"})()):
            self.assertEqual(sut.ctx(self.root,env,"unfinished-seed"),self.context)
            with self.assertRaisesRegex(sut.Held,"HOLD_UNAUTHORIZED_EXECUTION_CONTEXT"):
                sut.ctx(self.root,env,"unfinished-recover")
        with patch.object(sut.subprocess,"run",return_value=type("R",(),{"returncode":0,"stdout":"b"*40+"\n"})()):
            with self.assertRaisesRegex(sut.Held,"HOLD_WORKFLOW_CHECKOUT_MISMATCH"):
                sut.ctx(self.root,env,"unfinished-seed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
