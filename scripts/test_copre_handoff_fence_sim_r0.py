"""CoPre simulated lease fencing tests. No remote worker, no real-time proof."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

module_path=Path(__file__).with_name("copre_handoff_fence_sim_r0.py")
spec=importlib.util.spec_from_file_location("copre_handoff_fence_sim_r0", module_path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

KEY={
 "work_id":"CoAll.CoPreGeneric.CrossAudience.20261109",
 "source_revision":"63b41ead8797e5a781699f32bcbc77b78bdbd7af",
 "effect_key":"sim:copre:one-public-source-read"
}

class HandoffSimulation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"handoff.sqlite3"
        self.db=m.connect(self.path)
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def claim(self,actor="a",now=100,ttl=10,**overrides):
        return m.reserve(self.db,actor=actor,now=now,ttl=ttl,**(KEY|overrides))
    def finish(self,actor,epoch,receipt="r1",now=101,effect_key=None):
        return m.commit(self.db,effect_key=effect_key or KEY["effect_key"],
                        actor=actor,epoch=epoch,receipt=receipt,now=now)

    def test_local_commit_dedupes(self):
        a=self.claim()
        self.assertEqual(self.finish("a",a["epoch"]),"COMMITTED_LOCAL_LEDGER_ONLY")
        self.assertEqual(self.claim()["state"],"DUPLICATE_COMMITTED")
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],1)
    def test_restart_does_not_double_ledger_commit(self):
        a=self.claim()
        self.finish("a",a["epoch"])
        self.db.close(); self.db=m.connect(self.path)
        self.assertEqual(self.claim(actor="b",now=200)["state"],"DUPLICATE_COMMITTED")
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],1)
    def test_second_actor_held_while_first_lease_active(self):
        a=self.claim(actor="live",now=100)
        b=self.claim(actor="thief",now=109)
        self.assertEqual(b["state"],"HELD_ACTIVE_LEASE")
        self.assertEqual(self.finish("live",a["epoch"],now=109),"COMMITTED_LOCAL_LEDGER_ONLY")
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],1)
    def test_exact_boundary_reclaim_fences_old_writer(self):
        a=self.claim(actor="dead",now=100,ttl=10)
        b=self.claim(actor="live",now=110)
        self.assertEqual(b["state"],"RESERVED")
        self.assertEqual(b["epoch"],a["epoch"]+1)
        self.assertEqual(self.finish("dead",a["epoch"],"bad",now=110),"HELD_STALE_WRITER")
        self.assertEqual(self.finish("live",b["epoch"],"good",now=111),"COMMITTED_LOCAL_LEDGER_ONLY")
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],1)
    def test_same_actor_replay_retains_active_epoch(self):
        a=self.claim()
        b=self.claim()
        self.assertEqual(b,{"state":"ALREADY_RESERVED","epoch":a["epoch"],"lease_until":110})
    def test_same_actor_after_expiry_gets_new_epoch(self):
        a=self.claim()
        b=self.claim(now=111)
        self.assertEqual(b["epoch"],a["epoch"]+1)
        self.assertEqual(self.finish("a",a["epoch"],now=112),"HELD_STALE_WRITER")
    def test_expired_lease_cannot_commit_without_reclaim(self):
        a=self.claim()
        self.assertEqual(self.finish("a",a["epoch"],now=110),"HELD_EXPIRED_LEASE")
    def test_workid_conflict_held(self):
        self.claim()
        self.assertEqual(self.claim(work_id="unrelated")["state"],"HELD_SOURCE_OR_WORK_CONFLICT")
    def test_revision_conflict_held(self):
        self.claim()
        self.assertEqual(self.claim(source_revision="stale")["state"],"HELD_SOURCE_OR_WORK_CONFLICT")
    def test_conflicting_receipt_held(self):
        a=self.claim()
        self.finish("a",a["epoch"],receipt="receipt1")
        self.assertEqual(self.finish("a",a["epoch"],receipt="receipt2"),"HELD_RECEIPT_CONFLICT")
    def test_no_commit_without_reservation(self):
        self.assertEqual(self.finish("a",1,effect_key="missing"),"HELD_NO_RESERVATION")
    def test_empty_identity_and_receipt_rejected(self):
        self.assertEqual(self.claim(effect_key=" ")["state"],"HELD_INVALID_IDENTITY")
        a=self.claim()
        self.assertEqual(self.finish("a",a["epoch"],receipt=" "),"HELD_MISSING_RECEIPT_OR_EPOCH")
    def test_untrusted_time_and_ttl_rejected(self):
        self.assertEqual(self.claim(now=-1)["state"],"HELD_INVALID_SIMULATED_TIME_OR_TTL")
        self.assertEqual(self.claim(ttl=0)["state"],"HELD_INVALID_SIMULATED_TIME_OR_TTL")
        self.assertEqual(self.claim(now=True)["state"],"HELD_INVALID_SIMULATED_TIME_OR_TTL")
        self.assertEqual(self.claim(ttl=3601)["state"],"HELD_INVALID_SIMULATED_TIME_OR_TTL")
    def test_crash_uncommitted_is_not_effect_claim(self):
        self.claim()
        self.db.close();self.db=m.connect(self.path)
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],0)
    def test_external_effect_never_claimed(self):
        a=self.claim()
        self.finish("a",a["epoch"])
        snap=m.snapshot(self.db)
        self.assertFalse(snap["receiver_readproof"])
        self.assertFalse(snap["external_effects_proven"])
        self.assertFalse(snap["exactly_once_external"])
        self.assertEqual(snap["time_source"],"SIMULATED_CALLER_SUPPLIED_UNTRUSTED")

if __name__=="__main__":
    unittest.main()
