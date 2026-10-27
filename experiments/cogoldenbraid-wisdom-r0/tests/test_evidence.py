import copy
import json
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_evidence import verify
from braid import ROOT

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=(ROOT/'benchmark_evo.jsonl').read_text(encoding='utf-8').splitlines()
        cls.head=(ROOT/'HEAD.sha256').read_text(encoding='utf-8').strip()

    def test_valid_chain(self):self.assertGreater(verify(self.ledger,self.head),10)
    def test_tamper_rejected(self):
        rows=self.ledger.copy()
        obj=json.loads(rows[2]);obj['detail']['external_requests']=12;rows[2]=json.dumps(obj)
        with self.assertRaisesRegex(ValueError,'TAMPERED'):verify(rows,self.head)
    def test_truncate_rejected(self):
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'):verify(self.ledger[:-1],self.head)
    def test_wrong_head_rejected(self):
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'):verify(self.ledger,'0'*64)
    def test_duplicate_key_rejected(self):
        rows=self.ledger.copy();rows[0]=rows[0].replace('"seq":1','"seq":1,"seq":1')
        with self.assertRaisesRegex(ValueError,'DUPLICATE_KEY'):verify(rows,self.head)

if __name__=='__main__':unittest.main()
