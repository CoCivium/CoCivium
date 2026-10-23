#!/usr/bin/env python3
"""Select a tiny, explainable experiment frontier from an annotated candidate pool.

R0 performs multi-objective selection only. It does not score raw experiment
descriptors by guessing their value, and it does not execute experiments.
Every benefit/penalty estimate must be supplied explicitly with an evidence
reference. Selection uses Pareto layers, reserved lanes, and facet diversity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


FORMAT = "CoExperimentSelectorInputR0"
SCHEMA = "CoExperimentSelector.R0.v0.1-candidate"
MAX_CANDIDATES = 1000
MAX_SLOTS = 64
LANES = ("CHALLENGE", "EXPLORATION", "WEIRD", "REPLAY", "FAULT")
BENEFITS = (
    "information_gain",
    "falsifiability",
    "receiver_value",
    "novelty",
    "independence",
)
PENALTIES = (
    "cost",
    "latency",
    "risk",
    "coordination_debt",
    "proof_debt",
)


class SelectorError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SelectorError(message)


def fingerprint(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _metric_group(candidate: dict[str, Any], group: str, names: tuple[str, ...]) -> dict[str, int]:
    metrics = candidate.get(group)
    require(isinstance(metrics, dict), f"{group} must be an object")
    require(set(metrics) == set(names), f"{group} keys must match registry")
    values = {}
    for name in names:
        record = metrics[name]
        require(isinstance(record, dict), f"{group}.{name} must be an object")
        value = record.get("value")
        evidence_ref = record.get("evidence_ref")
        require(type(value) is int and 0 <= value <= 100,
                f"{group}.{name}.value must be integer 0..100")
        require(isinstance(evidence_ref, str) and evidence_ref.strip(),
                f"{group}.{name}.evidence_ref required")
        values[name] = value
    return values


def validate_input(payload: Any) -> dict[str, Any]:
    require(isinstance(payload, dict), "input must be an object")
    require(payload.get("format") == FORMAT, "wrong selector input format")

    slots = payload.get("selection_slots")
    require(type(slots) is int and 1 <= slots <= MAX_SLOTS,
            f"selection_slots must be integer 1..{MAX_SLOTS}")

    reserves = payload.get("reserves")
    require(isinstance(reserves, dict), "reserves must be an object")
    require(set(reserves) == set(LANES), "reserve keys must match lane registry")
    for lane, count in reserves.items():
        require(type(count) is int and 0 <= count <= slots,
                f"reserve {lane} must be integer 0..selection_slots")
    require(sum(reserves.values()) <= slots,
            "sum of reserves cannot exceed selection_slots")

    candidates = payload.get("candidates")
    require(isinstance(candidates, list) and 1 <= len(candidates) <= MAX_CANDIDATES,
            f"candidates must contain 1..{MAX_CANDIDATES} items")

    seen = set()
    for candidate in candidates:
        require(isinstance(candidate, dict), "candidate must be an object")
        candidate_id = candidate.get("experiment_descriptor_id")
        require(isinstance(candidate_id, str) and candidate_id.strip(),
                "experiment_descriptor_id required")
        require(candidate_id not in seen, "duplicate experiment_descriptor_id")
        seen.add(candidate_id)

        facets = candidate.get("facets")
        require(isinstance(facets, dict) and facets,
                "candidate facets must be a nonempty object")
        for key, value in facets.items():
            require(isinstance(key, str) and key.strip(), "facet key invalid")
            require(isinstance(value, str) and value.strip(), "facet value invalid")

        lanes = candidate.get("lanes")
        require(isinstance(lanes, list), "candidate lanes must be a list")
        require(all(isinstance(lane, str) and lane in LANES for lane in lanes),
                "candidate lane not in registry")
        require(len(lanes) == len(set(lanes)), "duplicate candidate lane")

        _metric_group(candidate, "benefits", BENEFITS)
        _metric_group(candidate, "penalties", PENALTIES)

    return payload


def metric_values(candidate: dict[str, Any]) -> tuple[dict[str, int], dict[str, int]]:
    return (
        {name: candidate["benefits"][name]["value"] for name in BENEFITS},
        {name: candidate["penalties"][name]["value"] for name in PENALTIES},
    )


def dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    lb, lp = metric_values(left)
    rb, rp = metric_values(right)
    no_worse = (
        all(lb[name] >= rb[name] for name in BENEFITS)
        and all(lp[name] <= rp[name] for name in PENALTIES)
    )
    strictly_better = (
        any(lb[name] > rb[name] for name in BENEFITS)
        or any(lp[name] < rp[name] for name in PENALTIES)
    )
    return no_worse and strictly_better


def pareto_layers(candidates: list[dict[str, Any]]) -> dict[str, int]:
    remaining = list(candidates)
    result: dict[str, int] = {}
    layer = 0
    while remaining:
        frontier = [
            candidate for candidate in remaining
            if not any(
                dominates(other, candidate)
                for other in remaining
                if other is not candidate
            )
        ]
        require(frontier, "pareto decomposition failed")
        for candidate in frontier:
            result[candidate["experiment_descriptor_id"]] = layer
        ids = {candidate["experiment_descriptor_id"] for candidate in frontier}
        remaining = [
            candidate for candidate in remaining
            if candidate["experiment_descriptor_id"] not in ids
        ]
        layer += 1
    return result


def facet_similarity(left: dict[str, str], right: dict[str, str]) -> int:
    shared_keys = set(left) & set(right)
    return sum(left[key] == right[key] for key in shared_keys)


def diversity_penalty(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> int:
    if not selected:
        return 0
    return max(
        facet_similarity(candidate["facets"], existing["facets"])
        for existing in selected
    )


def rank_key(
    candidate: dict[str, Any],
    layers: dict[str, int],
    selected: list[dict[str, Any]],
) -> tuple[Any, ...]:
    benefits, penalties = metric_values(candidate)
    return (
        layers[candidate["experiment_descriptor_id"]],
        diversity_penalty(candidate, selected),
        max(penalties.values()),
        -min(benefits.values()),
        -sum(benefits.values()),
        sum(penalties.values()),
        fingerprint(candidate["experiment_descriptor_id"]),
    )


def choose_best(
    pool: list[dict[str, Any]],
    layers: dict[str, int],
    selected: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not pool:
        return None
    return min(pool, key=lambda candidate: rank_key(candidate, layers, selected))


def select(payload: dict[str, Any]) -> dict[str, Any]:
    validate_input(payload)
    candidates = payload["candidates"]
    slots = min(payload["selection_slots"], len(candidates))
    layers = pareto_layers(candidates)
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    decisions: list[dict[str, Any]] = []

    for lane in LANES:
        for _ in range(payload["reserves"][lane]):
            pool = [
                candidate for candidate in candidates
                if lane in candidate["lanes"]
                and candidate["experiment_descriptor_id"] not in selected_ids
            ]
            winner = choose_best(pool, layers, selected)
            if winner is None:
                break
            selected.append(winner)
            selected_ids.add(winner["experiment_descriptor_id"])
            decisions.append({
                "experiment_descriptor_id": winner["experiment_descriptor_id"],
                "selection_reason": "RESERVED_LANE",
                "reserved_lane": lane,
                "pareto_layer": layers[winner["experiment_descriptor_id"]],
                "diversity_penalty_at_selection": diversity_penalty(
                    winner, selected[:-1]
                ),
            })

    while len(selected) < slots:
        pool = [
            candidate for candidate in candidates
            if candidate["experiment_descriptor_id"] not in selected_ids
        ]
        winner = choose_best(pool, layers, selected)
        if winner is None:
            break
        selected.append(winner)
        selected_ids.add(winner["experiment_descriptor_id"])
        decisions.append({
            "experiment_descriptor_id": winner["experiment_descriptor_id"],
            "selection_reason": "GENERAL_FILL",
            "reserved_lane": None,
            "pareto_layer": layers[winner["experiment_descriptor_id"]],
            "diversity_penalty_at_selection": diversity_penalty(
                winner, selected[:-1]
            ),
        })

    missing_reserves = {}
    for lane in LANES:
        requested = payload["reserves"][lane]
        achieved = sum(
            decision["reserved_lane"] == lane for decision in decisions
        )
        if achieved < requested:
            missing_reserves[lane] = requested - achieved

    output_identity = {
        "schema": SCHEMA,
        "input_fingerprint": fingerprint(payload),
        "decisions": decisions,
    }
    return {
        "schema": SCHEMA,
        "state": "SELECTOR_OUTPUT__ZERO_EXECUTION",
        "selection_id": "coexperiment-selection:" + fingerprint(output_identity),
        "input_fingerprint": fingerprint(payload),
        "candidate_count": len(candidates),
        "selection_slots": payload["selection_slots"],
        "selected_count": len(decisions),
        "pareto_layer_count": (max(layers.values()) + 1) if layers else 0,
        "requested_reserves": dict(payload["reserves"]),
        "unfilled_reserves": missing_reserves,
        "selection_order": decisions,
        "selected_descriptor_ids": [
            decision["experiment_descriptor_id"] for decision in decisions
        ],
        "ranking_policy": {
            "primary": "PARETO_LAYER",
            "secondary": [
                "LOW_FACET_SIMILARITY_TO_ALREADY_SELECTED",
                "LOW_WORST_PENALTY",
                "HIGH_WORST_BENEFIT",
                "HIGH_TOTAL_BENEFIT",
                "LOW_TOTAL_PENALTY",
                "DETERMINISTIC_ID_HASH_TIEBREAK",
            ],
            "single_scalar_quality_score": False,
            "raw_descriptor_facets_auto_scored": False,
        },
        "effects": {
            "experiments_executed": 0,
            "workers_started": 0,
            "provider_sessions_created": 0,
            "external_mutations": 0,
            "authority_granted": 0,
        },
        "next": "BIND_SELECTED_DESCRIPTORS_TO_STATIC_VALIDATION__THEN_ELECT_AT_MOST_ONE_MICRO_CANARY",
        "nonclaims": [
            "SELECTED_NE_EXECUTED",
            "METRIC_ESTIMATE_NE_MEASUREMENT_UNLESS_EVIDENCE_SUPPORTS_IT",
            "PARETO_NE_TRUTH",
            "DIVERSITY_NE_INDEPENDENCE",
            "RESERVED_LANE_NE_MATERIALIZATION",
            "SELECTOR_OUTPUT_NE_AUTHORITY",
            "SELECTOR_OUTPUT_NE_RUNTIME_ADOPTION",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = select(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, SelectorError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
