#!/usr/bin/env python3
"""CoPayload Large Path R0: bounded offline eligibility + checkpoint canary.

No native mouse hook, clipboard use, provider calls, file upload, background
processes, or actual multi-GiB allocation. All large cases are descriptors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "CoPayload.LargePathCanary.R0"
GIB = 1024 ** 3
MAX_SOURCE_BYTES = 16 * GIB
MAX_STAGE_BYTES = 2 * GIB
MAX_FILES = 4
MAX_CYCLES = 3
SMALL_INLINE_BYTES = 64 * 1024
CHUNK_BYTES = 4 * 1024 * 1024
KINDS = {"VIDEO", "AUDIO", "IMAGE", "DOCUMENT", "SOURCE", "ARCHIVE", "DATASET", "FILE"}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def descriptor(name: str, size: int, kind: str, *, privacy: str = "PRIVATE") -> dict:
    if not isinstance(name, str) or not name or len(name) > 256:
        raise ValueError("invalid logical name")
    if type(size) is not int or size < 0:
        raise ValueError("size must be a nonnegative integer")
    if kind not in KINDS or privacy not in {"PRIVATE", "PUBLIC_SAFE_CANDIDATE", "UNKNOWN"}:
        raise ValueError("unrecognized type or privacy classification")
    return {"name": name, "declared_bytes": size, "kind": kind, "privacy": privacy}


def plan(items: list[dict], mode: str) -> dict:
    if mode not in {"REFERENCE_ONLY", "STAGE_BYTES"}:
        raise ValueError("unknown transfer mode")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_FILES:
        raise ValueError("source count must be 1..4")
    parsed = []
    for x in items:
        if not isinstance(x, dict) or set(x) != {"name", "declared_bytes", "kind", "privacy"}:
            raise ValueError("unknown or missing descriptor fields")
        parsed.append(descriptor(x["name"], x["declared_bytes"], x["kind"], privacy=x["privacy"]))
    total = sum(x["declared_bytes"] for x in parsed)
    size_ok = all(x["declared_bytes"] <= MAX_SOURCE_BYTES for x in parsed) and total <= MAX_SOURCE_BYTES
    stage_ok = mode == "REFERENCE_ONLY" or (total <= MAX_STAGE_BYTES and all(x["declared_bytes"] <= MAX_STAGE_BYTES for x in parsed))
    allowed = size_ok and stage_ok
    reasons = []
    if not size_ok: reasons.append("SOURCE_HASHING_LIMIT_16_GIB")
    if not stage_ok: reasons.append("STAGING_LIMIT_2_GIB")
    rows = []
    for x in parsed:
        n = x["declared_bytes"]
        rows.append({
            **x,
            "estimated_chunks_4mib": (n + CHUNK_BYTES - 1) // CHUNK_BYTES,
            "payload_mode": ("SMALL_INLINE_CANDIDATE" if n <= SMALL_INLINE_BYTES else
                             "FILE_BACKED_REFERENCE" if mode == "REFERENCE_ONLY" else "STAGED_FILE_CANDIDATE"),
            "actual_file_sha256": None,
            "actual_bytes_read": 0,
            "file_existed_or_was_staged": False,
            "privacy_review": "NOT_PERFORMED",
        })
    return {
        "schema": SCHEMA,
        "state": "ELIGIBLE_LOGICAL_ONLY" if allowed else "HOLD_LIMIT",
        "mode": mode,
        "total_declared_bytes": total,
        "qualified": allowed,
        "hold_reasons": reasons,
        "items": rows,
        "source_files_opened": 0,
        "staged_bytes": 0,
        "receiver_ack": False,
        "external_effects": 0,
        "native_thumb_binding": "NOT_TESTED",
        "reality_boundaries": ["DESCRIPTOR_NE_FILE", "CHUNK_ESTIMATE_NE_ALLOCATION",
                               "PAYLOAD_POINTER_NE_PAYLOAD", "PREPARED_NE_SENT",
                               "LOGICAL_CAPACITY_NE_MEASURED_THROUGHPUT"],
    }


def inspect_real_file(path: Path) -> dict:
    """Read and hash one explicitly provided regular file; no byte staging."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or path.is_symlink():
        raise ValueError("regular non-symlink file required")
    if before.st_size > MAX_SOURCE_BYTES:
        raise ValueError("source exceeds R1 hashing ceiling")
    h = hashlib.sha256()
    read_count = 0
    chunks = 0
    with path.open("rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("source changed type during open")
        while True:
            piece = handle.read(CHUNK_BYTES)
            if not piece:
                break
            read_count += len(piece)
            chunks += 1
            if read_count > MAX_SOURCE_BYTES:
                raise ValueError("source grew beyond budget")
            h.update(piece)
        opened = os.fstat(handle.fileno())
    after = path.lstat()
    if (before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns
        or before.st_dev != after.st_dev or before.st_ino != after.st_ino
        or opened.st_size != before.st_size or read_count != before.st_size):
        raise ValueError("source changed during read")
    return {"sha256": h.hexdigest(), "bytes_read": read_count, "chunks_read": chunks,
            "read_proof": "LOCAL_STREAM_HASH_ONLY", "staged_bytes": 0,
            "external_effects": 0, "path_disclosed": False}


def fixtures() -> list[tuple[str, list[dict], str, bool]]:
    one = lambda name, n: [descriptor(name, n, "VIDEO")]
    return [
        ("small_inline", one("short", SMALL_INLINE_BYTES), "REFERENCE_ONLY", True),
        ("file_backed_300k", one("media", 300 * 1024 + 1), "REFERENCE_ONLY", True),
        ("stage_at_2gib", one("max_stage", MAX_STAGE_BYTES), "STAGE_BYTES", True),
        ("stage_over_2gib", one("over_stage", MAX_STAGE_BYTES + 1), "STAGE_BYTES", False),
        ("ref_at_16gib", one("max_ref", MAX_SOURCE_BYTES), "REFERENCE_ONLY", True),
        ("ref_over_16gib", one("over_ref", MAX_SOURCE_BYTES + 1), "REFERENCE_ONLY", False),
        ("aggregate_over_limit", [descriptor("half", MAX_SOURCE_BYTES // 2 + 1, "ARCHIVE"),
                                   descriptor("other", MAX_SOURCE_BYTES // 2, "ARCHIVE")], "REFERENCE_ONLY", False),
        ("four_file_reference", [descriptor("part" + str(i), i + 1, "DATASET") for i in range(4)], "REFERENCE_ONLY", True),
    ]


def execute(cycles: int = 3) -> dict:
    if type(cycles) is not int or not 1 <= cycles <= MAX_CYCLES:
        raise ValueError("cycles must be 1..3; no background scheduler")
    cases = fixtures()
    base_results = None
    history = []
    prev_digest = "GENESIS"
    for cycle in range(1, cycles + 1):
        results = []
        for name, items, mode, expected in cases:
            result = plan(items, mode)
            works = result["qualified"] is expected
            results.append({"test": name, "outcome": "PASS" if works else "FAIL",
                            "expected_eligible": expected, "observed_eligible": result["qualified"],
                            "hold_reasons": result["hold_reasons"], "payload_plan_sha256": sha(canonical(result))})
        normalized = sha(canonical(results))
        if base_results is None:
            base_results = normalized
        stable = normalized == base_results
        event = {"schema": "CoPayload.BenchmarkEvo.R0", "cycle": cycle,
                 "evidence_class": "SYNTHETIC_DESCRIPTOR_ONLY",
                 "status": "PASS" if stable and all(x["outcome"] == "PASS" for x in results) else "FAIL",
                 "source_contract": "CoThumbCoCopyR1 16GiB read-only / 2GiB stage, up to 4 files",
                 "results": results,
                 "previous_event_sha256": prev_digest,
                 "normalized_result_sha256": normalized,
                 "executed_workers": 0, "external_effects": 0, "nas_pickup": False,
                 "physical_button_verified": False}
        prev_digest = sha(canonical(event))
        history.append(event)
    return {"schema": SCHEMA, "cycles": cycles, "status": history[-1]["status"],
            "history": history, "last_sha256": prev_digest,
            "nonclaims": ["DESCRIPTOR_NE_REAL_16GIB_FILE_TEST", "REPEATED_CYCLES_NE_ALWAYS_ON_AUTONOMY",
                          "NO_FFPROBE_OR_BLACKDETECT_RERUN", "NO_CLAUDE_PI_CREDENTIAL_PROBE",
                          "NO_OLLAMA_INFERENCE", "NO_COORBWARE_OR_HARDWARE_MAPPING",
                          "NO_NAS_OR_EXTERNAL_RECEIVER_ACK"]}


def write_new(path: Path, content: bytes) -> None:
    # Parent must already exist. No clobber even on repeated invocation.
    with path.open("xb") as f:
        f.write(content)
        f.flush()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cycles", type=int, default=3)
    ap.add_argument("--output", type=Path, required=True, help="new .jsonl file, parent must exist")
    ap.add_argument("--summary", type=Path, required=True, help="new JSON file, parent must exist")
    ap.add_argument("--sample-file", type=Path, help="optional explicit local, non-sensitive file to hash without sending")
    args = ap.parse_args()
    if args.output.resolve() == args.summary.resolve():
        ap.error("output and summary must be distinct")
    if args.output.exists() or args.summary.exists():
        ap.error("output exists: no clobber")
    result = execute(args.cycles)
    real_probe = inspect_real_file(args.sample_file) if args.sample_file else None
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [dict(event, observed_utc=stamp) for event in result["history"]]
    write_new(args.output, b"".join(canonical(event) + b"\n" for event in rows))
    write_new(args.summary, canonical({"status": result["status"], "cycles": result["cycles"],
                                       "sha256": result["last_sha256"], "real_file_readproof": real_probe, "nonclaims": result["nonclaims"]}) + b"\n")
    print(json.dumps({"status": result["status"], "cycles": result["cycles"],
                      "cases_per_cycle": len(fixtures()), "effects": 0, "real_file_readproof": real_probe,
                      "output": str(args.output), "summary": str(args.summary)}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
