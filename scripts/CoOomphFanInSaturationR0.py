#!/usr/bin/env python3
"""CoOomph bounded fan-in measurement using the existing exact CoSession compiler.

This creates synthetic records only. No models, workers, sessions, receivers, messages,
deletions, account actions or external effects are invoked. Times measure the runner,
NOT provider inference, receiver value or production throughput.
"""
import argparse
import hashlib
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from CoSessionRelationalFanIn import compile_fanin

COMPILER_BLOB = "690cba4811eb8f4cf8cb6f4b1d4b52d8b6776002"
MODES = ("echo", "diverse", "pool32", "collision4", "private")
MAX_SIZE = 256
NONCLAIMS = [
    "LOGICAL_PROPOSAL_NE_ACTIVE_AI_SESSION",
    "UNIQUE_OPERATION_HASH_NE_VERIFIED_USEFUL_RESULT",
    "COLLISION_CANDIDATE_NE_PROVEN_CONTRADICTION",
    "SIMULATED_REVIEW_BUDGET_NE_LIVE_RECEIVER_CAPACITY",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_REAL_WORLD_EFFECTS_OR_EXPONENTIAL_SPEEDUP_CLAIM",
]


def check_source():
    data = (HERE / "CoSessionRelationalFanIn.py").read_bytes()
    git_blob = hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()
    if git_blob != COMPILER_BLOB:
        raise ValueError("FANIN_COMPILER_SOURCE_DRIFT_HOLD")
    return git_blob


def build_fixture(count, mode):
    if type(count) is not int or count < 1 or count > MAX_SIZE:
        raise ValueError("BOUNDED_COUNT_REQUIRED")
    if mode not in MODES:
        raise ValueError("UNKNOWN_MODE")
    deltas = []
    for i in range(count):
        if mode == "echo":
            subject, relation, object_id = "synthetic:shared", "proposes", "candidate:one"
        elif mode == "diverse" or mode == "private":
            subject, relation, object_id = f"synthetic:item:{i}", "proposes", f"candidate:{i}"
        elif mode == "pool32":
            subject, relation, object_id = f"synthetic:item:{i % 32}", "proposes", f"candidate:{i % 32}"
        else:
            subject, relation, object_id = "synthetic:question", "proposes", f"candidate:{i % 4}"
        deltas.append({
            "delta_id": f"synthetic:{mode}:{i}",
            "source_session": f"logical:{i}",
            "created_at": "2026-11-11T20:54:08Z",
            "target_domains": ["synthetic"],
            "operations": [{
                "op": "ADD", "subject": subject, "relation": relation,
                "object": object_id, "evidence_refs": ["synthetic://only"]
            }],
            "authority_ceiling": "CANDIDATE_ONLY",
            "public_safety": "PRIVATE_ONLY" if mode == "private" else "PUBLIC_SAFE",
            "nonclaims": ["SYNTHETIC_ONLY"],
            "next_gate": "INDEPENDENT_REVIEW",
        })
    return {"deltas": deltas}


def sample(count, mode, review_slots=8):
    if type(review_slots) is not int or not 1 <= review_slots <= 100:
        raise ValueError("REVIEW_BUDGET_BOUND_REQUIRED")
    compiler_blob = check_source()
    fixture = build_fixture(count, mode)
    # This temporary fixture is generated on the CI runner, not on X2/CoStead.
    with tempfile.TemporaryDirectory(prefix="cooomph-synthetic-") as dirname:
        path = Path(dirname) / "synthetic.json"
        path.write_text(json.dumps(fixture, sort_keys=True), encoding="utf-8")
        t0 = time.perf_counter()
        outcome = compile_fanin([str(path)])
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
    coverage = outcome["coverage"]
    if coverage["accepted_deltas"] != count or coverage["rejected_records"] != 0:
        raise ValueError("UNEXPECTED_COMPILE_REJECTION")
    if any(outcome["effects"].values()):
        raise ValueError("EFFECTS_NOT_ZERO")
    collision_hashes = {
        ref["operation_sha256"]
        for group in outcome["collision_candidates"]
        for variant in group["variants"]
        for ref in variant["refs"]
    }
    eligible_delta_ids = set(outcome["eligible_public_review_delta_ids"])
    candidate_hashes = {
        item["operation_sha256"]
        for item in outcome["unique_operations"]
        if item["operation_sha256"] not in collision_hashes
        and any(
            ref["delta_id"] in eligible_delta_ids
            for op_hash_group in [item["operation_sha256"]]
            for refs in outcome["duplicate_operation_groups"]
            if refs["operation_sha256"] == op_hash_group
            for ref in refs["refs"]
        )
    }
    # Unique operations lacking a duplicate group still need their own public origin.
    for item in outcome["unique_operations"]:
        if (item["operation_sha256"] not in collision_hashes
                and item["delta_id"] in eligible_delta_ids):
            candidate_hashes.add(item["operation_sha256"])
    # Every synthetic mode is uniform-public or uniform-private. No mixed-origin
    # coalescing is permitted by this canary.
    if mode == "private" and candidate_hashes:
        raise ValueError("PRIVATE_CANDIDATE_ESCAPED_HOLD")
    candidates = len(candidate_hashes)
    return {
        "mode": mode,
        "logical_proposals": count,
        "accepted_schema_records": coverage["accepted_deltas"],
        "unique_operation_candidates": coverage["unique_operations"],
        "duplicate_groups": coverage["duplicate_operation_groups"],
        "collision_review_groups": coverage["collision_candidates"],
        "public_holds": coverage["public_fanout_holds"],
        "eligible_unique_review_candidates": candidates,
        "hypothetical_review_slots_per_wave": review_slots,
        "hypothetical_next_wave_backlog": max(0, candidates - review_slots),
        "candidate_uniqueness_ratio": round(coverage["unique_operations"] / count, 5),
        "compiler_wall_ms_runner_only": elapsed_ms,
        "compiled_sha256": outcome["compiled_sha256"],
        "compiler_git_blob": compiler_blob,
        "real_worker_sessions_started": 0,
        "external_receiver_ack": False,
        "real_effects": 0,
    }


def run(sizes=(1, 18, 64, 256), review_slots=8):
    if not isinstance(sizes, (list, tuple)) or not 1 <= len(sizes) <= 8:
        raise ValueError("BOUNDED_SIZE_SET_REQUIRED")
    rows = [sample(n, mode, review_slots) for n in sizes for mode in MODES]
    return {
        "schema": "CoAll.CoOomph.FanInSaturationCanary.R0",
        "state": "SYNTHETIC_COMPILER_COUNTS_AND_RUNNER_TIME_ONLY",
        "compiler_git_blob": COMPILER_BLOB,
        "rows": rows,
        "real_workers_started": 0,
        "external_receiver_ack": False,
        "real_effects": 0,
        "nonclaims": NONCLAIMS,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--review-slots", type=int, default=8)
    args = p.parse_args()
    print(json.dumps(run(review_slots=args.review_slots), indent=2, sort_keys=True))
