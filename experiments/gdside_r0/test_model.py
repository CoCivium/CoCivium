"""Negative controls for speculative G_dSide comparison."""
import unittest
from model import Candidate, METRICS, SCENARIOS, dominates, frontier, interaction

class TestCandidate(unittest.TestCase):
    def test_future_scenario_can_win(self):
        self.assertEqual(frontier(SCENARIOS["future_benefit"]), ["gdside"])

    def test_backcast_can_lose(self):
        self.assertEqual(frontier(SCENARIOS["backcast_overfit"]), ["supply"])

    def test_rights_veto(self):
        self.assertEqual(frontier(SCENARIOS["rights_veto"]), ["supply"])

    def test_label_cannot_create_dominance(self):
        a = Candidate("gdside", dict(zip(METRICS, (5,5,5,5,5,5))))
        b = Candidate("demand", dict(zip(METRICS, (5,5,5,5,5,5))))
        self.assertFalse(dominates(a,b))
        self.assertEqual(frontier([a,b]), ["demand","gdside"])

    def test_incomparability_retained(self):
        a = Candidate("gdside", dict(zip(METRICS, (8,8,8,8,8,2))))
        b = Candidate("ecological", dict(zip(METRICS, (6,6,6,6,3,1))))
        self.assertEqual(frontier([a,b]), ["ecological","gdside"])

    def test_invalid_dimensions_fail(self):
        with self.assertRaisesRegex(ValueError, "SCHEMA"):
            frontier([Candidate("bad",{"flourishing":5})])

    def test_interaction_positive_negative(self):
        base=frozenset()
        v={base:0, frozenset({"a"}):3, frozenset({"b"}):2,
           frozenset({"a","b"}):7}
        self.assertEqual(interaction(v,base,"a","b"),2)
        v[frozenset({"a","b"})]=4
        self.assertEqual(interaction(v,base,"a","b"),-1)

    def test_duplicate_intervention_rejected(self):
        with self.assertRaises(ValueError):
            interaction({},frozenset(),"a","a")

if __name__=="__main__":
    unittest.main()
