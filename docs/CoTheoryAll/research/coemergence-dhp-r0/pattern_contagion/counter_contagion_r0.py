#!/usr/bin/env python3
"""Bounded synthetic correction-notice propagation. Not a truth or receiver model.

Reuses the tested CoPatternContagion R0 deterministic graph and its existing
source-only policy and non-effect validation. No network, files written or
external actions in the engine. All outputs are hypothetical simulations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pattern_contagion_r0 import Held, forward, validate

SCHEMA = "CoAll.CounterContagion.SyntheticPair.R0"
MAX_HORIZON = 12


def validate_pair(record: dict[str, Any]) -> None:
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        raise Held("WRONG_PAIR_SCHEMA")
    if record.get("external_effects") != "NONE":
        raise Held("NO_EXTERNAL_EFFECTS")
    allowed = {"schema", "external_effects", "claim_graph", "correction_graph", "horizon", "correction_start_tick", "synthetic_unverified_claim_class", "source_copies", "reported_receiver"}
    if set(record) != allowed:
        raise Held("MISSING_OR_UNRECOGNIZED_PAIR_FIELDS")
    graph_allowed = {"schema", "nodes", "edges", "seeds", "steps", "noise_amplitude", "seed_number", "external_effects"}
    if any(not isinstance(record.get(k), dict) or set(record[k]) != graph_allowed for k in ("claim_graph", "correction_graph")):
        raise Held("MISSING_OR_UNRECOGNIZED_GRAPH_FIELDS")
    claim = record.get("claim_graph")
    correction = record.get("correction_graph")
    claim_nodes, _ = validate(claim)
    correction_nodes, _ = validate(correction)
    c = {n["id"]: n["allow_synthetic_exposure"] for n in claim_nodes}
    d = {n["id"]: n["allow_synthetic_exposure"] for n in correction_nodes}
    if c != d:
        raise Held("CROSS_GRAPH_NODE_OR_RIGHTS_MISMATCH")
    if not claim["seeds"] or not correction["seeds"]:
        raise Held("SEED_REQUIRED")
    if set(claim["seeds"]) & set(correction["seeds"]):
        raise Held("INDEPENDENT_CHALLENGE_SEED_REQUIRED")
    horizon = record.get("horizon")
    start = record.get("correction_start_tick")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or not 0 <= horizon <= MAX_HORIZON:
        raise Held("BAD_HORIZON")
    if isinstance(start, bool) or not isinstance(start, int) or not 0 <= start <= horizon:
        raise Held("BAD_CORRECTION_START")
    if claim["steps"] < horizon or correction["steps"] < horizon:
        raise Held("INSUFFICIENT_GRAPH_TICKS")
    if record.get("synthetic_unverified_claim_class") != "DELIBERATELY_UNVERIFIED":
        raise Held("MUST_DECLARE_HYPOTHESIS_NOT_TRUTH")
    copies = record.get("source_copies")
    if not isinstance(copies, list) or not copies or len(copies) > 30:
        raise Held("BAD_SOURCE_COPIES")
    identifiers: set[str] = set()
    for item in copies:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k] for k in ("copy_id", "source_family")):
            raise Held("BAD_SOURCE_FAMILY")
        if item["copy_id"] in identifiers:
            raise Held("DUPLICATE_SOURCE_COPY")
        identifiers.add(item["copy_id"])
    if record.get("reported_receiver") not in c:
        raise Held("UNKNOWN_RECEIVER")


def arrival_ticks(graph: dict[str, Any]) -> dict[str, int]:
    report = forward(graph)
    return {name: tick["tick"] for tick in report["trail"] for name in tick["newly_active"]}


def scenario(record: dict[str, Any], correction_start: int | None) -> dict[str, Any]:
    horizon = record["horizon"]
    exposure = arrival_ticks(record["claim_graph"])
    correction = arrival_ticks(record["correction_graph"]) if correction_start is not None else {}
    exposures = {n: t for n, t in exposure.items() if t <= horizon}
    notices = {n: t + correction_start for n, t in correction.items() if t + correction_start <= horizon} if correction_start is not None else {}
    # A correction NOTICE does not demonstrate that it was read, understood,
    # accepted, or that the original unverified claim is factually false.
    exposed = set(exposures)
    corrected_exposures = exposed & set(notices)
    unresolved = exposed - corrected_exposures
    series = []
    total_unresolved_ticks = 0
    for tick in range(horizon + 1):
        exposure_seen = {n for n, t in exposures.items() if t <= tick}
        notice_seen = {n for n, t in notices.items() if t <= tick}
        unresolved_now = exposure_seen - notice_seen
        total_unresolved_ticks += len(unresolved_now)
        series.append({
            "tick": tick,
            "cumulative_unverified_exposures": len(exposure_seen),
            "cumulative_synthetic_correction_notices": len(notice_seen),
            "exposures_without_correction_notice": len(unresolved_now),
        })
    receiver = record["reported_receiver"]
    first_claim = exposures.get(receiver)
    first_notice = notices.get(receiver)
    return {
        "kind": "SIMULATED_NOTICE_REACH_NOT_ACCEPTANCE",
        "correction_start_tick": correction_start,
        "horizon": horizon,
        "claim_exposure_ids": sorted(exposed),
        "correction_notice_ids": sorted(notices),
        "exposed_without_notice_at_horizon": sorted(unresolved),
        "exposed_with_notice_at_horizon": sorted(corrected_exposures),
        "uncorrected_exposure_ticks": total_unresolved_ticks,
        "receiver_exposure_tick": first_claim,
        "receiver_correction_notice_tick": first_notice,
        "receiver_notice_lag_ticks": max(0, first_notice - first_claim) if first_claim is not None and first_notice is not None else None,
        "series": series,
        "historical_exposures_retained": True,
        "correction_truth_independently_verified": None,
        "correction_receiver_acknowledged": None,
        "real_world_harm_reduced": None,
    }


def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    validate_pair(record)
    early = scenario(record, 0)
    scheduled = scenario(record, record["correction_start_tick"])
    baseline = scenario(record, None)
    families = {c["source_family"] for c in record["source_copies"]}
    assert len(families) <= len(record["source_copies"])
    return {
        "schema": "CoAll.CounterContagion.SyntheticEvidence.R0",
        "state": "TESTED_SYNTHETIC_SOURCE_ONLY__NO_REAL_TRANSMISSION_OR_RECEIVER",
        "version": "0.1",
        "time_basis": "SIMULATION_TICKS_ONLY_NOT_COTIME_UTC",
        "source_copies": len(record["source_copies"]),
        "distinct_source_families": len(families),
        "independent_source_verification": None,
        "baseline_without_correction": baseline,
        "scheduled_correction": scheduled,
        "early_correction": early,
        "synthetic_early_versus_scheduled_delta_uncorrected_ticks": early["uncorrected_exposure_ticks"] - scheduled["uncorrected_exposure_ticks"],
        "speedo_shadow_projection": {
            "activity_series_kind": "SYNTHETIC_ONLY",
            "source_family_count": len(families),
            "copy_count": len(record["source_copies"]),
            "comparison": "SEE_THREE_SCENARIOS_AND_UNCORRECTED_EXPOSURE_TICKS",
            "verified_receiver_benefit": None,
            "independent_receiver_readproof": None,
            "actual_correction_accuracy": None,
            "current_runtime_health": None,
        },
        "oomph_shadow_projection": {
            "automatic_acceleration": False,
            "reason": "NO_RECEIVER_BENEFIT_OR_EFFECT_AUTHORITY",
            "effect_class": "NONE",
        },
        "nonclaims": [
            "SOURCE_COPIES_NE_INDEPENDENT_CONFIRMATION",
            "CORRECTION_NOTICE_NE_TRUTH_OR_ACCEPTANCE",
            "BACKWARD_QUERY_NE_RETROCAUSALITY",
            "SYNTHETIC_TICK_NE_REAL_TIME",
            "DIFFUSION_DELTA_NE_REAL_WORLD_CAUSAL_EFFECT",
            "TRIAL_PASS_NE_COALL_RUNTIME_OR_COEX",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.fixture.read_text(encoding="utf-8"))
        print(json.dumps(evaluate(data), indent=2, sort_keys=True))
    except (OSError, Held, ValueError, KeyError, TypeError) as error:
        parser.exit(2, "HELD: %s\n" % error)


if __name__ == "__main__":
    main()