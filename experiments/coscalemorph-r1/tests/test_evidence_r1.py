import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_evidence_r1 import verify
OUT=ROOT/'output'
DATA=(OUT/'benchmark_evo_R1.jsonl').read_text()
HEAD=(OUT/'HEAD_R1.sha256').read_text().strip()
PARENT=(OUT/'HEAD.sha256').read_text().strip()

class EvidenceTests(unittest.TestCase):
    def bad(self,changed):
        with self.assertRaises((ValueError,TypeError)):verify(changed,HEAD,PARENT)

    def test_frozen_evidence(self):
        s=verify(DATA,HEAD,PARENT)
        self.assertEqual(s['events'],32)
        self.assertEqual(s['statuses'],{'FAIL':3,'HOLD':3,'NOT_RUN':8,'PASS':18})

    def test_row_modified(self):
        self.bad(DATA.replace('HYPOTHESIS_TWO_PROCESSES_ALWAYS_FASTER','HYPOTHESIS_TWO_PROCESSES_NOT_FASTER'))

    def test_truncated_chain(self):
        self.bad('\n'.join(DATA.splitlines()[:-1]))

    def test_new_fake_head(self):
        with self.assertRaises(ValueError):verify(DATA,'a'*64,PARENT)

    def test_wrong_parent(self):
        with self.assertRaises(ValueError):verify(DATA,HEAD,'a'*64)

    def test_duplicate_json_key(self):
        self.bad(DATA.replace('"schema":', '"schema":"fake","schema":',1))

    def test_missing_status_not_silent_pass(self):
        self.bad(DATA.replace('"outcome":"PASS"','"outcome":"GOOD"',1))

if __name__=='__main__':unittest.main()
