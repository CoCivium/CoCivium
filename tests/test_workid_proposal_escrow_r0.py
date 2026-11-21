#!/usr/bin/env python3
"""PUBLIC_SYNTHETIC-only rejection escrow test for incumbent CoNarrative SQLite.

This is a TEST-LOCAL reference table in the SAME receiver DB, not a product
API, authenticated proposal writer, separate service or independent receiver.
A losing WorkID revision must not exist only in its dying child process.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoNarrativeWorkIDR0 import (  # noqa: E402
    Held, canonical, commit_once, connect, digest, readback,
    source_packet, validate,
)

TABLE = "synthetic_proposal_escrow"
NAME = re.compile(r"^[a-z][a-z0-9_-]{0,39}$")


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Held(reason)


def escrow_once(db: Path, name: str, packet: dict) -> dict:
    """No accepted WorkID state is changed here. Fail closed, no overwrite."""
    sha = validate(packet)
    require(type(name) is str and NAME.fullmatch(name) is not None,
            "HELD_ESCROW_PROPOSAL_ID")
    require(packet["privacy"] == "PUBLIC_SYNTHETIC" and
            packet["consent"] == "SYNTHETIC_TEST_ONLY",
            "HELD_ESCROW_SCOPE")
    conn = connect(db)
    try:
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS synthetic_proposal_escrow ("
            "proposal_id TEXT PRIMARY KEY, work_id TEXT NOT NULL, "
            "packet_sha TEXT NOT NULL, packet_json TEXT NOT NULL, "
            "state TEXT NOT NULL CHECK(state='PRESERVED_NOT_ELECTED'))"
        )
        prior = conn.execute(
            f"SELECT * FROM {TABLE} WHERE proposal_id=?", (name,)
        ).fetchone()
        if prior is not None:
            require(prior["packet_sha"] == sha and
                    prior["packet_json"] == canonical(packet),
                    "HELD_DIVERGENT_PROPOSAL_ID_NO_OVERWRITE")
            conn.commit()
            return {"new": False, "proposal_sha256": sha, "receiver_ack": False}
        conn.execute(
            f"INSERT INTO {TABLE} VALUES (?,?,?,?,?)",
            (name, packet["work_id"], sha, canonical(packet),
             "PRESERVED_NOT_ELECTED"),
        )
        conn.commit()
        return {"new": True, "proposal_sha256": sha, "receiver_ack": False}
    except (sqlite3.Error, ValueError):
        conn.rollback()
        raise
    finally:
        conn.close()


def cold_read(db: Path) -> list[dict]:
    """Independent process may read the two originals, not accept either."""
    conn = connect(db, readonly=True)
    try:
        rows = conn.execute(
            f"SELECT * FROM {TABLE} ORDER BY proposal_id"
        ).fetchall()
        out = []
        for row in rows:
            try:
                packet = json.loads(row["packet_json"])
            except ValueError as exc:
                raise Held("HELD_ESCROW_ROW_JSON") from exc
            require(row["packet_json"] == canonical(packet),
                    "HELD_ESCROW_ROW_NONCANONICAL")
            require(row["packet_sha"] == validate(packet) and
                    row["work_id"] == packet["work_id"] and
                    row["state"] == "PRESERVED_NOT_ELECTED",
                    "HELD_ESCROW_ROW_TAMPER_OR_WRONG_STATE")
            out.append({"proposal_id": row["proposal_id"],
                        "packet_sha256": row["packet_sha"],
                        "next_safe_deed": packet["next_safe_deed"],
                        "state": "PRESERVED_NOT_ELECTED",
                        "receiver_ack": False})
        return out
    finally:
        conn.close()


def child(mode: str, db: Path, packet_file: Path) -> None:
    if mode == "crash_before_escrow":
        os._exit(81)
    assert mode.startswith("commit_and_crash_")
    name = mode.removeprefix("commit_and_crash_")
    packet = json.loads(packet_file.read_text(encoding="utf-8"))
    escrow_once(db, name, packet)
    os._exit(82)  # deliberately no final reply / finally / graceful exit


class SuddenDeathTwoWriterEscrow(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="cocivium-escrow-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "receiver.sqlite"
        source = self.root / "CoPre.md"
        source.write_text("PUBLIC SYNTHETIC fixture only.\n", encoding="utf-8")
        self.left = source_packet(source, "a" * 40)
        self.left["next_safe_deed"] = "Synthetic proposal A: preserve the durable source first."
        self.right = {**self.left,
                      "next_safe_deed": "Synthetic proposal B: preserve the other source too."}
        self.assertNotEqual(digest(self.left), digest(self.right))

    def save_packet(self, name: str, packet: dict) -> Path:
        path = self.root / (name + ".json")
        path.write_text(canonical(packet), encoding="utf-8")
        return path

    def run_child(self, mode: str, packet: dict | None = None) -> int:
        path = self.save_packet(mode, packet or self.left)
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "child", mode, str(self.db), str(path)],
                           timeout=12, check=False, capture_output=True)
        self.assertEqual(p.stdout, b"")
        return p.returncode

    def run_cold_reader(self) -> dict:
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "read", str(self.db)],
                           capture_output=True, text=True, timeout=12, check=True)
        return json.loads(p.stdout)

    def test_01_no_escrow_before_crash_is_unrecoverable(self):
        self.assertEqual(self.run_child("crash_before_escrow"), 81)
        self.assertFalse(self.db.exists())

    def test_02_left_escrow_survives_no_final_turn(self):
        self.assertEqual(self.run_child("commit_and_crash_left", self.left), 82)
        cold = self.run_cold_reader()
        self.assertEqual(cold["count"], 1)
        self.assertEqual(cold["proposals"][0]["next_safe_deed"],
                         self.left["next_safe_deed"])
        self.assertFalse(cold["receiver_ack"])

    def test_03_both_proposals_survive_loser_conflict_and_child_death(self):
        self.assertEqual(self.run_child("commit_and_crash_left", self.left), 82)
        self.assertEqual(self.run_child("commit_and_crash_right", self.right), 82)
        winner = commit_once(self.db, self.left)
        self.assertEqual(winner["new_commits"], 1)
        with self.assertRaisesRegex(Held, "WORK_ID_REVISION_CONFLICT"):
            commit_once(self.db, self.right)
        cold = self.run_cold_reader()
        self.assertEqual(cold["count"], 2)
        self.assertEqual({p["next_safe_deed"] for p in cold["proposals"]},
                         {self.left["next_safe_deed"], self.right["next_safe_deed"]})
        self.assertFalse(cold["receiver_ack"])
        accepted = readback(self.db, expected_packet=self.left)
        self.assertEqual(accepted["state"], "COLD_SOURCE_RECONSTRUCTED")
        self.assertEqual(accepted["committed_work_ids"], 1)
        self.assertFalse(accepted["external_receiver_ack"])

    def test_04_identical_retry_deduped_before_election(self):
        self.assertTrue(escrow_once(self.db, "left", self.left)["new"])
        self.assertFalse(escrow_once(self.db, "left", self.left)["new"])
        self.assertEqual(len(cold_read(self.db)), 1)

    def test_05_divergent_same_proposal_id_is_held_without_clobber(self):
        escrow_once(self.db, "left", self.left)
        with self.assertRaisesRegex(Held, "HELD_DIVERGENT_PROPOSAL_ID"):
            escrow_once(self.db, "left", self.right)
        self.assertEqual(cold_read(self.db)[0]["next_safe_deed"],
                         self.left["next_safe_deed"])

    def test_06_tampered_escrow_hash_is_held_not_elected(self):
        escrow_once(self.db, "left", self.left)
        con = sqlite3.connect(self.db)
        try:
            con.execute(f"UPDATE {TABLE} SET packet_sha=?", ("0" * 64,))
            con.commit()
        finally:
            con.close()
        with self.assertRaisesRegex(Held, "HELD_ESCROW_ROW_TAMPER"):
            cold_read(self.db)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "child":
        child(sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]))
    elif len(sys.argv) >= 3 and sys.argv[1] == "read":
        proposals = cold_read(Path(sys.argv[2]))
        print(json.dumps({"count": len(proposals), "proposals": proposals,
                          "receiver_ack": False}, sort_keys=True))
    else:
        unittest.main(verbosity=2)
