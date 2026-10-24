#!/usr/bin/env python3
"""Regression tests for the non-executing role-concern lens."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("role_concern_under_test", ROOT / "scripts" / "CoRoleConcernPanelR0.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ConcernLensTests(unittest.TestCase):
    def test_seven_unassigned_seats(self):
        result = MOD.build(ROOT, "Could this role model be wrong?")
        self.assertEqual(len(result["seats"]), 7)
        self.assertEqual(len({s["seat_id"] for s in result["seats"]}), 7)
        self.assertEqual(result["effects"], {
            "actors_assigned": 0, "workers_started": 0,
            "permissions_granted": 0, "messages_sent": 0})
        self.assertEqual(result["state"], "UNASSIGNED_PANEL_PLAN__NO_EXECUTION")

    def test_no_subjective_worry_assumption(self):
        result = MOD.build(ROOT, "Do roles have worries?")
        self.assertTrue(all(s["subjective_worry"] == "NOT_INFERRED" for s in result["seats"]))
        self.assertEqual(result["unassigned_passive_role_example"]["concern_kind_refs"], [])
        self.assertIn("NO_ROLE_MUST_HAVE_WORRIES", result["nonclaims"])

    def test_seats_point_to_shared_role_and_concern_definitions(self):
        result = MOD.build(ROOT, "Review a bounded claim")
        roles, concerns = result["role_definition_refs"], result["concern_definition_refs"]
        self.assertEqual(roles, sorted(set(roles)))
        self.assertEqual(concerns, sorted(set(concerns)))
        for seat in result["seats"]:
            self.assertIn(seat["role_ref"], roles)
            self.assertTrue(set(seat["concern_kind_refs"]).issubset(concerns))
            self.assertNotIn("role_definition", seat)
            self.assertNotIn("concern_definitions", seat)

    def test_source_pinning_and_determinism(self):
        first = MOD.build(ROOT, "Check uncertainty", 7)
        self.assertEqual(first, MOD.build(ROOT, "Check uncertainty", 7))
        self.assertNotEqual(first["panel_id"], MOD.build(ROOT, "Check a different question", 7)["panel_id"])
        for ref in first["source_bindings"]:
            content = (ROOT / ref["path"]).read_bytes()
            self.assertEqual(ref["sha256"], MOD.checksum(content))
            self.assertEqual(ref["bytes"], len(content))

    def test_zero_seats_is_not_zero_roles_claim(self):
        result = MOD.build(ROOT, "Check no assignment", 0)
        self.assertEqual(result["seats"], [])
        self.assertEqual(result["role_definition_refs"], [])
        self.assertIn("RAW_CONFIGURATIONS_NE_MEANINGFUL_ROLES", result["nonclaims"])

    def test_invalid_inputs_fail_closed(self):
        for question in ("", " ", "x" * 801):
            with self.subTest(question=question[:10]), self.assertRaises(ValueError):
                MOD.build(ROOT, question)
        for seats in (-1, 8, True, 2.5):
            with self.subTest(seats=seats), self.assertRaises(ValueError):
                MOD.build(ROOT, "Review", seats)

    def test_unknown_role_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for ref in MOD.build(ROOT, "source")["source_bindings"]:
                target = root / ref["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / ref["path"]).read_bytes())
            policy_path = root / MOD.POLICY_PATH
            policy = json.loads(policy_path.read_text())
            policy["panel"][0]["role"] = "NEW_ROLE_WITHOUT_SOURCE_CONTRACT"
            policy_path.write_text(json.dumps(policy))
            with self.assertRaisesRegex(ValueError, "unknown operational role"):
                MOD.build(root, "Review")

    def test_unsafe_policy_does_not_materialize(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in (MOD.POLICY_PATH, MOD.ROLE_PATH):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            policy_path = root / MOD.POLICY_PATH
            policy = json.loads(policy_path.read_text())
            policy["bounds"]["max_active_workers"] = 567
            policy_path.write_text(json.dumps(policy))
            with self.assertRaisesRegex(ValueError, "unacceptable effect budget"):
                MOD.build(root, "Review")

    def test_nonmaterial_lenses_do_not_become_facts(self):
        result = MOD.build(ROOT, "Review spiritual or nonmaterial interpretation")
        self.assertIn("SPIRITUAL_OR_CULTURAL", result["perspective_lenses"])
        self.assertIn("SPECULATIVE_NONPHYSICAL", result["perspective_lenses"])
        self.assertIn("PERSPECTIVE_NE_EMPIRICAL_EVIDENCE", result["nonclaims"])

    def test_no_source_mutation(self):
        before = {path: (ROOT / path).read_bytes() for path in (MOD.POLICY_PATH, MOD.ROLE_PATH)}
        MOD.build(ROOT, "Read-only proof", 7)
        after = {path: (ROOT / path).read_bytes() for path in (MOD.POLICY_PATH, MOD.ROLE_PATH)}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
