import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('colens_build',HERE/'build.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class LivingMediaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=module.load()
        cls.html=(HERE/'index.html').read_text(encoding='utf-8')
        cls.template=(HERE/'template.html').read_text(encoding='utf-8')

    def test_schema(self):self.assertEqual(self.data['schema'],'CoAll.CoLens.LivingMediaTwin.R0')
    def test_no_public_authority(self):self.assertEqual(self.data['authority'],'NONE')
    def test_no_authoritative_declaration(self):self.assertEqual(self.data['source_provenance']['primary_declaration_text'],'NOT_LOCATED_IN_BOUNDED_SEARCH')
    def test_no_video_claim(self):self.assertEqual(self.data['source_provenance']['primary_media'],'NOT_LOCATED_IN_BOUNDED_SEARCH')
    def test_private_material_excluded(self):self.assertFalse(self.data['source_provenance']['private_material_included'])
    def test_no_legal_governance_claim(self):self.assertEqual(self.data['source_provenance']['legal_governance_status'],'NONE')
    def test_three_views(self):self.assertEqual(self.data['views'],['Map','Orb','Text'])
    def test_four_lenses(self):self.assertEqual(self.data['lenses'],['All','Story','Science','Systems'])
    def test_no_duplicate_nodes(self):
        ids=[x['id'] for x in self.data['nodes']]
        self.assertEqual(len(ids),len(set(ids)))
    def test_nonempty_node_semantics(self):
        for node in self.data['nodes']:
            for key in ['id','label','kind','lens','summary']:
                self.assertIsInstance(node[key],str)
                self.assertTrue(node[key].strip())
    def test_lens_coverage(self):
        for node in self.data['nodes']:self.assertIn(node['lens'],self.data['lenses'][1:])
    def test_relations_have_existing_ends(self):
        ids={x['id'] for x in self.data['nodes']}
        for e in self.data['relations']:
            self.assertIn(e['from'],ids);self.assertIn(e['to'],ids)
    def test_relations_not_promoted(self):
        self.assertTrue(self.data['relations'])
        self.assertTrue(all(e['status'] in {'PROPOSED','CONCEPTUAL_ONLY'} for e in self.data['relations']))
    def test_no_unqualified_physical_causation(self):
        banned={'CAUSES','PROVES','MEASURES','DEMONSTRATES_PHYSICAL_FIELD'}
        self.assertFalse(any(x['type'] in banned for x in self.data['relations']))
    def test_quantum_is_theory_not_metaphysical_proof(self):
        n=next(x for x in self.data['nodes'] if x['id']=='quantum')
        self.assertEqual(n['kind'],'ESTABLISHED_THEORY_WITH_OPEN_INTERPRETATIONS')
    def test_planck_not_claiming_measurement(self):
        n=next(x for x in self.data['nodes'] if x['id']=='planck')
        self.assertIn('no measurement',n['summary'])
    def test_gd_not_assumed_physics(self):
        n=next(x for x in self.data['nodes'] if x['id']=='gd')
        self.assertEqual(n['kind'],'UNDEFINED_SYMBOL_OR_SPECULATIVE_HYPOTHESIS')
    def test_aura_not_assumed_field(self):
        n=next(x for x in self.data['nodes'] if x['id']=='aura')
        self.assertEqual(n['kind'],'EXPERIENTIAL_OR_DESIGN_METAPHOR')
    def test_storyboard_all_references_grounded(self):
        ids={x['id'] for x in self.data['nodes']}
        for frame in self.data['storyboard']:
            self.assertTrue(frame['caption']);self.assertTrue(frame['node_ids'])
            self.assertTrue(set(frame['node_ids']).issubset(ids))
    def test_six_proposed_frames_not_video(self):self.assertEqual(len(self.data['storyboard']),6)
    def test_no_auto_evolution_writes(self):
        p=self.data['evolution']
        self.assertFalse(p['auto_rewrite']);self.assertFalse(p['auto_public_media']);self.assertFalse(p['auto_enable_device_io'])
    def test_explicit_change_triggers(self):self.assertIn('SOURCE_SEMANTIC_CHANGE',self.data['evolution']['new_version_trigger'])
    def test_changes_do_not_follow_clock_alone(self):self.assertEqual(self.data['evolution']['no_change'],'SLEEP_WITH_CURRENTNESS_RECEIPT')
    def test_private_network_telemetry_denied(self):
        p=self.data['privacy'];self.assertFalse(p['external_network']);self.assertFalse(p['tracking']);self.assertFalse(p['clipboard_read'])
    def test_required_nonclaims(self):
        for v in ['THEME_NE_ACTUAL_DECLARATION','QUANTUM_METAPHOR_NE_QUANTUM_EVIDENCE','DOCUMENT_NE_COCIVIUM_WIDE_DEPLOYMENT','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF']:
            self.assertIn(v,self.data['nonclaims'])
    def test_four_pinned_public_donors(self):
        items=self.data['public_donors'];self.assertEqual(len(items),4)
        self.assertEqual(len({x['path'] for x in items}),4)
        for x in items:self.assertRegex(x['git_blob'],r'^[a-f0-9]{40}$')
    def test_exact_generated_html(self):self.assertEqual(module.build(),self.html)
    def test_embed_same_json_across_views(self):
        import re
        m=re.search(r'<script type="application/json" id="manifest">(.*?)</script>',self.html,re.S)
        self.assertIsNotNone(m)
        self.assertEqual(json.loads(m.group(1)),self.data)
    def test_offline_content_security_policy(self):
        self.assertIn("connect-src 'none'",self.html)
        self.assertIn("default-src 'none'",self.html)
    def test_no_network_or_sensitive_api_in_template(self):
        for marker in ['fetch(', 'XMLHttpRequest', 'WebSocket(', 'sendBeacon(', 'localStorage', 'navigator.clipboard', 'getUserMedia(']:self.assertNotIn(marker,self.template)
    def test_keyboard_svg_selection(self):self.assertIn("ev.key==='Enter'||ev.key===' '",self.html)
    def test_live_status_and_reduced_motion(self):
        self.assertIn('aria-live="polite"',self.html)
        self.assertIn('prefers-reduced-motion:reduce',self.html)
    def test_source_donor_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            found=module.donor_verification(Path(tmp))
            self.assertTrue(all(s=='MISSING_FILE' for _,s in found))
    def test_donor_drift_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for source in self.data['public_donors']:
                p=root/source['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'changed public source')
            found=module.donor_verification(root)
            self.assertTrue(all(s=='DRIFT' for _,s in found))
    def test_graph_filter_is_view_not_source_mutation(self):
        snapshot=copy.deepcopy(self.data)
        for lens in self.data['lenses']:
            nodes=[n for n in self.data['nodes'] if lens=='All' or n['id']=='theme' or n['lens']==lens]
            self.assertGreaterEqual(len(nodes),1)
        self.assertEqual(self.data,snapshot)

if __name__=='__main__':unittest.main()
