"""Real local SQLite WorkID source-check integration; no network or OS startup."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from examples.cotalkitout.local_source_work_cycle_r0 import run
from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue


class LocalSourceCycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "CoPre.md"
        self.source.write_bytes(b"public-safe CoPre source A\n")
        self.db = str(self.root / "durable.sqlite")

    def test_real_source_is_committed_once_and_recovered_after_reopen(self):
        first = run(str(self.root), self.db, now=100)
        self.assertEqual(first["state"], "COMMITTED_LOCAL_ONLY")
        self.assertFalse(first["external_receiver_ack"])
        self.assertFalse(first["real_external_effect"])
        q = DueWorkQueue(self.db)
        try:
            self.assertEqual(q.snapshot(200)["total"], 1)
            self.assertEqual(q.snapshot(200)["complete"], 1)
        finally:
            q.close()
        second = run(str(self.root), self.db, now=200)
        self.assertEqual(second["state"], "LOCAL_REPLAY_OR_LEASED")
        self.assertEqual(second["queue_state"], "DONE")
        self.assertEqual(second["source_sha256"], first["source_sha256"])
        q = DueWorkQueue(self.db)
        try:
            self.assertEqual(q.snapshot(200)["total"], 1)
            self.assertEqual(q.snapshot(200)["complete"], 1)
        finally:
            q.close()

    def test_source_revision_conflict_cannot_supersede_prior(self):
        prior = run(str(self.root), self.db, now=100)
        self.source.write_bytes(b"public-safe CoPre source B\n")
        changed = run(str(self.root), self.db, now=200)
        self.assertEqual(changed["state"], "HOLD_SOURCE_REVISION_CONFLICT")
        q = DueWorkQueue(self.db)
        try:
            row = q.db.execute("SELECT payload_sha256,state FROM work").fetchone()
            self.assertEqual(row, (prior["source_sha256"], "DONE"))
        finally:
            q.close()

    def test_unsafe_path_refused_and_no_queue_created(self):
        with self.assertRaises(ValueError):
            run(str(self.root), self.db, source="../outside.txt", now=100)
        self.assertFalse(Path(self.db).exists())

    def test_no_early_claim_and_no_external_effect(self):
        q = DueWorkQueue(self.db)
        try:
            data = self.source.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            self.assertEqual(q.enqueue("CoPre:source-integrity:R0",
                         "sha256:" + digest, digest, 200), "ENQUEUED")
        finally:
            q.close()
        result = run(str(self.root), self.db, now=100)
        self.assertEqual(result["state"], "HOLD_SOURCE_REVISION_CONFLICT")
        # Different due times are deliberate conflicts, never silent reschedules.


if __name__ == "__main__":
    unittest.main(verbosity=2)
