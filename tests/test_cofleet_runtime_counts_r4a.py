"""Bounded CoFleet R4A runtime input truth regression, no device or network effects."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

source = Path(__file__).resolve().parents[1] / 'scripts' / 'CoFleetProjectionCompilerR4A.py'
spec = importlib.util.spec_from_file_location('cofleet_r4a', source)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CoFleetRuntimeTruth(unittest.TestCase):
    def project(self, runtime):
        return module.compile_projection(None, None, None, runtime, '2026-10-25T11:12:00Z')

    def test_01_true_workspace_is_unknown(self):
        self.assertEqual(self.project({'workspaces': True})['workspaces'], {'count': None, 'coverage': 'RUNTIME_FACT_UNPROVEN'})
    def test_02_false_worker_is_unknown(self):
        self.assertEqual(self.project({'materialized_workers': False})['materialized_workers']['count'], None)
    def test_03_negative_provider_is_unknown(self):
        self.assertEqual(self.project({'provider_sessions': -1})['provider_sessions']['count'], None)
    def test_04_fractional_model_is_unknown(self):
        self.assertEqual(self.project({'model_runtimes': 1.5})['model_runtimes']['count'], None)
    def test_05_string_provider_is_unknown(self):
        self.assertEqual(self.project({'provider_sessions': '2'})['provider_sessions']['count'], None)
    def test_06_zero_workers_valid(self):
        self.assertEqual(self.project({'materialized_workers': 0})['materialized_workers'], {'count': 0, 'coverage': 'BOUND_RUNTIME_FACT'})
    def test_07_three_models_valid(self):
        self.assertEqual(self.project({'model_runtimes': 3})['model_runtimes']['count'], 3)
    def test_08_true_lease_is_unknown(self):
        self.assertEqual(self.project({'effect_leases': True})['effect_leases'], {'count': None, 'coverage': 'RUNTIME_FACT_UNPROVEN'})
    def test_09_negative_lease_is_unknown(self):
        self.assertEqual(self.project({'effect_leases': -2})['effect_leases']['count'], None)
    def test_10_string_lease_is_unknown(self):
        self.assertEqual(self.project({'effect_leases': '0'})['effect_leases']['count'], None)
    def test_11_valid_zero_lease(self):
        self.assertEqual(self.project({'effect_leases': 0})['effect_leases'], {'count': 0, 'coverage': 'BOUND_RUNTIME_FACT'})
    def test_12_absent_lease_stays_logical(self):
        self.assertEqual(self.project({'workspaces': 1})['effect_leases']['coverage'], 'LOGICAL_CONTRACTS_ONLY__LIVE_RUNTIME_UNPROVEN')
    def test_13_no_runtime_is_unknown_not_live(self):
        self.assertEqual(module.compile_projection(None, None, None, None, '2026-10-25T11:12:00Z')['provider_sessions']['count'], None)
    def test_14_bad_count_does_not_create_human_gate(self):
        self.assertEqual(self.project({'effect_leases': True})['human_blockers'], [])
    def test_15_pressure_not_false_global_census(self):
        self.assertEqual(self.project({'workspaces': True})['coverage']['global_fleet_census'], 'UNPROVEN')

if __name__ == '__main__':
    unittest.main()
