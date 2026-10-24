from html.parser import HTMLParser
from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cospiff import ROOT,load_registry

class Parser(HTMLParser):
 def __init__(self): super().__init__(); self.hrefs=[];self.scripts=0;self.forms=0;self.inputs=0;self.details=0;self.summaries=0;self.main=0;self.route_articles=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a':self.hrefs.append(a.get('href',''))
  if tag=='script':self.scripts+=1
  if tag=='form':self.forms+=1
  if tag=='input':self.inputs+=1
  if tag=='details':self.details+=1
  if tag=='summary':self.summaries+=1
  if tag=='main':self.main+=1
  if tag=='article' and 'route' in a.get('class','').split():self.route_articles+=1

class HtmlSafety(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  text=(ROOT/'CoSpiff_FirstDoor.html').read_text(encoding='utf-8');cls.text=text;cls.parser=Parser();cls.parser.feed(text)
 def test_six_source_links_exact(self):
  expected=set(r['source_url'] for r in load_registry()['routes']); observed=set(h for h in self.parser.hrefs if '/blob/' in h)
  self.assertEqual(observed-expected, {'https://github.com/CoCivium/CoCivium/blob/main/ai/onramp/specialist-entrypoints-r0.json'})
  self.assertTrue(expected.issubset(observed))
 def test_no_js_or_tracking(self):
  self.assertEqual((self.parser.scripts,self.parser.forms,self.parser.inputs),(0,0,0))
 def test_progressive_disclosure(self):
  self.assertEqual((self.parser.details,self.parser.summaries,self.parser.main,self.parser.route_articles),(1,1,1,6))
 def test_label_source_only(self):
  self.assertEqual(self.text.count('Source verified in GitHub'),6)
 def test_no_invisible_fetch(self):
  for bad in ('http-equiv="refresh"','<iframe','<img ','localStorage','<script','fetch(','navigator.sendBeacon'):
   self.assertNotIn(bad,self.text)

if __name__=='__main__':unittest.main()
