import hashlib
import json
import unittest

from scripts.CoPreSeedPathReaderR0 import verify_bytes

class TestCoPreSeedPathReader(unittest.TestCase):
    def setUp(self):
        self.work = "copregeneric:handoff:public-seed-path:r0:20261109"
        self.payload = {"work_id":self.work,"state":"PUBLIC_SAFE_SOURCE_RECORD_NOT_RECEIVER_PICKUP_NOT_INTEGRATION_NOT_CANON","paths":[{"id":"path1"}]}
        self.raw=json.dumps(self.payload).encode()
        self.sha=hashlib.sha1(b"blob "+str(len(self.raw)).encode()+b"\0"+self.raw).hexdigest()

    def test_verified_packet(self):
        result=verify_bytes(self.raw,self.sha,self.work)
        self.assertEqual(result["cop_path_count"],1)

    def test_hash_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"BLOB_MISMATCH"):
            verify_bytes(self.raw,"0"*40,self.work)

    def test_work_id_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"WORK_ID_MISMATCH"):
            verify_bytes(self.raw,self.sha,"different")

    def test_state_mismatch_fails_closed(self):
        p=dict(self.payload,state="CANON")
        raw=json.dumps(p).encode()
        sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        with self.assertRaisesRegex(ValueError,"PACKET_STATE_MISMATCH"):
            verify_bytes(raw,sha,self.work)

    def test_empty_paths_fails_closed(self):
        p=dict(self.payload,paths=[])
        raw=json.dumps(p).encode()
        sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        with self.assertRaisesRegex(ValueError,"MISSING_COPATH"):
            verify_bytes(raw,sha,self.work)

if __name__ == "__main__":
    unittest.main()
