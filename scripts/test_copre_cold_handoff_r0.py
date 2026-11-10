"""CoPre public handoff negative controls. Never touches a network or a real receiver."""
from __future__ import annotations
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import copre_cold_handoff_r0 as m

REPO = Path(__file__).resolve().parents[1]
COMMIT = "a" * 40

class ColdHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = self.root / "packet"
        self.manifest = m.emit(REPO, self.payload, COMMIT)
        self.files = {path: (REPO / path).read_bytes() for path in m.FILES}
    def readback(self, commit, path):
        self.assertEqual(commit, COMMIT)
        self.assertIn(path, m.FILES)
        return self.files[path]
    def update_manifest(self, field, val):
        file = self.payload / "packet.json"
        obj = json.loads(file.read_text())
        obj[field] = val
        file.write_text(json.dumps(obj), encoding="utf-8")
    def test_emitted_packet_has_public_scope_only(self):
        self.assertEqual(self.manifest["scope"], "PUBLIC_SOURCE_ONLY")
        self.assertFalse(self.manifest["independent_receiver_ack"])
        self.assertFalse(self.manifest["co_stead_pickup"])
        self.assertFalse(self.manifest["cross_session_sync"])
        self.assertEqual(self.manifest["effect_count"], 0)
    def test_exact_work_id_is_stable_across_runs(self):
        other = m.emit(REPO, self.root / "other", COMMIT)
        self.assertEqual(other["work_id"], self.manifest["work_id"])
    def test_no_clobber_packet(self):
        with self.assertRaisesRegex(m.Held, "HELD_PACKET_PATH_EXISTS_NO_CLOBBER"):
            m.emit(REPO, self.payload, COMMIT)
    def test_packet_can_cold_readback_public_sources(self):
        receipt = m.accept(self.payload, self.readback, reader_id="actions:101:reader")
        self.assertEqual(receipt["state"], "CI_SEPARATE_JOB_COLD_SOURCE_READBACK_ONLY")
        self.assertEqual(receipt["work_id"], self.manifest["work_id"])
        self.assertEqual(receipt["navigation"], ["copre-entry", "copre-package"])
        self.assertFalse(receipt["independent_external_receiver_ack"])
        self.assertFalse(receipt["survived_24h"])
    def test_separate_directory_cold_reload_without_original_source(self):
        other_root = self.root / "new-worker"
        shutil.copytree(self.payload, other_root)
        r = m.accept(other_root, self.readback, reader_id="actions:101:new-worker")
        self.assertEqual(r["source_commit"], COMMIT)
    def test_digest_tamper_is_held(self):
        file = self.payload / "payload" / "CoPre.md"
        file.write_bytes(file.read_bytes() + b"\nHIDDEN TAMPER\n")
        with self.assertRaisesRegex(m.Held, "HELD_PAYLOAD_DIGEST_MISMATCH"):
            m.accept(self.payload, self.readback, reader_id="actions:1:reader")
    def test_manifest_sha_tamper_is_held(self):
        obj = copy.deepcopy(self.manifest)
        obj["files"][0]["sha256"] = "0" * 64
        (self.payload / "packet.json").write_text(json.dumps(obj))
        with self.assertRaisesRegex(m.Held, "HELD_PAYLOAD_DIGEST_MISMATCH"):
            m.validate(self.payload)
    def test_work_id_tamper_is_held(self):
        self.update_manifest("work_id", "copre:cold:forged")
        with self.assertRaisesRegex(m.Held, "HELD_WORK_ID_MISMATCH"):
            m.validate(self.payload)
    def test_missing_payload_is_held(self):
        (self.payload / "payload" / "CoPre.md").unlink()
        with self.assertRaisesRegex(m.Held, "HELD_MISSING_OR_LINKED_SOURCE"):
            m.validate(self.payload)
    def test_non_allowlisted_extra_path_is_held(self):
        obj = copy.deepcopy(self.manifest)
        obj["files"][0]["path"] = "secret.env"
        (self.payload / "packet.json").write_text(json.dumps(obj))
        with self.assertRaisesRegex(m.Held, "HELD_FILE_ALLOWLIST_OR_ORDER"):
            m.validate(self.payload)
    def test_wrong_commit_is_held(self):
        with self.assertRaisesRegex(m.Held, "HELD_INVALID_SOURCE_COMMIT"):
            m.emit(REPO, self.root/"wrong", "main")
    def test_receiver_ack_spoof_is_held(self):
        self.update_manifest("independent_receiver_ack", True)
        with self.assertRaisesRegex(m.Held, "HELD_CUSTODY_OR_AUTHORITY_ESCALATION"):
            m.validate(self.payload)
    def test_co_stead_spoof_is_held(self):
        self.update_manifest("co_stead_pickup", True)
        with self.assertRaisesRegex(m.Held, "HELD_CUSTODY_OR_AUTHORITY_ESCALATION"):
            m.validate(self.payload)
    def test_cross_session_spoof_is_held(self):
        self.update_manifest("cross_session_sync", True)
        with self.assertRaisesRegex(m.Held, "HELD_CUSTODY_OR_AUTHORITY_ESCALATION"):
            m.validate(self.payload)
    def test_receipt_never_claims_external_receiver(self):
        r = m.accept(self.payload, self.readback, reader_id="actions:1:reader")
        self.assertEqual(r["effect_count"], 0)
        self.assertEqual(r["failure_domain"], "GITHUB_ACTIONS_SHARED_PROVIDER")
        self.assertTrue(r["distinct_job_filesystem"])
        self.assertFalse(r["co_stead_pickup"])
        self.assertFalse(r["cross_session_sync"])
    def test_reader_id_must_be_bounded_and_stated(self):
        with self.assertRaisesRegex(m.Held, "HELD_UNQUALIFIED_READER"):
            m.accept(self.payload, self.readback, reader_id="../bad")
    def test_refetch_mismatch_fails_even_with_valid_packet(self):
        def bad(commit,path):
            return b"false mirror content"
        with self.assertRaisesRegex(m.Held, "HELD_COLD_REFETCH_MISMATCH"):
            m.accept(self.payload, bad, reader_id="actions:1:reader")
    def test_refetch_absent_fails_closed(self):
        with self.assertRaisesRegex(m.Held, "HELD_NO_INDEPENDENT_REFETCH"):
            m.accept(self.payload, None, reader_id="actions:1:reader")
    def test_duplicate_readback_no_double_effect(self):
        a = m.accept(self.payload, self.readback, reader_id="actions:1:reader")
        b = m.accept(self.payload, self.readback, reader_id="actions:1:reader")
        self.assertEqual(a["work_id"], b["work_id"])
        self.assertEqual((a["effect_count"], b["effect_count"]), (0,0))
    def test_payload_symlink_rejected(self):
        file = self.payload / "payload" / "CoPre.md"
        relocated = self.root / "relocated"
        file.rename(relocated)
        file.symlink_to(relocated)
        with self.assertRaisesRegex(m.Held, "HELD_MISSING_OR_LINKED_SOURCE"):
            m.validate(self.payload)
    def test_redirected_source_invalid(self):
        with self.assertRaisesRegex(m.Held, "HELD_NONALLOWLIST_SOURCE"):
            m.read_public_at_commit(COMMIT, "private/message.txt")
    def test_graph_invariant_detects_dangling_pointer(self):
        obj=json.loads(self.files[m.FILES[1]])
        obj["nodes"][0]["relations"].append("orphan-private-node")
        graph_bytes=json.dumps(obj).encode()
        file=self.payload/"payload"/m.FILES[1]
        file.write_bytes(graph_bytes)
        manifest=json.loads((self.payload/"packet.json").read_text())
        manifest["files"][1]["sha256"]=m.sha(graph_bytes)
        manifest["files"][1]["byte_count"]=len(graph_bytes)
        manifest["work_id"]=m.content_identity(COMMIT,manifest["files"])
        (self.payload/"packet.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "DANGLING_GRAPH_LINK"):
            m.validate(self.payload)
    def test_empty_response_cannot_pass_readback(self):
        with self.assertRaisesRegex(m.Held, "HELD_COLD_REFETCH_MISMATCH"):
            m.accept(self.payload,lambda *_:b"",reader_id="actions:1:reader")
    def test_historical_hash_not_24h(self):
        r=m.accept(self.payload,self.readback,reader_id="actions:1:reader")
        self.assertFalse(r["survived_24h"])
        self.assertIn("SOURCE_RECOVERY_NE_RUNTIME_SURVIVAL_24H",r["nonclaims"])

if __name__=="__main__":
    unittest.main()
