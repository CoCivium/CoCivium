#!/usr/bin/env python3
"""CoBF+ future-aware candidate shadow selector, with zero external effects.

A *structurally declared* independent measurement is not an independently
authenticated receiver. No source-level result is deployment, release, or
real-world reception proof. An authorized release controller must separately
verify evidence/rights/rollback and observe recipient outcomes.
"""
from __future__ import annotations

import re

EVENTS = {"MATERIAL_SOURCE_DELTA", "INDEPENDENT_RECEIVER_DELTA", "USER_COW_REVIEW"}
AUDIENCES = {"PUBLIC_HUMAN", "PUBLIC_MACHINE", "PRIVATE_OPERATOR", "HEADLESS_WORKER"}
METRICS = {"first_use_ms", "comprehension_per_1000", "task_success_per_1000", "interruptions"}
SHA = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[a-zA-Z][a-zA-Z0-9_.:-]{2,79}\Z")
REQ = {"id", "work_id", "audience", "source_sha256", "privacy", "currentness_at",
       "evidence", "metrics", "focus_interference"}
FUTURE = {"future_id", "epistemic", "horizon_seconds", "falsifier", "inverse_ref", "null_ref"}
BASELINE_STATE = "SELECTED_LAST_GOOD"


def valid_metrics(x: object) -> bool:
    if not isinstance(x, dict) or set(x) != METRICS:
        return False
    if any(type(v) is not int for v in x.values()):
        return False
    return (0 <= x["first_use_ms"] <= 600_000
            and 0 <= x["comprehension_per_1000"] <= 1000
            and 0 <= x["task_success_per_1000"] <= 1000
            and 0 <= x["interruptions"] <= 1000)


def valid_source(x: object, *, is_future: bool) -> bool:
    expected = REQ | ({"future"} if is_future else {"state"})
    if not isinstance(x, dict) or set(x) != expected:
        return False
    for k in ("id", "work_id"):
        if not isinstance(x[k], str) or not ID.fullmatch(x[k]):
            return False
    if (x["audience"] not in AUDIENCES or x["privacy"] != "PUBLIC_SAFE"
            or type(x["currentness_at"]) is not int
            or x["currentness_at"] < 0
            or type(x["focus_interference"]) is not bool
            or x["focus_interference"]
            or not isinstance(x["source_sha256"], str)
            or not SHA.fullmatch(x["source_sha256"])
            or not valid_metrics(x["metrics"])):
        return False
    if x["evidence"] not in {"SYNTHETIC_FIXTURE", "DECLARED_RECEIVER_MEASURE"}:
        return False
    if not is_future:
        return x["state"] == BASELINE_STATE
    f = x["future"]
    return (isinstance(f, dict) and set(f) == FUTURE
            and isinstance(f["future_id"], str) and ID.fullmatch(f["future_id"])
            and f["epistemic"] in {"PREFERRED", "SCENARIO", "PREDICTED"}
            and type(f["horizon_seconds"]) is int and 1 <= f["horizon_seconds"] <= 31536000
            and all(isinstance(f[k], str) and 4 <= len(f[k]) <= 160
                    for k in ("falsifier", "inverse_ref", "null_ref")))


def dominates(a: dict, b: dict) -> bool:
    """All measured dimensions no worse, at least one better, no hidden weights."""
    ge = (a["task_success_per_1000"] >= b["task_success_per_1000"]
          and a["comprehension_per_1000"] >= b["comprehension_per_1000"]
          and a["first_use_ms"] <= b["first_use_ms"]
          and a["interruptions"] <= b["interruptions"])
    return ge and any(a[k] != b[k] for k in METRICS)


def shadow_select(baseline: object, candidates: object, *, event: str,
                  now_s: int, max_age_s: int = 86400) -> dict:
    """Bounded event-driven read-only election; never invokes a deployment."""
    result = {
        "schema": "CoBF.FutureShadow.R0",
        "state": "HOLD", "selected_live_id": None, "shadow_candidate_ids": [],
        "holds": [], "effect": "NONE", "model_authority": False,
        "release_authorized": False, "receiver_ack": "NOT_ESTABLISHED",
        "global_front_binding": False, "focus_changes": 0,
        "next_wake": "NEW_QUALIFIED_MATERIAL_EVENT",
        "nonclaims": [
            "SCENARIO_NE_OBSERVATION", "FUTURE_PULL_NE_CAUSATION",
            "SOURCE_MEASUREMENT_DECLARATION_NE_INDEPENDENT_ATTESTATION",
            "SHADOW_ELECTION_NE_RELEASE", "EVERY_SECOND_POLL_NE_EVOLUTION",
            "NO_CLAIMS_OF_CONSCIOUSNESS_OR_PHYSICAL_FIELDS",
        ],
    }
    if (type(now_s) is not int or now_s < 0 or type(max_age_s) is not int
            or max_age_s < 1):
        return {**result, "holds": ["INVALID_TIME"]}
    if not valid_source(baseline, is_future=False):
        return {**result, "holds": ["INVALID_LAST_GOOD"]}
    result["selected_live_id"] = baseline["id"]
    if now_s < baseline["currentness_at"] or now_s-baseline["currentness_at"] > max_age_s:
        return {**result, "holds": ["STALE_OR_FUTURE_DATED_LAST_GOOD"]}
    if event not in EVENTS:
        return {**result, "state": "QUIET_NO_QUALIFIED_EVENT",
                "holds": ["TIMER_ALONE_CANNOT_REWRITE_FRONT"]}
    if not isinstance(candidates, list) or len(candidates) > 8:
        return {**result, "holds": ["INVALID_CANDIDATE_BUDGET"]}
    seen = {baseline["id"]}
    measured = []
    unmeasured = []
    invalid = []
    for c in candidates:
        if not valid_source(c, is_future=True):
            invalid.append("INVALID_CANDIDATE")
            continue
        if c["id"] in seen:
            invalid.append("DUPLICATE_ID")
            continue
        seen.add(c["id"])
        if (c["work_id"] != baseline["work_id"]
                or c["audience"] != baseline["audience"]):
            invalid.append("CROSS_WORK_OR_AUDIENCE")
            continue
        if now_s < c["currentness_at"] or now_s-c["currentness_at"] > max_age_s:
            invalid.append("STALE_OR_FUTURE_DATED_CANDIDATE")
            continue
        if c["evidence"] != "DECLARED_RECEIVER_MEASURE":
            unmeasured.append(c["id"])
            continue
        if dominates(c["metrics"], baseline["metrics"]):
            measured.append(c)
        else:
            invalid.append("NOT_PARETO_BETTER_THAN_BASELINE")
    if measured:
        frontier = [c["id"] for c in measured if not any(
            d["id"] != c["id"] and dominates(d["metrics"], c["metrics"])
            for d in measured
        )]
        return {**result, "state": "SHADOW_PARETO_IMPROVEMENT_CANDIDATES",
                "shadow_candidate_ids": sorted(frontier),
                "holds": sorted(set(invalid + ["RELEASE_AND_INDEPENDENT_ATTESTATION_HELD"]))}
    if unmeasured:
        return {**result, "state": "SHADOW_HYPOTHESES_NEED_MEASUREMENT",
                "shadow_candidate_ids": sorted(unmeasured),
                "holds": sorted(set(invalid + ["NO_INDEPENDENT_MEASUREMENTS"]))}
    return {**result, "state": "KEEP_LAST_GOOD",
            "holds": sorted(set(invalid or ["NO_DEMONSTRATED_BETTER"]))}
