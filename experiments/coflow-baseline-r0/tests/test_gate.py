import copy
import json
import sys
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import coflow_baseline as c

class CoFlowBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload=c.load_fixture(BASE/'fixtures'/'observations.json')
        cls.summary=c.summarize(cls.payload)
        cls.x2=next(v for v in cls.summary['cohorts'] if v['context']['device_class']=='X2-SYNTHETIC')

    def test_fixture_guard(self):
        f=copy.deepcopy(self.payload);f['fixture_only']=False
        tmp=BASE/'tests'/'temp_rejected_fixture.json'
        try:
            tmp.write_text(json.dumps(f))
            with self.assertRaisesRegex(ValueError,'FIXTURE_ONLY_REQUIRED'):c.load_fixture(tmp)
        finally:tmp.unlink(missing_ok=True)

    def test_peak_not_repeat_min(self):
        self.assertEqual(self.x2['historical_record']['rate_per_second'], 10)
        self.assertEqual(self.x2['sustained_candidates']['baseline']['repeat_min_rate'],2)

    def test_single_burst_unpromotable(self):
        self.assertEqual(self.x2['sustained_candidates']['burst']['state'],'HOLD_REPETITIONS')

    def test_candidate_comparable_throughput_improved(self):
        self.assertEqual(self.x2['sustained_candidates']['candidate']['repeat_min_rate'],3)
        self.assertEqual(self.x2['sustained_candidates']['candidate']['promotion_vs_baseline'],'THROUGHPUT_GATE_PASS_ONLY')

    def test_device_isolation(self):
        other=next(v for v in self.summary['cohorts'] if v['context']['device_class']=='OTHER-SYNTHETIC')
        self.assertEqual(other['historical_record']['rate_per_second'],200)
        self.assertEqual(self.x2['historical_record']['rate_per_second'],10)

    def test_missing_ack_and_quality_excluded(self):
        self.assertEqual(self.x2['unqualified_runs'],2)
        self.assertEqual(self.x2['qualified_runs'],7)

    def test_negative_duration_rejected(self):
        f=copy.deepcopy(self.payload);f['observations'][0]['elapsed_seconds']=-1
        with self.assertRaisesRegex(ValueError,'INVALID_ELAPSED'):c.summarize(f)

    def test_boolean_counts_rejected(self):
        f=copy.deepcopy(self.payload);f['observations'][0]['emitted']=True
        with self.assertRaisesRegex(ValueError,'INVALID_COUNT'):c.summarize(f)

    def test_quality_flag_must_be_boolean(self):
        f=copy.deepcopy(self.payload);f['observations'][0]['quality_pass']=1
        with self.assertRaisesRegex(ValueError,'MISSING_QUALITY_OR_CURRENTNESS'):c.summarize(f)

    def test_impossible_counts_rejected(self):
        f=copy.deepcopy(self.payload);f['observations'][0]['receiver_accepted']=26
        with self.assertRaisesRegex(ValueError,'IMPOSSIBLE_COUNT_ORDER'):c.summarize(f)

    def test_missing_context_rejected(self):
        f=copy.deepcopy(self.payload);del f['observations'][0]['context']['quality_contract']
        with self.assertRaisesRegex(ValueError,'CONTEXT_FIELDS_MISMATCH'):c.summarize(f)

    def test_duplicate_run_id_rejected(self):
        f=copy.deepcopy(self.payload);f['observations'][1]['run_id']=f['observations'][0]['run_id']
        with self.assertRaisesRegex(ValueError,'DUPLICATE_RUN_ID'):c.summarize(f)

    def test_hold_when_no_comparable_baseline(self):
        other=next(v for v in self.summary['cohorts'] if v['context']['device_class']=='OTHER-SYNTHETIC')
        self.assertEqual(other['sustained_candidates']['unmatched-device']['state'],'HOLD_REPETITIONS')

    def test_ledger_tamper_rejected(self):
        ev,head=c.build_events(self.summary)
        self.assertEqual(c.verify_events(ev,head),7)
        ev[2]['detail']='silently changed'
        with self.assertRaisesRegex(ValueError,'TAMPERED_EVENT'):c.verify_events(ev,head)

    def test_chain_wrong_head_rejected(self):
        ev,head=c.build_events(self.summary)
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'):c.verify_events(ev,'0'*64)

    def test_no_real_runtime_claim(self):
        self.assertTrue(self.summary['synthetic_only'])
        ev,_=c.build_events(self.summary)
        self.assertEqual(ev[-1]['outcome'],'NOT_RUN')

if __name__=='__main__':unittest.main()
