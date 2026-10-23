#!/usr/bin/env python3
"""Compile a bounded benchmark ladder without executing workloads.

CoStretch R0 represents benchmark pressure as a plan: logical population,
active-concurrency ceiling, repetitions, time/cost/memory budgets, and explicit
stop predicates. It performs no stress workload or external action.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any


SCHEMA = "CoStretchBenchmarkPlan.R0.v0.1-candidate"
MAX_LOGICAL_ITEMS = 10**12
MAX_CONCURRENCY = 4096
MAX_REPETITIONS = 100
MAX_STEPS = 32


@dataclass(frozen=True)
class Step:
    step: int
    logical_items: int
    concurrency_ceiling: int
    repetitions: int
    wall_time_budget_seconds: int
    memory_budget_mb: int
    cost_budget_microunits: int


def _int(value: Any, low: int, high: int, name: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer from {low} to {high}")
    return value


def fingerprint(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def geometric_ladder(start: int, stop: int, steps: int) -> list[int]:
    start = _int(start, 1, MAX_LOGICAL_ITEMS, "logical start")
    stop = _int(stop, start, MAX_LOGICAL_ITEMS, "logical stop")
    steps = _int(steps, 1, MAX_STEPS, "steps")
    if steps == 1 or start == stop:
        return [stop]
    values = [start]
    ratio = (stop / start) ** (1 / (steps - 1))
    for index in range(1, steps - 1):
        candidate = max(values[-1] + 1, int(round(start * (ratio ** index))))
        values.append(min(candidate, stop))
    values.append(stop)
    # Remove rounding duplicates while preserving order.
    deduped = []
    for value in values:
        if not deduped or value != deduped[-1]:
            deduped.append(value)
    return deduped


def concurrency_ladder(start: int, stop: int, steps: int) -> list[int]:
    start = _int(start, 1, MAX_CONCURRENCY, "concurrency start")
    stop = _int(stop, start, MAX_CONCURRENCY, "concurrency stop")
    values = geometric_ladder(start, stop, steps)
    return [min(value, MAX_CONCURRENCY) for value in values]


def compile_plan(
    *,
    logical_start: int = 1_000,
    logical_stop: int = 1_000_000,
    concurrency_start: int = 1,
    concurrency_stop: int = 64,
    steps: int = 7,
    repetitions: int = 3,
    wall_time_budget_seconds: int = 300,
    memory_budget_mb: int = 4096,
    cost_budget_microunits: int = 0,
) -> dict[str, Any]:
    steps = _int(steps, 1, MAX_STEPS, "steps")
    repetitions = _int(repetitions, 1, MAX_REPETITIONS, "repetitions")
    wall_time_budget_seconds = _int(
        wall_time_budget_seconds, 1, 86_400, "wall time budget"
    )
    memory_budget_mb = _int(memory_budget_mb, 1, 1_048_576, "memory budget")
    cost_budget_microunits = _int(
        cost_budget_microunits, 0, 10**12, "cost budget"
    )

    logical = geometric_ladder(logical_start, logical_stop, steps)
    concurrency = concurrency_ladder(
        concurrency_start, concurrency_stop, len(logical)
    )
    if len(concurrency) != len(logical):
        # geometric rounding can collapse neighboring points; align by index
        # through deterministic nearest-position selection.
        if len(concurrency) == 1:
            concurrency = concurrency * len(logical)
        else:
            concurrency = [
                concurrency[round(i * (len(concurrency) - 1) / (len(logical) - 1))]
                for i in range(len(logical))
            ]

    rows = [
        Step(
            step=index + 1,
            logical_items=logical_items,
            concurrency_ceiling=concurrency[index],
            repetitions=repetitions,
            wall_time_budget_seconds=wall_time_budget_seconds,
            memory_budget_mb=memory_budget_mb,
            cost_budget_microunits=cost_budget_microunits,
        )
        for index, logical_items in enumerate(logical)
    ]
    encoded_rows = [asdict(row) for row in rows]
    identity = {
        "schema": SCHEMA,
        "steps": encoded_rows,
    }

    return {
        "schema": SCHEMA,
        "state": "BENCHMARK_PLAN_ONLY__NO_WORKLOAD_EXECUTION",
        "plan_id": "costretch:" + fingerprint(identity),
        "steps": encoded_rows,
        "execution_performed": False,
        "active_workers_started": 0,
        "provider_sessions_created": 0,
        "benchmark_dimensions": [
            "correctness",
            "throughput",
            "median_latency",
            "p95_latency",
            "p99_latency",
            "error_rate",
            "memory_peak",
            "cpu_time",
            "wall_time",
            "cost",
            "energy_or_power_if_measured",
            "currentness_debt",
            "proof_debt",
            "receiver_value",
        ],
        "stop_predicates": [
            "CORRECTNESS_REGRESSION",
            "ERROR_RATE_EXCEEDS_BOUND",
            "P95_LATENCY_EXCEEDS_BOUND",
            "MEMORY_BUDGET_EXCEEDED",
            "WALL_TIME_BUDGET_EXCEEDED",
            "COST_BUDGET_EXCEEDED",
            "THERMAL_OR_POWER_GUARD_TRIGGERED_IF_AVAILABLE",
            "COORDINATION_DEBT_EXCEEDS_RECEIVER_VALUE",
            "NO_VERIFIED_MATERIAL_IMPROVEMENT",
        ],
        "champion_policy": {
            "newest_wins": False,
            "single_scalar_score_required": False,
            "must_preserve_correctness": True,
            "must_report_tradeoffs": True,
            "must_bind_exact_inputs": True,
            "must_bind_runtime_and_version": True,
            "must_repeat_measurements": True,
        },
        "activation_policy": {
            "logical_items_ne_active_workers": True,
            "concurrency_ceiling_ne_target_utilization": True,
            "capacity_ne_authority": True,
            "step_n_plus_one_requires_step_n_pass": True,
        },
        "next": "RUN_ONE_LOCAL_OR_CI_CANARY_WITH_REAL_METRICS_THEN_COMPARE_TO_PINNED_BASELINE",
        "nonclaims": [
            "PLAN_NE_BENCHMARK_RESULT",
            "LOGICAL_ITEMS_NE_ACTIVE_WORKERS",
            "CONCURRENCY_CEILING_NE_SATURATION",
            "HIGH_UTILIZATION_NE_HIGH_VALUE",
            "NEWEST_NE_BEST",
            "FASTEST_NE_BEST",
            "MORE_RESOURCES_NE_BETTER_SYSTEM",
            "PASS_NE_RUNTIME_ADOPTION",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--logical-start", type=int, default=1_000)
    parser.add_argument("--logical-stop", type=int, default=1_000_000)
    parser.add_argument("--concurrency-start", type=int, default=1)
    parser.add_argument("--concurrency-stop", type=int, default=64)
    parser.add_argument("--steps", type=int, default=7)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--wall-time-budget-seconds", type=int, default=300)
    parser.add_argument("--memory-budget-mb", type=int, default=4096)
    parser.add_argument("--cost-budget-microunits", type=int, default=0)
    args = parser.parse_args()
    try:
        result = compile_plan(
            logical_start=args.logical_start,
            logical_stop=args.logical_stop,
            concurrency_start=args.concurrency_start,
            concurrency_stop=args.concurrency_stop,
            steps=args.steps,
            repetitions=args.repetitions,
            wall_time_budget_seconds=args.wall_time_budget_seconds,
            memory_budget_mb=args.memory_budget_mb,
            cost_budget_microunits=args.cost_budget_microunits,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
