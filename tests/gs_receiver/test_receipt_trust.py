"""Receipt authenticity and custody checks, isolated reference contract.

HMAC proves possession of a shared key, not independent identity, authorization,
or a live X2 receiver. Production should use managed keys and rotation.
"""
import hashlib
import hmac
import json
import unittest

KEY = b"test-only-shared-key"

def canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def sign(record, key=KEY):
    return hmac.new(key, canonical(record), hashlib.sha256).hexdigest()

def validate(record, signature, key=KEY, expected_work="seed", expected_epoch=2):
    if not isinstance(signature, str):
        return "BAD_SIGNATURE"
    expected = sign(record, key)
    if not hmac.compare_digest(expected, signature):
        return "BAD_SIGNATURE"
    if record.get("work_id") != expected_work or record.get("epoch") != expected_epoch:
        return "WRONG_CUSTODY"
    if record.get("outcome") not in ("COMMITTED", "FAILED"):
        return "UNKNOWN_OUTCOME"
    return "AUTHENTICATED_NOT_AUTHORIZED"

class ReceiptTrustTests(unittest.TestCase):
    def setUp(self):
        self.receipt = {"work_id": "seed", "epoch": 2, "event_id": "e1",
                        "observed_at": 100, "outcome": "COMMITTED"}
        self.signature = sign(self.receipt)

    def test_valid_mac_does_not_grant_authorization(self):
        self.assertEqual(validate(self.receipt, self.signature), "AUTHENTICATED_NOT_AUTHORIZED")

    def test_payload_tamper_rejected(self):
        modified = dict(self.receipt, outcome="FAILED")
        self.assertEqual(validate(modified, self.signature), "BAD_SIGNATURE")

    def test_wrong_epoch_rejected_even_if_signed(self):
        modified = dict(self.receipt, epoch=1)
        self.assertEqual(validate(modified, sign(modified)), "WRONG_CUSTODY")

    def test_wrong_work_rejected_even_if_signed(self):
        modified = dict(self.receipt, work_id="other")
        self.assertEqual(validate(modified, sign(modified)), "WRONG_CUSTODY")

    def test_missing_signature_rejected(self):
        self.assertEqual(validate(self.receipt, None), "BAD_SIGNATURE")

if __name__ == "__main__":
    unittest.main(verbosity=2)
