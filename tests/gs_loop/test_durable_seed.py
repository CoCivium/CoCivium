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

if __name__=='__main__':unittest.main(verbosity=2)
