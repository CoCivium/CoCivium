#!/usr/bin/env python3
"""CoWave+ bounded, source-bound DIVERSITY PROPOSALS, never execution.

Consumes the existing public frontier index. No session-provider access, no
scheduler, no send, no X2 observation, no cross-session auto-drain or mutation.
A repeated *control* is legitimate only with its own proof, not a novelty label.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "CoAll.WaveDiversityProposal.R0"
FRONT_SCHEMA = "cocivium.frontier-index.r0"
INDEX_PATH = "docs/Evolution/FRONTIER_EVIDENCE_INDEX_R0.json"
# Audience/method/media/horizon/falsifier profiles supplement existing front IDs;
# the public frontier index remains the only source of front status/next gates.
PROFILES = {
    "receiver-evidence": ("readback-challenge", "operator", "receipt-test", "immediate", "forged-ack", 7),
    "x2-coorb-ux": ("human-first-use", "newcomer", "orb-journey", "day", "stale-visible-state", 6),
    "runtime-recovery": ("fault-injection", "maintainer", "restart-trace", "week", "crash-after-commit", 7),
    "conav-coregroup": ("source-rebound", "remote-reader", "nested-map", "day", "silent-missed-front", 5),
    "comvp-colockstep": ("rollback-qualification", "builder", "release-diff", "week", "intermediate-regression", 6),
    "coprimath-gdside": ("null-hypothesis-test", "researcher", "causal-model", "month", "baseline-beats-future", 4),
    "costead-onboarding": ("accessibility-task", "novice", "guided-setup", "day", "unrecoverable-first-use", 5),
    "comap-megascroller": ("reader-comprehension", "independent-reader", "public-megascroller", "day", "lost-navigation-context", 5),
    "colue-outreach": ("consent-route-test", "recipient", "mail-draft-review", "week", "cross-mailbox-send", 5),
    "colensmedia-lineage": ("media-provenance-audit", "access-reader", "media-graph", "month", "private-source-leak", 4),
    "cobrowser-cocarry": ("session-rebind", "session-owner", "browser-recovery", "immediate", "unsent-text-loss", 6),
}
AXES = ("method", "audience", "substrate", "horizon", "counterexample")
NONCLAIMS = (
    "WAVE_PROPOSAL_NE_EXECUTION", "ROTATION_NE_PARALLEL_SESSION_COORDINATION",
    "PUBLIC_FRONT_INDEX_NE_COMPLETE_HISTORY", "SOURCE_GIT_NE_RECEIVER_READPROOF",
    "NOVELTY_NE_VALUE", "REPLAY_FOR_CONTROLS_REMAINS_ALLOWED",
    "GDSIDE_NE_AUTHORITY", "NO_24H_OR_X2_RUNTIME_PROOF",
    "COPRE_ECHO_NE_PUBLICATION_AUTHORITY", "ONE_PROPOSAL_NE_ONE_RUNNING_ACTUATOR",
)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def utc(value):
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("HOLD_OBSERVATION_TIME")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("HOLD_OBSERVATION_TIME") from exc
    if dt.tzinfo is None or dt.utcoffset() != timedelta(0):
        raise ValueError("HOLD_OBSERVATION_TIME")
    return dt.isoformat().replace("+00:00", "Z")


def axes_for(front):
    method, audience, substrate, horizon, counterexample, _ = PROFILES[front]
    return dict(zip(AXES, (method, audience, substrate, horizon, counterexample)))


def distance(a, b):
    """Meaningful change across method/receiver/media/horizon/falsifier, not wording."""
    return sum(a[k] != b[k] for k in AXES)


def choose(index, observed_at_utc, *, limit=4, prior=()):
    stamp = utc(observed_at_utc)
    if type(limit) is not int or not 1 <= limit <= len(PROFILES):
        raise ValueError("HOLD_WAVE_LIMIT")
    if not isinstance(index, dict) or index.get("schema") != FRONT_SCHEMA:
        raise ValueError("HOLD_SOURCE_FRONT_INDEX")
    fronts = index.get("fronts")
    if not isinstance(fronts, list) or not 1 <= len(fronts) <= 256:
        raise ValueError("HOLD_SOURCE_FRONT_SET")
    if not isinstance(prior, (tuple, list)) or len(prior) > 128:
        raise ValueError("HOLD_PRIOR_WAVE_HISTORY")
    current = {}
    for front in fronts:
        if not isinstance(front, dict) or not isinstance(front.get("id"), str):
            raise ValueError("HOLD_FRONT_ID")
        fid = front["id"]
        if fid in current:
            raise ValueError("HOLD_DUPLICATE_FRONT")
        if not isinstance(front.get("next_gate"), str) or not front["next_gate"].strip():
            raise ValueError("HOLD_UNQUALIFIED_NEXT_GATE")
        if front.get("status") not in {"proposed", "source_committed", "tests_executed", "independently_observed", "released"}:
            raise ValueError("HOLD_UNTYPED_FRONT_STATUS")
        current[fid] = front
    previous = []
    for row in prior:
        if not isinstance(row, dict) or row.get("front_id") not in PROFILES:
            raise ValueError("HOLD_PRIOR_WAVE_ID")
        if row.get("axes") != axes_for(row["front_id"]):
            raise ValueError("HOLD_UNBOUND_WAVE_AXES")
        if row.get("state") == "RECEIVER_EFFECT_VERIFIED":
            raise ValueError("HOLD_EXTERNAL_READPROOF_UNSUPPORTED")
        if row.get("state") != "PROPOSED_ONLY":
            raise ValueError("HOLD_UNTYPED_WAVE_STATE")
        previous.append(row)
    source = digest(index)
    remaining = {fid for fid in current if fid in PROFILES and current[fid]["status"] != "released"}
    proposals = []
    while len(proposals) < limit and remaining:
        candidates = []
        for fid in remaining:
            candidate_axes = axes_for(fid)
            if any(p["front_id"] == fid for p in previous):
                continue  # no silent same-wave replay; controls need a separate explicit test
            most_recent = (previous + proposals)[-2:]
            nearest = min((distance(candidate_axes, p["axes"]) for p in most_recent), default=5)
            if nearest < 3:
                continue  # no synthetic novelty by mere renaming of a front
            priority = PROFILES[fid][5]
            candidates.append((nearest, priority, fid))
        if not candidates:
            break
        _, _, chosen = sorted(candidates, key=lambda c: (-c[0], -c[1], c[2]))[0]
        remaining.remove(chosen)
        f = current[chosen]
        profile = axes_for(chosen)
        signature = digest({"front_id": chosen, "axes": profile})
        proposals.append({
            "front_id": chosen, "state": "PROPOSED_ONLY", "axes": profile,
            "semantic_fingerprint_sha256": signature,
            "proposal_id": f"cowave:{chosen}:{source[:12]}:{signature[:12]}",
            "source_status": f["status"], "next_gate": f["next_gate"],
            "independent_readproof": None, "external_effect": "NONE",
            "collision_domain": chosen,
            "next_step": "OBSERVE_OR_CHALLENGE_ONLY_UNTIL_AUTHORIZED",
        })
    return {
        "schema": SCHEMA,
        "source_index": INDEX_PATH, "source_sha256": source,
        "as_of_declared_utc": stamp,
        "state": "PROPOSED_ONLY" if proposals else "HOLD_NO_ADMISSIBLE_DISTINCT_WAVE",
        "proposals": proposals,
        "held_fronts": sorted(set(current) - {p["front_id"] for p in proposals}),
        "unknown_profile_fronts": sorted(set(current) - set(PROFILES)),
        "single_actuator_elected": False, "receivers_acknowledged": 0,
        "effects_performed": 0, "sessions_drained": 0,
        "next_wake": "ON_VERIFIED_SOURCE_OR_RECEIVER_DELTA",
        "nonclaims": list(NONCLAIMS),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = choose(json.loads(args.index.read_text(encoding="utf-8")), args.as_of, limit=args.limit)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream: stream.write(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
