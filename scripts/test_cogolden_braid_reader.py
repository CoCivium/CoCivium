import json
import unittest
from cogolden_braid_reader import check, blob_sha

class GoldenBraidReaderTests(unittest.TestCase):
    def setUp(self):
        self.doc = {
            "schema": "cocivium.cogolden_braid.front_continuity.r0",
            "status": "PUBLIC_DRAFT_CONTRACT_NOT_AUTONOMOUS_RUNTIME",
            "front_identity": {}, "golden_thread": {}, "braid": {},
            "fray": {}, "continuity": {}, "tests": []
        }
        self.payload = json.dumps(self.doc).encode()

    def test_valid_pinned_document(self):
        self.assertTrue(check(self.payload, blob_sha(self.payload))["passed"])

    def test_hash_mismatch_fails_closed(self):
        receipt = check(self.payload, "0" * 40)
        self.assertFalse(receipt["passed"])
        self.assertEqual(receipt["hold_reason"], "contract_hash_mismatch")

    def test_missing_section_fails_closed(self):
        self.doc.pop("fray")
        data = json.dumps(self.doc).encode()
        self.assertFalse(check(data, blob_sha(data))["passed"])

    def test_runtime_claim_fails_closed(self):
        self.doc["status"] = "RUNTIME_VERIFIED"
        data = json.dumps(self.doc).encode()
        self.assertFalse(check(data, blob_sha(data))["passed"])

    def test_bad_json_fails_closed(self):
        data = b"{broken"
        self.assertFalse(check(data, blob_sha(data))["passed"])

if __name__ == "__main__":
    unittest.main()
