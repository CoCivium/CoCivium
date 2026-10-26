import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'src'/'evidence.py'
s=importlib.util.spec_from_file_location('evidence',p)
e=importlib.util.module_from_spec(s)
sys.modules[s.name]=e
s.loader.exec_module(e)

class EvidenceTest(unittest.TestCase):
    def test_chain(self):
        self.assertEqual(e.verify(),24)
    def test_explicit_negative_result_retained(self):
        ev,_=e.generate(json.loads((ROOT/'output'/'measurement.json').read_text()))
        self.assertEqual([x['status'] for x in ev].count('FAIL'),2)
        self.assertEqual(next(x['test'] for x in ev if x['status']=='FAIL'), 'NAIVE_DARK_MEANS_EMPTY_BASELINE')
    def test_modified_event_rejected(self):
        lines=(ROOT/'output'/'benchmark_evo.jsonl').read_text().splitlines()
        o=json.loads(lines[3]);o['status']='PASS';lines[3]=json.dumps(o)
        with tempfile.TemporaryDirectory() as t:
            q=pathlib.Path(t)/'events.jsonl';q.write_text('\n'.join(lines)+'\n')
            with self.assertRaisesRegex(ValueError,'BAD_EVENT_HASH'):
                e.verify(q,ROOT/'output'/'HEAD.sha256')
    def test_truncation_rejected(self):
        lines=(ROOT/'output'/'benchmark_evo.jsonl').read_text().splitlines()
        with tempfile.TemporaryDirectory() as t:
            q=pathlib.Path(t)/'events.jsonl';q.write_text('\n'.join(lines[:-1])+'\n')
            with self.assertRaisesRegex(ValueError,'PINNED_HEAD_MISMATCH'):
                e.verify(q,ROOT/'output'/'HEAD.sha256')
    def test_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            q=pathlib.Path(t)/'events.jsonl';q.write_text('{"seq":1,"seq":2}\n')
            with self.assertRaisesRegex(ValueError,'DUPLICATE_KEY'):
                e.verify(q,ROOT/'output'/'HEAD.sha256')
    def test_wrong_head_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            h=pathlib.Path(t)/'HEAD.sha256';h.write_text('f'*64+'\n')
            with self.assertRaisesRegex(ValueError,'PINNED_HEAD_MISMATCH'):
                e.verify(ROOT/'output'/'benchmark_evo.jsonl',h)

if __name__=='__main__':unittest.main()
