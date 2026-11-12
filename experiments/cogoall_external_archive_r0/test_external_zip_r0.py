import io, pathlib, sqlite3, tempfile, unittest, zipfile
from verify_external_zip_r0 import verify, Held, PIN

ROOT = pathlib.Path(__file__).parent
ARCHIVE = ROOT / "cogoall-unfinished-43113671112-a1.zip"

class ProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ARCHIVE.read_bytes()

    def test_real_archive_exact_readback(self):
        v = verify(self.data)
        self.assertEqual(v['queue_state'], 'LEASED_UNFINISHED')
        self.assertFalse(v['external_receiver_ack'])
        self.assertFalse(v['source_bytes_independently_fetched'])
        self.assertEqual(v['queue_rows'],1)

    def test_truncated_zip_held(self):
        with self.assertRaisesRegex(Held,'HOLD_ZIP_HASH'):
            verify(self.data[:-50])

    def test_mutated_zip_held(self):
        x = bytearray(self.data)
        x[20] ^= 1
        with self.assertRaisesRegex(Held,'HOLD_ZIP_HASH'):
            verify(bytes(x))

    def test_wrong_artifact_digest_held(self):
        pin = {**PIN, 'zip_sha256':'0'*64}
        with self.assertRaisesRegex(Held,'HOLD_ZIP_HASH'):
            verify(self.data,pin)

    def test_wrong_manifest_digest_held(self):
        pin={**PIN, 'manifest_sha256':'1'*64}
        with self.assertRaisesRegex(Held,'HOLD_MANIFEST_HASH'):
            verify(self.data,pin)

    def test_wrong_queue_digest_held(self):
        pin={**PIN,'queue_sha256':'2'*64}
        with self.assertRaisesRegex(Held,'HOLD_QUEUE_HASH'):
            verify(self.data,pin)

    def test_wrong_workid_held(self):
        pin={**PIN,'work_id':'not-original-work'}
        with self.assertRaisesRegex(Held,'HOLD_MANIFEST_FIELD_WORK_ID'):
            verify(self.data,pin)

if __name__=='__main__': unittest.main(verbosity=2)
