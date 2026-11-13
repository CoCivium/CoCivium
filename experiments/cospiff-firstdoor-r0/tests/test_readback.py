from pathlib import Path
import json
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cospiff import ROOT,load_registry

class SourceEvidence(unittest.TestCase):
 def test_six_github_readbacks_match_pinned(self):
  record=json.loads((ROOT/'source_readback.json').read_text(encoding='utf-8'))
  pinned={r['id']:r for r in load_registry()['routes']}
  self.assertEqual(len(record['observations']),6)
  self.assertEqual(set(x['id'] for x in record['observations']),set(pinned))
  for obj in record['observations']:
   route=pinned[obj['id']]
   self.assertEqual(obj['method'],'GitHub connector fetch_file')
   self.assertEqual(obj['observed_blob'],route['git_blob'])
   self.assertEqual(obj['locator'],route['source_url'])
   self.assertNotIn('remote_receiver_ack',obj)
 def test_no_false_http_claim(self):
  record=json.loads((ROOT/'source_readback.json').read_text(encoding='utf-8'))
  self.assertEqual(record['http_hosted_reachability'],'NOT_RUN')
  self.assertEqual(record['independent_users'],'NOT_MEASURED')

if __name__=='__main__':unittest.main()
