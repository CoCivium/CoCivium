"""Durable Seed + once-only handoff simulation; no network, OS, or real effects."""
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class SeedLedger:
    def __init__(self, path):
        self.db = sqlite3.connect(str(path), isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS seeds(work_id TEXT PRIMARY KEY, payload TEXT NOT NULL, source_sha TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts(handoff_id TEXT PRIMARY KEY, work_id TEXT NOT NULL, recipient TEXT NOT NULL, state TEXT NOT NULL, UNIQUE(work_id,recipient));
        CREATE TABLE IF NOT EXISTS receipts(handoff_id TEXT PRIMARY KEY, observer TEXT NOT NULL, result TEXT NOT NULL);
        """)
    def seed(self, work_id, payload, source_sha):
        if not work_id or not source_sha: raise ValueError("MISSING_SEED_IDENTITY")
        encoded=json.dumps(payload,sort_keys=True,separators=(",",":"))
        self.db.execute("INSERT OR IGNORE INTO seeds VALUES (?,?,?)",(work_id,encoded,source_sha))
        actual=self.db.execute("SELECT payload,source_sha FROM seeds WHERE work_id=?",(work_id,)).fetchone()
        if actual!=(encoded,source_sha): raise ValueError("SEED_COLLISION_HOLD")
    def handoff(self, handoff_id, work_id, recipient, *, authorized):
        if not authorized: return "NOT_AUTHORIZED"
        if not self.db.execute("SELECT 1 FROM seeds WHERE work_id=?",(work_id,)).fetchone(): return "NO_SEED_HOLD"
        # Atomic uniqueness constraint elects one attempt even across connections.
        # A prior SELECT followed by INSERT raced and could raise IntegrityError.
        inserted=self.db.execute("INSERT OR IGNORE INTO attempts VALUES (?,?,?,?)",
                                 (handoff_id,work_id,recipient,"ATTEMPTED")).rowcount
        if inserted: return "ATTEMPTED_NOT_VERIFIED"
        exact=self.db.execute("SELECT work_id,recipient FROM attempts WHERE handoff_id=?",
                              (handoff_id,)).fetchone()
        if exact and exact!=(work_id,recipient): return "HANDOFF_ID_COLLISION_HOLD"
        existing=self.db.execute("SELECT handoff_id FROM attempts WHERE work_id=? AND recipient=?",
                                 (work_id,recipient)).fetchone()
        return "REPLAY_SAME_HANDOFF" if existing and existing[0]==handoff_id else "DUPLICATE_EFFECT_HOLD"
    def independent_receive(self,handoff_id,observer,result):
        if not observer: raise ValueError("INDEPENDENT_OBSERVER_REQUIRED")
        attempt=self.db.execute("SELECT recipient FROM attempts WHERE handoff_id=?",(handoff_id,)).fetchone()
        if not attempt: return "NO_ATTEMPT_HOLD"
        if attempt[0]==observer: return "SELF_ACK_HOLD"
        inserted=self.db.execute("INSERT OR IGNORE INTO receipts VALUES (?,?,?)",
                                 (handoff_id,observer,result)).rowcount
        if inserted: return "INDEPENDENT_FIXTURE_RECEIPT"
        existing=self.db.execute("SELECT observer,result FROM receipts WHERE handoff_id=?",
                                 (handoff_id,)).fetchone()
        return "RECEIPT_REPLAY" if existing==(observer,result) else "CONFLICTING_RECEIPT_HOLD"
    def counts(self):
        return tuple(self.db.execute("SELECT COUNT(*) FROM "+name).fetchone()[0] for name in ("seeds","attempts","receipts"))
    def close(self): self.db.close()

class SeedContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"seed.sqlite3"
        self.ledger=SeedLedger(self.path)
        self.ledger.seed("seed-1",{"intent":"sample"},"source-sha-1")
    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()
    def reopen(self):
        self.ledger.close()
        self.ledger=SeedLedger(self.path)
    def test_persist_across_renderer_restart(self):
        self.reopen()
        self.assertEqual(self.ledger.counts(),(1,0,0))
    def test_same_seed_is_idempotent(self):
        self.ledger.seed("seed-1",{"intent":"sample"},"source-sha-1")
        self.assertEqual(self.ledger.counts(),(1,0,0))
    def test_changed_seed_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"COLLISION"):
            self.ledger.seed("seed-1",{"intent":"tampered"},"source-sha-1")
    def test_unauthorized_handoff_is_rejected(self):
        self.assertEqual(self.ledger.handoff("handoff-1","seed-1","target",authorized=False),"NOT_AUTHORIZED")
        self.assertEqual(self.ledger.counts(),(1,0,0))
    def test_missing_seed_is_held(self):
        self.assertEqual(self.ledger.handoff("handoff-1","missing","target",authorized=True),"NO_SEED_HOLD")
    def test_once_only_handoff_across_restart(self):
        self.assertEqual(self.ledger.handoff("handoff-1","seed-1","target",authorized=True),"ATTEMPTED_NOT_VERIFIED")
        self.reopen()
        self.assertEqual(self.ledger.handoff("handoff-1","seed-1","target",authorized=True),"REPLAY_SAME_HANDOFF")
        self.assertEqual(self.ledger.handoff("handoff-2","seed-1","target",authorized=True),"DUPLICATE_EFFECT_HOLD")
        self.assertEqual(self.ledger.counts(),(1,1,0))
    def test_self_ack_is_rejected(self):
        self.ledger.handoff("handoff-1","seed-1","target",authorized=True)
        self.assertEqual(self.ledger.independent_receive("handoff-1","target","PASS"),"SELF_ACK_HOLD")
        self.assertEqual(self.ledger.counts(),(1,1,0))
    def test_distinct_observer_receipt_survives_restart(self):
        self.ledger.handoff("handoff-1","seed-1","target",authorized=True)
        self.assertEqual(self.ledger.independent_receive("handoff-1","independent-fixture","PASS"),"INDEPENDENT_FIXTURE_RECEIPT")
        self.reopen()
        self.assertEqual(self.ledger.counts(),(1,1,1))
        self.assertEqual(self.ledger.independent_receive("handoff-1","independent-fixture","PASS"),"RECEIPT_REPLAY")
    def test_conflicting_receipt_is_rejected(self):
        self.ledger.handoff("handoff-1","seed-1","target",authorized=True)
        self.ledger.independent_receive("handoff-1","independent-fixture","PASS")
        self.assertEqual(self.ledger.independent_receive("handoff-1","other-fixture","FAIL"),"CONFLICTING_RECEIPT_HOLD")
    def test_handoff_id_collision_different_target_holds(self):
        self.assertEqual(self.ledger.handoff("handoff-1","seed-1","target",authorized=True),
                         "ATTEMPTED_NOT_VERIFIED")
        self.assertEqual(self.ledger.handoff("handoff-1","seed-1","another",authorized=True),
                         "HANDOFF_ID_COLLISION_HOLD")
        self.assertEqual(self.ledger.counts(),(1,1,0))
    def test_contending_connections_elect_only_one_attempt(self):
        # Concurrency across independent SQLite connections to the same Seed.
        def contend(i):
            worker=SeedLedger(self.path)
            try:
                return worker.handoff(f"h-{i}","seed-1","target",authorized=True)
            finally:
                worker.close()
        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes=list(pool.map(contend,range(8)))
        self.assertEqual(outcomes.count("ATTEMPTED_NOT_VERIFIED"),1)
        self.assertEqual(outcomes.count("DUPLICATE_EFFECT_HOLD"),7)
        self.assertEqual(self.ledger.counts(),(1,1,0))

    def test_missing_attempt_cannot_claim_receipt(self):
        self.assertEqual(self.ledger.independent_receive("no-handoff","independent-fixture","PASS"),"NO_ATTEMPT_HOLD")
if __name__=="__main__": unittest.main()
