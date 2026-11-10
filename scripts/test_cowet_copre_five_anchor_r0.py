"""CoPre five-anchor source-only quality checks; does not imply browser acceptance."""
from pathlib import Path
from html.parser import HTMLParser
import unittest
ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"examples/cowet/copre-five-anchor-frontdoor-r0.html"
class P(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set();self.times=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a":self.links.append(a.get("href",""))
        if "id" in a:self.ids.add(a["id"])
        if tag=="time":self.times.append(a.get("datetime"))
class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.txt=PAGE.read_text(encoding="utf-8")
        cls.page=P();cls.page.feed(cls.txt)
    def test_five_unique_anchors(self):
        for key in ["1 Seed","1 Orb","1 gauge","1 thumb","1 time"]:
            self.assertEqual(self.txt.count(key),1,key)
    def test_no_broken_local_links(self):
        for href in self.page.links:
            if not href or href.startswith("#"):continue
            source,_,fragment=href.partition("#")
            self.assertTrue((PAGE.parent/source).resolve().is_file(),href)
            self.assertFalse(fragment)
    def test_single_explicit_source_thumb(self):
        self.assertIn('id="thumb"',self.txt)
        self.assertIn("Open current CoPre source",self.txt)
        self.assertIn('href="../../CoPre.md"',self.txt)
    def test_hold_flags_visible(self):
        for term in ["UNPROVEN","Exactly-once external receiver effect",
                     "24-hour survival","Autonomous cross-session sync"]:
            self.assertIn(term,self.txt)
    def test_no_audio_or_external_automatic_runtime(self):
        self.assertIn("script-src 'none'",self.txt)
        self.assertIn("connect-src 'none'",self.txt)
        self.assertNotIn("<audio",self.txt)
        self.assertNotIn("<script",self.txt)
    def test_time_is_explicitly_date_only(self):
        self.assertEqual(self.page.times,["2026-11-10T00:00:00Z"])
        self.assertIn("(date only)",self.txt)
        self.assertIn("not a live poll",self.txt)
    def test_semantic_access_and_motion(self):
        self.assertIn("aria-label=",self.txt)
        self.assertIn("Skip to evidence",self.txt)
        self.assertIn("prefers-reduced-motion:reduce",self.txt)
    def test_not_device_or_worker_claim(self):
        self.assertIn("does not type into another application",self.txt)
        self.assertIn("no deployed CoOrb runtime",self.txt)
if __name__=="__main__":
    unittest.main()
