"""CoRel/CoBraid plan-only, receipt-gated causal ordering checks."""
import unittest
from corel_braid_wave_planner_r0 import plan

def n(i, state="UNPROVEN", deps=(), receipt=None):
    return {"id":i,"state":state,"deps":list(deps),"evidence_owner":"issue #317","receipt":receipt}

class BraidWaveTests(unittest.TestCase):
    def test_parallel_independent_work(self):
        p=plan([n("source","PROVEN",receipt="pinned-source"),n("testA",deps=["source"]),n("testB",deps=["source"])])
        self.assertEqual(p["waves"][0]["candidate_parallel"],["testA","testB"])
        self.assertEqual(p["execution"],"NONE")

    def test_sequential_chain_is_hypothetical(self):
        p=plan([n("a","PROVEN",receipt="a-receipt"),n("b",deps=["a"]),n("c",deps=["b"])])
        self.assertEqual([w["candidate_parallel"] for w in p["waves"]],[["b"],["c"]])
        self.assertIn("PLANNED_PREDECESSOR_NE_RECEIPTED_PREDECESSOR",p["warnings"])

    def test_missing_receipt_rejected(self):
        with self.assertRaises(ValueError):plan([n("a","PROVEN")])

    def test_unknown_and_self_dependencies_rejected(self):
        for nodes in ([n("a",deps=["missing"])],[n("a",deps=["a"])]):
            with self.subTest(nodes=nodes),self.assertRaises(ValueError):plan(nodes)

    def test_cycles_rejected(self):
        with self.assertRaisesRegex(ValueError,"cycle"):
            plan([n("a",deps=["b"]),n("b",deps=["a"])])

    def test_held_and_failed_never_elected(self):
        p=plan([n("root","HELD"),n("child",deps=["root"]),n("bad","FAILED")])
        self.assertEqual(p["waves"],[])
        self.assertEqual(p["blocked"]["child"]["unqualified"],["root"])
        self.assertEqual(p["blocked"]["bad"]["reason"],"FAILED")

    def test_bounded_waves(self):
        p=plan([n("a"),n("b",deps=["a"]),n("c",deps=["b"])],limit=1)
        self.assertEqual(len(p["waves"]),1)
        self.assertEqual(p["blocked"]["b"]["reason"],"WAVE_BUDGET")

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            plan([n("a"),n("a")])

    def test_no_implicit_authority(self):
        p=plan([n("a")])
        self.assertEqual(p["execution"],"NONE")
        self.assertIn("PARALLEL_READINESS_NE_PARALLEL_EFFECT_AUTHORITY",p["warnings"])

    def test_practical_handoff_cannot_leap_receiver_gate(self):
        p=plan([n("source","PROVEN",receipt="git-readback"),n("receiver","HELD",deps=["source"]),
                n("restart",deps=["receiver"]),n("mirror",deps=["receiver"])])
        self.assertEqual(p["waves"],[])
        self.assertEqual(p["blocked"]["receiver"]["reason"],"HELD")
        self.assertEqual(p["blocked"]["restart"]["unqualified"],["receiver"])
        self.assertEqual(p["blocked"]["mirror"]["unqualified"],["receiver"])

if __name__=="__main__":unittest.main()
