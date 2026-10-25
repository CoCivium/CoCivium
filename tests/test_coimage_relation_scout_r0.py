#!/usr/bin/env python3
"""Scoped CoImage tests: exact bytes, negative knowledge, no visual overclaim."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location(
    "coimage_under_test", Path(__file__).resolve().parents[1] / "scripts" / "CoImageRelationScoutR0.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def fixture(root):
    git(root, "init", "-q")
    (root / "assets").mkdir()
    image_bytes = b"\x89PNG\r\n\x1a\n" + b"synthetic-fixture-only"
    (root / "assets" / "co-orb-diagram.png").write_bytes(image_bytes)
    (root / "assets" / "same-as-orb.png").write_bytes(image_bytes)
    (root / "assets" / "malformed.png").write_bytes(b"this is not PNG")
    (root / "assets" / "glyph.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8"
    )
    (root / "assets" / "untracked.webp").write_bytes(b"RIFFx123WEBP")
    git(root, "add", "assets/co-orb-diagram.png", "assets/same-as-orb.png",
        "assets/malformed.png", "assets/glyph.svg")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-q", "-m", "synthetic fixture")
    return image_bytes


class CoImageCensusTests(unittest.TestCase):
    def with_fixture(self, callback):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            raw = fixture(root)
            return callback(root, raw)

    def test_tracked_scope_excludes_untracked(self):
        def check(root, raw):
            result = MOD.scan(root)
            self.assertEqual(result["discovered_image_paths"], 4)
            self.assertEqual(result["hashed_candidate_count"], 4)
            self.assertNotIn("assets/untracked.webp", [x["source_path"] for x in result["candidates"]])
            self.assertIsNotNone(result["source_commit"])
        self.with_fixture(check)

    def test_exact_hash_and_duplicates_without_semantic_merging(self):
        def check(root, raw):
            output = MOD.scan(root)
            import hashlib
            expected = hashlib.sha256(raw).hexdigest()
            same = [x for x in output["candidates"] if x["sha256"] == expected]
            self.assertEqual(len(same), 2)
            self.assertEqual(len(output["duplicate_byte_groups"]), 1)
            self.assertEqual(output["duplicate_byte_groups"][0]["sha256"], expected)
            self.assertIn("SAME_SHA_NE_SAME_PROVENANCE_OR_RIGHTS", output["nonclaims"])
        self.with_fixture(check)

    def test_content_header_looks_suspect_but_not_fully_decoded(self):
        def check(root, raw):
            by_path = {x["source_path"]: x for x in MOD.scan(root)["candidates"]}
            self.assertEqual(by_path["assets/malformed.png"]["format_header"], "SUSPECT")
            self.assertEqual(by_path["assets/glyph.svg"]["format_header"], "PLAUSIBLE_NOT_FULLY_DECODED")
            self.assertEqual(by_path["assets/co-orb-diagram.png"]["format_header"], "PLAUSIBLE_NOT_FULLY_DECODED")
            self.assertIn("FILE_HEADER_NE_FULL_SAFE_DECODING", MOD.scan(root)["nonclaims"])
        self.with_fixture(check)

    def test_filename_topics_are_not_facts(self):
        def check(root, raw):
            by_path = {x["source_path"]: x for x in MOD.scan(root)["candidates"]}
            self.assertEqual(by_path["assets/co-orb-diagram.png"]["candidate_topics_from_filename_only"],
                             ["CoDiagram", "CoOrbWare"])
            self.assertEqual(by_path["assets/glyph.svg"]["semantic_visual_review"], "NOT_PERFORMED")
        self.with_fixture(check)

    def test_every_candidate_remains_rights_and_privacy_held(self):
        def check(root, raw):
            for asset in MOD.scan(root)["candidates"]:
                self.assertEqual(asset["license"], "UNVERIFIED")
                self.assertEqual(asset["privacy"], "REVIEW_REQUIRED")
                self.assertEqual(asset["publication"], "HOLD")
                self.assertEqual(asset["routing"], "PRIVATE_OR_DRAFT_REVIEW_ONLY")
        self.with_fixture(check)

    def test_file_count_cap_preserves_negative_knowledge(self):
        def check(root, raw):
            result = MOD.scan(root, max_files=2)
            self.assertEqual(result["discovered_image_paths"], 4)
            self.assertEqual(result["hashed_candidate_count"], 2)
            self.assertEqual(result["unexamined_count"], 2)
            self.assertTrue(all(x["reason"] == "FILE_COUNT_CAP" for x in result["negative_knowledge"]))
        self.with_fixture(check)

    def test_byte_limits_do_not_claim_completeness(self):
        def check(root, raw):
            output = MOD.scan(root, max_one=1, max_total=2)
            self.assertEqual(output["hashed_candidate_count"], 0)
            self.assertEqual(output["unexamined_count"], 4)
            self.assertEqual(output["bytes_hashed"], 0)
            self.assertTrue(all(x["reason"] == "BYTE_BUDGET_CAP" for x in output["negative_knowledge"]))
        self.with_fixture(check)

    def test_reject_out_of_bound_values(self):
        def check(root, raw):
            for kw in ({"max_files":401}, {"max_files":-1}, {"max_one":8388609},
                       {"max_total":67108865}):
                with self.subTest(kw=kw), self.assertRaises(ValueError):
                    MOD.scan(root, **kw)
        self.with_fixture(check)

    def test_no_mutation_and_deterministic_output(self):
        def check(root, raw):
            before = {p.relative_to(root).as_posix():p.read_bytes()
                      for p in root.joinpath("assets").iterdir() if p.is_file()}
            result = MOD.scan(root)
            self.assertEqual(result, MOD.scan(root))
            after = {p.relative_to(root).as_posix():p.read_bytes()
                     for p in root.joinpath("assets").iterdir() if p.is_file()}
            self.assertEqual(before, after)
            self.assertTrue(all(v == 0 for v in result["effects"].values()))
        self.with_fixture(check)

    def test_symlink_not_followed(self):
        def check(root, raw):
            target = root / "outside.png"
            target.write_bytes(b"\x89PNG\r\n\x1a\n")
            link = root / "assets" / "external.png"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink not allowed here")
            git(root, "add", "assets/external.png")
            r = MOD.scan(root)
            self.assertEqual(r["discovered_image_paths"], 5)
            self.assertTrue(any(x["reason"] == "SYMLINK_NOT_FOLLOWED"
                                for x in r["negative_knowledge"]))
        self.with_fixture(check)

    def test_json_serialization_source_scoped(self):
        def check(root, raw):
            r = json.loads(json.dumps(MOD.scan(root)))
            self.assertEqual(r["schema"], "CoImage.TrackedVisualCandidateCensus.R0")
            self.assertIn("GIT_TRACKED_FILES", r["search_scope"])
            self.assertIn("TRACKED_IMAGE_PATHS_NE_ALL_RESEARCHABLE_IMAGES", r["nonclaims"])
        self.with_fixture(check)


if __name__ == "__main__":
    unittest.main()
