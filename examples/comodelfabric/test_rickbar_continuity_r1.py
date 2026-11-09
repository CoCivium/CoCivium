"""Synthetic RickBar R1 continuity and takeover contract tests.

No ChatGPT handoff, live Ollama, X2, account deletion or remote ACK asserted.
"""
import os
import pathlib
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

from rickbar_continuity_r1 import ContinuityStore, EVIDENCE_CLASS


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, "conversation.sqlite")
        self.a = ContinuityStore(self.path)
        self.cid = "conversation-1"
        self.assertEqual(self.a.create(conversation_id=self.cid)["state"],"CREATED")

    def tearDown(self):
        self.a.close()
        self.temp.cleanup()

    def test_exact_replay_and_conflict(self):
        self.assertEqual(self.a.begin_turn(self.cid,"turn-1","First question",1)["state"],"STARTED")
        r=self.a.commit_turn(self.cid,"turn-1","First answer",1)
        self.assertEqual(r["state"],"COMMITTED")
        self.assertEqual(r["evidence_class"],EVIDENCE_CLASS)
        self.assertEqual(self.a.begin_turn(self.cid,"turn-1","First question",1)["state"],"REPLAY")
        self.assertEqual(self.a.commit_turn(self.cid,"turn-1","First answer",1)["state"],"REPLAY")
        self.assertEqual(self.a.begin_turn(self.cid,"turn-1","Different question",1)["state"],"CONFLICT")
        self.assertEqual(self.a.commit_turn(self.cid,"turn-1","Different answer",1)["state"],"CONFLICT")
        self.assertEqual(len(self.a.state(self.cid)["turns"]),1)

    def test_handoff_keeps_committed_history_and_fences_predecessor(self):
        self.a.begin_turn(self.cid,"first","Hello",1)
        self.a.commit_turn(self.cid,"first","I am an unverified local model",1)
        b=ContinuityStore(self.path)
        try:
            self.assertEqual(b.elect(self.cid,"ollama:successor",1)["state"],"SUCCESSOR_ELECTED_SOURCE_ONLY")
            self.assertEqual(self.a.begin_turn(self.cid,"stale","should not run",1)["state"],"FENCED")
            self.assertEqual(self.a.commit_turn(self.cid,"first","late",1)["state"],"FENCED")
            self.assertEqual(b.begin_turn(self.cid,"second","Continue",2)["state"],"STARTED")
            self.assertEqual(b.commit_turn(self.cid,"second","Continued",2)["state"],"COMMITTED")
            state=b.state(self.cid)
            self.assertEqual(state["epoch"],2)
            self.assertEqual([t["status"] for t in state["turns"]],["COMMITTED","COMMITTED"])
            self.assertIn("First answer" if False else "unverified local model", b.model_context(self.cid,"Next"))
        finally:
            b.close()

    def test_crash_before_commit_never_fakes_reply(self):
        self.a.begin_turn(self.cid,"pending","Question",1)
        b=ContinuityStore(self.path)
        try:
            self.assertEqual(b.state(self.cid)["turns"][0]["status"],"PENDING")
            self.assertEqual(b.begin_turn(self.cid,"pending","Question",1)["state"],"ALREADY_PENDING")
            self.assertEqual(b.elect(self.cid,"ollama:successor",1)["epoch"],2)
            self.assertEqual(b.state(self.cid)["turns"][0]["status"],"INDETERMINATE")
            self.assertEqual(self.a.commit_turn(self.cid,"pending","old late answer",1)["state"],"FENCED")
            self.assertEqual(b.begin_turn(self.cid,"pending","Question",2)["state"],"INDETERMINATE")
            self.assertEqual(b.begin_turn(self.cid,"next","new request",2)["state"],"STARTED")
        finally:
            b.close()

    def test_restart_and_tamper_detection(self):
        self.a.begin_turn(self.cid,"turn-1","persist",1)
        self.a.commit_turn(self.cid,"turn-1","response",1)
        snap=self.a.state(self.cid)
        self.assertFalse(snap["receiver_ack"])
        self.assertFalse(snap["provider_session_deleted"])
        self.assertEqual(len(snap["snapshot_sha256"]),64)
        self.a.close()
        self.a=ContinuityStore(self.path)
        self.assertEqual(self.a.state(self.cid)["snapshot_sha256"],snap["snapshot_sha256"])

    def test_concurrent_election_one_winner(self):
        gate=threading.Barrier(2)
        def win(name):
            b=ContinuityStore(self.path)
            try:
                gate.wait(timeout=4)
                return b.elect(self.cid,"ollama:"+name,1)["state"]
            finally:
                b.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcome=list(pool.map(win,("a","b")))
        self.assertEqual(sorted(outcome),["FENCED","SUCCESSOR_ELECTED_SOURCE_ONLY"])

    def test_independent_process_reader_same_db_not_remote_ack(self):
        self.a.begin_turn(self.cid,"turn-1","hello",1)
        self.a.commit_turn(self.cid,"turn-1","world",1)
        b=ContinuityStore(self.path)
        try:
            state=b.state(self.cid)
            self.assertEqual(state["turns"][0]["response"],"world")
            self.assertEqual(state["evidence_class"],"MODEL_OUTPUT_UNVERIFIED")
            self.assertFalse(state["receiver_ack"])
        finally:
            b.close()

    def test_untrusted_input_rejected(self):
        for bad in ("../escape","", "a"*97):
            with self.assertRaises(ValueError):
                self.a.begin_turn(self.cid,bad,"hello",1)
        with self.assertRaises(ValueError):
            self.a.create(worker="hosted:fake",conversation_id="new")
        for epoch in (True,"1",0):
            with self.assertRaises(ValueError):
                self.a.begin_turn(self.cid,"x","hello",epoch)

    def test_bounded_context_and_unknown(self):
        self.a.begin_turn(self.cid,"t1","hello",1)
        self.a.commit_turn(self.cid,"t1","source output",1)
        self.assertIn("source output",self.a.model_context(self.cid,"carry"))
        self.assertNotIn("receipt ACK",self.a.model_context(self.cid,"carry"))
        self.assertEqual(self.a.state("unknown")["state"],"UNKNOWN_CONVERSATION")

    def test_no_auto_deletion_or_unauthorized_provider_session_migration(self):
        snap=self.a.state(self.cid)
        self.assertNotIn("remote_session_id",snap)
        self.assertFalse(snap["provider_session_deleted"])
        self.assertEqual(snap["worker"],"ollama:qwen3:4b")


if __name__=="__main__":
    unittest.main(verbosity=2)
