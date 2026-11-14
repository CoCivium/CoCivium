"""Positive and adverse recovery checks; no fake 325 metrics."""
import unittest
from scripts.CoSessionGraceRecoveryR0 import Measure, Session, Peer, evaluate

def session(**kwargs):
    d=dict(session_id="s1",work_id="w1",revision="sha1",state="ACTIVE",
           consent_to_peer_aid=True)
    d.update(kwargs)
    return Session(**d)

def measure(start,end,*,bad=True,source="observer:123"):
    return Measure("verified_progress",0.0,"receipts/hour",source,start,"peer:verifier",
                   start,end,bad)

def peer(**kwargs):
    d=dict(session_id="s2",capabilities=("REVIEW",),availability="AVAILABLE",
           consent_to_aid=True,health="HEALTHY_VERIFIED",
           source_revision="sha2",evidence_ref="receipt:peer")
    d.update(kwargs)
    return Peer(**d)

def windows():
    return ((measure("2026-11-08T10:00Z","2026-11-08T11:00Z"),),
            (measure("2026-11-08T11:00Z","2026-11-08T12:00Z"),))

class RecoveryTest(unittest.TestCase):
    def test_quiet_healthy_not_zombie(self):
        d=evaluate(session(healthy_quiet=True),windows(),(peer(),))
        self.assertEqual(d["verdict"],"QUIET_HEALTHY")
    def test_sleep_not_zombie(self):
        self.assertEqual(evaluate(session(explicit_sleep=True),windows(),(peer(),))["verdict"],"QUIET_HEALTHY")
    def test_pause_not_zombie(self):
        self.assertEqual(evaluate(session(pause_requested=True),windows(),(peer(),))["verdict"],"QUIET_HEALTHY")
    def test_one_window_cannot_trigger(self):
        self.assertEqual(evaluate(session(),(windows()[0],),(peer(),))["verdict"],"OBSERVE")
    def test_identical_windows_are_not_independent(self):
        self.assertEqual(evaluate(session(),(windows()[0],windows()[0]),(peer(),))["verdict"],"OBSERVE")
    def test_no_adversity_stays_quiet(self):
        w=((measure("2026-11-08T10:00Z","2026-11-08T11:00Z",bad=False),),
           (measure("2026-11-08T11:00Z","2026-11-08T12:00Z",bad=False),))
        self.assertEqual(evaluate(session(),w,(peer(),))["verdict"],"QUIET")
    def test_no_consent_holds(self):
        self.assertEqual(evaluate(session(consent_to_peer_aid=False),windows(),(peer(),))["verdict"],"HOLD")
    def test_unhealthy_peer_not_selected(self):
        self.assertEqual(evaluate(session(),windows(),(peer(health="DEGRADED"),))["verdict"],"HOLD")
    def test_unconsented_peer_not_selected(self):
        self.assertEqual(evaluate(session(),windows(),(peer(consent_to_aid=False),))["verdict"],"HOLD")
    def test_peer_without_review_capability_not_selected(self):
        self.assertEqual(evaluate(session(),windows(),(peer(capabilities=("WRITE",)),))["verdict"],"HOLD")
    def test_no_receiver_only_review(self):
        d=evaluate(session(),windows(),(peer(),))
        self.assertEqual(d["verdict"],"PROPOSE_PEER_REVIEW")
        self.assertFalse(d["physical_takeover"])
    def test_authenticated_receiver_still_advisory(self):
        d=evaluate(session(),windows(),(peer(),),actual_receiver=True,fenced_lease=True)
        self.assertEqual(d["verdict"],"PROPOSE_REVERSIBLE_HANDOFF")
        self.assertFalse(d["effect_executed"])
        self.assertFalse(d["independent_receiver_ack"])
    def test_325_target_not_claimed_as_observed(self):
        d=evaluate(session(),windows(),(peer(),),registry_count=325,registry_verified=False)
        self.assertEqual(d["registry_target"],325)
        self.assertIsNone(d["registry_observed"])
        self.assertFalse(d["registry_target_met"])
    def test_verified_registry_count_is_not_health_evidence(self):
        d=evaluate(session(healthy_quiet=True),windows(),(peer(),),
                   registry_count=400,registry_verified=True)
        self.assertTrue(d["registry_target_met"])
        self.assertEqual(d["verdict"],"QUIET_HEALTHY")
    def test_fake_metric_cannot_trigger(self):
        fake=Measure("progress",0,"", "", "bad","", "a","z",True)
        self.assertEqual(evaluate(session(),((fake,),(fake,)),(peer(),))["verdict"],"OBSERVE")
    def test_duplicate_peer_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            evaluate(session(),windows(),(peer(),peer()))
    def test_oversized_population_rejected(self):
        many=tuple(peer(session_id=str(i)) for i in range(13))
        with self.assertRaisesRegex(ValueError,"EXCESS"):
            evaluate(session(),windows(),many)
    def test_invalid_registry_size_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_REGISTRY"):
            evaluate(session(),windows(),registry_count=-1)

    def test_future_measurement_cannot_trigger(self):
        d=evaluate(session(),windows(),(peer(),),as_of_utc="2026-11-08T09:00:00Z")
        self.assertEqual(d["verdict"],"OBSERVE")
    def test_stale_measurement_cannot_trigger(self):
        d=evaluate(session(),windows(),(peer(),),as_of_utc="2026-11-11T12:00:00Z")
        self.assertEqual(d["verdict"],"OBSERVE")
    def test_fresh_measurements_still_propose_review(self):
        d=evaluate(session(),windows(),(peer(),),as_of_utc="2026-11-08T12:30:00Z")
        self.assertEqual(d["verdict"],"PROPOSE_PEER_REVIEW")
    def test_naive_as_of_rejected(self):
        with self.assertRaisesRegex(ValueError,"NOT_UTC"):
            evaluate(session(),windows(),(peer(),),as_of_utc="2026-11-08T13:00")
    def test_malformed_measure_time_is_not_verified(self):
        bad=Measure("progress", 0.0, "receipts/hour", "observer", "tomorrow",
                    "verifier", "2026-11-08T10:00Z", "2026-11-08T11:00Z", True)
        d=evaluate(session(),((bad,),(bad,)),(peer(),))
        self.assertEqual(d["verdict"],"OBSERVE")
    def test_overlapping_windows_not_persistence(self):
        overlap=measure("2026-11-08T10:30Z","2026-11-08T11:30Z")
        d=evaluate(session(),(windows()[0],(overlap,)),(peer(),))
        self.assertEqual(d["verdict"],"OBSERVE")
    def test_unbounded_freshness_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_FRESHNESS"):
            evaluate(session(),windows(),(peer(),),max_age_hours=float("inf"))
    def test_too_many_windows_rejected(self):
        with self.assertRaisesRegex(ValueError,"EXCESS_INPUT"):
            evaluate(session(),tuple(windows()[0] for _ in range(33)),(peer(),))

if __name__=="__main__":
    unittest.main()
