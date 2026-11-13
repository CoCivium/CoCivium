"""Adversarial, local-only CoWake admission journal tests. No scheduler/host effects."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from types import SimpleNamespace
import copy
import hashlib
import json
import sqlite3
import unittest

from scripts.CoGoAllWakeAdmissionR0 import SCHEMA
from scripts.CoGoAllWakeAdmissionJournalR0 import admit

HEAD = "c" * 40
NOW = datetime(2026, 11, 13, 15, 7, tzinfo=timezone.utc)
PATH = "ai/currentness/public-synthetic-r0.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        p = self.root / PATH
        p.parent.mkdir(parents=True)
        p.write_bytes(b'{"kind":"PUBLIC_SYNTHETIC","value":1}\n')
        self.path = p
        self.event = {
            "schema": SCHEMA,
            "event_id": "source-delta-01",
            "work_id": "CoAll.Work.SourceReview.R0",
            "source_path": PATH,
            "source_revision": HEAD,
            "source_sha256": sha(p.read_bytes()),
            "observed_at_utc": "2026-11-13T15:02:00Z",
            "materiality": "MATERIAL_DELTA",
            "materiality_evidence_sha256": "b" * 64,
            "authority_ceiling": "PUBLIC_READ_ONLY_SOURCE_VALIDATION",
            "confidentiality": "PUBLIC_SYNTHETIC",
            "collision_domain": "CI_PUBLIC_SOURCE_REVIEW",
            "idempotency_key": "coall-work-source-review-01",
            "predecessor_checkpoint_sha256": None,
            "receiver_class": "EXISTING_COGOALL_CI_SOURCE_VALIDATOR",
            "receiver_ready": True,
            "wake_condition": "ON_QUALIFIED_MATERIAL_DELTA",
            "stop_condition": "STOP_ON_HOLD_OR_NO_DELTA",
            "claimed_external_ack": False,
        }
        self.head = patch("scripts.CoGoAllWakeAdmissionJournalR0.subprocess.run",
                          return_value=SimpleNamespace(returncode=0,stdout=HEAD+"\n"))
        self.head.start()
        self.addCleanup(self.head.stop)

    def test_first_admission_then_exact_replay_quiet(self):
        a = admit(self.root, self.event, NOW)
        self.assertEqual(a["state"], "ADMITTED_LOCAL_ONLY_WAITING_FOR_WORKER")
        self.assertTrue(a["queue_admitted"])
        self.assertEqual(a["queue_state"], "PENDING")
        b = admit(self.root, copy.deepcopy(self.event), NOW)
        self.assertEqual(b["state"], "QUIESCENT_ALREADY_ADMITTED")
        self.assertFalse(b["queue_admitted"])
        self.assertEqual(b["wake_id"], a["wake_id"])
        self.assertFalse(b["external_receiver_ack"])
        self.assertFalse(b["task_dispatched"])

    def test_restart_readback_same_db_no_duplicate(self):
        a = admit(self.root, self.event, NOW)
        self.assertTrue(a["queue_admitted"])
        b = admit(self.root, self.event, NOW)
        self.assertEqual(b["state"], "QUIESCENT_ALREADY_ADMITTED")
        db = self.root/"out"/"cogoall"/"wake-admission-r0.sqlite"
        with sqlite3.connect(db) as sql:
            self.assertEqual(sql.execute("SELECT COUNT(*) FROM work").fetchone()[0], 1)
            self.assertEqual(sql.execute("SELECT state,epoch FROM work").fetchone(), ("PENDING",0))

    def test_conflicting_event_same_workid_cannot_clobber(self):
        admit(self.root, self.event, NOW)
        event={**self.event,"event_id":"source-delta-02"}
        out=admit(self.root,event,NOW)
        self.assertEqual(out["reason"],"HOLD_SAME_WORKID_DIFFERENT_WAKE_OR_SOURCE")

    def test_foreign_workid_in_single_owner_db_holds(self):
        admit(self.root,self.event,NOW)
        event={**self.event,"work_id":"Another.WorkID"}
        out=admit(self.root,event,NOW)
        self.assertEqual(out["reason"],"HOLD_FOREIGN_WORK_IN_SINGLE_OWNER_QUEUE")

    def test_source_file_changed_after_claim_holds_without_queue(self):
        self.path.write_text('{"value":"changed"}\n')
        result=admit(self.root,self.event,NOW)
        self.assertEqual(result["reason"],"HOLD_SOURCE_BYTE_DRIFT")
        self.assertFalse((self.root/"out"/"cogoall"/"wake-admission-r0.sqlite").exists())

    def test_checkout_head_drift_holds(self):
        with patch("scripts.CoGoAllWakeAdmissionJournalR0.subprocess.run",
                   return_value=SimpleNamespace(returncode=0,stdout="d"*40+"\n")):
            result=admit(self.root,self.event,NOW)
        self.assertEqual(result["reason"],"HOLD_CHECKOUT_REVISION_DRIFT")

    def test_untrusted_relative_path_holds(self):
        for path in ("../secret.json", "ai/currentness/../secret.json",
                     "C:\\private.json", "ai/secret.json"):
            result=admit(self.root,{**self.event,"source_path":path},NOW)
            self.assertFalse(result["queue_admitted"])
            self.assertEqual(result["state"],"HOLD_LOCAL_WAKE_ADMISSION")

    def test_source_symlink_holds(self):
        target=self.root/"other.json"
        target.write_text('{"value":1}\n')
        self.path.unlink()
        self.path.symlink_to(target)
        self.event["source_sha256"]=sha(target.read_bytes())
        result=admit(self.root,self.event,NOW)
        self.assertEqual(result["reason"],"HOLD_SOURCE_PATH_OR_SYMLINK")

    def test_source_not_json_holds_even_with_matching_hash(self):
        self.path.write_bytes(b"not-json")
        self.event["source_sha256"]=sha(self.path.read_bytes())
        result=admit(self.root,self.event,NOW)
        self.assertEqual(result["reason"],"HOLD_SOURCE_NOT_JSON")

    def test_no_delta_no_db_created(self):
        result=admit(self.root,{**self.event,"materiality":"NO_MATERIAL_DELTA"},NOW)
        self.assertEqual(result["state"],"QUIESCENT_NO_WAKE")
        self.assertFalse((self.root/"out"/"cogoall"/"wake-admission-r0.sqlite").exists())

    def test_unknown_privacy_or_elevated_authority_holds(self):
        for mutation in ({"confidentiality":"UNKNOWN"},
                         {"authority_ceiling":"WRITE"},
                         {"claimed_external_ack":True},
                         {"receiver_ready":False},
                         {"native_effect_authorized":True}):
            result=admit(self.root,{**self.event,**mutation},NOW)
            self.assertFalse(result["queue_admitted"])
            self.assertEqual(result["state"],"HOLD_LOCAL_WAKE_ADMISSION")

    def test_journal_output_never_forges_effect(self):
        result=admit(self.root,self.event,NOW)
        self.assertFalse(result["materiality_independently_attested"])
        self.assertFalse(result["prior_journal_authenticated"])
        self.assertFalse(result["task_dispatched"])
        self.assertFalse(result["external_receiver_ack"])
        self.assertEqual(result["source_attestation"],
                         "CHECKOUT_HEAD_AND_EXACT_LOCAL_FILE_SHA256")

    def test_invalid_lease_not_silently_repaired(self):
        admit(self.root,self.event,NOW)
        db=self.root/"out"/"cogoall"/"wake-admission-r0.sqlite"
        with sqlite3.connect(db) as sql:
            sql.execute("UPDATE work SET state='LEASED',epoch=3,owner='other',lease_until=1000")
        result=admit(self.root,self.event,NOW)
        self.assertEqual(result["state"],"QUIESCENT_ALREADY_ADMITTED")
        self.assertEqual(result["queue_state"],"LEASED")
        self.assertEqual(result["lease_epoch"],3)


if __name__ == "__main__":
    unittest.main()
