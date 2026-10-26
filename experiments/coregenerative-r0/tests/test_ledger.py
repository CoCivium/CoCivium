import json
import shutil
import tempfile
import unittest
from pathlib import Path
from verify_ledger import verify

ROOT=Path(__file__).resolve().parents[1]

class ReceiptChallenges(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='co_regen_')
        self.root=Path(self.tmp.name)
        (self.root/'output').mkdir()
        for src in ['cycle.py','build.py','README.md']:
            shutil.copy2(ROOT/src,self.root/src)
        for src in ['benchmark_evo.jsonl','HEAD.sha256','summary.json']:
            shutil.copy2(ROOT/'output'/src,self.root/'output'/src)
    def tearDown(self):self.tmp.cleanup()
    def test_original_ledger_verified(self):
        n,head=verify(self.root)
        self.assertEqual(n,13)
        self.assertEqual(len(head),64)
    def test_altered_event_rejected(self):
        p=self.root/'output/benchmark_evo.jsonl'
        s=p.read_text().replace('ATTENTION_BASELINE_LOW_YIELD','ATTENTION_BASELINE_HUGE_WIN')
        p.write_text(s)
        with self.assertRaises(AssertionError):verify(self.root)
    def test_truncated_ledger_rejected(self):
        p=self.root/'output/benchmark_evo.jsonl'
        p.write_text('\n'.join(p.read_text().splitlines()[:-1])+'\n')
        with self.assertRaises(AssertionError):verify(self.root)
    def test_duplicate_json_key_rejected(self):
        p=self.root/'output/benchmark_evo.jsonl'
        rows=p.read_text().splitlines()
        rows[0]=rows[0].replace('{','{"seq":1,',1)
        p.write_text('\n'.join(rows)+'\n')
        with self.assertRaises(AssertionError):verify(self.root)
    def test_wrong_head_rejected(self):
        (self.root/'output/HEAD.sha256').write_text('0'*64+'\n')
        with self.assertRaises(AssertionError):verify(self.root)
    def test_changed_source_rejected(self):
        p=self.root/'README.md'
        p.write_text(p.read_text()+'tampered\n')
        with self.assertRaises(AssertionError):verify(self.root)

if __name__=='__main__':unittest.main()
