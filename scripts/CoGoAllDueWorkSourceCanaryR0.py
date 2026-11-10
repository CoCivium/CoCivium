#!/usr/bin/env python3
"""CoGoAll R0: one source-pinned due WorkID -> existing read-only validator -> CI-job readback.

This is a bounded GitHub Actions canary, not an X2/CoStead worker, independent
provider pickup, durable queue across runs, user MVP, or authorization to act.
No model, arbitrary task command, network call, or privileged effect is started.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess

from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue
from scripts.CoObjectAgencyBridgeR0 import Held, require
from scripts.CoObjectAgencyTaskR0 import (
    POLICY, FIXTURE, CAPABILITY, canonical, check_readback, digest,
    execute_one, source_sha,
)

SCHEMA = "CoGoAll.OneDueSourceTask.R0"
RUN = re.compile(r"[1-9][0-9]*\\Z")
HEAD = re.compile(r"[a-f0-9]{40}\\Z")
MAX_JSON = 32768
MAX_DB = 2_000_000
CHECKPOINT_FIELDS = {
    "schema", "work_id", "source_commit", "run_id", "run_attempt", "event",
    "producer_job", "due_at", "completed_at", "lease_epoch", "lease_owner",
    "lease_until", "payload_sha256", "policy_sha256", "fixture_sha256",
    "task_receipt_sha256", "receipt_file_sha256", "queue_file_sha256",
    "capability", "effect_class", "checkpoint_scope", "external_receiver_ack",
    "x2_runtime_qualified", "product_mvp_qualified",
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require_checkout(root: Path, env, role: str) -> dict:
    require(env.get("GITHUB_ACTIONS") == "true" and env.get("GITHUB_JOB") == role,
            "HOLD_UNTRUSTED_JOB_CONTEXT")
    run_id, attempt = env.get("GITHUB_RUN_ID"), env.get("GITHUB_RUN_ATTEMPT")
    head, event = env.get("GITHUB_SHA"), env.get("GITHUB_EVENT_NAME")
    require(isinstance(run_id, str) and RUN.fullmatch(run_id)
            and isinstance(attempt, str) and RUN.fullmatch(attempt),
            "HOLD_RUN_ID")
    require(isinstance(head, str) and HEAD.fullmatch(head),
            "HOLD_SOURCE_COMMIT")
    require(event in {"push", "schedule", "workflow_dispatch", "pull_request"},
            "HOLD_UNQUALIFIED_EVENT")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True,
        timeout=10, check=False,
    )
    require(result.returncode == 0 and result.stdout.strip() == head,
            "HOLD_CHECKOUT_HEAD_MISMATCH")
    return {"run_id": run_id, "attempt": attempt, "head": head, "event": event}


def _work_id(ctx: dict) -> str:
    return "CoObject.PolicyReview." + ctx["run_id"] + ".a" + ctx["attempt"]


def _payload(policy_sha: str, fixture_sha: str) -> dict:
    return {"schema": "CoGoAll.ReadOnlyPolicyValidationTask.R0",
            "capability": CAPABILITY, "policy_sha256": policy_sha,
            "fixture_sha256": fixture_sha}


def _write_new(path: Path, data: dict) -> None:
    raw = json.dumps(data, sort_keys=True, indent=2) + "\n"
    with path.open("x", encoding="utf-8") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


def _bounded(path: Path, cap: int) -> bytes:
    require(path.is_file() and not path.is_symlink(),
            "HOLD_MISSING_OR_SYMLINK_ARTIFACT")
    require(0 < path.stat().st_size <= cap, "HOLD_ARTIFACT_SIZE")
    raw = path.read_bytes()
    require(0 < len(raw) <= cap, "HOLD_ARTIFACT_SIZE")
    return raw


def _json(raw: bytes) -> dict:
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise Held("HOLD_INVALID_JSON") from exc
    require(isinstance(data, dict), "HOLD_INVALID_OBJECT")
    return data


def produce(root: str | Path, bundle: str | Path, env, *, now=None) -> dict:
    """Select exactly one due code-owned task; produce result and local checkpoint."""
    root = Path(root).resolve(strict=True)
    ctx = _require_checkout(root, env, "task-producer")
    time = now if now is not None else datetime.now(timezone.utc)
    require(isinstance(time, datetime) and time.tzinfo is not None
            and time.utcoffset().total_seconds() == 0, "HOLD_NON_UTC_CLOCK")
    instant = int(time.timestamp())
    require(instant >= 0, "HOLD_TIME")
    policy_sha, fixture_sha = source_sha(root, POLICY), source_sha(root, FIXTURE)
    payload_sha = digest(canonical(_payload(policy_sha, fixture_sha)))
    work_id = _work_id(ctx)
    bundle = Path(bundle)
    require(not bundle.exists(), "HOLD_CREATE_ONLY_BUNDLE")
    bundle.mkdir(parents=True)
    queue_file = bundle / "queue.sqlite"
    owner = "GitHubActions." + ctx["run_id"] + ".a" + ctx["attempt"]
    queue = DueWorkQueue(str(queue_file))
    try:
        require(queue.enqueue(work_id, ctx["head"], payload_sha, instant)
                == "ENQUEUED", "HOLD_WORK_ID_COLLISION")
        claims = queue.claim_due(now=instant, owner=owner, lease_seconds=300, limit=1)
        require(len(claims) == 1 and claims[0].work_id == work_id
                and claims[0].source_revision == ctx["head"]
                and claims[0].payload_sha256 == payload_sha,
                "HOLD_DUE_SELECTION")
        claim = claims[0]
        receipt = execute_one(
            root, work_id, ctx["head"], time.isoformat(),
            policy_sha=policy_sha, fixture_sha=fixture_sha,
        )
        completed_at = int(datetime.now(timezone.utc).timestamp())
        require(queue.complete(claim, result_sha256=receipt["receipt_sha256"],
                               now=completed_at) == "COMMITTED_LOCAL_ONLY",
                "HOLD_FENCED_COMPLETION")
        snapshot = queue.snapshot(completed_at)
        require(snapshot["total"] == snapshot["complete"] == 1
                and snapshot["independent_receiver_ack"] is False
                and snapshot["external_effect_verified"] is False,
                "HOLD_QUEUE_STATE")
    finally:
        queue.close()

    receipt_file = bundle / "task-receipt.json"
    _write_new(receipt_file, receipt)
    checkpoint = {
        "schema": SCHEMA, "work_id": work_id, "source_commit": ctx["head"],
        "run_id": ctx["run_id"], "run_attempt": ctx["attempt"],
        "event": ctx["event"], "producer_job": "task-producer",
        "due_at": instant, "completed_at": completed_at,
        "lease_epoch": claim.epoch, "lease_owner": claim.owner,
        "lease_until": claim.lease_until, "payload_sha256": payload_sha,
        "policy_sha256": policy_sha, "fixture_sha256": fixture_sha,
        "task_receipt_sha256": receipt["receipt_sha256"],
        "receipt_file_sha256": _sha(_bounded(receipt_file, MAX_JSON)),
        "queue_file_sha256": _sha(_bounded(queue_file, MAX_DB)),
        "capability": CAPABILITY, "effect_class": "READ_ONLY_SOURCE_VALIDATION",
        "checkpoint_scope": "RUN_SCOPED_ARTIFACT_ONLY",
        "external_receiver_ack": False, "x2_runtime_qualified": False,
        "product_mvp_qualified": False,
    }
    _write_new(bundle / "checkpoint.json", checkpoint)
    return checkpoint


def readback(root: str | Path, bundle: str | Path, env) -> dict:
    """Recompute the source result and exact local DB transition in another CI job."""
    root = Path(root).resolve(strict=True)
    ctx = _require_checkout(root, env, "task-receiver")
    bundle = Path(bundle)
    require(bundle.is_dir() and not bundle.is_symlink(), "HOLD_BUNDLE")
    checkpoint_bytes = _bounded(bundle / "checkpoint.json", MAX_JSON)
    checkpoint = _json(checkpoint_bytes)
    require(set(checkpoint) == CHECKPOINT_FIELDS and checkpoint["schema"] == SCHEMA,
            "HOLD_CHECKPOINT_SCHEMA")
    require((checkpoint["work_id"], checkpoint["source_commit"],
             checkpoint["run_id"], checkpoint["run_attempt"], checkpoint["event"])
            == (_work_id(ctx), ctx["head"], ctx["run_id"], ctx["attempt"], ctx["event"]),
            "HOLD_WRONG_RUN_OR_SOURCE")
    require(checkpoint["producer_job"] == "task-producer"
            and checkpoint["capability"] == CAPABILITY
            and checkpoint["effect_class"] == "READ_ONLY_SOURCE_VALIDATION"
            and checkpoint["checkpoint_scope"] == "RUN_SCOPED_ARTIFACT_ONLY"
            and checkpoint["external_receiver_ack"] is False
            and checkpoint["x2_runtime_qualified"] is False
            and checkpoint["product_mvp_qualified"] is False,
            "HOLD_EFFECT_OR_AUTHORITY_INFLATION")
    policy_sha, fixture_sha = source_sha(root, POLICY), source_sha(root, FIXTURE)
    require(checkpoint["policy_sha256"] == policy_sha
            and checkpoint["fixture_sha256"] == fixture_sha
            and checkpoint["payload_sha256"] ==
            digest(canonical(_payload(policy_sha, fixture_sha))),
            "HOLD_CHANGED_TASK_SOURCE")

    receipt_bytes = _bounded(bundle / "task-receipt.json", MAX_JSON)
    require(_sha(receipt_bytes) == checkpoint["receipt_file_sha256"],
            "HOLD_RECEIPT_BYTES_DRIFT")
    receipt = _json(receipt_bytes)
    require(checkpoint["task_receipt_sha256"] == receipt.get("receipt_sha256"),
            "HOLD_RECEIPT_IDENTITY_DRIFT")
    confirmed = check_readback(root, receipt,
                               expected_work_id=_work_id(ctx),
                               expected_source_head=ctx["head"])
    require(confirmed["state"] == "SECOND_CI_JOB_RECOMPUTED_SOURCE_AND_VALIDATION"
            and confirmed["external_receiver_ack"] is False,
            "HOLD_VALIDATION_READBACK")

    queue_file = bundle / "queue.sqlite"
    queue_bytes = _bounded(queue_file, MAX_DB)
    require(_sha(queue_bytes) == checkpoint["queue_file_sha256"],
            "HOLD_QUEUE_BYTES_DRIFT")
    uri = "file:" + str(queue_file.resolve()) + "?immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        require(connection.execute("SELECT COUNT(*) FROM work").fetchone()[0] == 1,
                "HOLD_UNEXPECTED_WORK_COUNT")
        row = connection.execute(
            "SELECT work_id,source_revision,payload_sha256,due_at,state,epoch,"
            "owner,lease_until,result_sha256,completed_at FROM work"
        ).fetchone()
    finally:
        connection.close()
    require(row == (
        checkpoint["work_id"], ctx["head"], checkpoint["payload_sha256"],
        checkpoint["due_at"], "DONE", checkpoint["lease_epoch"],
        checkpoint["lease_owner"], checkpoint["lease_until"],
        checkpoint["task_receipt_sha256"], checkpoint["completed_at"],
    ), "HOLD_QUEUE_COMMIT_MISMATCH")
    require(type(checkpoint["lease_epoch"]) is int and checkpoint["lease_epoch"] == 1
            and type(checkpoint["due_at"]) is int
            and type(checkpoint["completed_at"]) is int
            and checkpoint["due_at"] <= checkpoint["completed_at"]
            < checkpoint["lease_until"],
            "HOLD_LEASE_TIME_OR_EPOCH")
    return {
        "schema": "CoGoAll.OneDueSourceTaskReadback.R0",
        "state": "SAME_PROVIDER_SOURCE_VALIDATION_AND_FENCED_QUEUE_READBACK",
        "work_id": _work_id(ctx), "source_commit": ctx["head"],
        "event": ctx["event"], "scheduled_wake": ctx["event"] == "schedule",
        "due_work_selected": True, "fenced_local_completion": True,
        "read_only_validation_recomputed": True,
        "source_checkpoint_sha256": _sha(checkpoint_bytes),
        "source_result_sha256": checkpoint["task_receipt_sha256"],
        "provider_failure_domain": "SAME_GITHUB_ACTIONS",
        "checkpoint_scope": "RUN_SCOPED_ARTIFACT_ONLY",
        "external_receiver_ack": False, "x2_runtime_qualified": False,
        "persistent_24h_seed_qualified": False, "product_mvp_qualified": False,
    }


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["produce", "readback"])
    p.add_argument("--root", default=".")
    p.add_argument("--bundle", required=True)
    p.add_argument("--readback")
    args = p.parse_args()
    try:
        if args.mode == "produce":
            require(args.readback is None, "HOLD_PRODUCER_READBACK_PATH")
            result = produce(args.root, args.bundle, os.environ)
        else:
            require(isinstance(args.readback, str) and bool(args.readback),
                    "HOLD_READBACK_PATH")
            result = readback(args.root, args.bundle, os.environ)
            dest = Path(args.readback)
            dest.parent.mkdir(parents=True, exist_ok=True)
            _write_new(dest, result)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Held, ValueError, TypeError, OSError, sqlite3.Error,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)[:160],
                          "external_receiver_ack": False}, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
