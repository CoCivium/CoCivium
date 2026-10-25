from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import codoodle
import nexus

RAW=(ROOT/'sample_synthetic.txt').read_text(encoding='utf-8')
SEEDS=codoodle.compile_doodle(RAW)

class CoNexTests(unittest.TestCase):
    def test_deterministic_same_seed(self):
        self.assertEqual(nexus.expand(SEEDS,140),nexus.expand(SEEDS,140))

    def test_different_seeds_vary_branch_selection(self):
        a=nexus.expand(SEEDS,140,fanout=3,max_total=24)
        b=nexus.expand(SEEDS,141,fanout=3,max_total=24)
        self.assertNotEqual([(x['branch']) for x in a['variants']],[(x['branch']) for x in b['variants']])

    def test_initial_inverse_every_nexus(self):
        a=nexus.expand(SEEDS,0,max_total=24)
        first=a['variants'][:SEEDS['candidate_count']]
        self.assertEqual(len(first),SEEDS['candidate_count'])
        self.assertTrue(all(x['branch']=='NOT_ELSE' for x in first))

    def test_small_budget_fairness(self):
        a=nexus.expand(SEEDS,2,max_total=4)
        self.assertEqual(a['emitted'],4)
        self.assertEqual(a['held_for_budget'],SEEDS['candidate_count']*2-4)
        self.assertEqual(len(set(x['nexus_parent_id'] for x in a['variants'])),4)

    def test_all_zero_effects(self):
        a=nexus.expand(SEEDS,4,fanout=3,max_total=24)
        self.assertTrue(all(x==0 for x in a['effects'].values()))
        self.assertTrue(all(x['executed'] is False for x in a['variants']))

    def test_spans_retained_and_raw_excluded(self):
        a=nexus.expand(SEEDS,7)
        self.assertEqual(a['parent_source_sha256'],SEEDS['source']['sha256'])
        self.assertNotIn(RAW,json.dumps(a))
        for v in a['variants']:
            self.assertIn(v['source_span_chars'],[p['source_span_chars'] for p in SEEDS['candidates']])
            self.assertNotIn('source_match',v)

    def test_symbolic_class_never_promotes(self):
        a=nexus.expand(SEEDS,77,fanout=3,max_total=24)
        for v in a['variants']:
            if v['original_family']=='symbolic_context':
                self.assertEqual(v['original_epistemic_class'],'SYMBOLIC_OR_SPECULATIVE')
                self.assertEqual(v['readiness'],'PROPOSAL_ONLY_UNSCORED')

    def test_external_effect_held(self):
        a=nexus.expand(codoodle.compile_doodle('publish outreach now'),6)
        self.assertTrue(all(x['effect_boundary']=='EXTERNAL_ACTION_HELD' for x in a['variants']))

    def test_empty_match_yields_zero_variants(self):
        a=nexus.expand(codoodle.compile_doodle('Ordinary table lamp.'),42)
        self.assertEqual(a['emitted'],0)

    def test_boolean_and_bad_seed_rejected(self):
        for bad in (True,False,-1,2**64,'42',None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError): nexus.expand(SEEDS,bad)

    def test_invalid_budgets_rejected(self):
        for f,t in [(0,12),(4,24),(1,0),(3,25),(True,2),(1,False)]:
            with self.subTest(f=f,t=t):
                with self.assertRaises(ValueError):nexus.expand(SEEDS,0,fanout=f,max_total=t)

    def test_invalid_schema(self):
        with self.assertRaises(ValueError): nexus.expand({'schema':'other'},0)

    def test_false_execution_claim_refused(self):
        v=json.loads(json.dumps(SEEDS))
        v['candidates'][0]['experiment_executed']=True
        with self.assertRaises(ValueError):nexus.expand(v,0)

    def test_digest_identity_mismatch_refused(self):
        v=json.loads(json.dumps(SEEDS))
        v['candidates'][0]['candidate_id']='codoodle:not-source:dummy'
        with self.assertRaises(ValueError):nexus.expand(v,0)

    def test_outward_claim_not_promoted(self):
        a=nexus.expand(codoodle.compile_doodle('ETs God G_d quantum signals all proven'),42)
        self.assertEqual(a['state'],'SEEDED_VARIANTS__ZERO_EXECUTION')
        self.assertEqual(a['effects']['provider_calls'],0)

    def test_json_cli_explicit_input_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'in.json'
            dest=Path(d)/'out.json'
            p.write_text(json.dumps(SEEDS),encoding='utf-8')
            command=[sys.executable,str(ROOT/'nexus.py'),'--input',str(p),'--seed','9','--output',str(dest)]
            a=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(a.returncode,0,a.stderr)
            self.assertEqual(json.loads(dest.read_text())['seed_u64'],9)
            before=dest.read_bytes()
            b=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(b.returncode,0)
            self.assertEqual(before,dest.read_bytes())

    def test_cli_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.json'; link=Path(d)/'link.json'
            p.write_text(json.dumps(SEEDS),encoding='utf-8')
            link.symlink_to(p)
            r=subprocess.run([sys.executable,str(ROOT/'nexus.py'),'--input',str(link),'--seed','4'],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)

    def test_source_catalog_is_classified_no_auto_fetch(self):
        data=json.loads((ROOT/'discovery_catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(data['execution'],'NO_NETWORK_SOURCE_CATALOG_ONLY')
        self.assertTrue(any(x['lane']=='CO_ET_SCIENCE' for x in data['sources']))
        self.assertTrue(any(x['lane']=='CO_GD_PHILOSOPHY' for x in data['sources']))
        self.assertTrue(all(x['live_connection']=='NOT_CONFIGURED' for x in data['sources']))
        self.assertTrue(all(x['claim_type']!='confirmed_ET' for x in data['sources']))

    def test_provider_registry_has_no_credentials(self):
        d=json.loads((ROOT/'provider_routes.json').read_text(encoding='utf-8'))
        self.assertEqual(d['status'],'DESIGN_ONLY__NO_AUTHENTICATED_PROVIDERS')
        self.assertTrue(all(p['credential_state']=='NOT_INSPECTED' for p in d['providers']))
        self.assertTrue(all(p['autorun'] is False for p in d['providers']))
        self.assertNotIn('api_key',json.dumps(d).lower())

    def test_no_meta_randomness_or_workers(self):
        import inspect
        src=inspect.getsource(nexus)
        for s in ('requests','urlopen','subprocess.','multiprocessing','ThreadPoolExecutor','getpass','pyautogui'):
            self.assertNotIn(s,src)
        self.assertIn('SHA256_LEXICOGRAPHIC_ORDER_R0_NOT_SECURITY_RANDOM',src)

if __name__=='__main__':
    unittest.main()
