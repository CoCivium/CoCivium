"""CoTalkItOut CoZombie/CoGrace triage negative controls: synthetic only."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"examples"/"cotalkitout"))
from session_recovery_r0 import Observation, TriagePolicy, classify

def specimen(**overrides):
    o=Observation(session_id="s1",work_id="w1",observed_at=10000,
        last_progress_at=100, due_at=1000,phase="ACTIVE",has_open_obligation=True,
        next_wake_at=None,is_lease_active=False,lease_epoch=2,
        receipt_refs=("job:abc",),peer_ids=("peer-b","peer-a"),
        context_compatible=True,consent_to_peer_assist=True)
    return replace(o, **overrides)

class RecoveryTests(unittest.TestCase):
    def test_healthy_dormancy_is_not_zombie(self):
        o=specimen(phase="DORMANT",next_wake_at=20000)
        self.assertEqual(classify(o)["state"],"HEALTHY_QUIET")
    def test_graceful_hold_preserved(self):
        self.assertEqual(classify(specimen(phase="GRACEFUL_HOLD",next_wake_at=20000))["next"],"SLEEP")
    def test_missing_progress_is_unknown_not_stall(self):
        self.assertEqual(classify(specimen(last_progress_at=None))["next"],"OBSERVE")
    def test_recent_progress_not_reassigned(self):
        self.assertEqual(classify(specimen(last_progress_at=9900))["next"],"RECHECK")
    def test_not_yet_due_not_reassigned(self):
        self.assertEqual(classify(specimen(due_at=20000))["next"],"RECHECK")
    def test_active_lease_fenced_before_handoff(self):
        self.assertEqual(classify(specimen(is_lease_active=True))["next"],"FENCE_FIRST")
    def test_unconsented_peer_stays_isolated(self):
        self.assertEqual(classify(specimen(consent_to_peer_assist=False))["next"],"TALK_OR_ISOLATED_TEST")
    def test_incompatible_peers_cannot_merge(self):
        self.assertEqual(classify(specimen(context_compatible=False))["next"],"TALK_OR_ISOLATED_TEST")
    def test_elect_one_candidate_without_effect(self):
        r=classify(specimen())
        self.assertEqual(r["next"],"PROPOSE_PEER_HANDOFF")
        self.assertEqual(r["candidate_peer"],"peer-a")
        self.assertEqual(r["previous_epoch"],2)
    def test_conflicting_receipt_requires_challenge(self):
        self.assertEqual(classify(specimen(conflict_detected=True))["next"],"FENCE_AND_CHALLENGE")
    def test_human_gate_cannot_be_peer_bypassed(self):
        self.assertEqual(classify(specimen(human_authority_required=True))["next"],"HUMAN_GATE")
    def test_no_open_obligation_is_healthy(self):
        self.assertEqual(classify(specimen(has_open_obligation=False))["state"],"HEALTHY_QUIET")
    def test_future_timestamp_is_unknown(self):
        self.assertEqual(classify(specimen(last_progress_at=10001))["next"],"OBSERVE")
    def test_no_proof_is_unknown(self):
        self.assertEqual(classify(specimen(receipt_refs=(),due_at=None))["next"],"OBSERVE")
    def test_policy_exposes_metric_families_not_fake_325(self):
        self.assertGreaterEqual(len(TriagePolicy().metric_families), 5)
        self.assertLess(len(TriagePolicy().metric_families), 325)

if __name__=="__main__":
    unittest.main(verbosity=2)
