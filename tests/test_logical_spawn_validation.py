"""Required-core planner boundary regressions, using only the standard library.

This deliberately tests a planner core profile, not full CoEvoDelta schema
conformance, source freshness, source truth, or live receiver continuity.
Synthetic identifiers and dates below are fixed test data.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "logical_spawn_validation_candidate", ROOT / "scripts/CoLogicalSpawnPlanner.py")
if SPEC is None or SPEC.loader is None:
    raise ImportError("Local planner cannot be loaded")
PLANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLANNER)
DELTA_SCHEMA = json.loads((ROOT / "schemas/coevo-delta-v0.1.schema.json").read_text())
CONTRACT_SCHEMA = json.loads((ROOT / "schemas/cospawn-contract-v0.1.schema.json").read_text())
ARRAY_FIELDS = tuple(k for k in DELTA_SCHEMA["required"]
                     if DELTA_SCHEMA["properties"][k].get("type") == "array")
SCALAR_FIELDS = tuple(k for k in DELTA_SCHEMA["required"] if k not in ARRAY_FIELDS)
ENUMS = {k: DELTA_SCHEMA["properties"][k]["enum"] for k in DELTA_SCHEMA["required"]
         if "enum" in DELTA_SCHEMA["properties"][k]}
LANES = {"domains": [["CoSession+", ["CoCivium"], "LOGICAL_ONLY"]]}
REPOS = {"repositories": [{"repo": "CoCivium/CoCivium", "visibility": "public"}]}


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(encoded(value)).hexdigest().upper()


def delta(identifier: object = "valid-a", **changes: object) -> dict:
    row = {
        "delta_id": identifier,
        "session_id": "synthetic-validation-session",
        "observed_at": "2026-10-22T18:50:00Z",
        "domain": ["CoSession+"],
        "subject": "synthetic-receiver-status",
        "relation": "HAS_STATUS",
        "epistemic_class": "OBSERVED",
        "source_refs": ["fixture:source"],
        "target_surfaces": ["CoCivium"],
        "mutation_class": "PROPOSE",
        "authority_ceiling": "ADVISORY_ONLY",
        "confidentiality": "PUBLIC",
        "next_receiver": "synthetic-review-receiver",
    }
    row.update(deepcopy(changes))
    return row


class LogicalSpawnValidationTests(unittest.TestCase):
    def assert_contract_schema(self, contract: dict) -> None:
        """Check every constraint used by this exact, simple CoSpawn schema."""
        props = CONTRACT_SCHEMA["properties"]
        self.assertIsInstance(contract, dict)
        self.assertTrue(set(CONTRACT_SCHEMA["required"]).issubset(contract))
        self.assertFalse(set(contract) - set(props))
        type_checks = {
            "string": lambda x: isinstance(x, str),
            "array": lambda x: isinstance(x, list),
            "object": lambda x: isinstance(x, dict),
            "null": lambda x: x is None,
        }
        for key, value in contract.items():
            spec = props[key]
            self.assertTrue(set(spec).issubset({"type", "enum", "minLength", "items"}),
                            f"Update schema assertion for new constraints on {key}")
            if "type" in spec:
                allowed = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
                self.assertTrue(any(type_checks[name](value) for name in allowed), (key, value))
            if "enum" in spec:
                self.assertIn(value, spec["enum"], key)
            if "minLength" in spec:
                self.assertGreaterEqual(len(value), spec["minLength"], key)
            if "items" in spec:
                self.assertEqual(spec["items"], {"type": "string"})
                self.assertTrue(all(isinstance(item, str) for item in value), key)

    def plan(self, rows: list[dict], lanes: dict | None = None,
             repos: dict | None = None) -> dict:
        before = encoded(rows)
        before_hash = hashlib.sha256(before).hexdigest()
        result = PLANNER.compile_plan(rows, deepcopy(LANES if lanes is None else lanes),
                                      deepcopy(REPOS if repos is None else repos))
        self.assertEqual(encoded(rows), before, "Planner changed a raw input")
        self.assertEqual(hashlib.sha256(encoded(rows)).hexdigest(), before_hash)
        self.assertTrue(all(value == 0 for value in result["effects"].values()))
        held_refs = set()
        for contract in result["contracts"]:
            self.assert_contract_schema(contract)
            self.assertEqual(contract["budget"]["max_live_embodiments"], 0)
            self.assertEqual(contract["budget"]["max_effectful_mutations"], 0)
            self.assertEqual(contract["lease"]["effect_lease"], "NONE")
            if contract["materialization_state"] == "BLOCKED":
                held_refs.update(contract["provenance"])
                self.assertIsInstance(contract["uncertainty"], str)
                self.assertTrue(contract["uncertainty"].strip())
        for donation in result["donations"]:
            self.assertNotIn(donation["donor_delta_id"], held_refs)
            self.assertNotIn(donation["receiver_delta_id"], held_refs)
        return result

    def only_contract(self, result: dict) -> dict:
        self.assertEqual(len(result["contracts"]), 1)
        return result["contracts"][0]

    def contract_for(self, result: dict, reference: str) -> dict:
        matches = [c for c in result["contracts"] if reference in c["provenance"]]
        self.assertEqual(len(matches), 1, reference)
        return matches[0]

    def assert_blocked(self, result: dict, count: int = 1) -> None:
        self.assertEqual(len(result["contracts"]), count)
        self.assertTrue(all(c["materialization_state"] == "BLOCKED" for c in result["contracts"]))
        self.assertEqual(result["coverage"]["blocked_contracts"], count)
        self.assertEqual(result["donations"], [])
        self.assertEqual(result["coverage"]["dedupe_donations"], 0)

    def test_unextended_baseline_covers_exact_required_schema_fields(self) -> None:
        row = delta()
        self.assertEqual(set(row), set(DELTA_SCHEMA["required"]))
        self.assertEqual(set(ARRAY_FIELDS), {"domain", "source_refs", "target_surfaces"})
        self.assertEqual(self.only_contract(self.plan([row]))["materialization_state"], "LOGICAL_ONLY")

    def test_all_declared_core_enum_values_remain_accepted(self) -> None:
        for field, choices in ENUMS.items():
            for value in choices:
                with self.subTest(field=field, value=value):
                    # Avoid a separate confidentiality-to-public-target collision.
                    row = delta(**{field: value, "target_surfaces": []})
                    expected = "SHADOW" if row["mutation_class"] == "EFFECT_GATED" else "LOGICAL_ONLY"
                    self.assertEqual(self.only_contract(self.plan([row]))["materialization_state"], expected)

    def test_required_scalar_null_blank_and_nonstring_values_are_held(self) -> None:
        invalid = (None, "", " \t\n", False, 0, [], {})
        for field in SCALAR_FIELDS:
            for value in invalid:
                with self.subTest(field=field, value=value):
                    self.assert_blocked(self.plan([delta(**{field: value})]))

    def test_each_missing_required_field_is_held_without_exception(self) -> None:
        for field in DELTA_SCHEMA["required"]:
            with self.subTest(field=field):
                row = delta()
                del row[field]
                self.assert_blocked(self.plan([row]))

    def test_array_scalars_and_objects_are_held_without_exception(self) -> None:
        invalid = (None, False, True, 0, 7, 0.5, "", "CoSession+", {"unexpected": "value"})
        for field in ARRAY_FIELDS:
            for value in invalid:
                with self.subTest(field=field, value=value):
                    self.assert_blocked(self.plan([delta(**{field: value})]))

    def test_nonstring_array_items_are_held_without_exception(self) -> None:
        for field in ARRAY_FIELDS:
            for value in (None, False, 0, {}, ["nested"]):
                with self.subTest(field=field, value=value):
                    valid_item = delta()[field][0]
                    self.assert_blocked(self.plan([delta(**{field: [valid_item, value]})]))

    def test_empty_domain_and_unregistered_domain_are_held(self) -> None:
        for value in ([], [""], ["unknown-domain"]):
            with self.subTest(value=value):
                self.assert_blocked(self.plan([delta(domain=value)]))

    def test_empty_and_blank_item_evidence_target_arrays_remain_legal(self) -> None:
        for field in ("source_refs", "target_surfaces"):
            for value in ([], [""], [" ", "\t"]):
                with self.subTest(field=field, value=value):
                    row = delta(**{field: value})
                    contract = self.only_contract(self.plan([row]))
                    self.assertEqual(contract["materialization_state"], "LOGICAL_ONLY")
                    if field == "source_refs":
                        self.assertEqual(contract["input_bindings"], sorted(set(value)))

    def test_unknown_and_wrong_case_enum_strings_are_held(self) -> None:
        for field, values in ENUMS.items():
            for value in ("NOT_A_DECLARED_VALUE", values[0].lower()):
                with self.subTest(field=field, value=value):
                    self.assert_blocked(self.plan([delta(**{field: value})]))

    def test_supported_timestamp_forms_preserve_exact_raw_text(self) -> None:
        valid = (
            "2026-10-22T18:50:00Z",
            "2026-10-22t18:50:00z",
            "2026-10-22T18:50:00.1Z",
            "2026-10-22t18:50:00.123456789+05:30",
            "2026-10-22T18:50:00-07:00",
            "2026-10-22T18:50:00-00:00",
            "2026-10-22T18:50:00+23:59",
            "2024-02-29T00:00:00Z",
        )
        for value in valid:
            with self.subTest(value=value):
                contract = self.only_contract(self.plan([delta(observed_at=value)]))
                self.assertEqual(contract["materialization_state"], "LOGICAL_ONLY")
                self.assertEqual(contract["currentness"], value)

    def test_invalid_timestamp_shapes_calendars_and_offsets_are_held(self) -> None:
        invalid = (
            "not-a-date", "2026-10-22", "2026-10-22T18:50:00",
            "2026-10-22 18:50:00Z", "2026-10-22T18:50Z",
            "2026-10-22T18:50:00+0000", "2026-10-22T18:50:00+00",
            "2026-10-22T18:50:00+24:00", "2026-10-22T18:50:00+01:60",
            "2026-10-22T18:50:00+01:00:30", "2026-10-22T24:00:00Z",
            "2026-10-22T18:60:00Z", "2026-10-22T23:59:60Z",
            "2026-10-22T18:50:00.Z", "2026-10-22T18:50:00.1e3Z",
            "2026-02-29T00:00:00Z", "2026-04-31T00:00:00Z",
            "2026-13-01T00:00:00Z", "0000-01-01T00:00:00Z",
            " 2026-10-22T18:50:00Z", "2026-10-22T18:50:00Z ",
        )
        for value in invalid:
            with self.subTest(value=value):
                result = self.plan([delta(observed_at=value)])
                self.assert_blocked(result)
                self.assertTrue(self.only_contract(result)["currentness"].startswith("INVALID_"))

    def test_invalid_scalar_output_fallbacks_are_explicit_and_schema_valid(self) -> None:
        fields = {
            "session_id": ("parent_identity", None),
            "authority_ceiling": ("authority_ceiling", False),
            "next_receiver": ("receiver", {}),
            "observed_at": ("currentness", "not-a-date"),
        }
        for field, (output_field, value) in fields.items():
            with self.subTest(field=field):
                result = self.plan([delta(**{field: value})])
                self.assert_blocked(result)
                fallback = self.only_contract(result)[output_field]
                self.assertTrue(fallback.startswith("INVALID_"), fallback)
                self.assertNotEqual(fallback, str(value))
        result = self.plan([delta(subject=None)])
        self.assert_blocked(result)
        self.assertIn("INVALID_", self.only_contract(result)["scope"])
        for value in (None, {}, False, "public", "NOT_CLASSIFIED"):
            with self.subTest(confidentiality=value):
                result = self.plan([delta(confidentiality=value)])
                self.assert_blocked(result)
                self.assertEqual(self.only_contract(result)["confidentiality"], "UNKNOWN")
        result = self.plan([delta(mutation_class={"unexpected": "object"})])
        self.assert_blocked(result)
        self.assertEqual(self.only_contract(result)["effect_classes"], [])

    def test_invalid_ids_do_not_alias_valid_text_ids_or_body_dedupe(self) -> None:
        for bad_id, text_id in ((False, "False"), (0, "0"), (None, "None")):
            with self.subTest(bad_id=bad_id):
                bad, good = delta(bad_id), delta(text_id)
                result = self.plan([bad, good])
                self.assertEqual(len(result["contracts"]), 2)
                self.assertEqual(self.contract_for(result, text_id)["materialization_state"], "LOGICAL_ONLY")
                diagnostic_refs = set(result["validation"]) - {text_id}
                self.assertEqual(len(diagnostic_refs), 1)
                reference = diagnostic_refs.pop()
                self.assertNotEqual(reference, str(bad_id))
                self.assertTrue(reference.endswith(digest(bad)), reference)
                held = self.contract_for(result, reference)
                self.assertEqual(held["materialization_state"], "BLOCKED")
                self.assertEqual(held["recovery_pointer"], reference)
                self.assertIn(digest(bad), held["idempotency_key"])
                self.assertEqual(result["donations"], [])

    def test_distinct_invalid_id_payloads_keep_distinct_raw_hash_references(self) -> None:
        rows = [delta(value) for value in (False, 0, None, [], {}, "", " ")]
        missing = delta()
        del missing["delta_id"]
        rows.append(missing)
        result = self.plan(rows)
        self.assert_blocked(result, len(rows))
        refs = set(result["validation"])
        self.assertEqual(len(refs), len(rows))
        self.assertEqual(len({c["idempotency_key"] for c in result["contracts"]}), len(rows))
        for row in rows:
            self.assertEqual(sum(ref.endswith(digest(row)) for ref in refs), 1)

    def test_generated_id_reference_cannot_shadow_caller_owned_identifiers(self) -> None:
        bad = delta(False)
        first = self.plan([bad])
        original_reference = self.only_contract(first)["recovery_pointer"]
        caller_ids = {original_reference, "_" + original_reference}
        rows = [bad] + [delta(identifier) for identifier in sorted(caller_ids)]
        result = self.plan(rows)
        held = [c for c in result["contracts"] if c["materialization_state"] == "BLOCKED"]
        self.assertEqual(len(held), 1)
        diagnostic = held[0]["recovery_pointer"]
        self.assertNotIn(diagnostic, caller_ids)
        self.assertTrue(diagnostic.endswith(digest(bad)))
        self.assertEqual(set(result["validation"]) - caller_ids, {diagnostic})
        for identifier in caller_ids:
            self.assertEqual(self.contract_for(result, identifier)["materialization_state"], "LOGICAL_ONLY")
        self.assertEqual(encoded(self.plan(list(reversed(rows)))), encoded(result))

    def test_identical_invalid_row_repetition_does_not_create_donation(self) -> None:
        bad = delta(False)
        result = self.plan([bad, deepcopy(bad)])
        self.assert_blocked(result)
        self.assertEqual(result["coverage"]["input_deltas"], 2)
        self.assertEqual(len(result["validation"]), 1)

    def test_malformed_array_reused_id_holds_valid_and_fresh_id_siblings(self) -> None:
        rows = [delta("shared-id", source_refs=42), delta("shared-id"), delta("fresh-id")]
        result = self.plan(rows)
        self.assert_blocked(result, 2)
        self.assertTrue(result["validation"]["shared-id"])
        self.assertEqual(self.contract_for(result, "fresh-id")["materialization_state"], "BLOCKED")

    def test_actual_body_ambiguity_can_hold_an_otherwise_valid_id(self) -> None:
        result = self.plan([delta(False, object="OFFLINE"), delta("valid-a", object="ONLINE")])
        self.assert_blocked(result, 2)

    def test_unrelated_valid_rows_stay_viable_among_malformed_rows(self) -> None:
        rows = [
            delta("bad-array", subject="synthetic-array", target_surfaces=7),
            delta("bad-time", subject="synthetic-time", observed_at="not-a-date"),
            delta("bad-enum", subject="synthetic-enum", confidentiality="public"),
            delta("good", subject="unrelated-synthetic-good"),
        ]
        result = self.plan(rows)
        self.assertEqual(len(result["contracts"]), 4)
        self.assertEqual(result["coverage"]["blocked_contracts"], 3)
        self.assertEqual(self.contract_for(result, "good")["materialization_state"], "LOGICAL_ONLY")

    def test_raw_array_errors_do_not_collapse_after_safe_projection(self) -> None:
        rows = [delta(f"bad-{i}", source_refs=value)
                for i, value in enumerate((False, 0, None, ""))]
        result = self.plan(rows)
        self.assert_blocked(result, len(rows))
        self.assertEqual(len({c["idempotency_key"] for c in result["contracts"]}), len(rows))
        self.assertTrue(all(c["input_bindings"] == [] for c in result["contracts"]))

    def test_extensions_are_preserved_without_claiming_full_schema_validation(self) -> None:
        base = delta()
        extended = delta(qualifiers={"nested": {"source_refs": [False, 0]}},
                         observed_base_ref="fixture:base", unknown_extension={"kind": "future"})
        plain_plan = self.plan([base])
        extended_plan = self.plan([extended])
        self.assertEqual(self.only_contract(extended_plan)["materialization_state"], "LOGICAL_ONLY")
        self.assertNotEqual(self.only_contract(plain_plan)["idempotency_key"],
                            self.only_contract(extended_plan)["idempotency_key"])
        twin = deepcopy(extended)
        twin["delta_id"] = "valid-b"
        result = self.plan([extended, twin])
        self.assertEqual(len(result["contracts"]), 1)
        self.assertEqual(len(result["donations"]), 1)

    def test_legacy_effect_gated_core_remains_shadow_without_union_only_fields(self) -> None:
        row = delta(mutation_class="EFFECT_GATED")
        self.assertNotIn("effect_gate", row)
        self.assertNotIn("effect_classes", row)
        contract = self.only_contract(self.plan([row]))
        self.assertEqual(contract["materialization_state"], "SHADOW")
        self.assertEqual(contract["role"], "VERIFIER")
        self.assertEqual(contract["lease"], {"mode": "SHADOW", "effect_lease": "NONE"})

    def test_private_public_target_collision_still_blocks(self) -> None:
        self.assert_blocked(self.plan([delta(confidentiality="PRIVATE")]))

    def test_mixed_input_permutations_are_deterministic(self) -> None:
        rows = [
            delta(False, source_refs=42),
            delta("False"),
            delta(0, subject="different-synthetic-id"),
            delta("good", subject="unrelated-synthetic-good"),
        ]
        baseline = self.plan(rows)
        self.assertEqual(baseline["coverage"]["blocked_contracts"], 2)
        self.assertEqual(self.contract_for(baseline, "False")["materialization_state"], "LOGICAL_ONLY")
        self.assertEqual(self.contract_for(baseline, "good")["materialization_state"], "LOGICAL_ONLY")
        serialized = json.dumps(baseline, indent=2, ensure_ascii=False)
        for order in permutations(range(len(rows))):
            with self.subTest(order=order):
                result = self.plan([rows[index] for index in order])
                self.assertEqual(json.dumps(result, indent=2, ensure_ascii=False), serialized)

    def test_pinned_r2_fixture_preserves_prechange_output_bytes_and_hashes(self) -> None:
        # Observed by running the pinned 4d3d3ba7 planner, Git blob
        # df95ed0b5e7ba8dcf973e42d2ff21cd47c8a1948, before this validation repair.
        fixture = json.loads((ROOT / "docs/Operations/fixtures/coevo-logical-spawn-r2-input.json").read_text())
        rows = fixture["deltas"] if isinstance(fixture, dict) else fixture
        lanes = json.loads((ROOT / "ai/evolution-lanes.json").read_text())
        repos = json.loads((ROOT / "ai/repo-role-map.json").read_text())
        result = self.plan(rows, lanes, repos)
        output = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        self.assertEqual(hashlib.sha256(output).hexdigest(),
                         "7351d52903fefb5e844c7337fa7b76a37f27ba17f3f8aaa5ae3bfe0796d67a21")


if __name__ == "__main__":
    unittest.main()
