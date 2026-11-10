#!/usr/bin/env python3
"""Synthetic-only bridge from CoOwnedWorkR0 browser record to existing CoNarrativeWorkIDR0 SQLite.

Explicit files, no transport, no browser storage access, no claim of independent-provider ACK.
Preserves exact browser record separately from receiver's intentionally different narrative.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

from CoNarrativeWorkIDR0 import (
    Held, canonical, commit_once, connect, digest, readback as receiver_readback,
    revoke as receiver_revoke, source_packet,
)

SCHEMA = "CoCivium.CoPre.BrowserSQLiteEnvelope.R0"
RECORD_SCHEMA = "CoAll.CoOwnedWork.BrowserLocal.R0.Record"
PACKET_SCHEMA = "CoAll.CoOwnedWork.BrowserLocal.R0.Packet"
SOURCE_COMMIT = "63b41ead8797e5a781699f32bcbc77b78bdbd7af"
SOURCE_SHA256 = "58f8c722bfbfc34cac41189c072d2effe4b19dbbe8a37be4f8687344d6b00b9a"
SOURCE_REF = "CoCivium/CoCivium:CoPre.md@" + SOURCE_COMMIT
WORK_ID = "CoPre.ReadyCycle.Synthetic.R0"
COLUMNS = {"schema", "work_id", "source_ref", "source_sha256", "narrative_summary",
           "prior_decisions", "open_blockers", "next_safe_deed", "privacy", "consent", "lease_epoch"}
ENVELOPE_KEYS = {"schema", "intent", "work_id", "privacy", "consent_epoch",
                 "human_consent_proven", "external_receiver_ack", "external_effects",
                 "source_verified_by_browser", "browser_record", "handoff_id"}


def expected_browser_packet():
    # Exact public synthetic fixture from CoOwnedWorkR0.js at source blob 073cf764...
    return {
        "schema": PACKET_SCHEMA, "work_id": WORK_ID,
        "source_ref": SOURCE_REF, "source_sha256": SOURCE_SHA256,
        "narrative_summary": "Recover the public CoPre Ready Cycle as one bounded work object; repeated assent is not a new task.",
        "prior_decisions": ["Reuse existing CoPre source", "One elected writer",
                            "Independent challenges have no write authority"],
        "open_blockers": ["External receiver unverified", "24-hour survival unverified",
                          "Human-time benefit unmeasured"],
        "next_safe_deed": "Verify one independent receiver without requiring human narrative relay.",
        "privacy": "PUBLIC_SYNTHETIC", "consent": "SYNTHETIC_TEST_ONLY", "lease_epoch": 1,
    }


def expect(condition, message):
    if not condition:
        raise Held(message)


def source(path):
    p = Path(path)
    expect(p.name == "CoPre.md" and p.is_file() and not p.is_symlink(), "HOLD_SOURCE_FILE")
    data = p.read_bytes()
    expect(0 < len(data) <= 131072 and hashlib.sha256(data).hexdigest() == SOURCE_SHA256,
           "HOLD_SOURCE_HASH")
    out = source_packet(p, SOURCE_COMMIT)
    expect(out["source_ref"] == SOURCE_REF and out["source_sha256"] == SOURCE_SHA256,
           "HOLD_RECEIVER_SOURCE_PIN")
    return out


def validate_envelope(e):
    expect(type(e) is dict and set(e) == ENVELOPE_KEYS and e["schema"] == SCHEMA,
           "HOLD_ENVELOPE_FIELDS")
    intent = e["intent"]
    expect(intent in ("INGEST_SYNTHETIC", "REVOKE_SYNTHETIC"), "HOLD_INTENT")
    expect(e["work_id"] == WORK_ID and e["privacy"] == "PUBLIC_SYNTHETIC",
           "HOLD_WORK_SCOPE")
    expect(type(e["consent_epoch"]) is int and e["consent_epoch"] == 1 and
           e["human_consent_proven"] is False and e["external_receiver_ack"] is False and
           type(e["external_effects"]) is int and e["external_effects"] == 0 and
           e["source_verified_by_browser"] is False and
           e["handoff_id"] == "CoPre.ReadyCycle.Synthetic.BrowserToSQLite.R0",
           "HOLD_CONSENT_AUTHORITY_OR_EFFECT")
    row = e["browser_record"]
    expect(type(row) is dict and set(row) == {
           "schema", "packet", "state", "commit_sequence", "receiver_ack", "source_verified_by_browser"},
           "HOLD_BROWSER_RECORD_FIELDS")
    expected_state = "ACTIVE" if intent == "INGEST_SYNTHETIC" else "REVOKED"
    expect(row["schema"] == RECORD_SCHEMA and row["packet"] == expected_browser_packet()
           and row["state"] == expected_state and type(row["commit_sequence"]) is int
           and row["commit_sequence"] == 1 and row["receiver_ack"] is False and
           row["source_verified_by_browser"] is False, "HOLD_BROWSER_PACKET_OR_STATE")
    return digest(e)


def db_record(db):
    conn = connect(db, readonly=True)
    try:
        try:
            rows = conn.execute("SELECT * FROM copre_browser_handoff WHERE work_id=?", (WORK_ID,)).fetchall()
        except sqlite3.OperationalError as err:
            raise Held("HOLD_HANDOFF_MISSING") from err
        expect(len(rows) == 1, "HOLD_HANDOFF_CARDINALITY")
        return dict(rows[0])
    finally:
        conn.close()


def setup_table(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS copre_browser_handoff ("
                 "work_id TEXT PRIMARY KEY, active_sha256 TEXT NOT NULL,"
                 "active_envelope_json TEXT NOT NULL, browser_record_json TEXT NOT NULL,"
                 "state TEXT NOT NULL, revoke_sha256 TEXT)")


def active_of(revoked):
    e = json.loads(canonical(revoked))
    e["intent"] = "INGEST_SYNTHETIC"
    e["browser_record"]["state"] = "ACTIVE"
    validate_envelope(e)
    return e


def ingest(db, source_path, envelope):
    packet = source(source_path)
    active_sha = validate_envelope(envelope)
    expect(envelope["intent"] == "INGEST_SYNTHETIC", "HOLD_NOT_INGEST_INTENT")
    # Existing CoNarrativeWorkIDR0 is the only receiver/work ledger; leave it unchanged.
    receiver = commit_once(db, packet)
    conn = connect(db)
    try:
        conn.execute("BEGIN IMMEDIATE")
        setup_table(conn)
        row = conn.execute("SELECT * FROM copre_browser_handoff WHERE work_id=?", (WORK_ID,)).fetchone()
        if row:
            expect(row["state"] == "ACTIVE", "HOLD_BROWSER_REVOKED")
            expect(row["active_sha256"] == active_sha and
                   row["active_envelope_json"] == canonical(envelope) and
                   row["browser_record_json"] == canonical(envelope["browser_record"]),
                   "HOLD_BROWSER_REPLAY_CONFLICT")
            inserted = False
        else:
            conn.execute("INSERT INTO copre_browser_handoff VALUES (?,?,?,?,?,NULL)",
                         (WORK_ID, active_sha, canonical(envelope),
                          canonical(envelope["browser_record"]), "ACTIVE"))
            inserted = True
        conn.commit()
    except (Held, sqlite3.Error):
        conn.rollback()
        raise
    finally:
        conn.close()
    proof = cold_readback(db, source_path)
    expect(proof["state"] == "VERIFIED_SYNTHETIC_SAME_SQLITE_RECEIVER", "HOLD_COLD_RECONCILIATION")
    return {"status": proof["state"], "new_receiver_writes": receiver["new_commits"],
            "new_browser_ledger_rows": int(inserted), "proof": proof}


def revoke(db, source_path, envelope):
    packet = source(source_path)
    revoked_sha = validate_envelope(envelope)
    expect(envelope["intent"] == "REVOKE_SYNTHETIC", "HOLD_NOT_REVOKE_INTENT")
    active = active_of(envelope)
    row = db_record(db)
    expect(row["active_sha256"] == digest(active) and
           row["active_envelope_json"] == canonical(active) and
           row["browser_record_json"] == canonical(active["browser_record"]),
           "HOLD_REVOKE_PRIOR_MISMATCH")
    expect(row["state"] in ("ACTIVE", "REVOKED"), "HOLD_BAD_BRIDGE_STATE")
    if row["state"] == "REVOKED":
        expect(row["revoke_sha256"] == revoked_sha, "HOLD_REVOKE_REPLAY_CONFLICT")
    else:
        # A crash between receiver revoke and local bridge-mark can be resumed.
        r = receiver_readback(db, expected_packet=packet, source_path=source_path)
        if r["state"] != "HELD_REVOKED":
            expect(r["state"] == "COLD_SOURCE_RECONSTRUCTED", "HOLD_RECEIVER_STATE")
            receiver_revoke(db, packet)
        conn = connect(db)
        try:
            conn.execute("BEGIN IMMEDIATE")
            observed = conn.execute("SELECT * FROM copre_browser_handoff WHERE work_id=?",
                                    (WORK_ID,)).fetchone()
            expect(observed is not None and observed["active_sha256"] == digest(active)
                   and observed["state"] == "ACTIVE", "HOLD_REVOKE_CONFLICT")
            conn.execute("UPDATE copre_browser_handoff SET state='REVOKED', revoke_sha256=? "
                         "WHERE work_id=?", (revoked_sha, WORK_ID))
            conn.commit()
        except (Held, sqlite3.Error):
            conn.rollback()
            raise
        finally:
            conn.close()
    proof = cold_readback(db, source_path)
    expect(proof["state"] == "HELD_REVOKED", "HOLD_REVOCATION_NOT_PROPAGATED")
    return {"status": proof["state"], "proof": proof}


def cold_readback(db, source_path):
    packet = source(source_path)
    r = receiver_readback(db, expected_packet=packet, source_path=source_path)
    b = db_record(db)
    expect(b["work_id"] == WORK_ID and b["state"] in ("ACTIVE", "REVOKED"),
           "HOLD_BRIDGE_ID_STATE")
    original = json.loads(b["active_envelope_json"])
    expect(validate_envelope(original) == b["active_sha256"] and
           canonical(original["browser_record"]) == b["browser_record_json"] and
           original["intent"] == "INGEST_SYNTHETIC", "HOLD_BRIDGE_SOURCE_TAMPER")
    expect((b["state"] == "REVOKED") == (r["state"] == "HELD_REVOKED"),
           "HOLD_BROWSER_RECEIVER_REVOCATION_DIVERGENCE")
    expect(r["source_sha256"] == SOURCE_SHA256, "HOLD_SOURCE_CHANGED")
    if b["state"] == "REVOKED":
        expect(type(b["revoke_sha256"]) is str and len(b["revoke_sha256"]) == 64,
               "HOLD_REVOKE_PROOF_MISSING")
    else:
        expect(b["revoke_sha256"] is None, "HOLD_REVOCATION_CONFLICT")
    return {
        "schema": "CoCivium.CoPre.BrowserSQLiteReadback.R0",
        "state": "HELD_REVOKED" if b["state"] == "REVOKED" else
                 "VERIFIED_SYNTHETIC_SAME_SQLITE_RECEIVER",
        "work_id": WORK_ID, "source_ref": SOURCE_REF, "source_sha256": SOURCE_SHA256,
        "browser_active_envelope_sha256": b["active_sha256"],
        "browser_original_record_sha256": digest(original["browser_record"]),
        "receiver_packet_sha256": r["packet_sha256"],
        "receiver_receipt_sha256": r["receipt_sha256"],
        "revoke_sha256": b["revoke_sha256"],
        "narratives_byte_equal": original["browser_record"]["packet"]["prior_decisions"] == r["prior_decisions"],
        "browser_original_preserved": True,
        "synthetic_only": True, "user_consent_proven": False,
        "external_receiver_ack": False, "cross_provider_sync": False,
        "x2_runtime": False, "survived_24h": None,
        "transport": "EXPLICIT_FILE_HANDOFF_NO_AUTONOMOUS_TRANSPORT",
        "authority": "NONE_FOR_EXTERNAL_EFFECTS",
    }


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("ingest", "revoke", "readback"))
    parser.add_argument("--db", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--envelope")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    if args.command in ("ingest", "revoke"):
        expect(args.envelope is not None, "HOLD_MISSING_EXPLICIT_ENVELOPE")
        p = Path(args.envelope)
        expect(p.is_file() and not p.is_symlink() and p.stat().st_size <= 16384,
               "HOLD_UNSAFE_ENVELOPE_FILE")
        e = json.loads(p.read_text(encoding="utf-8"))
        result = ingest(args.db, args.source, e) if args.command == "ingest" else revoke(args.db, args.source, e)
    else:
        result = cold_readback(args.db, args.source)
    if args.report:
        dest = Path(args.report)
        with dest.open("x", encoding="utf-8") as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run_cli())
    except (Held, ValueError, sqlite3.Error) as err:
        print("HELD: " + str(err), file=sys.stderr)
        raise SystemExit(2)
