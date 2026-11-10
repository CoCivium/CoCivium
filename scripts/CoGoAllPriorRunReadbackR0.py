#!/usr/bin/env python3
"""Re-read a PINNED, already completed WorkID from a later GitHub Actions run.

This does not re-execute the task, claim unfinished work, provide an external ACK,
or establish a permanent queue. It establishes exact prior-result retrieval
across two CI workflow runs, both inside GitHub's failure domain.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess

from scripts.CoObjectAgencyBridgeR0 import Held, require
from scripts.CoObjectAgencyTaskR0 import (
    POLICY, FIXTURE, RECEIPT_SCHEMA, canonical, digest, source_sha,
)
from scripts.CoGoAllDueWorkSourceCanaryR0 import (
    CAPABILITY, CHECKPOINT_FIELDS, SCHEMA, _payload,
)

PIN = {
    "prior_run": "42763951520", "attempt": "1",
    "work_id": "CoObject.PolicyReview.42763951520.a1",
    "source_commit": "8bc2e7adbd88e7a5fcc828ffa3f982614490b773",
    "checkpoint_sha256": "f833f762c2140448702e6ce47f5bf3b043f82a2ff373e748499aea48e4467cbd",
    "task_receipt_sha256": "4f0c5f4f080c6ba6b0931edb296b06b95a0ef16574a00a1c9c00a56e120ef4c0",
    "receipt_file_sha256": "f148ec78c79fcb4c25967abb750a4c59be3be36fe142d32286d5faf419a13c8d",
    "queue_file_sha256": "0946fc52f02721ef921a0da346ebf6dc53ede477d53824357266a150cad7b72f",
    "payload_sha256": "222368e7136009ac1c7ee496babd63b50ac7725e1692cfa35d53f310ad319bb1",
    "policy_sha256": "24a42d99690a0870857524e28a2b33c7b022af8367f166567d6c35d528c165a8",
    "fixture_sha256": "cc470e4d61e0ac506153244de8b225c4c6157c4bd796379547b0fb02323b26c9",
    "lease_owner": "GitHubActions.42763951520.a1",
    "due_at": 1794289447, "completed_at": 1794289447,
    "lease_until": 1794289747, "lease_epoch": 1,
    "prior_readback_state": "SAME_PROVIDER_SOURCE_VALIDATION_AND_FENCED_QUEUE_READBACK",
    "producer_artifact_id": 13738906845,
    "producer_archive_digest": "sha256:eb2749e33cfe20929d7f13f34a6a2981c6b7a16fc9b22df0d1f310d7e267049a",
    "producer_artifact_name": "cogoall-one-due-work-42763951520-a1",
    "receiver_artifact_id": 13739355879,
    "receiver_archive_digest": "sha256:92f270b30e9868dc7de3435417fca62d463a00740e1121b15578aff0535b91cf",
    "receiver_artifact_name": "cogoall-one-due-readback-42763951520-a1",
}
MAX_JSON = 32768
MAX_DB = 2_000_000
RUN = re.compile(r"[1-9][0-9]*\Z")
REV = re.compile(r"[0-9a-f]{40}\Z")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def bounded(path: Path, cap: int) -> bytes:
    require(path.is_file() and not path.is_symlink(),
            "HOLD_MISSING_OR_SYMLINK_PRIOR_OBJECT")
    require(0 < path.stat().st_size <= cap, "HOLD_PRIOR_OBJECT_SIZE")
    raw = path.read_bytes()
    require(0 < len(raw) <= cap, "HOLD_PRIOR_OBJECT_SIZE")
    return raw


def json_obj(raw: bytes) -> dict:
    try:
        x = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise Held("HOLD_PRIOR_JSON") from exc
    require(isinstance(x, dict), "HOLD_PRIOR_OBJECT")
    return x


def context(root: Path, env: dict) -> dict:
    require(env.get("GITHUB_ACTIONS") == "true"
            and env.get("GITHUB_JOB") == "prior-task-reader"
            and env.get("GITHUB_EVENT_NAME") == "pull_request",
            "HOLD_CI_PRIOR_READER_IDENTITY")
    rid, attempt, head = (env.get("GITHUB_RUN_ID"),
                          env.get("GITHUB_RUN_ATTEMPT"), env.get("GITHUB_SHA"))
    require(isinstance(rid, str) and RUN.fullmatch(rid)
            and isinstance(attempt, str) and RUN.fullmatch(attempt)
            and isinstance(head, str) and REV.fullmatch(head),
            "HOLD_NEW_RUN_IDENTITY")
    actual = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                            text=True, capture_output=True, timeout=10, check=False)
    require(actual.returncode == 0 and actual.stdout.strip() == head,
            "HOLD_NEW_RUN_CHECKOUT_MISMATCH")
    return {"run_id": rid, "attempt": attempt, "source_head": head}


def verify_metadata(source: Path, readback: Path, pin: dict) -> dict:
    for name, path in (("producer", source), ("receiver", readback)):
        meta = json_obj(bounded(path, MAX_JSON))
        require(meta.get("id") == pin[name + "_artifact_id"]
                and meta.get("name") == pin[name + "_artifact_name"]
                and meta.get("digest") == pin[name + "_archive_digest"]
                and meta.get("expired") is False,
                "HOLD_PRIOR_ARTIFACT_METADATA_" + name.upper())
        workflow = meta.get("workflow_run")
        require(isinstance(workflow, dict)
                and str(workflow.get("id")) == pin["prior_run"],
                "HOLD_PRIOR_ARTIFACT_RUN_" + name.upper())
    return {"producer_artifact_id": pin["producer_artifact_id"],
            "receiver_artifact_id": pin["receiver_artifact_id"],
            "archive_metadata": "PINNED_GITHUB_ASSERTION_NOT_LOCAL_ZIP_HASH"}


def reobserve(root: Path, bundle: Path, previous_readback: Path,
              metadata_producer: Path, metadata_receiver: Path,
              *, ctx: dict, pin: dict, observed_at: datetime) -> dict:
    """Verify immutable prior result without enqueue/claim/complete or task dispatch."""
    require(ctx["run_id"] != pin["prior_run"]
            and RUN.fullmatch(ctx["run_id"]) is not None,
            "HOLD_NOT_DISTINCT_RUN")
    require(observed_at.tzinfo is not None
            and observed_at.utcoffset().total_seconds() == 0,
            "HOLD_OBSERVATION_NOT_UTC")
    require(int(observed_at.timestamp()) >= pin["completed_at"],
            "HOLD_PRIOR_IN_FUTURE")
    require(bundle.is_dir() and not bundle.is_symlink(),
            "HOLD_PRIOR_BUNDLE")
    meta = verify_metadata(metadata_producer, metadata_receiver, pin)

    prior_raw = bounded(bundle / "checkpoint.json", MAX_JSON)
    require(sha(prior_raw) == pin["checkpoint_sha256"],
            "HOLD_PRIOR_CHECKPOINT_DIGEST")
    record = json_obj(prior_raw)
    require(set(record) == CHECKPOINT_FIELDS and record["schema"] == SCHEMA,
            "HOLD_PRIOR_CHECKPOINT_SCHEMA")
    fields = {
        "work_id": "work_id", "source_commit": "source_commit",
        "run_id": "prior_run", "run_attempt": "attempt",
        "policy_sha256": "policy_sha256",
        "fixture_sha256": "fixture_sha256",
        "payload_sha256": "payload_sha256",
        "receipt_file_sha256": "receipt_file_sha256",
        "task_receipt_sha256": "task_receipt_sha256",
        "queue_file_sha256": "queue_file_sha256",
        "due_at": "due_at", "completed_at": "completed_at",
        "lease_until": "lease_until", "lease_epoch": "lease_epoch",
        "lease_owner": "lease_owner",
    }
    require(all(type(record[key]) is type(pin[pkey])
                and record[key] == pin[pkey] for key, pkey in fields.items()),
            "HOLD_PRIOR_CHECKPOINT_IDENTITY")
    require(record["event"] == "pull_request"
            and record["producer_job"] == "task-producer"
            and record["capability"] == CAPABILITY
            and record["effect_class"] == "READ_ONLY_SOURCE_VALIDATION"
            and record["checkpoint_scope"] == "RUN_SCOPED_ARTIFACT_ONLY"
            and record["external_receiver_ack"] is False
            and record["x2_runtime_qualified"] is False
            and record["product_mvp_qualified"] is False,
            "HOLD_PRIOR_AUTHORITY_INFLATION")

    policy, fixture = source_sha(root, POLICY), source_sha(root, FIXTURE)
    require(policy == pin["policy_sha256"] and fixture == pin["fixture_sha256"]
            and pin["payload_sha256"] == digest(canonical(_payload(policy, fixture))),
            "HOLD_PRIOR_SOURCE_DRIFT")

    receipt_bytes = bounded(bundle / "task-receipt.json", MAX_JSON)
    require(sha(receipt_bytes) == pin["receipt_file_sha256"],
            "HOLD_PRIOR_RECEIPT_BYTES")
    receipt = json_obj(receipt_bytes)
    require(receipt.get("schema") == RECEIPT_SCHEMA
            and receipt.get("state") == "TRUSTED_READ_ONLY_VALIDATOR_EXECUTED_IN_CI"
            and receipt.get("work_id") == pin["work_id"]
            and receipt.get("source_commit") == pin["source_commit"]
            and receipt.get("receipt_sha256") == pin["task_receipt_sha256"],
            "HOLD_PRIOR_RECEIPT_IDENTITY")
    original = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    require(digest(canonical(original)) == pin["task_receipt_sha256"]
            and receipt.get("policy_sha256") == policy
            and receipt.get("fixture_sha256") == fixture
            and receipt.get("external_receiver_ack") is False
            and receipt.get("external_effects") == 0,
            "HOLD_PRIOR_RECEIPT_CONTRACT")

    queue = bundle / "queue.sqlite"
    require(sha(bounded(queue, MAX_DB)) == pin["queue_file_sha256"],
            "HOLD_PRIOR_QUEUE_BYTES")
    con = sqlite3.connect("file:" + str(queue.resolve()) + "?immutable=1", uri=True)
    try:
        con.execute("PRAGMA query_only=ON")
        require(con.execute("SELECT COUNT(*) FROM work").fetchone()[0] == 1,
                "HOLD_PRIOR_WORK_COUNT")
        row = con.execute(
            "SELECT work_id,source_revision,payload_sha256,due_at,state,epoch,"
            "owner,lease_until,result_sha256,completed_at FROM work").fetchone()
    finally:
        con.close()
    require(row == (pin["work_id"], pin["source_commit"],
                    pin["payload_sha256"], pin["due_at"], "DONE",
                    pin["lease_epoch"], pin["lease_owner"], pin["lease_until"],
                    pin["task_receipt_sha256"], pin["completed_at"]),
            "HOLD_PRIOR_COMPLETION_MISMATCH")

    prior_receiver_raw = bounded(previous_readback, MAX_JSON)
    prior_receiver = json_obj(prior_receiver_raw)
    require(prior_receiver.get("schema") == "CoGoAll.OneDueSourceTaskReadback.R0"
            and prior_receiver.get("state") == pin["prior_readback_state"]
            and prior_receiver.get("work_id") == pin["work_id"]
            and prior_receiver.get("source_commit") == pin["source_commit"]
            and prior_receiver.get("source_checkpoint_sha256")
            == pin["checkpoint_sha256"]
            and prior_receiver.get("source_result_sha256")
            == pin["task_receipt_sha256"]
            and prior_receiver.get("read_only_validation_recomputed") is True
            and prior_receiver.get("fenced_local_completion") is True
            and prior_receiver.get("external_receiver_ack") is False
            and prior_receiver.get("persistent_24h_seed_qualified") is False,
            "HOLD_PRIOR_RECEIVER_CONTRACT")

    return {
        "schema": "CoGoAll.PriorRunCompletedWorkReadback.R0",
        "state": "PRIOR_COMPLETED_WORK_VERIFIED_IN_LATER_GITHUB_RUN",
        "work_id": pin["work_id"], "prior_run_id": pin["prior_run"],
        "current_run_id": ctx["run_id"], "current_source_head": ctx["source_head"],
        "prior_source_commit": pin["source_commit"],
        "prior_checkpoint_sha256": pin["checkpoint_sha256"],
        "prior_receipt_sha256": pin["task_receipt_sha256"],
        "prior_readback_sha256": sha(prior_receiver_raw),
        "archival_metadata": meta,
        "age_seconds_at_recheck": int(observed_at.timestamp()) - pin["completed_at"],
        "already_completed_prior_task": True, "new_effect_executed": False,
        "prior_task_enqueued_again": False, "unfinished_work_recovered": False,
        "durable_external_checkpoint": False,
        "provider_failure_domain": "SAME_GITHUB_ACTIONS",
        "external_receiver_ack": False, "seed_24h_qualified": False,
        "x2_runtime_qualified": False, "product_mvp_qualified": False,
    }


def write_new(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--bundle", required=True)
    p.add_argument("--prior-readback", required=True)
    p.add_argument("--producer-metadata", required=True)
    p.add_argument("--receiver-metadata", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    try:
        root = Path(a.root).resolve(strict=True)
        observation = reobserve(
            root, Path(a.bundle), Path(a.prior_readback),
            Path(a.producer_metadata), Path(a.receiver_metadata),
            ctx=context(root, os.environ), pin=PIN,
            observed_at=datetime.now(timezone.utc),
        )
        write_new(Path(a.output), observation)
        print(json.dumps(observation, sort_keys=True))
        return 0
    except (Held, TypeError, ValueError, OSError, sqlite3.Error,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)[:160],
                          "external_receiver_ack": False}, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
