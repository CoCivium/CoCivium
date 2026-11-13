#!/usr/bin/env python3
"""Source-verified one-WorkID admission to the EXISTING CoGoAll SQLite queue.

Review-branch-only canary. No scheduler, model, provider session, HTTP call,
external effect, or receiver ACK. The local SQLite DB is run-scoped; it is
neither off-host custody nor proof an effect executed. A caller-supplied
materiality claim remains untrusted even when source bytes match.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess

from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue
from scripts.CoGoAllWakeAdmissionR0 import review, _utc

DB_PARTS = ("out", "cogoall", "wake-admission-r0.sqlite")
MAX_SOURCE_BYTES = 2_000_000
NONCLAIMS = [
    "ADMITTED_SQLITE_CANDIDATE_NE_TASK_DISPATCH",
    "FILE_HASH_NE_MATERIALITY_ATTESTATION",
    "LOCAL_DB_NE_INDEPENDENT_RECEIVER_CUSTODY",
    "CHECKOUT_HEAD_NE_PROVEN_GITHUB_ACCOUNT_AUTHORITY",
    "SOURCE_ONLY_NE_X2_OR_COBAR_RUNTIME",
    "NO_EXTERNAL_RECEIVER_ACK",
]


def _hold(reason: str, wid=None) -> dict:
    return {
        "schema": "CoGoAll.WakeAdmissionJournal.R0",
        "state": "HOLD_LOCAL_WAKE_ADMISSION",
        "reason": reason,
        "work_id": wid,
        "queue_admitted": False,
        "task_dispatched": False,
        "external_receiver_ack": False,
        "nonclaims": NONCLAIMS,
    }


def _source_attested(root: Path, event: dict) -> None:
    path = root / event["source_path"]
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError("HOLD_SOURCE_PATH_OR_SYMLINK")
    size = path.stat().st_size
    if not 0 < size <= MAX_SOURCE_BYTES:
        raise ValueError("HOLD_SOURCE_SIZE")
    raw = path.read_bytes()
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != event["source_sha256"]:
        raise ValueError("HOLD_SOURCE_BYTE_DRIFT")
    try:
        parsed = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("HOLD_SOURCE_NOT_JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("HOLD_SOURCE_NOT_OBJECT")
    # HEAD identity is a local Git constraint only, NOT independent provider
    # authentication. No shell=True and this never executes on X2.
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
            text=True, timeout=8, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("HOLD_HEAD_UNAVAILABLE") from exc
    if head.returncode != 0 or head.stdout.strip() != event["source_revision"]:
        raise ValueError("HOLD_CHECKOUT_REVISION_DRIFT")


def _queue_path(root: Path) -> Path:
    a, b, c = DB_PARTS
    first, directory = root / a, root / a / b
    if first.is_symlink() or directory.is_symlink():
        raise ValueError("HOLD_STATE_SYMLINK")
    if first.exists() and not first.is_dir():
        raise ValueError("HOLD_STATE_PATH")
    if directory.exists() and not directory.is_dir():
        raise ValueError("HOLD_STATE_PATH")
    db = directory / c
    if db.is_symlink() or (db.exists() and not db.is_file()):
        raise ValueError("HOLD_DB_NOT_REGULAR")
    directory.mkdir(parents=True, exist_ok=True)
    return db


def admit(root: str | Path, event: dict, now: datetime) -> dict:
    """One source-validated local admission candidate; never leases or executes."""
    wid = event.get("work_id") if isinstance(event, dict) else None
    proposal = review(event, [], now)
    if proposal["state"] != "WAKE_ADMISSION_REVIEW_CANDIDATE":
        return {
            **_hold(proposal.get("reason") or proposal["state"], wid),
            "state": proposal["state"] if proposal["state"].startswith("QUIESCENT") else "HOLD_LOCAL_WAKE_ADMISSION",
        }
    try:
        base = Path(root).resolve(strict=True)
        _source_attested(base, event)
        db = _queue_path(base)
        # Due time must survive retries. Use the source event's fixed timestamp,
        # not the current runner clock.
        due_at = int(_utc(event["observed_at_utc"]).timestamp())
        payload = hashlib.sha256(
            ("CoGoAll.WakeAdmissionJournal.R0:" + proposal["wake_id"]).encode("utf-8")
        ).hexdigest()
        queue = DueWorkQueue(str(db))
        try:
            other = queue.db.execute(
                "SELECT work_id FROM work WHERE work_id!=? LIMIT 1", (wid,)
            ).fetchone()
            if other:
                raise ValueError("HOLD_FOREIGN_WORK_IN_SINGLE_OWNER_QUEUE")
            decision = queue.enqueue(wid, event["source_revision"], payload, due_at)
            if decision == "CONFLICT":
                raise ValueError("HOLD_SAME_WORKID_DIFFERENT_WAKE_OR_SOURCE")
            row = queue.db.execute(
                "SELECT work_id,source_revision,payload_sha256,due_at,state,epoch "
                "FROM work WHERE work_id=?", (wid,)
            ).fetchone()
            if row is None or row[:4] != (wid, event["source_revision"], payload, due_at):
                raise ValueError("HOLD_DURABLE_QUEUE_READBACK_DIFFERENCE")
            return {
                "schema": "CoGoAll.WakeAdmissionJournal.R0",
                "state": ("ADMITTED_LOCAL_ONLY_WAITING_FOR_WORKER"
                          if decision == "ENQUEUED" else "QUIESCENT_ALREADY_ADMITTED"),
                "work_id": wid,
                "wake_id": proposal["wake_id"],
                "queue_admitted": decision == "ENQUEUED",
                "queue_state": row[4],
                "lease_epoch": row[5],
                "source_sha256": event["source_sha256"],
                "source_revision": event["source_revision"],
                "source_attestation": "CHECKOUT_HEAD_AND_EXACT_LOCAL_FILE_SHA256",
                "prior_journal_authenticated": False,
                "materiality_independently_attested": False,
                "task_dispatched": False,
                "external_receiver_ack": False,
                "nonclaims": NONCLAIMS,
            }
        finally:
            queue.close()
    except (ValueError, OSError, sqlite3.Error, TypeError) as exc:
        return _hold(str(exc) if str(exc).startswith("HOLD_") else "HOLD_LOCAL_DB_ERROR", wid)
