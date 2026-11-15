"""One WorkID, two distinct Python processes, durable source and receiver readproof.

Synthetic file-backed contract only. No X2 service, network, model, OS control,
authorization token or real cross-provider integration is implemented here.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve()
SCHEMA = "CoAll.WorkID.ProcessHandoff.R0"


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    temp = path.with_name(path.name + ".pending")
    with open(temp, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def produce(root, *, work_id, payload):
    """Separate producer process creates exact source and source-bound intent."""
    root.mkdir(parents=True, exist_ok=True)
    source = encoded({"work_id": work_id, "payload": payload, "schema": SCHEMA})
    atomic_write(root / "source.json", source)
    intent = encoded({"work_id": work_id, "source_sha256": digest(source),
                      "schema": SCHEMA, "requested_effect": "WRITE_SYNTHETIC_RECEIPT"})
    atomic_write(root / "intent.json", intent)


def receive(root):
    """Independent receiver process validates exact source before one effect."""
    intent = json.loads((root / "intent.json").read_bytes())
    source_bytes = (root / "source.json").read_bytes()
    source = json.loads(source_bytes)
    if intent["schema"] != SCHEMA or source["schema"] != SCHEMA:
        raise ValueError("schema mismatch")
    if digest(source_bytes) != intent["source_sha256"]:
        raise ValueError("source hash mismatch")
    if source["work_id"] != intent["work_id"]:
        raise ValueError("WorkID mismatch")
    if intent["requested_effect"] != "WRITE_SYNTHETIC_RECEIPT":
        raise ValueError("unapproved effect type")

    # Receiver owns this single synthetic effect. No second payload mutation.
    effect_path = root / "receiver-effect.json"
    effect = encoded({"work_id": intent["work_id"], "source_sha256": digest(source_bytes),
                      "effect": "SYNTHETIC_EFFECT_ONLY", "schema": SCHEMA})
    if effect_path.exists():
        if effect_path.read_bytes() != effect:
            raise ValueError("conflicting existing effect")
    else:
        # A single elected receiver is assumed; multi-writer locking/fencing
        # is NOT proven by this test and must be implemented separately.
        atomic_write(effect_path, effect)
    receipt = encoded({"receiver_role": "INDEPENDENT_TEST_PROCESS",
                       "effect_sha256": digest(effect_path.read_bytes()),
                       "work_id": intent["work_id"], "source_sha256": digest(source_bytes),
                       "schema": SCHEMA})
    atomic_write(root / "receiver-readback.json", receipt)


def verify(root, *, expected_work_id):
    """Test orchestrator independently reads files after receiver process exits."""
    source = (root / "source.json").read_bytes()
    effect = (root / "receiver-effect.json").read_bytes()
    receipt = json.loads((root / "receiver-readback.json").read_bytes())
    if (receipt["schema"] != SCHEMA
            or receipt["work_id"] != expected_work_id
            or receipt["source_sha256"] != digest(source)
            or receipt["effect_sha256"] != digest(effect)
            or json.loads(effect)["work_id"] != expected_work_id):
        raise ValueError("independent readback mismatch")
    return {"work_id": expected_work_id, "effect_sha256": digest(effect),
            "classification": "TWO_PROCESS_SYNTHETIC_READBACK"}


def child(role, root):
    return subprocess.run([sys.executable, str(HERE), "--child", role, str(root)],
                          capture_output=True, text=True, timeout=15)


class TwoProcessHandoffTests(unittest.TestCase):
    def test_producer_receiver_two_processes_with_interruption(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            a = child("producer", root)
            self.assertEqual(a.returncode, 0, a.stderr)
            self.assertFalse((root / "receiver-readback.json").exists())
            # The producer is gone before independent receiver starts.
            b = child("receiver", root)
            self.assertEqual(b.returncode, 0, b.stderr)
            first = verify(root, expected_work_id="fixture-work-1")
            # Recovery/replayed delivery must not produce another effect.
            c = child("receiver", root)
            self.assertEqual(c.returncode, 0, c.stderr)
            self.assertEqual(first, verify(root, expected_work_id="fixture-work-1"))

    def test_tampered_source_fails_before_effect(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(child("producer", root).returncode, 0)
            (root / "source.json").write_text('{"tampered":true}', encoding="utf-8")
            result = child("receiver", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "receiver-effect.json").exists())

    def test_wrong_work_id_rejected_on_readback(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(child("producer", root).returncode, 0)
            self.assertEqual(child("receiver", root).returncode, 0)
            with self.assertRaises(ValueError):
                verify(root, expected_work_id="other-work")

    def test_receiver_absence_never_counts_as_pickup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(child("producer", root).returncode, 0)
            with self.assertRaises(FileNotFoundError):
                verify(root, expected_work_id="fixture-work-1")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--child":
        role, root = sys.argv[2], Path(sys.argv[3])
        if role == "producer":
            produce(root, work_id="fixture-work-1", payload={"value": 7})
        elif role == "receiver":
            receive(root)
        else:
            raise SystemExit("invalid role")
    else:
        unittest.main()
