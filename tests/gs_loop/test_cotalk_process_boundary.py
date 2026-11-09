"""Cross-process CoTalk handoff fixture using the already tested SQLite Seed.

These are *local subprocess* boundaries, not independent authenticated hosts,
CoStead/X2 runtime, provider-session federation, or 24-hour continuity.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_cotalk_recovery import Readproof, RecoveryCoordinator
from test_durable_seed import DurableSeed


CHILD_READ = r'''
import json, os, sys
from dataclasses import asdict
from test_cotalk_recovery import receiver_read_checkpoint
path, receiver, seed_id, work_id, epoch, event_id = sys.argv[1:]
proof = receiver_read_checkpoint(path, receiver, seed_id, work_id,
                                 int(epoch), event_id)
print(json.dumps({'pid': os.getpid(),
                  'proof': asdict(proof) if proof else None}, sort_keys=True))
'''

CHILD_ELECT = r'''
import json, os, sys
from test_durable_seed import DurableSeed
path, seed_id, expected_epoch = sys.argv[1:]
seed = DurableSeed(path)
try:
    result = seed.elect_if_current(seed_id, int(expected_epoch))
    print(json.dumps({'pid': os.getpid(), 'epoch': result}, sort_keys=True))
finally:
    seed.close()
'''


class SubprocessHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'seed.sqlite')
        self.seed = DurableSeed(self.path)
        self.worker = RecoveryCoordinator(self.seed, self.path)
        for _ in range(3):
            self.worker.observe('blocked', expected_to_work=True)
        self.assertEqual(self.worker.status, 'STALLED')
        self.assertEqual(self.worker.checkpoint('checkpoint-from-producer'), 'COMMITTED')

    def tearDown(self):
        self.seed.close()
        self.tmp.cleanup()

    def child(self, code, *arguments, expected_success=True):
        proc = subprocess.run(
            [sys.executable, '-c', code, *(str(a) for a in arguments)],
            cwd=str(Path(__file__).resolve().parent),
            capture_output=True, text=True, timeout=12, check=False,
        )
        if expected_success:
            self.assertEqual(proc.returncode, 0, proc.stderr)
            record = json.loads(proc.stdout)
            self.assertNotEqual(record['pid'], os.getpid())
            return record
        return proc

    def receiver_read(self, *, receiver='successor', work_id='work-1', event_id=None,
                      expected_success=True):
        return self.child(CHILD_READ, self.path, receiver, 'co-seed', work_id,
                          self.worker.epoch, event_id or self.worker.checkpoint_id,
                          expected_success=expected_success)

    def test_subprocess_readback_survives_exit_restart_and_fences_old_worker(self):
        observed = self.receiver_read()
        proof = Readproof(**observed['proof'])
        self.assertEqual(self.worker.handoff(True, proof),
                         'FIXTURE_READBACK_MATCHED_NOT_EXTERNAL_ACK')
        self.assertEqual(self.seed.commit('co-seed', 1, 'late-effect', 'late'), 'FENCED')
        self.assertEqual(self.seed.commit('co-seed', 2, 'successor-effect', 'ok'), 'COMMITTED')
        self.seed.close()
        self.seed = DurableSeed(self.path)
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 2)
        self.assertEqual(self.seed.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0], 2)
        self.assertEqual(self.seed.db.execute(
            'SELECT payload_sha256 FROM fixture_receiver_reads').fetchone()[0],
            proof.payload_sha256)

    def test_wrong_work_id_cannot_produce_readproof(self):
        self.assertIsNone(self.receiver_read(work_id='different-work')['proof'])
        self.assertEqual(self.worker.handoff(True, None), 'ACK_UNPROVEN')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)

    def test_receiver_id_must_not_impersonate_producer(self):
        proc = self.receiver_read(receiver='producer', expected_success=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('distinct fixture receiver required', proc.stderr)
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)

    def test_duplicate_child_reads_one_persisted_record(self):
        a = self.receiver_read()['proof']
        b = self.receiver_read()['proof']
        self.assertEqual(a, b)
        self.assertEqual(self.seed.db.execute(
            'SELECT COUNT(*) FROM fixture_receiver_reads').fetchone()[0], 1)

    def test_other_process_wins_cas_before_stale_handoff(self):
        proof = Readproof(**self.receiver_read()['proof'])
        contender = self.child(CHILD_ELECT, self.path, 'co-seed', 1)
        self.assertEqual(contender['epoch'], 2)
        self.assertEqual(self.worker.handoff(True, proof), 'STALE_LEASE_FENCED')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 2)
        self.assertEqual(self.seed.commit('co-seed', 1, 'stale', 'bad'), 'FENCED')

    def test_corrupted_checkpoint_after_child_read_fails_closed(self):
        proof = Readproof(**self.receiver_read()['proof'])
        self.seed.db.execute('UPDATE receipts SET payload=? WHERE id=?',
                             ('corrupted', self.worker.checkpoint_id))
        self.seed.db.commit()
        self.assertEqual(self.worker.handoff(True, proof), 'ACK_UNPROVEN')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
