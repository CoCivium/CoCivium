"""Public pointer exact-file readback and duplicate-intent identity tests.

No network, authorization, receiver or live queue implied by these tests.
"""
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
POINTER = json.loads((ROOT / "public_seed_pointer_r0.json").read_text(encoding="utf-8"))


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def observation_key(work_id, source_revision, intent_kind, normalized_payload):
    """Stable idempotency key; observations of one intent share one work identity."""
    if not all((work_id, source_revision, intent_kind, normalized_payload)):
        raise ValueError("incomplete source-bound intent")
    body = json.dumps([work_id, source_revision, intent_kind, normalized_payload],
                      separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def dedupe(observations):
    """Return one elected intent with retained observation counts; no tasks executed."""
    ledger = {}
    for observation in observations:
        key = observation_key(*observation)
        if key not in ledger:
            ledger[key] = {"intent": observation, "observations": 0}
        ledger[key]["observations"] += 1
    return ledger


class PublicSeedPointerTests(unittest.TestCase):
    def test_pointer_is_one_public_read_only_work_identity(self):
        self.assertEqual(POINTER["schema"], "CoAll.PublicSeedPointer.R0")
        self.assertTrue(POINTER["work_id"])
        self.assertEqual(POINTER["authority"], "PUBLIC_READ_ONLY_SOURCE_DISCOVERY")

    def test_each_source_exact_git_blob_matches(self):
        for source in POINTER["surfaces"]:
            with self.subTest(source=source["id"]):
                path = ROOT.parent.parent / source["path"]
                self.assertEqual(git_blob_sha1(path.read_bytes()), source["git_blob_sha1"])

    def test_pointer_cannot_claim_external_ack(self):
        self.assertEqual(POINTER["receiver_acceptance"], "NOT_PROVEN")
        self.assertEqual(POINTER["operational_sync"], "NOT_PROVEN")
        self.assertEqual(POINTER["durable_host_survival_24h"], "NOT_PROVEN")
        self.assertEqual(POINTER["coex_canon_runtime"], "NOT_PROVEN")

    def test_source_is_draft_candidate_not_release(self):
        self.assertEqual(POINTER["source"]["state"], "DRAFT_CANDIDATE_NOT_MAIN")

    def test_repeat_prompt_increments_observation_not_work(self):
        event = ("work1", "rev1", "CoPre", "agreed all")
        result = dedupe([event, event, event])
        self.assertEqual(len(result), 1)
        self.assertEqual(next(iter(result.values()))["observations"], 3)

    def test_distinct_revision_is_not_silently_deduped(self):
        a = ("work1", "rev1", "CoPre", "same")
        b = ("work1", "rev2", "CoPre", "same")
        self.assertEqual(len(dedupe((a, b))), 2)

    def test_distinct_intent_not_deduped_merely_by_text(self):
        a = ("work1", "rev1", "MAIL_REVIEW", "same")
        b = ("work1", "rev1", "PUBLISH_REQUEST", "same")
        self.assertEqual(len(dedupe((a, b))), 2)

    def test_empty_source_provenance_is_rejected(self):
        with self.assertRaises(ValueError):
            observation_key("w", "", "CoPre", "message")

    def test_no_private_mailbox_or_personal_recipient_in_public_pointer(self):
        raw = json.dumps(POINTER).lower()
        for secret in ("gmail.com", "inseed.com", "password", "private:pointer",
                       "ndizeyeelix", "rick ballard"):
            self.assertNotIn(secret, raw)

    def test_no_execution_claims_in_dedupe(self):
        record = next(iter(dedupe([("w", "r", "INTENT", "x")]).values()))
        self.assertNotIn("sent", record)
        self.assertNotIn("acknowledged", record)


if __name__ == "__main__":
    unittest.main()
