#!/usr/bin/env python3
"""CoStretch+ R1. Bounded, standard-library-only offline benchmark.

No network, hardware discovery, provider calls, process spawning, credentials,
external account operations or background work. Evaluates trillions of *logical*
configuration addresses without enumerating them. Executor max_threads=4.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

AXES = ("work", "substrate", "time", "observer", "verification", "recovery",
        "resource", "audience", "privacy", "accessibility", "failure", "representation")
RADIX = 10
CARDINALITY = RADIX ** len(AXES)
MAX_WIDTH = 4
TASKS = 160
PAYLOAD_SIZE = 256 * 1024
TURTLE_DEPTH = 50000


def decode_index(index: int) -> tuple[int, ...]:
    if not 0 <= index < CARDINALITY:
        raise ValueError("logical candidate outside address space")
    digits = []
    for _ in AXES:
        index, digit = divmod(index, RADIX)
        digits.append(digit)
    return tuple(digits)


def encode_index(digits: tuple[int, ...]) -> int:
    if len(digits) != len(AXES) or any(not 0 <= d < RADIX for d in digits):
        raise ValueError("invalid address vector")
    return sum(d * RADIX ** i for i, d in enumerate(digits))


def task_digest(task_id: int, *, force_once: bool = False, attempt: int = 1) -> str:
    if force_once and attempt == 1:
        raise RuntimeError("injected transient fault")
    block = f"CoStretch-R1-task:{task_id:06d}|".encode("ascii")
    payload = (block * ((PAYLOAD_SIZE // len(block)) + 1))[:PAYLOAD_SIZE]
    return hashlib.sha256(payload).hexdigest()


def run_batch(width: int, task_count: int = TASKS, fault_task: int | None = None,
              max_attempts: int = 2) -> dict:
    if width not in (1, 2, 4):
        raise ValueError("this bounded test permits only width 1,2,4")
    if not 0 <= task_count <= TASKS:
        raise ValueError("out-of-bounds task count")
    indices = list(range(task_count))
    attempts = {i: 0 for i in indices}
    results: dict[int, str] = {}
    failures: list[int] = []
    started = time.perf_counter()

    def apply(i: int) -> tuple[int, str | None]:
        attempts[i] += 1
        try:
            return (i, task_digest(i, force_once=(i == fault_task), attempt=attempts[i]))
        except RuntimeError:
            return (i, None)

    outstanding = indices
    while outstanding:
        if width == 1:
            batch = [apply(i) for i in outstanding]
        else:
            with ThreadPoolExecutor(max_workers=width) as pool:
                batch = list(pool.map(apply, outstanding))
        outstanding = []
        for i, answer in batch:
            if answer is not None:
                results[i] = answer
            elif attempts[i] < max_attempts:
                outstanding.append(i)
            else:
                failures.append(i)
    elapsed = time.perf_counter() - started
    assert len(results) + len(failures) == task_count
    root = hashlib.sha256("|".join(results[i] for i in sorted(results)).encode()).hexdigest()
    return {
        "width": width, "task_count": task_count, "completed": len(results),
        "failed": failures, "retries": sum(a-1 for a in attempts.values()),
        "elapsed_s": round(elapsed, 6),
        "verified_items_per_s": round(len(results) / elapsed, 3) if elapsed else None,
        "digest_root": root,
    }


def turtle_root(depth: int, *, checkpoint_at: int | None = None) -> tuple[str, str | None]:
    if not 0 <= depth <= TURTLE_DEPTH:
        raise ValueError("out-of-bounds turtle depth")
    state = hashlib.sha256(b"CoTurtle-R1-genesis").digest()
    checkpoint = None
    for i in range(depth):
        state = hashlib.sha256(state + i.to_bytes(8, "big")).digest()
        if checkpoint_at == i + 1:
            checkpoint = state.hex()
    return state.hex(), checkpoint


def resume_turtle(checkpoint: str, start_index: int, depth: int) -> str:
    state = bytes.fromhex(checkpoint)
    for i in range(start_index, depth):
        state = hashlib.sha256(state + i.to_bytes(8, "big")).digest()
    return state.hex()


def record(name: str, status: str, *, observed: dict | None = None,
           expected: str | None = None, proof_class: str = "ISOLATED_WORKBENCH_TEST") -> dict:
    return {
        "schema": "CoAll.CoStretch.BenchmarkEvo.v0.1", "test": name,
        "status": status, "proof_class": proof_class,
        "observed": observed or {}, "expected": expected,
        "boundary": "OFFLINE_BOUNDED_FIXTURE_NOT_PRODUCTION_NOT_X2_CALIBRATION",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    items = []
    rng = random.Random(20261023)
    selected = [0, 1, 9, 10, CARDINALITY - 2, CARDINALITY - 1]
    selected += [rng.randrange(CARDINALITY) for _ in range(1024)]
    t0 = time.perf_counter()
    correct = all(encode_index(decode_index(i)) == i for i in selected)
    logical_elapsed = time.perf_counter() - t0
    items.append(record("trillion_logical_addresses", "PASS" if correct else "FAIL", observed={
        "axes": len(AXES), "options_per_axis": RADIX,
        "addressable_candidates": CARDINALITY, "sampled": len(selected),
        "elapsed_s": round(logical_elapsed, 6), "physical_workers_created": 0,
    }, expected="Exact encode/decode; no candidate materialization"))

    serial = run_batch(1)
    fixed2 = run_batch(2)
    fixed4 = run_batch(4)
    outputs_equal = serial["digest_root"] == fixed2["digest_root"] == fixed4["digest_root"]
    for label, outcome in (("serial", serial), ("fixed_2", fixed2), ("fixed_4", fixed4)):
        items.append(record("queue_output_" + label,
            "PASS" if outputs_equal and outcome["completed"] == TASKS and not outcome["failed"] else "FAIL",
            observed=outcome, expected="160 matching verified task digests; width capped at 4"))
    items.append(record("width_4_is_always_faster", "FAIL", proof_class="UNSUPPORTED_GENERALIZATION",
        observed={"serial_elapsed_s": serial["elapsed_s"], "four_elapsed_s": fixed4["elapsed_s"],
                  "single_short_run": True},
        expected="Repeat across workload types, environments and time; isolated sample insufficient"))

    recovered = run_batch(4, fault_task=7)
    items.append(record("transient_worker_failure_recovery",
        "PASS" if recovered["digest_root"] == serial["digest_root"] and recovered["retries"] == 1 and not recovered["failed"] else "FAIL",
        observed=recovered, expected="Exactly one injected retry; final digest equals baseline"))
    permanent = run_batch(2, task_count=32, fault_task=7, max_attempts=1)
    items.append(record("failure_exhaustion_fails_closed",
        "PASS" if permanent["failed"] == [7] and permanent["completed"] == 31 else "FAIL",
        observed=permanent, expected="Task 7 remains failed and is never called complete"))

    root, checkpoint = turtle_root(TURTLE_DEPTH, checkpoint_at=TURTLE_DEPTH // 2)
    resumed = resume_turtle(checkpoint, TURTLE_DEPTH // 2, TURTLE_DEPTH)
    items.append(record("turtle_provenance_checkpoint_replay",
        "PASS" if resumed == root else "FAIL", observed={
            "layers": TURTLE_DEPTH, "checkpoint_layer": TURTLE_DEPTH // 2,
            "root_sha256": root, "resumed_equals_baseline": resumed == root,
        }, expected="Deep lineage resumable without recursion or lost identity"))
    tampered = resume_turtle(hashlib.sha256(bytes.fromhex(checkpoint)).hexdigest(),
                             TURTLE_DEPTH // 2, TURTLE_DEPTH)
    items.append(record("turtle_tamper_detection",
        "PASS" if tampered != root else "FAIL", observed={
            "tampered_equals_reference": tampered == root
        }, expected="Modified checkpoint must never validate"))

    items.append(record("trillion_concurrent_workers_confirmed", "FAIL",
        proof_class="UNPROVEN_CLAIM_GATE", observed={
            "actual_max_threads": MAX_WIDTH, "addressable_candidates": CARDINALITY,
            "model_does_not_launch_trillion_workers": True,
        }, expected="Independent, permitted physical runtime evidence required"))
    items.append(record("energy_savings_confirmed", "FAIL",
        proof_class="NOT_MEASURED", observed={"energy_meter": None},
        expected="Actual joules per verified result with baseline required"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # No overwrite: every fresh run should receive its own immutable output path.
    with args.output.open("x", encoding="utf-8") as handle:
        for row in items:
            row["run_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    checks = [r for r in items if r["proof_class"] == "ISOLATED_WORKBENCH_TEST"]
    print(json.dumps({
        "output": str(args.output), "tests_passed": sum(r["status"]=="PASS" for r in checks),
        "tests_failed": sum(r["status"]=="FAIL" for r in checks),
        "claim_gates_rejected": sum(r["status"]=="FAIL" for r in items if r not in checks),
        "candidate_space": CARDINALITY, "max_workers": MAX_WIDTH,
        "serial_s": serial["elapsed_s"], "fixed4_s": fixed4["elapsed_s"],
    }, indent=2))


if __name__ == "__main__":
    main()
