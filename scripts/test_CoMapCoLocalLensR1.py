#!/usr/bin/env python3
"""CoMap CoLocal lens R1: exact graph parity and public-source UX guardrails."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'examples/comap/colocal-source-lens-r1.html').read_text('utf-8')
R0 = json.loads((ROOT / 'ai/comap-source-projection-r0.json').read_text('utf-8'))
R1_PATH = ROOT / 'ai/comap-colocal-currentness-projection-r1.json'
R1_BYTES = R1_PATH.read_bytes()
R1 = json.loads(R1_BYTES)
MATCH = re.search(r'<script type="application/json" id="evidencePayload">(.*?)</script>', HTML, re.S)
if MATCH is None:
    raise RuntimeError('HOLD_LENS_EMBEDDED_DATA_MISSING')
PAYLOAD = json.loads(MATCH.group(1))


def gitblob(b):
    return hashlib.sha1(('blob %d\0' % len(b)).encode() + b).hexdigest()


class CoMapCoLocalLensR1(unittest.TestCase):
    def test_source_blob_pin(self):
        self.assertEqual(gitblob(R1_BYTES), '1c9eb9b4c608d2f13dc3d7bc8ec524831d6708a3')
        self.assertEqual(PAYLOAD['r1_source_blob'], gitblob(R1_BYTES))

    def test_r0_coverage_is_unchanged(self):
        self.assertEqual((len(R0['nodes']), len(R0['edges'])), (56, 61))

    def test_r1_is_versioned_successor(self):
        self.assertEqual((len(R1['nodes']), len(R1['edges'])), (58, 66))
        self.assertEqual(R1['predecessor']['git_blob_sha1'], '9cc47926d2f61f439db1818702127382f78d693f')

    def test_predecessor_nodes_exactly_preserved(self):
        self.assertEqual(R0['nodes'], R1['nodes'][:56])

    def test_predecessor_edges_exactly_preserved(self):
        self.assertEqual(R0['edges'], R1['edges'][:61])

    def test_five_relation_payload_matches_source_exactly(self):
        self.assertEqual(PAYLOAD['edges'], R1['edges'][-5:])

    def test_five_endpoint_payload_matches_source_exactly(self):
        ids = {x for e in R1['edges'][-5:] for x in (e['from'], e['to'])}
        expected = [
            {k: n.get(k) for k in ('id', 'label', 'kind', 'status', 'source', 'url')}
            for n in R1['nodes'] if n['id'] in ids
        ]
        self.assertEqual(PAYLOAD['nodes'], expected)
        self.assertEqual(len(expected), 5)

    def test_source_pointers_are_the_two_pinned_public_sources(self):
        self.assertEqual(PAYLOAD['sources'], R1['sources'][-2:])
        self.assertEqual(
            {s['blob_sha'] for s in PAYLOAD['sources']},
            {'c9c6dd3a4d6074a5a34e3decdbeb56f574d9f200',
             'b86ec3d7a30a9c1bb6e96c75fd242a3fe8c5cc97'}
        )

    def test_no_receiver_runtime_promotion(self):
        self.assertFalse(PAYLOAD['external_receiver_ack'])
        self.assertEqual(PAYLOAD['source_ci'], 'PASS_SOURCE_CI_ONLY_NOT_X2')
        self.assertIn('not verified', HTML.lower())

    def test_shown_scope_not_misrepresented_as_full_graph(self):
        self.assertEqual(PAYLOAD['display_scope'], 'FIVE_NEW_RELATIONS_ONLY_NOT_WHOLE_GRAPH')
        self.assertEqual((PAYLOAD['base_nodes'], PAYLOAD['base_edges']), (56, 61))
        self.assertEqual((PAYLOAD['r1_nodes'], PAYLOAD['r1_edges']), (58, 66))

    def test_schema_and_links_exposed(self):
        self.assertIn('<html lang="en">', HTML)
        self.assertIn('aria-live="polite"', HTML)
        self.assertIn('aria-pressed="true"', HTML)
        self.assertIn('href="source-weave-r0.html"', HTML)
        self.assertIn('href="../../docs/CoLocal/README.md"', HTML)
        self.assertIn('href="../../ai/comap-colocal-currentness-projection-r1.json"', HTML)

    def test_controls_have_handlers(self):
        for item in ('id="search"', 'data-filter="seed"', 'data-filter="ci"',
                     'id="reset"', 'id="relations"', 'id="nodes"', 'id="detailLinks"'):
            self.assertIn(item, HTML)
        self.assertIn('addEventListener("input",draw)', HTML)
        self.assertIn('aria-pressed', HTML)

    def test_no_external_request_or_inline_remote_assets(self):
        self.assertNotRegex(HTML, r'<script[^>]+src=')
        self.assertNotRegex(HTML, r'<link[^>]+href=')
        self.assertNotRegex(HTML, r'\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon')
        self.assertNotIn('<iframe', HTML)

    def test_source_content_is_rendered_with_textcontent(self):
        self.assertNotIn('innerHTML', HTML)
        self.assertIn('textContent=e.relation', HTML)
        self.assertIn('textContent=n.label', HTML)

    def test_private_identifiers_not_exported(self):
        for private in ('D:\\CoCivium', 'C:\\Users\\Owner', 'libfile_', 'file_00000000',
                        '@inseed.com', 'PRIVATE_LIBRARY_DONORS'):
            self.assertNotIn(private, HTML)

    def test_mobile_css_and_no_forced_wide_layout(self):
        self.assertIn('@media(max-width:440px)', HTML)
        self.assertIn('minmax(0,1fr)', HTML)
        self.assertNotIn('min-width:900px', HTML)

    def test_every_new_edge_source_exists(self):
        source_ids={s['id'] for s in R1['sources']}
        self.assertTrue(all(e['source'] in source_ids for e in PAYLOAD['edges']))

    def test_renderer_keeps_counters_literal_and_honest(self):
        self.assertIn('of 5 new source-typed relations shown', HTML)
        self.assertIn('56 → 58', HTML)
        self.assertIn('61 → 66', HTML)


if __name__ == '__main__':
    unittest.main()
