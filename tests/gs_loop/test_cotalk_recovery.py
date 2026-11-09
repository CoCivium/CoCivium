"""CoTalkItOut synthetic handoff with exact persisted checkpoint readback.

Separate SQLite connections are not independent authenticated receivers.
This fixture neither controls ChatGPT sessions nor proves X2/CoStead runtime.
"""
import hashlib
import json
import os
import sqlite3
import tempfile
import unittest
from dataclasses import dataclass
from test_durable_seed import DurableSeed
from test_loop_guard import LoopGuard


@dataclass(frozen=True)
class Readproof:
    receiver_id: str
    seed_id: str
    work_id: str
    epoch: int
    event_id: str
    payload_sha256: str


def receiver_read_checkpoint(path, receiver_id, seed_id, work_id, epoch, event_id):
    """Read exact checkpoint through a distinct DB connection, then record a fixture ACK.

    The receiver ID is asserted, not cryptographically authenticated.
    """
    if not receiver_id or receiver_id == 'producer':
        raise ValueError('distinct fixture receiver required')
    with sqlite3.connect(path) as db:
        row = db.execute(
            'SELECT epoch, payload FROM receipts WHERE id=? AND seed_id=?',
            (event_id, seed_id)).fetchone()
        if row is None or row[0] != epoch:
            return None
        try:
            decoded = json.loads(row[1])
        except (TypeError, ValueError):
            return None
        if decoded.get('work_id') != work_id or decoded.get('epoch') != epoch:
            return None
        digest = hashlib.sha256(row[1].encode('utf-8')).hexdigest()
        db.execute('''CREATE TABLE IF NOT EXISTS fixture_receiver_reads(
            seed_id TEXT NOT NULL, event_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL, epoch INTEGER NOT NULL,
            payload_sha256 TEXT NOT NULL,
            PRIMARY KEY(seed_id,event_id,receiver_id))''')
        db.execute('''INSERT INTO fixture_receiver_reads
          (seed_id,event_id,receiver_id,epoch,payload_sha256) VALUES(?,?,?,?,?)
          ON CONFLICT(seed_id,event_id,receiver_id) DO NOTHING''',
          (seed_id,event_id,receiver_id,epoch,digest))
    return Readproof(receiver_id, seed_id, work_id, epoch, event_id, digest)


