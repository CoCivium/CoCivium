"""Fail-closed regression tests for the Evergreen benchmark ledger status dialect."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "CoBenchmarkEvoCheckR0.py"
spec = importlib.util.spec_from_file_location("cobenchmark_evo_check", MODULE_PATH)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def record(status="PASS", **changes):
    row = {
        "observed_at": "2026-10-25",
        "id": "fixture:original:one",
        "status": status,
        "artifact": "isolated synthetic fixture",
        "test": "synthetic_descriptor",
        "result": "No real receiver or runtime effects",
        "evidence_ref": "fixture:hash:123",
        "nonclaims": ["FIXTURE_NE_PRODUCT_PROOF"],
    }
    if status == "HELD":
        row["hold_reason"] = "no receiver available"
    row.update(changes)
    return row


class EvergreenTypedStatusTests(unittest.TestCase):
    def check_rows(self, rows):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "benchmark.jsonl"
            path.write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n",
                encoding="utf-8",
            )
            return checker.validate(path)

    def must_reject(self, rows, phrase):
        with self.assertRaisesRegex(ValueError, phrase):
            self.check_rows(rows)

    def test_plain_pass(self):
        self.assertEqual(self.check_rows([record()])["counts"]["PASS"], 1)

    def test_plain_fail_kept(self):
        self.assertEqual(self.check_rows([record("FAIL")])["counts"]["FAIL"], 1)

    def test_scoped_fail_stays_negative(self):
        x = self.check_rows([record("FAIL_SCOPED")])
        self.assertEqual(x["counts"]["FAIL_SCOPED"], 1)
        self.assertEqual(x["counts"]["PASS"], 0)

    def test_held_with_explicit_reason(self):
        self.assertEqual(self.check_rows([record("HELD")])["counts"]["HELD"], 1)

    def test_publication_only_full_cannot_be_plain_pass(self):
        x = self.check_rows([record("PASS_PUBLICATION_ONLY")])
        self.assertEqual(x["counts"]["PASS_PUBLICATION_ONLY"], 1)
        self.assertEqual(x["counts"]["PASS"], 0)

    def test_compact_publication_with_all_held_gates(self):
        compact = {
            "id": "fixture:public:one",
            "date": "2026-10-25",
            "status": "PASS_PUBLICATION_ONLY",
            "evidence_ref": "fixture:github-comment",
            "scope": "publication only; no device receiver",
            "gates": {"native_device": "NOT_RUN_HELD", "remote_user": "NOT_RUN_HELD"},
            "nonclaims": ["PUBLICATION_NE_ADOPTION"],
        }
        self.assertEqual(self.check_rows([compact])["counts"]["PASS_PUBLICATION_ONLY"], 1)

    def test_compact_publication_rejects_fake_pass_gate(self):
        self.must_reject([{
            "id": "fixture:public:one",
            "date": "2026-10-25",
            "status": "PASS_PUBLICATION_ONLY",
            "evidence_ref": "fixture:github-comment",
            "scope": "publication only",
            "gates": {"native_device": "PASS"},
            "nonclaims": ["PUBLICATION_NE_ADOPTION"],
        }], "cannot promote gate")

    def test_compact_publication_requires_scope(self):
        self.must_reject([{
            "id": "fixture:public:one",
            "date": "2026-10-25",
            "status": "PASS_PUBLICATION_ONLY",
            "evidence_ref": "fixture:github-comment",
            "gates": {"native_device": "NOT_RUN_HELD"},
            "nonclaims": ["PUBLICATION_NE_ADOPTION"],
        }], "scope must be nonblank")

    def test_compact_publication_requires_nonempty_gates(self):
        self.must_reject([{
            "id": "fixture:public:one",
            "date": "2026-10-25",
            "status": "PASS_PUBLICATION_ONLY",
            "evidence_ref": "fixture:github-comment",
            "scope": "publication only",
            "gates": {},
            "nonclaims": ["PUBLICATION_NE_ADOPTION"],
        }], "needs explicit gates")

    def test_compact_publication_invalid_date(self):
        self.must_reject([{
            "id": "fixture:public:one",
            "date": "2026-14-71",
            "status": "PASS_PUBLICATION_ONLY",
            "evidence_ref": "fixture:github-comment",
            "scope": "publication only",
            "gates": {"device": "NOT_RUN_HELD"},
            "nonclaims": ["PUBLICATION_NE_ADOPTION"],
        }], "invalid compact date")

    def test_unknown_status_does_not_sneak_in(self):
        self.must_reject([record("MAGIC_FOREVER")], "unsupported status")

    def test_missing_evidence_rejected(self):
        self.must_reject([record("FAIL_SCOPED", evidence_ref="")], "evidence_ref must be nonblank")

    def test_missing_nonclaims_rejected(self):
        self.must_reject([record(nonclaims=[])], "nonclaims must be nonempty")

    def test_bad_nonclaim_rejected(self):
        self.must_reject([record(nonclaims=[""])], "nonclaim must be nonblank")

    def test_duplicate_id_rejected(self):
        self.must_reject([record(), record()], "duplicate id")

    def test_general_status_requires_observed_at(self):
        row = record()
        row.pop("observed_at")
        row["date"] = "2026-10-25"
        self.must_reject([row], "observed_at must be nonblank")

    def test_unknown_missing_held_reason_rejected(self):
        row = record("HELD")
        row.pop("hold_reason")
        self.must_reject([row], "HELD requires hold_reason")

    def test_exact_legacy_inline_held_reason_accepted_only_with_evidence(self):
        legacy_id = next(iter(checker.LEGACY_INLINE_HELD))
        row = record("HELD", id=legacy_id)
        row.pop("hold_reason")
        x = self.check_rows([row])
        self.assertEqual(x["legacy_inline_hold_reasons"], [legacy_id])
        self.assertEqual(x["counts"]["HELD"], 1)

    def test_legacy_held_without_evidence_still_rejected(self):
        legacy_id = next(iter(checker.LEGACY_INLINE_HELD))
        row = record("HELD", id=legacy_id, evidence_ref="")
        row.pop("hold_reason")
        self.must_reject([row], "evidence_ref must be nonblank")

    def test_mixed_vocab_preserves_categories(self):
        rows = [
            record("PASS", id="fixture:1"),
            record("FAIL", id="fixture:2"),
            record("FAIL_SCOPED", id="fixture:3"),
            record("HELD", id="fixture:4"),
            record("PASS_PUBLICATION_ONLY", id="fixture:5"),
        ]
        s = self.check_rows(rows)
        self.assertEqual(s["records"], 5)
        self.assertEqual(set(s["counts"].values()), {1})

    def test_real_ledger_smoke_without_mutation(self):
        path = ROOT / "ai" / "benchmark-evo.jsonl"
        before = path.read_bytes()
        x = checker.validate(path)
        self.assertGreaterEqual(x["records"], 131)
        self.assertGreaterEqual(x["counts"]["FAIL_SCOPED"], 2)
        self.assertGreaterEqual(x["counts"]["PASS_PUBLICATION_ONLY"], 4)
        self.assertEqual(path.read_bytes(), before)

    def test_blank_line_rejected(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "emptyrow.jsonl"
            path.write_text(json.dumps(record()) + "\n\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "blank line"):
                checker.validate(path)

    def test_empty_log_rejected(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "empty.jsonl"
            path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "empty"):
                checker.validate(path)

    def test_invalid_json_rejected(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.jsonl"
            path.write_text("{not json}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                checker.validate(path)


if __name__ == "__main__":
    unittest.main()
