#!/usr/bin/env python3
"""Static, no-network contract checks for the offline CoMap/CoOrb canary."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest

class FixtureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capturing = False
        self.payload = []
    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('id') == 'fixture':
            self.capturing = True
    def handle_endtag(self, tag):
        if tag == 'script' and self.capturing:
            self.capturing = False
    def handle_data(self, data):
        if self.capturing:
            self.payload.append(data)

source = (Path(__file__).parent / 'index.html').read_text(encoding='utf-8')
p = FixtureParser()
p.feed(source)
fixture = json.loads(''.join(p.payload))

class Tests(unittest.TestCase):
    def test_candidate_schema(self):
        self.assertEqual(fixture['schema'], 'CoAll.CoMapOrbProjection.v0.1-candidate')
        self.assertTrue(fixture['synthetic_fixture'])
    def test_zero_effect_authority(self):
        self.assertEqual(fixture['effect_authority'], 'NONE')
    def test_node_identity_unique(self):
        ids=[n['id'] for n in fixture['nodes']]
        self.assertEqual(len(ids),len(set(ids)))
    def test_edge_identity_unique(self):
        ids=[e['id'] for e in fixture['edges']]
        self.assertEqual(len(ids),len(set(ids)))
    def test_all_endpoints_known(self):
        nodes={n['id'] for n in fixture['nodes']}
        for e in fixture['edges']:
            self.assertIn(e['from'], nodes)
            self.assertIn(e['to'], nodes)
    def test_sources_grounded(self):
        for e in fixture['edges']:
            self.assertIn(e['source'],fixture['source_refs'])
            self.assertTrue(fixture['source_refs'][e['source']].startswith('https://github.com/CoCivium/'))
    def test_all_relations_privacy_typed(self):
        for e in fixture['edges']:
            self.assertIn(e['privacy'], ['PUBLIC','PRIVATE','RESTRICTED','UNKNOWN'])
    def test_private_regression_fixture(self):
        private=[e for e in fixture['edges'] if e['privacy']!='PUBLIC']
        self.assertEqual(len(private),1)
        self.assertEqual(private[0]['id'],'E10')
        self.assertIn('e.privacy!=="PUBLIC"',source)
    def test_predictions_temporally_separated(self):
        for e in fixture['edges']:
            if e['kind']=='predicted':
                self.assertEqual(e['period'],2)
        self.assertIn('if(!speculative&&e.kind==="predicted")return false',source)
    def test_no_ambiguous_truth_types(self):
        self.assertEqual({e['kind'] for e in fixture['edges']}, {'documented','proposed','predicted'})
    def test_default_glance_is_bounded(self):
        glance=[e for e in fixture['edges'] if e['privacy']=='PUBLIC' and e['period']<=1 and e['id'] in ['E01','E02','E03','E04','E07']]
        self.assertEqual(len(glance),5)
    def test_no_auto_network(self):
        self.assertNotRegex(source, r'\bfetch\s*\(|\bXMLHttpRequest\b|new\s+WebSocket\s*\(')
        self.assertNotRegex(source, r'<script[^>]+src=')
    def test_accessibility(self):
        for required in ['aria-live="polite"','aria-pressed="true"','aria-label="CoTime lens','role="group"',"e.key===\"Enter\"", "e.key===\" \""]:
            self.assertIn(required,source)
    def test_motion_off(self):
        self.assertIn('@media(prefers-reduced-motion:reduce)',source)
        self.assertNotIn('requestAnimationFrame',source)
    def test_predictive_beyond_caret_not_overwriting(self):
        self.assertIn('slice(0,input.selectionStart',source)
        self.assertIn('startsWith(lookup)',source)
        self.assertIn('e.privacy==="PUBLIC"',source)
        self.assertIn('LOOKAHEAD / NOT INTENT',source)
    def test_explicit_review_not_receiver_ack(self):
        for s in ['REVIEWED_LOCAL_ONLY','RAW_CHANGED__NOT_ACK','REWISED_AND_CLEARED','NOT receiver ACK']:
            self.assertIn(s,source)
    def test_no_predictive_private_broadcast(self):
        self.assertIn('effect_authority":"NONE"',source)
        self.assertNotRegex(source, r'\bfetch\s*\(|\bXMLHttpRequest\b|new\s+WebSocket\s*\(')
        for forbidden in ['localStorage','sessionStorage','navigator.sendBeacon','document.cookie','addEventListener("auxclick"']:
            self.assertNotIn(forbidden,source)
    def test_evo_control_keyboard_compatible(self):
        self.assertIn('id="evoAction"',source)
        self.assertIn('LOCAL PREVIEW:',source)
    def test_no_runtime_claim(self):
        self.assertIn('OFFLINE REFERENCE CANARY · NOT LIVE',source)
        self.assertIn('NOT_WALLPAPER_INSTALLED', (Path(__file__).parent/'README.md').read_text(encoding='utf-8'))

if __name__=='__main__':
    unittest.main(verbosity=2)