#!/usr/bin/env python3
"""Deterministic CoHereNow convergence canary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ZERO_EFFECTS = {
    "network_calls": 0,
    "provider_mutations": 0,
    "session_closures": 0,
    "session_merges": 0,
    "source_deletions": 0,
    "external_messages": 0,
    "account_changes": 0,
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def run(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == "CoHereNow.ConvergenceFixture.R0.v0.1", "wrong schema")
    fronts = payload.get("fronts")
    require(isinstance(fronts, list) and len(fronts) >= 2, "at least two fronts required")

    goal = payload.get("shared_goal_id")
    require(isinstance(goal, str) and goal, "shared_goal_id required")
    require(all(f.get("front_id") for f in fronts), "front_id required")
    require(len({f["front_id"] for f in fronts}) == len(fronts), "duplicate front_id")
    require(all(f.get("source_ref") for f in fronts), "source_ref required")
    require(all(f.get("confidentiality") == fronts[0]["confidentiality"] for f in fronts), "confidentiality mismatch")
    require(all(f.get("authority_ceiling") == fronts[0]["authority_ceiling"] for f in fronts), "authority mismatch")

    operator_sets = [set(f.get("action_operators", [])) for f in fronts]
    shared_ops = sorted(set.intersection(*operator_sets))
    require(len(shared_ops) >= 4, "insufficient action-operator overlap")

    next_sets = [set(f.get("candidate_next_actions", [])) for f in fronts]
    shared_next = sorted(set.intersection(*next_sets))
    require(len(shared_next) == 1, "expected exactly one shared next action")

    specialties = sorted({f["specialty"] for f in fronts})
    require(len(specialties) == len(fronts), "fixture must preserve distinct specialties")

    lineage = [
        {
            "front_id": f["front_id"],
            "source_ref": f["source_ref"],
            "specialty": f["specialty"],
            "unresolved": list(f.get("unresolved", [])),
            "source_disposition": "PRESERVED",
        }
        for f in fronts
    ]

    projection = {
        "schema": "CoHereNow.ConvergenceProjection.R0.v0.1",
        "state": "PASS_SYNTHETIC_SHARED_FRONT__NO_SESSION_MUTATION",
        "shared_goal_id": goal,
        "source_front_count": len(fronts),
        "convergence_group_count": 1,
        "shared_action_operators": shared_ops,
        "preserved_specialties": specialties,
        "elected_next_action": shared_next[0],
        "authority_ceiling": fronts[0]["authority_ceiling"],
        "confidentiality": fronts[0]["confidentiality"],
        "source_lineage": lineage,
        "uncertainty": sorted({u for f in fronts for u in f.get("unresolved", [])}),
        "effects": dict(ZERO_EFFECTS),
        "rails": [
            "CONVERGENCE_NE_MERGE_OF_TRUTH",
            "SHARED_FRONT_NE_SOURCE_DELETION",
            "SIMILAR_LANGUAGE_NE_SAME_WORK",
            "USER_VISIBLE_COMPRESSION_NE_BACKEND_COLLAPSE",
            "FRONTIER_COMPACTION_NE_LOSSLESS_TOTALITY",
            "SESSION_COUNT_NE_FRONT_COUNT",
        ],
        "nonclaims": [
            "SYNTHETIC_FRONT_NE_LIVE_SESSION_INGESTION",
            "PROJECTION_NE_PROVIDER_SESSION_MERGE",
            "NO_X2_RUNTIME_INTEGRATION_PROVED",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
        ],
    }

    require(all(x["source_disposition"] == "PRESERVED" for x in lineage), "source lineage not preserved")
    require(all(v == 0 for v in projection["effects"].values()), "nonzero effect")
    return projection


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", type=Path, required=True)
    args = p.parse_args()
    payload = json.loads(args.fixture.read_text(encoding="utf-8"))
    print(json.dumps(run(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
