"""Deterministic, side-effect-free acceptance for CoAliveObject R0."""
import copy
import json
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import CoAlive, digest, canonical_bytes, reject_duplicate_keys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'manifest.json').read_bytes()
M = json.loads(SOURCE)


def engine(modifier=None):
    m = copy.deepcopy(M)
    if modifier:
        modifier(m)
    return CoAlive(canonical_bytes(m))


def signal(id='source1', obj='mouse', kind='SOURCE_DELTA_REPORTED', scope='SYNTHETIC_SHADOW'):
    return {'event_id': id, 'object_id': obj, 'kind': kind,
            'source_blob_sha': next(x['source']['git_blob_sha1'] for x in M['objects'] if x['id']==obj),
            'scope': scope}


class SourceIdentity(unittest.TestCase):
    def test_source_catalog_three_types(self):
        self.assertEqual(set(x['id'] for x in CoAlive(SOURCE).objects.values()), {'mouse','spiff','morph'})
    def test_parent_manifest_exact_bytes(self):
        self.assertEqual(CoAlive(SOURCE).manifest_hash, __import__('hashlib').sha256(SOURCE).hexdigest())
    def test_changed_whitespace_changes_namespace(self):
        self.assertNotEqual(CoAlive(SOURCE).manifest_hash, CoAlive(SOURCE + b' ').manifest_hash)
    def test_refuses_duplicate_object(self):
        with self.assertRaises(ValueError):engine(lambda m:m['objects'].append(copy.deepcopy(m['objects'][0])))
    def test_refuses_effect_authority(self):
        with self.assertRaises(ValueError):engine(lambda m:m['objects'][0].update(effect_authority='NETWORK_WRITE'))
    def test_refuses_private_object(self):
        with self.assertRaises(ValueError):engine(lambda m:m['objects'][0].update(privacy='PRIVATE'))
    def test_refuses_relation_with_power(self):
        with self.assertRaises(ValueError):engine(lambda m:m['relations'][0].update(effect_authority='APPROVED'))
    def test_refuses_dangling_relation(self):
        with self.assertRaises(ValueError):engine(lambda m:m['relations'][0].update(to='ghost'))
    def test_rejects_unbounded_pulse_limit(self):
        with self.assertRaises(ValueError):engine(lambda m:m['policy'].update(max_work_per_pulse=1_000_000))
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):json.loads('{"k":1,"k":2}', object_pairs_hook=reject_duplicate_keys)
    def test_public_gap_explicitly_unknown(self):
        self.assertEqual({x['id']: x['state'] for x in CoAlive(SOURCE).manifest['gaps']},
                         {'x2-currentness':'NOT_OBSERVED','physical-mouse':'HELD','independent-first-use':'UNKNOWN'})


class Intake(unittest.TestCase):
    def test_no_event_no_work_initial_tick(self):
        a=engine().pulse(0);self.assertEqual(a['processed_count'],0);self.assertEqual(a['pending_count'],0)
    def test_valid_shadow_event(self):
        a=engine().pulse(0,[signal()]);self.assertEqual(a['admissions'][0]['outcome'],'ADMITTED_SHADOW_ONLY')
    def test_no_clipboard_exfiltration_fields(self):
        e=signal();e['clipboard_text']='secret';a=engine().pulse(0,[e]);self.assertEqual(a['admissions'][0]['outcome'],'HOLD_MALFORMED_OR_PRIVATE_FIELDS')
    def test_private_event_held(self):
        a=engine().pulse(0,[signal(scope='PRIVATE')]);self.assertEqual(a['admissions'][0]['outcome'],'HOLD_UNAUTHORIZED_EVENT')
    def test_unknown_event_kind_held(self):
        a=engine().pulse(0,[signal(kind='EXECUTE_CURL')]);self.assertEqual(a['admissions'][0]['outcome'],'HOLD_UNAUTHORIZED_EVENT')
    def test_missing_source_held(self):
        e=signal();e['source_blob_sha']='0'*40;a=engine().pulse(0,[e]);self.assertEqual(a['admissions'][0]['outcome'],'HOLD_SOURCE_MISMATCH')
    def test_unknown_resource_held(self):
        e=signal();e['object_id']='unknown';a=engine().pulse(0,[e]);self.assertEqual(a['admissions'][0]['outcome'],'HOLD_UNKNOWN_IDENTITY')
    def test_duplicate_event_idempotent(self):
        e=engine();a=e.pulse(0,[signal('same')]);b=e.pulse(0,[signal('same')]);self.assertEqual(b['admissions'][0]['outcome'],'DEDUPLICATED')
    def test_id_collision_held(self):
        e=engine();e.pulse(0,[signal('same')]);self.assertEqual(e.pulse(0,[signal('same',obj='spiff')])['admissions'][0]['outcome'],'HOLD_EVENT_ID_COLLISION')
    def test_event_cap_holds_new(self):
        e=engine(lambda m:m['policy'].update(max_seen_entries=1));e.pulse(0,[signal('a')]);self.assertEqual(e.pulse(0,[signal('b')])['admissions'][0]['outcome'],'HOLD_SEEN_CAPACITY')
    def test_queue_cap_held(self):
        e=engine(lambda m:m['policy'].update(max_pending=1,max_work_per_pulse=1));e.pulse(0,[signal('a')]);e.pulse(0,[signal('b')]);e.pulse(0,[signal('c')]);out=e.pulse(0,[signal('d')]);self.assertIn(out['admissions'][0]['outcome'],{'HOLD_QUEUE_CAPACITY','ADMITTED_SHADOW_ONLY'})
    def test_revoked_no_future_wake(self):
        e=engine();e.revoke('mouse');self.assertEqual(e.pulse(4,[signal('before')])['admissions'][0]['outcome'],'HOLD_REVOKED')
    def test_nonmonotonic_tick(self):
        e=engine();e.pulse(5);self.assertRaises(ValueError,e.pulse,4)


