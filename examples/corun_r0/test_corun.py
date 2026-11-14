"""Offline, stdlib-only tests for the finite CoRun+ R0 control and challenger."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

try:
    from .corun import (Node, build_graph, canonical_bytes, compare, execute,
                        exclusive_write, git_blob, load_source, sha, validate_graph, WORK_ID)
except ImportError:
    from corun import (Node, build_graph, canonical_bytes, compare, execute,
                       exclusive_write, git_blob, load_source, sha, validate_graph, WORK_ID)

HERE = Path(__file__).resolve().parent


def source():
    return json.loads((HERE / "fixture.json").read_text())


class CoRunTests(unittest.TestCase):
    def test_fixture_contract_and_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "src.json"
            p.write_bytes(canonical_bytes(source()))
            value, meta = load_source(p, git_blob(p.read_bytes()))
            self.assertEqual(len(value["cases"]), 12)
            self.assertEqual(meta["sha256"], sha(p.read_bytes()))
            self.assertEqual(meta["git_blob_sha1"], git_blob(p.read_bytes()))

    def test_pin_mismatch_halts(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "src.json"
            p.write_bytes(canonical_bytes(source()))
            with self.assertRaisesRegex(ValueError, "pin mismatch"):
                load_source(p, "0" * 40)

    def test_source_changed_halts(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "src.json"
            p.write_bytes(canonical_bytes(source()))
            pin = git_blob(p.read_bytes())
            p.write_bytes(p.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "pin mismatch"):
                load_source(p, pin)

    def test_duplicate_case_halts(self):
        v = source()
        v["cases"].append(copy.deepcopy(v["cases"][0]))
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "s.json"
            p.write_bytes(canonical_bytes(v))
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_source(p)

    def test_unknown_status_halts(self):
        v = source()
        v["cases"][0]["ledger_status"] = "VERIFIED_ADOPTION"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "s.json"
            p.write_bytes(canonical_bytes(v))
            with self.assertRaisesRegex(ValueError, "unrecognized ledger status"):
                load_source(p)

    def test_missing_pair_halts(self):
        v = source()
        v["cases"][0]["paired_case_id"] = "F99"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "s.json"
            p.write_bytes(canonical_bytes(v))
            with self.assertRaisesRegex(ValueError, "paired case absent"):
                load_source(p)

    def test_bad_schema_halts(self):
        v = source()
        v["schema"] = "NOT_TRUSTED"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "s.json"
            p.write_bytes(canonical_bytes(v))
            with self.assertRaisesRegex(ValueError, "schema"):
                load_source(p)

    def test_invalid_graph_self_cycle(self):
        with self.assertRaisesRegex(ValueError, "invalid dependency"):
            validate_graph([Node("a", "test", ("a",))])

    def test_invalid_graph_mutual_cycle(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            validate_graph([Node("a", "test", ("b",)), Node("b", "test", ("a",))])

    def test_unbounded_worker_budget_halts(self):
        with self.assertRaisesRegex(ValueError, "worker/latency budget"):
            execute(source(), 99)

    def test_equal_outputs_independent_of_schedule(self):
        a, m1 = execute(source(), 1)
        b, m2 = execute(source(), 4)
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))
        self.assertEqual(m1["nodes_completed"], m2["nodes_completed"])
        self.assertEqual(a["audit"]["strata_counts"], {"WORKED_SCOPED": 4, "PARTIAL_OR_BLOCKED": 4, "FAILED_HISTORICAL_REPAIRED": 3, "FAILED_STILL_OBSERVED": 1})
        self.assertEqual(a["counterevidence"]["independence"], "NOT_ESTABLISHED")
        self.assertIsNone(a["counterevidence"]["human_minutes"])

    def test_fault_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "failed closed"):
            execute(source(), 4, inject_fail="case:W01")

    def test_nonreciprocal_dissent(self):
        v = source()
        for c in v["cases"]:
            if c["id"] == "F01":
                c["paired_case_id"] = None
        result, _ = execute(v, 4)
        self.assertIn("NONRECIPROCAL_PAIR_REFERENCE", result["counterevidence"]["warnings"])

    def test_ab_honest_classification(self):
        r = compare(source(), {"git_blob_sha1": "synthetic", "sha256": "synthetic"}, 4)
        self.assertTrue(r["outputs_equal"])
        self.assertEqual(r["comparison"]["classification"], "LOCAL_STRUCTURAL_PROBE")
        self.assertEqual(r["comparison"]["production_promotion"], "HELD")
        self.assertIsNone(r["comparison"]["human_time_saved"])
        self.assertNotIn("WINNER_IS_REAL_WORLD_PROVEN", json.dumps(r))

    def test_injected_latency_classified_synthetic(self):
        r = compare(source(), {"git_blob_sha1": "synthetic", "sha256": "synthetic"}, 4, delay_ms=15)
        self.assertEqual(r["comparison"]["classification"], "SYNTHETIC_DELAY_CONTROL")
        self.assertEqual(r["comparison"]["production_promotion"], "HELD")

    def test_hash_receipt_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as td:
            r = compare(source(), {"git_blob_sha1": "synthetic", "sha256": "synthetic"}, 2)
            output = Path(td) / "newrun"
            report_path, receipt_path = exclusive_write(output, r)
            receipt = json.loads(receipt_path.read_text())
            self.assertEqual(receipt["runset_sha256"], hashlib.sha256(report_path.read_bytes()).hexdigest())
            self.assertEqual(receipt["external_receiver"], "UNKNOWN")
            with self.assertRaisesRegex(ValueError, "output exists"):
                exclusive_write(output, r)

    def test_source_unmodified(self):
        v = source()
        before = canonical_bytes(v)
        execute(v, 4)
        self.assertEqual(canonical_bytes(v), before)

    def test_workers_never_promoted_to_agents(self):
        r = compare(source(), {"git_blob_sha1": "synthetic", "sha256": "synthetic"}, 4)
        self.assertIn("THREAD_COUNT_NE_AUTONOMOUS_AGENTS", r["nonclaims"])
        self.assertEqual(r["deliverable"]["effect_class"], "READ_ONLY_LOCAL")


if __name__ == "__main__":
    unittest.main()
