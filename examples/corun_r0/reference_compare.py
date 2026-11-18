#!/usr/bin/env python3
"""CoRun+ R0 independent-code-path differential test, not a product A/B.

The oracle and graph use the SAME historical source and evidence specification.
This measures semantic agreement, not independence of facts, reviewer or provider.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import statistics
import sys
import time

from corun import (canonical_bytes, execute, load_source, sha)
from reference_oracle import independent_reference

REPORT_SCHEMA = "CoCivium.CoRunPlus.ReferenceComparison.R0"


def assert_semantic_agreement(reference: dict, candidate: dict) -> str:
    """Raise on any difference, including regressions in negative evidence."""
    if canonical_bytes(reference) != canonical_bytes(candidate):
        raise ValueError("independent reference mismatch, HOLD")
    return sha(canonical_bytes(reference))


def compare_paths(source: dict, source_meta: dict, workers: int = 4,
                  trials: int = 7) -> dict:
    if not isinstance(trials, int) or not 3 <= trials <= 25:
        raise ValueError("trials must be 3..25")
    if not isinstance(workers, int) or not 1 <= workers <= 8:
        raise ValueError("workers must be 1..8")
    pristine = canonical_bytes(source)
    timings = {"A_DIRECT_REFERENCE": [], "B_CORUN_DAG": []}
    common_sha = None
    for index in range(trials):
        # Counterbalanced alternating order, no random claims, no simulated delay.
        order = ("A_DIRECT_REFERENCE", "B_CORUN_DAG") if index % 2 == 0 else (
            "B_CORUN_DAG", "A_DIRECT_REFERENCE")
        outputs = {}
        for arm in order:
            start = time.perf_counter_ns()
            if arm == "A_DIRECT_REFERENCE":
                outputs[arm] = independent_reference(source)
            else:
                outputs[arm], metrics = execute(source, workers, delay_ms=0)
                if metrics["peak_active"] > workers or metrics["nodes_completed"] == 0:
                    raise ValueError("unbounded or empty candidate run")
            elapsed = time.perf_counter_ns() - start
            timings[arm].append(elapsed)
        common_sha = assert_semantic_agreement(outputs["A_DIRECT_REFERENCE"],
                                               outputs["B_CORUN_DAG"])
        if canonical_bytes(source) != pristine:
            raise ValueError("source changed during read-only experiment")
    return {
        "schema": REPORT_SCHEMA,
        "source": source_meta,
        "trials": trials,
        "co_run_worker_limit": workers,
        "output_equal_every_trial": True,
        "semantic_sha256": common_sha,
        "arms": {
            name: {
                "elapsed_ns": samples,
                "median_ns": int(statistics.median(samples)),
                "min_ns": min(samples),
                "max_ns": max(samples),
            } for name, samples in timings.items()
        },
        "measurement_status": "CODE_PATH_SEMANTICS_ONLY__NOT_FAIR_PRODUCT_SPEED_TRIAL",
        "measurement_limitations": [
            "SAME_SOURCE_AND_SPEC__NOT_INDEPENDENT_EVIDENCE",
            "SAME_AUTHORING_WAVE__NOT_INDEPENDENT_HUMAN_REVIEW",
            "REFERENCE_NO_PER_NODE_HASHES__WORKLOAD_COSTS_DIFFER",
            "CPU_AND_THREAD_SCHEDULING_NOT_CONTROLLED",
            "LEGACY_PRODUCT_BASELINE_NOT_MEASURED",
            "HUMAN_ACTIVE_MINUTES_NOT_MEASURED",
            "PRODUCT_RECEIVER_ACK_UNKNOWN",
        ],
        "product_promotion": "HELD",
        "external_effects": "NONE",
    }


def write_evidence(out: Path, record: dict) -> tuple[Path, Path]:
    """No file overwrite; receipt authenticates the exact local output bytes."""
    out.mkdir(parents=True, exist_ok=False)
    body = canonical_bytes(record)
    report = out / "reference-compare.json"
    receipt = out / "reference-compare.receipt.json"
    with report.open("xb") as stream:
        stream.write(body)
    receipt_data = {
        "schema": "CoCivium.CoRunPlus.ReferenceReceipt.R0",
        "report_sha256": sha(body),
        "report_bytes": len(body),
        "state": "PASS_CODE_PATH_SEMANTICS_ONLY",
        "receiver_ack": "UNKNOWN",
        "human_minutes": None,
        "independent_facts": False,
        "product_promotion": "HELD",
    }
    with receipt.open("xb") as stream:
        stream.write(canonical_bytes(receipt_data))
    return report, receipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--expected-git-blob")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--trials", type=int, default=7)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        source, meta = load_source(args.input, args.expected_git_blob)
        record = compare_paths(source, meta, workers=args.workers, trials=args.trials)
        rp, rc = write_evidence(args.out, record)
    except (OSError, ValueError) as exc:
        print("HOLD_OR_FAIL_CLOSED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "status": record["measurement_status"],
        "trials": record["trials"],
        "semantic_sha256": record["semantic_sha256"],
        "A_median_ns": record["arms"]["A_DIRECT_REFERENCE"]["median_ns"],
        "B_median_ns": record["arms"]["B_CORUN_DAG"]["median_ns"],
        "report": str(rp),
        "receipt": str(rc),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
