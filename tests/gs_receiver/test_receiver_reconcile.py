"""Isolated CoReceiverReconcile+ test contract; NOT deployed on X2."""
import sqlite3
import unittest

SCHEMA = '''
CREATE TABLE work (id TEXT PRIMARY KEY, epoch INTEGER NOT NULL, status TEXT NOT NULL);
CREATE TABLE events (event_id TEXT PRIMARY KEY, work_id TEXT NOT NULL, epoch INTEGER NOT NULL, payload TEXT NOT NULL);
CREATE TABLE receipts (event_id TEXT PRIMARY KEY, work_id TEXT NOT NULL, payload TEXT NOT NULL);
'''

class Receiver:
    def __init__(self):
        self.db = sqlite3.connect(':memory:')
        self.db.executescript(SCHEMA)

    def seed(self, work_id):
        self.db.execute('INSERT INTO work VALUES (?, 1, ?)', (work_id, 'pending'))

    def handoff(self, work_id):
        self.db.execute('UPDATE work SET epoch=epoch+1 WHERE id=?', (work_id,))
        return self.db.execute('SELECT epoch FROM work WHERE id=?', (work_id,)).fetchone()[0]

    def submit(self, event_id, work_id, epoch, payload):
        with self.db:
            row = self.db.execute('SELECT epoch FROM work WHERE id=?', (work_id,)).fetchone()
            if not row or row[0] != epoch:
                return 'STALE'
            prior = self.db.execute('SELECT work_id, payload FROM receipts WHERE event_id=?', (event_id,)).fetchone()
            if prior:
                return 'DUPLICATE' if prior == (work_id, payload) else 'CONFLICT'
            self.db.execute('INSERT INTO events VALUES (?,?,?,?)', (event_id, work_id, epoch, payload))
            self.db.execute('INSERT INTO receipts VALUES (?,?,?)', (event_id, work_id, payload))
            self.db.execute('UPDATE work SET status=? WHERE id=?', ('received', work_id))
            return 'COMMITTED'

    def projection(self, work_id):
        return self.db.execute('SELECT status, epoch FROM work WHERE id=?', (work_id,)).fetchone()

class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.r = Receiver()
        self.r.seed('seed-1')

    def test_replay_and_handoff(self):
        self.assertEqual(self.r.submit('ev-1','seed-1',1,'sample'), 'COMMITTED')
        self.assertEqual(self.r.submit('ev-1','seed-1',1,'sample'), 'DUPLICATE')
        self.assertEqual(self.r.submit('ev-1','seed-1',1,'tampered'), 'CONFLICT')
        self.assertEqual(self.r.handoff('seed-1'), 2)
        self.assertEqual(self.r.submit('ev-2','seed-1',1,'late'), 'STALE')
        self.assertEqual(self.r.submit('ev-2','seed-1',2,'new'), 'COMMITTED')
        self.assertEqual(self.r.projection('seed-1'), ('received',2))
        self.assertEqual(self.r.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],2)

    def test_producer_sample_without_receiver_ack_is_not_verified(self):
        # A producer-side sample alone cannot establish receiver evidence.
        producer_sample = {'work_id': 'seed-1', 'cpu': 3.0, 'memory_gb': 66.9}
        self.assertEqual(producer_sample['work_id'], 'seed-1')
        self.assertEqual(self.r.projection('seed-1'), ('pending', 1))
        self.assertEqual(self.r.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0], 0)
        self.assertEqual(self.r.submit('ack-1', 'seed-1', 1, 'observer-verified'), 'COMMITTED')
        self.assertEqual(self.r.projection('seed-1'), ('received', 1))

    def test_no_unverified_projection(self):
        self.assertEqual(self.r.projection('seed-1'), ('pending',1))
        self.assertEqual(self.r.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
