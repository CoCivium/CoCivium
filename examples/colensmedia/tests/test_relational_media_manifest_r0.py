"""Cross-media CoSourceGraph fixture controls, no external effects."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / 'relational_media_manifest_r0.py'
FIXTURE = SRC.parent / 'relational_media_fixture_r0.json'
DIAGRAM = SRC.parent / 'relational_media_diagram_r0.md'
spec = importlib.util.spec_from_file_location('media_graph', SRC)
media = importlib.util.module_from_spec(spec)
spec.loader.exec_module(media)


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(FIXTURE.read_text())

    def test_01_clean_full_multimedia_braid(self):
        report = media.audit(self.base)
        self.assertEqual(report['state'], 'SOURCE_GRAPH_CANDIDATE_CLEAN')
        self.assertEqual(report['asset_count'], 7)
        self.assertEqual(report['relation_count'], 10)
        self.assertEqual(report['orphan_asset_ids'], [])
        self.assertIn('METADATA_RELATION_NE_RECEIVER_ACK', report['nonclaims'])

    def test_02_same_fixture_mermaid_and_accessible_text(self):
        text = media.render_markdown(self.base)
        self.assertEqual(text, DIAGRAM.read_text())
        self.assertIn('```mermaid', text)
        self.assertIn('## Accessible text equivalent', text)
        self.assertNotIn('EMAIL_DRAFT', text)

    def test_03_graph_repeatable(self):
        self.assertEqual(media.audit(self.base), media.audit(self.base))
        self.assertEqual(media.render_markdown(self.base), media.render_markdown(self.base))

    def test_04_modified_source_marks_dependent_diagram_stale(self):
        self.base['assets'][0]['source_revision'] = 'src-v2'
        report = media.audit(self.base)
        self.assertEqual(report['state'], 'SOURCE_GRAPH_REVIEW_REQUIRED')
        self.assertIn('diagram:v1', report['stale_current_asset_ids'])
        self.assertIn('draft:v1', report['stale_current_asset_ids'])

    def test_05_missing_derivation_is_orphan(self):
        self.base['relations'] = [x for x in self.base['relations']
                                   if not (x['from'] == 'orb:v1' and x['type'] == 'DERIVED_FROM')]
        report=media.audit(self.base)
        self.assertIn('orb:v1',report['orphan_asset_ids'])

    def test_06_explicitly_disconnected_not_forced_into_graph(self):
        self.base['relations'] = [x for x in self.base['relations']
                                   if not (x['from'] == 'orb:v1' and x['type'] == 'DERIVED_FROM')]
        self.base['assets'][-1]['isolation_reason'] = 'Consent scope prohibits automatic interlink'
        report=media.audit(self.base)
        self.assertEqual(report['orphan_asset_ids'], [])
        self.assertIn('orb:v1',report['intentionally_isolated_asset_ids'])

    def test_07_intentionally_unrelated_edge_is_not_proven_parent(self):
        self.base['relations'] = [x for x in self.base['relations']
                                   if not (x['from'] == 'orb:v1' and x['type'] == 'DERIVED_FROM')]
        self.base['relations'].append({'from':'orb:v1','to':'work:media-r0',
                                       'type':'INTENTIONALLY_UNRELATED', 'evidence_ref':'fixture:no-link'})
        self.assertIn('orb:v1',media.audit(self.base)['orphan_asset_ids'])

    def test_08_derivation_cycle_rejected(self):
        self.base['relations'].append({'from':'work:media-r0','to':'diagram:v1',
                                       'type':'DERIVED_FROM', 'evidence_ref':'fixture:bad-cycle'})
        # Root cannot have a parent; this is a lineage cycle in the overall graph.
        with self.assertRaises(ValueError):
            media.audit(self.base)

    def test_09_hidden_cycle_with_valid_root_path_rejected(self):
        # Diagram already reaches root; a second parent leading back must not be skipped.
        self.base['relations'].append({'from':'diagram:v1','to':'alt:diagram',
                                       'type':'DERIVED_FROM', 'evidence_ref':'fixture:cycle'})
        self.base['relations'].append({'from':'alt:diagram','to':'diagram:v1',
                                       'type':'DERIVED_FROM', 'evidence_ref':'fixture:cycle'})
        with self.assertRaisesRegex(ValueError,'DERIVATION_CYCLE'):
            media.audit(self.base)

    def test_10_public_asset_cannot_derive_from_private_email(self):
        self.base['relations'].append({'from':'orb:v1','to':'draft:v1',
                                       'type':'DERIVED_FROM', 'evidence_ref':'fixture:inference-risk'})
        with self.assertRaisesRegex(ValueError,'PUBLIC_DERIVED_FROM_PRIVATE'):
            media.audit(self.base)

    def test_11_missing_accessible_twin_flagged(self):
        self.base['assets'][1].pop('accessibility_twin_id')
        self.assertIn('diagram:v1',media.audit(self.base)['accessibility_gap_asset_ids'])

    def test_12_stale_accessible_twin_flagged(self):
        self.base['assets'][2]['source_revision'] = 'older'
        self.assertIn('diagram:v1',media.audit(self.base)['accessibility_gap_asset_ids'])

    def test_13_invalid_relation_type_denied(self):
        self.base['relations'][0]['type'] = 'AUTO_SEND'
        with self.assertRaisesRegex(ValueError,'INVALID_RELATION_TYPE'):
            media.audit(self.base)

    def test_14_relations_require_evidence(self):
        self.base['relations'][0]['evidence_ref'] = ''
        with self.assertRaisesRegex(ValueError,'MISSING_RELATION_EVIDENCE'):
            media.audit(self.base)

    def test_15_missing_relation_endpoint_denied(self):
        self.base['relations'][0]['to'] = 'unknown'
        with self.assertRaisesRegex(ValueError,'MISSING_RELATION_ENDPOINT'):
            media.audit(self.base)

    def test_16_duplicate_asset_denied(self):
        self.base['assets'].append(copy.deepcopy(self.base['assets'][1]))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_ASSET_ID'):
            media.audit(self.base)

    def test_17_duplicate_relation_denied(self):
        self.base['relations'].append(copy.deepcopy(self.base['relations'][0]))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_RELATION'):
            media.audit(self.base)

    def test_18_workid_mismatch_denied(self):
        self.base['assets'][1]['work_id'] = 'another-work'
        with self.assertRaisesRegex(ValueError,'MIXED_WORK_IDS'):
            media.audit(self.base)

    def test_19_invalid_hash_denied(self):
        self.base['assets'][1]['sha256'] = 'not-a-hash'
        with self.assertRaisesRegex(ValueError,'INVALID_ASSET_HASH'):
            media.audit(self.base)

    def test_20_html_script_label_denied(self):
        self.base['assets'][1]['label'] = '<script>alert(1)</script>'
        with self.assertRaisesRegex(ValueError,'UNSAFE_DISPLAY_LABEL'):
            media.audit(self.base)

    def test_21_unbound_revision_only_as_archived_version(self):
        self.base['assets'][1]['current'] = False
        self.base['assets'][1]['source_revision'] = 'src-v0'
        self.assertNotIn('diagram:v1',media.audit(self.base)['stale_current_asset_ids'])

    def test_22_rendered_diagram_check_fails_after_upstream_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            fixture=tmp/'fixture.json'
            fixture.write_text(json.dumps(self.base))
            diagram=tmp/'view.md'
            diagram.write_text(media.render_markdown(self.base))
            self.base['assets'][0]['source_revision']='src-v2'
            fixture.write_text(json.dumps(self.base))
            result=subprocess.run([sys.executable,str(SRC),'--fixture',str(fixture),
                                   '--diagram',str(diagram),'--check'],
                                  capture_output=True,text=True,timeout=5)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('HOLD_DIAGRAM_OUT_OF_SYNC',result.stderr)

    def test_23_renderer_does_not_overwrite_existing_diagram(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); fixture=tmp/'fixture.json'; out=tmp/'view.md'
            fixture.write_text(json.dumps(self.base));out.write_text('user edited')
            result=subprocess.run([sys.executable,str(SRC),'--fixture',str(fixture),
                                   '--diagram',str(out)],capture_output=True,text=True,timeout=5)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(out.read_text(),'user edited')

    def test_24_private_draft_may_derive_from_public_source(self):
        self.assertEqual(media.audit(self.base)['state'],'SOURCE_GRAPH_CANDIDATE_CLEAN')

    def test_25_public_render_hides_private_draft_nodes(self):
        doc = media.render_markdown(self.base)
        self.assertNotIn('draft:v1', doc)
        self.assertNotIn('CoMail staged draft', doc)
        self.assertNotIn('EMAIL_DRAFT', doc)

    def test_26_private_only_change_does_not_change_public_view(self):
        baseline = media.render_markdown(self.base)
        self.base['assets'][5]['sha256'] = media.sha(b'new private edit')
        self.base['assets'][5]['source_revision'] = 'private-revision'
        self.assertEqual(media.render_markdown(self.base), baseline)

    def test_27_public_change_moves_public_projection_digest(self):
        baseline = media.render_markdown(self.base)
        self.base['assets'][1]['sha256'] = media.sha(b'new public diagram')
        self.assertNotEqual(media.render_markdown(self.base), baseline)



if __name__=='__main__':
    unittest.main(verbosity=2)
