import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import CoDoodleCardBridgeR0 as a

HEX='c'*64

def row(scenario='ENGINEERING_DEVICE', operator='NULL', cid='b'*20, epistemic=None, review=None):
    if epistemic is None:
        epistemic=a.ALLOWED_SCENARIOS[scenario][0]
    if review is None:
        review=('PASS_SHADOW_POLICY_ONLY' if scenario in ('ENGINEERING_DEVICE','INTERSTICE_UI')
                else 'HELD_NO_QUALIFIED_EXECUTOR_OR_EMPIRICAL_EVIDENCE')
    return {'candidate_id':cid,'logical_index':'123',
            'axes':{'scenario':scenario,'operator':operator,'surface':'TEXT', 'temporal':'FORECAST','observer':'SKEPTIC'},
            'epistemic_class':epistemic, 'proof_boundary':'HELD' if scenario!='ENGINEERING_DEVICE' else 'BOUNDED',
            'authority':'NONE','effects':{'provider_calls':0,'network':0,'devices':0,'emails':0,'workers':0},
            'micro_canary_eligible':True if scenario in ('ENGINEERING_DEVICE','INTERSTICE_UI') else False,
            'review_state':review, 'score':90}

def frontier(rows=None):
    xs=rows if rows is not None else [row()]
    return {'schema':a.FRONTIER_SCHEMA,'source_sha256':HEX,'seed':'public-synthetic',
            'selected':xs,'selected_count':len(xs),'no_execution':True,'active_workers':0,
            'total_syntactic_descriptors':'2247370997760'}

class CardBridgeTests(unittest.TestCase):
    def assertHeld(self,fr):
        with self.assertRaises(ValueError):a.compile_cards(fr)
    def test_empty(self):
        self.assertEqual(a.compile_cards(frontier([]))['selected_count'],0)
    def test_public_synthetic(self):
        o=a.compile_cards(frontier());self.assertEqual(o['selected_count'],1)
        self.assertFalse(o['receiver_ack']);self.assertFalse(o['auto_publish'])
    def test_stable_json(self):
        f=frontier();self.assertEqual(a.canonical(a.compile_cards(f)),a.canonical(a.compile_cards(f)))
    def test_source_bound(self):
        o=a.compile_cards(frontier());self.assertEqual(o['cards'][0]['source_sha256'],HEX)
        self.assertEqual(o['input_frontier_sha256'],a.sha(a.canonical(frontier())))
    def test_zero_effects(self):
        o=a.compile_cards(frontier());self.assertEqual(o['external_effects'],0)
        self.assertEqual(o['cards'][0]['effects']['workers'],0)
    def test_gd_philosophical(self):
        f=frontier([row(scenario='G_D_PHILOSOPHY')]);o=a.compile_cards(f)
        self.assertIn('PHILOSOPHICAL',o['cards'][0]['epistemic_class'])
        self.assertEqual(o['cards'][0]['status'],'PROPOSAL_ONLY_NOT_EXECUTED')
    def test_et_rfi_control(self):
        o=a.compile_cards(frontier([row(scenario='ET_TECHNOSIGNATURE',operator='FALSIFIER')]))
        self.assertIn('interference',o['cards'][0]['question'])
    def test_synthkind_fiction(self):
        o=a.compile_cards(frontier([row(scenario='SYNTHKIND_FICTION')]))
        self.assertEqual(o['cards'][0]['epistemic_class'],'SPECULATIVE_STORY')
        self.assertIn('fictional',o['cards'][0]['alternative'])
    def test_accessible_glyph_labels(self):
        f=frontier([row(operator='INVERSE')]);o=a.compile_cards(f)
        self.assertEqual(o['cards'][0]['glyph_ascii'],'INV')
        self.assertTrue(o['cards'][0]['glyph_plain_label'])
    def test_no_private_source_text(self):
        o=a.compile_cards(frontier());self.assertTrue(o['source_text_republished'] is False)
        self.assertNotIn('raw_source',json.dumps(o))
    def test_more_than_limit(self):
        with self.assertRaises(ValueError):a.compile_cards(frontier(),9)
    def test_boolean_limit(self):
        with self.assertRaises(ValueError):a.compile_cards(frontier(),True)
    def test_limit_zero(self):
        self.assertEqual(a.compile_cards(frontier(),0)['selected_count'],0)
    def test_missing_schema(self):
        f=frontier();f['schema']='UNTRUSTED';self.assertHeld(f)
    def test_no_execution_false(self):
        f=frontier();f['no_execution']=False;self.assertHeld(f)
    def test_worker_nonzero(self):
        f=frontier();f['active_workers']=1;self.assertHeld(f)
    def test_select_count_false(self):
        f=frontier();f['selected_count']=2;self.assertHeld(f)
    def test_duplicate(self):
        f=frontier([row(),row()]);self.assertHeld(f)
    def test_more_than_32(self):
        f=frontier([row(cid=format(i,'020x')) for i in range(33)]);self.assertHeld(f)
    def test_bad_authority(self):
        f=frontier();f['selected'][0]['authority']='SEND';self.assertHeld(f)
    def test_bad_provider_effect(self):
        f=frontier();f['selected'][0]['effects']['provider_calls']=1;self.assertHeld(f)
    def test_boolean_effect(self):
        f=frontier();f['selected'][0]['effects']['network']=False;self.assertHeld(f)
    def test_negative_worker(self):
        f=frontier();f['selected'][0]['effects']['workers']=-1;self.assertHeld(f)
    def test_false_et_pass(self):
        f=frontier([row(scenario='ET_TECHNOSIGNATURE',review='PASS_SHADOW_POLICY_ONLY')]);self.assertHeld(f)
    def test_false_science_promotion(self):
        f=frontier([row(scenario='G_D_PHILOSOPHY',epistemic='MEASURED')]);self.assertHeld(f)
    def test_missing_fields(self):
        f=frontier();del f['selected'][0]['axes']['operator'];self.assertHeld(f)
    def test_bad_hash(self):
        f=frontier();f['source_sha256']='z'*64;self.assertHeld(f)
    def test_bad_scenario(self):
        f=frontier();f['selected'][0]['axes']['scenario']='REAL_ET';self.assertHeld(f)
    def test_bounded_story_canaries(self):
        rows=[row(scenario=s,cid=format(i+1,'020x')) for i,s in enumerate(a.ALLOWED_SCENARIOS)]
        out=a.compile_cards(frontier(rows))
        self.assertEqual(out['selected_count'],5)
        self.assertEqual({c['scenario'] for c in out['cards']},set(a.ALLOWED_SCENARIOS))
        self.assertTrue(all(c['independent_receiver_ack'] is False for c in out['cards']))
    @unittest.skipUnless((Path(__file__).resolve().parent/'CoDoodleNexR1.py').exists(),'R1 core not staged locally; CI runs integration')
    def test_actual_mainline_r1_module_integration(self):
        core=a.load_core()
        source=json.loads((Path(__file__).resolve().parent/'synthetic_source.json').read_text())
        core.validate_fixture(source)
        a0,b=a.run_from_r1(source,'co-doodle-integration',6,5)
        self.assertEqual(a0['selected_count'],6)
        self.assertEqual(a0['external_effects'],0)
        self.assertGreater(b['median_ns'],0)
        self.assertEqual(a0['source_sha256'],core.sha(core.canonical(source)))

if __name__ == '__main__':unittest.main()
