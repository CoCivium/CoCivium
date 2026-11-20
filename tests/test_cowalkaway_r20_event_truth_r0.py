"""Synthetic R20 receipt classification. No native task or external network."""
import copy
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples" / "cowalkaway"))
from r20_event_truth_r0 import classify


def normal():
    return {
      'schema': 'CoWalkAway.R20.NativeSupervisorEvent',
      'native_task': 'CoWalkAwayR2_LocalEvent',
      'result': 'BOUNDED_PARENT_AUTORECOVERY_PASS',
      'event_id': 'a'*32,
      'child_script_sha256': 'b'*64,
      'effects': 'LOCAL_SQLITE_AND_RECEIPTS_ONLY',
      'started_utc':'2026-11-20T20:46:13.000Z',
      'finished_utc':'2026-11-20T20:46:15.000Z',
      'child_fault_canary_consumed': False,
      'lease_recovery': None,
      'attempts':[{'start_utc':'2026-11-20T20:46:13.500Z',
                   'end_utc':'2026-11-20T20:46:14.500Z',
                   'exit':0, 'fault_injected':False}]
    }

def recovery():
    x=normal()
    x['child_fault_canary_consumed']=True
    x['attempts']=[
        {'start_utc':'2026-11-20T20:46:13.050Z','end_utc':'2026-11-20T20:46:13.500Z', 'exit':77, 'fault_injected':True},
        {'start_utc':'2026-11-20T20:46:14.000Z','end_utc':'2026-11-20T20:46:14.500Z', 'exit':0,'fault_injected':False}
    ]
    x['lease_recovery']={'lease_owner_observed':True,'seconds_waited':1}
    return x

class Tests(unittest.TestCase):
    def test_no_fault_not_recovery(self):
        self.assertEqual('NORMAL_LOCAL_TASK_COMPLETION_ONLY',classify(normal())['state'])
    def test_recovered_child_not_reboot(self):
        d=classify(recovery())
        self.assertEqual('BOUNDED_CHILD_RECOVERY_WITHIN_SURVIVING_PARENT',d['state'])
        self.assertFalse(d['reboot_recovery_proven'])
    def test_no_receiver_ack_from_label(self):
        self.assertFalse(classify(recovery())['receiver_ack'])
    def test_no_new_jobs_from_invocation(self):
        self.assertFalse(classify(normal())['new_jobs_proven'])
    def test_missing_event(self):
        self.assertTrue(classify(None)['state'].startswith('HOLD'))
    def test_fake_task(self):
        x=normal();x['native_task']='Else';self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_invalid_id(self):
        x=normal();x['event_id']='a';self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_bad_digest(self):
        x=normal();x['child_script_sha256']='main';self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_extra_attempts(self):
        x=normal();x['attempts']*=3;self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_forged_fault_bit(self):
        x=normal();x['child_fault_canary_consumed']=True;self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_two_attempts_without_fault(self):
        x=recovery();x['child_fault_canary_consumed']=False;self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_fake_exit_zero_on_first(self):
        x=recovery();x['attempts'][0]['exit']=0;self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_bad_lease(self):
        x=recovery();x['lease_recovery']['seconds_waited']=200;self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_bad_lease_type(self):
        x=recovery();x['lease_recovery']['seconds_waited']=True;self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_fake_effect(self):
        x=normal();x['effects']='PUBLIC';self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_backward_time(self):
        x=normal();x['finished_utc']='2026-11-20T20:46:00Z';self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_naive_time(self):
        x=normal();x['finished_utc']='2026-11-20T20:46:15';self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_missing_attempt_timestamp(self):
        x=normal();del x['attempts'][0]['end_utc'];self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_conflicting_injected_without_recovery(self):
        x=normal();x['attempts'][0]['fault_injected']=True;self.assertTrue(classify(x)['state'].startswith('HOLD'))
    def test_false_reported_status(self):
        x=recovery();x['result']='HOLD';self.assertTrue(classify(x)['state'].startswith('HOLD'))

if __name__=='__main__': unittest.main(verbosity=2)
