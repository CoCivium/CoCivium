"""One pinned public candidate set, several loss-declared audience projections."""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coaudience_circuit_r0 import render, validate
from conav_retro_r0 import read_manifest

MANIFEST = ROOT/'conav_retro_manifest_r0.json'
POLICY = ROOT/'coaudience_circuit_policy_r0.json'
DIAGRAM = ROOT/'coaudience_circuit_r0.md'
SCRIPT = ROOT/'coaudience_circuit_r0.py'


class CircuitTests(unittest.TestCase):
    def setUp(self):
        self.raw = MANIFEST.read_bytes()
        self.manifest = read_manifest(MANIFEST)
        self.policy = json.loads(POLICY.read_text())

    def test_01_same_prior_five_candidates(self):
        doc, report = render(self.policy, self.manifest, self.raw)
        self.assertEqual(report['meta_candidates'], 5)
        self.assertEqual(len(report['source_ids']), len(set(report['source_ids'])))
        self.assertEqual(report['promoted'], 0)
        self.assertEqual(report['sent'], 0)

    def test_02_saved_diagram_equals_generated_view(self):
        self.assertEqual(render(self.policy, self.manifest, self.raw)[0], DIAGRAM.read_text())

    def test_03_deterministic_replay(self):
        self.assertEqual(render(self.policy,self.manifest,self.raw),render(self.policy,self.manifest,self.raw))

    def test_04_source_blob_is_exact(self):
        self.assertEqual(self.policy['source_git_blob'],'51be2e100f4f01920c1e1cfa42af0bc6a4c78ff1')
        self.assertIn(self.policy['source_git_blob'],render(self.policy,self.manifest,self.raw)[0])

    def test_05_source_byte_drift_fails(self):
        with self.assertRaisesRegex(ValueError,'HOLD_PINNED_SOURCE_CHANGED'):
            render(self.policy,self.manifest,self.raw+b' ')

    def test_06_unknown_policy_field_fails(self):
        self.policy['approve_all'] = True
        with self.assertRaisesRegex(ValueError,'INVALID_AUDIENCE_POLICY'):
            validate(self.policy,self.manifest)

    def test_07_symbolic_gdside_has_no_grant(self):
        self.policy['g_dside_authority']='RELEASE_NOW'
        with self.assertRaisesRegex(ValueError,'G_DSIDE_CANNOT_GRANT_AUTHORITY'):
            validate(self.policy,self.manifest)

    def test_08_supply_demand_futures_all_retained(self):
        self.policy['lenses']=['G_DSIDE','SUPPLY','DEMAND']
        with self.assertRaisesRegex(ValueError,'LOSS_OF_SUPPLY_DEMAND_FUTURES_BRAID'):
            validate(self.policy,self.manifest)

    def test_09_effect_ceiling_cannot_expand(self):
        self.policy['effect_authority']='MASS_EMAIL'
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_SUBSTRATE_EFFECTS'):
            validate(self.policy,self.manifest)

    def test_10_hidden_substrate_effect_rejected(self):
        self.policy['substrates'][0]['effect_ceiling']='AUTO_EXECUTE'
        with self.assertRaisesRegex(ValueError,'SUBSTRATE_UNAUTHORIZED_ACTION'):
            validate(self.policy,self.manifest)

    def test_11_substrate_requires_loss_disclosure(self):
        self.policy['substrates'][0]['losses']=[]
        with self.assertRaisesRegex(ValueError,'MISSING_PROJECTION_LOSS_CONTRACT'):
            validate(self.policy,self.manifest)

    def test_12_audience_binding_required(self):
        self.policy['substrates'][0]['audience_ids']=['invisible_reader']
        with self.assertRaisesRegex(ValueError,'UNBOUND_SUBSTRATE_AUDIENCE'):
            validate(self.policy,self.manifest)

    def test_13_accessible_text_must_be_present(self):
        self.policy['substrates']=[s for s in self.policy['substrates'] if s['id']!='ACCESSIBLE_TEXT']
        with self.assertRaisesRegex(ValueError,'SUBSTRATE_COVERAGE_MISSING'):
            validate(self.policy,self.manifest)

    def test_14_duplicate_audience_rejected(self):
        self.policy['audiences'].append(copy.deepcopy(self.policy['audiences'][0]))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_AUDIENCE'):
            validate(self.policy,self.manifest)

    def test_15_future_has_falsifier(self):
        self.policy['audiences'][0]['falsifier']=''
        with self.assertRaisesRegex(ValueError,'INVALID_AUDIENCE_FALSIFIER'):
            validate(self.policy,self.manifest)

    def test_16_private_candidate_cannot_enter_public_view(self):
        self.manifest['candidates'][0]['visibility']='PRIVATE'
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_RETRO_PROMOTION'):
            validate(self.policy,self.manifest)

    def test_17_rights_promotion_cannot_be_inferred(self):
        self.manifest['candidates'][0]['rights_state']='LICENSE_GRANTED'
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_RETRO_PROMOTION'):
            validate(self.policy,self.manifest)

    def test_18_no_semantic_review_promotion(self):
        self.manifest['candidates'][0]['status']='ADOPTED_CANON'
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_RETRO_PROMOTION'):
            validate(self.policy,self.manifest)

    def test_19_duplicate_media_identity_fails(self):
        self.manifest['candidates'][1]['id']=self.manifest['candidates'][0]['id']
        with self.assertRaisesRegex(ValueError,'INVALID_OR_DUPLICATED_CANDIDATE'):
            validate(self.policy,self.manifest)

    def test_20_circuit_is_not_claimed_physical(self):
        doc, report=render(self.policy,self.manifest,self.raw)
        self.assertIn('CIRCUIT_NOT_EXECUTABLE',doc)
        self.assertIn('NOT OBSERVED',doc)
        self.assertIn('HOLD: links only',doc)
        self.assertFalse(report['receiver_acks'])

    def test_21_no_original_media_bytes_or_private_info(self):
        doc,_=render(self.policy,self.manifest,self.raw)
        self.assertNotIn('inseed.com',doc)
        self.assertNotIn('libfile_',doc)
        self.assertNotIn('file_000000',doc)
        self.assertNotIn('FULL_EMAIL_BODY',doc)

    def test_22_cli_check_passes_current(self):
        proc=subprocess.run([sys.executable,str(SCRIPT),'--manifest',str(MANIFEST),
            '--policy',str(POLICY),'--diagram',str(DIAGRAM),'--check'],capture_output=True,text=True,timeout=8)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertIn('EXACT_SOURCE_ONLY_PROJECTION',proc.stdout)

    def test_23_cli_fails_stale_output_without_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            altered=Path(d)/'old.md';altered.write_text('old',encoding='utf-8')
            proc=subprocess.run([sys.executable,str(SCRIPT),'--manifest',str(MANIFEST),
                '--policy',str(POLICY),'--diagram',str(altered),'--check'],capture_output=True,text=True,timeout=8)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('HOLD_STALE_CIRCUIT_VIEW',proc.stderr)
            self.assertEqual(altered.read_text(),'old')

    def test_24_cli_never_clobbers_existing(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'view.md';out.write_text('unchanged')
            proc=subprocess.run([sys.executable,str(SCRIPT),'--manifest',str(MANIFEST),
                '--policy',str(POLICY),'--diagram',str(out)],capture_output=True,text=True,timeout=8)
            self.assertNotEqual(proc.returncode,0)
            self.assertEqual(out.read_text(),'unchanged')

    def test_25_baseline_contrast_and_loss_are_visible(self):
        doc,_=render(self.policy,self.manifest,self.raw)
        for phrase in ('Supply means','Demand means','simpler baseline','Loses or cannot establish'):
            self.assertIn(phrase,doc)

if __name__ == '__main__':
    unittest.main(verbosity=2)
