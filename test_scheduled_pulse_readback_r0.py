"""Negative controls for a real-job-bounded CoGoAll pulse readback.

These are synthetic fixtures. GitHub CI must separately prove an actual
producer artifact was consumed by a distinct job.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "examples" / "cotalkitout"))
from scheduled_pulse_readback_r0 import (
    EXPECTED_CLAIMS, EXPECTED_LOGS, SOURCE_SCHEMA, observe, write_receipt
)

SHA = "a" * 40


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def context(**overrides):
    value = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_JOB": "pulse-receiver",
        "GITHUB_RUN_ID": "12345",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": SHA,
        "GITHUB_EVENT_NAME": "schedule",
    }
    value.update(overrides)
    return value


class PulseReadbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "download"
        self.source.mkdir()
        self.dest = self.root / "receiver" / "readback.json"
        hashes = {}
        for name in EXPECTED_LOGS:
            raw = ("CI synthetic " + name + "\n").encode()
            (self.source / (name + ".log")).write_bytes(raw)
            hashes[name] = digest(raw)
        audit = b'{"scope":"synthetic-schedule-audit"}\n'
        (self.source / "schedule-audit.json").write_bytes(audit)
        rebound = json.dumps({"schema": "CoAll.ReboundIntegrity.R0",
                              "state": "SOURCE_LINKS_VALIDATED_ONLY",
                              "missing_local_targets": [], "violations": []}).encode() + b"\n"
        (self.source / "rebound-report.json").write_bytes(rebound)
        self.record = {
            "schema": SOURCE_SCHEMA,
            "observed_at_utc": "2026-11-09T03:22:17+00:00",
            "run_id": "12345", "attempt": "1",
            "head": SHA, "event": "schedule", "outcome": "success",
            "log_sha256": hashes,
            "schedule_audit_sha256": digest(audit),
            "rebound_audit_sha256": digest(rebound),
            "claims": EXPECTED_CLAIMS[:],
        }
        self.save()

    def save(self):
        (self.source / "proof-receipt.json").write_text(
            json.dumps(self.record, sort_keys=True, indent=2) + "\n",
            encoding="utf-8"
        )

    def test_valid_readback_is_scoped_and_not_external_ack(self):
        result = observe(self.source, context())
        self.assertEqual(result["verified_log_count"], 9)
        self.assertEqual(result["state"], "GITHUB_JOB_BOUNDARY_ARTIFACT_HASH_READBACK")
        self.assertEqual(result["work_id"], "CoGoAll.PulseReceipt.12345.a1")
        self.assertEqual(result["due_work_selection"], "NOT_TESTED")
        self.assertEqual(result["real_worker_effect"], "NOT_TESTED")
        self.assertIs(result["external_receiver_ack"], False)
        self.assertEqual(result["provider_failure_domain"], "SAME_GITHUB_ACTIONS")
        self.assertEqual(result["rebound_audit_sha256"], self.record["rebound_audit_sha256"])
        self.assertEqual(result["source_receipt_sha256"], digest(
            (self.source / "proof-receipt.json").read_bytes()))

    def test_actual_subprocess_cli_uses_os_environ(self):
        cmd = [sys.executable, "-B",
               str(ROOT / "examples" / "cotalkitout" / "scheduled_pulse_readback_r0.py"),
               "--source-dir", str(self.source), "--receipt", str(self.dest)]
        proc = subprocess.run(
            cmd, env={**os.environ, **context()}, text=True,
            capture_output=True, timeout=10
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        claimed = json.loads(proc.stdout)
        self.assertEqual(claimed, json.loads(self.dest.read_text()))
        self.assertEqual(claimed["run_id"], "12345")

    def test_changed_log_fails_closed(self):
        (self.source / "decision.log").write_text("attacker rewrote")
        with self.assertRaisesRegex(ValueError, "HOLD_LOG_DIGEST_MISMATCH"):
            observe(self.source, context())

    def test_missing_log_fails_closed(self):
        (self.source / "decision.log").unlink()
        with self.assertRaisesRegex(ValueError, "HOLD_MISSING_OR_LINKED_ARTIFACT"):
            observe(self.source, context())

    def test_missing_log_hash_fails_closed(self):
        del self.record["log_sha256"]["decision"]
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_MISSING_LOG_IDENTITIES"):
            observe(self.source, context())

    def test_changed_schedule_audit_fails_closed(self):
        (self.source / "schedule-audit.json").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "HOLD_CADENCE_DIGEST_MISMATCH"):
            observe(self.source, context())

    def test_false_receiver_ack_field_fails_closed(self):
        self.record["external_receiver_ack"] = True
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_UNEXPECTED_PROOF_FIELDS"):
            observe(self.source, context())

    def test_modified_nonclaims_fails_closed(self):
        self.record["claims"].append("VERIFIED_EXTERNAL_ACK")
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_AUTHORITY_OR_ACK_INFLATION"):
            observe(self.source, context())

    def test_wrong_sha_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_WRONG_RUN_OR_SOURCE"):
            observe(self.source, context(GITHUB_SHA="b"*40))

    def test_wrong_run_attempt_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_WRONG_RUN_OR_SOURCE"):
            observe(self.source, context(GITHUB_RUN_ATTEMPT="2"))

    def test_wrong_job_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_NOT_RECEIVER_JOB"):
            observe(self.source, context(GITHUB_JOB="proof"))

    def test_wrong_event_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_WRONG_RUN_OR_SOURCE"):
            observe(self.source, context(GITHUB_EVENT_NAME="push"))

    def test_unqualified_event_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_EVENT_NOT_QUALIFIED"):
            observe(self.source, context(GITHUB_EVENT_NAME="pull_request"))

    def test_missing_environment_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_GITHUB_CONTEXT_MISSING"):
            observe(self.source, {})

    def test_source_tests_not_passed_fails_closed(self):
        self.record["outcome"] = "failure"
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_TESTS_NOT_PASSED"):
            observe(self.source, context())

    def test_non_utc_timestamp_fails_closed(self):
        self.record["observed_at_utc"] = "2026-11-09T03:22:17-05:00"
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_NOT_UTC"):
            observe(self.source, context())

    def test_symlink_log_fails_closed(self):
        alternate = self.root / "secret"
        alternate.write_text("secret")
        link = self.source / "decision.log"
        link.unlink()
        try:
            link.symlink_to(alternate)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        with self.assertRaisesRegex(ValueError, "HOLD_MISSING_OR_LINKED_ARTIFACT"):
            observe(self.source, context())

    def test_no_clobber_existing_receiver(self):
        readback = observe(self.source, context())
        write_receipt(readback, self.dest)
        before = self.dest.read_bytes()
        with self.assertRaises(FileExistsError):
            write_receipt(readback, self.dest)
        self.assertEqual(before, self.dest.read_bytes())


    def test_missing_rebound_audit_is_held(self):
        (self.source / "rebound-report.json").unlink()
        with self.assertRaisesRegex(ValueError, "HOLD_MISSING_OR_LINKED_ARTIFACT"):
            observe(self.source, context())

    def test_altered_rebound_report_is_held(self):
        (self.source / "rebound-report.json").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "HOLD_REBOUND_DIGEST_MISMATCH"):
            observe(self.source, context())

    def test_invalid_rebound_state_is_held_even_with_matching_digest(self):
        raw = json.dumps({"schema": "CoAll.ReboundIntegrity.R0",
                          "state": "SOURCE_CONTINUITY_HOLD",
                          "missing_local_targets": ["lost"], "violations": []}).encode()
        (self.source / "rebound-report.json").write_bytes(raw)
        self.record["rebound_audit_sha256"] = digest(raw)
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_REBOUND_REPORT_NOT_VALID"):
            observe(self.source, context())

    def test_legacy_schema_holds_in_new_receiver(self):
        self.record["schema"] = "cogoall-proof-pulse-r0"
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_PROOF_SCHEMA"):
            observe(self.source, context())

    def test_missing_rebound_hash_field_fails_closed(self):
        del self.record["rebound_audit_sha256"]
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_UNEXPECTED_PROOF_FIELDS"):
            observe(self.source, context())

    def test_new_rebound_log_hash_missing_fails_closed(self):
        del self.record["log_sha256"]["rebound-links"]
        self.save()
        with self.assertRaisesRegex(ValueError, "HOLD_MISSING_LOG_IDENTITIES"):
            observe(self.source, context())

if __name__ == "__main__":
    unittest.main(verbosity=2)
