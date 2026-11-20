"""CoLocalWorkID R0: synthetic process-loss, fencing and bounded multiworker tests.

Exercises the incumbent DueWorkQueue without starting a scheduler, model, device,
or external receiver. Deliberately uses fixture UTC ticks; these are not wall-time
liveness or real-host recovery evidence. No private X2 data is imported.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cotalkitout"))
from due_work_catchup_r0 import Claim, DueWorkQueue

SOURCE = hashlib.sha256(b"synthetic-producer-R0").hexdigest()
RESULT = hashlib.sha256(b"synthetic-consumer-accepted-local-R0").hexdigest()
DUE = 1_700_000_000


def command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), *map(str, args)],
                          capture_output=True, text=True, timeout=15)


def child(mode: str, db: str, owner: str, now: int) -> None:
    q = DueWorkQueue(db)
    claims = q.claim_due(now=now, owner=owner, lease_seconds=5, limit=1)
    print(json.dumps([dataclasses.asdict(c) for c in claims], sort_keys=True), flush=True)
    if mode == "child-crash":
        # Simulates hard process termination AFTER the SQLite lease committed.
        # No finally/close, no in-memory handoff and no result effect.
        os._exit(47)
    q.close()


class WorkerRecovery(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = str(Path(tmp.name) / "work.sqlite3")
        q = DueWorkQueue(self.db)
        self.assertEqual(q.enqueue("W1", "SYNTHETIC_R0", SOURCE, DUE), "ENQUEUED")
        q.close()

    def test_hard_process_death_lease_expiry_fence_and_replay(self) -> None:
        died = command("child-crash", self.db, "worker-A", DUE)
        self.assertEqual(died.returncode, 47, died.stderr)
        claims = json.loads(died.stdout)
        self.assertEqual(len(claims), 1)
        stale = Claim(**claims[0])
        self.assertEqual(stale.epoch, 1)
        self.assertEqual(stale.lease_until, DUE + 5)

        premature = command("child-claim", self.db, "worker-B", DUE + 4)
        self.assertEqual(premature.returncode, 0, premature.stderr)
        self.assertEqual(json.loads(premature.stdout), [])

        recovered = command("child-claim", self.db, "worker-B", DUE + 5)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        renewed = Claim(**json.loads(recovered.stdout)[0])
        self.assertEqual((renewed.work_id, renewed.epoch, renewed.owner),
                         ("W1", 2, "worker-B"))

        q = DueWorkQueue(self.db)
        try:
            self.assertEqual(q.complete(stale, result_sha256=RESULT, now=DUE + 6), "FENCED")
            self.assertEqual(q.complete(renewed, result_sha256=RESULT, now=DUE + 6),
                             "COMMITTED_LOCAL_ONLY")
            self.assertEqual(q.complete(renewed, result_sha256=RESULT, now=DUE + 6), "REPLAY")
            self.assertEqual(q.complete(stale, result_sha256=RESULT, now=DUE + 6), "CONFLICT")
            self.assertEqual(q.enqueue("W1", "SYNTHETIC_R0", SOURCE, DUE), "REPLAY")
            self.assertEqual(q.enqueue("W1", "OTHER", SOURCE, DUE), "CONFLICT")
            self.assertEqual(q.claim_due(now=DUE + 999, owner="worker-C"), [])
            snapshot = q.snapshot(DUE + 999)
            self.assertEqual((snapshot["total"], snapshot["complete"], snapshot["next_wake"]),
                             (1, 1, None))
            self.assertFalse(snapshot["independent_receiver_ack"])
            self.assertFalse(snapshot["external_effect_verified"])
        finally:
            q.close()

    def test_competing_fresh_processes_claim_one_elected_worker(self) -> None:
        workers = [subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                                     "child-claim", self.db, "contender-" + str(i), str(DUE)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True) for i in range(4)]
        outputs = [w.communicate(timeout=15) for w in workers]
        for w, (out, err) in zip(workers, outputs):
            self.assertEqual(w.returncode, 0, err)
            self.assertTrue(out.strip())
        granted = [claim for out, _ in outputs for claim in json.loads(out)]
        self.assertEqual(len(granted), 1, "multiple processes may not own one live lease")
        self.assertEqual(granted[0]["work_id"], "W1")
        self.assertEqual(granted[0]["epoch"], 1)

    def test_completed_sibling_is_not_reexecuted_after_orphan_expiry(self) -> None:
        q = DueWorkQueue(self.db)
        try:
            self.assertEqual(q.enqueue("W2", "SYNTHETIC_R0", SOURCE, DUE), "ENQUEUED")
            initial = q.claim_due(now=DUE, owner="original", lease_seconds=5, limit=2)
            self.assertEqual([x.work_id for x in initial], ["W1", "W2"])
            self.assertEqual(q.complete(initial[0], result_sha256=RESULT, now=DUE + 1),
                             "COMMITTED_LOCAL_ONLY")
        finally:
            q.close()
        recovered = command("child-claim", self.db, "successor", DUE + 5)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        later = [Claim(**d) for d in json.loads(recovered.stdout)]
        self.assertEqual([c.work_id for c in later], ["W2"])
        q = DueWorkQueue(self.db)
        try:
            self.assertEqual(q.complete(initial[1], result_sha256=RESULT, now=DUE + 6),
                             "FENCED")
            self.assertEqual(q.complete(later[0], result_sha256=RESULT, now=DUE + 6),
                             "COMMITTED_LOCAL_ONLY")
            self.assertEqual(q.snapshot(DUE + 7)["complete"], 2)
            self.assertEqual(q.claim_due(now=DUE + 900, owner="third", limit=2), [])
        finally:
            q.close()

    def test_lease_boundary_fails_closed(self) -> None:
        q = DueWorkQueue(self.db)
        try:
            claim = q.claim_due(now=DUE, owner="owner", lease_seconds=5)[0]
            self.assertEqual(q.complete(claim, result_sha256=RESULT, now=DUE + 5),
                             "FENCED")
            new = q.claim_due(now=DUE + 5, owner="successor", lease_seconds=5)[0]
            self.assertEqual(new.epoch, 2)
            self.assertEqual(q.complete(new, result_sha256=RESULT, now=DUE + 6),
                             "COMMITTED_LOCAL_ONLY")
        finally:
            q.close()

    def test_invalid_batch_and_time_rejected(self) -> None:
        q = DueWorkQueue(self.db)
        try:
            for kwargs in ({"now": True, "owner": "X"},
                           {"now": DUE, "owner": "X", "lease_seconds": 0},
                           {"now": DUE, "owner": "X", "limit": 101}):
                with self.assertRaises(ValueError):
                    q.claim_due(**kwargs)
        finally:
            q.close()


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] in {"child-crash", "child-claim"}:
        child(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        unittest.main()
