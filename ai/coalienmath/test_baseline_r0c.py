"""Public synthetic comparison with an ordinary typed-JSON baseline.

The test author controls both implementations and the fixture design.
Agreement on these finite cases does not prove superiority or independence.
"""
from __future__ import annotations

import json
import math
import pathlib
import unittest

from plain_json_baseline_r0c import evaluate as json_baseline
from model_r0 import (
    NullKind, QualifiedObservation, authorized_transform,
    count_failure_domains, decision_preserving, distinguishable_by,
    likelihood_evidence_bits, numeric_residual,
)


HERE = pathlib.Path(__file__).resolve().parent


def model_observation(data):
    # Explicit transport decoding is distinct from a dataclass receiving raw data.
    raw = data["null_kind"]
    if type(raw) is str and raw in {entry.value for entry in NullKind}:
        raw = NullKind(raw)
    return QualifiedObservation(data["subject"], data["quantity_kind"], data["unit"], data["value"], raw)


def model_evaluate(row):
    op = row["op"]
    try:
        if op == "observation":
            model_observation(row["item"])
            return "ALLOW"
        if op == "residual":
            return numeric_residual(model_observation(row["predicted"]), model_observation(row["observed"]))
        if op == "bits":
            return likelihood_evidence_bits(row["p_h"], row["p_not_h"])
        if op == "permission":
            return "ALLOW" if authorized_transform(frozenset(row["source"]), frozenset(row["target"])) else "BLOCK"
        if op == "witnesses":
            return count_failure_domains(row["domains"])
        if op == "decision":
            pairs = row["pairs"]
            return "TRUE" if decision_preserving(pairs, lambda x: x["code"], lambda x: x["decision"]) else "FALSE"
        if op == "distinguish":
            return "TRUE" if distinguishable_by(row["first"], row["second"], lambda x: x) else "FALSE"
    except (TypeError, ValueError, KeyError, OverflowError):
        return "HOLD"
    return "HOLD"


def matches(got, expected):
    if type(got) in (float, int) and type(expected) in (float, int):
        return math.isfinite(got) and math.isclose(got, expected, rel_tol=1e-12, abs_tol=1e-12)
    return type(got) is type(expected) and got == expected


class PlainTypedJsonBaselineComparisonR0C(unittest.TestCase):
    def test_fixture_identity_and_distinctness(self):
        cases = json.loads((HERE / "baseline_cases_r0c.json").read_text(encoding="utf-8"))
        ids = [row["id"] for row in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 25)
        self.assertTrue(all(type(row["op"]) is str for row in cases))

    def test_baseline_matches_precommitted_expected(self):
        cases = json.loads((HERE / "baseline_cases_r0c.json").read_text(encoding="utf-8"))
        for row in cases:
            with self.subTest(id=row["id"]):
                self.assertTrue(matches(json_baseline(row), row["expect"]), (row["id"], json_baseline(row), row["expect"]))

    def test_candidate_matches_same_expected(self):
        cases = json.loads((HERE / "baseline_cases_r0c.json").read_text(encoding="utf-8"))
        for row in cases:
            with self.subTest(id=row["id"]):
                got = model_evaluate(row)
                self.assertTrue(matches(got, row["expect"]), (row["id"], got, row["expect"]))

    def test_parity_on_all_precommitted_cases(self):
        cases = json.loads((HERE / "baseline_cases_r0c.json").read_text(encoding="utf-8"))
        for row in cases:
            with self.subTest(id=row["id"]):
                self.assertTrue(matches(json_baseline(row), model_evaluate(row)), (row["id"], json_baseline(row), model_evaluate(row)))

    def test_no_false_green_on_invalid_case(self):
        cases = json.loads((HERE / "baseline_cases_r0c.json").read_text(encoding="utf-8"))
        negative = [row for row in cases if row["expect"] == "HOLD"]
        self.assertGreaterEqual(len(negative), 10)
        for row in negative:
            with self.subTest(id=row["id"]):
                self.assertEqual(json_baseline(row), "HOLD")
                self.assertEqual(model_evaluate(row), "HOLD")


if __name__ == "__main__":
    unittest.main()
