"""Negative controls for read-only historical CoGoAll WorkID readback.

The actual previously retained GitHub artifacts are required for the CI job;
these tests prove early-denial behavior with synthetic local objects only.
"""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import scripts.CoGoAllPriorRunReadbackR0 as sut
from scripts.CoObjectAgencyBridgeR0 import Held


class PriorRunReadbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.meta1 = self.root / "producer.json"
        self.meta2 = self.root / "receiver.json"
        self.ctx = {"run_id":"1111111111","attempt":"1","source_head":"c"*40}
        self.clock = datetime.fromtimestamp(sut.PIN["completed_at"] + 300,
                                             tz=timezone.utc)

    def metadata(self, which):
        return {
            "id":sut.PIN[which+"_artifact_id"],
            "name":sut.PIN[which+"_artifact_name"],
            "digest":sut.PIN[which+"_archive_digest"],
            "expired":False,
            "workflow_run":{"id":int(sut.PIN["prior_run"])},
        }

    def write_metadata(self):
        self.meta1.write_text(json.dumps(self.metadata("producer")))
        self.meta2.write_text(json.dumps(self.metadata("receiver")))

    def test_metadata_pins_two_distinct_archive_identities(self):
        self.write_metadata()
        result = sut.verify_metadata(self.meta1,self.meta2,sut.PIN)
        self.assertEqual(result["producer_artifact_id"],13738906845)
        self.assertEqual(result["receiver_artifact_id"],13739355879)
        self.assertEqual(result["archive_metadata"],
                         "PINNED_GITHUB_ASSERTION_NOT_LOCAL_ZIP_HASH")

    def test_tampered_archive_digest_is_held(self):
        self.write_metadata()
        x = self.metadata("producer")
        x["digest"] = "sha256:" + "0"*64
        self.meta1.write_text(json.dumps(x))
        with self.assertRaisesRegex(Held,"HOLD_PRIOR_ARTIFACT_METADATA_PRODUCER"):
            sut.verify_metadata(self.meta1,self.meta2,sut.PIN)

    def test_wrong_prior_run_is_held(self):
        self.write_metadata()
        x = self.metadata("receiver")
        x["workflow_run"]["id"] += 1
        self.meta2.write_text(json.dumps(x))
        with self.assertRaisesRegex(Held,"HOLD_PRIOR_ARTIFACT_RUN_RECEIVER"):
            sut.verify_metadata(self.meta1,self.meta2,sut.PIN)

    def test_expired_archive_is_held(self):
        self.write_metadata()
        x = self.metadata("producer")
        x["expired"] = True
        self.meta1.write_text(json.dumps(x))
        with self.assertRaisesRegex(Held,"HOLD_PRIOR_ARTIFACT_METADATA_PRODUCER"):
            sut.verify_metadata(self.meta1,self.meta2,sut.PIN)

    def test_wrong_archive_identity_is_held(self):
        self.write_metadata()
        x = self.metadata("producer")
        x["name"] = "unrelated-task"
        self.meta1.write_text(json.dumps(x))
        with self.assertRaisesRegex(Held,"HOLD_PRIOR_ARTIFACT_METADATA_PRODUCER"):
            sut.verify_metadata(self.meta1,self.meta2,sut.PIN)

    def test_not_distinct_run_is_held(self):
        with self.assertRaisesRegex(Held,"HOLD_NOT_DISTINCT_RUN"):
            sut.reobserve(self.root,self.root,self.root,self.meta1,self.meta2,
                          ctx={**self.ctx,"run_id":sut.PIN["prior_run"]},
                          pin=sut.PIN,observed_at=self.clock)

    def test_future_prior_completion_is_held(self):
        with self.assertRaisesRegex(Held,"HOLD_PRIOR_IN_FUTURE"):
            sut.reobserve(self.root,self.root,self.root,self.meta1,self.meta2,
                          ctx=self.ctx,pin=sut.PIN,
                          observed_at=datetime.fromtimestamp(
                              sut.PIN["completed_at"]-1,tz=timezone.utc))

    def test_utc_observation_required(self):
        with self.assertRaisesRegex(Held,"HOLD_OBSERVATION_NOT_UTC"):
            sut.reobserve(self.root,self.root,self.root,self.meta1,self.meta2,
                          ctx=self.ctx,pin=sut.PIN,
                          observed_at=datetime.fromtimestamp(
                              sut.PIN["completed_at"]+1))

    def test_missing_prior_artifacts_fail_before_claiming_effect(self):
        with self.assertRaisesRegex(Held,"HOLD_MISSING_OR_SYMLINK_PRIOR_OBJECT"):
            sut.reobserve(self.root,self.root,self.root,self.meta1,self.meta2,
                          ctx=self.ctx,pin=sut.PIN,observed_at=self.clock)

    def test_identity_context_requires_specific_ci_job(self):
        with self.assertRaisesRegex(Held,"HOLD_CI_PRIOR_READER_IDENTITY"):
            sut.context(self.root,{"GITHUB_ACTIONS":"true",
                                  "GITHUB_JOB":"task-producer"})

    def test_checkout_mismatch_is_held(self):
        env={"GITHUB_ACTIONS":"true","GITHUB_JOB":"prior-task-reader",
             "GITHUB_EVENT_NAME":"pull_request","GITHUB_RUN_ID":"123",
             "GITHUB_RUN_ATTEMPT":"1","GITHUB_SHA":"a"*40}
        with patch.object(sut.subprocess,"run",return_value=SimpleNamespace(
                returncode=0,stdout="b"*40+"\n")):
            with self.assertRaisesRegex(Held,"HOLD_NEW_RUN_CHECKOUT_MISMATCH"):
                sut.context(self.root,env)

    def test_current_checkout_context_binds_pr_head(self):
        env={"GITHUB_ACTIONS":"true","GITHUB_JOB":"prior-task-reader",
             "GITHUB_EVENT_NAME":"pull_request","GITHUB_RUN_ID":"123",
             "GITHUB_RUN_ATTEMPT":"1","GITHUB_SHA":"a"*40}
        with patch.object(sut.subprocess,"run",return_value=SimpleNamespace(
                returncode=0,stdout="a"*40+"\n")):
            result=sut.context(self.root,env)
        self.assertEqual(result["run_id"],"123")
        self.assertEqual(result["source_head"],"a"*40)

    def test_prior_checkpoint_byte_tamper_held(self):
        self.write_metadata()
        (self.root/"checkpoint.json").write_bytes(b'{"schema":"wrong"}\n')
        with self.assertRaisesRegex(Held,"HOLD_PRIOR_CHECKPOINT_DIGEST"):
            sut.reobserve(self.root,self.root,self.root,self.meta1,self.meta2,
                          ctx=self.ctx,pin=sut.PIN,observed_at=self.clock)

    def test_create_only_receiver_receipt(self):
        out=self.root/"readback.json"
        sut.write_new(out,{"example":"bounded"})
        with self.assertRaises(FileExistsError):
            sut.write_new(out,{"example":"clobber"})


if __name__=="__main__":
    unittest.main(verbosity=2)
