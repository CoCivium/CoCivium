#!/usr/bin/env python3
"""One-shot local CoGoAll source-verification WorkID; no scheduler or external effects.

A single invocation checks exact public-safe source bytes and commits a LOCAL_ONLY
result to the existing fenced SQLite queue. It never runs arbitrary WorkID commands,
touches network, starts a GUI/PowerShell window, or claims receiver acceptance.
An OS/service wake can invoke this later, but is deliberately not installed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(root: str, db_path: str, source: str = "CoPre.md",
        work_id: str = "CoPre:source-integrity:R0", now: int | None = None) -> dict:
    base = Path(root).resolve(strict=True)
    candidate = Path(source)
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise ValueError("HOLD_UNSAFE_SOURCE_PATH")
    path = base / candidate
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(base):
        raise ValueError("HOLD_SOURCE_NOT_REGULAR_IN_ROOT")
    if path.stat().st_size > 2_000_000 or path.stat().st_size == 0:
        raise ValueError("HOLD_SOURCE_SIZE")
    source_bytes = path.read_bytes()
    if not source_bytes or len(source_bytes) > 2_000_000:
        raise ValueError("HOLD_SOURCE_SIZE")
    digest = sha256(source_bytes)
    moment = int(time.time()) if now is None else now
    # Source revision and payload digest must be pinned. A changed source is
    # CONFLICT, not silent supersession of the existing WorkID.
    queue = DueWorkQueue(db_path)
    try:
        # This one-shot command owns only its exact WorkID. Do not write
        # into a shared queue while another front could be selected.
        foreign = queue.db.execute(
            "SELECT 1 FROM work WHERE work_id!=? LIMIT 1", (work_id,)
        ).fetchone()
        if foreign:
            return {"state": "HOLD_SHARED_QUEUE_REQUIRES_ELECTED_DISPATCHER",
                    "work_id": work_id, "external_receiver_ack": False}
        # Due time belongs to the durable WorkID, not the invocation clock.
        # Retain it across restart/replay. Never silently overwrite changed
        # source bytes or bring a future-due WorkID forward.
        existing = queue.db.execute(
            "SELECT source_revision,payload_sha256,due_at FROM work WHERE work_id=?",
            (work_id,)
        ).fetchone()
        due_at = existing[2] if existing else moment
        decision = queue.enqueue(work_id, "sha256:" + digest, digest, due_at)
        if decision == "CONFLICT":
            return {"state": "HOLD_SOURCE_REVISION_CONFLICT",
                    "work_id": work_id, "source_sha256": digest,
                    "external_receiver_ack": False}
        claims = queue.claim_due(now=moment, owner="local-source-verifier",
                                 lease_seconds=30, limit=1)
        if not claims:
            row = queue.db.execute("SELECT state,result_sha256 FROM work WHERE work_id=?",
                                   (work_id,)).fetchone()
            return {"state": "LOCAL_REPLAY_OR_LEASED",
                    "work_id": work_id, "queue_state": row[0] if row else "UNKNOWN",
                    "source_sha256": digest, "external_receiver_ack": False}
        claim = claims[0]
        if claim.work_id != work_id:
            return {"state": "HOLD_DIFFERENT_DUE_WORK",
                    "work_id": work_id, "claimed_work_id": claim.work_id,
                    "external_receiver_ack": False}
        # Verify source bytes a second time after claiming to reject changing
        # input; do not commit a success for stale or mismatched content.
        if not path.is_file() or path.is_symlink() or sha256(path.read_bytes()) != digest:
            return {"state": "HOLD_SOURCE_CHANGED_AFTER_CLAIM",
                    "work_id": work_id, "external_receiver_ack": False}
        receipt_payload = json.dumps({
            "action": "VERIFY_LOCAL_SOURCE_BYTES", "source": source,
            "work_id": work_id, "source_sha256": digest
        }, sort_keys=True, separators=(",", ":")).encode()
        result_sha = sha256(receipt_payload)
        completion = queue.complete(claim, result_sha256=result_sha, now=moment)
        return {"state": completion, "work_id": work_id,
                "source_sha256": digest, "local_result_sha256": result_sha,
                "external_receiver_ack": False, "real_external_effect": False}
    finally:
        queue.close()


def main() -> None:
    p = argparse.ArgumentParser(description="One-shot, local-only durable source check")
    p.add_argument("--root", required=True)
    p.add_argument("--db", required=True)
    p.add_argument("--source", default="CoPre.md")
    p.add_argument("--work-id", default="CoPre:source-integrity:R0")
    args = p.parse_args()
    try:
        result = run(args.root, args.db, args.source, args.work_id)
    except (ValueError, OSError) as exc:
        print(json.dumps({"state": "HOLD_LOCAL_ERROR", "reason": str(exc),
                          "external_receiver_ack": False}, sort_keys=True))
        raise SystemExit(2)
    print(json.dumps(result, sort_keys=True))
    if not (result["state"] == "COMMITTED_LOCAL_ONLY" or
            (result["state"] == "LOCAL_REPLAY_OR_LEASED" and
             result.get("queue_state") == "DONE")):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
