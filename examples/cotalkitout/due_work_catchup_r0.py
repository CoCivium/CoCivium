"""CoGoAll due-WorkID catch-up R0: local SQLite proof, no external effects.

A hosted cron tick is an optional hint. A wake can recover all *eligible*
backlogged WorkIDs, bounded by limit, without replaying finished local receipts.
Completion here is a DB transition, not proof of a real receiver effect.
"""
from __future__ import annotations
import re
import sqlite3
from dataclasses import dataclass

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def _moment(value: int) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("nonnegative integer UTC epoch seconds required")
    return value


def _digest(value: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError("lowercase SHA-256 digest required")
    return value


def _identity(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError("nonempty bounded identity required")
    return value


@dataclass(frozen=True)
class Claim:
    work_id: str
    source_revision: str
    payload_sha256: str
    epoch: int
    owner: str
    lease_until: int


class DueWorkQueue:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, timeout=5)
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS work (
            work_id TEXT PRIMARY KEY, source_revision TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL, due_at INTEGER NOT NULL,
            state TEXT NOT NULL DEFAULT 'PENDING', epoch INTEGER NOT NULL DEFAULT 0,
            owner TEXT, lease_until INTEGER, result_sha256 TEXT, completed_at INTEGER,
            CHECK (state IN ('PENDING','LEASED','DONE')))""")
        self.db.commit()

    def close(self):
        self.db.close()

    def enqueue(self, work_id: str, source_revision: str, payload_sha256: str, due_at: int):
        work_id, source_revision = _identity(work_id), _identity(source_revision)
        payload_sha256, due_at = _digest(payload_sha256), _moment(due_at)
        with self.db:
            inserted = self.db.execute("""INSERT INTO work(work_id,source_revision,payload_sha256,due_at)
                VALUES(?,?,?,?) ON CONFLICT(work_id) DO NOTHING""",
                (work_id, source_revision, payload_sha256, due_at)).rowcount
            row = self.db.execute("""SELECT source_revision,payload_sha256,due_at
                FROM work WHERE work_id=?""", (work_id,)).fetchone()
            if inserted:
                return "ENQUEUED"
            return "REPLAY" if row == (source_revision, payload_sha256, due_at) else "CONFLICT"

    def claim_due(self, *, now: int, owner: str, lease_seconds: int = 300, limit: int = 1):
        now, owner = _moment(now), _identity(owner)
        if type(lease_seconds) is not int or not 1 <= lease_seconds <= 86400:
            raise ValueError("bounded lease required")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("bounded batch required")
        acquired = []
        # BEGIN IMMEDIATE serializes competing claimers even across processes.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            rows = self.db.execute("""SELECT work_id FROM work
                WHERE (state='PENDING' AND due_at<=?) OR
                    (state='LEASED' AND lease_until<=?)
                ORDER BY due_at,work_id LIMIT ?""", (now, now, limit)).fetchall()
            for (work_id,) in rows:
                self.db.execute("""UPDATE work SET state='LEASED',
                    epoch=epoch+1,owner=?,lease_until=? WHERE work_id=?""",
                    (owner, now + lease_seconds, work_id))
                row = self.db.execute("""SELECT work_id,source_revision,payload_sha256,
                    epoch,owner,lease_until FROM work WHERE work_id=?""",
                    (work_id,)).fetchone()
                acquired.append(Claim(*row))
        return acquired

    def complete(self, claim: Claim, *, result_sha256: str, now: int):
        if not isinstance(claim, Claim):
            raise TypeError("claim token required")
        result_sha256, now = _digest(result_sha256), _moment(now)
        with self.db:
            row = self.db.execute("""SELECT state,epoch,owner,lease_until,
                source_revision,payload_sha256,result_sha256 FROM work WHERE work_id=?""",
                (claim.work_id,)).fetchone()
            if row is None:
                return "UNKNOWN_WORK"
            state, epoch, owner, lease_until, source_revision, payload_sha256, old_result = row
            if state == "DONE":
                exact_prior = (epoch == claim.epoch and owner == claim.owner
                               and lease_until == claim.lease_until
                               and source_revision == claim.source_revision
                               and payload_sha256 == claim.payload_sha256
                               and old_result == result_sha256)
                return "REPLAY" if exact_prior else "CONFLICT"
            if (state != "LEASED" or epoch != claim.epoch or owner != claim.owner
                or lease_until != claim.lease_until or lease_until <= now
                or source_revision != claim.source_revision
                or payload_sha256 != claim.payload_sha256):
                return "FENCED"
            self.db.execute("""UPDATE work SET state='DONE',result_sha256=?,completed_at=?
                WHERE work_id=?""",
                (result_sha256, now, claim.work_id))
            return "COMMITTED_LOCAL_ONLY"

    def next_wake(self):
        row = self.db.execute("""SELECT MIN(CASE WHEN state='PENDING' THEN due_at
            ELSE lease_until END) FROM work WHERE state!='DONE'""").fetchone()
        return row[0]

    def snapshot(self, now: int):
        now = _moment(now)
        rows = self.db.execute("""SELECT state,due_at,lease_until FROM work""").fetchall()
        return {"total": len(rows), "complete": sum(s == "DONE" for s,_,_ in rows),
                "due_pending": sum(s == "PENDING" and due <= now for s,due,_ in rows),
                "expired_leases": sum(s == "LEASED" and until <= now for s,_,until in rows),
                "next_wake": self.next_wake(),
                "independent_receiver_ack": False, "external_effect_verified": False}
