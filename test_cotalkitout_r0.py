"""Synthetic negative/positive tests for CoTalkItOut decision discipline."""
import unittest
from scripts.CoTalkItOutR0 import Proposal, Work, decide, projection

def p(peer="one", option="a", evidence="SOURCE_LANDED", risk="REVERSIBLE"):
    return Proposal(peer, option, "github:commit-pin", evidence, risk)
def w(**kw):
    baseline={"work_id":"W1","source_revision":"sha123","blocker":"NONE",
              "options":(p(),), "elected_actuator":"one"}
    baseline.update(kw)
    return Work(**baseline)

class Tests(unittest.TestCase):
    def test_one_converged_proposal_not_actual_effect(self):
        d=decide(w())
        self.assertEqual(d["verdict"],"ACT_PROPOSAL")
        self.assertTrue(d["no_effect_executed"])
        self.assertFalse(projection(d)["native_effect"])
        self.assertEqual(projection(d)["receiver_ack"],"UNPROVEN")
    def test_disagreement_requests_independent_test(self):
        d=decide(w(options=(p(),p("two","b"))))
        self.assertEqual(d["verdict"],"CHALLENGE")
        self.assertTrue(d["disagreement"])
    def test_repeated_unchanged_dissent_goes_quiet(self):
        d=decide(w(options=(p(),p("two","b")),prior_rounds=1))
        self.assertEqual(d["verdict"],"QUIET")
    def test_external_change_reopens_once(self):
        d=decide(w(options=(p(),p("two","b")),prior_rounds=1,external_change=True))
        self.assertEqual(d["verdict"],"CHALLENGE")
    def test_no_receiver_never_claims_action(self):
        self.assertEqual(decide(w(blocker="NO_AUTHORIZED_RECEIVER"))["verdict"],"HOLD")
    def test_missing_consent_holds(self):
        self.assertEqual(decide(w(blocker="MISSING_CONSENT"))["verdict"],"HOLD")
    def test_irreversible_effect_escalates(self):
        self.assertEqual(decide(w(options=(p(risk="IRREVERSIBLE"),)))["verdict"],"ESCALATE")
    def test_budget_exhaustion_holds(self):
        self.assertEqual(decide(w(budget_remaining=0))["verdict"],"HOLD")
    def test_round_limit_holds(self):
        self.assertEqual(decide(w(prior_rounds=3))["verdict"],"HOLD")
    def test_no_fenced_election_holds(self):
        self.assertEqual(decide(w(elected_actuator=""))["verdict"],"HOLD")
    def test_empty_task_quiet(self):
        self.assertEqual(decide(w(options=()))["verdict"],"QUIET")
    def test_peer_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            decide(w(options=(p(),p(option="b"))))
    def test_bad_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNBOUND"):
            decide(w(options=(p(evidence="MAGIC_ACK"),)))
    def test_invalid_revision_rejected(self):
        with self.assertRaisesRegex(ValueError,"MISSING"):
            decide(w(source_revision=""))
    def test_receiver_ack_not_inferred_from_ci(self):
        d=decide(w(options=(p(evidence="CI_PASS"),)))
        self.assertEqual(d["receiver_ack"],"UNPROVEN")
    def test_capped_population(self):
        with self.assertRaisesRegex(ValueError,"BOUNDS"):
            decide(w(options=tuple(p(str(i)) for i in range(13))))
if __name__=="__main__":
    unittest.main()