class RecoveryCoordinator:
    """A bounded test fixture; no provider, network or external effects."""
    def __init__(self, seed, db_path, seed_id='co-seed', work_id='work-1'):
        self.seed, self.db_path = seed, db_path
        self.seed_id, self.work_id = seed_id, work_id
        self.guard = LoopGuard(max_repeats=2, max_steps=12)
        self.blocker_id = None
        self.epoch = seed.elect(seed_id)
        self.checkpoint_id = None
        self.status = 'HEALTHY_IDLE'

    def observe(self, fingerprint=None, progress=False, expected_to_work=False):
        if not expected_to_work:
            return self.status
        state = self.guard.observe(fingerprint, verified_progress=progress)
        if state == 'PROGRESS':
            self.status = 'HEALTHY_ACTIVE'
        elif state.startswith('SUSPENDED'):
            self.status = 'STALLED'
            self.blocker_id = f'{self.seed_id}:stalled:{self.epoch}'
        else:
            self.status = 'HEALTHY_ACTIVE'
        return self.status

    def checkpoint(self, value):
        if self.status != 'STALLED' or not isinstance(value, str) or not value:
            return 'CHECKPOINT_DENIED'
        event_id = f'{self.seed_id}:{self.work_id}:checkpoint:{self.epoch}'
        payload = json.dumps({'seed_id': self.seed_id, 'work_id': self.work_id,
                              'epoch': self.epoch, 'value': value},
                             sort_keys=True, separators=(',', ':'))
        state = self.seed.commit(self.seed_id, self.epoch, event_id, payload)
        if state in ('COMMITTED', 'REPLAY'):
            self.checkpoint_id = event_id
        return state

    def handoff(self, permitted, readproof):
        if self.status != 'STALLED' or not permitted:
            return 'DENIED'
        if not self.checkpoint_id or not isinstance(readproof, Readproof):
            self.status = 'WAITING_ON_EVENT'
            return 'ACK_UNPROVEN'
        if (readproof.receiver_id == 'producer'
            or readproof.seed_id != self.seed_id
            or readproof.work_id != self.work_id
            or readproof.epoch != self.epoch
            or readproof.event_id != self.checkpoint_id):
            self.status = 'WAITING_ON_EVENT'
            return 'ACK_UNPROVEN'
        # Verify both the immutable checkpoint and a separately persisted receiver read.
        with sqlite3.connect(self.db_path) as db:
            checkpoint = db.execute(
                'SELECT epoch, payload FROM receipts WHERE id=? AND seed_id=?',
                (self.checkpoint_id, self.seed_id)).fetchone()
            try:
                receiver_row = db.execute('''SELECT epoch,payload_sha256 FROM fixture_receiver_reads
                    WHERE seed_id=? AND event_id=? AND receiver_id=?''',
                    (self.seed_id, self.checkpoint_id, readproof.receiver_id)).fetchone()
            except sqlite3.OperationalError:
                receiver_row = None
        digest = (hashlib.sha256(checkpoint[1].encode('utf-8')).hexdigest()
                  if checkpoint and checkpoint[0] == self.epoch else None)
        if not digest or digest != readproof.payload_sha256 or receiver_row != (self.epoch, digest):
            self.status = 'WAITING_ON_EVENT'
            return 'ACK_UNPROVEN'
        # Atomic compare-and-swap: a newer owner must never be displaced.
        next_epoch = self.seed.elect_if_current(self.seed_id, self.epoch)
        if next_epoch is None:
            self.status = 'WAITING_ON_EVENT'
            return 'STALE_LEASE_FENCED'
        self.epoch = next_epoch
        self.status = 'RECOVERING'
        return 'FIXTURE_READBACK_MATCHED_NOT_EXTERNAL_ACK'


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, 'seed.db')
        self.seed = DurableSeed(self.db_path)
        self.coordinator = RecoveryCoordinator(self.seed, self.db_path)
    def tearDown(self):
        self.seed.close()
        self.tmp.cleanup()
    def stall(self):
        for _ in range(3):
            self.coordinator.observe('stuck', expected_to_work=True)
    def proof(self, **changes):
        self.assertEqual(self.coordinator.checkpoint('exact payload'), 'COMMITTED')
        args = dict(path=self.db_path, receiver_id='successor', seed_id='co-seed',
                    work_id='work-1', epoch=self.coordinator.epoch,
                    event_id=self.coordinator.checkpoint_id)
        args.update(changes)
        return receiver_read_checkpoint(**args)
    def test_healthy_idle_is_not_zombie(self):
        for _ in range(20):
            self.assertEqual(self.coordinator.observe('idle'), 'HEALTHY_IDLE')
        self.assertIsNone(self.coordinator.blocker_id)
    def test_duplicate_stall_signals_one_blocker(self):
        self.stall()
        first = self.coordinator.blocker_id
        for _ in range(20):
            self.assertEqual(self.coordinator.observe('stuck', expected_to_work=True), 'STALLED')
        self.assertEqual(self.coordinator.blocker_id, first)
    def test_real_sqlite_readback_fences_predecessor(self):
        self.stall()
        proof = self.proof()
        old_epoch = self.coordinator.epoch
        self.assertEqual(self.coordinator.handoff(True, proof),
                         'FIXTURE_READBACK_MATCHED_NOT_EXTERNAL_ACK')
        self.assertEqual(self.seed.commit('co-seed', old_epoch, 'late', 'stale'), 'FENCED')
        self.assertEqual(self.seed.commit('co-seed', self.coordinator.epoch, 'new', 'ok'), 'COMMITTED')
        self.seed.close()
        self.seed = DurableSeed(self.db_path)
        self.assertEqual(self.seed.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0], 2)
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], old_epoch + 1)
    def test_no_unauthorized_handoff(self):
        self.stall()
        proof = self.proof()
        self.assertEqual(self.coordinator.handoff(False, proof), 'DENIED')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)
    def test_boolean_assertion_never_advances_lease(self):
        self.stall()
        self.assertEqual(self.coordinator.checkpoint('exact payload'), 'COMMITTED')
        self.assertEqual(self.coordinator.handoff(True, True), 'ACK_UNPROVEN')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)
    def test_wrong_work_id_cannot_be_read_as_matching(self):
        self.stall()
        self.assertIsNone(self.proof(work_id='another-work'))
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)
    def test_missing_checkpoint_denies_transfer(self):
        self.stall()
        self.assertEqual(self.coordinator.handoff(True, None), 'ACK_UNPROVEN')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)
    def test_forged_content_hash_is_rejected(self):
        from dataclasses import replace
        self.stall()
        proof = replace(self.proof(), payload_sha256='0' * 64)
        self.assertEqual(self.coordinator.handoff(True, proof), 'ACK_UNPROVEN')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)
    def test_no_double_handoff(self):
        self.stall()
        proof = self.proof()
        self.assertEqual(self.coordinator.handoff(True, proof),
                         'FIXTURE_READBACK_MATCHED_NOT_EXTERNAL_ACK')
        self.assertEqual(self.coordinator.handoff(True, proof), 'DENIED')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 2)
    def test_tampered_checkpoint_after_read_is_rejected(self):
        self.stall()
        proof = self.proof()
        self.seed.db.execute('UPDATE receipts SET payload=? WHERE id=?',
                             ('altered', self.coordinator.checkpoint_id))
        self.seed.db.commit()
        self.assertEqual(self.coordinator.handoff(True, proof), 'ACK_UNPROVEN')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 1)

    def test_stale_handoff_cannot_preempt_new_owner(self):
        self.stall()
        proof = self.proof()
        contender = DurableSeed(self.db_path)
        try:
            self.assertEqual(contender.elect_if_current('co-seed', 1), 2)
        finally:
            contender.close()
        self.assertEqual(self.coordinator.handoff(True, proof), 'STALE_LEASE_FENCED')
        self.assertEqual(self.coordinator.status, 'WAITING_ON_EVENT')
        self.assertEqual(self.seed.db.execute('SELECT epoch FROM seed').fetchone()[0], 2)
        self.assertEqual(self.seed.commit('co-seed', 1, 'late', 'stale'), 'FENCED')

if __name__ == '__main__': unittest.main(verbosity=2)
