"""Synthetic missed-cron recovery tests, never an assertion of X2 uptime."""
import hashlib
import os
from pathlib import Path
import tempfile
import threading
import unittest
import subprocess
import sys
import json
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue, Claim


def digest(txt):
    return hashlib.sha256(txt.encode()).hexdigest()


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'work.db')
        self.a = DueWorkQueue(self.path)
        self.assertEqual(self.a.enqueue('w1','source:sha1',digest('payload'),10),'ENQUEUED')

    def tearDown(self):
        self.a.close()
        self.tmp.cleanup()

    def test_nine_missed_ticks_one_due_task_one_receipt(self):
        self.assertEqual(self.a.snapshot(540)['due_pending'],1)
        token, = self.a.claim_due(now=540,owner='workerA')
        self.assertEqual(token.epoch,1)
        self.assertEqual(self.a.complete(token,result_sha256=digest('result'),now=541),'COMMITTED_LOCAL_ONLY')
        self.assertEqual(self.a.complete(token,result_sha256=digest('result'),now=541),'REPLAY')
        self.assertEqual(self.a.claim_due(now=999,owner='workerB'),[])
        self.assertEqual(self.a.snapshot(999)['complete'],1)
        self.assertFalse(self.a.snapshot(999)['independent_receiver_ack'])

    def test_missed_wake_does_not_invent_duplicate_workids(self):
        for _ in range(9):
            self.assertEqual(self.a.enqueue('w1','source:sha1',digest('payload'),10),'REPLAY')
        self.assertEqual(self.a.snapshot(1000)['total'],1)

    def test_identity_conflict_cannot_clobber_existing_task(self):
        self.assertEqual(self.a.enqueue('w1','other',digest('payload'),10),'CONFLICT')
        self.assertEqual(self.a.enqueue('w1','source:sha1',digest('new'),10),'CONFLICT')
        self.assertEqual(self.a.snapshot(100)['total'],1)

    def test_future_due_does_not_get_leased_early(self):
        self.assertEqual(self.a.claim_due(now=9,owner='workerA'),[])
        self.assertEqual(self.a.next_wake(),10)

    def test_expired_lease_reclaims_and_fences_old(self):
        old, = self.a.claim_due(now=10,owner='A',lease_seconds=30)
        self.assertEqual(self.a.claim_due(now=39,owner='B'),[])
        successor, = self.a.claim_due(now=40,owner='B',lease_seconds=30)
        self.assertEqual(successor.epoch,old.epoch+1)
        self.assertEqual(self.a.complete(old,result_sha256=digest('old'),now=41),'FENCED')
        self.assertEqual(self.a.complete(successor,result_sha256=digest('new'),now=41),'COMMITTED_LOCAL_ONLY')

    def test_restart_preserves_due_and_completed_tasks(self):
        self.a.close()
        self.a=DueWorkQueue(self.path)
        token, = self.a.claim_due(now=120,owner='A')
        self.a.close()
        self.a=DueWorkQueue(self.path)
        self.assertEqual(self.a.claim_due(now=200,owner='B'),[])
        self.assertEqual(self.a.complete(token,result_sha256=digest('ok'),now=121),'COMMITTED_LOCAL_ONLY')
        self.a.close()
        self.a=DueWorkQueue(self.path)
        self.assertEqual(self.a.snapshot(999)['complete'],1)

    def test_wrong_owner_or_epoch_cannot_complete(self):
        from dataclasses import replace
        token, = self.a.claim_due(now=10,owner='A')
        self.assertEqual(self.a.complete(replace(token,owner='B'),result_sha256=digest('out'),now=11),'FENCED')
        self.assertEqual(self.a.complete(replace(token,epoch=99),result_sha256=digest('out'),now=11),'FENCED')
        self.assertEqual(self.a.snapshot(11)['complete'],0)

    def test_completion_requires_live_lease(self):
        token, = self.a.claim_due(now=10,owner='A',lease_seconds=5)
        self.assertEqual(self.a.complete(token,result_sha256=digest('out'),now=15),'FENCED')
        self.assertEqual(self.a.snapshot(15)['expired_leases'],1)

    def test_bounded_batch_deterministic_order(self):
        self.assertEqual(self.a.enqueue('w2','src',digest('payload2'),5),'ENQUEUED')
        self.assertEqual(self.a.enqueue('w3','src',digest('payload3'),8),'ENQUEUED')
        first = self.a.claim_due(now=100,owner='A',limit=2)
        self.assertEqual([c.work_id for c in first],['w2','w3'])
        second = self.a.claim_due(now=100,owner='B',limit=1)
        self.assertEqual([c.work_id for c in second],['w1'])
        self.assertEqual(self.a.claim_due(now=100,owner='B'),[])

    def test_concurrent_claimers_single_winner(self):
        barrier=threading.Barrier(2)
        def race(owner):
            queue=DueWorkQueue(self.path)
            try:
                barrier.wait(timeout=3)
                return queue.claim_due(now=10,owner=owner)
            finally:
                queue.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            a,b=list(pool.map(race,['A','B']))
        self.assertEqual(len(a)+len(b),1)
        self.assertEqual(self.a.snapshot(11)['total'],1)

    def test_invalid_clock_digest_and_batch_fail_closed(self):
        for now in (True,-1,'99'):
            with self.assertRaises(ValueError):
                self.a.claim_due(now=now,owner='A')
        with self.assertRaises(ValueError):
            self.a.enqueue('x','src','not-a-sha',10)
        with self.assertRaises(ValueError):
            self.a.claim_due(now=10,owner='A',limit=0)
        with self.assertRaises(ValueError):
            self.a.claim_due(now=10,owner='A',lease_seconds=0)

    def test_duplicate_result_mismatch_conflicts(self):
        token,=self.a.claim_due(now=10,owner='A')
        self.assertEqual(self.a.complete(token,result_sha256=digest('r1'),now=11),'COMMITTED_LOCAL_ONLY')
        self.assertEqual(self.a.complete(token,result_sha256=digest('r2'),now=11),'CONFLICT')
        self.assertEqual(self.a.complete(replace(token,owner='forged'),result_sha256=digest('r1'),now=11),'CONFLICT')
        self.assertEqual(self.a.complete(replace(token,source_revision='forged'),result_sha256=digest('r1'),now=11),'CONFLICT')

    def test_child_process_crash_recovered_after_lease_expiry(self):
        child = '''from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue
import sys,json
q=DueWorkQueue(sys.argv[1]); c,=q.claim_due(now=10,owner='child',lease_seconds=5)
print(json.dumps({'work_id':c.work_id,'epoch':c.epoch,'lease_until':c.lease_until}));q.close()
'''
        proc=subprocess.run([sys.executable,'-c',child,self.path],
                            cwd=str(Path(__file__).resolve().parent),
                            capture_output=True,text=True,timeout=5,check=False)
        self.assertEqual(proc.returncode,0,proc.stderr)
        info=json.loads(proc.stdout)
        self.assertEqual(info,{'work_id':'w1','epoch':1,'lease_until':15})
        self.assertEqual(self.a.claim_due(now=14,owner='other'),[])
        succ,=self.a.claim_due(now=15,owner='successor')
        self.assertEqual(succ.epoch,2)
        self.assertEqual(self.a.complete(succ,result_sha256=digest('after_crash'),now=16),'COMMITTED_LOCAL_ONLY')
        self.assertEqual(self.a.snapshot(999)['complete'],1)


    def test_interleaved_competitor_cannot_overwrite_first_result(self):
        import sqlite3
        token, = self.a.claim_due(now=10, owner='A')
        competitor_digest = digest('competitor-result')
        stale_digest = digest('stale-writer-result')
        original = self.a.db
        db_path = self.path

        class InterposeOnce:
            def __init__(self):
                self.triggered = False
            def __enter__(self):
                original.__enter__()
                return self
            def __exit__(self, *args):
                return original.__exit__(*args)
            def __getattr__(self, name):
                return getattr(original, name)
            def execute(self, statement, params=()):
                # Deterministic interleaving: another DB connection completes
                # just before this writer's UPDATE. This is a local fixture.
                if "UPDATE work" in statement and "SET state='DONE'" in statement and not self.triggered:
                    self.triggered = True
                    with sqlite3.connect(db_path, timeout=3) as other:
                        other.execute("UPDATE work SET state='DONE', result_sha256=?, "
                                      "completed_at=? WHERE work_id=?",
                                      (competitor_digest, 11, token.work_id))
                return original.execute(statement, params)
        interceptor = InterposeOnce()
        self.a.db = interceptor
        try:
            outcome = self.a.complete(token, result_sha256=stale_digest, now=12)
        finally:
            self.a.db = original
        self.assertTrue(interceptor.triggered)
        self.assertEqual(outcome, 'CONFLICT')
        self.assertEqual(original.execute('SELECT result_sha256 FROM work WHERE work_id=?',
                                          (token.work_id,)).fetchone()[0], competitor_digest)

    def test_two_concurrent_finishers_one_commit_other_conflict(self):
        token, = self.a.claim_due(now=10, owner='A')
        barrier = threading.Barrier(2)
        def finish(item):
            q = DueWorkQueue(self.path)
            try:
                barrier.wait(timeout=4)
                return q.complete(token, result_sha256=digest(item), now=11)
            finally:
                q.close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(finish, ['one', 'two']))
        self.assertCountEqual(results, ['COMMITTED_LOCAL_ONLY', 'CONFLICT'])
        final = self.a.db.execute('SELECT result_sha256 FROM work WHERE work_id=?',
                                  (token.work_id,)).fetchone()[0]
        self.assertIn(final, (digest('one'), digest('two')))

    def test_replay_keeps_completed_identity_and_digest(self):
        token, = self.a.claim_due(now=10, owner='A')
        result = digest('first')
        self.assertEqual(self.a.complete(token,result_sha256=result,now=11),'COMMITTED_LOCAL_ONLY')
        self.assertEqual(self.a.complete(token,result_sha256=result,now=12),'REPLAY')
        self.assertEqual(self.a.db.execute('SELECT completed_at FROM work').fetchone()[0],11)


if __name__=='__main__': unittest.main(verbosity=2)
