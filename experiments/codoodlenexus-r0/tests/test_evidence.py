import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import verify_evidence as ev

class EvidenceTests(unittest.TestCase):
    def fake(self):
        row={'schema':'CoDoodleNexus.Receipt.R0','seq':1,'kind':'TEST','status':'PASS',
             'detail':'synthetic','prev_hash':'0'*64}
        row['event_hash']=ev.digest(row)
        return row
    def test_valid(self):
        row=self.fake();self.assertEqual(ev.verify([json.dumps(row)],row['event_hash'])['events'],1)
    def test_modified(self):
        row=self.fake();row['detail']='silently altered'
        with self.assertRaisesRegex(ValueError,'BAD_EVENT_HASH'): ev.verify([json.dumps(row)],row['event_hash'])
    def test_truncated(self):
        row=self.fake();withheld='0'*64
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'):ev.verify([json.dumps(row)],withheld)
    def test_duplicate_key(self):
        row=self.fake();raw=json.dumps(row)
        raw=raw[:-1]+',"seq":1}'
        with self.assertRaisesRegex(ValueError,'DUPLICATE_KEY'):ev.verify([raw],row['event_hash'])
    def test_wrong_sequence(self):
        row=self.fake();row['seq']=2;row['event_hash']=ev.digest({k:v for k,v in row.items() if k!='event_hash'})
        with self.assertRaisesRegex(ValueError,'BAD_SEQUENCE'):ev.verify([json.dumps(row)],row['event_hash'])

if __name__=='__main__':unittest.main()
