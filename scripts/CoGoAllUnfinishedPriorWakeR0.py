#!/usr/bin/env python3
"""Recover one PINNED unfinished WorkID from a different GitHub workflow run.

The run ID, SHA and artifact metadata are fixed evidence constraints. This
may verify a second GitHub run without falsely claiming independent-provider
custody, real elapsed lease time, or any external effect. No scheduler added.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess

from scripts.CoGoAllUnfinishedCanaryR0 import (
    Held, require, sha, serialize, ctx, read_manifest, recover, SOURCE,
)

PIN = {
    "run_id": "43113671112",
    "attempt": "1",
    "source_commit": "6ca5f069ca0e0cf7f9ae6985b2e16a28cf579e6f",
    "work_id": "CoGoAll.Unfinished.43113671112.a1",
    "source_sha256": "30129e630e73359bbe476d61e21cff4f5e7a8992cd1a79630c001a7de6bf84e4",
    "manifest_sha256": "eda81823dd2e2f07401bbe22bb9d43de19c0d1656921d8af55047f89c8a53599",
    "queue_sha256": "f54e89033aa68c9c94ce803feb41a1bcd70a71bb3c4ec444ee4a92f69dfeed04",
    "artifact_id": 13896878596,
    "artifact_name": "cogoall-unfinished-43113671112-a1",
    "artifact_digest": "sha256:df10aa56be73cb131aa78cecf341dd4b329edabd6f1822711c755335fa9e813e",
}
RESULT_SCHEMA = "CoGoAll.UnfinishedPriorWorkflowReadback.R0"
MAX_META = 32768


def regular_bytes(file: Path, limit: int = MAX_META) -> bytes:
    require(file.is_file() and not file.is_symlink(), "HOLD_PRIOR_FILE_NOT_REGULAR")
    require(0 < file.stat().st_size <= limit, "HOLD_PRIOR_FILE_SIZE")
    data = file.read_bytes()
    require(0 < len(data) <= limit, "HOLD_PRIOR_FILE_SIZE")
    return data


def verified_original(current_root: Path, historical_root: Path,
                      bundle: Path, metadata_file: Path,
                      current_ctx: dict, pin: dict = PIN) -> dict:
    root = current_root.resolve(strict=True)
    require(current_ctx["run_id"] != pin["run_id"], "HOLD_NOT_DISTINCT_RUN")
    require(historical_root.is_dir() and not historical_root.is_symlink(),
            "HOLD_PINNED_SOURCE_NOT_DIRECTORY")
    old = historical_root.resolve(strict=True)
    require(old != root and old.is_relative_to(root), "HOLD_SOURCE_OUTSIDE_ROOT")
    require(bundle.is_dir() and not bundle.is_symlink()
            and bundle.resolve().is_relative_to(root), "HOLD_ARCHIVE_OUTSIDE_ROOT")
    require(metadata_file.is_file() and not metadata_file.is_symlink()
            and metadata_file.resolve().is_relative_to(root), "HOLD_METADATA_OUTSIDE_ROOT")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=old,
                          text=True, capture_output=True, timeout=10,
                          check=False)
    require(head.returncode == 0 and head.stdout.strip() == pin["source_commit"],
            "HOLD_PINNED_GIT_COMMIT_MISMATCH")
    try:
        meta = json.loads(regular_bytes(metadata_file))
    except (ValueError, UnicodeDecodeError) as exc:
        raise Held("HOLD_ARTIFACT_META_JSON") from exc
    require(isinstance(meta, dict)
            and meta.get("id") == pin["artifact_id"]
            and meta.get("name") == pin["artifact_name"]
            and meta.get("digest") == pin["artifact_digest"]
            and meta.get("expired") is False
            and isinstance(meta.get("workflow_run"), dict)
            and str(meta["workflow_run"].get("id")) == pin["run_id"],
            "HOLD_ARCHIVE_METADATA_MISMATCH")
    require(sha(regular_bytes(bundle / "manifest.json")) == pin["manifest_sha256"],
            "HOLD_MANIFEST_DIGEST")
    require(sha(regular_bytes(bundle / "queue.sqlite", limit=2_000_000))
            == pin["queue_sha256"], "HOLD_QUEUE_DIGEST")
    previous_ctx = {"run_id": pin["run_id"], "attempt": pin["attempt"],
                    "source_commit": pin["source_commit"]}
    manifest = read_manifest(bundle, previous_ctx, old)
    require(manifest["work_id"] == pin["work_id"]
            and manifest["source_sha256"] == pin["source_sha256"],
            "HOLD_PINNED_WORKID_OR_SOURCE")
    return previous_ctx


def recover_previous(current_root: Path, historical_root: Path,
                     bundle: Path, metadata_file: Path,
                     stage_receipt: Path, final_receipt: Path,
                     current_ctx: dict, pin: dict = PIN) -> dict:
    require(not stage_receipt.exists() and not stage_receipt.is_symlink()
            and not final_receipt.exists() and not final_receipt.is_symlink(),
            "HOLD_EXISTING_RECEIPT")
    previous_ctx = verified_original(current_root, historical_root, bundle,
                                     metadata_file, current_ctx, pin)
    # This operates only on the downloaded COPY, never the archived prior ZIP.
    earlier = recover(historical_root, bundle, stage_receipt, previous_ctx)
    require(earlier["state"] == "SAME_PROVIDER_UNFINISHED_LEASE_RECOVERED_ACROSS_CI_JOBS"
            and earlier["work_id"] == pin["work_id"]
            and earlier["old_worker_fenced"] is True
            and earlier["completed_work_ids"] == 1
            and earlier["external_receiver_ack"] is False,
            "HOLD_UNFINISHED_RECOVERY_NOT_QUALIFIED")
    report = {
        "schema": RESULT_SCHEMA,
        "state": "SAME_PROVIDER_PINNED_UNFINISHED_WORK_RECOVERED_IN_LATER_RUN",
        "prior_run_id": pin["run_id"],
        "current_run_id": current_ctx["run_id"],
        "prior_source_commit": pin["source_commit"],
        "current_source_head": current_ctx["source_commit"],
        "work_id": pin["work_id"],
        "prior_artifact_id": pin["artifact_id"],
        "prior_artifact_digest": pin["artifact_digest"],
        "prior_manifest_sha256": pin["manifest_sha256"],
        "original_queue_sha256": pin["queue_sha256"],
        "stage_readback_sha256": sha(regular_bytes(stage_receipt)),
        "recovered_queue_sha256": earlier["final_queue_sha256"],
        "distinct_workflow_run": True,
        "prior_unfinished_state_qualified": True,
        "expired_owner_fenced": True,
        "completed_work_ids": 1,
        "new_external_effect_executed": False,
        "source_drift_override": False,
        "provider_failure_domain": "SAME_GITHUB_ACTIONS",
        "archive_integrity_scope": "PINNED_EXTRACTED_FILES_AND_GITHUB_METADATA",
        "actual_lease_elapsed_time_verified": False,
        "virtual_lease_expiry": True,
        "independent_receiver_ack": False,
        "x2_runtime_qualified": False,
        "coex": False,
    }
    final_receipt.parent.mkdir(parents=True, exist_ok=True)
    with final_receipt.open("xb") as stream:
        stream.write(serialize(report))
        stream.flush()
        os.fsync(stream.fileno())
    return report


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--historical-root", required=True)
    p.add_argument("--bundle", required=True)
    p.add_argument("--metadata", required=True)
    p.add_argument("--stage-readback", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    try:
        root = Path(a.root).resolve(strict=True)
        data = recover_previous(
            root, Path(a.historical_root), Path(a.bundle), Path(a.metadata),
            Path(a.stage_readback), Path(a.output),
            current_ctx=ctx(root, os.environ, "unfinished-prior-wake"),
        )
        print(json.dumps(data, sort_keys=True))
        return 0
    except (Held, TypeError, ValueError, OSError, sqlite3.Error,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)[:140],
                          "independent_receiver_ack": False}, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
