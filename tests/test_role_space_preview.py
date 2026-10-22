#!/usr/bin/env python3
"""Bounded role-preview regressions using source bytes and small independent grids.

These tests establish projection and sampling behavior, not eligible-role counts,
actor independence, current-source discovery, or live fleet execution.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import itertools
import json
from math import prod
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/CoRoleSpacePreviewR0.py"
SPEC = importlib.util.spec_from_file_location("role_preview_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PREVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREVIEW)

# The independent oracle reads the four declared source contracts directly.
SOURCE_PATHS = (
    "schemas/cospawn-contract-v0.1.schema.json",
    "ai/virtual-session-policy.json",
    "ai/evolution-lanes.json",
    "schemas/coevo-delta-v0.1.schema.json",
)
AXIS_NAMES = (
    "operational_role", "morphology", "persistence_mode",
    "participant_class", "domain", "epistemic_class",
)
PINNED_SHA256 = (
    "28062b9c86edfb633c6c3eea3b1b71dea0307ff42692a93a5d05c7ffb90dad0b",
    "ee9dd50d81b43ecf5efca9743a8c99f7a661b9538927846d2f98809c0a3cae3d",
    "68b9a58e1f300f5dc7e0713598e96d4b18de0bfc4b06813b96b6446a578c670b",
    "c14088d04c4ceea9674e4865eff62055ba323dbb31be484e462f1c95ff3ed506",
)


def source_bytes(root: Path) -> dict[str, bytes]:
    return {name: (root / name).read_bytes() for name in SOURCE_PATHS}


def independent_axes(raw: dict[str, bytes]) -> dict[str, list[str]]:
    spawn, policy, lanes, delta = (
        json.loads(raw[name].decode("utf-8")) for name in SOURCE_PATHS
    )
    return {
        "operational_role": spawn["properties"]["role"]["enum"],
        "morphology": policy["morphologies"],
        "persistence_mode": policy["persistence_modes"],
        "participant_class": policy["participant_classes"],
        "domain": [row[0] for row in lanes["domains"]],
        "epistemic_class": delta["properties"]["epistemic_class"]["enum"],
    }


def fixture_documents(width: int = 2) -> dict[str, dict]:
    def values(prefix: str) -> list[str]:
        return [f"{prefix}-{index}" for index in range(width)]

    return {
        SOURCE_PATHS[0]: {"properties": {"role": {"enum": values("role")}}},
        SOURCE_PATHS[1]: {
            "morphologies": values("morphology"),
            "persistence_modes": values("persistence"),
            "participant_classes": values("participant"),
        },
        SOURCE_PATHS[2]: {
            "domains": [[name, [], "TEST"] for name in values("domain")],
        },
        SOURCE_PATHS[3]: {
            "properties": {"epistemic_class": {"enum": values("epistemic")}},
        },
    }


def set_axis(documents: dict, name: str, values) -> None:
    if name == "operational_role":
        documents[SOURCE_PATHS[0]]["properties"]["role"]["enum"] = values
    elif name == "epistemic_class":
        documents[SOURCE_PATHS[3]]["properties"]["epistemic_class"]["enum"] = values
    elif name == "domain":
        documents[SOURCE_PATHS[2]]["domains"] = [[value, [], "TEST"] for value in values]
    else:
        key = {
            "morphology": "morphologies",
            "persistence_mode": "persistence_modes",
            "participant_class": "participant_classes",
        }[name]
        documents[SOURCE_PATHS[1]][key] = values


def write_fixture(root: Path, documents: dict) -> None:
    for name in SOURCE_PATHS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(documents[name], ensure_ascii=False) + "\n", encoding="utf-8")


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in root.rglob("*")
    }


class RoleSpacePreviewTests(unittest.TestCase):
    def checked_preview(self, root: Path = ROOT, filters=None, limit=7, seed="0"):
        before = source_bytes(root)
        filters_before = copy.deepcopy(filters)
        axes = independent_axes(before)
        result = PREVIEW.build_preview(root, filters, limit, seed)
        self.assertEqual(source_bytes(root), before, "preview altered a source file")
        self.assertEqual(filters, filters_before, "preview altered caller filters")

        expected_bindings = [
            {"path": name, "sha256": hashlib.sha256(before[name]).hexdigest(), "bytes": len(before[name])}
            for name in SOURCE_PATHS
        ]
        self.assertEqual(result["source_bindings"], expected_bindings)
        self.assertEqual(result["axis_counts"], {name: len(values) for name, values in axes.items()})
        self.assertEqual(result["raw_configuration_count"], prod(map(len, axes.values())))
        selected = {
            name: [filters[name]] if filters and name in filters else values
            for name, values in axes.items()
        }
        count = prod(map(len, selected.values()))
        self.assertEqual(result["filtered_configuration_count"], count)
        self.assertEqual(result["exact_filters"], filters or {})
        self.assertIsNone(result["eligible_configuration_count"])
        self.assertEqual(result["sample_count"], min(limit, count))
        self.assertEqual(len(result["preview"]), min(limit, count))
        self.assertLessEqual(len(result["preview"]), 100)
        self.assertEqual(result["sampling"]["maximum_sample"], 100)
        self.assertEqual(result["sampling"]["coverage_claim"], "NONE")
        self.assertEqual(result["sampling"]["seed"], seed)
        self.assertEqual(result["state"], "CANDIDATE_PREVIEW__NO_ASSIGNMENT_OR_MATERIALIZATION")
        self.assertEqual(result["effects"], {
            "actors_assigned": 0, "workers_started": 0,
            "permissions_granted": 0, "external_mutations": 0,
        })

        identifiers, ranks, tuples = set(), set(), set()
        for item in result["preview"]:
            self.assertEqual(item["assessment"], "UNASSESSED")
            self.assertEqual(set(item["facets"]), set(AXIS_NAMES))
            for name, value in item["facets"].items():
                self.assertIn(value, selected[name])
            self.assertIs(type(item["filtered_rank"]), int)
            self.assertGreaterEqual(item["filtered_rank"], 0)
            self.assertLess(item["filtered_rank"], count)
            self.assertIsInstance(item["configuration_id"], str)
            self.assertNotIn(item["configuration_id"], identifiers)
            self.assertNotIn(item["filtered_rank"], ranks)
            signature = tuple(item["facets"][name] for name in AXIS_NAMES)
            self.assertNotIn(signature, tuples)
            identifiers.add(item["configuration_id"])
            ranks.add(item["filtered_rank"])
            tuples.add(signature)
        return result

    def test_current_source_bindings_and_independently_derived_counts(self):
        result = self.checked_preview()
        actual_hashes = tuple(binding["sha256"] for binding in result["source_bindings"])
        if actual_hashes == PINNED_SHA256:
            # Snapshot assertion applies only to these exact source bytes.
            self.assertEqual(tuple(result["axis_counts"][name] for name in AXIS_NAMES), (12, 19, 10, 12, 21, 11))
            self.assertEqual(result["raw_configuration_count"], 6_320_160)

    def test_exact_filters_reduce_product_and_preserve_raw_count(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, fixture_documents())
            unfiltered = self.checked_preview(root)
            one = self.checked_preview(root, {"domain": "domain-1"})
            two = self.checked_preview(root, {"domain": "domain-1", "morphology": "morphology-0"})
            self.assertEqual([result["filtered_configuration_count"] for result in (unfiltered, one, two)], [64, 32, 16])
            self.assertEqual({result["raw_configuration_count"] for result in (unfiltered, one, two)}, {64})

    def test_fully_filtered_current_sources_have_one_unique_configuration(self):
        filters = {name: values[0] for name, values in independent_axes(source_bytes(ROOT)).items()}
        result = self.checked_preview(filters=filters, limit=100)
        self.assertEqual(result["filtered_configuration_count"], 1)
        self.assertEqual(result["sample_count"], 1)
        self.assertEqual(result["preview"][0]["facets"], filters)
        self.assertEqual(result["preview"][0]["filtered_rank"], 0)

    def test_filter_order_does_not_change_preview(self):
        axes = independent_axes(source_bytes(ROOT))
        expressions = [f"{name}={axes[name][0]}" for name in ("domain", "operational_role", "morphology")]
        forward = PREVIEW.parse_filters(expressions)
        backward = PREVIEW.parse_filters(list(reversed(expressions)))
        self.assertEqual(self.checked_preview(filters=forward, limit=100, seed="order"),
                         self.checked_preview(filters=backward, limit=100, seed="order"))

    def test_filter_parser_rejects_incomplete_expressions(self):
        for expression in ("", "domain", "=value", "domain=", "="):
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                PREVIEW.parse_filters([expression])

    def test_filter_parser_rejects_duplicate_axis_even_same_value(self):
        for expressions in (["domain=a", "domain=a"], ["domain=a", "domain=b"]):
            with self.subTest(expressions=expressions), self.assertRaises(ValueError):
                PREVIEW.parse_filters(expressions)

    def test_unknown_and_nonexact_filter_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, fixture_documents())
            for filters in ({"unknown_axis": "role-0"}, {"domain": "missing"},
                            {"domain": "DOMAIN-0"}, {"domain": " domain-0"},
                            {"domain": "domain-0 "}, {"domain": ""},
                            {"domain": None}, {"domain": 0}, {"domain": ["domain-0"]}):
                with self.subTest(filters=filters), self.assertRaises(ValueError):
                    PREVIEW.build_preview(root, filters)

    def test_nonmapping_filter_inputs_are_rejected(self):
        for filters in ([], (), "domain=x", 0, False):
            with self.subTest(filters=filters), self.assertRaises(ValueError):
                PREVIEW.build_preview(ROOT, filters)

    def test_limit_100_is_allowed_and_typed_out_of_bounds_values_fail(self):
        self.checked_preview(limit=100)
        for limit in (-1, 101, True, False, 1.0, 100.0, "1", None):
            with self.subTest(limit=repr(limit)), self.assertRaises(ValueError):
                PREVIEW.build_preview(ROOT, limit=limit)

    def test_zero_limit_retains_counts_without_decoding(self):
        with patch.object(PREVIEW, "decode_rank", wraps=PREVIEW.decode_rank) as decoder:
            result = self.checked_preview(limit=0)
        decoder.assert_not_called()
        self.assertEqual(result["preview"], [])
        self.assertGreater(result["raw_configuration_count"], 0)

    def test_nonstring_seed_is_rejected(self):
        for seed in (None, 0, False, [], {}):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                PREVIEW.build_preview(ROOT, seed=seed)

    def test_identical_inputs_and_string_seed_repeat_exactly(self):
        for seed in ("0", "", "α/研究/2026-10-22"):
            with self.subTest(seed=seed):
                first = self.checked_preview(limit=100, seed=seed)
                second = self.checked_preview(limit=100, seed=seed)
                self.assertEqual(first, second)

    def test_decoded_work_is_bounded_by_sample_limit(self):
        # This observes the bounded decoder path; source review establishes that
        # no hidden Cartesian-product collection is constructed elsewhere.
        with patch.object(PREVIEW, "decode_rank", wraps=PREVIEW.decode_rank) as decoder:
            result = self.checked_preview(limit=100, seed="bounded")
        self.assertEqual(decoder.call_count, result["sample_count"])

    def test_small_product_exhaustion_matches_independent_cartesian_grid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, fixture_documents())
            axes = independent_axes(source_bytes(root))
            expected = set(itertools.product(*(axes[name] for name in AXIS_NAMES)))
            result = self.checked_preview(root, limit=100, seed="exhaust-small-grid")
            actual = {tuple(item["facets"][name] for name in AXIS_NAMES) for item in result["preview"]}
            self.assertEqual(len(expected), 64)
            self.assertEqual(actual, expected)
            self.assertEqual({item["filtered_rank"] for item in result["preview"]}, set(range(64)))

    def test_singleton_registries_sample_once_even_at_limit_100(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, fixture_documents(width=1))
            result = self.checked_preview(root, limit=100)
            self.assertEqual(result["raw_configuration_count"], 1)
            self.assertEqual(result["sample_count"], 1)

    def test_valid_registry_growth_remains_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            documents = fixture_documents()
            write_fixture(root, documents)
            before = self.checked_preview(root, limit=100)
            documents[SOURCE_PATHS[1]]["morphologies"].append("morphology-new")
            write_fixture(root, documents)
            after = self.checked_preview(root, limit=100)
            self.assertEqual(before["raw_configuration_count"], 64)
            self.assertEqual(after["raw_configuration_count"], 96)
            self.assertEqual(after["sample_count"], 96)
            self.assertTrue(any(item["facets"]["morphology"] == "morphology-new" for item in after["preview"]))

    def test_each_axis_rejects_duplicate_registry_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for axis in AXIS_NAMES:
                with self.subTest(axis=axis):
                    documents = fixture_documents()
                    set_axis(documents, axis, ["same", "same"])
                    write_fixture(root, documents)
                    with self.assertRaises(ValueError):
                        PREVIEW.load_axes(root)

    def test_each_axis_rejects_empty_blank_and_nonstring_registry_values(self):
        bad_values = ([], [""], [" \t\n"], [0], [False], [None], ["valid", 1], [["nested"]], [{"name": "value"}])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for axis in AXIS_NAMES:
                for values in bad_values:
                    with self.subTest(axis=axis, values=values):
                        documents = fixture_documents()
                        set_axis(documents, axis, values)
                        write_fixture(root, documents)
                        with self.assertRaises(ValueError):
                            PREVIEW.load_axes(root)

    def test_direct_axis_fields_require_arrays(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for axis in (name for name in AXIS_NAMES if name != "domain"):
                for values in ("value", {"value": True}, 0, None, False):
                    with self.subTest(axis=axis, values=values):
                        documents = fixture_documents()
                        set_axis(documents, axis, values)
                        write_fixture(root, documents)
                        with self.assertRaises(ValueError):
                            PREVIEW.load_axes(root)

    def test_domain_rows_require_exact_three_item_array_shape(self):
        bad_rows = ("domain-0", {"domain": "domain-0"}, None,
                    ["domain-0"], [["domain-0"]], [["domain-0", []]],
                    [["domain-0", [], "TEST", "extra"]],
                    [{"domain": "domain-0", "repos": [], "mode": "TEST"}])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for rows in bad_rows:
                with self.subTest(rows=rows):
                    documents = fixture_documents()
                    documents[SOURCE_PATHS[2]]["domains"] = rows
                    write_fixture(root, documents)
                    with self.assertRaises(ValueError):
                        PREVIEW.load_axes(root)

    def test_missing_source_required_field_or_malformed_json_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in SOURCE_PATHS:
                with self.subTest(source=name):
                    write_fixture(root, fixture_documents())
                    (root / name).unlink()
                    with self.assertRaises(OSError):
                        PREVIEW.load_axes(root)
                    write_fixture(root, fixture_documents())
                    (root / name).write_text("{", encoding="utf-8")
                    with self.assertRaises(ValueError):
                        PREVIEW.load_axes(root)
                    write_fixture(root, fixture_documents())
                    (root / name).write_text("{}", encoding="utf-8")
                    with self.assertRaises(KeyError):
                        PREVIEW.load_axes(root)

    def test_each_source_byte_change_rebinds_identical_facets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for changed in SOURCE_PATHS:
                with self.subTest(source=changed):
                    write_fixture(root, fixture_documents())
                    filters = {name: values[0] for name, values in independent_axes(source_bytes(root)).items()}
                    before = self.checked_preview(root, filters, limit=100)
                    path = root / changed
                    path.write_bytes(path.read_bytes() + b" \n")
                    after = self.checked_preview(root, filters, limit=100)
                    self.assertEqual(before["axis_counts"], after["axis_counts"])
                    self.assertEqual(before["preview"][0]["facets"], after["preview"][0]["facets"])
                    self.assertNotEqual(before["preview"][0]["configuration_id"], after["preview"][0]["configuration_id"])
                    old_bindings = {binding["path"]: binding for binding in before["source_bindings"]}
                    new_bindings = {binding["path"]: binding for binding in after["source_bindings"]}
                    for name in SOURCE_PATHS:
                        if name == changed:
                            self.assertNotEqual(old_bindings[name]["sha256"], new_bindings[name]["sha256"])
                            self.assertEqual(new_bindings[name]["bytes"], old_bindings[name]["bytes"] + 2)
                        else:
                            self.assertEqual(old_bindings[name], new_bindings[name])

    def test_preview_does_not_create_remove_or_modify_input_tree_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root, fixture_documents())
            (root / "unrelated.txt").write_text("keep this sentinel\n", encoding="utf-8")
            before = tree_snapshot(root)
            self.checked_preview(root, limit=0)
            self.checked_preview(root, {"domain": "domain-0"}, limit=100, seed="immutable")
            with self.assertRaises(ValueError):
                PREVIEW.build_preview(root, {"domain": "absent"})
            self.assertEqual(tree_snapshot(root), before)


if __name__ == "__main__":
    unittest.main()