class RelationalPulse(unittest.TestCase):
    def test_periodic_due_is_proposal_only(self):
        e=engine();a=e.pulse(4);self.assertTrue(any(p['kind']=='SOURCE_REVIEW_DUE' for p in a['processed']))
    def test_cycles_suppressed(self):
        e=engine(lambda m:m['policy'].update(max_hops=3,max_work_per_pulse=10));a=e.pulse(0,[signal()]);self.assertGreater(a['cycle_edges_suppressed'],0)
    def test_bounded_fanout(self):
        e=engine(lambda m:m['policy'].update(max_hops=2,max_fanout=1,max_work_per_pulse=1));a=e.pulse(0,[signal()]);self.assertLessEqual(a['processed_count'],1)
    def test_no_remote_authority_or_ack(self):
        e=engine();a=e.pulse(4,[signal()]);self.assertEqual(a['external_effects'],0);self.assertEqual(a['provider_calls'],0);self.assertEqual(a['remote_acks_observed'],0)
        self.assertTrue(all(p['effect_authority']=='NONE' and p['receiver_ack']=='NOT_OBSERVED' for p in a['processed']))
    def test_processing_eventually_drains(self):
        e=engine(lambda m:m['policy'].update(max_work_per_pulse=1,max_hops=2));e.pulse(0,[signal()]);
        for _ in range(8):e.pulse(0)
        self.assertEqual(e.pending,[])
    def test_no_repeat_roots_on_same_tick(self):
        e=engine();a=e.pulse(4);b=e.pulse(4);self.assertTrue(a['processed_count']>0);self.assertEqual(b['processed_count'],0)
    def test_relation_dedupe_same_wave(self):
        e=engine(lambda m:m['policy'].update(max_work_per_pulse=8));a=e.pulse(4,[signal()]);self.assertGreaterEqual(a['duplicate_proposals_suppressed'],1)
    def test_gap_not_auto_promoted(self):
        e=engine();e.pulse(20);self.assertTrue(all(g['state']!='ACKNOWLEDGED' for g in e.manifest['gaps']))


class Recovery(unittest.TestCase):
    def test_snapshot_reconstruction(self):
        e=engine(lambda m:m['policy'].update(max_work_per_pulse=1));e.pulse(0,[signal()]);snap=e.snapshot();r=CoAlive(canonical_bytes(e.manifest),snap)
        self.assertEqual(r.snapshot(),snap);self.assertEqual(r.pulse(0),e.pulse(0))
    def test_snapshot_no_alias(self):
        e=engine();e.pulse(0,[signal()]);before=e.snapshot();other=e.snapshot();other['payload']['pending'].clear();self.assertEqual(e.snapshot(),before)
    def test_changed_manifest_rejected(self):
        e=engine();snap=e.snapshot();changed=copy.deepcopy(M);changed['gaps'][0]['description']+=' altered';
        with self.assertRaisesRegex(ValueError,'SPEC_NAMESPACE_CHANGED'):CoAlive(canonical_bytes(changed),snap)
    def test_tampered_snapshot_detected(self):
        e=engine();snap=e.snapshot();snap['payload']['last_tick']=999
        with self.assertRaisesRegex(ValueError,'SNAPSHOT_TAMPERED'):CoAlive(canonical_bytes(M),snap)
    def test_forged_pending_without_seen_rejected(self):
        e=engine();snap=e.snapshot();snap['payload']['pending']=[{'id':'ghost:root','object_id':'mouse','kind':'SOURCE_REVIEW_DUE','root_id':'ghost','depth':0,'trail':['mouse']}];snap['state_sha256']=digest(snap['payload'])
        with self.assertRaises(ValueError):CoAlive(canonical_bytes(M),snap)
    def test_source_namespace_survives_restart(self):
        e=CoAlive(SOURCE);e.pulse(4,[signal('a')]);snap=e.snapshot();r=CoAlive(SOURCE,snap);self.assertEqual(e.manifest_hash,r.manifest_hash)
    def test_revocation_survives_restart(self):
        e=CoAlive(SOURCE);e.revoke('mouse');r=CoAlive(SOURCE,e.snapshot());self.assertEqual(r.pulse(4,[signal('a')])['admissions'][0]['outcome'],'HOLD_REVOKED')
    def test_pending_relation_forgery_rejected_even_if_self_rehashed(self):
        e=engine(lambda m:m['policy'].update(max_work_per_pulse=1));e.pulse(0,[signal()]);s=e.snapshot();
        q=s['payload']['pending'][0];q['trail']=['mouse','morph'];q['object_id']='morph';q['depth']=1;q['kind']='RELATION_CHALLENGE';s['state_sha256']=digest(s['payload']);
        with self.assertRaises(ValueError):CoAlive(canonical_bytes(e.manifest),s)
    def test_snapshot_limits_rejected(self):
        e=engine();s=e.snapshot();s['payload']['seen']={f'e{i}':'0'*64 for i in range(2050)};s['state_sha256']=digest(s['payload']);
        with self.assertRaises(ValueError):CoAlive(canonical_bytes(e.manifest),s)


if __name__=='__main__':unittest.main()
