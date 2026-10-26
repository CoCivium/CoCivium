import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import finder

class TestCoVisualFinderR1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg=finder.load()
    def clone(self): return copy.deepcopy(self.reg)
    def rejected(self, mutate):
        x=self.clone(); mutate(x)
        with self.assertRaises(ValueError): finder.validate(x)
    def test_01_schema(self): self.assertEqual(self.reg['schema'],'CoCivium.CoVisual.ExternalInspiration.R1')
    def test_02_bounded_sample(self): self.assertEqual(len(finder.validate(self.reg)),4)
    def test_03_no_external_effects(self): self.assertTrue(all(v==0 for v in self.reg['effects'].values()))
    def test_04_no_media_bytes(self): self.assertFalse(self.reg['policy']['media_bytes_permitted'])
    def test_05_no_auto_derivative_license(self): self.assertFalse(self.reg['policy']['license_qualified_for_derivative'])
    def test_06_no_broadcast(self): self.assertIn('NO_SEND',self.reg['policy']['route_mode'])
    def test_07_unique_ids(self): self.assertEqual(len({x['id'] for x in self.reg['public_donors']}),4)
    def test_08_unique_urls(self): self.assertEqual(len({x['source_page'] for x in self.reg['public_donors']}),4)
    def test_09_source_https_only(self): self.assertTrue(all(finder.check_url(x['source_page']) for x in self.reg['public_donors']))
    def test_10_rights_qualified_distinctly(self): self.assertEqual(len({x['rights_state'] for x in self.reg['public_donors']}),4)
    def test_11_no_endorsement(self): self.assertTrue(all(x['noendorsement'] for x in self.reg['public_donors']))
    def test_12_accessible_twins(self): self.assertTrue(all(len(x['accessible_twin'])>=40 for x in self.reg['public_donors']))
    def test_13_inverse_challenges(self): self.assertTrue(all('?' in x['inverse_challenge'] for x in self.reg['public_donors']))
    def test_14_discriminating_tests(self): self.assertTrue(all(x['next_test'] for x in self.reg['public_donors']))
    def test_15_fan_limited(self): self.assertLessEqual(sum(len(x['consumers']) for x in self.reg['public_donors']),12)
    def test_16_projection_proposed_only(self): self.assertEqual(finder.project(self.reg)['actual_receivers'],0)
    def test_17_projection_source_digest(self): self.assertEqual(finder.project(self.reg)['sources_digest'],finder.sha(finder.canon(self.reg).encode()))
    def test_18_projection_4(self): self.assertEqual(len(finder.project(self.reg)['candidates']),4)
    def test_19_deterministic_html(self): self.assertEqual(finder.render(self.reg, finder.project(self.reg)), finder.render(self.reg,finder.project(self.reg)))
    def test_20_original_source_links(self): self.assertEqual(finder.render(self.reg,finder.project(self.reg)).count('Open original source page'),4)
    def test_21_no_external_images(self): self.assertIn("img-src 'none'",finder.render(self.reg,finder.project(self.reg)))
    def test_22_html_escapes_injection(self):
        x=self.clone(); x['public_donors'][0]['title']='<script>unexpected()</script>'
        h=finder.render(x,finder.project(x))
        self.assertNotIn('<script>unexpected()</script>',h);self.assertIn('&lt;script&gt;',h)
    def test_23_deny_unsafe_host(self): self.assertFalse(finder.check_url('https://evil.example.org/'))
    def test_24_deny_embedded_user(self): self.assertFalse(finder.check_url('https://admin:password@commons.wikimedia.org/x'))
    def test_25_deny_http(self): self.assertFalse(finder.check_url('http://commons.wikimedia.org/x'))
    def test_26_deny_js(self): self.assertFalse(finder.check_url('javascript:alert(1)'))
    def test_27_unsupported_schema_fails(self): self.rejected(lambda x:x.update(schema='OTHER'))
    def test_28_mass_candidates_fails(self): self.rejected(lambda x:x['public_donors'].append(dict(x['public_donors'][0],id='extra',source_page='https://www.w3.org/other')))
    def test_29_more_than_3_roles_fails(self): self.rejected(lambda x:x['public_donors'][0]['consumers'].append('CoOrb'))
    def test_30_duplicate_role_fails(self): self.rejected(lambda x:x['public_donors'][0]['consumers'].__setitem__(1,'CoMap'))
    def test_31_unknown_role_fails(self): self.rejected(lambda x:x['public_donors'][0].update(consumers=['CoUnknown']))
    def test_32_send_flag_fails(self): self.rejected(lambda x:x['effects'].update(external_sends=1))
    def test_33_network_flag_fails(self): self.rejected(lambda x:x['effects'].update(network_calls=1))
    def test_34_copy_flag_fails(self): self.rejected(lambda x:x['policy'].update(media_bytes_permitted=True))
    def test_35_license_override_fails(self): self.rejected(lambda x:x['policy'].update(license_qualified_for_derivative=True))
    def test_36_license_unknown_fails(self): self.rejected(lambda x:x['public_donors'][0].update(rights_state='PUBLIC_DOMAIN_APPROVED'))
    def test_37_media_binary_fails(self): self.rejected(lambda x:x['public_donors'][0].update(raw_image='abcdef'))
    def test_38_private_content_fails(self): self.rejected(lambda x:x['public_donors'][0].update(raw_private_data='PRIVATE'))
    def test_39_url_dedupe_fails(self): self.rejected(lambda x:x['public_donors'][1].update(source_page=x['public_donors'][0]['source_page']))
    def test_40_source_rights_url_fails(self): self.rejected(lambda x:x['public_donors'][1].update(rights_evidence_page='https://unauthorized.example.org'))
    def test_41_private_url_fails(self): self.rejected(lambda x:x['public_donors'][1].update(source_page='file:///secret.png'))
    def test_42_invalid_prior_path_fails(self): self.rejected(lambda x:x['existing_donor_families'][0].update(path='../secret'))
    def test_43_unqualified_reuse_fails(self): self.rejected(lambda x:x['public_donors'][0].update(selected_reuse='REPUBLISH_AS_OWN'))
    def test_44_empty_credit_fails(self): self.rejected(lambda x:x['public_donors'][0].update(credit=' '))
    def test_45_embedded_image_not_present(self): self.assertNotIn('<img ',finder.render(self.reg,finder.project(self.reg)))
    def test_46_zero_full_image_downloads(self): self.assertEqual(finder.project(self.reg)['network_calls'],0)
    def test_47_routes_proposals_12(self): self.assertEqual(finder.project(self.reg)['routes_proposed'],12)
    def test_48_no_receiver_ack(self): self.assertIn('SOURCE_PAGE_NE_RECEIVER_ACK',self.reg['nonclaims'])
    def test_49_w3c_not_normative(self): self.assertEqual(self.reg['public_donors'][2]['epistemic_class'],'TECHNICAL_REFERENCE_DRAFT_NOT_NORMATIVE')
    def test_50_license_local_scope(self): self.assertTrue(all(x['selected_reuse']=='MOTIF_ONLY_LINK_BACK_TO_SOURCE' for x in self.reg['public_donors']))

    def test_51_url_query_rejected(self):
        self.assertFalse(finder.check_url('https://commons.wikimedia.org/wiki/File:Example.svg?token=synthetic-private'))
    def test_52_custom_port_rejected(self):
        self.assertFalse(finder.check_url('https://commons.wikimedia.org:8443/wiki/File:Example.svg'))
    def test_53_invalid_port_rejected_without_exception(self):
        self.assertFalse(finder.check_url('https://commons.wikimedia.org:bad/wiki/File:Example.svg'))
    def test_54_non_string_url_rejected(self):
        self.assertFalse(finder.check_url(None))
    def test_55_control_character_rejected(self):
        self.assertFalse(finder.check_url('https://commons.wikimedia.org/wiki/File:Example.svg\n'))
    def test_56_fewer_than_four_sources_rejected(self):
        self.rejected(lambda x:x['public_donors'].pop())
    def test_57_empty_catalogue_rejected(self):
        self.rejected(lambda x:x.update(public_donors=[]))
    def test_58_unknown_root_private_field_rejected(self):
        self.rejected(lambda x:x.update(raw_private_data='synthetic-private-fixture'))
    def test_59_unknown_source_field_rejected(self):
        self.rejected(lambda x:x['public_donors'][0].update(user_clipboard='synthetic-private-fixture'))
    def test_60_unknown_policy_field_rejected(self):
        self.rejected(lambda x:x['policy'].update(autosend=True))
    def test_61_unknown_effect_field_rejected(self):
        self.rejected(lambda x:x['effects'].update(public_broadcast=0))
    def test_62_original_public_reference_links_remain_valid(self):
        self.assertTrue(all(finder.check_url(x['source_page']) and
                            finder.check_url(x['rights_evidence_page']) for x in self.reg['public_donors']))

if __name__=='__main__': unittest.main()
