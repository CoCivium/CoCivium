import hashlib
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ViewerTests(unittest.TestCase):
    def test_no_external_assets(self):
        src=(ROOT/'CoAliveObject_Viewer.html').read_text()
        for term in ('src="http','href="http','fetch(', 'XMLHttpRequest', 'WebSocket', 'navigator.clipboard', 'window.open('):
            self.assertNotIn(term,src)
    def test_payload_matches_frozen_trace(self):
        src=(ROOT/'CoAliveObject_Viewer.html').read_text()
        p=src.split('<script id="data" type="application/json">',1)[1].split('</script>',1)[0]
        data=json.loads(p)
        trace=json.loads((ROOT/'output/pulse_trace.json').read_text())
        self.assertEqual(data['trace'], trace['trace'])
    def test_no_live_status_claim(self):
        src=(ROOT/'CoAliveObject_Viewer.html').read_text()
        self.assertIn('OFFLINE',src)
        self.assertIn('No provider calls or receiver acknowledgments observed.',src)
if __name__=='__main__':unittest.main()
