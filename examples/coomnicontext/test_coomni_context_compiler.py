import copy
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from CoOmniContextCompilerR0 import compile_packet, rehydrate_public, source_sha


def src(id, text, role='SOURCE', visibility='PUBLIC', epistemic='OBSERVED'):
    return dict(id=id,text=text,sha256=source_sha(text),role=role,visibility=visibility,epistemic=epistemic)


def fixture():
    guide = ('First-use guide: inspect a source, preview, accept and undo. CoOrb contextual choices. Verify keyboard accessibility, source identity, device reach, fallback, permission and interruption cost. ' * 18).strip()
    challenge = ('Challenge: no independent human first-use acceptance or provider-independent restore receipt. User failure, absent consent, privacy leakage and stale source are counterexamples. ' * 12).strip()
    fallback = ('Baseline: preserve a standalone accessible text view for recovery and compare against a task-first flow. ' * 8).strip()
    return dict(schema='CoAll.ContextSources.R0',work_id='COOMNI_SAMPLE_001',intent='improve CoOrb first use recovery',sources=[
        src('public-guide',guide),
        src('challenge',challenge, 'CHALLENGE','PUBLIC','HYPOTHESIS'),
        src('fallback',fallback,'BASELINE'),
        src('private-example','NOT FOR PUBLIC CONTEXT: synthetic restricted material.','SOURCE','RESTRICTED'),
        src('other','Visible event log and exact SHA references for CoOrb.', 'SOURCE'),
    ])

class ContextTests(unittest.TestCase):
    def test_01_basic(self):
        p=compile_packet(fixture());self.assertEqual(p['status'],'PASS_BOUNDED')
    def test_02_preserves_challenge(self):
        p=compile_packet(fixture());self.assertIn('challenge',[s['id'] for s in p['sources']])
    def test_03_preserves_source(self):
        p=compile_packet(fixture());self.assertTrue(any(s['role']=='SOURCE' for s in p['sources']))
    def test_04_privacy(self):
        p=compile_packet(fixture());self.assertEqual(p['withheld_nonpublic'],1);self.assertNotIn('restricted',json.dumps(p).lower())
    def test_05_budget(self):
        for lim in [900,1000,1200,1800,2500]:
            p=compile_packet(fixture(),lim);self.assertLessEqual(len(json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),lim)
    def test_06_deterministic(self):
        self.assertEqual(compile_packet(fixture()),compile_packet(fixture()))
    def test_07_rehydrate(self):
        d=fixture();x=d['sources'][0];self.assertEqual(rehydrate_public(d,x['id'],x['sha256']),x['text'])
    def test_08_private_rehydrate_denied(self):
        d=fixture();x=d['sources'][3];
        with self.assertRaises(PermissionError):rehydrate_public(d,x['id'],x['sha256'])
    def test_09_stale(self):
        d=fixture();x=d['sources'][0];
        with self.assertRaises(ValueError):rehydrate_public(d,x['id'],'0'*64)
    def test_10_sha_tamper(self):
        d=fixture();d['sources'][0]['text']+=' changed'
        with self.assertRaisesRegex(ValueError,'DIGEST'):compile_packet(d)
    def test_11_unknown_visibility_fails(self):
        d=fixture();d['sources'][0]['visibility']='WHO_KNOWS'
        with self.assertRaisesRegex(ValueError,'UNKNOWN_VISIBILITY'):compile_packet(d)
    def test_12_missing_visibility_fails(self):
        d=fixture();del d['sources'][0]['visibility']
        with self.assertRaisesRegex(ValueError,'UNKNOWN_VISIBILITY'):compile_packet(d)
    def test_13_bad_role(self):
        d=fixture();d['sources'][0]['role']='SEND_EMAIL'
        with self.assertRaisesRegex(ValueError,'UNKNOWN_ROLE'):compile_packet(d)
    def test_14_no_challenge_held(self):
        d=fixture();d['sources']=[s for s in d['sources'] if s['role']!='CHALLENGE'];p=compile_packet(d)
        self.assertEqual(p['status'],'HELD');self.assertIn('NO_PUBLIC_CHALLENGE',p['missing'])
    def test_15_private_challenge_not_enough(self):
        d=fixture();d['sources'][1]['visibility']='RESTRICTED';p=compile_packet(d)
        self.assertEqual(p['status'],'HELD');self.assertIn('NO_PUBLIC_CHALLENGE',p['missing'])
    def test_16_duplicate_id(self):
        d=fixture();d['sources'][1]['id']=d['sources'][0]['id']
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):compile_packet(d)
    def test_17_invalid_budget(self):
        with self.assertRaisesRegex(ValueError,'BUDGET'):compile_packet(fixture(),120)
    def test_18_small_budget_held(self):
        p=compile_packet(fixture(),700);self.assertEqual(p['status'],'HELD');self.assertIn('BUDGET_CANNOT_PRESERVE_CORE_AND_CHALLENGE',p['missing'])
    def test_19_token_not_claimed(self):
        p=compile_packet(fixture());self.assertIn('PACKET_NE_INFINITE_CONTEXT',p['nonclaims'])
    def test_20_no_output_mutation(self):
        d=fixture();before=copy.deepcopy(d);compile_packet(d);self.assertEqual(before,d)
    def test_21_source_digest(self):
        self.assertEqual(source_sha('abc'),hashlib.sha256(b'abc').hexdigest())
    def test_22_no_private_ids(self):
        d=fixture();d['sources'][3]['id']='PRIVATE_SECRET_IDENTIFIER';p=compile_packet(d)
        self.assertNotIn('PRIVATE_SECRET_IDENTIFIER',json.dumps(p))
    def test_23_unknown_epistemic(self):
        d=fixture();d['sources'][0]['epistemic']='PROVEN_BY_AI'
        with self.assertRaisesRegex(ValueError,'EPISTEMIC'):compile_packet(d)
    def test_24_too_many_sources(self):
        d=fixture();d['sources']=d['sources']*30
        with self.assertRaises(ValueError):compile_packet(d)

if __name__=='__main__': unittest.main(verbosity=2)
