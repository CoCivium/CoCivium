#!/usr/bin/env python3
"""Offline, synthetic-only tests for the real browser packet -> SQLite adapter."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoOwnedWorkSqliteBridgeR0 import (
    BROWSER_SCHEMA, Held, adapt, apply_browser_revocation, node_fixture, run,
)
from CoNarrativeWorkIDR0 import commit_once, readback, revoke

JS = ROOT / "examples/conodcothumb/context_rail_r1/CoOwnedWorkR0.js"
GATE = ROOT / "tests/fixtures/ownedwork_synthetic_gate_r0.json"
SOURCE = Path(os.environ["COPRE_PINNED_SOURCE"])


class SyntheticBridgeR0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = node_fixture(JS)
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))

    def record(self):
        return {
            "schema": BROWSER_SCHEMA + ".Record",
            "packet": copy.deepcopy(self.fixture),
            "state": "ACTIVE", "commit_sequence": 1,
            "receiver_ack": False, "source_verified_by_browser": False,
        }

    def accepted(self, record=None, gate=None, source=None):
        return adapt(record if record is not None else self.record(),
                     gate if gate is not None else self.gate,
                     source if source is not None else SOURCE, JS)

    def held(self, record=None, gate=None, source=None):
        with self.assertRaises(Held):
            self.accepted(record, gate, source)

    def test_exact_narrative_and_explicit_consent_epoch(self):
        r = self.record()
        p = self.accepted(r)
        self.assertEqual(p["consent_epoch"], 1)
        self.assertEqual(p["lease_epoch"], 1)
        for key in ("narrative_summary", "prior_decisions",
                    "open_blockers", "next_safe_deed"):
            self.assertEqual(p[key], r["packet"][key])
        self.assertEqual(p["privacy"], "PUBLIC_SYNTHETIC")

    def test_missing_stale_or_forged_gate_is_held(self):
        for name, value in (("consent_epoch", 0), ("consent_epoch", 2),
                            ("actor", "UNAUTHORIZED"), ("permission", "REAL_WRITE"),
                            ("source_commit", "0"*40), ("scope", "PRIVATE")):
            gate = dict(self.gate, **{name: value})
            with self.subTest(field=name, value=value):
                self.held(gate=gate)
        gate = dict(self.gate)
        del gate["consent_epoch"]
        self.held(gate=gate)

    def test_browser_state_ack_and_schema_are_held(self):
        for name, value in (("state", "REVOKED"), ("receiver_ack", True),
                            ("source_verified_by_browser", True),
                            ("commit_sequence", 2),
                            ("schema", "OTHER")):
            rec = self.record()
            rec[name] = value
            with self.subTest(field=name):
                self.held(record=rec)

    def test_silent_narrative_rewrite_is_held(self):
        for field in ("narrative_summary", "prior_decisions",
                      "open_blockers", "next_safe_deed"):
            rec = self.record()
            rec["packet"][field] = "altered" if isinstance(
                rec["packet"][field], str) else ["altered"]
            with self.subTest(field=field):
                self.held(record=rec)

    def test_wrong_source_or_privacy_is_held(self):
        rec = self.record()
        rec["packet"]["source_sha256"] = "0"*64
        self.held(record=rec)
        rec = self.record()
        rec["packet"]["privacy"] = "PRIVATE"
        self.held(record=rec)
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d) / "CoPre.md"
            fake.write_bytes(SOURCE.read_bytes() + b"\ntampered")
            self.held(source=fake)

    def test_duplicate_lost_ack_revocation_and_replay_denial(self):
        packet = self.accepted()
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "test.sqlite"
            with self.assertRaisesRegex(Held, "INJECTED_AFTER_COMMIT_ACK_LOST"):
                commit_once(db, packet, fault="AFTER_COMMIT")
            repeat = commit_once(db, packet)
            self.assertEqual(repeat["new_commits"], 0)
            self.assertTrue(repeat["duplicate"])
            cold = readback(db, expected_packet=packet, source_path=SOURCE)
            self.assertEqual(cold["committed_work_ids"], 1)
            self.assertFalse(cold["external_receiver_ack"])
            revoke(db, packet)
            self.assertEqual(readback(db, expected_packet=packet)["state"],
                             "HELD_REVOKED")
            with self.assertRaisesRegex(Held, "HELD_REVOKED"):
                commit_once(db, packet)

    def test_converged_artifact_one_commit_and_fail_closed_no_clobber(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            inp = root / "browser-record.json"
            inp.write_text(json.dumps(self.record()), encoding="utf-8")
            out = root / "handoff"
            proof = run(inp, GATE, SOURCE, JS, out)
            self.assertEqual(proof["local_commits"], 1)
            self.assertEqual(proof["duplicate_suppressed"], 1)
            self.assertFalse(proof["receiver_ack"])
            self.assertTrue(proof["narrative_fields_preserved"])
            self.assertEqual(proof["receiver_readback"]["committed_work_ids"], 1)
            with self.assertRaisesRegex(Held, "HELD_OUTPUT_EXISTS_NO_CLOBBER"):
                run(inp, GATE, SOURCE, JS, out)


    def test_exact_browser_origin_revocation_crosses_sqlite_boundary(self):
        active = self.record()
        revoked = {**active, "state": "REVOKED"}
        packet = self.accepted(active)
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "receiver.sqlite"
            commit_once(db, packet)
            proof = apply_browser_revocation(
                db, active, revoked, self.gate, SOURCE, JS)
            self.assertEqual(
                proof["state"],
                "SYNTHETIC_BROWSER_ORIGIN_REVOCATION_APPLIED_CI_ONLY")
            self.assertEqual(proof["before"], "COLD_SOURCE_RECONSTRUCTED")
            self.assertEqual(proof["after"], "HELD_REVOKED")
            self.assertFalse(proof["receiver_ack"])
            self.assertFalse(proof["real_human_consent"])
            self.assertFalse(proof["independent_sender_authentication"])
            self.assertEqual(
                readback(db, expected_packet=packet)["state"], "HELD_REVOKED")
            with self.assertRaisesRegex(Held, "HELD_REVOKED"):
                commit_once(db, packet)
            with self.assertRaisesRegex(Held, "HELD_RECEIVER_NOT_ACTIVE_FOR_REVOKE"):
                apply_browser_revocation(
                    db, active, revoked, self.gate, SOURCE, JS)

    def test_corrupt_revocation_and_stale_gate_leave_receiver_active(self):
        active = self.record()
        revoked = {**active, "state": "REVOKED"}
        packet = self.accepted(active)
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "receiver.sqlite"
            commit_once(db, packet)
            cases = (
                {"state": "ACTIVE"},
                {"commit_sequence": 2},
                {"receiver_ack": True},
                {"source_verified_by_browser": True},
                {"schema": "Other.Record"},
                {"packet": {**active["packet"], "lease_epoch": 2}},
                {"packet": {**active["packet"], "source_sha256": "0" * 64}},
                {"packet": {**active["packet"], "narrative_summary": "forged"}},
            )
            for mutation in cases:
                with self.subTest(mutation=mutation):
                    forged = {**revoked, **mutation}
                    with self.assertRaisesRegex(
                            Held, "HELD_REVOKE_NOT_SAME_BROWSER_RECORD"):
                        apply_browser_revocation(
                            db, active, forged, self.gate, SOURCE, JS)
                    self.assertEqual(
                        readback(db, expected_packet=packet)["state"],
                        "COLD_SOURCE_RECONSTRUCTED")
            for gate_mutation in (
                    {"consent_epoch": 2}, {"actor": "UNAUTHENTICATED"},
                    {"permission": "REAL_WRITE"}, {"source_commit": "0"*40}):
                with self.subTest(gate=gate_mutation):
                    with self.assertRaises(Held):
                        apply_browser_revocation(
                            db, active, revoked,
                            {**self.gate, **gate_mutation}, SOURCE, JS)
                    self.assertEqual(
                        readback(db, expected_packet=packet)["state"],
                        "COLD_SOURCE_RECONSTRUCTED")

    def test_revoke_from_different_browser_workid_denied(self):
        active = self.record()
        revoked = {**active, "state": "REVOKED",
                   "packet": {**active["packet"], "work_id": "other-work"}}
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "receiver.sqlite"
            packet = self.accepted(active)
            commit_once(db, packet)
            with self.assertRaisesRegex(
                    Held, "HELD_REVOKE_NOT_SAME_BROWSER_RECORD"):
                apply_browser_revocation(
                    db, active, revoked, self.gate, SOURCE, JS)
            self.assertEqual(
                readback(db, expected_packet=packet)["state"],
                "COLD_SOURCE_RECONSTRUCTED")


if __name__ == "__main__":
    unittest.main()
