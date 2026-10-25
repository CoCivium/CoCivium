import copy
import importlib.util
import json
import sys
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('visual_prior_bridge',HERE/'visual_prior_bridge.py')
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
REG=json.loads(bridge.REGISTRY.read_text(encoding='utf-8'))

class TestVisualSourceBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=REG
        cls.source=bridge.assert_registry(REG)
        cls.proj=bridge.projection(REG)
        cls.template=bridge.TEMPLATE.read_text(encoding='utf-8')
        cls.html=bridge.render(cls.proj,cls.source,cls.template)

    def mutate_bad(self,method):
        obj=copy.deepcopy(self.registry)
        method(obj)
        with self.assertRaises(ValueError): bridge.assert_registry(obj)

    def test_01_registry_schema(self): self.assertEqual(self.registry['schema'],'CoCivium.CoVisual.ExternalInspiration.R1')
    def test_02_one_source_selected(self): self.assertEqual(self.source['id'],bridge.TARGET_ID)
    def test_03_source_url(self): self.assertTrue(self.source['source_page'].startswith('https://commons.wikimedia.org/'))
    def test_04_typed_output_schema(self): self.assertEqual(self.proj['schema'],bridge.SCHEMA)
    def test_05_one_work_id(self): self.assertEqual(self.proj['work_id'],'coal.covisual.commons-source-graph.r1')
    def test_06_three_views(self): self.assertEqual(self.proj['views'],['Map','Orb','Text'])
    def test_07_four_lenses(self): self.assertEqual(self.proj['lenses'],['All','Story','Science','Systems'])
    def test_08_authority(self): self.assertEqual(self.proj['authority'],'NONE')
    def test_09_no_image_sha_claim(self): self.assertIsNone(self.proj['source_provenance']['image_sha256'])
    def test_10_no_verified_image_bytes(self): self.assertFalse(self.proj['source_provenance']['image_bytes_verified'])
    def test_11_no_private_content(self): self.assertFalse(self.proj['source_provenance']['private_material_included'])
    def test_12_source_page_preserved(self): self.assertEqual(self.proj['source_provenance']['source_page'],self.source['source_page'])
    def test_13_source_metadata_digest(self): self.assertEqual(self.proj['source_provenance']['source_record_sha256'],bridge.sha(bridge.canonical(self.source).encode('utf-8')))
    def test_14_credit_preserved(self): self.assertEqual(self.proj['source_provenance']['credit'],self.source['credit'])
    def test_15_rights_status_not_promoted(self): self.assertEqual(self.proj['source_provenance']['rights_status'],bridge.RIGHTS)
    def test_16_no_media_derivative_authority(self): self.assertEqual(self.proj['source_provenance']['image_derivative_permission'],'NOT_GRANTED_BY_THIS_ADAPTER')
    def test_17_no_network_effects(self): self.assertFalse(self.proj['privacy']['external_network'])
    def test_18_no_automatic_public_media(self): self.assertFalse(self.proj['evolution']['auto_public_media'])
    def test_19_no_device_io(self): self.assertFalse(self.proj['evolution']['auto_enable_device_io'])
    def test_20_no_auto_rewrite(self): self.assertFalse(self.proj['evolution']['auto_rewrite'])
    def test_21_no_duplicate_nodes(self): self.assertEqual(len(self.proj['nodes']),len({n['id'] for n in self.proj['nodes']}))
    def test_22_relation_endpoints_exist(self):
        ids={n['id'] for n in self.proj['nodes']}
        self.assertTrue(all(r['from'] in ids and r['to'] in ids for r in self.proj['relations']))
    def test_23_no_claimed_reciprocal_edge(self): self.assertFalse(any(r['type'] in {'CAUSES','PROVES','IS_RECIPROCAL_TO','SENDS'} for r in self.proj['relations']))
    def test_24_inverse_is_question(self): self.assertIn('?',next(n for n in self.proj['nodes'] if n['id']=='inverse')['summary'])
    def test_25_unknown_remains_unknown(self): self.assertEqual(next(n for n in self.proj['nodes'] if n['id']=='unknown')['kind'],'UNKNOWN_NOT_FALSE_AND_NOT_TRUE')
    def test_26_source_identity_across_views(self): self.assertEqual(len(self.proj['nodes']),9)
    def test_27_no_real_receiver_ack(self): self.assertFalse(self.proj['bridge']['receiver_ack'])
    def test_28_projection_loss_recorded(self): self.assertEqual(len(self.proj['bridge']['projection_loss']),3)
    def test_29_exact_build_replay(self): self.assertEqual(bridge.build()[1:],bridge.build()[1:])
    def test_30_generated_json_is_exact(self): self.assertEqual(bridge.MANIFEST_OUT.read_bytes(),bridge.build()[1])
    def test_31_generated_html_is_exact(self): self.assertEqual(bridge.HTML_OUT.read_bytes(),bridge.build()[2])
    def test_32_html_no_unsafe_external_images(self): self.assertIn("img-src data:;",self.html)
    def test_33_html_no_script_network(self): self.assertIn("connect-src 'none'",self.html)
    def test_34_html_source_link(self): self.assertIn(self.source['source_page'],self.html)
    def test_35_html_not_synthkind_declaration(self): self.assertNotIn('Synthkind',self.html)
    def test_36_html_projection_controls(self): self.assertEqual(self.html.count('data-view='),3)
    def test_37_html_six_beats(self): self.assertEqual(len(self.proj['storyboard']),6)
    def test_38_html_escapes_risky_text(self):
        obj=copy.deepcopy(self.proj);obj['nodes'][0]['label']='</script><script>attack()</script>'
        out=bridge.render(obj,self.source,self.template)
        self.assertNotIn('</script><script>attack()',out)
        self.assertIn('\\u003c/script\\u003e',out)
    def test_39_source_unchanged_by_build(self):
        before=bridge.REGISTRY.read_bytes();bridge.build();self.assertEqual(before,bridge.REGISTRY.read_bytes())
    def test_40_reject_schema_drift(self): self.mutate_bad(lambda x:x.update(schema='UNKNOWN'))
    def test_41_reject_media_copy(self): self.mutate_bad(lambda x:x['policy'].update(media_bytes_permitted=True))
    def test_42_reject_derivative_clearance(self): self.mutate_bad(lambda x:x['policy'].update(license_qualified_for_derivative=True))
    def test_43_reject_send(self): self.mutate_bad(lambda x:x['effects'].update(external_sends=1))
    def test_44_reject_other_route(self): self.mutate_bad(lambda x:x['policy'].update(route_mode='PUBLIC_SPRAY'))
    def test_45_reject_rename(self): self.mutate_bad(lambda x:x['public_donors'][0].update(id='UNKNOWN'))
    def test_46_reject_missing_credit(self): self.mutate_bad(lambda x:x['public_donors'][0].update(credit=''))
    def test_47_reject_wrong_rights(self): self.mutate_bad(lambda x:x['public_donors'][0].update(rights_state='PUBLIC_DOMAIN'))
    def test_48_reject_noendorsement_false(self): self.mutate_bad(lambda x:x['public_donors'][0].update(noendorsement=False))
    def test_49_reject_image_copy_reuse(self): self.mutate_bad(lambda x:x['public_donors'][0].update(selected_reuse='COPY_IMAGE_BYTES'))
    def test_50_reject_new_consumers(self): self.mutate_bad(lambda x:x['public_donors'][0].update(consumers=['CoMap','PRIVATE_MESSAGE_SEND']))
    def test_51_reject_non_question_inverse(self): self.mutate_bad(lambda x:x['public_donors'][0].update(inverse_challenge='verified inverse'))
    def test_52_reject_non_https(self): self.mutate_bad(lambda x:x['public_donors'][0].update(source_page='http://commons.wikimedia.org/x'))
    def test_53_reject_fake_host(self): self.mutate_bad(lambda x:x['public_donors'][0].update(source_page='https://commons.wikimedia.org.evil.tld/a'))
    def test_54_reject_credential_url(self): self.mutate_bad(lambda x:x['public_donors'][0].update(source_page='https://user:pass@commons.wikimedia.org/x'))
    def test_55_reject_mismatched_rights_url(self): self.mutate_bad(lambda x:x['public_donors'][0].update(rights_evidence_page='https://commons.wikimedia.org/wiki/Other'))
    def test_56_reject_duplicated_identity(self): self.mutate_bad(lambda x:x['public_donors'].append(copy.deepcopy(x['public_donors'][0])))
    def test_57_reject_more_than_4_sources(self): self.mutate_bad(lambda x:x['public_donors'].extend([copy.deepcopy(x['public_donors'][0]) for _ in range(5)]))
    def test_58_reject_template_label_drift(self):
        with self.assertRaises(ValueError): bridge.render(self.proj,self.source,self.template.replace('One relationship, many honest lenses','changed'))
    def test_59_accessible_description(self): self.assertIn(self.source['accessible_twin'],next(n for n in self.proj['nodes'] if n['id']=='text')['summary'])
    def test_60_no_external_image_embed(self): self.assertNotIn('<img ',self.html)
    def test_61_neutral_source_status_field(self):
        self.assertEqual(self.proj['source_provenance']['source_status'],'EXTERNAL_SOURCE_PAGE_METADATA_ONLY__NO_IMAGE_BYTES')
        self.assertNotIn('primary_declaration_text',self.proj['source_provenance'])
        self.assertIn('data.source_provenance.source_status',self.html)


if __name__=='__main__': unittest.main()
