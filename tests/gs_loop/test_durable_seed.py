import os, sqlite3, tempfile, unittest

"""Isolated durable seed test: not X2 deployed; 24h survival NOT tested."""

class DurableSeed:
    def __init__(self, path):
        self.db=sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('CREATE TABLE IF NOT EXISTS seed(id TEXT PRIMARY KEY, epoch INTEGER NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY, seed_id TEXT NOT NULL, epoch INTEGER NOT NULL, payload TEXT NOT NULL)')
        self.db.commit()
    def elect(self, seed_id):
        with self.db:
            self.db.execute('INSERT INTO seed VALUES (?,0) ON CONFLICT(id) DO NOTHING',(seed_id,))
            self.db.execute('UPDATE seed SET epoch=epoch+1 WHERE id=?',(seed_id,))
            return self.db.execute('SELECT epoch FROM seed WHERE id=?',(seed_id,)).fetchone()[0]
    def elect_if_current(self, seed_id, expected_epoch):
        """Atomically acquire a successor epoch only from the expected epoch.

        A stale caller cannot preempt a more recent owner. None means fenced.
        This fixture still does not implement distributed authentication/leases.
        """
        if isinstance(expected_epoch, bool) or not isinstance(expected_epoch, int) or expected_epoch < 0:
            raise ValueError('expected_epoch must be a nonnegative integer')
        with self.db:
            changed = self.db.execute(
                'UPDATE seed SET epoch=epoch+1 WHERE id=? AND epoch=?',
                (seed_id, expected_epoch)).rowcount
            return expected_epoch + 1 if changed == 1 else None

    def commit(self, seed_id, epoch, event_id, payload):
        with self.db:
            current=self.db.execute('SELECT epoch FROM seed WHERE id=?',(seed_id,)).fetchone()
            if not current or current[0]!=epoch:return 'FENCED'
            old=self.db.execute('SELECT seed_id,epoch,payload FROM receipts WHERE id=?',(event_id,)).fetchone()
            if old:return 'REPLAY' if old==(seed_id,epoch,payload) else 'CONFLICT'
            self.db.execute('INSERT INTO receipts VALUES (?,?,?,?)',(event_id,seed_id,epoch,payload))
            return 'COMMITTED'
    def close(self):self.db.close()

class Tests(unittest.TestCase):
    def test_restart_handoff_and_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,'seed.db')
            a=DurableSeed(path); e1=a.elect('seed'); self.assertEqual(a.commit('seed',e1,'evt','verified'),'COMMITTED'); a.close()
            b=DurableSeed(path); self.assertEqual(b.commit('seed',e1,'evt','verified'),'REPLAY'); e2=b.elect('seed'); self.assertEqual(e2,e1+1)
            self.assertEqual(b.commit('seed',e1,'late','stale'),'FENCED'); self.assertEqual(b.commit('seed',e2,'next','verified'),'COMMITTED'); b.close()
            c=DurableSeed(path); self.assertEqual(c.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],2); c.close()
    def test_conflict_after_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,'seed.db'); a=DurableSeed(path); e=a.elect('s'); a.commit('s',e,'x','A'); a.close()
            b=DurableSeed(path); self.assertEqual(b.commit('s',e,'x','B'),'CONFLICT'); b.close()


    def test_ten_duplicate_acks_one_receipt(self):
        # This models duplicate transport delivery, not proof of live session fan-in.
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,'seed.db')
            a=DurableSeed(path); epoch=a.elect('seed')
            results=[a.commit('seed',epoch,'ack:one','same-request') for _ in range(10)]
            self.assertEqual(results,['COMMITTED']+['REPLAY']*9)
            self.assertEqual(a.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],1)
            self.assertEqual(a.db.execute('SELECT COUNT(*) FROM seed').fetchone()[0],1)
            a.close()

    def test_separate_receiver_reopens_checkpoint_after_handoff(self):
        # Independent SQLite connection is not independent machine or CoEx ACK.
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,'seed.db')
            source=DurableSeed(path)
            old=source.elect('seed')
            self.assertEqual(source.commit('seed',old,'evt1','A'),'COMMITTED')
            receiver=DurableSeed(path)
            self.assertEqual(receiver.db.execute(
                'SELECT payload FROM receipts WHERE id=?',('evt1',)).fetchone()[0],'A')
            new=receiver.elect('seed')
            self.assertEqual(source.commit('seed',old,'late','B'),'FENCED')
            self.assertEqual(receiver.commit('seed',new,'evt2','C'),'COMMITTED')
            self.assertEqual(source.db.execute(
                'SELECT payload FROM receipts WHERE id=?',('evt2',)).fetchone()[0],'C')
            receiver.close(); source.close()

    def test_replayed_old_epoch_cannot_claim_current_effect(self):
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,'seed.db')
            a=DurableSeed(path)
            old=a.elect('seed')
            self.assertEqual(a.commit('seed',old,'first','A'),'COMMITTED')
            next_epoch=a.elect('seed')
            self.assertEqual(a.commit('seed',old,'first','A'),'FENCED')
            self.assertEqual(a.commit('seed',next_epoch,'first','A'),'CONFLICT')
            self.assertEqual(a.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],1)
            a.close()


    def test_atomic_epoch_election_rejects_stale_winner(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'seed.db')
            a, b = DurableSeed(path), DurableSeed(path)
            old = a.elect('seed')
            self.assertEqual(b.elect_if_current('seed', old), old + 1)
            self.assertIsNone(a.elect_if_current('seed', old))
            self.assertEqual(a.commit('seed', old, 'late', 'stale'), 'FENCED')
            self.assertEqual(a.db.execute('SELECT epoch FROM seed').fetchone()[0], old + 1)
            a.close(); b.close()
    def test_two_simultaneous_successors_one_wins(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'seed.db')
            parent = DurableSeed(path)
            epoch = parent.elect('seed')
            barrier = Barrier(2)
            def compete():
                client = DurableSeed(path)
                try:
                    barrier.wait(timeout=3)
                    return client.elect_if_current('seed', epoch)
                finally:
                    client.close()
            with ThreadPoolExecutor(max_workers=2) as workers:
                answers = list(workers.map(lambda unused: compete(), range(2)))
            self.assertEqual(answers.count(epoch + 1), 1)
            self.assertEqual(answers.count(None), 1)
            self.assertEqual(parent.db.execute('SELECT epoch FROM seed').fetchone()[0], epoch + 1)
            parent.close()
    def test_atomic_epoch_election_unknown_or_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            a = DurableSeed(os.path.join(d, 'seed.db'))
            self.assertIsNone(a.elect_if_current('missing', 0))
            for invalid in (-1, True, '1'):
                with self.assertRaises(ValueError):
                    a.elect_if_current('seed', invalid)
            a.close()

if __name__=='__main__':unittest.main(verbosity=2)
