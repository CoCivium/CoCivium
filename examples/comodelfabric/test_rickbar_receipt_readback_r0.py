"""Fresh-process structural readback with tamper and false-ACK controls."""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from test_gateway_bridge import ReceiptStore
from rickbar_receipt_readback_r0 import readback

SCRIPT = pathlib.Path(__file__).with_name("rickbar_receipt_readback_r0.py")


class ColdReadbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.wid = "rb-fixture-1"
        self.synthetic_result = {
            "work_id": self.wid,
            "model": "fixture-local",
            "status": "MODEL_OUTPUT_UNVERIFIED",
            "text": "synthetic private-shaped output, not returned to caller",
        }
        self.receipt = ReceiptStore(self.tmp.name).save(self.wid, self.synthetic_result)
        self.path = self.root / (self.wid + ".json")
        self.sha = self.receipt["sha256"]

    def tearDown(self):
        self.tmp.cleanup()

    def call_cli(self, sha=None, wid=None, root=None):
        c = subprocess.run([sys.executable, "-B", str(SCRIPT),
                            "--receipt-dir", str(root or self.root),
                            "--work-id", wid or self.wid,
                            "--sha256", sha or self.sha],
                           capture_output=True, text=True, timeout=6, check=False)
        return c.returncode, json.loads(c.stdout)

    def test_fresh_process_recovers_exact_receipt(self):
        status, data = self.call_cli()
        self.assertEqual(status, 0)
        self.assertEqual(data["sha256"], self.sha)
        self.assertEqual(data["state"], "STRUCTURAL_COLD_PROCESS_READBACK")
        self.assertNotEqual(data["reader_pid"], os.getpid())
        self.assertFalse(data["independent_receiver_ack"])
        self.assertFalse(data["model_output_verified"])
        self.assertNotIn("synthetic private-shaped output", json.dumps(data))

    def test_second_read_deterministic(self):
        a = readback(self.tmp.name, self.wid, self.sha)
        b = readback(self.tmp.name, self.wid, self.sha)
        self.assertEqual(a["sha256"], b["sha256"])
        self.assertEqual(a["state"], b["state"])

    def test_tampered_bytes_fail(self):
        self.path.write_bytes(self.path.read_bytes() + b" ")
        status, data = self.call_cli()
        self.assertEqual(status, 3)
        self.assertEqual(data["reason"], "RECEIPT_DIGEST_MISMATCH")

    def test_wrong_digest_fails(self):
        status, data = self.call_cli(sha="a" * 64)
        self.assertEqual(status, 3)
        self.assertEqual(data["reason"], "RECEIPT_DIGEST_MISMATCH")

    def test_invalid_digest_fails(self):
        with self.assertRaisesRegex(ValueError, "INVALID_EXPECTED_DIGEST"):
            readback(self.tmp.name, self.wid, "not-a-digest")

    def test_parent_path_attack_fails(self):
        with self.assertRaisesRegex(ValueError, "INVALID_WORK_ID"):
            readback(self.tmp.name, "../escape", self.sha)

    def test_other_work_id_not_promoted(self):
        with self.assertRaisesRegex(ValueError, "RECEIPT_NOT_READABLE"):
            readback(self.tmp.name, "some-other", self.sha)

    def test_identity_mismatch_fails_despite_valid_hash(self):
        altered = json.loads(self.path.read_text())
        altered["result"]["work_id"] = "different"
        raw = json.dumps(altered, sort_keys=True).encode("utf-8")
        self.path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "IDENTITY"):
            readback(self.tmp.name, self.wid, hashlib.sha256(raw).hexdigest())

    def test_fake_verified_status_fails_even_with_hash(self):
        altered = json.loads(self.path.read_text())
        altered["status"] = "VERIFIED_EFFECT"
        raw = json.dumps(altered, sort_keys=True).encode("utf-8")
        self.path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "STATE_MISMATCH"):
            readback(self.tmp.name, self.wid, hashlib.sha256(raw).hexdigest())

    def test_symlink_receipt_fails(self):
        target = self.root / "safe-target.json"
        target.write_bytes(self.path.read_bytes())
        self.path.unlink()
        try:
            self.path.symlink_to(target)
        except OSError:
            self.skipTest("symlinks unavailable")
        status, data = self.call_cli()
        self.assertEqual(status, 3)
        self.assertIn(data["reason"], {"UNSAFE_RECEIPT_FILE", "RECEIPT_NOT_READABLE"})

    def test_no_reply_content_in_error(self):
        self.path.unlink()
        status, data = self.call_cli()
        self.assertEqual(status, 3)
        self.assertFalse(data["independent_receiver_ack"])
        self.assertNotIn("synthetic private-shaped output", json.dumps(data))

    def test_root_is_not_untrusted_symlink(self):
        link = self.root.parent / (self.root.name + "-link")
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks unavailable")
        try:
            with self.assertRaisesRegex(ValueError, "UNBOUND_RECEIPT_ROOT"):
                readback(str(link), self.wid, self.sha)
        finally:
            link.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
