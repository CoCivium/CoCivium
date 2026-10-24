import json
import os
from pathlib import Path
import tempfile
import unittest
import sys
from unittest import mock
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cothumb import create_capsule, verify_capsule, SCHEMA, MAX_FILES, check_authority

class CapsuleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.src=self.root/'intentionally-private-named-client-media.mp4'
        self.src.write_bytes(bytes([x % 251 for x in range(400_321)]))
        self.out=self.root/'out'

    def make(self):
        return create_capsule([str(self.src)], str(self.out), intent='inspect')

    def test_real_binary_above_300kb(self):
        path,manifest,receipt=self.make()
        self.assertGreater(manifest['total_bytes'],300_000)
        self.assertEqual(manifest['objects'][0]['size_bytes'],400_321)
        self.assertTrue((path/'bundle.copack.zip').is_file())

    def test_local_parallel_three_check_pass(self):
        path,_,_=self.make()
        r=verify_capsule(str(path),workers=3)
        self.assertEqual(r['state'],'PASS_LOCAL_CHECKS')
        self.assertEqual(len(r['checks']),3)
        self.assertEqual(r['receiver_readproof'],'NONE')

    def test_serial_parity(self):
        path,_,_=self.make()
        a=verify_capsule(str(path),workers=1,write_receipt=False)
        b=verify_capsule(str(path),workers=3,write_receipt=False)
        self.assertEqual(a['checks'],b['checks'])

    def test_filename_and_absolute_path_not_in_package(self):
        path,manifest,_=self.make()
        raw=(path/'manifest.json').read_text()
        self.assertNotIn(self.src.name,raw)
        self.assertNotIn(str(self.root),raw)
        with zipfile.ZipFile(path/'bundle.copack.zip') as z:
            for filename in z.namelist():
                self.assertNotIn(self.src.name, filename)
            self.assertNotIn(self.src.name,z.read('manifest.json').decode())

    def test_no_external_authority(self):
        path,m,_=self.make()
        self.assertEqual(m['authority']['remote_use'],'NONE')
        self.assertEqual(m['authority']['publish'],'NONE')
        self.assertEqual(m['effects']['messages_sent'],0)
        self.assertEqual(m['receiver']['readproof'],'NOT_RECEIVED')

    def test_tampered_payload_rejected(self):
        path,m,_=self.make()
        f=path/m['objects'][0]['payload_relpath']
        with f.open('r+b') as out:
            out.seek(0)
            out.write(b'Z')
        r=verify_capsule(str(path),write_receipt=False)
        self.assertEqual(r['state'],'FAIL_LOCAL_CHECKS')
        self.assertTrue(any(x['worker']=='content_hashes' and x['status']=='FAIL' for x in r['checks']))

    def test_tampered_archive_rejected(self):
        path,_,_=self.make()
        (path/'bundle.copack.zip').write_bytes(b'not-a-zip')
        self.assertEqual(verify_capsule(str(path),write_receipt=False)['state'],'FAIL_LOCAL_CHECKS')

    def test_manifest_external_authority_rejected(self):
        path,m,_=self.make()
        m['authority']['remote_use']='ALL'
        self.assertEqual(check_authority(path,m)['status'],'FAIL')

    def test_path_in_manifest_rejected(self):
        path,m,_=self.make()
        m['objects'][0]['original_name_and_path']='C:\\Secret\\private.txt'
        (path/'manifest.json').write_text(json.dumps(m))
        self.assertEqual(verify_capsule(str(path),write_receipt=False)['state'],'FAIL_LOCAL_CHECKS')

    def test_bad_relative_path_rejected(self):
        path,m,_=self.make()
        m['objects'][0]['payload_relpath']='../../etc/passwd'
        (path/'manifest.json').write_text(json.dumps(m))
        self.assertEqual(verify_capsule(str(path),write_receipt=False)['state'],'FAIL_LOCAL_CHECKS')

    def test_duplicate_source_rejected(self):
        with self.assertRaises(ValueError):
            create_capsule([str(self.src),str(self.src)],str(self.out))

    def test_bad_intent_rejected(self):
        with self.assertRaises(ValueError):
            create_capsule([str(self.src)],str(self.out),intent='send-to-everyone')

    def test_too_small_budget_rejected(self):
        with self.assertRaises(ValueError):
            create_capsule([str(self.src)],str(self.out),max_bytes=1024)

    def test_symlink_input_rejected(self):
        link=self.root/'sym.mp4'
        try:
            link.symlink_to(self.src)
        except OSError:
            self.skipTest('Symlink privileges unavailable')
        with self.assertRaises(ValueError):
            create_capsule([str(link)],str(self.out))

    def test_more_than_8_files_rejected(self):
        with self.assertRaises(ValueError):
            create_capsule([str(self.src)]*9,str(self.out))

    def test_invalid_workers_rejected(self):
        path,_,_=self.make()
        with self.assertRaises(ValueError):
            verify_capsule(str(path),workers=500)

    def test_receipt_write_is_no_clobber(self):
        path,_,_=self.make()
        a=verify_capsule(str(path),workers=1)
        b=verify_capsule(str(path),workers=1)
        self.assertEqual(a['state'],b['state'])
        self.assertEqual(len(list(path.glob('verify-*.json'))),2)

    def test_archive_has_exact_members(self):
        path,m,_=self.make()
        with zipfile.ZipFile(path/'bundle.copack.zip') as z:
            self.assertEqual(sorted(z.namelist()),['manifest.json','objects/object-001.blob'])
            self.assertEqual(z.read('objects/object-001.blob'),self.src.read_bytes())

if __name__ == '__main__':
    unittest.main(verbosity=2)
