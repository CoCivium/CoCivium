#!/usr/bin/env python3
"""Source-bound static federation and negative-case controls."""
from pathlib import Path
import hashlib
import json
import re
import unittest
from copy import deepcopy
from html.parser import HTMLParser
from build import load_manifest, validate, build, decode_index

ROOT=Path(__file__).resolve().parent

class Tags(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.external=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='script' and 'src' in a:self.external.append(a['src'])
        if tag=='link' and 'href' in a:self.external.append(a['href'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])

class FederationTests(unittest.TestCase):
    def setUp(self):self.m=load_manifest()
    def test_schema(self):self.assertEqual(self.m['schema'],'CoAll.CoPublicationFederation.FirstProof.R0')
    def test_validate(self):self.assertTrue(validate(self.m))
    def test_exclusive_six_routes(self):self.assertEqual(len(self.m['routes']),6)
    def test_source_pin(self):self.assertEqual(self.m['source']['git_blob_sha1'],'9202ab5a8d0bfef509922c8c047363ea7a346ce2')
    def test_all_six_claims(self):self.assertEqual([x['id'] for x in self.m['claims']],['C01','C02','C03','C04','C05','C06'])
    def test_no_fact_drift(self):
        kernel=self.m['claim_ids_required_in_every_route']
        for r in self.m['routes']:self.assertEqual(r['claims'],kernel)
    def test_sources_public(self):
        self.assertTrue(all(x['action_url'].startswith('https://github.com/CoCivium/CoCivium/') for x in self.m['routes']))
    def test_qualify_proposals(self):self.assertIn('NOT_RUNTIME',self.m['source']['status'])
    def test_no_runtime_claim(self):self.assertIn('NOT_SUBSTACK_POSTED',self.m['status'])
    def test_no_published_posts(self):self.assertEqual(self.m['actual_substack_posts_created'],0)
    def test_no_external_sends(self):self.assertEqual(self.m['external_sends'],0)
    def test_no_tracking(self):self.assertIs(self.m['tracking'],False)
    def test_no_inferred_interests(self):self.assertIs(self.m['interest_inference'],False)
    def test_no_read_implies_send(self):self.assertEqual(self.m['reader_feedback_writeback'],'NONE_LOCAL_PREVIEW_ONLY')
    def test_no_fake_deadline(self):self.assertEqual(self.m['urgency']['mode'],'NONE_NO_REAL_DEADLINE_VERIFIED')
    def test_no_countdown(self):self.assertIs(self.m['urgency']['countdowns'],False)
    def test_no_deliberate_link_rot(self):self.assertIs(self.m['urgency']['deliberately_expiring_links'],False)
    def test_history_chain(self):self.assertEqual(self.m['edition_history'][1]['predecessor'],'r0.1')
    def test_history_nonpublic(self):self.assertTrue(all(v['kind'].startswith('LOCAL_SYNTHETIC') for v in self.m['edition_history']))
    def test_current_declared(self):self.assertEqual(self.m['current_edition'],'r0.2')
    def test_12_axes(self):self.assertEqual(len(self.m['logical_axes']),12)
    def test_10_options_each(self):self.assertTrue(all(len(set(x))==10 for x in self.m['logical_axes'].values()))
    def test_trillion_addresses(self):self.assertEqual(int(self.m['logical_candidate_space']),10**12)
    def test_zero_index(self):
        got=decode_index(0,self.m['logical_axes'])
        self.assertEqual(list(got.values()),[v[0] for v in self.m['logical_axes'].values()])
    def test_upper_index(self):
        got=decode_index(10**12-1,self.m['logical_axes'])
        self.assertEqual(list(got.values()),[v[-1] for v in self.m['logical_axes'].values()])
    def test_random_lazy_index(self):
        got=decode_index(314159265358,self.m['logical_axes'])
        self.assertEqual(len(got),12)
        self.assertTrue(all(v in self.m['logical_axes'][k] for k,v in got.items()))
    def test_negative_index_rejected(self):
        with self.assertRaises(ValueError):decode_index(-1,self.m['logical_axes'])
    def test_too_large_index_rejected(self):
        with self.assertRaises(ValueError):decode_index(10**12,self.m['logical_axes'])
    def test_float_index_rejected(self):
        with self.assertRaises(ValueError):decode_index(7.0,self.m['logical_axes'])
    def test_mutated_claim_is_held(self):
        b=deepcopy(self.m);b['routes'][0]['claims'].pop()
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_deadline_is_held(self):
        b=deepcopy(self.m);b['urgency']['countdowns']=True
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_tracking_is_held(self):
        b=deepcopy(self.m);b['tracking']=True
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_link_is_held(self):
        b=deepcopy(self.m);b['routes'][0]['action_url']='https://evil.invalid/login'
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_history_is_held(self):
        b=deepcopy(self.m);b['edition_history'][1]['predecessor']=None
        with self.assertRaises(AssertionError):validate(b)
    def test_mutated_source_state_is_held(self):
        b=deepcopy(self.m);b['source']['status']='VERIFIED_UNIVERSAL_DEPLOYMENT'
        with self.assertRaises(AssertionError):validate(b)
    def test_expected_html_exists(self):self.assertTrue((ROOT/'index.html').exists())
    def test_exact_generated_parity(self):self.assertEqual((ROOT/'index.html').read_text(),build(self.m))
    def test_no_script_injection(self):
        b=deepcopy(self.m);b['routes'][0]['entry']='</script><img onerror="bad()">'
        html=build(b)
        self.assertNotIn('</script><img',html)
        self.assertIn('\\u003c/script\\u003e',html)
    def test_csp_blocks_network(self):self.assertIn("connect-src 'none'",(ROOT/'index.html').read_text())
    def test_no_external_scripts_or_styles(self):
        p=Tags();p.feed((ROOT/'index.html').read_text())
        self.assertEqual(p.external,[])
    def test_all_html_ids_unique(self):
        p=Tags();p.feed((ROOT/'index.html').read_text())
        self.assertEqual(len(p.ids),len(set(p.ids)))
    def test_external_links_allowlisted(self):
        p=Tags();p.feed((ROOT/'index.html').read_text())
        self.assertTrue(all((link == 'https://github.com/CoCivium/CoCivium' or link.startswith('https://github.com/CoCivium/CoCivium/') or link.startswith('#') or link == 'https://rickpublic.substack.com/p/does-ai-make-the-stock-market-obsolete') for link in p.links))
    def test_reader_bridge_discoverable_from_first_screen(self):
        html=(ROOT/'index.html').read_text()
        self.assertEqual(html.count('href="#edge-in-heading"'),1)
        self.assertIn('Compare a published article with the draft chapter',html)
    def test_one_verified_rickpublic_published_link(self):
        html=(ROOT/'index.html').read_text()
        self.assertEqual(html.count('href="https://rickpublic.substack.com/p/does-ai-make-the-stock-market-obsolete"'),1)
        self.assertIn('Read the existing public article',html)
        self.assertIn('Its forecasts are hypotheses',html)
    def test_draft_chapter_pinned_and_explicitly_unpublished(self):
        html=(ROOT/'index.html').read_text()
        self.assertEqual(html.count('https://github.com/CoCivium/CoCivium/blob/1487b330d35ddec03f32000e6846dd3b35ed774a/docs/books/great-refact-r0/01-your-product-is-still-here.md'),1)
        self.assertIn('source-controlled, unmerged working draft, not a published Substack article',html)
        self.assertIn('21bb508b5b0fe9e34011590539993e14d4325edc',html)
    def test_reader_bridge_no_automatic_send_and_clear_exit(self):
        html=(ROOT/'index.html').read_text()
        self.assertIn('id="edge-in-heading"',html)
        self.assertIn('or simply leave',html)
        self.assertIn('No reading behavior or responses are transmitted by this page.',html)
        self.assertIn("connect-src 'none'",html)
    def test_single_html_manifest(self):self.assertEqual((ROOT/'index.html').read_text().count('id="manifest"'),1)
    def test_keyboard_access(self):self.assertIn('focus-visible',(ROOT/'index.html').read_text())
    def test_reduced_motion(self):self.assertIn('prefers-reduced-motion',(ROOT/'index.html').read_text())
    def test_mobile_breakpoints(self):self.assertIn('@media(max-width:760px)',(ROOT/'index.html').read_text())
    def test_no_raw_private_media(self):self.assertNotIn('WhatsApp',(ROOT/'index.html').read_text())
    def test_title_and_source(self):self.assertIn('The Great ReFact | Six reader doorways',(ROOT/'index.html').read_text())
    def test_no_fake_viral_guarantee(self):self.assertIn('No artificial timers',(ROOT/'index.html').read_text())
    def test_action_not_automatic(self):self.assertIn('UNSENT_LOCAL_PROPOSAL',(ROOT/'index.html').read_text())
    def test_conditional_false_metrics(self):self.assertFalse(any('300% more leads' in r['entry'] for r in self.m['routes']))
    def test_claim_kernel_not_medium_specific(self):self.assertTrue(all('claims' in r for r in self.m['routes']))
    def test_manifest_is_ascii_transportable(self):self.assertTrue((ROOT/'manifest.json').read_text().isascii())
    def test_static_source_is_not_substack_domain(self):self.assertNotIn('substack.com/p/',self.m['source']['url'])
    def test_local_only_copy_preview(self):self.assertIn('No feedback prepared or sent.',(ROOT/'index.html').read_text())
    def test_all_actions_named(self):self.assertTrue(all(r['task'] and r['action_label'] for r in self.m['routes']))
    def test_no_brittle_snapshot(self):self.assertGreater(len(self.m['edition_history']),1)
    def test_risk_counterpoint_present(self):self.assertTrue(all(len(r['counterpoint'])>30 for r in self.m['routes']))
    def test_status_unknown_not_erased(self):self.assertTrue(any('time saved' in c['text'] for c in self.m['claims']))

if __name__=='__main__':unittest.main(verbosity=2)
