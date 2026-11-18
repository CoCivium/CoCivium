#!/usr/bin/env python3
"""Lease-fenced *simulation-only* CoPre local SQLite handoff.

No external effects, real-time scheduler, distributed consensus, device access,
real receiver ACK, or exactly-once external guarantee. 'now' is explicitly
supplied simulated integer time; never interpret it as a trusted wall clock.
"""
import sqlite3

DDL = """
CREATE TABLE IF NOT EXISTS handoffs (
 effect_key TEXT PRIMARY KEY, work_id TEXT NOT NULL, source_revision TEXT NOT NULL,
 actor TEXT NOT NULL, epoch INTEGER NOT NULL, state TEXT NOT NULL,
 receipt TEXT, lease_until INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS committed (
 effect_key TEXT PRIMARY KEY, receipt TEXT NOT NULL
);
"""

def connect(path):
    db = sqlite3.connect(str(path), isolation_level=None, timeout=3)
    db.executescript(DDL)
    return db

def reserve(db, *, work_id, source_revision, effect_key, actor, now, ttl=10):
    if not all(isinstance(v, str) and v.strip() for v in
               [work_id, source_revision, effect_key, actor]):
        return {"state": "HELD_INVALID_IDENTITY"}
    if type(now) is not int or now < 0 or type(ttl) is not int or ttl <= 0 or ttl > 3600:
        return {"state": "HELD_INVALID_SIMULATED_TIME_OR_TTL"}
    db.execute("BEGIN IMMEDIATE")
    try:
        r = db.execute(
            "SELECT work_id,source_revision,actor,epoch,state,lease_until "
            "FROM handoffs WHERE effect_key=?", (effect_key,)
        ).fetchone()
        if r is None:
            db.execute("INSERT INTO handoffs VALUES (?,?,?,?,?,?,?,?)",
                       (effect_key, work_id, source_revision, actor,
                        1, "RESERVED", None, now + ttl))
            result = {"state": "RESERVED", "epoch": 1, "lease_until": now + ttl}
        elif r[0] != work_id or r[1] != source_revision:
            result = {"state": "HELD_SOURCE_OR_WORK_CONFLICT"}
        elif r[4] == "COMMITTED":
            result = {"state": "DUPLICATE_COMMITTED", "epoch": r[3]}
        elif now < r[5]:
            result = ({"state": "ALREADY_RESERVED", "epoch": r[3], "lease_until": r[5]}
                      if r[2] == actor else
                      {"state": "HELD_ACTIVE_LEASE", "lease_until": r[5]})
        else:
            # Even a repeated actor must acquire a new fencing epoch after expiry.
            epoch = r[3] + 1
            db.execute(
                "UPDATE handoffs SET actor=?,epoch=?,lease_until=? WHERE effect_key=?",
                (actor, epoch, now + ttl, effect_key)
            )
            result = {"state": "RESERVED", "epoch": epoch, "lease_until": now + ttl}
        db.execute("COMMIT")
        return result
    except:
        db.execute("ROLLBACK")
        raise

def commit(db, *, effect_key, actor, epoch, receipt, now):
    if not isinstance(receipt, str) or not receipt.strip() or type(epoch) is not int:
        return "HELD_MISSING_RECEIPT_OR_EPOCH"
    if type(now) is not int or now < 0:
        return "HELD_INVALID_SIMULATED_TIME_OR_TTL"
    db.execute("BEGIN IMMEDIATE")
    try:
        r = db.execute(
            "SELECT actor,epoch,state,receipt,lease_until FROM handoffs WHERE effect_key=?",
            (effect_key,)
        ).fetchone()
        if r is None:
            state = "HELD_NO_RESERVATION"
        elif r[0] != actor or r[1] != epoch:
            state = "HELD_STALE_WRITER"
        elif r[2] == "COMMITTED":
            state = "DUPLICATE_COMMITTED" if r[3] == receipt else "HELD_RECEIPT_CONFLICT"
        elif now >= r[4]:
            state = "HELD_EXPIRED_LEASE"
        else:
            db.execute(
                "UPDATE handoffs SET state='COMMITTED',receipt=? WHERE effect_key=?",
                (receipt, effect_key)
            )
            db.execute("INSERT INTO committed VALUES (?,?)", (effect_key, receipt))
            state = "COMMITTED_LOCAL_LEDGER_ONLY"
        db.execute("COMMIT")
        return state
    except:
        db.execute("ROLLBACK")
        raise

def snapshot(db):
    return {
        "ledger_commits": db.execute("SELECT count(*) FROM committed").fetchone()[0],
        "external_effects_proven": False,
        "receiver_readproof": False,
        "exactly_once_external": False,
        "time_source": "SIMULATED_CALLER_SUPPLIED_UNTRUSTED"
    }
