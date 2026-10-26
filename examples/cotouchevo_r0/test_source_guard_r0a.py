"""Scoped source identity, rights/retraction and receiver-sleep challenge tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from source_guard_r0a import (
    PUBLIC_DONOR, PUBLIC_DONOR_BLOB, LIMIT_BYTES,
    ZERO_EFFECTS, git_blob_sha1, preview,
)

ROOT = Path(__file__).resolve().parents[2]
FIX = json.loads((Path(__file__).parent / "fixture.json").read_text(encoding="utf-8"))
SYNTHETIC_OLDER = "0" * 40


def run(fixture=None, previous_blob=PUBLIC_DONOR_BLOB, kind="CONTENT",
        repo_root=ROOT, current_blob=PUBLIC_DONOR_BLOB):
    return preview(repo_root, FIX if fixture is None else fixture,
                   expected_current_blob=current_blob,
                   previous_blob=previous_blob, kind=kind)


class SourceBoundGuardTests(unittest.TestCase):
    def test_exact_public_donor_pin_is_current(self):
        raw = (ROOT / PUBLIC_DONOR).read_bytes()
        self.assertEqual(git_blob_sha1(raw), PUBLIC_DONOR_BLOB)

    def test_same_source_causes_no_cascade(self):
        r = run()
        self.assertEqual(r["source_identity"], "EXACT_PUBLIC_DONOR_BYTES_VERIFIED")
        self.assertEqual(r["state"], "NO_CONTENT_DELTA")
        self.assertEqual(r["shadow_proposals"], [])
        self.assertEqual(r["effects"], ZERO_EFFECTS)

    def test_scoped_synthetic_change_only(self):
        r = run(previous_blob=SYNTHETIC_OLDER)
        self.assertEqual(r["state"], "SIMULATED_CONTENT_DELTA_SHADOW_ONLY")
        self.assertEqual(len(r["shadow_proposals"]), 4)
        self.assertEqual(r["interested_receiver_count"], 3)
        self.assertEqual(r["sleeping_receiver_count"], 1)
        self.assertEqual(r["change_event_origin"], "NOT_AUTHENTICATED")
        self.assertEqual(r["previous_pin_authenticity"], "UNVERIFIED_SCENARIO_INPUT")
        self.assertEqual(r["effects"], ZERO_EFFECTS)

    def test_no_public_frontdoor_receiver_wake(self):
        r = run(previous_blob=SYNTHETIC_OLDER)
        self.assertNotIn("co-public", {x["receiver"] for x in r["shadow_proposals"]})

    def test_inspiration_is_review_only(self):
        r = run(previous_blob=SYNTHETIC_OLDER)
        self.assertTrue(any(x["relation"] == "INSPIRED_BY" for x in r["review_only"]))
        self.assertFalse(any(x["subject"] == "candidate:visual-look"
                             for x in r["shadow_proposals"]))

    def test_rights_change_with_unchanged_file_still_holds(self):
        r = run(kind="RIGHTS_CHANGE")
        self.assertEqual(r["state"], "HELD_RIGHTS_EVENT_AND_RECEIVER_AUTHORIZATION")
        self.assertEqual(r["shadow_proposals"], [])
        self.assertEqual(r["effects"], ZERO_EFFECTS)

    def test_retraction_may_exist_without_byte_difference(self):
        r = run(kind="RETRACTION")
        self.assertEqual(r["state"], "HELD_RIGHTS_EVENT_AND_RECEIVER_AUTHORIZATION")
        self.assertEqual(r["shadow_proposals"], [])

    def test_retraction_hides_private_and_public_target_names(self):
        r = run(kind="RETRACTION",previous_blob=SYNTHETIC_OLDER)
        text = json.dumps(r)
        self.assertNotIn("memo:private", text)
        self.assertNotIn("view:map", text)

    def test_relation_edit_requires_typed_source_event(self):
        self.assertEqual(run(kind="RELATION_EDIT")["state"],
                         "HELD_TYPED_RELATION_OR_RULE_ORIGIN")

    def test_rule_edit_requires_typed_source_event(self):
        self.assertEqual(run(kind="RULE_EDIT")["state"],
                         "HELD_TYPED_RELATION_OR_RULE_ORIGIN")

    def test_unknown_kind_fails_closed(self):
        with self.assertRaises(ValueError):
            run(kind="EVERYTHING_EXECUTES")

    def test_bad_or_nonhex_blob_fails_closed(self):
        with self.assertRaises(ValueError):
            run(previous_blob="not a sha")
        with self.assertRaises(ValueError):
            run(current_blob="F" * 40)

    def test_current_blob_mismatch_holds(self):
        r = run(current_blob=SYNTHETIC_OLDER)
        self.assertEqual(r["state"], "HELD_CURRENT_BLOB_MISMATCH")
        self.assertEqual(r["shadow_proposals"], [])

    def test_unreviewed_new_local_version_holds(self):
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / PUBLIC_DONOR
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / PUBLIC_DONOR).read_bytes() + b"\n")
            changed_blob = git_blob_sha1(target.read_bytes())
            r = run(repo_root=Path(t), current_blob=changed_blob,
                    previous_blob=PUBLIC_DONOR_BLOB)
            self.assertEqual(r["state"], "HELD_UNREVIEWED_CURRENT_DONOR")
            self.assertEqual(r["shadow_proposals"], [])

    def test_missing_source_is_held(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(run(repo_root=Path(t))["state"], "HELD_SOURCE_MISSING")

    def test_oversize_source_is_held_without_reading_content(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/PUBLIC_DONOR
            target.parent.mkdir(parents=True)
            target.write_bytes(b"x"*(LIMIT_BYTES+1))
            self.assertEqual(run(repo_root=Path(t))["state"], "HELD_SOURCE_OVERSIZE")

    def test_symlink_source_is_held(self):
        with tempfile.TemporaryDirectory() as t:
            target = Path(t)/PUBLIC_DONOR
            target.parent.mkdir(parents=True)
            try:
                target.symlink_to(ROOT / PUBLIC_DONOR)
            except OSError:
                self.skipTest("symlink unavailable")
            self.assertEqual(run(repo_root=Path(t))["state"], "HELD_SOURCE_SYMLINK")

    def test_incorrect_subject_does_not_route(self):
        f = copy.deepcopy(FIX)
        f["change"]["subject"] = "memo:private"
        self.assertEqual(run(fixture=f, previous_blob=SYNTHETIC_OLDER)["state"],
                         "HELD_FIXTURE_SOURCE_MISMATCH")

    def test_hypothesis_does_not_become_observed(self):
        f = copy.deepcopy(FIX)
        f["change"]["evidence"] = "HYPOTHESIS"
        self.assertEqual(run(fixture=f, previous_blob=SYNTHETIC_OLDER)["state"],
                         "HELD_HYPOTHETICAL_CHANGE")

    def test_deterministic_same_inputs(self):
        self.assertEqual(run(previous_blob=SYNTHETIC_OLDER),
                         run(previous_blob=SYNTHETIC_OLDER))

    def test_donor_file_not_modified_by_preview(self):
        before = (ROOT / PUBLIC_DONOR).read_bytes()
        run(previous_blob=SYNTHETIC_OLDER)
        self.assertEqual((ROOT / PUBLIC_DONOR).read_bytes(), before)

    def test_zero_effects_for_all_kinds(self):
        for kind in ("CONTENT","RIGHTS_CHANGE","RETRACTION","RELATION_EDIT","RULE_EDIT"):
            self.assertEqual(run(kind=kind, previous_blob=SYNTHETIC_OLDER)["effects"],
                             ZERO_EFFECTS)


if __name__ == "__main__":
    unittest.main()
