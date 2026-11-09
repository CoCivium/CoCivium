"""Public chronology sample tests: historical source pointers, not invented archive."""
import json
from datetime import datetime
from pathlib import Path
import unittest

DATA = json.loads((Path(__file__).resolve().parent /
                   "public_front_chronology_sample_r0.json").read_text())


class PublicFrontChronologyTests(unittest.TestCase):
    def test_six_observed_distinct_issue_ids(self):
        rows = DATA["records"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({r["issue"] for r in rows}), 6)

    def test_order_is_actual_creation_time_not_update_time(self):
        created = [datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
                   for r in DATA["records"]]
        self.assertEqual(created, sorted(created))

    def test_source_urls_correspond_to_issue_id(self):
        for r in DATA["records"]:
            self.assertEqual(r["source_url"],
                             "https://github.com/CoCivium/CoCivium/issues/" + str(r["issue"]))

    def test_mutable_issues_not_fake_hashed(self):
        self.assertTrue(all(r["content_sha256"] is None for r in DATA["records"]))
        self.assertIn("ISSUE_METADATA_IS_NOT_IMMUTABLE_BYTES", DATA["nonclaims"])

    def test_created_time_does_not_claim_idea_origin(self):
        self.assertIn("ISSUE_CREATED_TIME_NOT_ORIGIN_OF_IDEA", DATA["nonclaims"])

    def test_partial_semantic_inspection_not_complete_ingestion(self):
        self.assertTrue(all(r["semantic_review"] == "PARTIAL_ISSUE_EXCERPT"
                            for r in DATA["records"]))
        self.assertIn("POINTER_IS_NOT_SEMANTIC_INGESTION", DATA["nonclaims"])

    def test_coverage_says_what_was_not_inspected(self):
        self.assertFalse(DATA["coverage"]["complete_history"])
        for unscanned in ("CoFarm", "NAS", "historic chats", "Meta AI sessions"):
            self.assertIn(unscanned, DATA["coverage"]["not_scanned"])

    def test_source_pointer_is_not_receiver_ack(self):
        self.assertIn("PUBLIC_SOURCE_IS_NOT_RECEIVER_PICKUP", DATA["nonclaims"])


if __name__ == "__main__":
    unittest.main()
