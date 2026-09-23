#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def stable_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_deltas(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        rows = value
    elif isinstance(value, dict) and isinstance(value.get("deltas"), list):
        rows = value["deltas"]
    else:
        raise ValueError("deltas input must be an array or an object with deltas[]")
    if not all(isinstance(x, dict) for x in rows):
        raise ValueError("every delta must be an object")
    return rows


def lane_map(lanes: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in lanes.get("domains", []):
        if not isinstance(row, list) or len(row) != 3:
            continue
        domain, repos, mode = row
        out[str(domain)] = {"repositories": list(repos), "mode": str(mode)}
    return out


def repo_visibility_map(repo_map_obj: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in repo_map_obj.get("repositories", []):
        repo = str(row.get("repo", ""))
        name = repo.split("/", 1)[-1] if repo else ""
        if name:
            out[name] = str(row.get("visibility", "unknown"))
    return out


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def choose_role(delta: dict[str, Any]) -> str:
    mutation = str(delta.get("mutation_class", ""))
    epistemic = str(delta.get("epistemic_class", ""))
    targets = list(delta.get("target_surfaces") or [])
    if mutation == "OBSERVE":
        return "OBSERVER"
    if mutation == "REVIEW_CHALLENGE":
        return "CHALLENGER"
    if mutation == "EFFECT_GATED":
        return "VERIFIER"
    if epistemic in {"HYPOTHESIS", "PREDICTED", "COUNTERFACTUAL", "UNKNOWN"}:
        return "RESEARCH_DONOR"
    if len(targets) > 1:
        return "PROJECTION_COMPILER"
    return "WORKER"


def validate_delta(delta: dict[str, Any], lanes: dict[str, dict[str, Any]], vis: dict[str, str]) -> list[str]:
    required = [
        "delta_id", "session_id", "observed_at", "domain", "subject", "relation",
        "epistemic_class", "source_refs", "target_surfaces", "mutation_class",
        "authority_ceiling", "confidentiality", "next_receiver"
    ]
    issues = [f"MISSING_{x}" for x in required if x not in delta or delta.get(x) in (None, "")]
    domains = list(delta.get("domain") or [])
    issues.extend(f"UNKNOWN_DOMAIN:{d}" for d in domains if str(d) not in lanes)

    confidentiality = str(delta.get("confidentiality", "UNKNOWN"))
    if confidentiality in {"PRIVATE", "RESTRICTED", "UNKNOWN"}:
        for target in list(delta.get("target_surfaces") or []):
            name = str(target).split("/", 1)[-1]
            if vis.get(name) == "public":
                issues.append(f"CONFIDENTIALITY_PUBLIC_TARGET_COLLISION:{name}")
    return issues


def compile_plan(deltas: list[dict[str, Any]], lanes_obj: dict[str, Any], repo_map_obj: dict[str, Any]) -> dict[str, Any]:
    lanes = lane_map(lanes_obj)
    vis = repo_visibility_map(repo_map_obj)

    groups: dict[str, list[dict[str, Any]]] = {}
    collision_groups: dict[str, list[str]] = {}
    validation: dict[str, list[str]] = {}

    for delta in deltas:
        did = str(delta.get("delta_id", ""))
        issues = validate_delta(delta, lanes, vis)
        validation[did] = issues

        dedupe_basis = {
            "domain": sorted(str(x) for x in list(delta.get("domain") or [])),
            "subject": normalize_text(delta.get("subject")),
            "relation": normalize_text(delta.get("relation")),
            "targets": sorted(str(x) for x in list(delta.get("target_surfaces") or [])),
            "confidentiality": str(delta.get("confidentiality", "UNKNOWN")),
        }
        dedupe_key = stable_hash(dedupe_basis)
        groups.setdefault(dedupe_key, []).append(delta)

        collision_basis = {
            "domain": dedupe_basis["domain"],
            "subject": dedupe_basis["subject"],
            "targets": dedupe_basis["targets"],
        }
        collision_key = stable_hash(collision_basis)[:24]
        collision_groups.setdefault(collision_key, []).append(did)

    contracts: list[dict[str, Any]] = []
    donations: list[dict[str, Any]] = []

    for dedupe_key in sorted(groups):
        group = sorted(groups[dedupe_key], key=lambda x: (str(x.get("observed_at", "")), str(x.get("delta_id", ""))))
        primary = group[0]
        primary_id = str(primary["delta_id"])
        all_issues = sorted({issue for item in group for issue in validation[str(item.get("delta_id", ""))]})

        collision_basis = {
            "domain": sorted(str(x) for x in list(primary.get("domain") or [])),
            "subject": normalize_text(primary.get("subject")),
            "targets": sorted(str(x) for x in list(primary.get("target_surfaces") or [])),
        }
        collision_domain = "coevo:" + stable_hash(collision_basis)[:24]
        role = choose_role(primary)
        blocked = bool(all_issues) or str(primary.get("mutation_class")) == "EFFECT_GATED"

        input_bindings = []
        for item in group:
            input_bindings.extend(str(x) for x in list(item.get("source_refs") or []))
        input_bindings = sorted(set(input_bindings))

        contract = {
            "spawn_id": "cospawn:" + stable_hash({"primary": primary_id, "dedupe": dedupe_key})[:24],
            "purpose": f"Process bounded CoEvoDelta group led by {primary_id}",
            "parent_identity": str(primary.get("session_id")),
            "role": role,
            "scope": f"domains={','.join(str(x) for x in list(primary.get('domain') or []))}; subject={primary.get('subject')}",
            "input_bindings": input_bindings,
            "authority_ceiling": str(primary.get("authority_ceiling")),
            "effect_classes": [str(primary.get("mutation_class"))],
            "budget": {"max_live_embodiments": 0, "max_effectful_mutations": 0, "logical_work_units": 1},
            "lease": {"mode": "LOGICAL_ONLY", "effect_lease": "NONE"},
            "idempotency_key": "dedupe:" + dedupe_key,
            "collision_domain": collision_domain,
            "receiver": str(primary.get("next_receiver")),
            "success_condition": "RECEIVER_DISPOSITION_AND_EVIDENCE_RECORDED",
            "stop_condition": "AUTHORITY_CONFIDENTIALITY_OR_COLLISION_AMBIGUITY",
            "checkpoint": None,
            "recovery_pointer": primary_id,
            "failure_domain": None,
            "handoff_rule": "DONATE_EQUIVALENT_DELTAS_TO_PRIMARY_AND_PRESERVE_SOURCE_REFS",
            "retirement_condition": "PRIMARY_DELTA_DISPOSITION_RECORDED_AND_DONATED_EQUIVALENTS_BOUND",
            "provenance": [str(x.get("delta_id")) for x in group],
            "currentness": str(primary.get("observed_at")),
            "uncertainty": ";".join(all_issues) if all_issues else None,
            "materialization_state": "BLOCKED" if blocked else "LOGICAL_ONLY",
        }
        contracts.append(contract)

        for duplicate in group[1:]:
            donations.append({
                "donor_delta_id": str(duplicate.get("delta_id")),
                "receiver_delta_id": primary_id,
                "relation": "EQUIVALENT_DEDUPE_DONATION",
                "dedupe_key": dedupe_key,
                "nonclaims": ["DONATION_NE_SEMANTIC_IDENTITY_TOTALITY", "DEDUPE_NE_DELETE"]
            })

    collisions = []
    for key, ids in sorted(collision_groups.items()):
        unique_ids = sorted(set(ids))
        if len(unique_ids) > 1:
            collisions.append({
                "collision_domain": "coevo:" + key,
                "delta_ids": unique_ids,
                "state": "SERIAL_REVIEW_REQUIRED_IF_RELATIONS_DIFFER_OR_EFFECTS_COLLIDE"
            })

    return {
        "schema": "CoLogicalSpawnPlanner.R2.v0.1-candidate",
        "state": "LOGICAL_SPAWN_PLAN_COMPILED__NO_LIVE_MATERIALIZATION",
        "coverage": {
            "input_deltas": len(deltas),
            "logical_contracts": len(contracts),
            "dedupe_donations": len(donations),
            "collision_groups": len(collisions),
        },
        "contracts": contracts,
        "donations": donations,
        "collisions": collisions,
        "validation": validation,
        "effects": {
            "live_workers_started": 0,
            "provider_sessions_created": 0,
            "provider_titles_mutated": 0,
            "provider_tabs_closed": 0,
            "repo_mutations_executed": 0,
            "authority_changes": 0,
        },
        "next": "R3_LOCAL_OLLAMA_MATERIALIZATION_CANARY_FOR_ONE_UNBLOCKED_LOW_EFFECT_CONTRACT",
        "nonclaims": [
            "SPAWN_NE_NEW_CHAT",
            "LOGICAL_RESERVE_NE_LIVE_WORKER",
            "DEDUPE_NE_DELETE",
            "MODEL_NE_AUTHORITY",
            "GITHUB_WRITE_ACCESS_NE_GLOBAL_AUTHORITY",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deltas", required=True)
    ap.add_argument("--lanes", required=True)
    ap.add_argument("--repo-map", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    plan = compile_plan(
        as_deltas(load_json(Path(args.deltas))),
        load_json(Path(args.lanes)),
        load_json(Path(args.repo_map)),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(plan, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE": plan["state"],
        "OUTPUT": str(out),
        "OUTPUT_SHA256": hashlib.sha256(encoded).hexdigest().upper(),
        "INPUT_DELTAS": plan["coverage"]["input_deltas"],
        "LOGICAL_CONTRACTS": plan["coverage"]["logical_contracts"],
        "DONATIONS": plan["coverage"]["dedupe_donations"],
        "COLLISION_GROUPS": plan["coverage"]["collision_groups"],
        "LIVE_WORKERS_STARTED": 0,
        "NEXT": plan["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
