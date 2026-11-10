import tempfile
import unittest
from pathlib import Path
from workid_source_pin import verify_source, EXPECTED_REF


class SourcePinTests(unittest.TestCase):
    def test_wrong_reference(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "CoPre.md"
            p.write_bytes(b"fixture")
            self.assertEqual(verify_source(p, "untrusted")["state"], "HELD_PIN_MISMATCH")

    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(verify_source(Path(d) / "CoPre.md", EXPECTED_REF)["state"], "HELD_SOURCE_UNAVAILABLE")

    def test_tampered_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "CoPre.md"
            p.write_bytes(b"tampered")
            result = verify_source(p, EXPECTED_REF)
            self.assertEqual(result["state"], "HELD_SOURCE_BYTES_MISMATCH")
            self.assertFalse(result["source_verified"])

    def test_wrong_name(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "wrong.md"
            p.write_bytes(b"fixture")
            self.assertEqual(verify_source(p, EXPECTED_REF)["state"], "HELD_SOURCE_UNAVAILABLE")

    def test_oversize(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "CoPre.md"
            p.write_bytes(b"x" * 131073)
            self.assertEqual(verify_source(p, EXPECTED_REF)["state"], "HELD_SOURCE_SIZE")

    def test_empty(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "CoPre.md"
            p.write_bytes(b"")
            self.assertEqual(verify_source(p, EXPECTED_REF)["state"], "HELD_SOURCE_SIZE")


if __name__ == "__main__":
    unittest.main()
