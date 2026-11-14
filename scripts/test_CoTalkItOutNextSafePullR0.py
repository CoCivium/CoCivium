#!/usr/bin/env python3
"""Negative controls: source-only work selection never becomes dispatch."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from CoTalkItOutNextSafePullR0 import (
    ROOT, CSV_PATH, SCHEMA, ROLES, WORKID, choose, pull,
)
from verify_cotalkitout_headless_roadmap_r0 import EXPECTED_SHA256
import csv
import io

class RoleScopedPullTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=CSV_PATH.read_bytes()
        cls.records=list(csv.DictReader(io.StringIO(cls.raw.decode("utf-8"))))
        cls.source_hash=hashlib.sha256(cls.raw).hexdigest()

    def safe(self, d):
        self.assertEqual(d["schema"], SCHEMA)
        self.assertEqual(d["work_id"], WORKID)
        self.assertIs(d["dispatch_allowed"], False)
        self.assertIs(d["external_effect"], False)
        self.assertEqual(d["authority"], "NONE")
        self.assertNotEqual(d["decision"], "EXECUTED")
        self.assertEqual(d["independent_receiver_ack"], "UNKNOWN")
        self.assertIs(d["source_promoted_to_runtime"], False)

    def test_general_selects_observed_root_not_accepted(self):
        d=pull(ROOT,"GENERAL_READ_ONLY");self.safe(d)
        self.assertEqual(d["selected_task"]["task_id"],"X01")
        self.assertEqual(d["decision"],"READ_ONLY_REVIEW_CANDIDATE")
        self.assertIs(d["selected_task"]["accepted"],False)
        self.assertEqual(d["source_sha256"],EXPECTED_SHA256)
        self.assertEqual(d["source_git_blob_sha1"],"6c5b6ee32e394051eb8795c64fd32ef5b0a384a9")
        self.assertEqual(d["all_sessions_ack"],"UNKNOWN")

    def test_x2_owner_rebind_is_required(self):
        d=pull(ROOT,"X2_DESKTOP_RECOVERY");self.safe(d)
        self.assertEqual(d["selected_task"]["task_id"],"X01")
        self.assertEqual(d["decision"],"HOLD")
        self.assertEqual(d["reason"],"HOLD_INCUMBENT_X2_OWNER_REFRESH_REQUIRED")
        self.assertIn("181",d["next_safe_probe"])
        self.assertIs(d["new_watcher_created"],False)
        self.assertIs(d["private_payload_accessed"],False)

    def test_existing_custody_lane_root(self):
        d=pull(ROOT,"WORKID_CUSTODY");self.safe(d)
        self.assertEqual(d["selected_task"]["task_id"],"W01")
        self.assertEqual(d["decision"],"READ_ONLY_REVIEW_CANDIDATE")
        self.assertEqual(d["selected_task"]["evidence_state"],"SOURCE_TESTED_ONLY")
        self.assertIs(d["selected_task"]["accepted"],False)

    def test_provider_exit_lane_root(self):
        d=pull(ROOT,"PROVIDER_EXIT");self.safe(d)
        self.assertEqual(d["selected_task"]["task_id"],"E01")
        self.assertEqual(d["decision"],"READ_ONLY_REVIEW_CANDIDATE")
        self.assertFalse(d["dispatch_allowed"])

    def test_voice_lane_blocked_on_unaccepted_predecessor(self):
        d=pull(ROOT,"VOICE_FIRST");self.safe(d)
        self.assertEqual(d["decision"],"HOLD")
        self.assertEqual(d["reason"],"HOLD_PREREQUISITE_ACCEPTANCE_UNPROVEN")
        self.assertGreater(len(d["selected_task"]["prerequisite_task_ids"]),0)

    def test_unknown_role_closed(self):
        d=pull(ROOT,"UNRECOGNIZED");self.safe(d)
        self.assertEqual(d["decision"],"HOLD")
        self.assertEqual(d["reason"],"HOLD_UNRECOGNIZED_ROLE")

    def test_no_forged_x2_rebind(self):
        fake={"state":"APPROVED","incident_owner":"https://github.com/CoCivium/CoCivium/issues/181",
              "x2_shell_started":False,"runtime_accepted":False}
        d=choose(self.records,"X2_DESKTOP_RECOVERY",x2_rebind=fake,
                 source_sha256=self.source_hash,source_blob="z")
        self.safe(d)
        self.assertEqual(d["reason"],"HOLD_X2_ROLE_REBIND_FAILED")

    def test_same_source_same_result(self):
        self.assertEqual(pull(ROOT,"GENERAL_READ_ONLY"),pull(ROOT,"GENERAL_READ_ONLY"))

    def test_source_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            dest=root / CSV_PATH.relative_to(ROOT)
            dest.parent.mkdir(parents=True)
            dest.write_bytes(self.raw.replace(b"X01,",b"X09,",1))
            d=pull(root,"GENERAL_READ_ONLY");self.safe(d)
            self.assertEqual(d["decision"],"HOLD")
            self.assertEqual(d["reason"],"HOLD_SOURCE_UNAVAILABLE_OR_MALFORMED")
            self.assertIsNone(d["selected_task"])

    def test_source_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            d=pull(Path(td),"GENERAL_READ_ONLY");self.safe(d)
            self.assertEqual(d["decision"],"HOLD")
            self.assertIsNone(d["selected_task"])

    def test_no_runtime_by_inmemory_source_state_claim(self):
        modified=copy.deepcopy(self.records)
        modified[0]["evidence_state"]="NATIVE_RUNTIME_VERIFIED"
        d=choose(modified,"GENERAL_READ_ONLY",x2_rebind=None,
                 source_sha256=self.source_hash,source_blob="fake")
        self.safe(d)
        self.assertEqual(d["decision"],"HOLD")
        self.assertEqual(d["reason"],"HOLD_SOURCE_STATE_UNQUALIFIED")

    def test_role_whitelist_is_bounded(self):
        self.assertEqual(len(ROLES),6)
        self.assertFalse(any("SECRET" in key for key in ROLES))

if __name__=="__main__":
    unittest.main(verbosity=2)
