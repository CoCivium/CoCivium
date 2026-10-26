#!/usr/bin/env python3
import copy
import hashlib
import json
import unittest
from pathlib import Path
import coproc as c

class TestField(unittest.TestCase):
    def test_logical_scale(self): self.assertGreater(c.LOGICAL_SPACE,10**24)
    def test_roundtrip_1024(self):
        samples=[0,1,c.LOGICAL_SPACE-1]+[(i*7919+i*i)%c.LOGICAL_SPACE for i in range(1021)]
        self.assertTrue(all(c.unaddress(c.address(n))==n for n in samples))
    def test_invalid_negative(self):
        with self.assertRaises(ValueError):c.address(-1)
    def test_invalid_upper_bound(self):
        with self.assertRaises(ValueError):c.address(c.LOGICAL_SPACE)
    def test_noninteger(self):
        with self.assertRaises(ValueError):c.address(1.5)
    def test_invalid_case(self):
        with self.assertRaises(ValueError):c.unaddress('A'*20)
    def test_invalid_length(self):
        with self.assertRaises(ValueError):c.unaddress('f'*19)
    def test_task_valid(self):self.assertTrue(c.valid(c.task(3)))
    def test_forged_source_rejected(self):
        t=c.task(3);t['source_sha256']='0'*64
        with self.assertRaises(ValueError):c.valid(t)
    def test_idempotent_admit(self):
        s=c.empty();self.assertEqual(c.admit(s,c.task(10)),'ADMITTED')
        self.assertEqual(c.admit(s,c.task(10)),'IDEMPOTENT');self.assertEqual(len(s['tasks']),1)
    def test_collision_held(self):
        s=c.empty();c.admit(s,c.task(8,source='A'))
        self.assertEqual(c.admit(s,c.task(8,source='B')),'COLLISION_HOLD')
        self.assertEqual(s['tasks'][c.task(8)['id']]['source'],'A')
    def test_touch_limit(self):
        s=c.empty()
        for i in range(c.MAX_TOUCH):self.assertEqual(c.admit(s,c.task(i)),'ADMITTED')
        self.assertEqual(c.admit(s,c.task(333)),'TOUCH_BUDGET_HOLD')
    def test_two_simulated_slots(self):
        s=c.empty()
        for i in range(7):c.admit(s,c.task(i))
        self.assertEqual(len(c.elect(s,0,'LOW')),2)
        self.assertEqual(len(c.elect(s,0,'LOW')),0)
        self.assertEqual(sum(x['state']=='LEASED_SIMULATED' for x in s['tasks'].values()),2)
    def test_pressure_medium(self):
        s=c.empty();[c.admit(s,c.task(i)) for i in range(5)]
        self.assertEqual(len(c.elect(s,0,'MEDIUM')),1)
    def test_pressure_high(self):
        s=c.empty();[c.admit(s,c.task(i)) for i in range(5)]
        self.assertEqual(c.elect(s,0,'HIGH'),[])
    def test_pressure_never_preempts_live(self):
        s=c.empty();[c.admit(s,c.task(i)) for i in range(5)]
        c.elect(s,0,'LOW');self.assertEqual(c.elect(s,1,'HIGH'),[])
        self.assertEqual(sum(x['state']=='LEASED_SIMULATED' for x in s['tasks'].values()),2)
    def test_aging_over_recent_priority(self):
        s=c.empty();c.admit(s,c.task(1,priority=0,submitted=0));c.admit(s,c.task(2,priority=4,submitted=19))
        self.assertEqual(c.elect(s,20,'MEDIUM'),[c.task(1)['id']])
    def test_future_not_woken(self):
        s=c.empty();c.admit(s,c.task(1,wake=7));self.assertEqual(c.elect(s,5),[])
        self.assertEqual(c.elect(s,7),[c.task(1)['id']])
    def test_private_not_leased(self):
        s=c.empty();c.admit(s,c.task(1,privacy='PRIVATE'))
        self.assertEqual(c.elect(s,0),[])
    def test_unknown_not_leased(self):
        s=c.empty();c.admit(s,c.task(1,privacy='UNKNOWN'))
        self.assertEqual(c.elect(s,0),[])
    def test_external_effect_not_leased(self):
        s=c.empty();c.admit(s,c.task(1,effect='EXTERNAL'))
        self.assertEqual(c.elect(s,0),[])
    def test_turtle_depth_two(self):
        s=c.empty();c.admit(s,c.task(1,depth=2))
        self.assertEqual(c.elect(s,0),[c.task(1)['id']])
    def test_turtle_depth_three_held(self):
        s=c.empty();c.admit(s,c.task(1,depth=3))
        self.assertEqual(c.elect(s,0),[])
    def test_finishing_produces_no_ack(self):
        s=c.empty();c.admit(s,c.task(1));id=c.elect(s,0)[0];c.finish(s,id,1)
        self.assertEqual(s['tasks'][id]['receipt']['receiver_ack'],'UNPROVEN')
        self.assertEqual(s['tasks'][id]['receipt']['external_effects'],0)
    def test_double_finish_rejected(self):
        s=c.empty();c.admit(s,c.task(1));id=c.elect(s,0)[0];c.finish(s,id,0)
        with self.assertRaises(ValueError):c.finish(s,id,0)
    def test_expired_lease_no_fake_ack(self):
        s=c.empty();c.admit(s,c.task(1));id=c.elect(s,0)[0]
        self.assertEqual(c.reap(s,3),[id])
        self.assertIsNone(s['tasks'][id]['receipt']);self.assertEqual(s['tasks'][id]['state'],'WAITING')
    def test_expired_finish_rejected(self):
        s=c.empty();c.admit(s,c.task(1));id=c.elect(s,0)[0]
        with self.assertRaises(ValueError):c.finish(s,id,3)
    def test_monotonic_clock(self):
        s=c.empty();c.elect(s,5)
        with self.assertRaises(ValueError):c.elect(s,4)
    def test_checkpoint_roundtrip(self):
        s=c.empty();c.admit(s,c.task(10));k=c.checkpoint(s)
        self.assertEqual(c.recover(k),s)
    def test_checkpoint_tamper(self):
        k=c.checkpoint(c.empty());k['payload']['state']['receiver_ack']='TRUE'
        with self.assertRaises(ValueError):c.recover(k)
    def test_checkpoint_namespace_pinned(self):
        k=c.checkpoint(c.empty());k['payload']['spec_sha256']='0'*64;k['sha256']=c.digest(k['payload'])
        with self.assertRaises(ValueError):c.recover(k)
    def test_foreign_auth_rejected(self):
        s=c.empty();s['effect_authority']='SELF_GRANTED'
        with self.assertRaises(ValueError):c.checkpoint(s)
    def test_fake_ack_rejected(self):
        s=c.empty();s['receiver_ack']='YES'
        with self.assertRaises(ValueError):c.checkpoint(s)
    def test_public_orb_hides_private_ids_and_counts(self):
        s=c.empty();c.admit(s,c.task(1,privacy='PUBLIC_SYNTHETIC'))
        c.admit(s,c.task(2,privacy='PRIVATE',source='PRIVATE_NONSECRET_FIXTURE'))
        q=c.public_orb(s);encoded=json.dumps(q)
        self.assertNotIn(c.task(2)['id'],encoded)
        self.assertNotIn('PRIVATE_NONSECRET_FIXTURE',encoded)
        self.assertIsNone(q['hidden_counts'])
        self.assertEqual(q['observed_working_set'],1)
    def test_public_orb_no_live_claim(self):
        s=c.empty();c.admit(s,c.task(1));c.elect(s,0)
        self.assertEqual(c.public_orb(s)['execution'],'NO_LIVE_WORKERS_FROM_ORB')
        self.assertEqual(c.public_orb(s)['receiver_ack'],'UNPROVEN')
    def test_checkpoint_witness_immutable(self):
        s=c.empty();c.admit(s,c.task(1));cp=c.checkpoint(s);old=copy.deepcopy(cp)
        r=c.recover(cp);r['tick']=42
        self.assertEqual(cp,old)
    def test_shared_spec_sha256(self):
        s=c.empty();self.assertEqual(s['spec_sha256'],c.SPEC_SHA256)
        self.assertEqual(c.public_orb(s)['spec_sha256'],c.SPEC_SHA256)
    def test_no_network_or_persistence_primitives(self):
        src=Path(c.__file__).read_text(encoding='utf-8')
        for forbidden in ['requests.', 'urllib.request', 'socket.socket(', 'http.client.', 'os.system(', 'while True:']:
            self.assertNotIn(forbidden,src)
    def test_depth_over_limit_held_visibly(self):
        s=c.empty();t=c.task(7,depth=3);c.admit(s,t)
        self.assertEqual(s['tasks'][t['id']]['state'],'HELD')
    def test_external_effect_held_visibly(self):
        s=c.empty();t=c.task(7,effect='EXTERNAL');c.admit(s,t)
        self.assertEqual(s['tasks'][t['id']]['state'],'HELD')
    def test_probe_refuses_more_than_eight(self):
        with self.assertRaises(ValueError):c.live_probe(count=9,cap=2)
    def test_live_two_bounded_subprocesses(self):
        r=c.live_probe(count=4,cap=2)
        self.assertEqual(r['launched'],4)
        self.assertEqual(r['completed'],4)
        self.assertEqual(r['peak_parent_observed_processes'],2)
        self.assertEqual(r['remaining_children'],0)
        self.assertEqual(r['external_effects'],0)
        self.assertEqual(len(set(x['nonce'] for x in r['receipts'])),4)

if __name__=='__main__':unittest.main(verbosity=2)
