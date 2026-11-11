"""Isolated durable receiver contract; not an X2 integration test."""
import os
import sqlite3
import tempfile
import unittest


def connect(path):
    db = sqlite3.connect(path)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS lease (work_id TEXT PRIMARY KEY, epoch INTEGER NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS receipts (event_id TEXT PRIMARY KEY, work_id TEXT NOT NULL, payload TEXT NOT NULL)')
    db.commit()
    return db


def commit_event(db, work_id, epoch, event_id, payload):
    with db:
        lease = db.execute('SELECT epoch FROM lease WHERE work_id=?', (work_id,)).fetchone()
        if lease is None or lease[0] != epoch:
            return 'STALE'
        prior = db.execute('SELECT work_id, payload FROM receipts WHERE event_id=?', (event_id,)).fetchone()
        if prior is not None:
            return 'DUPLICATE' if prior == (work_id, payload) else 'CONFLICT'
        db.execute('INSERT INTO receipts VALUES (?,?,?)', (event_id, work_id, payload))
        return 'COMMITTED'


class DurableReceiverTests(unittest.TestCase):
    def test_restart_replay_fencing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, 'receiver.sqlite')
            db = connect(path)
            with db:
                db.execute('INSERT INTO lease VALUES (?,?)', ('seed', 1))
            self.assertEqual(commit_event(db, 'seed', 1, 'e1', 'payload'), 'COMMITTED')
            db.close()
            db = connect(path)
            self.assertEqual(commit_event(db, 'seed', 1, 'e1', 'payload'), 'DUPLICATE')
            self.assertEqual(commit_event(db, 'seed', 1, 'e1', 'changed'), 'CONFLICT')
            with db:
                db.execute('UPDATE lease SET epoch=2 WHERE work_id=?', ('seed',))
            self.assertEqual(commit_event(db, 'seed', 1, 'e2', 'late'), 'STALE')
            self.assertEqual(commit_event(db, 'seed', 2, 'e2', 'fresh'), 'COMMITTED')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0], 2)
            db.close()

    def test_rollback_on_error(self):
        with tempfile.TemporaryDirectory() as temp:
            db = connect(os.path.join(temp, 'receiver.sqlite'))
            with self.assertRaises(RuntimeError):
                with db:
                    db.execute('INSERT INTO lease VALUES (?,?)', ('seed', 1))
                    raise RuntimeError('simulated failure before commit')
            self.assertIsNone(db.execute('SELECT epoch FROM lease WHERE work_id=?', ('seed',)).fetchone())
            db.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
