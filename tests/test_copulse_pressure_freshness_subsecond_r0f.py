"""Regression against exact original R0F code. No external network or devices."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
TARGET=Path(os.environ.get('COPULSE_R0F_SOURCE',HERE.parent/'scripts'/'CoPulseReceiverPressureFreshnessR0F.py'))
spec=importlib.util.spec_from_file_location('copulse_r0f_target', TARGET)
mod=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

def outcome(sample, evaltime='2026-10-25T04:00:00Z', ttl=300, skew=5):
    obj={'sample_id':'synthetic-r0f','receiver_id':'synthetic-receiver','sampled_at':sample}
    raw=json.dumps(obj,sort_keys=True).encode('utf-8')
    return mod.evaluate(obj,raw,evaltime,ttl,skew)

class SubsecondBoundary(unittest.TestCase):
    def test_01_expired_by_point_one_second_is_held(self):
        self.assertEqual(outcome('2026-10-25T03:54:59.900000Z')['state'],'HOLD_STALE_PRESSURE_SAMPLE')
    def test_02_expired_by_point_nine_is_held(self):
        self.assertEqual(outcome('2026-10-25T03:54:59.100000Z')['state'],'HOLD_STALE_PRESSURE_SAMPLE')
    def test_03_future_by_point_one_is_held(self):
        self.assertEqual(outcome('2026-10-25T04:00:05.100000Z')['state'],'HOLD_FUTURE_PRESSURE_SAMPLE')
    def test_04_future_by_point_nine_is_held(self):
        self.assertEqual(outcome('2026-10-25T04:00:05.900000Z')['state'],'HOLD_FUTURE_PRESSURE_SAMPLE')
    def test_05_exact_past_deadline_passes(self):
        self.assertEqual(outcome('2026-10-25T03:55:00Z')['state'],'PASS_FRESH_PRESSURE_SAMPLE')
    def test_06_exact_future_limit_passes(self):
        self.assertEqual(outcome('2026-10-25T04:00:05Z')['state'],'PASS_FRESH_PRESSURE_SAMPLE')
    def test_07_inside_past_window_passes(self):
        self.assertEqual(outcome('2026-10-25T03:55:00.500000Z')['state'],'PASS_FRESH_PRESSURE_SAMPLE')
    def test_08_inside_future_window_passes(self):
        self.assertEqual(outcome('2026-10-25T04:00:04.500000Z')['state'],'PASS_FRESH_PRESSURE_SAMPLE')
    def test_09_integertime_output_preserved(self):
        self.assertIsInstance(outcome('2026-10-25T03:55:00.500000Z')['age_seconds'],int)
    def test_10_exact_second_receipt_shape_unchanged(self):
        a=outcome('2026-10-25T03:55:00Z');self.assertEqual(a['age_seconds'],300)
        self.assertEqual(a['freshness_sha256'],mod.sha256_bytes(mod.canonical({k:v for k,v in a.items() if k!='freshness_sha256'})))
    def test_11_zero_skew_future_point_one_fails(self):
        self.assertEqual(outcome('2026-10-25T04:00:00.100000Z',skew=0)['state'],'HOLD_FUTURE_PRESSURE_SAMPLE')
    def test_12_zero_ttl_past_point_one_fails(self):
        self.assertEqual(outcome('2026-10-25T03:59:59.900000Z',ttl=0)['state'],'HOLD_STALE_PRESSURE_SAMPLE')

if __name__=='__main__':unittest.main()
