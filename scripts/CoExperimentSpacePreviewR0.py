#!/usr/bin/env python3
"""Count and sample a huge candidate experiment-descriptor space without executing experiments.

This preview combines existing CoCivium role/session/domain/epistemic registries
with experiment-specific axes. It computes the exact Cartesian-product count
and decodes only a bounded deterministic sample. It grants no authority,
starts no workers, and performs no experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import gcd, prod
from pathlib import Path
from typing import Any


RECIPE = "CoExperimentSpacePreview.R0.v0.1-candidate"
MAX_SAMPLE = 100
SOURCE_PATHS = (
    "schemas/cospawn-contract-v0.1.schema.json",
    "ai/virtual-session-policy.json",
    "ai/evolution-lanes.json",
    "schemas/coevo-delta-v0.1.schema.json",
)

FIXED_AXES = {
    "experiment_family": [
        "DETERMINISTIC_ALGORITHM",
        "MODEL_QUALITY",
        "RETRIEVAL",
        "PROVENANCE",
        "STORAGE_LAYOUT",
        "GRAPH_QUERY",
        "RECOVERY",
        "FAULT_INJECTION",
        "HISTORICAL_REPLAY",
        "UX_ACCESSIBILITY",
        "SCHEDULING",
        "RESOURCE_EFFICIENCY",
    ],
    "substrate_class": [
        "DETERMINISTIC_LOCAL",
        "LOCAL_MODEL",
        "GITHUB_CI",
        "PROVIDER_MODEL",
        "BROWSER_STATIC",
        "MCP_ADAPTER",
        "FEDERATED_NODE",
        "SIMULATION_ONLY",
    ],
    "evidence_mode": [
        "PINNED_BYTES",
        "DECLARED_FIXTURE",
        "LIVE_OBSERVATION",
        "HISTORICAL_ARTIFACT",
        "SYNTHETIC_COUNTEREXAMPLE",
        "INDEPENDENT_IMPLEMENTATION",
        "SHARED_SOURCE_REVIEW",
        "UNKNOWN_EVIDENCE_MODE",
    ],
    "fault_mode": [
        "NONE",
        "PROCESS_EXIT",
        "TIMEOUT",
        "MISSING_SOURCE",
        "SOURCE_HASH_CHANGE",
        "STALE_CURRENTNESS",
        "PARTIAL_WRITE",
        "DUPLICATE_WORK",
        "DELAYED_ACK",
        "RECEIVER_UNAVAILABLE",
        "CACHE_STALE",
        "MALFORMED_INPUT",
    ],
    "evaluation_focus": [
        "CORRECTNESS",
        "THROUGHPUT",
        "MEDIAN_LATENCY",
        "P95_LATENCY",
        "P99_LATENCY",
        "ERROR_RATE",
        "MEMORY",
        "COST",
        "ENERGY_IF_MEASURED",
        "PROOF_DEBT",
        "CURRENTNESS_DEBT",
        "RECOVERY_TIME",
        "RECEIVER_VALUE",
        "ACCESSIBILITY",
    ],
    "scale_class": [
        "S1",
        "S10",
        "S100",
        "S1K",
        "S10K",
        "S100K",
        "S1M",
        "S10M",
        "S100M",
        "S1B_PLUS_LOGICAL",
    ],
    "concurrency_class": [
        "C1",
        "C2",
        "C4",
        "C8",
        "C16",
        "C32",
        "C64",
        "C128",
        "C256",
        "C512_PLUS_CEILING",
    ],
    "budget_profile": [
        "TINY",
        "SMALL",
        "MEDIUM",
        "LARGE_BOUNDED",
        "LATENCY_FIRST",
        "COST_FIRST",
        "ENERGY_FIRST",
        "RECEIVER_VALUE_FIRST",
    ],
    "turtle_template": [
        "NO_RECURSION",
        "CHALLENGER_ON_PROPOSAL",
        "VERIFIER_ON_PROPOSAL",
        "CHALLENGER_THEN_VERIFIER",
        "SEVEN_SEAT_ONE_ROUND",
        "SEVEN_SEAT_TWO_ROUNDS_MAX",
    ],
    "turtle_depth": [
        "DEPTH_0",
        "DEPTH_1",
        "DEPTH_2_MAX",
    ],
    "mutation_class": [
        "NO_MUTATION",
        "INPUT_VARIANT",
        "ALGORITHM_VARIANT",
        "PROMPT_VARIANT",
        "STORAGE_VARIANT",
        "ROUTING_VARIANT",
    ],
    "replay_epoch": [
        "CURRENT_ONLY",
        "PREVIOUS_RELEASE",
        "HISTORICAL_MODEL",
        "HISTORICAL_TOOLCHAIN",
        "CROSS_GENERATION_COMPARE",
        "UNKNOWN_HISTORICAL_ENVIRONMENT",
    ],
}


def fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


def load_axes(root: Path) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    docs = {}
    bindings = []
    for relative in SOURCE_PATHS:
        raw = (root / relative).read_bytes()
        docs[relative] = json.loads(raw.decode("utf-8"))
        bindings.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })

    spawn = docs[SOURCE_PATHS[0]]
    policy = docs[SOURCE_PATHS[1]]
    lanes = docs[SOURCE_PATHS[2]]
    delta = docs[SOURCE_PATHS[3]]

    axes = {
        "operational_role": spawn["properties"]["role"]["enum"],
        "morphology": policy["morphologies"],
        "persistence_mode": policy["persistence_modes"],
        "participant_class": policy["participant_classes"],
        "domain": [row[0] for row in lanes["domains"]],
        "epistemic_class": delta["properties"]["epistemic_class"]["enum"],
        **FIXED_AXES,
    }

    normalized = {}
    for name, values in axes.items():
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"{name} must be a nonempty list of nonblank strings")
        if len(set(values)) != len(values):
            raise ValueError(f"{name} contains duplicate values")
        normalized[name] = sorted(values)
    return normalized, bindings


def parse_filters(items: list[str]) -> dict[str, str]:
    result = {}
    for item in items:
        name, separator, value = item.partition("=")
        if not separator or not name or not value:
            raise ValueError("filters must use exact AXIS=VALUE form")
        if name in result:
            raise ValueError(f"duplicate filter axis: {name}")
        result[name] = value
    return result


def decode_rank(rank: int, axes: dict[str, list[str]]) -> dict[str, str]:
    decoded = {}
    for name in reversed(axes):
        rank, index = divmod(rank, len(axes[name]))
        decoded[name] = axes[name][index]
    return {name: decoded[name] for name in axes}


def build_preview(
    root: Path,
    filters: dict[str, str] | None = None,
    limit: int = 12,
    seed: str = "0",
) -> dict[str, Any]:
    if type(limit) is not int or not 0 <= limit <= MAX_SAMPLE:
        raise ValueError(f"limit must be an integer from 0 to {MAX_SAMPLE}")
    if not isinstance(seed, str):
        raise ValueError("seed must be a string")
    if filters is not None and not isinstance(filters, dict):
        raise ValueError("filters must be an object")

    filters = {} if filters is None else dict(filters)
    axes, bindings = load_axes(root)

    for name, value in filters.items():
        if name not in axes or not isinstance(value, str) or value not in axes[name]:
            raise ValueError(f"unknown axis or value: {name}={value}")

    selected = {
        name: [filters[name]] if name in filters else values
        for name, values in axes.items()
    }
    raw_count = prod(len(values) for values in axes.values())
    filtered_count = prod(len(values) for values in selected.values())
    sample_count = min(limit, filtered_count)

    basis = {
        "recipe": RECIPE,
        "source_bindings": bindings,
        "filters": dict(sorted(filters.items())),
        "seed": seed,
    }
    digest = fingerprint(basis)
    if sample_count:
        start = int(digest[:32], 16) % filtered_count
        stride = int(digest[32:], 16) % filtered_count or 1
        while gcd(stride, filtered_count) != 1:
            stride += 1
    else:
        start = 0
        stride = 1

    sample = []
    for index in range(sample_count):
        rank = (start + index * stride) % filtered_count
        facets = decode_rank(rank, selected)
        identity = {
            "recipe": RECIPE,
            "source_bindings": bindings,
            "facets": facets,
        }
        sample.append({
            "experiment_descriptor_id": "coexperiment:" + fingerprint(identity),
            "filtered_rank": rank,
            "facets": facets,
            "assessment": "UNASSESSED",
            "execution_state": "NOT_SELECTED_OR_EXECUTED",
        })

    return {
        "schema": RECIPE,
        "state": "CANDIDATE_EXPERIMENT_SPACE_PREVIEW__ZERO_EXECUTION",
        "source_bindings": bindings,
        "axis_counts": {name: len(values) for name, values in axes.items()},
        "axis_count": len(axes),
        "raw_candidate_descriptor_count": raw_count,
        "exact_filters": dict(sorted(filters.items())),
        "filtered_candidate_descriptor_count": filtered_count,
        "eligible_experiment_count": None,
        "executed_experiment_count": 0,
        "sample_count": sample_count,
        "sampling": {
            "method": "SHA256_SEEDED_COPRIME_STRIDE_V1",
            "seed": seed,
            "start": start,
            "stride": stride,
            "maximum_sample": MAX_SAMPLE,
            "coverage_claim": "NONE",
        },
        "sample": sample,
        "turtle_policy": {
            "maximum_runtime_depth": 2,
            "maximum_review_rounds": 2,
            "children_share_parent_budget": True,
            "children_may_replenish_budget": False,
            "children_may_raise_authority": False,
            "selection_or_descriptor_ne_materialization": True,
            "stop_conditions": [
                "ACCEPTANCE",
                "AGGREGATE_BUDGET_EXHAUSTED",
                "NO_VERIFIED_MATERIAL_IMPROVEMENT_IN_COMPLETE_ROUND",
            ],
        },
        "promotion_ladder": [
            "DESCRIPTOR",
            "STATIC_VALIDATION",
            "SHADOW",
            "MICRO_CANARY",
            "REPEATED_CANARY",
            "CROSS_SUBSTRATE_COMPARE",
            "INDEPENDENCE_AUDIT",
            "RECEIVER_VALUE_CHECK",
            "HIGH_BAR_CANDIDATE",
        ],
        "high_bar_gates": [
            "EXACT_INPUT_BINDINGS",
            "PINNED_BASELINE",
            "CORRECTNESS_NONREGRESSION",
            "REPEATED_MEASUREMENTS",
            "TAIL_LATENCY_AND_ERROR_REPORT",
            "RESOURCE_AND_COST_REPORT",
            "PROVENANCE_AND_CURRENTNESS",
            "COUNTEREXAMPLE_OR_CHALLENGE",
            "RECOVERY_OR_ROLLBACK_WHERE_APPLICABLE",
            "INDEPENDENCE_STATUS_EXPLICIT",
            "RECEIVER_VALUE_EXPLICIT",
            "UNRESOLVED_DISSENT_PRESERVED",
        ],
        "effects": {
            "workers_started": 0,
            "provider_sessions_created": 0,
            "experiments_executed": 0,
            "external_mutations": 0,
            "authority_granted": 0,
        },
        "next": "FILTER_AND_SCORE_DESCRIPTORS__THEN_RUN_ONE_BOUNDED_MICRO_CANARY",
        "nonclaims": [
            "RAW_DESCRIPTOR_COUNT_NE_USEFUL_EXPERIMENT_COUNT",
            "DESCRIPTOR_NE_EXPERIMENT",
            "SAMPLE_NE_COVERAGE",
            "TURTLE_TEMPLATE_NE_LIVE_RECURSION",
            "LOGICAL_SCALE_NE_ACTIVE_WORKERS",
            "PROVIDER_COUNT_NE_INDEPENDENCE",
            "HIGH_BAR_CANDIDATE_NE_PROMOTION",
            "PREVIEW_NE_RUNTIME_ADOPTION",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--filter", action="append", default=[], metavar="AXIS=VALUE")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--seed", default="0")
    args = parser.parse_args()
    try:
        result = build_preview(
            args.repo_root,
            filters=parse_filters(args.filter),
            limit=args.limit,
            seed=args.seed,
        )
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
