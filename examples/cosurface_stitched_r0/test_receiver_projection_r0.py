"""CoOrb projection adapter for the existing synthetic WorkID file handoff.

This validates actual source/effect/readback bytes written by the distinct test
processes. It does not authenticate a receiver identity or connect to X2.
"""
import hashlib
import json
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory

from test_workid_process_handoff import child


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def receipt_projection(root):
    """Fail-closed projection; never promote an incomplete readback to verified."""
    root = Path(root)
    result = {
        "schema": "CoOrb.ReceiverProjection.R0",
        "boundary": "LOCAL_TWO_PROCESS_SYNTHETIC",
        "work_id": None,
        "source_sha256": None,
        "status": "UNVERIFIED",
        "reason": "RECEIVER_READBACK_NOT_PRESENT",
        "live_receiver_proven": False,
        "x2_runtime_proven": False,
    }
    try:
        source_bytes = (root / "source.json").read_bytes()
        intent_bytes = (root / "intent.json").read_bytes()
        effect_bytes = (root / "receiver-effect.json").read_bytes()
        receipt_bytes = (root / "receiver-readback.json").read_bytes()
        source = json.loads(source_bytes)
        intent = json.loads(intent_bytes)
        effect = json.loads(effect_bytes)
        receipt = json.loads(receipt_bytes)
        work_id = source.get("work_id")
        result["work_id"] = work_id
        result["source_sha256"] = sha256(source_bytes)
        if not work_id or any(
            item.get("work_id") != work_id for item in (intent, effect, receipt)
        ):
            raise ValueError("WORK_ID_MISMATCH")
        if not all(item.get("schema") == "CoAll.WorkID.ProcessHandoff.R0"
                   for item in (source, intent, effect, receipt)):
            raise ValueError("SCHEMA_MISMATCH")
        if intent.get("source_sha256") != sha256(source_bytes):
            raise ValueError("INTENT_SOURCE_MISMATCH")
        if effect.get("source_sha256") != sha256(source_bytes):
            raise ValueError("EFFECT_SOURCE_MISMATCH")
        if receipt.get("source_sha256") != sha256(source_bytes):
            raise ValueError("RECEIPT_SOURCE_MISMATCH")
        if receipt.get("effect_sha256") != sha256(effect_bytes):
            raise ValueError("RECEIPT_EFFECT_MISMATCH")
        if receipt.get("receiver_role") != "INDEPENDENT_TEST_PROCESS":
            raise ValueError("UNQUALIFIED_RECEIVER_ROLE")
        if effect.get("effect") != "SYNTHETIC_EFFECT_ONLY":
            raise ValueError("UNQUALIFIED_EFFECT")
        result["status"] = "SYNTHETIC_RECEIVER_READBACK_CONFIRMED"
        result["reason"] = "EXACT_LOCAL_BYTES_MATCHED"
    except FileNotFoundError:
        pass
    except (ValueError, UnicodeDecodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        result["reason"] = str(exc) or "INVALID_RECEIPT"
    return result


class ReceiverProjectionTests(unittest.TestCase):
    def test_missing_receiver_stays_unverified(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(child("producer", root).returncode, 0)
            p = receipt_projection(root)
            self.assertEqual(p["status"], "UNVERIFIED")
            self.assertEqual(p["reason"], "RECEIVER_READBACK_NOT_PRESENT")

    def test_receiver_exact_readback_is_synthetic_only(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(child("producer", root).returncode, 0)
            self.assertEqual(child("receiver", root).returncode, 0)
            p = receipt_projection(root)
            self.assertEqual(p["status"], "SYNTHETIC_RECEIVER_READBACK_CONFIRMED")
            self.assertEqual(p["work_id"], "fixture-work-1")
            self.assertFalse(p["live_receiver_proven"])
            self.assertFalse(p["x2_runtime_proven"])

    def test_effect_tampering_cannot_green_orb(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(child("producer", root).returncode, 0)
            self.assertEqual(child("receiver", root).returncode, 0)
            # Preserve WorkID and source relation; mutate only the bytes that
            # the receiver's effect digest is supposed to authenticate.
            effect_file = root / "receiver-effect.json"
            effect = json.loads(effect_file.read_bytes())
            effect["effect"] = "TAMPERED_EFFECT"
            effect_file.write_text(json.dumps(effect), encoding="utf-8")
            p = receipt_projection(root)
            self.assertEqual(p["status"], "UNVERIFIED")
            self.assertEqual(p["reason"], "RECEIPT_EFFECT_MISMATCH")

    def test_source_tampering_cannot_green_orb(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(child("producer", root).returncode, 0)
            self.assertEqual(child("receiver", root).returncode, 0)
            (root / "source.json").write_bytes(b'{"work_id":"altered"}')
            p = receipt_projection(root)
            self.assertEqual(p["status"], "UNVERIFIED")

    def test_fake_receiver_label_cannot_green_orb(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(child("producer", root).returncode, 0)
            self.assertEqual(child("receiver", root).returncode, 0)
            f = root / "receiver-readback.json"
            receipt = json.loads(f.read_bytes())
            receipt["receiver_role"] = "CLAIMED_EXTERNAL_AI"
            f.write_text(json.dumps(receipt), encoding="utf-8")
            p = receipt_projection(root)
            self.assertEqual(p["status"], "UNVERIFIED")
            self.assertEqual(p["reason"], "UNQUALIFIED_RECEIVER_ROLE")


if __name__ == "__main__":
    unittest.main()
