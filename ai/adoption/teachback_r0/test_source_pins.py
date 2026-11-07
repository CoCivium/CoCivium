import copy
import hashlib
import json
import pathlib
import tempfile
import unittest
from verify_pins import verify, blob_sha1

class CheckoutPinTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.path=self.root/'docs'/'info.md';self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b'public fixture source\n')
        self.m={'source_repo':'CoCivium/CoCivium','source_paths_count':1,'source_index':[{'id':'one','path':'docs/info.md','git_blob_sha1':blob_sha1(self.path.read_bytes())}]}
        self.sync()
    def sync(self):
        self.body=(json.dumps(self.m,sort_keys=True)+'\n').encode()
        self.pin=blob_sha1(self.body)
    def good(self,mb=None,pin=None):
        return verify(self.body if mb is None else mb,self.root,self.pin if pin is None else pin)
    def reject(self,mb=None,pin=None):
        with self.assertRaises((ValueError,KeyError,OSError)):
            self.good(mb,pin)
    def test_valid_checkout(self):
        s=self.good();self.assertEqual(s['sources_count'],1);self.assertEqual(s['external_receiver_ack'],'NOT_OBSERVED')
    def test_tampered_file(self):
        self.path.write_bytes(b'public fixture SOURCE changed\n');self.reject()
    def test_deleted_file(self):
        self.path.unlink();self.reject()
    def test_manifest_modified_but_old_pin(self):
        m=copy.deepcopy(self.m);m['source_index'][0]['id']='spoof'
        self.reject(mb=(json.dumps(m,sort_keys=True)+'\n').encode())
    def test_wrong_expected_pin(self):self.reject(pin='0'*40)
    def test_parent_escape(self):
        self.m['source_index'][0]['path']='../secret';self.sync();self.reject()
    def test_absolute_path(self):
        self.m['source_index'][0]['path']='/tmp/secret';self.sync();self.reject()
    def test_duplicate_source(self):
        self.m['source_index'].append(copy.deepcopy(self.m['source_index'][0]));self.m['source_paths_count']=2;self.sync();self.reject()
    def test_source_list_count(self):
        self.m['source_paths_count']=99;self.sync();self.reject()
    def test_unqualified_repo(self):
        self.m['source_repo']='untrusted/other';self.sync();self.reject()
    def test_invalid_hash(self):
        self.m['source_index'][0]['git_blob_sha1']='not-a-blob';self.sync();self.reject()

if __name__=='__main__':unittest.main()
