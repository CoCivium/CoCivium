import unittest
import simulate
class Tests(unittest.TestCase):
    def test_all_policies_present(self):self.assertEqual(len(simulate.POLICIES),5)
    def test_identical_seeds_reproducible(self):
        for p in simulate.POLICIES:self.assertEqual(simulate.run_one(3,p),simulate.run_one(3,p))
    def test_stock_nonnegative(self):
        for p in simulate.POLICIES:
            out=simulate.run_one(4,p,trace=True)
            self.assertTrue(all(0<=t['stock']<=simulate.K for t in out['trace']))
    def test_allocation_budget_bound(self):
        for p in simulate.POLICIES:
            a=simulate.policy_action(p,list(simulate.NEEDS),list(simulate.EFF),list(simulate.WEALTH),1000,__import__('random').Random(1))
            self.assertLessEqual(sum(a),min(140,sum(n/e for n,e in zip(simulate.NEEDS,simulate.EFF)))+1e-7)
    def test_no_negative_extraction(self):
        for p in simulate.POLICIES:
            a=simulate.policy_action(p,list(simulate.NEEDS),list(simulate.EFF),list(simulate.WEALTH),600,__import__('random').Random(1))
            self.assertTrue(all(x>=0 for x in a))
    def test_min_ratio_equalizer(self):
        a,unused=simulate.max_min_alloc([10,10],[1,2],7.5)
        self.assertAlmostEqual(a[0]/10,a[1]*2/10)
        self.assertAlmostEqual(sum(a)+unused,7.5)
    def test_common_exogenous_shocks(self):self.assertEqual(simulate.conditions(2),simulate.conditions(2))
    def test_different_shocks(self):self.assertNotEqual(simulate.conditions(2),simulate.conditions(3))
    def test_metrics_satisfaction_bounded(self):
        for p in simulate.POLICIES:
            o=simulate.run_one(2,p)
            self.assertGreaterEqual(o['mean_satisfaction'],0)
            self.assertLessEqual(o['mean_satisfaction'],1)
    def test_rights_violation_integer(self):
        for p in simulate.POLICIES:
            o=simulate.run_one(1,p)
            self.assertIsInstance(o['rights_violations'],int)
            self.assertGreaterEqual(o['rights_violations'],0)
    def test_gdside_not_marked_winner(self):
        report=simulate.make_report(3,6)
        self.assertNotIn('winner',report)
        self.assertIn('synthetic',report['epistemic_class'].lower())
    def test_deterministic_summary(self):
        self.assertEqual(simulate.summarize([1,2,3],10),simulate.summarize([1,2,3],10))
if __name__=='__main__': unittest.main(verbosity=2)
