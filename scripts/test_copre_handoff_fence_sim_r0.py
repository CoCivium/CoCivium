"""CoPre local handoff fencing simulation; no external effects."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
m_path=Path(__file__).with_name("copre_handoff_fence_sim_r0.py")
s=importlib.util.spec_from_file_location("copre_handoff_fence_sim_r0",m_path)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

KEY={"work_id":"CoAll.CoPreGeneric.CrossAudience.20261109",
     "source_revision":"63b41ead8797e5a781699f32bcbc77b78bdbd7af",
     "effect_key":"sim:copre:one-public-source-read"}

class HandoffSimulation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"handoff.sqlite3"
        self.db=m.connect(self.path)
    def tearDown(self):
        self.db.close();self.tmp.cleanup()
    def claim(self,actor="a",**overrides):
        return m.reserve(self.db,actor=actor,**(KEY|overrides))
    def test_local_one_commit_after_duplicate(self):
        a=self.claim()
        self.assertEqual(a["state"],"RESERVED")
        self.assertEqual(m.commit(self.db,effect_key=KEY["effect_key"],actor="a",epoch=a["epoch"],receipt="r1"),"COMMITTED_LOCAL_LEDGER_ONLY")
        self.assertEqual(self.claim()["state"],"DUPLICATE_COMMITTED")
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],1)
    def test_restart_does_not_double_commit(self):
        a=self.claim()
        self.assertEqual(m.commit(self.db,effect_key=KEY["effect_key"],actor="a",epoch=a["epoch"],receipt="r1"),"COMMITTED_LOCAL_LEDGER_ONLY")
        self.db.close();self.db=m.connect(self.path)
        self.assertEqual(self.claim(actor="b")["state"],"DUPLICATE_COMMITTED")
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],1)
    def test_reclaim_after_uncommitted_crash_fences_old_writer(self):
        a=self.claim(actor="dead")
        b=self.claim(actor="live")
        self.assertEqual(b["epoch"],a["epoch"]+1)
        self.assertEqual(m.commit(self.db,effect_key=KEY["effect_key"],actor="dead",epoch=a["epoch"],receipt="bad"),"HELD_STALE_WRITER")
        self.assertEqual(m.commit(self.db,effect_key=KEY["effect_key"],actor="live",epoch=b["epoch"],receipt="good"),"COMMITTED_LOCAL_LEDGER_ONLY")
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],1)
    def test_same_actor_replay_no_epoch_bump(self):
        a=self.claim();b=self.claim()
        self.assertEqual(b,{"state":"ALREADY_RESERVED","epoch":a["epoch"]})
    def test_source_revision_conflict_held(self):
        self.claim()
        self.assertEqual(self.claim(source_revision="future-stale")["state"],"HELD_SOURCE_OR_WORK_CONFLICT")
    def test_workid_conflict_held(self):
        self.claim()
        self.assertEqual(self.claim(work_id="another")["state"],"HELD_SOURCE_OR_WORK_CONFLICT")
    def test_receipt_conflict_held(self):
        a=self.claim()
        self.assertEqual(m.commit(self.db,effect_key=KEY["effect_key"],actor="a",epoch=a["epoch"],receipt="r1"),"COMMITTED_LOCAL_LEDGER_ONLY")
        self.assertEqual(m.commit(self.db,effect_key=KEY["effect_key"],actor="a",epoch=a["epoch"],receipt="r2"),"HELD_RECEIPT_CONFLICT")
    def test_no_commit_without_claim(self):
        self.assertEqual(m.commit(self.db,effect_key="x",actor="a",epoch=1,receipt="r1"),"HELD_NO_RESERVATION")
    def test_no_empty_identifiers(self):
        self.assertEqual(self.claim(effect_key=" ")["state"],"HELD_INVALID_IDENTITY")
    def test_no_empty_receipt(self):
        a=self.claim()
        self.assertEqual(m.commit(self.db,effect_key=KEY["effect_key"],actor="a",epoch=a["epoch"],receipt=""),"HELD_MISSING_RECEIPT_OR_EPOCH")
    def test_external_effect_never_proven(self):
        a=self.claim()
        m.commit(self.db,effect_key=KEY["effect_key"],actor="a",epoch=a["epoch"],receipt="r1")
        snap=m.snapshot(self.db)
        self.assertFalse(snap["external_effects_proven"])
        self.assertFalse(snap["receiver_readproof"])
        self.assertFalse(snap["exactly_once_external"])
    def test_uncommitted_run_records_no_effect(self):
        self.claim()
        self.db.close();self.db=m.connect(self.path)
        self.assertEqual(m.snapshot(self.db)["ledger_commits"],0)

if __name__=="__main__":
    unittest.main()
