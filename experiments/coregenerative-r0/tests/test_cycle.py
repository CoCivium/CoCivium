import unittest
from dataclasses import replace
from cycle import State, Offer, Policy, tick, simulate, qualify_highlight

class RegenerativeCanaries(unittest.TestCase):
    def setUp(self):
        self.good=Offer('Verified-use synthetic',quality=.95,risk=.04,attention=10)
        self.hype=Offer('High-click low-evidence synthetic',quality=.1,risk=.15,attention=100000)
    def test_growth_possible_not_guaranteed(self):
        rows=simulate(State(),self.good,external_inflow=4,turns=24)
        self.assertGreater(rows[4]['after']['useful'],rows[0]['before']['useful'])
        self.assertLessEqual(max(r['after']['capacity'] for r in rows),110)
    def test_zero_budget_dissipates(self):
        rows=simulate(State(18,0,25),self.good,turns=8)
        self.assertLess(rows[-1]['after']['useful'],rows[0]['before']['useful'])
        self.assertTrue(all(r['decision']['spend']==0 for r in rows))
    def test_attentional_hype_held(self):
        rows=simulate(State(),self.hype,external_inflow=4,turns=6)
        self.assertTrue(all(r['decision']['spend']==0 for r in rows))
    def test_clicks_baseline_wastes_budget(self):
        rows=simulate(State(),self.hype,external_inflow=0,turns=6,mode='attention')
        self.assertGreater(rows[-1]['after']['cumulative_spend'],0)
        total_produced=sum(x['decision']['produced'] for x in rows)
        self.assertLess(total_produced/rows[-1]['after']['cumulative_spend'],.3) # lousy benefit per resource
    def test_revocation(self):
        x,d=tick(State(),replace(self.good,consent=False),external_inflow=4)
        self.assertEqual(d['spend'],0)
        self.assertFalse(d['authorized'])
    def test_revocation_even_clicks_policy(self):
        x,d=tick(State(),replace(self.hype,consent=False),mode='attention')
        self.assertEqual(d['spend'],0)
    def test_stale_source(self):
        self.assertEqual(tick(State(),replace(self.good,current=False))[1]['spend'],0)
    def test_private_source(self):
        self.assertEqual(tick(State(),replace(self.good,public_source=False))[1]['spend'],0)
    def test_high_risk_held(self):
        self.assertEqual(tick(State(),replace(self.good,risk=.7))[1]['spend'],0)
    def test_no_negative_reserve(self):
        x,d=tick(State(reserve=1),self.good,external_inflow=0)
        self.assertGreaterEqual(x.reserve,0)
        self.assertEqual(d['spend'],1)
    def test_no_infinite_gain_with_fixed_capacity(self):
        rows=simulate(State(),self.good,external_inflow=4,turns=200)
        self.assertLessEqual(max(r['after']['useful'] for r in rows),110)
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError): tick(State(),replace(self.good,attention=float('inf')))
    def test_invalid_quality_rejected(self):
        with self.assertRaises(ValueError): tick(State(),replace(self.good,quality=1.2))
    def test_turns_bounded(self):
        with self.assertRaises(ValueError): simulate(State(),self.good,turns=1001)
    def test_deterministic(self):
        self.assertEqual(simulate(State(),self.good,external_inflow=4),simulate(State(),self.good,external_inflow=4))
    def test_source_highlighting_no_adoption_claim(self):
        a={'goal':'relationships','source_state':'GITHUB_BLOB_VERIFIED','privacy':'PUBLIC','requires_registration':False,'independent_first_use':None}
        s=qualify_highlight(a,'relationships')
        self.assertEqual(s['status'],'CANDIDATE_SOURCE_ONLY')
        self.assertEqual(s['rank'],1)
    def test_highlighting_private_held(self):
        a={'goal':'default','source_state':'GITHUB_BLOB_VERIFIED','privacy':'PRIVATE','requires_registration':False}
        self.assertEqual(qualify_highlight(a,'default')['status'],'HELD')
    def test_highlighting_registration_held(self):
        a={'goal':'default','source_state':'GITHUB_BLOB_VERIFIED','privacy':'PUBLIC','requires_registration':True}
        self.assertEqual(qualify_highlight(a,'default')['status'],'HELD')
    def test_unknown_goal_no_silent_persona(self):
        with self.assertRaises(ValueError): qualify_highlight({},'political_party_member')
    def test_no_growth_without_input_is_possible(self):
        rows=simulate(State(useful=50,reserve=0,capacity=100),self.good,turns=6,external_inflow=0)
        self.assertLess(rows[-1]['after']['useful'],50)

if __name__=='__main__':unittest.main()
