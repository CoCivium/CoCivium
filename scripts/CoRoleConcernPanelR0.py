#!/usr/bin/env python3
"""Read-only optional concern lens over existing CoRoleSpace preview.

A concern is a typed task relation, not an emotion. No actual person, worker,
consent, permission, spiritual phenomenon, or independent reviewer is created.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

POLICY_PATH = "ai/corole-concern-lens-r0.json"
ROLE_PATH = "schemas/cospawn-contract-v0.1.schema.json"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def build(root: Path, question: str, max_seats: int = 7):
    if not isinstance(question, str) or not question.strip() or len(question) > 800:
        raise ValueError("a bounded nonblank question is required (max 800 characters)")
    if type(max_seats) is not int or not 0 <= max_seats <= 7:
        raise ValueError("max_seats must be 0..7")
    raw_policy = (root / POLICY_PATH).read_bytes()
    raw_roles = (root / ROLE_PATH).read_bytes()
    policy = json.loads(raw_policy)
    roles = json.loads(raw_roles)["properties"]["role"]["enum"]
    if policy["schema"] != "CoRole.ConcernLens.R0.v0.1-candidate":
        raise ValueError("wrong policy schema")
    kinds = policy["kinds"]
    if not isinstance(kinds, dict) or not kinds:
        raise ValueError("missing concern-kind definitions")
    seats = policy["panel"]
    if len(seats) != 7 or len({x["seat"] for x in seats}) != 7:
        raise ValueError("panel seats must be unique and finite")
    if not all(s["role"] in roles for s in seats):
        raise ValueError("unknown operational role")
    if not all(set(s["concerns"]).issubset(kinds) for s in seats):
        raise ValueError("unrecognized concern kind")
    if policy["default_subjective_worry"] != "NOT_INFERRED":
        raise ValueError("subjective states must not be inferred")
    for role, concerns in policy["role_overrides"].items():
        if role not in roles or not isinstance(concerns, list):
            raise ValueError("invalid role override")
        if not set(concerns).issubset(kinds):
            raise ValueError("invalid override concern")
    bounds = policy["bounds"]
    if bounds["max_active_workers"] != 0 or bounds["max_effects"] != 0:
        raise ValueError("unacceptable effect budget")
    if bounds["max_review_rounds"] > 2 or bounds["max_nesting_depth"] > 2:
        raise ValueError("unbounded recursive panel")
    if max_seats > bounds["max_seats"]:
        raise ValueError("seat limit exceeded")
    input_refs = [
        {"path": POLICY_PATH, "sha256": checksum(raw_policy), "bytes": len(raw_policy)},
        {"path": ROLE_PATH, "sha256": checksum(raw_roles), "bytes": len(raw_roles)},
    ]
    chosen = seats[:max_seats]
    # Shared strings and definitions, referenced by ID instead of repeated prose.
    selected_roles = sorted({s["role"] for s in chosen})
    selected_kinds = sorted({kind for s in chosen for kind in s["concerns"]})
    question = question.strip()
    identity = {
        "question": question,
        "source_bindings": input_refs,
        "seats": [{"seat": s["seat"], "role": s["role"], "concerns": s["concerns"]} for s in chosen],
    }
    return {
        "schema": "CoRole.ConcernPanelPlan.R0.v0.1-candidate",
        "state": "UNASSIGNED_PANEL_PLAN__NO_EXECUTION",
        "panel_id": "corole-panel:" + checksum(canonical(identity).encode("utf-8")),
        "question": question,
        "source_bindings": input_refs,
        "role_definition_refs": selected_roles,
        "concern_definition_refs": selected_kinds,
        "seats": [
            {
                "seat_id": s["seat"],
                "role_ref": s["role"],
                "concern_kind_refs": s["concerns"],
                "reviewer": None,
                "independence": "UNKNOWN",
                "subjective_worry": "NOT_INFERRED",
                "epistemic_state": "UNASSESSED",
                "effect_authority": "NONE",
            }
            for s in chosen
        ],
        "unassigned_passive_role_example": {
            "role_ref": "QUIESCENT_RESERVE",
            "concern_kind_refs": policy["role_overrides"]["QUIESCENT_RESERVE"],
            "subjective_worry": "NOT_INFERRED",
        },
        "perspective_lenses": policy["perspectives"],
        "limits": bounds,
        "effects": {"actors_assigned": 0, "workers_started": 0, "permissions_granted": 0, "messages_sent": 0},
        "storage_claim": "REFERENTIAL_DESIGN_ONLY__NO_BENCHMARK",
        "next_gate": "BIND_NAMED_TASK_AND_ACTUAL_REVIEWERS_WITH_EXISTING_AUTHORITY_BEFORE_EFFECTS",
        "nonclaims": policy["nonclaims"],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--question", required=True)
    p.add_argument("--max-seats", type=int, default=7)
    args = p.parse_args()
    result = build(args.repo_root, args.question, args.max_seats)
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
