"""Negative-control pull-vector tests: declared futures are not facts."""
import unittest
from pull_vector_r0 import Objective, Action, assess, fixture

def obj():
    return (Objective("a","units",10,1,0,"fixture:source"),)
def run(actions=(), **kwargs):
    return assess({"a":5},obj(),actions,budget=4,**kwargs)

class PullVectorTests(unittest.TestCase):
    def test_expected_gain_is_not_effect(self):
        d=fixture()
        self.assertEqual(d["proposed_action"],"teach")
        self.assertFalse(d["effect_executed"])
        self.assertFalse(d["receiver_ack"])
    def test_do_nothing_can_win(self):
        self.assertIsNone(run((Action("harm",1,(("a",-1),),"fixture:harm"),))["proposed_action"])
    def test_rights_veto(self):
        self.assertIsNone(run((Action("coerce",1,(("a",20),),"fixture:x",False),))["proposed_action"])
    def test_budget_veto(self):
        self.assertIsNone(run((Action("spend",5,(("a",20),),"fixture:x"),))["proposed_action"])
    def test_floor_veto(self):
        o=(Objective("a","units",10,1,6,"fixture:floor"),)
        d=assess({"a":5},o,(Action("small",1,(("a",0.5),),"fixture:small"),),budget=1)
        self.assertIsNone(d["proposed_action"])
    def test_model_overclaim_can_fool_selector(self):
        good=fixture()
        bad=fixture(misleading=True)
        self.assertEqual(good["proposed_action"],"teach")
        self.assertEqual(bad["proposed_action"],"hype")
        self.assertTrue(bad["candidates"][0]["uncertainty_unverified"])
    def test_reliability_zero_removes_claimed_gain(self):
        self.assertIsNone(run((Action("gain",1,(("a",20),),"fixture:gain"),),effect_reliability=0)["proposed_action"])
    def test_unbound_effect_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNBOUND_EFFECT"):
            run((Action("bad",1,(("unknown",4),),"fixture:x"),))
    def test_duplicate_effect_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_EFFECT"):
            run((Action("bad",1,(("a",3),("a",4)),"fixture:x"),))
    def test_bad_horizon_rejected(self):
        with self.assertRaisesRegex(ValueError,"BOUND_REQUIRED"):
            run(horizon=1000)
    def test_bad_reliability_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_RELIABILITY"):
            run(effect_reliability=2)
    def test_duplicate_objective_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_OBJECTIVE"):
            assess({"a":5},obj()+obj(),(),budget=2)
    def test_source_required(self):
        with self.assertRaisesRegex(ValueError,"INVALID_ACTION"):
            run((Action("x",1,(("a",2),),""),))
    def test_negative_cost_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_ACTION"):
            run((Action("x",-1,(("a",2),),"fixture:x"),))
if __name__=="__main__":
    unittest.main()
