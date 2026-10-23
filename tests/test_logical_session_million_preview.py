from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "CoLogicalSessionMillionPreviewR0.py"
SPEC = importlib.util.spec_from_file_location("logical_million", SCRIPT)
logical = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(logical)


class LogicalMillionPreviewTests(unittest.TestCase):
    def test_one_million_is_recipe_backed_and_not_materialized(self):
        result = logical.build_preview(
            ROOT, logical_count=1_000_000, sample_limit=12,
            materialization_ceiling=64, seed="million"
        )
        self.assertEqual(result["logical_session_count"], 1_000_000)
        self.assertEqual(result["enumerated_session_records"], 12)
        self.assertEqual(result["eligible_materialization_count"], None)
        self.assertEqual(result["selected_for_materialization"], [])
        self.assertEqual(result["effects"]["workers_started"], 0)
        self.assertEqual(result["effects"]["provider_sessions_created"], 0)
        self.assertEqual(result["effects"]["accounts_created"], 0)
        self.assertTrue(all(
            row["materialization_state"] == "LOGICAL_ONLY"
            for row in result["preview"]
        ))

    def test_large_count_decodes_only_bounded_sample(self):
        with mock.patch.object(
            logical, "session_descriptor", wraps=logical.session_descriptor
        ) as descriptor:
            result = logical.build_preview(
                ROOT, logical_count=10**12, sample_limit=7,
                materialization_ceiling=128, seed="huge"
            )
        self.assertEqual(descriptor.call_count, 7)
        self.assertEqual(result["enumerated_session_records"], 7)

    def test_zero_sample_decodes_no_sessions(self):
        with mock.patch.object(logical, "session_descriptor") as descriptor:
            result = logical.build_preview(
                ROOT, logical_count=1_000_000, sample_limit=0,
                materialization_ceiling=0, seed="quiet"
            )
        descriptor.assert_not_called()
        self.assertEqual(result["preview"], [])
        self.assertEqual(result["sampling"]["sample_indices"], [])

    def test_sample_is_deterministic_and_unique(self):
        left = logical.build_preview(ROOT, 1_000_000, 40, 64, "same")
        right = logical.build_preview(ROOT, 1_000_000, 40, 64, "same")
        self.assertEqual(left, right)
        ids = [row["virtual_session_id"] for row in left["preview"]]
        indices = left["sampling"]["sample_indices"]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(indices), len(set(indices)))

    def test_seed_changes_preview_identity(self):
        left = logical.build_preview(ROOT, 1000, 5, 8, "a")
        right = logical.build_preview(ROOT, 1000, 5, 8, "b")
        self.assertNotEqual(
            [row["virtual_session_id"] for row in left["preview"]],
            [row["virtual_session_id"] for row in right["preview"]],
        )

    def test_materialization_ceiling_never_selects_by_itself(self):
        result = logical.build_preview(ROOT, 1000, 8, 1000, "ceiling")
        self.assertEqual(result["materialization_ceiling"], 1000)
        self.assertEqual(result["selected_for_materialization"], [])
        self.assertIn(
            "MATERIALIZATION_CEILING_NE_SELECTION", result["nonclaims"]
        )

    def test_facets_are_drawn_from_existing_registries(self):
        policy, spawn, _ = logical.load_sources(ROOT)
        result = logical.build_preview(ROOT, 1000, 20, 4, "facets")
        for row in result["preview"]:
            self.assertIn(row["role"], spawn["properties"]["role"]["enum"])
            self.assertIn(row["morphology"], policy["morphologies"])
            self.assertIn(row["persistence_mode"], policy["persistence_modes"])

    def test_invalid_numeric_bounds_fail_closed(self):
        cases = [
            dict(logical_count=0),
            dict(logical_count=10**12 + 1),
            dict(logical_count=True),
            dict(sample_limit=-1),
            dict(sample_limit=101),
            dict(sample_limit=False),
            dict(materialization_ceiling=-1),
            dict(materialization_ceiling=4097),
            dict(materialization_ceiling=True),
        ]
        for changes in cases:
            kwargs = dict(
                logical_count=100, sample_limit=5,
                materialization_ceiling=10, seed="x"
            )
            kwargs.update(changes)
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    logical.build_preview(ROOT, **kwargs)

    def test_nonclaims_keep_logical_and_live_counts_separate(self):
        result = logical.build_preview(ROOT, 1_000_000, 1, 64, "rails")
        self.assertIn(
            "LOGICAL_SESSION_COUNT_NE_ACTIVE_PROCESS_COUNT",
            result["nonclaims"],
        )
        self.assertIn(
            "LOGICAL_SESSION_COUNT_NE_PROVIDER_SESSION_COUNT",
            result["nonclaims"],
        )
        self.assertEqual(
            result["activation_policy"]["anonymous_or_deceptive_identity_creation"],
            "OUT_OF_SCOPE_AND_NOT_PERMITTED_BY_THIS_PREVIEW",
        )


if __name__ == "__main__":
    unittest.main()
