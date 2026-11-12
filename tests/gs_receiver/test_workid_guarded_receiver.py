"""Regression tests for the guarded synthetic write boundary."""
import tempfile
import unittest
from pathlib import Path

from test_workid_sqlite_convergence import proposal, authorization, source_bytes
from workid_guarded_receiver import commit_guarded


class GuardedReceiverTests(unittest.TestCase):
    def test_guarded_commit_duplicate_and_readback(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "CoPre.md"
            source.write_bytes(source_bytes())
            db = root / "work.sqlite"
            first = commit_guarded(db, proposal(), authorization(), source)
            second = commit_guarded(db, proposal(), authorization(), source)
            self.assertEqual(first["state"], "SYNTHETIC_LOCAL_READBACK_ONLY")
            self.assertEqual((first["new_commits"], second["new_commits"]), (1, 0))
            self.assertTrue(second["duplicate"])
            self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])
            self.assertFalse(first["external_receiver_ack"])
            self.assertFalse(first["authenticated_authority"])

    def test_rejected_proposals_never_create_database(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "CoPre.md"
            source.write_bytes(source_bytes())
            db = root / "work.sqlite"
            cases = [
                (proposal(), None, source),
                (dict(proposal(), lease_epoch=2), authorization(), source),
                (dict(proposal(), consent="REAL"), authorization(), source),
            ]
            for packet, auth, path in cases:
                with self.subTest(packet=packet, auth=auth):
                    result = commit_guarded(db, packet, auth, path)
                    self.assertEqual(result["state"], "HELD_BEFORE_WRITE")
                    self.assertFalse(db.exists())
            source.write_bytes(b"tampered")
            result = commit_guarded(db, proposal(), authorization(), source)
            self.assertEqual(result["state"], "HELD_BEFORE_WRITE")
            self.assertFalse(db.exists())


if __name__ == "__main__":
    unittest.main()
