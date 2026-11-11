#!/usr/bin/env python3
"""Synthetic, source-bound Narrative-to-WorkID replay and cold readback R0.

Creates one durable SQLite record for repeated source-bound CoLatch events. This
is not chat extraction, a real gesture, user consent, a worker, or external ACK.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

SCHEMA = "CoAll.CoNarrativeWorkID.R0"
WORK_ID = "CoPre.ReadyCycle.Synthetic.R0"
SHA1 = re.compile(r"^[a-f0-9]{40}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
FIELDS = frozenset({"schema", "work_id", "source_ref", "source_sha256",
    "narrative_summary", "prior_decisions", "open_blockers", "next_safe_deed",
    "privacy", "consent", "consent_epoch", "lease_epoch"})
NONCLAIMS = ["NOT_CHAT_CAPTURED", "NOT_REAL_MOUSE", "NOT_HUMAN_CONSENT",
    "NO_AUTONOMOUS_WORKER", "NO_EXTERNAL_RECEIVER_ACK", "NO_24H_PROOF",
    "NOT_DEPLOYED", "SAME_GITHUB_PROVIDER_FAILURE_DOMAIN"]


class Held(ValueError):
    pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def require(condition, reason):
    if not condition:
        raise Held(reason)


def source_packet(path, commit):
    path = Path(path)
    require(path.name == "CoPre.md" and not path.is_symlink() and path.is_file(), "SOURCE_NOT_PINNED_COPRE")
    require(isinstance(commit, str) and SHA1.fullmatch(commit), "SOURCE_COMMIT_REQUIRED")
    raw = path.read_bytes()
    require(0 < len(raw) <= 131072, "SOURCE_SIZE_UNSAFE")
    return {
        "schema": SCHEMA,
        "work_id": WORK_ID,
        "source_ref": "CoCivium/CoCivium:CoPre.md@" + commit,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "narrative_summary": "Recover the public CoPre Ready Cycle as one bounded work object; repeated assent is not a new task.",
        "prior_decisions": ["Reuse CoPre source", "One elected writer", "Independent challenges are nonauthoritative"],
        "open_blockers": ["External receiver unverified", "24-hour survival unverified", "Human-time benefit unmeasured"],
        "next_safe_deed": "Verify one independent receiver without requiring a human to relay narrative.",
        "privacy": "PUBLIC_SYNTHETIC", "consent": "SYNTHETIC_TEST_ONLY",
        "consent_epoch": 1, "lease_epoch": 1,
    }


def validate(packet):
    require(isinstance(packet, dict) and set(packet) == FIELDS and packet["schema"] == SCHEMA,
            "PACKET_SCHEMA_OR_FIELDS_INVALID")
    require(packet["work_id"] == WORK_ID, "WORK_ID_UNBOUND")
    require(isinstance(packet["source_ref"], str) and
            re.fullmatch(r"CoCivium/CoCivium:CoPre\.md@[a-f0-9]{40}", packet["source_ref"]),
            "SOURCE_REF_NOT_PINNED")
    require(isinstance(packet["source_sha256"], str) and SHA256.fullmatch(packet["source_sha256"]),
            "SOURCE_SHA256_INVALID")
    require(packet["privacy"] == "PUBLIC_SYNTHETIC" and packet["consent"] == "SYNTHETIC_TEST_ONLY",
            "PRIVACY_OR_CONSENT_HELD")
    require(type(packet["consent_epoch"]) is int and packet["consent_epoch"] == 1 and
            type(packet["lease_epoch"]) is int and packet["lease_epoch"] == 1,
            "EPOCH_NOT_APPROVED")
    for field in ("narrative_summary", "next_safe_deed"):
        require(isinstance(packet[field], str) and 1 <= len(packet[field]) <= 240,
                "INVALID_NARRATIVE_FIELD")
    for field in ("prior_decisions", "open_blockers"):
        values = packet[field]
        require(isinstance(values, list) and len(values) <= 8 and
                all(isinstance(v, str) and 1 <= len(v) <= 160 for v in values),
                "INVALID_NARRATIVE_LIST")
    return digest(packet)


def connect(db_path, readonly=False):
    path = Path(db_path)
    require(not path.is_symlink(), "SYMLINK_DB_DENIED")
    if not readonly:
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        require(path.is_file(), "MISSING_DURABLE_RECORD")
    conn = sqlite3.connect(f"file:{path.resolve()}?mode=ro" if readonly else str(path),
                           uri=readonly, timeout=4.0)
    conn.row_factory = sqlite3.Row
    if not readonly:
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("CREATE TABLE IF NOT EXISTS work ("
                     "work_id TEXT PRIMARY KEY, packet_json TEXT NOT NULL,"
                     "packet_sha256 TEXT NOT NULL, receipt_json TEXT NOT NULL,"
                     "state TEXT NOT NULL, lease_epoch INTEGER NOT NULL)")
    return conn


def make_receipt(packet, packet_sha):
    receipt = {
        "schema": SCHEMA + ".Receipt", "state": "COMMITTED_SYNTHETIC_LOCAL",
        "work_id": packet["work_id"], "source_ref": packet["source_ref"],
        "source_sha256": packet["source_sha256"], "packet_sha256": packet_sha,
        "commit_sequence": 1, "actual_external_effects": 0,
        "receiver_ack": False, "authority": "SYNTHETIC_ONLY",
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def commit_once(db_path, packet, fault=None):
    """Exactly one durable local insert. Fault injection simulates lost ACK."""
    packet_sha = validate(packet)
    require(fault in {None, "BEFORE_COMMIT", "AFTER_COMMIT"}, "FAULT_NOT_ALLOWED")
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM work WHERE work_id=?", (packet["work_id"],)).fetchone()
        if row is not None:
            require(row["state"] == "ACTIVE", "HELD_REVOKED")
            require(row["packet_sha256"] == packet_sha, "WORK_ID_REVISION_CONFLICT")
            require(row["lease_epoch"] == packet["lease_epoch"], "STALE_LEASE")
            receipt = json.loads(row["receipt_json"])
            conn.commit()
            return {"new_commits": 0, "duplicate": True, "receipt": receipt}
        if fault == "BEFORE_COMMIT":
            conn.rollback()
            raise Held("INJECTED_BEFORE_COMMIT")
        receipt = make_receipt(packet, packet_sha)
        conn.execute("INSERT INTO work VALUES (?,?,?,?,?,?)",
                     (packet["work_id"], canonical(packet), packet_sha,
                      canonical(receipt), "ACTIVE", packet["lease_epoch"]))
        conn.commit()
        if fault == "AFTER_COMMIT":
            raise Held("INJECTED_AFTER_COMMIT_ACK_LOST")
        return {"new_commits": 1, "duplicate": False, "receipt": receipt}
    except (ValueError, sqlite3.Error):
        conn.rollback()
        raise
    finally:
        conn.close()


def revoke(db_path, packet, *, expected_lease=1):
    """Synthetic-only revocation; old packets remain addressable but ineligible."""
    packet_sha = validate(packet)
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM work WHERE work_id=?", (packet["work_id"],)).fetchone()
        require(row is not None and row["packet_sha256"] == packet_sha, "REVOKE_SOURCE_MISMATCH")
        require(row["state"] == "ACTIVE" and row["lease_epoch"] == expected_lease,
                "REVOKE_STALE_LEASE")
        conn.execute("UPDATE work SET state='REVOKED',lease_epoch=? WHERE work_id=?",
                     (expected_lease + 1, packet["work_id"]))
        conn.commit()
    except (ValueError, sqlite3.Error):
        conn.rollback()
        raise
    finally:
        conn.close()


def readback(db_path, *, expected_packet=None, source_path=None):
    """Cold, read-only verification; integrity is not a cryptographic identity proof."""
    conn = connect(db_path, readonly=True)
    try:
        rows = conn.execute("SELECT * FROM work").fetchall()
        require(len(rows) == 1, "NOT_EXACTLY_ONE_WORKID")
        row = rows[0]
        packet, receipt = json.loads(row["packet_json"]), json.loads(row["receipt_json"])
        sha = validate(packet)
        require(row["packet_sha256"] == sha, "PACKET_DIGEST_MISMATCH")
        require(receipt == make_receipt(packet, sha), "RECEIPT_INTEGRITY_FAIL")
        require(row["work_id"] == WORK_ID, "WORK_ID_CHANGED")
        if expected_packet is not None:
            require(packet == expected_packet, "COLD_READER_SOURCE_MISMATCH")
        if source_path is not None:
            p = Path(source_path)
            require(p.name == "CoPre.md" and p.is_file() and not p.is_symlink(), "SOURCE_UNREADABLE")
            require(hashlib.sha256(p.read_bytes()).hexdigest() == packet["source_sha256"],
                    "SOURCE_NO_LONGER_MATCHES")
        state = "HELD_REVOKED" if row["state"] == "REVOKED" else "COLD_SOURCE_RECONSTRUCTED"
        require(row["state"] in {"ACTIVE", "REVOKED"}, "INVALID_RECORD_STATE")
        return {"schema": SCHEMA + ".Readback", "state": state, "work_id": WORK_ID,
                "source_ref": packet["source_ref"], "source_sha256": packet["source_sha256"],
                "packet_sha256": sha, "receipt_sha256": receipt["receipt_sha256"],
                "narrative_summary": packet["narrative_summary"],
                "prior_decisions": packet["prior_decisions"], "open_blockers": packet["open_blockers"],
                "next_safe_deed": packet["next_safe_deed"] if row["state"] == "ACTIVE" else None,
                "committed_work_ids": len(rows), "committed_effects": 1,
                "local_replay_only": True, "external_receiver_ack": False,
                "live_mouse_binding": False, "independent_provider": False,
                "nonclaims": NONCLAIMS}
    finally:
        conn.close()


def create_report(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as file:
        json.dump(obj, file, sort_keys=True, indent=2)
        file.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ("produce", "verify"):
        p = sub.add_parser(cmd)
        p.add_argument("--db", required=True)
        p.add_argument("--source", required=True)
        p.add_argument("--source-commit", required=True)
        p.add_argument("--report", required=True)
    args = parser.parse_args(argv)
    packet = source_packet(args.source, args.source_commit)
    if args.command == "produce":
        rounds = [commit_once(args.db, packet) for _ in range(10)]
        require(sum(x["new_commits"] for x in rounds) == 1 and
                sum(x["duplicate"] for x in rounds) == 9, "REPLAY_GATE_FAIL")
        result = {"schema": SCHEMA + ".ProducerProof", "events": 10,
                  "committed_work_ids": 1, "committed_effects": 1,
                  "duplicates_suppressed": 9,
                  "readback": readback(args.db, expected_packet=packet, source_path=args.source)}
    else:
        result = {"schema": SCHEMA + ".ColdReaderProof",
                  "independent_process": True, "same_provider_failure_domain": True,
                  "readback": readback(args.db, expected_packet=packet, source_path=args.source)}
    create_report(args.report, result)
    print(canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
