"""Offline tests for strict CoSpeedo ledger evidence and nonpromotion."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import CoSpeedoLedgerAuditR0 as audit


class CoSpeedoLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "ai").mkdir()
        (self.root / "benchmarks").mkdir()
        self.ai = self.root / "ai/benchmark-evo.jsonl"
        self.events = self.root / "benchmarks/evo.jsonl"
        self.write_lines(self.ai, [
            {"id":"test-source-one","observed_at":"2026-10-23T18:36:58Z","status":"PASS"},
            {"id":"test-source-two","observed_at":"2026-10-25","status":"HELD"},
        ])
        self.write_lines(self.events, [
            {"wave":"wave-one","ts":"2026-10-24T01:00:00Z","state":"BOUNDED_COMPLETE"},
            {"wave":"wave-two","ts":"2026-10-26T05:35:36Z","state":"SOURCE_CHANGE_ONLY"},
        ])

    def write_lines(self, path, objects):
        path.write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in objects),encoding="utf-8")

    def report(self):
        return audit.build_report(self.root,date(2026,10,26))

    def test_01_schema_and_exact_sample_scope(self):
        x=self.report()
        self.assertEqual(x["schema"],audit.SCHEMA)
        self.assertEqual(x["sampled_total_rows"],4)
        self.assertEqual(len(x["source_checks"]),2)

    def test_02_all_seven_days_present(self):
        v=self.report()["sampled_daily_activity"]
        self.assertEqual(v[0]["utc_day"],"2026-10-20")
        self.assertEqual(v[-1]["utc_day"],"2026-10-26")
        self.assertEqual([x["sampled_evidence_records"] for x in v],[0,0,0,1,1,1,1])

    def test_03_no_records_not_global_zero(self):
        x=self.report()["sampled_daily_activity"][0]
        self.assertEqual(x["sampled_evidence_records"],0)
        self.assertIn("NOT_GLOBAL_ZERO",x["coverage"])

    def test_04_status_pass_is_not_useful_acceptance(self):
        m=self.report()["metrics"]
        self.assertIsNone(m["CoClosureYield"]["value"])
        self.assertEqual(m["CoClosureYield"]["state"],"UNKNOWN")

    def test_05_exponential_claim_not_promoted(self):
        m=self.report()["metrics"]
        self.assertEqual(m["CoSpeedoBenefitAcceleration"]["state"],"NOT_ESTABLISHED")
        self.assertIsNone(m["CoTurtleCompoundingGain"]["value"])

    def test_06_tasks_and_providers_not_started(self):
        e=self.report()["effects"]
        self.assertTrue(all(v==0 for v in e.values()))

    def test_07_old_literal_escaped_newline_rejected(self):
        self.events.write_text(
            '{"ts":"2026-10-23T00:00:00Z","wave":"A","state":"X"}\\n'
            '{"ts":"2026-10-23T01:00:00Z","wave":"B","state":"Y"}\n',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(audit.LedgerError,"INVALID_JSONL"):
            self.report()

    def test_08_repaired_two_newlines_pass(self):
        self.write_lines(self.events,[
            {"ts":"2026-10-23T00:00:00Z","wave":"A","state":"X"},
            {"ts":"2026-10-23T01:00:00Z","wave":"B","state":"Y"},
        ])
        self.assertEqual(self.report()["sampled_total_rows"],4)

    def test_09_duplicate_wave_rejected(self):
        self.write_lines(self.events,[
            {"ts":"2026-10-23T00:00:00Z","wave":"A","state":"X"},
            {"ts":"2026-10-23T01:00:00Z","wave":"A","state":"Y"},
        ])
        with self.assertRaisesRegex(audit.LedgerError,"DUPLICATE_RECORD_ID"):
            self.report()

    def test_10_duplicate_ai_identity_rejected(self):
        self.write_lines(self.ai,[
            {"observed_at":"2026-10-23","id":"one","status":"PASS"},
            {"observed_at":"2026-10-24","id":"one","status":"FAIL"},
        ])
        with self.assertRaisesRegex(audit.LedgerError,"DUPLICATE_RECORD_ID"):
            self.report()

    def test_11_malformed_time_rejected(self):
        self.write_lines(self.ai,[{"observed_at":"not a real date","id":"x","status":"PASS"}])
        with self.assertRaisesRegex(audit.LedgerError,"UNPARSEABLE_OBSERVATION_TIME"):
            self.report()

    def test_12_timestamp_must_be_timezone_qualified(self):
        self.write_lines(self.ai,[{"observed_at":"2026-10-25T01:00:00","id":"x","status":"PASS"}])
        with self.assertRaisesRegex(audit.LedgerError,"MISSING_TZ"):
            self.report()

    def test_13_missing_source_is_not_an_empty_ledger(self):
        self.ai.unlink()
        with self.assertRaisesRegex(audit.LedgerError,"MISSING_ELECTED_LEDGER"):
            self.report()

    def test_14_truncated_json_rejected(self):
        self.events.write_text('{"wave":"A","ts":"2026-10-23T00:00:00Z",',encoding="utf-8")
        with self.assertRaisesRegex(audit.LedgerError,"INVALID_JSONL"):
            self.report()

    def test_15_invalid_utf8_rejected(self):
        self.events.write_bytes(b"\xff\xfe")
        with self.assertRaisesRegex(audit.LedgerError,"INVALID_UTF8"):
            self.report()

    def test_16_invalid_ai_status_rejected(self):
        self.write_lines(self.ai,[{"observed_at":"2026-10-23","id":"x","status":"UNIVERSAL_SUCCESS"}])
        with self.assertRaisesRegex(audit.LedgerError,"INVALID_SCOPED_TEST_STATUS"):
            self.report()

    def test_17_unknown_effect_fields_do_not_overclaim(self):
        self.write_lines(self.ai,[{
            "observed_at":"2026-10-24","id":"x","status":"PASS",
            "receiver_accepted":True,"benefit":"claimed without exact independent readproof",
        }])
        m=self.report()["metrics"]
        self.assertIsNone(m["CoClosureYield"]["value"])
        self.assertEqual(m["CoSpeedoBenefitAcceleration"]["state"],"NOT_ESTABLISHED")

    def test_18_empty_interior_row_rejected(self):
        self.events.write_text(
            '{"ts":"2026-10-24","wave":"one","state":"SOURCE"}\n\n'
            '{"ts":"2026-10-24","wave":"two","state":"SOURCE"}\n',encoding="utf-8")
        with self.assertRaisesRegex(audit.LedgerError,"EMPTY_INTERIOR_JSONL_ROW"):
            self.report()

    def test_19_none_for_incomplete_recurrence_coverage(self):
        self.assertEqual(self.report()["metrics"]["InternalRecurringProductRatio"]["state"],"UNKNOWN")

    def test_20_real_repo_fixture_when_available(self):
        root=Path(__file__).resolve().parents[1]
        if not (root/"benchmarks/evo.jsonl").exists() or not (root/"ai/benchmark-evo.jsonl").exists():
            self.skipTest("repo ledgers not present in isolated fixture")
        output=audit.build_report(root,date(2026,10,26))
        self.assertEqual(output["source_checks"][0]["physical_jsonl_rows"],
                         output["source_checks"][0]["unique_record_ids"])
        self.assertEqual(output["source_checks"][1]["physical_jsonl_rows"],
                         output["source_checks"][1]["unique_record_ids"])
        self.assertEqual(output["metrics"]["CoSpeedoBenefitAcceleration"]["state"],"NOT_ESTABLISHED")

    def test_21_cli_failure_does_not_print_fake_report(self):
        self.ai.unlink()
        capture=io.StringIO()
        with contextlib.redirect_stderr(capture):
            rc=audit.main(["--root",str(self.root),"--as-of","2026-10-26"])
        self.assertEqual(rc,2)
        self.assertIn("FAIL_CLOSED",capture.getvalue())


if __name__ == "__main__":
    unittest.main()
