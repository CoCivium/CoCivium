import json
import re
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from braid import ROOT,load

class ViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'CoGoldenBraid_Viewer.html').read_text(encoding='utf-8')
    def test_seed_present(self):
        self.assertIn('CoGoldenBraidWisdomSeed/0.1',self.html)
    def test_no_request_apis(self):
        for disallowed in ('fetch(', 'XMLHttpRequest','WebSocket(', 'sendBeacon(', 'EventSource('):
            with self.subTest(disallowed=disallowed):self.assertNotIn(disallowed,self.html)
    def test_no_hidden_storage(self):
        for disallowed in ('localStorage','sessionStorage','indexedDB','serviceWorker'):
            with self.subTest(disallowed=disallowed):self.assertNotIn(disallowed,self.html)
    def test_no_clipboard_read(self):
        self.assertNotIn('clipboard.readText',self.html)
        self.assertIn("e('copy').addEventListener('click'",self.html)
    def test_no_autopost(self):
        self.assertNotIn('submit()',self.html)
        self.assertNotIn('form action=',self.html)
    def test_explicit_counterexample(self):
        self.assertIn('Where it may fail',self.html)
    def test_provenance_hidden_until_requested(self):
        self.assertIn('<details><summary>Source boundary and lineage',self.html)
    def test_keyboard_supported(self):
        self.assertIn('<button id="prev"',self.html)
        self.assertIn('<select id="pick"',self.html)
    def test_no_autonomous_loop(self):
        self.assertNotIn('setInterval(',self.html)
        self.assertNotIn('setTimeout(',self.html)
    def test_no_public_personal_data(self):
        self.assertNotIn('rballard@',self.html)
        self.assertNotIn('Andrew Kalek',self.html)

if __name__=='__main__':unittest.main()
