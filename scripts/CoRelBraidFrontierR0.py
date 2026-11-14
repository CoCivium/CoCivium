#!/usr/bin/env python3
"""Read-only CoRel/CoBraid logical frontier planner R0.

Input declarations are NOT independent evidence. Does not run workers, check
remote source bytes, grant authority or complete user tasks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "CoAll.CoRelBraid.FrontierInput.R0"
OUTPUT = "CoAll.CoRelBraid.FrontierPlan.R0"
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,95}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
STATES = {"DECLARED_DONE", "CANDIDATE", "HELD"}
MUTATIONS = {"READ_ONLY", "EFFECT_GATED"}
MAX_NODES = 64
MAX_EDGES = 256


class Hold(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Hold(reason)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
        separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def validate(payload):
    require(type(payload) is dict and set(payload) == {
        "schema", "work_id", "source_revision", "max_parallel", "tasks",
    }, "INVALID_ROOT")
    require(payload["schema"] == SCHEMA, "INVALID_SCHEMA")
    require(type(payload["work_id"]) is str and ID.fullmatch(payload["work_id"]), "INVALID_WORK_ID")
    require(type(payload["source_revision"]) is str
            and SHA.fullmatch(payload["source_revision"]), "INVALID_SOURCE_REVISION")
    require(type(payload["max_parallel"]) is int
            and 1 <= payload["max_parallel"] <= 8, "INVALID_BUDGET")
    tasks = payload["tasks"]
    require(type(tasks) is list and 1 <= len(tasks) <= MAX_NODES, "INVALID_TASK_COUNT")
    ids = [t.get("id") for t in tasks if type(t) is dict]
    require(len(ids) == len(tasks) and len(ids) == len(set(ids)),
            "DUPLICATE_OR_MALFORMED_TASK")
    require(all(type(i) is str and ID.fullmatch(i) for i in ids), "INVALID_TASK_ID")
    idset = set(ids)
    edges = 0
    for t in tasks:
        require(set(t) == {
            "id", "depends_on", "state", "mutation_class", "collision_domain",
            "source_ref", "source_sha256", "receipt_ref", "priority",
        }, "INVALID_TASK_FIELDS")
        require(t["state"] in STATES and t["mutation_class"] in MUTATIONS, "INVALID_TASK_STATE")
        require(type(t["depends_on"]) is list
                and all(type(d) is str for d in t["depends_on"]), "INVALID_DEPENDENCIES")
        require(len(set(t["depends_on"])) == len(t["depends_on"]), "DUPLICATE_DEPENDENCY")
        require(all(d in idset and d != t["id"] for d in t["depends_on"]),
                "UNKNOWN_OR_SELF_DEPENDENCY")
        edges += len(t["depends_on"])
        require(type(t["collision_domain"]) is str
                and ID.fullmatch(t["collision_domain"]), "INVALID_COLLISION_DOMAIN")
        require(type(t["source_ref"]) is str and t["source_ref"].strip()
                and len(t["source_ref"]) <= 512, "SOURCE_REQUIRED")
        require(type(t["source_sha256"]) is str
                and SHA.fullmatch(t["source_sha256"]), "SOURCE_SHA_REQUIRED")
        require(type(t["priority"]) is int and 0 <= t["priority"] <= 9, "INVALID_PRIORITY")
        if t["state"] == "DECLARED_DONE":
            require(type(t["receipt_ref"]) is str and t["receipt_ref"].strip(),
                    "DONE_REQUIRES_DECLARED_RECEIPT")
            require(t["mutation_class"] == "READ_ONLY", "EFFECT_CANNOT_BE_SELF_CERTIFIED_DONE")
        else:
            require(t["receipt_ref"] is None, "NON_DONE_MUST_NOT_HAVE_RECEIPT")
    require(edges <= MAX_EDGES, "EDGE_BUDGET")
    indeg = {i: 0 for i in ids}
    child = {i: [] for i in ids}
    for t in tasks:
        for dep in t["depends_on"]:
            indeg[t["id"]] += 1
            child[dep].append(t["id"])
    wave = sorted(i for i in ids if indeg[i] == 0)
    levels = []
    visited = 0
    while wave:
        levels.append(wave)
        visited += len(wave)
        nxt = []
        for u in wave:
            for v in child[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    nxt.append(v)
        wave = sorted(nxt)
    require(visited == len(ids), "CAUSAL_CYCLE_REJECTED")
    by_id = {t["id"]: t for t in tasks}
    for t in tasks:
        if t["state"] == "DECLARED_DONE":
            # Check order only after detecting cycles, so the root cause wins.
            # A declared receipt is still unverified until receiver-origin proof.
            require(all(by_id[dep]["state"] == "DECLARED_DONE"
                        for dep in t["depends_on"]),
                    "DECLARED_DONE_WITH_INCOMPLETE_PREREQUISITE")
    return levels


def compile_frontier(payload):
    levels = validate(payload)
    by_id = {t["id"]: t for t in payload["tasks"]}
    candidates = []
    deferred = []
    complete = []
    for t in sorted(payload["tasks"], key=lambda a: (a["priority"], a["id"])):
        if t["state"] == "DECLARED_DONE":
            complete.append({
                "id": t["id"], "receipt_ref": t["receipt_ref"],
                "status": "DECLARED_ONLY_NOT_INDEPENDENTLY_VERIFIED",
            })
            continue
        reasons = []
        if t["state"] == "HELD":
            reasons.append("TASK_HELD")
        if t["mutation_class"] == "EFFECT_GATED":
            reasons.append("EFFECT_AUTHORITY_UNAVAILABLE")
        for dep in sorted(t["depends_on"]):
            if by_id[dep]["state"] != "DECLARED_DONE":
                reasons.append("DEP_NOT_DECLARED_DONE:" + dep)
        if reasons:
            deferred.append({"id": t["id"], "reasons": reasons})
        else:
            candidates.append(t)
    elected = []
    collision_held = []
    domains = set()
    for t in candidates:
        if len(elected) >= payload["max_parallel"]:
            collision_held.append({"id": t["id"], "reason": "PARALLEL_BUDGET_EXHAUSTED"})
        elif t["collision_domain"] in domains:
            collision_held.append({"id": t["id"], "reason": "COLLISION_DOMAIN_ALREADY_ELECTED"})
        else:
            domains.add(t["collision_domain"])
            elected.append({
                "id": t["id"], "collision_domain": t["collision_domain"],
                "source_ref": t["source_ref"], "source_sha256": t["source_sha256"],
                "state": "LOGICAL_READ_ONLY_CANDIDATE",
                "authority": "NONE_GRANTED", "external_effect": "NONE",
                "actual_source_readproof": "NOT_OBSERVED",
            })
    return {
        "schema": OUTPUT, "state": "READ_ONLY_CAUSAL_PLAN__NO_RUNTIME",
        "work_id": payload["work_id"], "declared_source_revision": payload["source_revision"],
        "input_digest": digest(payload),
        "causal_levels_potential_only": levels,
        "logical_parallel_frontier": elected,
        "declared_complete_unverified": complete,
        "deferred": sorted(deferred, key=lambda x: x["id"]),
        "collision_or_budget_held": sorted(collision_held, key=lambda x: x["id"]),
        "metrics": {
            "declared_nodes": len(payload["tasks"]),
            "potential_levels": len(levels),
            "logical_candidates": len(candidates),
            "parallel_elected": len(elected),
            "active_workers": 0, "external_effects": 0, "receiver_acks": 0,
        },
        "rails": [
            "DECLARED_RECEIPT_NE_VERIFIED_EFFECT", "LOGICAL_FRONTIER_NE_WORKER",
            "HELD_EDGE_NE_HELD_GRAPH", "SHARED_COLLISION_DOMAIN_NE_PARALLEL_EFFECT",
            "CAUSAL_DAG_NE_PROVEN_CAUSALITY", "SOURCE_HASH_DECLARED_NE_SOURCE_READBACK",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    args = ap.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(compile_frontier(source), sort_keys=True, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (Hold, KeyError, TypeError, OSError, ValueError) as err:
        raise SystemExit("HOLD: " + str(err))
