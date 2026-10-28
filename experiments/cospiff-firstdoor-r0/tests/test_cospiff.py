import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cospiff import load_registry,audit_registry,propose_route,write_ledger,verify_ledger,hash_event

class AuditTests(unittest.TestCase):
    def setUp(self):self.registry=load_registry()
    def test_six_pinned_routes(self):self.assertEqual(audit_registry(self.registry),[])
    def test_reject_forged_authority(self):
        self.registry['routes'][1]['authority']='WRITE';self.assertIn('IMPLIED_AUTHORITY:words', audit_registry(self.registry))
    def test_reject_domain_alias(self):
        self.registry['routes'][1]['source_url']='https://cocivium.org/words';self.assertIn('SOURCE_URL_MISMATCH:words',audit_registry(self.registry))
    def test_reject_stale_or_wrong_blob(self):
        self.registry['routes'][1]['git_blob']='not_a_sha';self.assertIn('BAD_BLOB:words',audit_registry(self.registry))
    def test_reject_parent_traversal(self):
        self.registry['routes'][1]['path']='../private';self.assertIn('BAD_PATH:words',audit_registry(self.registry))
    def test_reject_duplicate(self):
        self.registry['routes'][2]['id']='words';self.assertIn('DUPLICATE_ROUTE_ID',audit_registry(self.registry))
    def test_all_public_no_login_required(self):
        for route in self.registry['routes']:
            self.assertEqual(route['authority'],'NONE');self.assertFalse(route['role_required']);self.assertTrue(route['source_only'])

class RouterTests(unittest.TestCase):
    def test_default_no_profile(self):self.assertEqual(propose_route('I am curious')['route'],'one-task')
    def test_route_qualified(self):self.assertEqual(propose_route('visualize relationships')['route'],'relationships')
    def test_ambiguous_is_not_forced(self):self.assertEqual(propose_route('build a fictional game')['state'],'ASK_OPTIONAL_CHOICE')
    def test_sensitive_is_held(self):self.assertEqual(propose_route('my private key here')['state'],'HOLD')
    def test_no_implicit_execution(self):self.assertEqual(propose_route('build a python tool')['state'],'SUGGEST_ONLY')
    def test_invalid_type_held(self):self.assertEqual(propose_route(None)['state'],'HOLD')
    def test_oversized_input_held(self):self.assertEqual(propose_route('x'*5000)['state'],'HOLD')

class LedgerTests(unittest.TestCase):
    def test_valid_and_tampered(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'events.jsonl'
            head=write_ledger([{'kind':'TEST','status':'PASS','result':{'a':1}}],p)
            self.assertEqual(verify_ledger(p,head),1)
            row=json.loads(p.read_text());row['result']['a']=2
            p.write_text(json.dumps(row)+'\n')
            with self.assertRaises(ValueError):verify_ledger(p,head)
    def test_wrong_pinned_head(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'events.jsonl';write_ledger([{'kind':'TEST','status':'FAIL'}],p)
            with self.assertRaises(ValueError):verify_ledger(p,'0'*64)

if __name__=='__main__':unittest.main()
