"""Bounded retrospective CoMap source atlas tests, no private file ingestion."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1]
ROOT = SRC.parents[1]
sys.path.insert(0, str(SRC))
from retro_atlas_r0 import atlas, in_scope, inventory, read_public_file, sha


class RetroAtlasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path_a = "examples/colensmedia/sample.html"
        self.path_b = "examples/comap/diagram.svg"
        for p, text in ((self.path_a, "<html>public sample</html>"),
                        (self.path_b, "<svg>public diagram</svg>")):
            file = self.root/p
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text, encoding="utf-8")
        self.paths = [self.path_a, self.path_b]
        self.scan = inventory(self.root, self.paths)
        self.frontier = json.loads(
            (ROOT/"docs/Evolution/FRONTIER_EVIDENCE_INDEX_R0.json").read_text())
        self.media = json.loads((SRC/"relational_media_fixture_r0.json").read_text())

    def test_public_checkout_candidate_is_hash_verified_not_semantically_ingested(self):
        self.assertEqual(self.scan["new_candidates"], 2)
        self.assertEqual(len(self.scan["current_source_keys"]), 2)
        self.assertEqual(self.scan["inspiration_edges_promoted"], 0)
        self.assertFalse(self.scan["all_prior_media_covered"])
        self.assertFalse(self.scan["actual_receiver_ack"])
        self.assertTrue(all(x["semantic_coverage"] == "NOT_SEMANTICALLY_REVIEWED"
                            and x["inspiration_edges"] == []
                            and x["lifecycle"] == "VERIFIED_LOCAL"
                            for x in self.scan["candidates"]))

    def test_real_hash_matches_bytes(self):
        a = next(x for x in self.scan["candidates"]
                 if x["source_path"] == self.path_a)
        self.assertEqual(a["sha256"], sha((self.root/self.path_a).read_bytes()))

    def test_identical_rescan_is_idempotent(self):
        updated = inventory(self.root, self.paths, prior=self.scan)
        self.assertEqual(updated["new_candidates"], 0)
        self.assertEqual(updated["candidates"], self.scan["candidates"])

    def test_revision_keeps_exact_prior_without_canon_supersession(self):
        (self.root/self.path_a).write_text("<html>source revised</html>")
        changed = inventory(self.root, self.paths, self.scan)
        self.assertEqual(changed["new_candidates"], 1)
        self.assertEqual(len(changed["candidates"]), 3)
        self.assertEqual(changed["historical_candidates_retained"], 1)
        newer = next(x for x in changed["candidates"]
                     if x["source_path"] == self.path_a
                     and x["sha256"] != sha(b"<html>public sample</html>"))
        self.assertIn(sha(b"<html>public sample</html>"),
                      newer["possible_predecessor_hashes"])
        self.assertEqual(newer["inspiration_edges"], [])

    def test_discovered_source_disappears_but_history_survives(self):
        (self.root/self.path_a).unlink()
        result = inventory(self.root, [self.path_b], self.scan)
        self.assertEqual(result["historical_candidates_retained"], 1)
        self.assertTrue(any(x["source_path"]==self.path_a
                            for x in result["candidates"]))

    def test_same_bytes_distinct_public_paths_not_semantic_duplicates(self):
        (self.root/self.path_b).write_bytes((self.root/self.path_a).read_bytes())
        result = inventory(self.root, self.paths)
        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(result["inspiration_edges_promoted"], 0)

    def test_private_path_never_scanned(self):
        self.assertFalse(in_scope("private/chat-media/image.png"))
        with self.assertRaisesRegex(ValueError, "HOLD_UNAUTHORIZED"):
            inventory(self.root, ["private/chat-media/image.png"])

    def test_parent_escape_never_scanned(self):
        with self.assertRaisesRegex(ValueError, "HOLD_UNAUTHORIZED"):
            read_public_file(self.root, "examples/comap/../../private.png")

    def test_unapproved_email_media_never_scanned(self):
        self.assertFalse(in_scope("examples/comail_r0/invite_template.md"))

    def test_symlink_cannot_capture_external_bytes(self):
        source = self.root/self.path_a
        target = self.root/"private.txt"
        target.write_text("private secret")
        source.unlink()
        try:
            source.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink not available")
        with self.assertRaisesRegex(ValueError, "HOLD_SYMLINK_MEDIA_SOURCE"):
            inventory(self.root, self.paths)

    def test_untracked_missing_path_not_accepted(self):
        with self.assertRaisesRegex(ValueError, "HOLD_MEDIA_SOURCE_MISSING"):
            inventory(self.root, ["examples/comap/untracked.html"])

    def test_duplicates_in_discovery_list_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_MEDIA_SCAN_SCOPE_OR_DUPLICATE"):
            inventory(self.root, [self.path_a, self.path_a])

    def test_tampered_prior_inspiration_edge_not_promoted(self):
        prior = copy.deepcopy(self.scan)
        prior["candidates"][0]["inspiration_edges"] = ["self:claimed"]
        with self.assertRaisesRegex(ValueError, "HOLD_PRIOR_INDEX_AUTHORITY"):
            inventory(self.root, self.paths, prior)

    def test_nested_atlas_is_one_workid_with_multiple_lenses(self):
        text = atlas(self.frontier, self.media, self.scan)
        self.assertIn("subgraph COALL", text)
        self.assertIn("subgraph F", text)
        self.assertIn("subgraph M", text)
        self.assertIn("subgraph RETRO", text)
        self.assertIn("CoMap diagram", text)
        self.assertIn("Audio transcript", text)
        self.assertIn("UNREVIEWED", text)
        self.assertIn("Verified CoSeed/CoPath inspiration links: ZERO", text)

    def test_private_draft_absent_from_rendered_visual_and_text(self):
        text = atlas(self.frontier, self.media, self.scan)
        self.assertNotIn("draft:v1", text)
        self.assertNotIn("CoMail staged draft", text)
        self.assertNotIn("EMAIL_DRAFT", text)

    def test_private_only_change_does_not_change_public_atlas(self):
        baseline = atlas(self.frontier, self.media, self.scan)
        alt = copy.deepcopy(self.media)
        private = next(x for x in alt["assets"] if x["visibility"]=="PRIVATE")
        private["sha256"] = sha(b"another private revision")
        self.assertEqual(baseline, atlas(self.frontier, alt, self.scan))

    def test_private_source_root_rejected(self):
        alt = copy.deepcopy(self.media)
        next(x for x in alt["assets"] if x["kind"]=="SOURCE")["visibility"] = "PRIVATE"
        with self.assertRaises(ValueError):
            atlas(self.frontier, alt, self.scan)

    def test_unvalidated_front_status_fails_closed(self):
        bad = copy.deepcopy(self.frontier)
        bad["fronts"][0]["status"] = "LIVE_X2_VERIFIED"
        with self.assertRaisesRegex(ValueError, "HOLD_INVALID_FRONT_OR_DUPLICATE"):
            atlas(bad, self.media, self.scan)

    def test_no_hypothesis_edges_invented_between_fronts_and_candidates(self):
        md = atlas(self.frontier, self.media, self.scan)
        self.assertNotIn(" -->|inspires| ", md.lower())
        self.assertIn("Proximity is not a verified relationship", md)

    def test_visible_source_links_open_only_public_repo(self):
        md = atlas(self.frontier, self.media, self.scan)
        self.assertIn("https://github.com/CoCivium/CoCivium/blob/main/", md)
        self.assertNotIn("chatgpt.com/c/", md)
        self.assertNotIn("mail.google.com/", md)

    def test_output_repeat_is_byte_identical(self):
        md = atlas(self.frontier, self.media, self.scan)
        self.assertEqual(sha(md.encode()), sha(atlas(
            self.frontier, self.media, self.scan).encode()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
