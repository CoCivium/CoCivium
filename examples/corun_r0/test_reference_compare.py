"""Adversarial checks for independent-code-path CoRun reference comparison.

No claims of independent scientific replication, legacy-product superiority,
or human-time savings. The source is synthetic and code is read-only.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

try:
    from .corun import canonical_bytes, execute, git_blob, load_source
    from .reference_oracle import independent_reference
    from .reference_compare import (
        assert_semantic_agreement, compare_paths, write_evidence,
    )
except ImportError:
    from corun import canonical_bytes, execute, git_blob, load_source
    from reference_oracle import independent_reference
    from reference_compare import (
        assert_semantic_agreement, compare_paths, write_evidence,
    )

HERE = Path(__file__).resolve().parent


def fixture() -> dict:
    return json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def meta() -> dict:
    return {"sha256": "TEST_FIXTURE", "git_blob_sha1": "TEST_FIXTURE"}


class IndependentCodePathTests(unittest.TestCase):
    def test_reference_matches_separately_executed_dag(self):
        v = fixture()
        oracle = independent_reference(v)
        actual, _ = execute(v, 4)
        self.assertEqual(canonical_bytes(oracle), canonical_bytes(actual))
        self.assertEqual(assert_semantic_agreement(oracle, actual),
                         hashlib.sha256(canonical_bytes(actual)).hexdigest())

    def test_counterbalanced_comparison_receipts_only_semantics(self):
        data = compare_paths(fixture(), meta(), workers=4, trials=5)
        self.assertEqual(data["trials"], 5)
        self.assertTrue(data["output_equal_every_trial"])
        self.assertEqual(len(data["arms"]["A_DIRECT_REFERENCE"]["elapsed_ns"]), 5)
        self.assertEqual(len(data["arms"]["B_CORUN_DAG"]["elapsed_ns"]), 5)
        self.assertEqual(data["product_promotion"], "HELD")
        self.assertIn("LEGACY_PRODUCT_BASELINE_NOT_MEASURED",
                      data["measurement_limitations"])
        self.assertIn("HUMAN_ACTIVE_MINUTES_NOT_MEASURED",
                      data["measurement_limitations"])

    def test_oracle_detects_counterevidence_change(self):
        original = independent_reference(fixture())
        altered = copy.deepcopy(original)
        altered["counterevidence"]["warnings"].remove(
            "ONE_PIPELINE_NOT_INDEPENDENT_REPLICATION"
        )
        with self.assertRaisesRegex(ValueError, "mismatch"):
            assert_semantic_agreement(altered, original)

    def test_oracle_detects_dropped_failure(self):
        original = independent_reference(fixture())
        altered = copy.deepcopy(original)
        altered["audit"]["cases"] = [
            c for c in altered["audit"]["cases"] if c["id"] != "F04"
        ]
        with self.assertRaisesRegex(ValueError, "mismatch"):
            assert_semantic_agreement(altered, original)

    def test_pair_challenge_kept_in_both_independent_paths(self):
        v = fixture()
        for c in v["cases"]:
            if c["id"] == "F01":
                c["paired_case_id"] = None
        reference = independent_reference(v)
        candidate, _ = execute(v, 2)
        self.assertIn("NONRECIPROCAL_PAIR_REFERENCE",
                      reference["counterevidence"]["warnings"])
        self.assertEqual(canonical_bytes(reference), canonical_bytes(candidate))

    def test_pair_does_not_hide_missing_source(self):
        v = fixture()
        v["cases"][0]["paired_case_id"] = "MISSING"
        with self.assertRaisesRegex(ValueError, "target absent"):
            independent_reference(v)

    def test_reference_rejects_duplicate_cases(self):
        v = fixture()
        v["cases"].append(copy.deepcopy(v["cases"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            independent_reference(v)

    def test_parameter_budget_fail_closed(self):
        for args in ({"trials": 2}, {"trials": 26}, {"workers": 0},
                     {"workers": 9}):
            with self.subTest(args=args):
                with self.assertRaisesRegex(ValueError, "must be"):
                    compare_paths(fixture(), meta(), **args)

    def test_source_not_mutated_and_no_unproven_promotion(self):
        v = fixture()
        original = canonical_bytes(v)
        result = compare_paths(v, meta(), trials=3)
        self.assertEqual(original, canonical_bytes(v))
        self.assertEqual(result["measurement_status"],
                         "CODE_PATH_SEMANTICS_ONLY__NOT_FAIR_PRODUCT_SPEED_TRIAL")
        self.assertEqual(result["external_effects"], "NONE")
        self.assertNotIn("INDEPENDENT_FACTS_PROVED", json.dumps(result))

    def test_reference_receipt_exact_and_no_overwrite(self):
        record = compare_paths(fixture(), meta(), trials=3)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "run"
            report, receipt = write_evidence(dest, record)
            proof = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(proof["report_sha256"],
                             hashlib.sha256(report.read_bytes()).hexdigest())
            self.assertFalse(proof["independent_facts"])
            self.assertEqual(proof["receiver_ack"], "UNKNOWN")
            with self.assertRaises(FileExistsError):
                write_evidence(dest, record)

    def test_readonly_source_pin_rejects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "input.json"
            path.write_bytes(canonical_bytes(fixture()))
            valid = git_blob(path.read_bytes())
            self.assertEqual(load_source(path, valid)[1]["git_blob_sha1"], valid)
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "pin mismatch"):
                load_source(path, valid)


if __name__ == "__main__":
    unittest.main()
