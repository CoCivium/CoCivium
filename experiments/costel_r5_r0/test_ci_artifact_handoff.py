"""Adversarial, local tests for the two-job GitHub Actions handoff contract.

Fixtures imitate runner variables; actual separate-job pickup requires hosted CI.
"""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ci_artifact_handoff import (
    WORK_ID, PRODUCER_JOB, RECEIVER_JOB, SOURCE_SCHEMA,
    canonical, produce, receive, require_context,
)

SHA = "a" * 40


def context(job, *, run_id="171", attempt="1", sha=SHA):
    return {"GITHUB_ACTIONS": "true", "GITHUB_JOB": job,
            "GITHUB_RUN_ID": run_id, "GITHUB_RUN_ATTEMPT": attempt,
            "GITHUB_SHA": sha}


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.data = self.root / "producer_artifact"
        self.receipt = self.root / "receiver" / "pickup.json"

    def prepared(self):
        produce(self.data, context(PRODUCER_JOB))
        return self.data

    def test_valid_scoped_pickup(self):
        self.prepared()
        claimed = json.loads((self.data / "producer_claim.json").read_bytes())
        result = receive(self.data, self.receipt, context(RECEIVER_JOB))
        raw = (self.data / "source.json").read_bytes()
        self.assertEqual(result["state"], "HASH_MATCHED_ARTIFACT_PICKUP_CI_SCOPE")
        self.assertEqual(result["source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["source_sha256"], claimed["source_sha256"])
        self.assertEqual(result, json.loads(self.receipt.read_bytes()))
        self.assertEqual(result["work_id"], WORK_ID)
        self.assertEqual(result["receiver_job"], RECEIVER_JOB)
        self.assertEqual(result["useful_work_effect"], "NOT_TESTED")
        self.assertEqual(result["cross_provider_recovery"], "NOT_TESTED")
        self.assertEqual(result["x2_native_receiver"], "NOT_TESTED")
        self.assertIs(result["global_session_ack"], False)

    def test_distinct_job_identity_is_required(self):
        self.prepared()
        with self.assertRaisesRegex(ValueError, "HOLD_WRONG_JOB_IDENTITY"):
            receive(self.data, self.receipt, context(PRODUCER_JOB))

    def test_producer_must_be_producer(self):
        with self.assertRaisesRegex(ValueError, "HOLD_WRONG_JOB_IDENTITY"):
            produce(self.data, context(RECEIVER_JOB))

    def test_missing_job_context(self):
        with self.assertRaisesRegex(ValueError, "HOLD_MISSING_GITHUB_CONTEXT"):
            require_context({}, PRODUCER_JOB)

    def test_explicit_actions_environment(self):
        env = context(PRODUCER_JOB)
        env["GITHUB_ACTIONS"] = "false"
        with self.assertRaisesRegex(ValueError, "HOLD_WRONG_JOB_IDENTITY"):
            produce(self.data, env)

    def test_invalid_run_identity(self):
        with self.assertRaisesRegex(ValueError, "HOLD_INVALID_RUN_ID"):
            produce(self.data, context(PRODUCER_JOB, run_id="some-run"))

    def test_invalid_attempt_identity(self):
        with self.assertRaisesRegex(ValueError, "HOLD_INVALID_ATTEMPT"):
            produce(self.data, context(PRODUCER_JOB, attempt="0"))

    def test_invalid_source_sha(self):
        with self.assertRaisesRegex(ValueError, "HOLD_INVALID_SOURCE_REVISION"):
            produce(self.data, context(PRODUCER_JOB, sha="not-a-git-sha"))

    def test_no_clobber_producer(self):
        self.prepared()
        original = (self.data / "source.json").read_bytes()
        with self.assertRaises(FileExistsError):
            produce(self.data, context(PRODUCER_JOB))
        self.assertEqual((self.data / "source.json").read_bytes(), original)

    def test_no_clobber_receiver(self):
        self.prepared()
        receive(self.data, self.receipt, context(RECEIVER_JOB))
        raw = self.receipt.read_bytes()
        with self.assertRaises(FileExistsError):
            receive(self.data, self.receipt, context(RECEIVER_JOB))
        self.assertEqual(self.receipt.read_bytes(), raw)

    def test_mismatched_run_id_rejected(self):
        self.prepared()
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_BINDING_MISMATCH"):
            receive(self.data, self.receipt, context(RECEIVER_JOB, run_id="172"))

    def test_mismatched_run_attempt_rejected(self):
        self.prepared()
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_BINDING_MISMATCH"):
            receive(self.data, self.receipt, context(RECEIVER_JOB, attempt="2"))

    def test_mismatched_commit_rejected(self):
        self.prepared()
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_BINDING_MISMATCH"):
            receive(self.data, self.receipt, context(RECEIVER_JOB, sha="b"*40))

    def test_modified_source_rejected(self):
        self.prepared()
        obj = json.loads((self.data / "source.json").read_bytes())
        self.assertEqual(obj["schema"], SOURCE_SCHEMA)
        obj["message"] = "untrusted substitute"
        (self.data / "source.json").write_bytes(canonical(obj))
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_BINDING_MISMATCH"):
            receive(self.data, self.receipt, context(RECEIVER_JOB))

    def test_changed_source_and_forged_claim_still_rejected(self):
        self.prepared()
        obj = json.loads((self.data / "source.json").read_bytes())
        obj["message"] = "tampered by producer"
        raw = canonical(obj)
        (self.data / "source.json").write_bytes(raw)
        claim = json.loads((self.data / "producer_claim.json").read_bytes())
        claim["source_sha256"] = hashlib.sha256(raw).hexdigest()
        claim["source_bytes"] = len(raw)
        (self.data / "producer_claim.json").write_bytes(canonical(claim))
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_BINDING_MISMATCH"):
            receive(self.data, self.receipt, context(RECEIVER_JOB))

    def test_corrupt_producer_hash_rejected(self):
        self.prepared()
        claim = json.loads((self.data / "producer_claim.json").read_bytes())
        claim["source_sha256"] = "0"*64
        (self.data / "producer_claim.json").write_bytes(canonical(claim))
        with self.assertRaisesRegex(ValueError, "HOLD_PRODUCER_CLAIM_MISMATCH"):
            receive(self.data, self.receipt, context(RECEIVER_JOB))

    def test_corrupt_producer_size_rejected(self):
        self.prepared()
        claim = json.loads((self.data / "producer_claim.json").read_bytes())
        claim["source_bytes"] = 0
        (self.data / "producer_claim.json").write_bytes(canonical(claim))
        with self.assertRaisesRegex(ValueError, "HOLD_PRODUCER_CLAIM_MISMATCH"):
            receive(self.data, self.receipt, context(RECEIVER_JOB))

    def test_noncanonical_source_rejected(self):
        self.prepared()
        source = json.loads((self.data / "source.json").read_bytes())
        (self.data / "source.json").write_text(json.dumps(source, indent=2))
        with self.assertRaisesRegex(ValueError, "HOLD_NONCANONICAL_OBJECT"):
            receive(self.data, self.receipt, context(RECEIVER_JOB))

    def test_noncanonical_claim_rejected(self):
        self.prepared()
        claim = json.loads((self.data / "producer_claim.json").read_bytes())
        (self.data / "producer_claim.json").write_text(json.dumps(claim, indent=2))
        with self.assertRaisesRegex(ValueError, "HOLD_NONCANONICAL_OBJECT"):
            receive(self.data, self.receipt, context(RECEIVER_JOB))

    def test_claimed_cross_provider_not_a_fact(self):
        self.prepared()
        result = receive(self.data, self.receipt, context(RECEIVER_JOB))
        self.assertEqual(result["provider_failure_domain"], "SAME_GITHUB_ACTIONS_PROVIDER")
        self.assertNotIn("INDEPENDENT_COLD_RECOVERY", str(result))

    def test_no_extra_action_words_in_payload(self):
        self.prepared()
        payload = json.loads((self.data / "source.json").read_bytes())
        self.assertEqual(set(payload), {"schema","work_id","source_commit","ci_run_id",
                                        "ci_attempt","producer_job","message"})
        self.assertNotIn("authorization", payload)
        self.assertNotIn("execute", payload)


if __name__ == "__main__":
    unittest.main()
