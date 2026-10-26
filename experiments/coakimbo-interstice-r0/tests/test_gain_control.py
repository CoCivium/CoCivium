import importlib.util
import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('gain_control',ROOT/'src'/'gain_control.py')
m=importlib.util.module_from_spec(s)
sys.modules[s.name]=m
s.loader.exec_module(m)

class GainTest(unittest.TestCase):
    def test_invalid_policy(self):
        with self.assertRaises(ValueError):m.run(policy='magic')
    def test_invalid_scenario(self):
        with self.assertRaises(ValueError):m.run(scenario='et_signal')
    def test_determinism(self):
        self.assertEqual(m.run(),m.run())
    def test_budget_cap(self):
        for s in m.SCENARIOS:
            for p in m.POLICIES:
                self.assertLessEqual(m.run(scenario=s,policy=p)['action_budget_spent'],m.BUDGET+1e-9)
    def test_known_proxy_shift_can_hurt(self):
        a=m.study(12)
        self.assertGreater(a['calibrated_proxy']['wins'],0)
        self.assertGreater(a['reversed_proxy']['losses'],0)
    def test_study_is_finite(self):
        self.assertEqual(set(m.study()),set(m.SCENARIOS))
    def test_no_real_energy_claim(self):
        self.assertIn('Synthetic outcomes',m.study()['calibrated_proxy']['note'])

if __name__=='__main__':unittest.main()
