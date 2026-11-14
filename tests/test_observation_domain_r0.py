"""Synthetic, adversarial domain checks. Run on ordinary and optimized Python."""
import copy
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0, str(ROOT / 'ai' / 'measurement'))
from observation_domain_r0 import validate_observation_domain

REG = json.loads((ROOT / 'ai' / 'measurement' / 'registry_r0_1.json').read_text())
UNITS = {m['id']:m for m in REG['metric_families']}

def obs(metric, value, **edits):
    m=UNITS[metric]
    v={
        'metric_id':metric, 'quantity_kind':m['quantity_kind'],
        'value_state':'MEASURED', 'value':value, 'unit_id':m['unit_id'],
        'observed_at_utc':'2026-11-08T06:00:00Z', 'observer_id':'synthetic:fixture',
        'source_id':'synthetic:fixture', 'source_sha256':'a'*64,
        'interval_or_window':'synthetic:w1', 'uncertainty_kind':'NOT_ESTIMATED',
        'uncertainty_value_or_null':None, 'method_or_null':'synthetic:method',
        'authority_scope':'synthetic_readonly', 'comparison_baseline_or_null':None,
    }
    v.update(edits)
    return v

def subset(n='3',d='4',**extra):
    a={'numerator':n,'denominator':d,'window_id':'synthetic:w1',
       'scope_id':'synthetic:scope1','count_kind':'qualified_delivery_and_exact_object_ack'}
    a.update(extra)
    return a

class DomainTests(unittest.TestCase):
    def ok(self,metric,value,**k):
        result=validate_observation_domain(obs(metric,value,**k),REG)
        self.assertEqual(result['state'],'DOMAIN_CONSISTENT_ONLY')
        self.assertIn('NO_INDEPENDENT_RECEIVER_ACK', result['nonclaims'])

    def rejects(self,metric,value,counts=None,**edits):
        with self.assertRaises(ValueError):
            validate_observation_domain(obs(metric,value,**edits),REG,counts=counts)

    def test_real_metric_profile_exact(self):
        self.assertEqual(len(UNITS),7)

    def test_positive_signed_source_skew(self):
        self.ok('CoTime.source_age','-1/2')

    def test_positive_rate_zero(self):
        self.ok('CoSpeedo.verified_useful_delta_rate','0')

    def test_negative_rate_forbidden(self):
        self.rejects('CoSpeedo.verified_useful_delta_rate','-0.1')

    def test_positive_count(self):
        self.ok('CoUX.human_touch_count','2')

    def test_negative_count(self):
        self.rejects('CoUX.human_touch_count','-1')

    def test_fractional_human_count(self):
        self.rejects('CoUX.human_touch_count','1/2')

    def test_failure_domain_not_fraction(self):
        self.rejects('CoReach.failure_domain_coverage','3/2')

    def test_bounded_fraction_ok(self):
        r=validate_observation_domain(obs('CoMx.receiver_pickup_fraction','3/4'),REG,counts=subset())
        self.assertEqual(r['value_exact'],'3/4')

    def test_share_over_one_rejected(self):
        self.rejects('CoMx.receiver_pickup_fraction','5/4',counts=subset('5','4'))

    def test_negative_share_rejected(self):
        self.rejects('CoMx.receiver_pickup_fraction','-1/8',counts=subset())

    def test_zero_denominator_is_not_zero_percent(self):
        self.rejects('CoMx.receiver_pickup_fraction','0',counts=subset('0','0'))

    def test_fraction_must_match_counts(self):
        self.rejects('CoMx.receiver_pickup_fraction','1/4',counts=subset('3','4'))

    def test_fractional_acks_invalid(self):
        self.rejects('CoMx.receiver_pickup_fraction','1/2',counts=subset('1/2','1'))

    def test_missing_counts_invalid(self):
        self.rejects('CoMx.receiver_pickup_fraction','3/4')

    def test_window_mismatch(self):
        self.rejects('CoMx.receiver_pickup_fraction','3/4',counts=subset(window_id='synthetic:other'))

    def test_wrong_unit_held(self):
        self.rejects('CoUX.human_touch_count','2',unit_id='ratio')

    def test_unknown_is_not_zero(self):
        self.rejects('CoUX.human_touch_count','0',value_state='UNKNOWN')

    def test_observed_zero_strict(self):
        self.ok('CoUX.human_touch_count','0',value_state='OBSERVED_ZERO')
        self.rejects('CoUX.human_touch_count','1',value_state='OBSERVED_ZERO')

    def test_nan_nonfinite_float_boolean(self):
        for x in ('NaN','Infinity',False,1.5,'1/0','1e999'):
            with self.subTest(x=x):
                self.rejects('CoUX.human_touch_count',x)

    def test_forged_evaluator_qualifier_rejected(self):
        self.rejects('CoUX.human_touch_count','2',competition_claim_eligible=True)

    def test_receipt_authority_requires_source_hash_syntax(self):
        self.rejects('CoUX.human_touch_count','2',source_sha256='not-a-hash')

    def test_missing_observer_held(self):
        self.rejects('CoUX.human_touch_count','2',observer_id='')

    def test_unbounded_uncertainty_held(self):
        self.rejects('CoUX.human_touch_count','2',uncertainty_value_or_null='-1')

    def test_future_metric_held_not_assumed(self):
        v=obs('CoUX.human_touch_count','1')
        v['metric_id']='future.unknown'
        with self.assertRaises(ValueError):
            validate_observation_domain(v, REG)

    def test_unknown_uncertainty_policy(self):
        self.rejects('CoUX.human_touch_count','1',uncertainty_kind='invented')
        self.rejects('CoUX.human_touch_count','1',uncertainty_value_or_null='1')
        self.rejects('CoUX.human_touch_count','1',uncertainty_kind='REPORTED_STD')
        self.ok('CoUX.human_touch_count','1',uncertainty_kind='REPORTED_STD',uncertainty_value_or_null='1/4')

    def test_timestamp_utc_required(self):
        self.rejects('CoUX.human_touch_count','1',observed_at_utc='2026-11-08T06:00:00')

    def test_zero_restore_time_acceptance_not_guaranteed(self):
        self.ok('CoResilience.mean_time_to_restore','0')

    def test_energy_per_joule_nonnegative(self):
        self.ok('CoEnergy.useful_delta_per_joule','1/2000')
        self.rejects('CoEnergy.useful_delta_per_joule','-2')

if __name__=='__main__':unittest.main()