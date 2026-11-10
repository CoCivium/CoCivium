"""Positive source-pin check from the repository's immutable Git object.

Requires full Git history (CI checkout fetch-depth: 0). No network fetch here.
"""
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from workid_source_pin import EXPECTED_COMMIT, EXPECTED_REF, EXPECTED_SHA256, verify_source


class HistoricalSourcePinTests(unittest.TestCase):
    def test_pinned_git_object_matches_fixture_and_verifier(self):
        repo = Path(__file__).resolve().parents[2]
        proc = subprocess.run(
            ["git", "-C", str(repo), "show", f"{EXPECTED_COMMIT}:CoPre.md"],
            capture_output=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, "Pinned Git object unavailable; full history required")
        raw = proc.stdout
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "CoPre.md"
            source.write_bytes(raw)
            result = verify_source(source, EXPECTED_REF)
            self.assertEqual(result["state"], "SOURCE_BYTES_MATCH_FIXTURE_PIN")
            self.assertTrue(result["source_verified"])
            self.assertFalse(result["authenticated_origin"])
            self.assertFalse(result["receiver_ack"])


if __name__ == "__main__":
    unittest.main()
