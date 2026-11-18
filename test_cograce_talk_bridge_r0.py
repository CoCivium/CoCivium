"""Cross-contract shadow exercise: CoGrace cannot grant CoTalk authority."""
import unittest
from scripts.CoGraceTalkBridgeR0 import reconcile
from scripts.CoSessionGraceRecoveryR0 import Session, Peer, Measure

def session(**kwargs):
    d=dict(session_id="s1",work_id="w1",revision="sha1",state="ACTIVE",
           consent_to_peer_aid=True)
    d.update(kwargs)
    return Session(**d)
def peer(**kwargs):
    d=dict(session_id="s2",capabilities=("REVIEW",),availability="AVAILABLE",
           consent_to_aid=True,health="HEALTHY_VERIFIED",source_revision="sha2",
           evidence_ref="public:peer")
    d.update(kwargs)
    return Peer(**d)
def windows(adverse=True):
    def one(a,b):
        return (Measure("progress",0,"receipts/hour","trusted:fixture",b,
                        "fixture:verifier",a,b,adverse),)
    return (one("2026-11-08T10:00Z","2026-11-08T11:00Z"),
            one("2026-11-08T11:00Z","2026-11-08T12:00Z"))
def run(s=None,ps=None,w=None,**kwargs):
    return reconcile(s or session(),w if w is not None else windows(),
                     ps if ps is not None else (peer(),),
                     source_revision="sha1",as_of_utc="2026-11-08T12:30:00Z",**kwargs)

class BridgeTest(unittest.TestCase):
    def test_healthy_quiet_does_not_invite_peer(self):
        out=run(s=session(healthy_quiet=True))
        self.assertEqual(out["coordination"],"NO_FANOUT")
        self.assertFalse(out["actual_handoff"])
    def test_well_fed_unstalled_does_not_invite_peer(self):
        out=run(w=windows(False))
        self.assertEqual(out["coordination"],"NO_FANOUT")
    def test_no_consent_does_not_invite_peer(self):
        out=run(s=session(consent_to_peer_aid=False))
        self.assertEqual(out["coordination"],"NO_FANOUT")
    def test_no_peer_does_not_invite_peer(self):
        out=run(ps=())
        self.assertEqual(out["coordination"],"NO_FANOUT")
    def test_stale_windows_cannot_trigger_fanout(self):
        out=reconcile(session(),windows(),(peer(),),source_revision="sha1",
                      as_of_utc="2026-11-12T12:30:00Z")
        self.assertEqual(out["coordination"],"NO_FANOUT")
    def test_candidate_no_receiver_is_not_handoff(self):
        out=run()
        self.assertEqual(out["coordination"],"REVIEW_CANDIDATE_ONLY")
        self.assertEqual(out["decision"]["verdict"],"HOLD")
        self.assertFalse(out["external_ack"])
    def test_claimed_receiver_and_lease_still_not_handoff(self):
        out=run(receiver_attested=True,lease_attested=True)
        self.assertEqual(out["health"]["verdict"],"PROPOSE_REVERSIBLE_HANDOFF")
        self.assertEqual(out["decision"]["verdict"],"HOLD")
        self.assertFalse(out["actual_handoff"])
        self.assertFalse(out["external_ack"])
    def test_two_peers_trigger_challenge_not_exec(self):
        out=run(ps=(peer(),peer(session_id="s3",evidence_ref="public:p3")))
        self.assertEqual(out["decision"]["verdict"],"HOLD")  # same option, no elected actuator
    def test_revision_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_REVISION"):
            reconcile(session(),windows(),(peer(),),source_revision="stale")
    def test_quiet_when_no_health_observation(self):
        out=run(w=())
        self.assertEqual(out["coordination"],"NO_FANOUT")
    def test_paused_not_overridden(self):
        out=run(s=session(pause_requested=True))
        self.assertEqual(out["coordination"],"NO_FANOUT")
if __name__=="__main__":
    unittest.main()
