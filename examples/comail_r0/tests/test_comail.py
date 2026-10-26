"""Semantic negative tests for the synthetic CoMail fixed-message/living-resource twin."""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core import validate,read_fixture,digest_version,text_sha,sha,json_bytes,update_pins
import build

class CoMailR0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=read_fixture(ROOT/"fixture.json")

    def test_00_scoped_pass(self):
        self.assertEqual(validate(self.fixture)["status"],"PASS_BOUNDED_SYNTHETIC_R0")
    def test_01_no_actual_send(self):
        self.assertEqual(validate(self.fixture)["actual_sends"],0)
    def test_02_no_subscribers(self):
        self.assertEqual(validate(self.fixture)["actual_subscribers"],0)
    def test_03_exact_version_count(self):
        self.assertEqual(validate(self.fixture)["version_count"],3)
    def test_04_fixed_note_pinned(self):
        m=self.fixture['fixed_message'];self.assertEqual(m['sha256'],sha(json_bytes({k:v for k,v in m.items() if k!='sha256'})))
    def test_05_current_head_pinned(self):
        r=self.fixture['resource'];self.assertEqual(r['current_sha256'],r['versions'][-1]['sha256'])
    def test_06_chain_linked(self):
        v=self.fixture['resource']['versions'];self.assertEqual([x['predecessor'] for x in v],[None,'v0','v1'])
    def test_07_hashes_distinct(self):
        self.assertEqual(len({x['sha256'] for x in self.fixture['resource']['versions']}),3)
    def test_08_versions_increment(self):
        self.assertEqual([x['id'] for x in self.fixture['resource']['versions']],['v0','v1','v2'])
    def test_09_source_donors_named(self):
        self.assertEqual(len(self.fixture['source_contracts']),3)
    def test_10_no_recipient_ids(self):
        for part in (self.fixture,self.fixture['distribution'],self.fixture['fixed_message'],self.fixture['resource']):
            for k in ('to','from','cc','bcc','email','recipient_id'):
                self.assertNotIn(k,part)
    def test_11_original_claim_visible(self):
        self.assertIn('fixed historical example',self.fixture['fixed_message']['body'])
    def test_12_free_is_not_payment(self):
        v=self.fixture['resource']['versions'][-1];self.assertIn('accepts no money',v['body'])
    def test_13_draft_is_not_sent(self):
        self.assertEqual(self.fixture['fixed_message']['state'],'SYNTHETIC_NOT_SENT')
    def test_14_local_only_feedback(self):
        self.assertEqual(self.fixture['distribution']['feedback_runtime'],'LOCAL_UNSENT_ONLY')
    def test_15_offline_csp(self):
        h=build.make_html(self.fixture);self.assertIn("connect-src 'none'",h);self.assertIn("form-action 'none'",h)
    def test_16_compiler_escapes_html_json(self):
        mock=copy.deepcopy(self.fixture)
        mock['resource']['versions'][0]['body']='</script><img src=x onerror=alert(1)>'
        update_pins(mock);validate(mock);h=build.make_html(mock)
        self.assertNotIn('</script><img',h)
        self.assertIn('\\u003c/script\\u003e',h)
    def test_17_deterministic_build(self):
        self.assertEqual(build.outputs()['index.html'],(ROOT/'index.html').read_text('utf-8'))
    def test_18_deterministic_atom(self):
        self.assertEqual(build.outputs()['feed.atom'],(ROOT/'feed.atom').read_text('utf-8'))
    def test_19_deterministic_receipt(self):
        self.assertEqual(build.outputs()['receipt.json'],(ROOT/'receipt.json').read_text('utf-8'))
    def test_20_atom_valid_xml(self):
        root=ET.fromstring(build.make_atom(self.fixture));self.assertTrue(root.tag.endswith('feed'))
    def test_21_atom_versions(self):
        root=ET.fromstring(build.make_atom(self.fixture));n='{http://www.w3.org/2005/Atom}';self.assertEqual(len(root.findall(n+'entry')),3)
    def test_22_atom_has_author(self):
        root=ET.fromstring(build.make_atom(self.fixture));n='{http://www.w3.org/2005/Atom}';self.assertIsNotNone(root.find(n+'author'))
    def test_23_no_network_js(self):
        template=(ROOT/'template.html').read_text('utf-8');self.assertNotIn('fetch(',template);self.assertNotIn('XMLHttpRequest',template);self.assertNotIn('WebSocket(',template)
    def test_24_no_persistent_storage_js(self):
        template=(ROOT/'template.html').read_text('utf-8');self.assertNotIn('localStorage',template);self.assertNotIn('sessionStorage',template)
    def test_25_no_auto_send(self):
        self.assertIn("delivery:'NOT_SENT'",(ROOT/'template.html').read_text('utf-8'))
    def test_26_feedback_click_required(self):
        self.assertIn("el('save-feedback').addEventListener('click'",(ROOT/'template.html').read_text('utf-8'))
    def test_27_no_auto_donation(self):
        self.assertNotIn('payment_url',json.dumps(self.fixture))
    def test_28_has_reduced_motion(self):
        self.assertIn('prefers-reduced-motion',(ROOT/'template.html').read_text('utf-8'))
    def test_29_has_mobile_media_query(self):
        self.assertIn('max-width:720px',(ROOT/'template.html').read_text('utf-8'))
    def test_30_historical_message_not_current(self):
        self.assertNotEqual(self.fixture['fixed_message']['message_id'],self.fixture['resource']['resource_id'])
    def test_31_explicit_uncertainties(self):
        self.assertIn('NO_PUBLIC_SITE_ADOPTION',self.fixture['nonclaims'])
    def test_32_static_feed_not_live(self):
        self.assertIn('no live subscription',build.make_atom(self.fixture).lower())
    def test_33_no_external_urls(self):
        self.assertNotIn('https://',json.dumps(self.fixture));self.assertNotIn('http://',json.dumps(self.fixture))
    def test_34_code_utf8_sha(self):
        self.assertEqual(text_sha('abc'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    def test_35_fixed_resource_binding(self):
        self.assertEqual(self.fixture['fixed_message']['resource_ref'],self.fixture['resource']['resource_id'])
    def test_36_no_mutating_builder(self):
        proc=subprocess.run([sys.executable,str(ROOT/'build.py'),'--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)


def wrong(mutator):
    t=copy.deepcopy(CoMailR0.fixture)
    mutator(t)
    with unittest.TestCase().assertRaises(ValueError):validate(t)

MUTATIONS = {
'schema_swap':lambda t:t.__setitem__('schema','unknown'),
'private_visibility':lambda t:t.__setitem__('visibility','PRIVATE'),
'effect_auto_send':lambda t:t['distribution'].__setitem__('auto_send',True),
'fake_sent_delivery':lambda t:t['distribution'].__setitem__('delivery_evidence','SENT'),
'fake_ack_delivery':lambda t:t['distribution'].__setitem__('delivery_evidence','ACKED'),
'fake_subscriber':lambda t:t['distribution'].__setitem__('actual_recipient_count',1),
'fake_subscription':lambda t:t['distribution'].__setitem__('subscription_runtime','ACTIVE'),
'fake_payment':lambda t:t['distribution'].__setitem__('payment_runtime','ENABLED'),
'live_feedback':lambda t:t['distribution'].__setitem__('feedback_runtime','AUTO_SEND'),
'fake_message_sent':lambda t:t['fixed_message'].__setitem__('state','SENT'),
'edit_fixed_note':lambda t:t['fixed_message'].__setitem__('body','Hidden rewrite'),
'swap_message_hash':lambda t:t['fixed_message'].__setitem__('sha256','0'*64),
'edit_old_version':lambda t:t['resource']['versions'][0].__setitem__('body','Tampered old source'),
'edit_current_version':lambda t:t['resource']['versions'][-1].__setitem__('body','Tampered latest source'),
'edit_revision_reason':lambda t:t['resource']['versions'][1].__setitem__('why_changed','Tampered explanation'),
'edit_revision_time':lambda t:t['resource']['versions'][1].__setitem__('observed_at','2000-01-01T00:00:00Z'),
'bad_utc':lambda t:t['resource']['versions'][1].__setitem__('observed_at','2026-10-25T10:00:00-04:00'),
'missing_predecessor':lambda t:t['resource']['versions'][1].__setitem__('predecessor',None),
'reversed_chain':lambda t:t['resource']['versions'][2].__setitem__('predecessor','v0'),
'duplicate_version':lambda t:t['resource']['versions'][1].__setitem__('id','v0'),
'wrong_head':lambda t:t['resource'].__setitem__('current','v0'),
'wrong_head_digest':lambda t:t['resource'].__setitem__('current_sha256','1'*64),
'false_review_authority':lambda t:t['resource']['versions'][1].__setitem__('state','PUBLISHED'),
'rights_removed':lambda t:t['resource'].__setitem__('rights','UNKNOWN'),
'false_maturity':lambda t:t['resource'].__setitem__('epistemic_status','LIVE'),
'add_send_param':lambda t:t['distribution'].__setitem__('send_on_change',True),
'add_payment_endpoint':lambda t:t['resource'].__setitem__('payment_url','https://pay.example'),
'add_recipient':lambda t:t['fixed_message'].__setitem__('to','person@example.org'),
'email_in_body':lambda t:t['fixed_message'].__setitem__('body','Send to hidden@example.org'),
'url_in_body':lambda t:t['resource']['versions'][0].__setitem__('body','Open https://unverified.example'),
'forge_donor':lambda t:t['source_contracts'][0].__setitem__('blob_sha','badsha'),
'missing_donors':lambda t:t.__setitem__('source_contracts',[]),
'extra_source_field':lambda t:t['source_contracts'][1].__setitem__('secret','unknown'),
'wrong_nonclaims':lambda t:t.__setitem__('nonclaims',[]),
'no_versions':lambda t:t['resource'].__setitem__('versions',[]),
'extra_top_level':lambda t:t.__setitem__('sponsor_endpoint','nonexistent'),
'invent_approval':lambda t:t['resource']['versions'][0].__setitem__('review_approved',True),
'wrong_living_resource':lambda t:t['fixed_message'].__setitem__('resource_ref','urn:co:resource:synthetic:different')
}

def _make_test(fn):
    def test(self):
        a=copy.deepcopy(self.fixture)
        fn(a)
        with self.assertRaises(ValueError):validate(a)
    return test

for suffix,mutator in MUTATIONS.items():
    setattr(CoMailR0,'test_reject_'+suffix,_make_test(mutator))

if __name__=='__main__':unittest.main()
