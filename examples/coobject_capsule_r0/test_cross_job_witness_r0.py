#!/usr/bin/env python3
"""Adversarial stdlib tests for read-only CoObject witness. No network."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from cross_job_witness_r0 import SOURCE, SOURCE_SHA, sha, inspect, Hold, main

class TestWitness(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.producer = self.base / "producer"
        self.receiver = self.base / "receiver"
        (self.producer / "capsule").mkdir(parents=True)
        self.receiver.mkdir()
        self.manifest = {
            "schema": "CoCivium.CoObject.OfflineCapsule.R0",
            "object_id": "coobj-" + SOURCE_SHA[:20],
            "content_sha256": SOURCE_SHA,
            "content_bytes": len(SOURCE),
            "copies": ["payload.bin", "recovery.bin"],
            "authority": "DATA_ONLY_NO_EXECUTION",
            "privacy": "LOCAL_PRIVATE_BY_DEFAULT",
            "receiver_readproof": None,
            "source_authenticity": "SELF_PACKAGED_NOT_EXTERNALLY_SIGNED",
            "minimum_use": "Recover exact synthetic bytes after one local replica failure",
        }
        (self.producer / "capsule" / "payload.bin").write_bytes(SOURCE)
        (self.producer / "capsule" / "recovery.bin").write_bytes(SOURCE)
        self._write_manifest()
        self.handoff = {
            "schema": "CoCivium.CoObject.CrossJobSyntheticArtifact.R0",
            "object_id": self.manifest["object_id"],
            "source_sha256": SOURCE_SHA,
            "source_bytes": len(SOURCE),
            "manifest_sha256": sha(self.manifest_bytes),
            "authority": "DATA_ONLY_NO_EXECUTION",
            "content_class": "PUBLIC_SYNTHETIC_FIXED_LITERAL",
            "producer_claim": "CAPSULE_CREATED_ONE_CI_JOB",
            "receiver_ack": None,
            "independent_storage_verified": False,
        }
        self.receipt = {
            "schema": "CoCivium.CoObject.CrossJobSourceReadback.R0",
            "state": "CROSS_JOB_SYNTHETIC_RECONSTRUCTION_PASS",
            "work_id": "CoObject.CrossJobSyntheticTransfer.R0",
            "content_sha256": SOURCE_SHA,
            "producer_manifest_sha256": self.handoff["manifest_sha256"],
            "produced_two_copies": "READY_LOCAL_TWO_COPIES",
            "receiver_one_copy_degradation": "DEGRADED_LOCAL_ONE_COPY",
            "receiver_restored_bytes_match_literal": True,
            "source_authenticity_established": False,
            "third_party_independent_receiver_ack": False,
            "storage_fault_domain_independence_established": False,
            "x2_receiver_verified": False,
            "time_survival_24h_verified": False,
            "real_user_benefit_verified": False,
            "effect_authority": "NONE",
        }
        self._write_handoff()
        self._write_receipt()

    def _encoded(self, obj):
        return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()

    def _write_manifest(self):
        self.manifest_bytes = self._encoded(self.manifest)
        (self.producer / "capsule" / "manifest.json").write_bytes(self.manifest_bytes)

    def _write_handoff(self):
        (self.producer / "handoff.json").write_bytes(self._encoded(self.handoff))

    def _write_receipt(self):
        (self.receiver / "receipt.json").write_bytes(self._encoded(self.receipt))

    def _run(self):
        return inspect(self.producer, self.receiver)

    def _zip(self, root, filename):
        target = self.base / filename
        with zipfile.ZipFile(target, "w") as z:
            for p in root.rglob("*"):
                if p.is_file():
                    z.write(p, p.relative_to(root).as_posix())
        return target

    def test_valid_independent_consistency(self):
        result = self._run()
        self.assertEqual(result["state"], "THIRD_JOB_SOURCE_SCOPE_CONSISTENCY_PASS")
        self.assertTrue(result["witness_reconstructed_surviving_copy_exact"])
        self.assertFalse(result["receiver_restoration_independently_observed"])
        self.assertFalse(result["separate_organization_or_trust_root_verified"])

    def test_valid_zip_roundtrip(self):
        self.assertEqual(inspect(self._zip(self.producer, "p.zip"), self._zip(self.receiver, "r.zip")), self._run())

    def test_missing_copy(self):
        (self.producer / "capsule" / "payload.bin").unlink()
        with self.assertRaises(Hold): self._run()

    def test_corrupt_copy(self):
        (self.producer / "capsule" / "recovery.bin").write_bytes(b"tampered")
        with self.assertRaisesRegex(Hold, "PRODUCER_SOURCE_BYTES_WRONG"): self._run()

    def test_corrupt_source_digest(self):
        self.handoff["source_sha256"] = "0" * 64
        self._write_handoff()
        with self.assertRaisesRegex(Hold, "HANDOFF_SOURCE_ID"): self._run()

    def test_fake_receiver_ack(self):
        self.receipt["third_party_independent_receiver_ack"] = True
        self._write_receipt()
        with self.assertRaisesRegex(Hold, "FALSE_EVIDENCE_FIELD"): self._run()

    def test_fake_user_benefit(self):
        self.receipt["real_user_benefit_verified"] = True
        self._write_receipt()
        with self.assertRaisesRegex(Hold, "FALSE_EVIDENCE_FIELD"): self._run()

    def test_false_effect_authority(self):
        self.receipt["effect_authority"] = "PUBLISH"
        self._write_receipt()
        with self.assertRaisesRegex(Hold, "FALSE_AUTHORITY"): self._run()

    def test_receiver_proof_claim_mismatch(self):
        self.receipt["receiver_restored_bytes_match_literal"] = False
        self._write_receipt()
        with self.assertRaisesRegex(Hold, "RECEIVER_DID_NOT_REPORT_RESTORED_BYTES"): self._run()

    def test_manifest_tampered(self):
        self.manifest["privacy"] = "AUTO_PUBLIC"
        self._write_manifest()
        self.handoff["manifest_sha256"] = sha(self.manifest_bytes)
        self.receipt["producer_manifest_sha256"] = self.handoff["manifest_sha256"]
        self._write_handoff()
        self._write_receipt()
        with self.assertRaisesRegex(Hold, "MANIFEST_PRIVACY"): self._run()

    def test_receipt_digest_wrong(self):
        self.receipt["producer_manifest_sha256"] = "b" * 64
        self._write_receipt()
        with self.assertRaisesRegex(Hold, "RECEIPT_DIGEST_MISMATCH"): self._run()

    def test_symlink_file_held(self):
        (self.producer / "capsule" / "payload.bin").unlink()
        (self.producer / "capsule" / "payload.bin").symlink_to(self.producer / "capsule" / "recovery.bin")
        with self.assertRaisesRegex(Hold, "UNSAFE_INPUT_FILE"): self._run()

    def test_unexpected_file_held(self):
        (self.producer / "extra.txt").write_text("invalid")
        with self.assertRaisesRegex(Hold, "UNEXPECTED_INPUT_FILE"): self._run()

    def test_duplicate_json_key_held(self):
        (self.producer / "handoff.json").write_text('{"schema":"a","schema":"b"}')
        with self.assertRaisesRegex(Hold, "DUPLICATE_JSON_KEY"): self._run()

    def test_source_length_boolean_held(self):
        self.handoff["source_bytes"] = True
        self._write_handoff()
        with self.assertRaisesRegex(Hold, "HANDOFF_BYTES"): self._run()

    def test_zip_duplicate_member_held(self):
        p = self._zip(self.producer, "p.zip")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(p, "a") as z:
                z.writestr("capsule/manifest.json", b"spoof")
        with self.assertRaisesRegex(Hold, "UNEXPECTED_ARCHIVE_FILE_COUNT"): inspect(p, self.receiver)

    def test_zip_slip_held(self):
        p = self._zip(self.producer, "p.zip")
        with zipfile.ZipFile(p, "a") as z:
            z.writestr("../evil.txt", "x")
        with self.assertRaisesRegex(Hold, "UNEXPECTED_ARCHIVE_FILE_COUNT"): inspect(p, self.receiver)

    def test_receipt_no_overwrite(self):
        path = self.base / "result.json"
        path.write_text("existing")
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            code = main([str(self.producer), str(self.receiver), "--report", str(path)])
        self.assertEqual(code, 2)
        self.assertEqual(path.read_text(), "existing")

    def test_wrong_receiver_schema(self):
        self.receipt["schema"] = "WRONG"
        self._write_receipt()
        with self.assertRaisesRegex(Hold, "RECEIPT_SCHEMA"): self._run()

if __name__ == "__main__":
    unittest.main(verbosity=2)