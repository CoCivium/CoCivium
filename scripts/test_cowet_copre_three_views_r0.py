"""Three-view CoPre binding: source-only regression, not browser acceptance."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"examples/cowet/copre-three-views-r0.html"
GRAPH=ROOT/"ai/copre-seed-path-fabric-r0-20261109.json"
WORK="CoAll.CoPreGeneric.CrossAudience.20261109"
NODE="copre-entry"

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.articles=[]
        self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="article":self.articles.append(a)
        if tag=="a":self.links.append(a.get("href"))

class ThreeViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=PAGE.read_text(encoding="utf-8")
        cls.parser=Inspector();cls.parser.feed(cls.html)
        cls.graph=json.loads(GRAPH.read_text(encoding="utf-8"))
    def test_three_views_same_workid(self):
        self.assertEqual(len(self.parser.articles),3)
        self.assertEqual({x.get("data-work-id") for x in self.parser.articles},{WORK})
        self.assertEqual({x.get("data-graph-node-id") for x in self.parser.articles},{NODE})
    def test_graph_has_exact_entry(self):
        items=[n for n in self.graph["nodes"] if n["id"]==NODE]
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]["path"],"CoPre.md")
    def test_all_references_resolve_locally(self):
        for href in self.parser.links:
            if href and href.startswith("../"):
                self.assertTrue((PAGE.parent / href).resolve().is_file(),href)
    def test_no_fake_receiver_ack(self):
        self.assertIn("UNPROVEN",self.html)
        self.assertNotIn("receiver_ack:true",self.html)
    def test_no_sound_or_network(self):
        self.assertIn("script-src 'none'",self.html)
        self.assertIn("connect-src 'none'",self.html)
        self.assertNotIn("<audio",self.html)
    def test_accessibility_and_source_plain(self):
        self.assertIn("Skip to verified source context",self.html)
        self.assertIn("aria-label=",self.html)
        self.assertIn("Accessible text",self.html)
    def test_rich_and_plain_share_source(self):
        self.assertGreaterEqual(self.html.count('href="../../CoPre.md"'),3)
    def test_no_authority_conversion(self):
        self.assertIn("grants no execution privileges",self.html)
        self.assertIn("NOT CANON",self.html)

if __name__=="__main__":
    unittest.main()
