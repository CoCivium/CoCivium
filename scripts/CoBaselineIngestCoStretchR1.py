#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SELECTED = {
    "queue_output_serial": 1,
    "queue_output_fixed_2": 2,
    "queue_output_fixed_4": 4,
}

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def load_rows(path: Path) -> tuple[list[dict[str, Any]], str]:
    data = path.read_bytes()
    rows = []
    for i, line in enumerate(data.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL line {i}") from exc
    return rows, hashlib.sha256(data).hexdigest()

def normalize(path: Path) -> dict[str, Any]:
    rows, source_sha = load_rows(path)
    chosen = {r.get("test"): r for r in rows if r.get("test") in SELECTED}
    require(set(chosen) == set(SELECTED), "required CoStretch comparison rows missing")

    ordered = [chosen[name] for name in SELECTED]
    task_counts = {r["observed"].get("task_count") for r in ordered}
    digest_roots = {r["observed"].get("digest_root") for r in ordered}
    boundaries = {r.get("boundary") for r in ordered}
    proof_classes = {r.get("proof_class") for r in ordered}
    run_times = {r.get("run_utc") for r in ordered}

    require(task_counts == {160}, f"unexpected task_count set: {task_counts}")
    require(len(digest_roots) == 1 and None not in digest_roots, "digest roots differ or missing")
    require(len(boundaries) == 1 and None not in boundaries, "boundaries differ or missing")
    require(proof_classes == {"ISOLATED_WORKBENCH_TEST"}, f"unexpected proof classes: {proof_classes}")
    require(len(run_times) == 1 and None not in run_times, "run timestamps differ or missing")

    records = []
    for name, expected_width in SELECTED.items():
        row = chosen[name]
        obs = row["observed"]
        require(row.get("status") == "PASS", f"{name}: not PASS")
        require(obs.get("width") == expected_width, f"{name}: wrong width")
        require(obs.get("completed") == obs.get("task_count") == 160, f"{name}: incomplete")
        require(obs.get("failed") == [], f"{name}: failures present")
        require(obs.get("retries") == 0, f"{name}: retries make direct family comparison ambiguous")
        require(isinstance(obs.get("verified_items_per_s"), (int, float)), f"{name}: throughput missing")
        require(isinstance(obs.get("elapsed_s"), (int, float)), f"{name}: elapsed missing")

        records.append({
            "result_id": f"costretch-r1-{name}",
            "workload_id": "costretch-r1-queue-output-160-digest-verify",
            "environment": "historical-offline-bounded-workbench-20261023",
            "receiver_class": "benchmark-harness",
            "authority_ceiling": "LOCAL_OFFLINE_BOUNDED_FIXTURE",
            "privacy_class": "PUBLIC_SAFE_FIXTURE",
            "observed_at": row["run_utc"],
            "state": "PASS",
            "current": False,
            "metrics": {
                "useful_throughput": float(obs["verified_items_per_s"]),
                "correctness": 1.0,
                "recovery_success": 1.0,
                "elapsed_s": float(obs["elapsed_s"]),
                "worker_width": int(obs["width"]),
            },
            "source_row": name,
            "source_digest_root": obs["digest_root"],
        })

    return {
        "schema": "CoBaseline.RealHistoricalFixture.R1.v0.1",
        "source": {
            "path": path.as_posix(),
            "sha256": source_sha,
            "proof_class": "COMMITTED_HISTORICAL_BENCHMARK_READBACK",
            "boundary": next(iter(boundaries)),
            "currentness": "HISTORICAL_NOT_CURRENT_RUNTIME",
        },
        "metric_directions": {
            "useful_throughput": "max",
            "correctness": "max",
            "recovery_success": "max",
            "elapsed_s": "min",
        },
        "hard_floors": {
            "correctness": 1.0,
            "recovery_success": 1.0,
        },
        "records": records,
        "nonclaims": [
            "HISTORICAL_PASS_NE_CURRENT_RUNTIME",
            "WIDTH_4_WIN_NE_UNIVERSAL_OPTIMUM",
            "OFFLINE_FIXTURE_NE_X2_CALIBRATION",
            "RECORDED_THROUGHPUT_NE_SUSTAINED_CAPACITY",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
        ],
    }

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    fixture = normalize(args.source)
    text = json.dumps(fixture, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
