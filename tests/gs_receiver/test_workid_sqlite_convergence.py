"""Synthetic convergence-to-SQLite integration, never an external receiver ACK.

Exercises the existing receiver implementation rather than a duplicate store.
Requires full Git history for immutable CoPre fixture bytes.
"""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

from workid_convergence import inspect_with_source
from workid_handoff_gate import WORK_ID, SOURCE_REF, SOURCE_SHA256
from workid_source_pin import EXPECTED_COMMIT

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "CoNarrativeWorkIDR0.py"


def receiver_module():
    spec = importlib.util.spec_from_file_location("conarrative_workid_r0", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_bytes():
    return subprocess.check_output(["git", "-C", str(REPO), "show",
                                    f"{EXPECTED_COMMIT}:CoPre.md"])


def proposal():
    return {
        "schema": "CoAll.CoOwnedWork.BrowserLocal.R0.Packet",
        "work_id": WORK_ID, "source_ref": SOURCE_REF,
        "source_sha256": SOURCE_SHA256,
        "narrative_summary": "Synthetic local convergence readback",
        "prior_decisions": [], "open_blockers": [],
        "next_safe_deed": "Inspect local synthetic receipt",
        "privacy": "PUBLIC_SYNTHETIC", "consent": "SYNTHETIC_TEST_ONLY",
        "lease_epoch": 1,
    }


def authorization():
    return {"scope": "PUBLIC_SYNTHETIC_HANDOFF",
            "source_ref": SOURCE_REF, "consent_epoch": 1}


class SyntheticSqliteConvergenceTests(unittest.TestCase):
    def test_proposal_commit_duplicate_cold_readback_and_revoke(self):
        receiver = receiver_module()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "CoPre.md"
            source.write_bytes(source_bytes())
            db = root / "synthetic.sqlite3"
            candidate = proposal()
            gate = inspect_with_source(candidate, authorization(), source)
            self.assertEqual(gate["state"], "PROPOSAL_SOURCE_BYTES_MATCHED_ONLY")
            self.assertFalse(gate["receiver_ack"])
            # Explicit schema boundary: receiver's local-only packet has an
            # additional consent_epoch and a different schema identifier.
            packet = dict(candidate, schema=receiver.SCHEMA, consent_epoch=1)
            self.assertEqual(set(packet), receiver.FIELDS)
            self.assertEqual(receiver.validate(packet), receiver.digest(packet))
            first = receiver.commit_once(db, packet)
            second = receiver.commit_once(db, packet)
            self.assertEqual((first["new_commits"], second["new_commits"]), (1, 0))
            self.assertTrue(second["duplicate"])
            self.assertEqual(first["receipt"], second["receipt"])
            self.assertFalse(first["receipt"]["receiver_ack"])
            cold = receiver.readback(db, expected_packet=packet, source_path=source)
            self.assertEqual(cold["state"], "COLD_SOURCE_RECONSTRUCTED")
            self.assertEqual(cold["committed_work_ids"], 1)
            self.assertFalse(cold["external_receiver_ack"])
            receiver.revoke(db, packet)
            revoked = receiver.readback(db, expected_packet=packet, source_path=source)
            self.assertEqual(revoked["state"], "HELD_REVOKED")
            self.assertIsNone(revoked["next_safe_deed"])
            with self.assertRaises(receiver.Held):
                receiver.commit_once(db, packet)

    def test_lost_ack_recovers_without_second_commit(self):
        receiver = receiver_module()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "CoPre.md"
            source.write_bytes(source_bytes())
            db = root / "synthetic.sqlite3"
            candidate = proposal()
            gate = inspect_with_source(candidate, authorization(), source)
            self.assertEqual(gate["state"], "PROPOSAL_SOURCE_BYTES_MATCHED_ONLY")
            packet = dict(candidate, schema=receiver.SCHEMA, consent_epoch=1)
            with self.assertRaisesRegex(receiver.Held, "INJECTED_AFTER_COMMIT_ACK_LOST"):
                receiver.commit_once(db, packet, fault="AFTER_COMMIT")
            cold = receiver.readback(db, expected_packet=packet, source_path=source)
            self.assertEqual(cold["state"], "COLD_SOURCE_RECONSTRUCTED")
            self.assertEqual(cold["committed_work_ids"], 1)
            self.assertFalse(cold["external_receiver_ack"])
            replay = receiver.commit_once(db, packet)
            self.assertEqual(replay["new_commits"], 0)
            self.assertTrue(replay["duplicate"])
            self.assertEqual(replay["receipt"]["receipt_sha256"], cold["receipt_sha256"])


    def test_held_source_does_not_create_sqlite_record(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "CoPre.md"
            source.write_bytes(b"wrong source")
            db = root / "synthetic.sqlite3"
            result = inspect_with_source(proposal(), authorization(), source)
            self.assertEqual(result["state"], "HELD_SOURCE_PROOF")
            self.assertFalse(db.exists())


    def test_held_authorization_or_epoch_cannot_create_record(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "CoPre.md"
            source.write_bytes(source_bytes())
            db = root / "synthetic.sqlite3"
            cases = [
                (proposal(), None, "HELD_AUTHORIZATION"),
                (proposal(), {"scope": "PUBLIC_SYNTHETIC_HANDOFF",
                              "source_ref": SOURCE_REF, "consent_epoch": 2},
                 "HELD_AUTHORIZATION"),
                (dict(proposal(), lease_epoch=2), authorization(), "HELD_EPOCH"),
                (dict(proposal(), consent="REAL_USER_CONSENT"), authorization(),
                 "HELD_SCOPE"),
            ]
            for packet, auth, expected in cases:
                with self.subTest(expected=expected):
                    result = inspect_with_source(packet, auth, source)
                    self.assertEqual(result["state"], expected)
                    self.assertFalse(db.exists())


if __name__ == "__main__":
    unittest.main()
