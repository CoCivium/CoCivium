"""Bounded planner identity regressions; synthetic dates are fixed inputs.

Passing these checks does not establish source freshness, receiver pickup,
live-session liveness, authority, or general continuity.
Run with Python's standard library only: python -B <this-file> -v
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
CANDIDATE_ROOT = Path(__file__).resolve().parents[1]
PLANNER_PATH = CANDIDATE_ROOT / "scripts" / "CoLogicalSpawnPlanner.py"
SPEC = importlib.util.spec_from_file_location("logical_spawn_identity_candidate", PLANNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load local planner: {PLANNER_PATH}")
PLANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLANNER)

LANES = {"domains": [
    ["CoSession+", ["CoCivium"], "LOGICAL_ONLY"],
    ["CoTheoryAll+", ["CoCivium"], "LOGICAL_ONLY"],
]}
REPOSITORIES = {"repositories": [
    {"repo": "CoCivium/CoCivium", "visibility": "public"},
    {"repo": "CoCivium/CoAura", "visibility": "public"},
]}
ZERO_EFFECT_FIELDS = {
    "live_workers_started", "provider_sessions_created", "provider_titles_mutated",
    "provider_tabs_closed", "repo_mutations_executed", "authority_changes",
}


def delta(delta_id: str = "delta-a", **changes: object) -> dict:
    value = {
        "delta_id": delta_id,
        "session_id": "synthetic-session-a",
        "observed_at": "2026-10-22T12:00:00Z",
        "domain": ["CoSession+"],
        "subject": "synthetic-receiver-a",
        "relation": "HAS_STATUS",
        "object": "ONLINE",
        "qualifiers": {"scope": "synthetic-fixture"},
        "source_head": "a" * 40,
        "epistemic_class": "PLANNED",
        "source_refs": ["fixture:receiver-state-a"],
        "target_surfaces": ["CoCivium"],
        "mutation_class": "PROPOSE",
        "authority_ceiling": "ADVISORY_ONLY",
        "confidentiality": "PUBLIC",
        "next_receiver": "synthetic-receiver-review-a",
        "confidence": 0.8,
        "tests": ["synthetic-readability-check"],
        "risks": ["unverified source freshness"],
        "wake_conditions": ["synthetic-review-ready"],
    }
    value.update(deepcopy(changes))
    return value


class LogicalSpawnIdentityTests(unittest.TestCase):
    def plan(self, rows: list[dict], lanes: dict | None = None,
             repositories: dict | None = None) -> dict:
        result = PLANNER.compile_plan(
            deepcopy(rows), deepcopy(LANES if lanes is None else lanes),
            deepcopy(REPOSITORIES if repositories is None else repositories),
        )
        self.assertTrue(ZERO_EFFECT_FIELDS.issubset(result["effects"]))
        self.assertTrue(all(v == 0 for v in result["effects"].values()), result["effects"])
        for contract in result["contracts"]:
            self.assertEqual(contract["budget"]["max_live_embodiments"], 0)
            self.assertEqual(contract["budget"]["max_effectful_mutations"], 0)
            self.assertEqual(contract["lease"]["effect_lease"], "NONE")
        return result

    def contract_for(self, plan: dict, delta_id: str) -> dict:
        matches = [c for c in plan["contracts"] if delta_id in c["provenance"]]
        self.assertEqual(len(matches), 1, (delta_id, matches))
        return matches[0]

    def assert_pair_retained(self, first: dict, second: dict, state: str) -> dict:
        result = self.plan([first, second])
        self.assertEqual(result["coverage"]["logical_contracts"], 2)
        self.assertEqual(len(result["contracts"]), 2)
        self.assertEqual(result["coverage"]["dedupe_donations"], 0)
        self.assertEqual(result["donations"], [])
        self.assertEqual(len({c["spawn_id"] for c in result["contracts"]}), 2)
        self.assertEqual(len({c["idempotency_key"] for c in result["contracts"]}), 2)
        for row in (first, second):
            contract = self.contract_for(result, row["delta_id"])
            self.assertEqual(contract["materialization_state"], state)
            self.assertEqual(contract["parent_identity"], row["session_id"])
            self.assertEqual(contract["currentness"], row["observed_at"])
        return result

    def assert_held(self, result: dict, reason: str) -> None:
        self.assertEqual(result["coverage"]["blocked_contracts"], len(result["contracts"]))
        self.assertEqual(result["donations"], [])
        self.assertEqual(result["coverage"]["dedupe_donations"], 0)
        for contract in result["contracts"]:
            self.assertEqual(contract["materialization_state"], "BLOCKED")
            self.assertIsInstance(contract["uncertainty"], str)
            self.assertIn(reason, contract["uncertainty"])
            self.assertNotIn("PROVEN_CONTRADICTION", contract["uncertainty"].upper())

    def assert_ambiguity(self, result: dict) -> None:
        self.assert_held(result, "AMBIGUOUS")

    def test_exact_payloads_with_distinct_ids_donate_once(self) -> None:
        first, second = delta("delta-a"), delta("delta-b")
        result = self.plan([second, first])
        self.assertEqual(len(result["contracts"]), 1)
        self.assertEqual(result["coverage"]["dedupe_donations"], 1)
        self.assertEqual(len(result["donations"]), 1)
        contract = result["contracts"][0]
        self.assertEqual(set(contract["provenance"]), {"delta-a", "delta-b"})
        self.assertEqual(contract["materialization_state"], "LOGICAL_ONLY")
        self.assertEqual(contract["currentness"], first["observed_at"])
        self.assertEqual(contract["parent_identity"], first["session_id"])
        self.assertEqual(contract["input_bindings"], first["source_refs"])
        donation = result["donations"][0]
        self.assertEqual({donation["donor_delta_id"], donation["receiver_delta_id"]},
                         {"delta-a", "delta-b"})
        self.assertEqual(donation["relation"], "EQUIVALENT_DEDUPE_DONATION")

    def test_repeated_identical_ids_never_create_self_or_duplicate_donations(self) -> None:
        for ids, count in [
            (["delta-a", "delta-a", "delta-a"], 0),
            (["delta-a", "delta-b", "delta-a", "delta-b"], 1),
        ]:
            with self.subTest(ids=ids):
                result = self.plan([delta(identifier) for identifier in ids])
                self.assertEqual(len(result["contracts"]), 1)
                self.assertEqual(len(result["donations"]), count)
                self.assertEqual(set(result["contracts"][0]["provenance"]), set(ids))
                for donation in result["donations"]:
                    self.assertNotEqual(donation["donor_delta_id"], donation["receiver_delta_id"])

    def test_root_evidence_session_and_time_changes_are_retained_without_ambiguity(self) -> None:
        variations = {
            "session_id": "synthetic-session-b",
            "observed_at": "2026-10-22T12:00:01Z",
            "source_refs": ["fixture:receiver-state-b"],
            "confidence": 0.4,
            "tests": ["different-synthetic-check"],
            "risks": ["different-review-annotation"],
            "wake_conditions": ["different-synthetic-wake"],
        }
        for field, value in variations.items():
            with self.subTest(field=field):
                first, second = delta("delta-a"), delta("delta-b", **{field: value})
                result = self.assert_pair_retained(first, second, "LOGICAL_ONLY")
                self.assertTrue(all(c["uncertainty"] is None for c in result["contracts"]))
                for row in (first, second):
                    self.assertEqual(self.contract_for(result, row["delta_id"])["input_bindings"],
                                     row["source_refs"])

    def test_head_changes_only_inside_opaque_source_refs_do_not_claim_freshness_validation(self) -> None:
        first = delta("delta-a", source_refs=["fixture:commit:" + "a" * 40])
        second = delta("delta-b", source_refs=["fixture:commit:" + "b" * 40])
        result = self.assert_pair_retained(first, second, "LOGICAL_ONLY")
        for row in (first, second):
            self.assertEqual(self.contract_for(result, row["delta_id"])["input_bindings"],
                             row["source_refs"])

    def test_domain_and_target_order_changes_identity_but_not_conflict(self) -> None:
        first = delta("delta-a", domain=["CoSession+", "CoTheoryAll+"],
                      target_surfaces=["CoCivium", "CoAura"])
        second = deepcopy(first)
        second.update(delta_id="delta-b", domain=list(reversed(first["domain"])),
                      target_surfaces=list(reversed(first["target_surfaces"])))
        self.assert_pair_retained(first, second, "LOGICAL_ONLY")

    def test_online_offline_remain_two_held_ambiguous_candidates(self) -> None:
        result = self.assert_pair_retained(delta("delta-a", object="ONLINE"),
                                           delta("delta-b", object="OFFLINE"), "BLOCKED")
        self.assert_ambiguity(result)

    def test_critical_payload_changes_are_retained_and_held(self) -> None:
        changes = {
            "authority_ceiling": "PRIVATE_REVIEW_ONLY",
            "epistemic_class": "HYPOTHESIS",
            "mutation_class": "EFFECT_GATED",
            "next_receiver": "synthetic-receiver-review-b",
            "source_head": "b" * 40,
            "source_base": {"commit": "b" * 40},
            "qualifiers": {"scope": "different-synthetic-fixture"},
            "value": "OFFLINE",
            "typed_operation": {"op": "RELATE", "object": "OFFLINE"},
            "unrecognized_extension": {"future_policy": "different"},
        }
        for field, value in changes.items():
            with self.subTest(field=field):
                result = self.assert_pair_retained(delta("delta-a"),
                                                   delta("delta-b", **{field: value}), "BLOCKED")
                self.assert_ambiguity(result)

    def test_boolean_false_and_number_zero_remain_distinct(self) -> None:
        result = self.assert_pair_retained(delta("delta-a", object=False),
                                           delta("delta-b", object=0), "BLOCKED")
        self.assert_ambiguity(result)

    def test_missing_and_explicit_null_extension_remain_distinct(self) -> None:
        result = self.assert_pair_retained(delta("delta-a"),
                                           delta("delta-b", unrecognized_extension=None), "BLOCKED")
        self.assert_ambiguity(result)

    def test_root_exclusions_do_not_remove_nested_metadata(self) -> None:
        changes = {
            "delta_id": ("nested-a", "nested-b"),
            "session_id": ("nested-session-a", "nested-session-b"),
            "observed_at": ("2026-10-21T00:00:00Z", "2026-10-22T00:00:00Z"),
            "source_refs": (["nested:source-a"], ["nested:source-b"]),
            "confidence": (0.8, 0.2),
            "tests": (["nested-test-a"], ["nested-test-b"]),
            "risks": (["nested-risk-a"], ["nested-risk-b"]),
            "wake_conditions": (["nested-wake-a"], ["nested-wake-b"]),
        }
        for field, (before, after) in changes.items():
            with self.subTest(field=field):
                first = delta("delta-a", extension={"metadata": {field: before}})
                second = delta("delta-b", extension={"metadata": {field: after}})
                self.assert_ambiguity(self.assert_pair_retained(first, second, "BLOCKED"))

    def test_metadata_only_reuse_blocks_all_carriers_without_donation(self) -> None:
        first = delta("reused-id", source_refs=["fixture:evidence-a"])
        changed = delta("reused-id", source_refs=["fixture:evidence-b"])
        fresh = deepcopy(changed)
        fresh["delta_id"] = "fresh-sibling"
        result = self.plan([first, changed, fresh])
        self.assertEqual(len(result["contracts"]), 2)
        self.assert_held(result, "DELTA_ID_REUSED_WITH_DIFFERENT_PAYLOAD")
        self.assertTrue(all("reused-id" in c["provenance"] for c in result["contracts"]))
        self.assertEqual(self.contract_for(result, "fresh-sibling")["materialization_state"], "BLOCKED")

    def test_malformed_then_valid_reused_id_retains_validation_and_blocks_fresh_sibling(self) -> None:
        malformed = delta("reused-id")
        del malformed["source_refs"]
        result = self.plan([malformed, delta("reused-id"), delta("fresh-sibling")])
        self.assertEqual(len(result["contracts"]), 2)
        self.assert_held(result, "DELTA_ID_REUSED_WITH_DIFFERENT_PAYLOAD")
        self.assertIn("MISSING_source_refs", result["validation"]["reused-id"])
        for contract in result["contracts"]:
            self.assertIn("reused-id", contract["provenance"])
            self.assertIn("MISSING_source_refs", contract["uncertainty"])
        self.assertEqual(self.contract_for(result, "fresh-sibling")["materialization_state"], "BLOCKED")

    def test_reused_id_unions_multiple_validation_failures(self) -> None:
        missing_refs, missing_receiver = delta("reused-id"), delta("reused-id")
        del missing_refs["source_refs"]
        del missing_receiver["next_receiver"]
        result = self.plan([missing_refs, missing_receiver, delta("reused-id"), delta("fresh-sibling")])
        self.assertEqual(len(result["contracts"]), 3)
        self.assert_held(result, "DELTA_ID_REUSED_WITH_DIFFERENT_PAYLOAD")
        expected = {"MISSING_source_refs", "MISSING_next_receiver"}
        self.assertTrue(expected.issubset(result["validation"]["reused-id"]))
        for contract in result["contracts"]:
            for issue in expected:
                self.assertIn(issue, contract["uncertainty"])

    def test_input_permutations_produce_identical_serialized_output(self) -> None:
        malformed = delta("reused-id")
        del malformed["source_refs"]
        rows = [malformed, delta("reused-id"), delta("fresh-sibling"),
                delta("independent-id", subject="independent-synthetic-receiver")]
        baseline = json.dumps(self.plan(rows), indent=2, ensure_ascii=False)
        for order in permutations(range(len(rows))):
            with self.subTest(order=order):
                actual = json.dumps(self.plan([rows[index] for index in order]),
                                    indent=2, ensure_ascii=False)
                self.assertEqual(actual, baseline)

    def test_unrelated_claim_slots_do_not_block_each_other(self) -> None:
        self.assert_pair_retained(delta("delta-a", object="ONLINE"),
                                  delta("delta-b", subject="different-receiver", object="OFFLINE"),
                                  "LOGICAL_ONLY")

    def test_private_to_public_target_validation_remains_blocked(self) -> None:
        for confidentiality in ("PRIVATE", "RESTRICTED", "UNKNOWN"):
            with self.subTest(confidentiality=confidentiality):
                result = self.plan([delta(confidentiality=confidentiality)])
                self.assertEqual(len(result["contracts"]), 1)
                contract = result["contracts"][0]
                self.assertEqual(contract["materialization_state"], "BLOCKED")
                self.assertIn("CONFIDENTIALITY_PUBLIC_TARGET_COLLISION:CoCivium",
                              contract["uncertainty"])

    def test_blocked_exact_duplicates_never_emit_equivalence_donations(self) -> None:
        result = self.plan([delta("delta-a", confidentiality="PRIVATE"),
                            delta("delta-b", confidentiality="PRIVATE")])
        self.assertEqual(len(result["contracts"]), 1)
        self.assertEqual(result["contracts"][0]["materialization_state"], "BLOCKED")
        self.assertEqual(set(result["contracts"][0]["provenance"]), {"delta-a", "delta-b"})
        self.assertEqual(result["coverage"]["dedupe_donations"], 0)
        self.assertEqual(result["donations"], [])

    def test_valid_effect_gated_candidate_remains_read_only_shadow(self) -> None:
        result = self.plan([delta(mutation_class="EFFECT_GATED")])
        self.assertEqual(len(result["contracts"]), 1)
        contract = result["contracts"][0]
        self.assertEqual(contract["role"], "VERIFIER")
        self.assertEqual(contract["materialization_state"], "SHADOW")
        self.assertEqual(contract["lease"]["mode"], "SHADOW")
        self.assertEqual(result["coverage"]["shadow_contracts"], 1)

    def test_ambiguous_effect_gated_candidates_stay_blocked_instead_of_shadow(self) -> None:
        first = delta("delta-a", mutation_class="EFFECT_GATED", object="ONLINE")
        second = delta("delta-b", mutation_class="EFFECT_GATED", object="OFFLINE")
        result = self.assert_pair_retained(first, second, "BLOCKED")
        self.assert_ambiguity(result)
        self.assertEqual(result["coverage"]["shadow_contracts"], 0)

    def test_existing_r2_fixture_retains_three_candidates_and_private_gate(self) -> None:
        paths = {
            "fixture": CANDIDATE_ROOT / "docs/Operations/fixtures/coevo-logical-spawn-r2-input.json",
            "lanes": CANDIDATE_ROOT / "ai/evolution-lanes.json",
            "repositories": CANDIDATE_ROOT / "ai/repo-role-map.json",
        }
        for label, path in paths.items():
            self.assertTrue(path.is_file(), f"Missing pinned {label}: {path}")
        fixture = json.loads(paths["fixture"].read_text(encoding="utf-8"))
        rows = fixture["deltas"] if isinstance(fixture, dict) else fixture
        result = self.plan(rows, json.loads(paths["lanes"].read_text(encoding="utf-8")),
                           json.loads(paths["repositories"].read_text(encoding="utf-8")))
        self.assertEqual(result["coverage"]["input_deltas"], 3)
        self.assertEqual(result["coverage"]["logical_contracts"], 3)
        self.assertEqual(result["coverage"]["dedupe_donations"], 0)
        self.assertEqual(result["coverage"]["collision_groups"], 1)
        self.assertEqual(result["coverage"]["blocked_contracts"], 1)
        self.assertEqual(result["donations"], [])
        states = {"delta-ux-001": "LOGICAL_ONLY", "delta-ux-002": "LOGICAL_ONLY",
                  "delta-theory-private-001": "BLOCKED"}
        for row in rows:
            contract = self.contract_for(result, row["delta_id"])
            self.assertEqual(contract["materialization_state"], states[row["delta_id"]])
            self.assertEqual(contract["parent_identity"], row["session_id"])
            self.assertEqual(contract["currentness"], row["observed_at"])
            self.assertEqual(contract["input_bindings"], row["source_refs"])


if __name__ == "__main__":
    unittest.main()
