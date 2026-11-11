"""Negative controls for the standalone evidence verifier."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_ledger import verify

LEDGER=(ROOT/'output/benchmark_evo.jsonl').read_text()
HEAD=(ROOT/'output/HEAD.sha256').read_text().strip()

class LedgerTests(unittest.TestCase):
    def test_actual_ledger(self):self.assertEqual(verify(LEDGER,HEAD),21)
    def test_modified_content_rejected(self):
        lines=LEDGER.splitlines()
        row=json.loads(lines[3]);row['detail']['visible']=[0,0,0]
        lines[3]=json.dumps(row)
        with self.assertRaisesRegex(ValueError,'TAMPERED_ROW'):verify('\n'.join(lines),HEAD)
    def test_truncation_rejected(self):
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'):verify('\n'.join(LEDGER.splitlines()[:-1]),HEAD)
    def test_fake_final_head_rejected(self):
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'):verify(LEDGER,'0'*64)
if __name__=='__main__':unittest.main()
