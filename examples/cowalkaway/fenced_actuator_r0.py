#!/usr/bin/env python3
"""CoWalkAway W07 R0: offline fencing/replay canary.

PUBLIC-SAFE SYNTHETIC TEST ONLY: not a scheduler, service, CoStead pickup,
independent reviewer, authority assignment, or live worker.  SQLite is local.
No network, process spawning, external writes, or production access.
Time is injected, not attested; no real clock, process liveness, or boot survival proof.

Run: python -B fenced_actuator_r0.py --self-test
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path


class Hold(RuntimeError):
    """A required authorization, identity, or current lease is absent."""


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


class Ledger:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path, timeout=5, isolation_level=None, check_same_thread=False)
        self.db.execute('PRAGMA busy_timeout=5000')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('CREATE TABLE IF NOT EXISTS lease ('
                        'scope TEXT PRIMARY KEY, owner TEXT NOT NULL, token INTEGER NOT NULL, until INTEGER NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS receipt ('
                        'job TEXT PRIMARY KEY, scope TEXT NOT NULL, input_hash TEXT NOT NULL, '
                        'receipt_hash TEXT NOT NULL, token INTEGER NOT NULL)')

    def close(self):
        self.db.close()

    def acquire(self, scope: str, owner: str, now: int, ttl: int) -> int:
        if not scope or not owner or type(now) is not int or type(ttl) is not int or ttl <= 0:
            raise Hold('INVALID_LEASE_REQUEST')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT owner, token, until FROM lease WHERE scope=?', (scope,)).fetchone()
            if row and row[2] > now:
                if row[0] != owner:
                    raise Hold('ACTUATOR_ALREADY_ELECTED')
                # Same owner may not silently reacquire another token; only existing lease identity remains.
                return row[1]
            token = row[1] + 1 if row else 1
            self.db.execute('INSERT INTO lease(scope, owner, token, until) VALUES(?,?,?,?) '
                            'ON CONFLICT(scope) DO UPDATE SET owner=excluded.owner, token=excluded.token, until=excluded.until',
                            (scope, owner, token, now + ttl))
            return token

    def finish(self, *, scope: str, owner: str, token: int, now: int,
               job: str, input_hash: str, output: dict) -> tuple[str, str]:
        if not scope or not owner or not job or type(token) is not int or type(now) is not int:
            raise Hold('INVALID_JOB_IDENTITY')
        if len(input_hash) != 64 or any(x not in '0123456789abcdef' for x in input_hash):
            raise Hold('INVALID_SOURCE_DIGEST')
        if not isinstance(output, dict):
            raise Hold('INVALID_OUTPUT')
        receipt = {
            'schema': 'CoWalkAway.FencedActuatorReceipt.R0', 'scope': scope,
            'job': job, 'source_hash': input_hash, 'output': output,
            'epistemic_class': 'SYNTHETIC_TEST_ONLY',
            'receiver_ack': False, 'public_effect': False,
        }
        receipt_hash = sha256(canonical(receipt))
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT owner, token, until FROM lease WHERE scope=?', (scope,)).fetchone()
            if not row or row[0] != owner or row[1] != token or row[2] <= now:
                raise Hold('STALE_OR_EXPIRED_ACTUATOR')
            old = self.db.execute('SELECT scope, input_hash, receipt_hash FROM receipt WHERE job=?', (job,)).fetchone()
            if old:
                if old == (scope, input_hash, receipt_hash):
                    return ('REPLAY_NO_NEW_EFFECT', receipt_hash)
                raise Hold('JOB_IDENTITY_COLLISION')
            self.db.execute('INSERT INTO receipt(job, scope, input_hash, receipt_hash, token) VALUES(?,?,?,?,?)',
                            (job, scope, input_hash, receipt_hash, token))
            return ('ONE_NEW_SYNTHETIC_RECEIPT', receipt_hash)

    def receipts(self) -> list[tuple]:
        return self.db.execute('SELECT job, scope, input_hash, receipt_hash, token FROM receipt ORDER BY job').fetchall()


class FencedActuatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'ledger.sqlite'
        self.db = Ledger(self.path)
        self.source = sha256('source-v1')

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def finish(self, **kw):
        defaults = dict(scope='site', owner='a', token=1, now=1, job='j1', input_hash=self.source, output={'test': 'passed'})
        defaults.update(kw)
        return self.db.finish(**defaults)

    def test_single_election(self):
        self.assertEqual(1, self.db.acquire('site', 'a', 0, 10))
        with self.assertRaisesRegex(Hold, 'ALREADY_ELECTED'):
            self.db.acquire('site', 'b', 1, 10)

    def test_reentrant_owner_same_token(self):
        self.db.acquire('site', 'a', 0, 10)
        self.assertEqual(1, self.db.acquire('site', 'a', 1, 10))

    def test_expiry_rotates_fence(self):
        self.db.acquire('site', 'a', 0, 10)
        self.assertEqual(2, self.db.acquire('site', 'b', 10, 10))
        with self.assertRaisesRegex(Hold, 'STALE_OR_EXPIRED'):
            self.finish()

    def test_stale_owner_after_reopen(self):
        self.db.acquire('site', 'a', 0, 2)
        self.db.close()
        self.db = Ledger(self.path)
        self.assertEqual(2, self.db.acquire('site', 'b', 2, 10))
        with self.assertRaisesRegex(Hold, 'STALE_OR_EXPIRED'):
            self.finish()

    def test_one_receipt_then_replay(self):
        self.db.acquire('site', 'a', 0, 10)
        self.assertEqual('ONE_NEW_SYNTHETIC_RECEIPT', self.finish()[0])
        self.assertEqual('REPLAY_NO_NEW_EFFECT', self.finish()[0])
        self.assertEqual(1, len(self.db.receipts()))

    def test_replay_survives_reopen(self):
        self.db.acquire('site', 'a', 0, 10)
        first = self.finish()
        self.db.close()
        self.db = Ledger(self.path)
        self.assertEqual(('REPLAY_NO_NEW_EFFECT', first[1]), self.finish())
        self.assertEqual(1, len(self.db.receipts()))

    def test_conflicting_receipt_holds(self):
        self.db.acquire('site', 'a', 0, 10)
        self.finish()
        with self.assertRaisesRegex(Hold, 'IDENTITY_COLLISION'):
            self.finish(output={'test': 'changed'})
        self.assertEqual(1, len(self.db.receipts()))

    def test_changed_source_holds(self):
        self.db.acquire('site', 'a', 0, 10)
        self.finish()
        with self.assertRaisesRegex(Hold, 'IDENTITY_COLLISION'):
            self.finish(input_hash=sha256('source-v2'))

    def test_expired_lease_cannot_commit(self):
        self.db.acquire('site', 'a', 0, 5)
        with self.assertRaisesRegex(Hold, 'STALE_OR_EXPIRED'):
            self.finish(now=5)

    def test_unknown_scope_cannot_commit(self):
        with self.assertRaisesRegex(Hold, 'STALE_OR_EXPIRED'):
            self.finish()

    def test_bad_digest_rejected(self):
        self.db.acquire('site', 'a', 0, 10)
        with self.assertRaisesRegex(Hold, 'SOURCE_DIGEST'):
            self.finish(input_hash='not-sha')

    def test_bad_lease_ttl_rejected(self):
        with self.assertRaisesRegex(Hold, 'INVALID_LEASE'):
            self.db.acquire('site', 'a', 0, 0)

    def test_parallel_independent_scopes(self):
        ta = self.db.acquire('s1', 'a', 0, 10)
        tb = self.db.acquire('s2', 'b', 0, 10)
        self.assertEqual((1, 1), (ta, tb))
        self.assertEqual('ONE_NEW_SYNTHETIC_RECEIPT', self.finish(scope='s1', job='j1')[0])
        self.assertEqual('ONE_NEW_SYNTHETIC_RECEIPT', self.finish(scope='s2', owner='b', job='j2')[0])
        self.assertEqual(2, len(self.db.receipts()))

    def test_concurrent_election_one_winner(self):
        results = []
        lock = threading.Lock()
        barrier = threading.Barrier(4)
        def run(i):
            other = Ledger(self.path)
            try:
                barrier.wait(timeout=3)
                try:
                    result = ('WIN', other.acquire('shared', f'a{i}', 0, 10))
                except Hold as e:
                    result = ('HOLD', str(e))
                with lock:
                    results.append(result)
            finally:
                other.close()
        threads = [threading.Thread(target=run, args=(i,)) for i in range(4)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=6)
        self.assertFalse(any(t.is_alive() for t in threads))
        self.assertEqual(1, sum(r[0] == 'WIN' for r in results))
        self.assertEqual(3, sum(r[0] == 'HOLD' for r in results))

    def test_receipt_not_ack(self):
        self.db.acquire('site', 'a', 0, 10)
        result = self.finish()
        self.assertEqual('ONE_NEW_SYNTHETIC_RECEIPT', result[0])
        self.assertNotIn('ACK', result[0])

    def test_nonfinite_output_fails(self):
        self.db.acquire('site', 'a', 0, 10)
        with self.assertRaises(ValueError):
            self.finish(output={'unsafe': float('nan')})
        self.assertEqual([], self.db.receipts())


    def run_fresh_process(self, mode):
        """Run the same durable SQLite WorkID in an actual fresh Python process.

        This is an isolated Linux CI fixture, not an X2 reboot, daemon,
        external side effect, independently operated receiver or 3ind proof.
        """
        child_code = r'''
import os
import sys
from fenced_actuator_r0 import Ledger, sha256

db = Ledger(sys.argv[1])
mode = sys.argv[2]
source = sha256("source-v1")
out = {"test": "passed"}
if mode == "first":
    token = db.acquire("os-restart", "process-a", 0, 4)
    state, _ = db.finish(scope="os-restart", owner="process-a", token=token,
                         now=1, job="replay-os", input_hash=source, output=out)
    print(state)
elif mode == "replay":
    token = db.acquire("os-restart", "process-b", 4, 4)
    state, _ = db.finish(scope="os-restart", owner="process-b", token=token,
                         now=5, job="replay-os", input_hash=source, output=out)
    print(state)
elif mode == "uncommitted-crash":
    token = db.acquire("os-crash", "process-a", 0, 4)
    db.db.execute("BEGIN IMMEDIATE")
    db.db.execute("INSERT INTO receipt(job,scope,input_hash,receipt_hash,token) VALUES(?,?,?,?,?)",
                  ("uncommitted", "os-crash", source, source, token))
    os._exit(91)  # Intentionally skips transaction commit, finally and destructor.
elif mode == "committed-ack-lost":
    token = db.acquire("os-ack", "process-a", 0, 4)
    db.finish(scope="os-ack", owner="process-a", token=token,
              now=1, job="ack-lost", input_hash=source, output=out)
    os._exit(92)  # SQLite commit succeeds but result was never returned to caller.
else:
    raise RuntimeError("UNEXPECTED_CANARY_MODE")
db.close()
'''
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parent) + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-B", "-c", child_code, str(self.path), mode],
            capture_output=True, text=True, timeout=12, env=env, check=False
        )

    def test_fresh_os_process_replay_one_receipt(self):
        first = self.run_fresh_process("first")
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertIn("ONE_NEW_SYNTHETIC_RECEIPT", first.stdout)
        replay = self.run_fresh_process("replay")
        self.assertEqual(0, replay.returncode, replay.stderr)
        self.assertIn("REPLAY_NO_NEW_EFFECT", replay.stdout)
        self.assertEqual(["replay-os"], [r[0] for r in self.db.receipts()])

    def test_os_process_killed_with_uncommitted_sqlite_transaction(self):
        killed = self.run_fresh_process("uncommitted-crash")
        self.assertEqual(91, killed.returncode, killed.stderr)
        self.assertEqual([], self.db.receipts())
        token = self.db.acquire("os-crash", "process-b", 4, 4)
        self.assertEqual(2, token)
        state, _ = self.db.finish(
            scope="os-crash", owner="process-b", token=token, now=5,
            job="uncommitted", input_hash=self.source, output={"test": "passed"}
        )
        self.assertEqual("ONE_NEW_SYNTHETIC_RECEIPT", state)
        self.assertEqual(1, len(self.db.receipts()))

    def test_os_process_crashed_after_commit_before_ack(self):
        lost = self.run_fresh_process("committed-ack-lost")
        self.assertEqual(92, lost.returncode, lost.stderr)
        self.assertEqual(["ack-lost"], [r[0] for r in self.db.receipts()])
        token = self.db.acquire("os-ack", "process-b", 4, 4)
        self.assertEqual(2, token)
        state, _ = self.db.finish(
            scope="os-ack", owner="process-b", token=token, now=5,
            job="ack-lost", input_hash=self.source, output={"test": "passed"}
        )
        self.assertEqual("REPLAY_NO_NEW_EFFECT", state)
        self.assertEqual(1, len(self.db.receipts()))


if __name__ == '__main__':
    import sys
    if sys.argv[1:] != ['--self-test']:
        raise SystemExit('Run with --self-test; this is not a daemon or worker.')
    sys.argv = [sys.argv[0]]
    unittest.main(verbosity=2)
