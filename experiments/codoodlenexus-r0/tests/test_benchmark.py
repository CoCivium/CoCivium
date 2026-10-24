import json
import pathlib
import sys
import unittest
from html.parser import HTMLParser
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import benchmark
import nexus
import build_view

class TagScanner(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.ids=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
        self.ids.extend([v for k,v in attrs if k=='id'])

class BenchmarkTests(unittest.TestCase):
    def test_normal_selector_fixture(self):
        b=benchmark.run(trials=20)
        self.assertEqual(b['outcome_normal'],{'wins':20,'ties':0,'losses':0})

    def test_adversarial_loses(self):
        b=benchmark.run(trials=20)
        self.assertEqual(b['outcome_adversarial'],{'wins':0,'ties':0,'losses':20})

    def test_timing_nonzero(self):
        b=benchmark.measure(samples=64,repeats=3)
        self.assertGreater(b['median_compile_ms'],0)
        self.assertIn('no experiment',b['warning'].lower())

    def test_reject_benchmark_flood(self):
        for kwargs in ({'trials':1001},{'sample':2049},{'pick':17}):
            with self.assertRaises(ValueError): benchmark.run(**kwargs)

    def test_view_embeds_no_private_input(self):
        s=(pathlib.Path(__file__).resolve().parents[1]/'CoDoodleNexus_Viewer.html').read_text()
        self.assertIn('connect-src \'none\'',s)
        self.assertNotIn('https://',s)
        self.assertNotIn('XMLHttpRequest',s)
        self.assertNotIn('fetch(',s)
        self.assertNotIn('localStorage',s)
        self.assertNotIn('navigator.clipboard',s)

    def test_view_progressive_disclosure(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        s=(root/'CoDoodleNexus_Viewer.html').read_text()
        scanner=TagScanner();scanner.feed(s)
        self.assertIn("tag('details',div)",s)
        for id in ('all','shadow','held','cards','triage','benchmark'):
            self.assertIn(id,scanner.ids)
        self.assertIn('No candidates in this filter.',s)

    def test_source_is_manifested_and_not_microsecond_claim(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        x=json.loads((root/'output/shadow_candidates.json').read_text())
        self.assertEqual(x['manifest_hash'],nexus.sha(nexus.DIMENSIONS))
        self.assertEqual(x['logical_capacity'],nexus.capacity())
        self.assertNotIn('microsecond',json.dumps(x))

if __name__=='__main__': unittest.main()
