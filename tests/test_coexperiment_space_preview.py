from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "CoExperimentSpacePreviewR0.py"
IMPORT = importlib.util.spec_from_file_location("coexperiment", SCRIPT)
coexperiment = importlib.util.module_from_spec(IMPORT)
IMPORT.loader.exec_module(coexperiment)

EXPECTED_RAW_COUNT = 422_730_484_678_656_000


class CoExperimentSpacePreviewTests(unittest.TestCase):
    def test_raw_space_is_quadrillion_scale_and_zero_execution(self):
        result = coexperiment.build_preview(ROOT, limit=12, seed="turtles")
        self.assertEqual(result["raw_candidate_descriptor_count"], EXPECTED_RAW_COUNT)
        self.assertGreater(result["raw_candidate_descriptor_count"], 10**15)
        self.assertEqual(result["executed_experiment_count"], 0)
        self.assertEqual(result["effects"]["workers_started"], 0)
        self.assertEqual(result["effects"]["provider_sessions_created"], 0)
        self.assertEqual(result["effects"]["experiments_executed"], 0)

    def test_sample_is_bounded_and_deterministic(self):
        left = coexperiment.build_preview(ROOT, limit=100, seed="same")
        right = coexperiment.build_preview(ROOT, limit=100, seed="same")
        self.assertEqual(left, right)
        self.assertEqual(left["sample_count"], 100)
        ids = [row["experiment_descriptor_id"] for row in left["sample"]]
        ranks = [row["filtered_rank"] for row in left["sample"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ranks), len(set(ranks)))

    def test_zero_sample_does_not_decode_descriptors(self):
        result = coexperiment.build_preview(ROOT, limit=0, seed="none")
        self.assertEqual(result["sample"], [])
        self.assertEqual(result["sample_count"], 0)

    def test_exact_filter_reduces_space_without_claiming_eligibility(self):
        result = coexperiment.build_preview(
            ROOT,
            filters={
                "operational_role": "CHALLENGER",
                "turtle_depth": "DEPTH_2_MAX",
                "experiment_family": "FAULT_INJECTION",
            },
            limit=5,
            seed="filtered",
        )
        self.assertLess(
            result["filtered_candidate_descriptor_count"],
            result["raw_candidate_descriptor_count"],
        )
        self.assertIsNone(result["eligible_experiment_count"])
        for row in result["sample"]:
            self.assertEqual(row["facets"]["operational_role"], "CHALLENGER")
            self.assertEqual(row["facets"]["turtle_depth"], "DEPTH_2_MAX")
            self.assertEqual(row["facets"]["experiment_family"], "FAULT_INJECTION")

    def test_turtles_share_budget_and_cannot_raise_authority(self):
        turtle = coexperiment.build_preview(ROOT, limit=1)["turtle_policy"]
        self.assertEqual(turtle["maximum_runtime_depth"], 2)
        self.assertEqual(turtle["maximum_review_rounds"], 2)
        self.assertTrue(turtle["children_share_parent_budget"])
        self.assertFalse(turtle["children_may_replenish_budget"])
        self.assertFalse(turtle["children_may_raise_authority"])

    def test_high_bar_requires_correctness_provenance_and_receiver_value(self):
        gates = set(coexperiment.build_preview(ROOT, limit=1)["high_bar_gates"])
        required = {
            "EXACT_INPUT_BINDINGS",
            "PINNED_BASELINE",
            "CORRECTNESS_NONREGRESSION",
            "REPEATED_MEASUREMENTS",
            "PROVENANCE_AND_CURRENTNESS",
            "COUNTEREXAMPLE_OR_CHALLENGE",
            "INDEPENDENCE_STATUS_EXPLICIT",
            "RECEIVER_VALUE_EXPLICIT",
        }
        self.assertTrue(required.issubset(gates))

    def test_promotion_ladder_starts_as_descriptor_not_execution(self):
        result = coexperiment.build_preview(ROOT, limit=1)
        self.assertEqual(result["promotion_ladder"][0], "DESCRIPTOR")
        self.assertIn("MICRO_CANARY", result["promotion_ladder"])
        self.assertEqual(
            result["sample"][0]["execution_state"],
            "NOT_SELECTED_OR_EXECUTED",
        )

    def test_invalid_filters_and_limits_fail_closed(self):
        with self.assertRaises(ValueError):
            coexperiment.build_preview(
                ROOT, filters={"not_an_axis": "x"}, limit=1
            )
        with self.assertRaises(ValueError):
            coexperiment.build_preview(
                ROOT, filters={"turtle_depth": "DEPTH_999"}, limit=1
            )
        for limit in (-1, 101, True):
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    coexperiment.build_preview(ROOT, limit=limit)

    def test_source_bindings_cover_existing_registries(self):
        result = coexperiment.build_preview(ROOT, limit=1)
        paths = {row["path"] for row in result["source_bindings"]}
        self.assertEqual(paths, set(coexperiment.SOURCE_PATHS))

    def test_nonclaims_separate_descriptor_scale_from_runtime(self):
        nonclaims = set(coexperiment.build_preview(ROOT, limit=1)["nonclaims"])
        self.assertIn("RAW_DESCRIPTOR_COUNT_NE_USEFUL_EXPERIMENT_COUNT", nonclaims)
        self.assertIn("DESCRIPTOR_NE_EXPERIMENT", nonclaims)
        self.assertIn("TURTLE_TEMPLATE_NE_LIVE_RECURSION", nonclaims)
        self.assertIn("LOGICAL_SCALE_NE_ACTIVE_WORKERS", nonclaims)


if __name__ == "__main__":
    unittest.main()
