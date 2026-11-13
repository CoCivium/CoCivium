"""Synthetic regressions; never contain or reach real conversation data."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import warnings
import zipfile

from ai_history_intake_r0 import run, Hold, DB, RECEIPT, KEY


def conversation(i):
    return {"id": "private-id-" + str(i), "title": "Never save title " + str(i),
            "create_time": 1234 + i, "update_time": 2345 + i,
            "mapping": {"a": {"message": {"content": {"parts": ["secret message { [ quote \\\" "]}}}}}


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "export.zip"

    def make(self, docs=None, entries=None):
        if docs is None:
            docs = [conversation(i) for i in range(3)]
        with zipfile.ZipFile(self.source, "w", zipfile.ZIP_DEFLATED) as f:
            if entries is None:
                f.writestr("folder/conversations.json", json.dumps(docs))
                f.writestr("misc/other.txt", "other secret")
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    for name, value in entries:
                        f.writestr(name, value)
        return self.source

    def test_inspect_has_no_extraction_or_secrets(self):
        self.make()
        s = run(self.source, self.root / "inspect")
        self.assertEqual(s["state"], "FORMAT_CANDIDATE")
        self.assertEqual(s["conversation_source_candidates"], 1)
        self.assertFalse((self.root / "inspect" / DB).exists())
        self.assertNotIn("private-id", (self.root / "inspect" / RECEIPT).read_text())
        self.assertNotIn("secret message", (self.root / "inspect" / RECEIPT).read_text())
        self.assertEqual(s["zip_sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_exact_census_and_private_db(self):
        self.make()
        s = run(self.source, self.root / "census", "census")
        self.assertEqual(s["distinct_conversation_ids_in_export"], 3)
        self.assertEqual(s["observed_records"], 3)
        self.assertFalse(s["delete_safe"])
        self.assertTrue((self.root / "census" / KEY).exists())
        data = (self.root / "census" / DB).read_bytes()
        self.assertNotIn(b"private-id-", data)
        self.assertNotIn(b"Never save title", data)
        with sqlite3.connect(self.root / "census" / DB) as conn:
            self.assertEqual(conn.execute("SELECT SUM(message_nodes) FROM conversations").fetchone()[0], 3)

    def test_duplicate_ids_hold(self):
        self.make([conversation(1), conversation(1)])
        x = run(self.source, self.root / "census", "census")
        self.assertEqual(x["duplicate_id_records"], 1)
        self.assertEqual(x["state"], "HOLD_INCOMPLETE_OR_AMBIGUOUS_CENSUS")

    def test_missing_ids_hold(self):
        doc = conversation(1)
        del doc["id"]
        self.make([doc])
        x = run(self.source, self.root / "census", "census")
        self.assertEqual(x["missing_id_records"], 1)
        self.assertEqual(x["state"], "HOLD_INCOMPLETE_OR_AMBIGUOUS_CENSUS")

    def test_traversal_rejected(self):
        self.make(entries=[("../secret/conversations.json", "[]")])
        with self.assertRaisesRegex(Hold, "HOLD_UNSAFE_PATH"):
            run(self.source, self.root / "o")

    def test_duplicate_member_rejected(self):
        self.make(entries=[("conversations.json", "[]"), ("conversations.json", "[]")])
        with self.assertRaisesRegex(Hold, "HOLD_DUPLICATE_MEMBER"):
            run(self.source, self.root / "o")

    def test_missing_source_explicitly_unsupported(self):
        self.make(entries=[("else.json", "[]")])
        x = run(self.source, self.root / "o")
        self.assertEqual(x["state"], "UNSUPPORTED_OR_AMBIGUOUS_FORMAT")
        self.assertNotIn("distinct_conversation_ids_in_export", x)

    def test_two_source_members_rejected_for_census(self):
        self.make(entries=[("a/conversations.json", "[]"), ("b/conversations.json", "[]")])
        with self.assertRaisesRegex(Hold, "HOLD_EXACTLY_ONE"):
            run(self.source, self.root / "o", "census")

    def test_existing_output_not_overwritten(self):
        self.make()
        dst = self.root / "o"
        dst.mkdir()
        with self.assertRaisesRegex(Hold, "HOLD_OUTPUT_ALREADY_EXISTS"):
            run(self.source, dst)

    def test_escaped_quotes_braces_nesting(self):
        self.make([conversation(1), conversation(2)])
        x = run(self.source, self.root / "census", "census")
        self.assertEqual(x["distinct_conversation_ids_in_export"], 2)

    def test_trailing_json_rejected(self):
        self.make(entries=[("conversations.json", '[{"id":"a"}] {"x":"y"}')])
        with self.assertRaisesRegex(Hold, "HOLD_TRAILING_DATA"):
            run(self.source, self.root / "o", "census")

    def test_json_top_level_object_not_silently_zero(self):
        self.make(entries=[("conversations.json", '{"conversations":[]}')])
        with self.assertRaisesRegex(Hold, "HOLD_TOP_LEVEL_NOT_ARRAY"):
            run(self.source, self.root / "o", "census")

    def test_invalid_json_not_silently_counted(self):
        self.make(entries=[("conversations.json", '[{"id": "a", }]')])
        with self.assertRaisesRegex(Hold, "HOLD_INVALID_RECORD_JSON"):
            run(self.source, self.root / "o", "census")

if __name__ == "__main__":
    unittest.main()
