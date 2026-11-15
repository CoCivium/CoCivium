"""Adversarial CoMedia retroactive-inventory tests; synthetic fixture files."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from retro_media_backfill_r0 import inspect, SCHEMA


class RetroMediaBackfillTests(unittest.TestCase):
    def test_exact_bytes_hash_and_no_semantic_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "diagram.png"
            file.write_bytes(b"synthetic-pixels")
            result = inspect([str(file)])
            item = result["media"][0]
            self.assertEqual(item["sha256"], hashlib.sha256(b"synthetic-pixels").hexdigest())
            self.assertEqual(item["semantic_review"], "NOT_SEMANTICALLY_REVIEWED")
            self.assertEqual(item["co_seed_adoption"], "NOT_PROVEN")
            self.assertEqual(item["publication"], "NOT_AUTHORIZED")

    def test_retro_media_does_not_auto_join_copath(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "old.svg").write_text("<svg/>", encoding="utf-8")
            row = inspect([directory])["media"][0]
            self.assertEqual(row["kind"], "diagram")
            self.assertEqual(row["inspiration"], "CANDIDATE_UNREVIEWED")
            self.assertEqual(row["co_path_adoption"], "NOT_PROVEN")
            self.assertEqual(row["receiver_ack"], "NOT_PROVEN")

    def test_duplicate_content_retains_two_separate_source_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("a.png", "b.png"):
                (Path(directory) / name).write_bytes(b"same-bytes")
            result = inspect([directory])
            self.assertEqual(len(result["media"]), 2)
            self.assertEqual(result["hashes"]["duplicate_content_candidates"], 1)
            self.assertNotEqual(result["media"][0]["source_path"],
                                result["media"][1]["source_path"])

    def test_bounded_scan_explicitly_reports_truncation(self):
        with tempfile.TemporaryDirectory() as directory:
            for idx in range(4):
                (Path(directory) / f"{idx}.jpg").write_bytes(bytes([idx]))
            report = inspect([directory], max_files=2)
            self.assertEqual(len(report["media"]), 2)
            self.assertTrue(report["coverage"]["truncated"])
            self.assertFalse(report["coverage"]["complete_history"])

    def test_oversized_media_held(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "huge.mp4").write_bytes(b"abcdef")
            r = inspect([directory], max_bytes_per_file=3)
            self.assertEqual(r["media"], [])
            self.assertEqual(r["skipped"][0]["reason"], "TOO_LARGE_OR_NOT_REGULAR")

    def test_unknown_extension_not_inventoried_as_media(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "notes.unknown").write_bytes(b"x")
            self.assertEqual(inspect([directory])["media"], [])

    def test_symlink_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "asset.png").write_bytes(b"original")
            try:
                (base / "alias.png").symlink_to(base / "asset.png")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            report = inspect([directory])
            self.assertEqual(len(report["media"]), 1)

    def test_requires_explicit_roots_and_budgets(self):
        with self.assertRaises(ValueError):
            inspect([])
        with self.assertRaises(ValueError):
            inspect(["."], max_files=0)

    def test_incomplete_coverage_nonclaims_included(self):
        with tempfile.TemporaryDirectory() as directory:
            report = inspect([directory])
            self.assertEqual(report["schema"], SCHEMA)
            self.assertIn("DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY", report["nonclaims"])
            self.assertIn("HASHING_IS_NOT_SEMANTIC_INGESTION", report["nonclaims"])
            self.assertEqual(report["privacy"], "PRIVATE_MANIFEST_DO_NOT_PUBLICLY_COMMIT")

    def test_repeating_same_root_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "one.webp").write_bytes(b"data")
            self.assertEqual(len(inspect([directory, directory])["media"]), 1)


if __name__ == "__main__":
    unittest.main()
