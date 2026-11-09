#!/usr/bin/env python3
"""Read actual CoGoAll pulse artifact in a *different GitHub job*.

This verifier is intentionally read-only until it writes its own bounded local
receipt. It does not select work, prove a runtime effect, authenticate external
parties, or infer anything about X2. No network calls, secrets, or executors.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import re

SOURCE_SCHEMA = "cogoall-proof-pulse-r0"
RECEIVER_SCHEMA = "CoGoAll.PulseJobReadback.R0"
SOURCE_JOB = "proof"
RECEIVER_JOB = "pulse-receiver"
EXPECTED_LOGS = (
    "decision", "grace", "succession", "acceptance", "progress",
    "cadence-tests", "catchup-tests", "rebound-tests", "rebound-links"
)
EXPECTED_CLAIMS = [
    "SOURCE_TESTS_ONLY", "NO_X2_RECEIVER_ACK", "NO_24H_SEED_PROOF"
]
MAX_RECEIPT = 32768
MAX_EVIDENCE = 2_000_000


def hold(predicate: bool, reason: str) -> None:
    if not predicate:
        raise ValueError(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bounded_file(path: Path, max_bytes: int) -> bytes:
    hold(not path.is_symlink() and path.is_file(), "HOLD_MISSING_OR_LINKED_ARTIFACT")
    hold(0 < path.stat().st_size <= max_bytes, "HOLD_ARTIFACT_SIZE")
    data = path.read_bytes()
    hold(0 < len(data) <= max_bytes, "HOLD_ARTIFACT_SIZE")
    return data


def check_context(env: Mapping) -> dict:
    keys = (
        "GITHUB_ACTIONS", "GITHUB_JOB", "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT", "GITHUB_SHA", "GITHUB_EVENT_NAME"
    )
    hold(isinstance(env, Mapping) and all(
        isinstance(env.get(k), str) and bool(env.get(k))
        for k in keys
    ), "HOLD_GITHUB_CONTEXT_MISSING")
    hold(env["GITHUB_ACTIONS"] == "true" and env["GITHUB_JOB"] == RECEIVER_JOB,
         "HOLD_NOT_RECEIVER_JOB")
    hold(bool(re.fullmatch(r"[1-9][0-9]*", env["GITHUB_RUN_ID"])),
         "HOLD_BAD_RUN_ID")
    hold(bool(re.fullmatch(r"[1-9][0-9]*", env["GITHUB_RUN_ATTEMPT"])),
         "HOLD_BAD_ATTEMPT")
    hold(bool(re.fullmatch(r"[0-9a-f]{40}", env["GITHUB_SHA"])),
         "HOLD_BAD_SOURCE_COMMIT")
    hold(env["GITHUB_EVENT_NAME"] in ("schedule", "push", "workflow_dispatch"),
         "HOLD_EVENT_NOT_QUALIFIED")
    return {k: env[k] for k in keys}


def observe(directory: str | Path, env: Mapping) -> dict:
    ctx = check_context(env)
    root = Path(directory)
    hold(root.is_dir() and not root.is_symlink(), "HOLD_ARTIFACT_DIRECTORY")
    original = bounded_file(root / "proof-receipt.json", MAX_RECEIPT)
    try:
        source = json.loads(original)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("HOLD_INVALID_PROOF_JSON") from exc
    hold(isinstance(source, dict), "HOLD_INVALID_PROOF")
    expected_fields = {
        "schema", "observed_at_utc", "run_id", "attempt", "head", "event",
        "outcome", "log_sha256", "schedule_audit_sha256",
        "rebound_audit_sha256", "claims"
    }
    hold(set(source) == expected_fields, "HOLD_UNEXPECTED_PROOF_FIELDS")
    hold(source["schema"] == SOURCE_SCHEMA, "HOLD_PROOF_SCHEMA")
    hold(source["run_id"] == ctx["GITHUB_RUN_ID"]
         and source["attempt"] == ctx["GITHUB_RUN_ATTEMPT"]
         and source["head"] == ctx["GITHUB_SHA"]
         and source["event"] == ctx["GITHUB_EVENT_NAME"],
         "HOLD_WRONG_RUN_OR_SOURCE")
    hold(source["outcome"] == "success", "HOLD_TESTS_NOT_PASSED")
    hold(source["claims"] == EXPECTED_CLAIMS, "HOLD_AUTHORITY_OR_ACK_INFLATION")
    stamp = source["observed_at_utc"]
    hold(isinstance(stamp, str), "HOLD_TIMESTAMP")
    try:
        value = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("HOLD_TIMESTAMP") from exc
    hold(value.tzinfo is not None and value.utcoffset() == timedelta(0),
         "HOLD_NOT_UTC")
    hashes = source["log_sha256"]
    hold(isinstance(hashes, dict) and set(hashes) == set(EXPECTED_LOGS),
         "HOLD_MISSING_LOG_IDENTITIES")
    for name in EXPECTED_LOGS:
        digest = hashes[name]
        hold(isinstance(digest, str) and bool(re.fullmatch(r"[a-f0-9]{64}", digest)),
             "HOLD_INVALID_LOG_HASH")
        raw = bounded_file(root / (name + ".log"), MAX_EVIDENCE)
        hold(sha(raw) == digest, "HOLD_LOG_DIGEST_MISMATCH")
    cadence_digest = source["schedule_audit_sha256"]
    hold(isinstance(cadence_digest, str) and bool(
        re.fullmatch(r"[a-f0-9]{64}", cadence_digest)
    ), "HOLD_CADENCE_DIGEST_MISSING")
    cadence = bounded_file(root / "schedule-audit.json", MAX_EVIDENCE)
    hold(sha(cadence) == cadence_digest, "HOLD_CADENCE_DIGEST_MISMATCH")
    rebound_digest = source["rebound_audit_sha256"]
    hold(isinstance(rebound_digest, str) and bool(
        re.fullmatch(r"[a-f0-9]{64}", rebound_digest)
    ), "HOLD_REBOUND_DIGEST_MISSING")
    rebound_report = bounded_file(root / "rebound-report.json", MAX_EVIDENCE)
    hold(sha(rebound_report) == rebound_digest, "HOLD_REBOUND_DIGEST_MISMATCH")
    return {
        "schema": RECEIVER_SCHEMA,
        "state": "GITHUB_JOB_BOUNDARY_ARTIFACT_HASH_READBACK",
        "work_id": "CoGoAll.PulseReceipt." + ctx["GITHUB_RUN_ID"] + ".a" + ctx["GITHUB_RUN_ATTEMPT"],
        "source_commit": ctx["GITHUB_SHA"],
        "run_id": ctx["GITHUB_RUN_ID"],
        "run_attempt": ctx["GITHUB_RUN_ATTEMPT"],
        "event": ctx["GITHUB_EVENT_NAME"],
        "producer_job": SOURCE_JOB,
        "receiver_job": RECEIVER_JOB,
        "source_receipt_sha256": sha(original),
        "schedule_audit_sha256": cadence_digest,
        "rebound_audit_sha256": rebound_digest,
        "verified_log_count": len(EXPECTED_LOGS),
        "provider_failure_domain": "SAME_GITHUB_ACTIONS",
        "due_work_selection": "NOT_TESTED",
        "real_worker_effect": "NOT_TESTED",
        "external_receiver_ack": False,
        "x2_receiver": "NOT_TESTED",
        "seed_survives_24h": "NOT_TESTED",
    }


def write_receipt(observation: dict, dest: str | Path) -> None:
    target = Path(dest)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(observation, sort_keys=True, indent=2) + "\n").encode()
    with target.open("xb") as stream:
        stream.write(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    observation = observe(args.source_dir, os.environ)
    write_receipt(observation, args.receipt)
    print(json.dumps(observation, sort_keys=True))


if __name__ == "__main__":
    main()
