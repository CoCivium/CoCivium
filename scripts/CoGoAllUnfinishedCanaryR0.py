#!/usr/bin/env python3
"""PR-only unfinished WorkID canary across GitHub Actions jobs, same provider.

This is a deterministic virtual-time lease expiry proof over an exact source
and file-backed SQLite queue. It does not recover across separate workflow
runs or establish any external receiver, service, X2 runtime, or OS wake.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess

from examples.cotalkitout.due_work_catchup_r0 import DueWorkQueue, Claim

SCHEMA = "CoGoAll.UnfinishedJobBoundary.R0"
RESULT_SCHEMA = "CoGoAll.UnfinishedJobBoundaryReadback.R0"
SOURCE = "CoPre.md"
START = 100
EXPIRY = 130
FINISH = 131
LIMIT = 2_000_000
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
ID = re.compile(r"[1-9][0-9]*\Z")
FIELDS = {
    "schema", "work_id", "source_commit", "source_sha256", "run_id",
    "attempt", "queue_sha256", "lease_owner", "lease_epoch",
    "lease_until", "effect_executed", "external_receiver_ack",
    "provider_scope", "clock_scope",
}


class Held(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Held(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def serialize(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode("utf-8")


def ctx(root: Path, env: dict, role: str) -> dict:
    require(env.get("GITHUB_ACTIONS") == "true"
            and env.get("GITHUB_JOB") == role
            and env.get("GITHUB_EVENT_NAME") == "pull_request",
            "HOLD_UNAUTHORIZED_EXECUTION_CONTEXT")
    rid, attempt, head = env.get("GITHUB_RUN_ID"), env.get("GITHUB_RUN_ATTEMPT"), env.get("GITHUB_SHA")
    require(all(isinstance(x, str) for x in (rid, attempt, head))
            and ID.fullmatch(rid) is not None
            and ID.fullmatch(attempt) is not None
            and HEX40.fullmatch(head) is not None,
            "HOLD_WORKFLOW_IDENTITY")
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                        text=True, capture_output=True, timeout=10, check=False)
    require(cp.returncode == 0 and cp.stdout.strip() == head,
            "HOLD_WORKFLOW_CHECKOUT_MISMATCH")
    return {"run_id": rid, "attempt": attempt, "source_commit": head}


def source_digest(root: Path) -> str:
    base = root.resolve(strict=True)
    file = base / SOURCE
    require(file.is_file() and not file.is_symlink()
            and file.resolve().is_relative_to(base), "HOLD_SOURCE_NOT_REGULAR")
    size = file.stat().st_size
    require(0 < size <= LIMIT, "HOLD_SOURCE_SIZE")
    data = file.read_bytes()
    require(len(data) == size and len(data) <= LIMIT, "HOLD_SOURCE_CHANGED_DURING_READ")
    return sha(data)


def work_id(ctx_: dict) -> str:
    return f"CoGoAll.Unfinished.{ctx_['run_id']}.a{ctx_['attempt']}"


def seed(root: Path, bundle: Path, ctx_: dict) -> dict:
    src = source_digest(root)
    require(not bundle.exists() and not bundle.is_symlink(), "HOLD_CREATE_ONLY_BUNDLE")
    bundle.mkdir(parents=True, exist_ok=False)
    db = DueWorkQueue(str(bundle / "queue.sqlite"))
    owner = f"CoGoAll.Seed.{ctx_['run_id']}.a{ctx_['attempt']}"
    try:
        require(db.enqueue(work_id(ctx_), ctx_["source_commit"], src, START) == "ENQUEUED",
                "HOLD_ENQUEUE")
        claims = db.claim_due(now=START, owner=owner,
                              lease_seconds=EXPIRY - START, limit=1)
        require(len(claims) == 1, "HOLD_LEASE_MISSING")
        claim = claims[0]
        require(claim.work_id == work_id(ctx_) and claim.epoch == 1
                and claim.lease_until == EXPIRY, "HOLD_WRONG_LEASE")
        require(db.snapshot(START)["complete"] == 0, "HOLD_PRECOMPLETED")
    finally:
        db.close()
    queue = bundle / "queue.sqlite"
    require(queue.is_file() and not queue.is_symlink(), "HOLD_QUEUE_ABSENT")
    require({x.name for x in bundle.iterdir()} == {"queue.sqlite"},
            "HOLD_QUEUE_SIDECAR_UNEXPECTED")
    manifest = {
        "schema": SCHEMA, "work_id": work_id(ctx_), "source_commit": ctx_["source_commit"],
        "source_sha256": src, "run_id": ctx_["run_id"], "attempt": ctx_["attempt"],
        "queue_sha256": sha(queue.read_bytes()), "lease_owner": owner,
        "lease_epoch": 1, "lease_until": EXPIRY,
        "effect_executed": False, "external_receiver_ack": False,
        "provider_scope": "SAME_GITHUB_ACTIONS", "clock_scope": "SYNTHETIC_VIRTUAL_SECONDS",
    }
    with (bundle / "manifest.json").open("xb") as stream:
        stream.write(serialize(manifest))
        stream.flush()
        os.fsync(stream.fileno())
    return manifest


def read_manifest(bundle: Path, ctx_: dict, root: Path) -> dict:
    require(bundle.is_dir() and not bundle.is_symlink(), "HOLD_BUNDLE_ABSENT")
    require({x.name for x in bundle.iterdir()} == {"queue.sqlite", "manifest.json"},
            "HOLD_BUNDLE_UNEXPECTED_OBJECT")
    manfile, dbfile = bundle / "manifest.json", bundle / "queue.sqlite"
    require(all(f.is_file() and not f.is_symlink() and 0 < f.stat().st_size <= LIMIT
                for f in (manfile, dbfile)), "HOLD_BUNDLE_FILE")
    try:
        manifest = json.loads(manfile.read_bytes())
    except (ValueError, UnicodeDecodeError) as exc:
        raise Held("HOLD_BAD_MANIFEST_JSON") from exc
    require(isinstance(manifest, dict) and set(manifest) == FIELDS
            and manifest["schema"] == SCHEMA, "HOLD_MANIFEST_SCHEMA")
    require(manifest["run_id"] == ctx_["run_id"]
            and manifest["attempt"] == ctx_["attempt"]
            and manifest["source_commit"] == ctx_["source_commit"]
            and manifest["work_id"] == work_id(ctx_),
            "HOLD_CROSS_RUN_OR_SOURCE")
    require(manifest["provider_scope"] == "SAME_GITHUB_ACTIONS"
            and manifest["clock_scope"] == "SYNTHETIC_VIRTUAL_SECONDS"
            and manifest["effect_executed"] is False
            and type(manifest["effect_executed"]) is bool
            and manifest["external_receiver_ack"] is False
            and type(manifest["external_receiver_ack"]) is bool,
            "HOLD_AUTHORITY_INFLATION")
    require(manifest["source_sha256"] == source_digest(root),
            "HOLD_SOURCE_DRIFT")
    require(manifest["queue_sha256"] == sha(dbfile.read_bytes()),
            "HOLD_QUEUE_TAMPER")
    require(type(manifest["lease_epoch"]) is int and manifest["lease_epoch"] == 1
            and type(manifest["lease_until"]) is int
            and manifest["lease_until"] == EXPIRY
            and manifest["lease_owner"] ==
                f"CoGoAll.Seed.{ctx_['run_id']}.a{ctx_['attempt']}",
            "HOLD_LEASE_FIELDS")
    return manifest


def recover(root: Path, bundle: Path, receipt: Path, ctx_: dict) -> dict:
    require(not receipt.exists() and not receipt.is_symlink(),
            "HOLD_RECEIPT_EXISTS")
    manifest = read_manifest(bundle, ctx_, root)
    queue = DueWorkQueue(str(bundle / "queue.sqlite"))
    try:
        rows = queue.db.execute("""SELECT work_id,source_revision,payload_sha256,
            due_at,state,epoch,owner,lease_until,result_sha256,completed_at FROM work""").fetchall()
        require(rows == [(manifest["work_id"], ctx_["source_commit"],
                          manifest["source_sha256"], START, "LEASED", 1,
                          manifest["lease_owner"], EXPIRY, None, None)],
                "HOLD_UNFINISHED_WORK_MISMATCH")
        require(queue.claim_due(now=EXPIRY - 1, owner="too-early") == [],
                "HOLD_EARLY_RECLAIM")
        successor_owner = f"CoGoAll.Recover.{ctx_['run_id']}.a{ctx_['attempt']}"
        claims = queue.claim_due(now=EXPIRY, owner=successor_owner, lease_seconds=30)
        require(len(claims) == 1, "HOLD_SUCCESSOR_NOT_ELECTED")
        successor = claims[0]
        require(successor.work_id == manifest["work_id"]
                and successor.epoch == 2 and successor.lease_until == EXPIRY+30,
                "HOLD_SUCCESSOR_FENCE")
        stale = Claim(manifest["work_id"], ctx_["source_commit"],
                      manifest["source_sha256"], 1, manifest["lease_owner"], EXPIRY)
        stale_result = queue.complete(stale, result_sha256=sha(b"stale-attempt"),
                                      now=FINISH)
        require(stale_result == "FENCED", "HOLD_STALE_WRITER_NOT_FENCED")
        result = sha(serialize({"kind": "READ_ONLY_SOURCE_SHA_VERIFICATION",
                                "source_sha256": manifest["source_sha256"],
                                "work_id": manifest["work_id"]}))
        committed = queue.complete(successor, result_sha256=result, now=FINISH)
        require(committed == "COMMITTED_LOCAL_ONLY", "HOLD_RECOVERY_FAILED")
        replay = queue.complete(successor, result_sha256=result, now=FINISH + 1)
        require(replay == "REPLAY" and queue.claim_due(now=1000, owner="third") == [],
                "HOLD_DUPLICATE_EXECUTION")
        snap = queue.snapshot(1000)
        require(snap["total"] == 1 and snap["complete"] == 1
                and snap["next_wake"] is None
                and snap["external_effect_verified"] is False
                and snap["independent_receiver_ack"] is False,
                "HOLD_RECOVERY_SNAPSHOT")
    finally:
        queue.close()
    data = {
        "schema": RESULT_SCHEMA,
        "state": "SAME_PROVIDER_UNFINISHED_LEASE_RECOVERED_ACROSS_CI_JOBS",
        "work_id": manifest["work_id"], "source_commit": ctx_["source_commit"],
        "source_sha256": manifest["source_sha256"],
        "seed_manifest_sha256": sha((bundle / "manifest.json").read_bytes()),
        "seed_queue_sha256": manifest["queue_sha256"],
        "final_queue_sha256": sha((bundle / "queue.sqlite").read_bytes()),
        "recovered_epoch": 2, "lease_expired_at_virtual_time": EXPIRY,
        "old_worker_fenced": True, "successor_completion": committed,
        "successor_replay": replay, "completed_work_ids": 1,
        "external_effects": 0, "external_receiver_ack": False,
        "independent_provider_receiver": False, "distinct_workflow_run": False,
        "clock_scope": "SYNTHETIC_VIRTUAL_SECONDS",
        "provider_scope": "SAME_GITHUB_ACTIONS",
        "x2_runtime_qualified": False, "coex": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open("xb") as stream:
        stream.write(serialize(data))
        stream.flush()
        os.fsync(stream.fileno())
    return data


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("seed", "recover"))
    p.add_argument("--root", default=".")
    p.add_argument("--bundle", required=True)
    p.add_argument("--readback")
    a = p.parse_args()
    try:
        root = Path(a.root).resolve(strict=True)
        role = "unfinished-seed" if a.mode == "seed" else "unfinished-recover"
        context = ctx(root, os.environ, role)
        if a.mode == "seed":
            data = seed(root, Path(a.bundle), context)
        else:
            require(bool(a.readback), "HOLD_READBACK_PATH_REQUIRED")
            data = recover(root, Path(a.bundle), Path(a.readback), context)
        print(json.dumps(data, sort_keys=True))
        return 0
    except (Held, TypeError, ValueError, OSError, sqlite3.Error,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)[:140],
                          "external_receiver_ack": False}, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
