"""Synthetic adversarial tests for a later, DISTINCT GitHub run's pinned pickup.

No claim about separate service provider or physical elapsed time.
"""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from scripts import CoGoAllUnfinishedPriorWakeR0 as sut
from scripts.CoGoAllUnfinishedCanaryR0 import seed, sha


class PinTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.old=self.root/"old-source"
        self.old.mkdir()
        (self.old/"CoPre.md").write_bytes(b"fixed old source\n")
        self.bundle=self.root/"prior-run-artifact"
        self.meta=self.root/"artifact-meta.json"
        self.stage=self.root/"stage-readback.json"
        self.out=self.root/"later-run-readback.json"
        self.pin={**sut.PIN,"source_commit":"a"*40,
                  "source_sha256":sha((self.old/"CoPre.md").read_bytes())}
        self.prior={"run_id":self.pin["run_id"],"attempt":"1",
                    "source_commit":self.pin["source_commit"]}
        seed(self.old,self.bundle,self.prior)
        self.pin["manifest_sha256"]=sha((self.bundle/"manifest.json").read_bytes())
        self.pin["queue_sha256"]=sha((self.bundle/"queue.sqlite").read_bytes())
        self.current={"run_id":"999998","attempt":"1","source_commit":"b"*40}
        self.meta.write_text(json.dumps({"id":self.pin["artifact_id"],
             "name":self.pin["artifact_name"],"digest":self.pin["artifact_digest"],
             "expired":False,"workflow_run":{"id":int(self.pin["run_id"])}}))

    def verify(self, **kwargs):
        with patch.object(sut.subprocess,"run",return_value=SimpleNamespace(
                returncode=0,stdout=self.pin["source_commit"]+"\n")):
            return sut.verified_original(self.root,self.old,self.bundle,self.meta,
                                        self.current,kwargs.get("pin",self.pin))

    def complete(self):
        with patch.object(sut.subprocess,"run",return_value=SimpleNamespace(
                returncode=0,stdout=self.pin["source_commit"]+"\n")):
            return sut.recover_previous(self.root,self.old,self.bundle,self.meta,
                self.stage,self.out,self.current,self.pin)

    def test_pinned_distinct_run_success_with_limited_scope(self):
        r=self.complete()
        self.assertTrue(r["distinct_workflow_run"])
        self.assertTrue(r["prior_unfinished_state_qualified"])
        self.assertTrue(r["expired_owner_fenced"])
        self.assertEqual(r["completed_work_ids"],1)
        self.assertFalse(r["actual_lease_elapsed_time_verified"])
        self.assertFalse(r["independent_receiver_ack"])
        self.assertFalse(r["new_external_effect_executed"])
        self.assertEqual(json.loads(self.out.read_text()),r)
        with self.assertRaisesRegex(sut.Held,"HOLD_EXISTING_RECEIPT"):
            self.complete()

    def test_same_run_refused(self):
        self.current["run_id"]=self.pin["run_id"]
        with self.assertRaisesRegex(sut.Held,"HOLD_NOT_DISTINCT_RUN"):
            self.verify()

    def test_wrong_historical_git_commit_refused(self):
        with patch.object(sut.subprocess,"run",return_value=SimpleNamespace(
                returncode=0,stdout="f"*40+"\n")):
            with self.assertRaisesRegex(sut.Held,"HOLD_PINNED_GIT_COMMIT_MISMATCH"):
                sut.verified_original(self.root,self.old,self.bundle,self.meta,
                                      self.current,self.pin)

    def test_expired_or_replaced_github_metadata_refused(self):
        for name,value in (("expired",True),("digest","sha256:"+"0"*64),
                           ("id",123),("name","wrong")):
            original=json.loads(self.meta.read_text())
            changed={**original,name:value}
            self.meta.write_text(json.dumps(changed))
            with self.assertRaisesRegex(sut.Held,"HOLD_ARCHIVE_METADATA_MISMATCH"):
                self.verify()
            self.meta.write_text(json.dumps(original))

    def test_tampered_manifest_rejected_before_effect(self):
        with (self.bundle/"manifest.json").open("ab") as f:f.write(b"x")
        with self.assertRaisesRegex(sut.Held,"HOLD_MANIFEST_DIGEST"):
            self.verify()
        self.assertFalse(self.out.exists())

    def test_tampered_queue_rejected_before_effect(self):
        with (self.bundle/"queue.sqlite").open("ab") as f:f.write(b"z")
        with self.assertRaisesRegex(sut.Held,"HOLD_QUEUE_DIGEST"):
            self.verify()
        self.assertFalse(self.out.exists())

    def test_prior_source_byte_drift_rejected(self):
        (self.old/"CoPre.md").write_text("different\n")
        with self.assertRaisesRegex(sut.Held,"HOLD_SOURCE_DRIFT"):
            self.verify()

    def test_wrong_original_workid_rejected(self):
        self.pin["work_id"]="CoGoAll.Unfinished.99.a1"
        with self.assertRaisesRegex(sut.Held,"HOLD_PINNED_WORKID_OR_SOURCE"):
            self.verify()


if __name__=="__main__":unittest.main(verbosity=2)
