#!/usr/bin/env python3
"""Deterministic, source-only, synthetic pattern diffusion and inverse reachability.

This program performs no network calls, actions, model invocations, or source promotions.
Edges are hypothetical pathways, not observed causal transmission or consent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

MAX_NODES = 30
MAX_EDGES = 120
MAX_TICKS = 12


class Held(ValueError):
    """Invalid or unsupported input, not a source of action authority."""


def _check_probability(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise Held(f"INVALID_{name.upper()}")


def validate(data):
    if not isinstance(data, dict) or data.get("schema") != "CoAll.PatternContagion.SyntheticGraph.R0":
        raise Held("INVALID_SCHEMA")
    nodes, edges = data.get("nodes"), data.get("edges")
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= MAX_NODES:
        raise Held("NODE_BUDGET_OR_TYPE")
    if not isinstance(edges, list) or len(edges) > MAX_EDGES:
        raise Held("EDGE_BUDGET_OR_TYPE")
    ids = set()
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"]:
            raise Held("INVALID_NODE_ID")
        if node["id"] in ids:
            raise Held("DUPLICATE_NODE")
        ids.add(node["id"])
        _check_probability(node.get("threshold"), "threshold")
        if not isinstance(node.get("allow_synthetic_exposure"), bool):
            raise Held("MISSING_EXPOSURE_POLICY")
    seen = set()
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("from") not in ids or edge.get("to") not in ids:
            raise Held("UNRESOLVED_EDGE")
        if edge["from"] == edge["to"]:
            raise Held("SELF_EDGE_UNSUPPORTED")
        key = (edge["from"], edge["to"])
        if key in seen:
            raise Held("DUPLICATE_EDGE")
        seen.add(key)
        _check_probability(edge.get("strength"), "strength")
        if edge.get("relation_type") != "PATTERN_PROPAGATION_CANDIDATE":
            raise Held("UNTYPED_OR_FALSE_CAUSAL_EDGE")
        if edge.get("authority") != "NONE":
            raise Held("EDGE_CANNOT_GRANT_AUTHORITY")
    seeds = data.get("seeds")
    if not isinstance(seeds, list) or len(seeds) != len(set(seeds)) or any(s not in ids for s in seeds):
        raise Held("INVALID_SEEDS")
    if any(not next(n for n in nodes if n["id"] == s)["allow_synthetic_exposure"] for s in seeds):
        raise Held("DISALLOWED_SEED")
    steps = data.get("steps")
    if isinstance(steps, bool) or not isinstance(steps, int) or not 0 <= steps <= MAX_TICKS:
        raise Held("INVALID_STEP_BUDGET")
    noise = data.get("noise_amplitude", 0)
    _check_probability(noise, "noise_amplitude")
    if noise > 0.25:
        raise Held("NOISE_BUDGET_EXCEEDED")
    if not isinstance(data.get("seed_number"), int) or isinstance(data["seed_number"], bool):
        raise Held("INVALID_RANDOM_SEED")
    if data.get("external_effects") != "NONE":
        raise Held("EXTERNAL_EFFECTS_PROHIBITED")
    return nodes, edges


def perturb(graph_seed, tick, dest, amplitude):
    if amplitude == 0:
        return 0.0
    raw = hashlib.sha256(f"{graph_seed}|{tick}|{dest}|R0".encode()).digest()
    u = int.from_bytes(raw[:8], "big") / float(2**64)
    return (2*u-1)*amplitude


def forward(data, removed_edges=()):
    nodes, edges = validate(data)
    ids = {n["id"]: n for n in nodes}
    removed = set(removed_edges)
    if any((not isinstance(x, tuple) or len(x) != 2) for x in removed):
        raise Held("INVALID_REMOVED_EDGE")
    active = set(data["seeds"])
    trail = [{"tick": 0, "newly_active": sorted(active), "cumulative_active": len(active)}]
    for tick in range(1, data["steps"] + 1):
        new = set()
        for dest in sorted(ids):
            if dest in active or not ids[dest]["allow_synthetic_exposure"]:
                continue
            strength = max((e["strength"] for e in edges
                            if e["to"] == dest and e["from"] in active
                            and (e["from"], e["to"]) not in removed), default=0.0)
            if strength == 0:
                continue
            threshold = ids[dest]["threshold"]
            adjusted = min(1.0, max(0.0, strength + perturb(data["seed_number"], tick, dest, data.get("noise_amplitude", 0))))
            if adjusted >= threshold:
                new.add(dest)
        active |= new
        trail.append({"tick": tick, "newly_active": sorted(new), "cumulative_active": len(active)})
    return {
        "mode": "SYNTHETIC_FORWARD_PROJECTION_NOT_FORECAST",
        "active": sorted(active),
        "trail": trail,
        "synthetic_adoption_count": len(active),
        "verified_benefit_count": None,
        "independent_receiver_ack_count": None,
        "observed_real_world_transmission": False,
    }


def backward_candidates(data, target, mode="BACKTRACE"):
    nodes, edges = validate(data)
    ids = {n["id"] for n in nodes}
    if target not in ids or mode not in ("BACKTRACE", "BACKCAST"):
        raise Held("INVALID_TARGET_OR_MODE")
    reversed_frontier, reachable = {target}, {target}
    while reversed_frontier:
        older = {e["from"] for e in edges if e["to"] in reversed_frontier and e["strength"] > 0
                 and e["from"] not in reachable}
        reachable |= older
        reversed_frontier = older
    return {
        "mode": "POSSIBLE_ANCESTORS_NOT_CAUSES" if mode == "BACKTRACE" else "POSSIBLE_UPSTREAM_LEVERS_NOT_EFFECT_PROMISES",
        "target": target,
        "candidate_upstream": sorted(reachable - {target}),
        "retrocausality_claim": False,
        "causality_established": False,
    }


def counterfactual(data, blocked):
    nodes, edges = validate(data)
    if any(b not in {(e["from"], e["to"]) for e in edges} for b in blocked):
        raise Held("UNKNOWN_COUNTERFACTUAL_EDGE")
    base = forward(data)
    changed = forward(data, removed_edges=blocked)
    return {
        "mode": "STRUCTURAL_COUNTERFACTUAL_SYNTHETIC_ONLY",
        "reference_synthetic_active": base["synthetic_adoption_count"],
        "removed_edges_synthetic_active": changed["synthetic_adoption_count"],
        "delta_synthetic_active": changed["synthetic_adoption_count"] - base["synthetic_adoption_count"],
        "real_world_causal_effect": None,
    }


def emit(data):
    f = forward(data)
    observation = data["observation_target"]
    aim = data["desired_future_target"]
    blocked = [tuple(pair) for pair in data.get("counterfactual_blocked_edges", [])]
    return {
        "schema": "CoAll.PatternContagion.SyntheticEvidence.R0",
        "work_id": "CoPatternContagion.20261110.R0",
        "state": "SOURCE_ONLY_SYNTHETIC_NO_RECEIVER_NO_RUNTIME_NO_AUTHORITIES",
        "forward": f,
        "backtrace": backward_candidates(data, observation),
        "backcast": backward_candidates(data, aim, "BACKCAST"),
        "counterfactual": counterfactual(data, blocked),
        "speedo_projection": {
            "activity_needle": f["synthetic_adoption_count"],
            "benefit_needle": None,
            "independent_proof_needle": None,
            "counterneedle": "SYNTHETIC_ONLY_CORRELATED_TRANSMISSION_AND_COST_NOT_MEASURED",
            "time_basis": "SIMULATION_TICK_NOT_WALL_CLOCK",
            "status": "NOT_LIVE_TELEMETRY",
        },
        "oomph_projection": {
            "pace_advice": "HOLD_EFFECTS_RESEARCH_ONLY",
            "source_reason": "NO_VERIFIED_RECEIVER_BENEFIT_OR_EFFECT_AUTHORITY",
            "automatic_acceleration": False,
        },
        "coobject_relation": "CANDIDATE_EDGES_ONLY__NO_SOURCE_OR_PERMISSION_REWRITE",
        "cotume_relation": "UNRESOLVED_ALIAS_CANDIDATE__DO_NOT_NORMALIZE",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("fixture", type=Path)
    args = p.parse_args()
    try:
        data = json.loads(args.fixture.read_text(encoding="utf-8"))
        print(json.dumps(emit(data), sort_keys=True, indent=2))
    except (Held, OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        p.exit(2, f"HELD: {error}\n")


if __name__ == "__main__":
    main()
