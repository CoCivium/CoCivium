#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HOT = {"ACTIVE","WORKING","CHALLENGING","REAWAKENED","RECOVERY","DEGRADED"}
WARM = {"BOOTSTRAPPING","WAITING","COTWILIGHT","EXTERNALIZING","SUCCESSOR_READY"}
DORMANT = {"QUIESCENT","DORMANT"}
ARCHIVE = {"CLOSE_SAFE"}
COMPOST = {"SUPERSEDED"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected object: {path}")
    return obj


def count_block(count: int | None, coverage: str) -> dict[str, Any]:
    return {"count": count, "coverage": coverage}


def classify_temperature(projection: str) -> str:
    p = projection.upper()
    if p in HOT:
        return "HOT"
    if p in WARM:
        return "WARM"
    if p in DORMANT:
        return "DORMANT"
    if p in ARCHIVE:
        return "ARCHIVE"
    if p in COMPOST:
        return "COMPOST"
    return "COOL"


def front_count(front_registry: dict[str, Any] | None) -> tuple[int | None, str]:
    if not front_registry:
        return None, "NO_FRONT_REGISTRY_INPUT"
    fronts = front_registry.get("fronts")
    if not isinstance(fronts, list):
        return None, "FRONT_REGISTRY_UNREADABLE"
    return len(fronts), "BOUND_FRONT_REGISTRY"


def runtime_count(runtime: dict[str, Any] | None, key: str) -> tuple[int | None, str]:
    if not runtime:
        return None, "NO_RUNTIME_FACTS_INPUT"
    value = runtime.get(key)
    if isinstance(value, int) and value >= 0:
        return value, "BOUND_RUNTIME_FACT"
    return None, "RUNTIME_FACT_UNPROVEN"


def compile_projection(
    ledger: dict[str, Any] | None,
    spawn: dict[str, Any] | None,
    fronts: dict[str, Any] | None,
    runtime: dict[str, Any] | None,
    observed_at: str,
) -> dict[str, Any]:
    sessions = list((ledger or {}).get("sessions") or [])
    contracts = list((spawn or {}).get("contracts") or [])
    evidence_refs: list[str] = []

    if ledger:
        cov = ledger.get("coverage") or {}
        if cov.get("source_sha256"):
            evidence_refs.append("shadow-ledger-source:" + str(cov["source_sha256"]))
    if spawn:
        evidence_refs.append("logical-spawn-plan:" + sha256(
            json.dumps(spawn, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
        ))

    temperatures = {k:0 for k in ("HOT","WARM","COOL","DORMANT","COMPOST","ARCHIVE")}
    degraded = 0
    for s in sessions:
        projection = str(s.get("projection") or "UNORIENTED")
        t = classify_temperature(projection)
        temperatures[t] += 1
        if projection in {"DEGRADED","RECOVERY"}:
            degraded += 1

    blocked = [c for c in contracts if c.get("materialization_state") == "BLOCKED"]
    logical_only = [c for c in contracts if c.get("materialization_state") == "LOGICAL_ONLY"]
    active_effect_leases = [
        c for c in contracts
        if str((c.get("lease") or {}).get("effect_lease","NONE")).upper() not in {"","NONE"}
    ]

    exceptions: list[dict[str, Any]] = []
    for c in blocked:
        exceptions.append({
            "exception_class":"LOGICAL_CONTRACT_BLOCKED",
            "subject":c.get("scope"),
            "reason":c.get("uncertainty") or c.get("stop_condition") or "UNSPECIFIED",
            "spawn_id":c.get("spawn_id"),
            "human_action_required":"UNPROVEN"
        })
    for s in sessions:
        if str(s.get("projection")) in {"DEGRADED","RECOVERY"}:
            exceptions.append({
                "exception_class":"SESSION_DEGRADED_OR_RECOVERY",
                "subject":s.get("session_id"),
                "reason":s.get("projection_basis"),
                "human_action_required":"UNPROVEN"
            })

    # Human blockers are intentionally not inferred from generic blocked work.
    human_blockers = list((runtime or {}).get("human_blockers") or []) if runtime else []

    workspaces_count, workspaces_cov = runtime_count(runtime, "workspaces")
    workers_count, workers_cov = runtime_count(runtime, "materialized_workers")
    providers_count, providers_cov = runtime_count(runtime, "provider_sessions")
    models_count, models_cov = runtime_count(runtime, "model_runtimes")
    front_n, front_cov = front_count(fronts)

    if runtime and isinstance(runtime.get("effect_leases"), int):
        lease_count = runtime["effect_leases"]
        lease_cov = "BOUND_RUNTIME_FACT"
    else:
        lease_count = len(active_effect_leases)
        lease_cov = "LOGICAL_CONTRACTS_ONLY__LIVE_RUNTIME_UNPROVEN"

    currentness = {"state":"UNKNOWN","age_seconds":None}
    if runtime and isinstance(runtime.get("currentness"), dict):
        rc = runtime["currentness"]
        state = str(rc.get("state","UNKNOWN")).upper()
        if state in {"HEALTHY","AGING","STALE","DEGRADED","UNKNOWN"}:
            currentness = {
                "state":state,
                "age_seconds":rc.get("age_seconds")
            }

    dimensions = {
        "bounded_session_count":len(sessions),
        "logical_contract_count":len(contracts),
        "logical_only_contracts":len(logical_only),
        "blocked_contracts":len(blocked),
        "degraded_or_recovery_sessions":degraded,
        "human_blockers":len(human_blockers),
        "effect_leases_observed_or_inferred":lease_count,
    }
    if not sessions and not contracts:
        headline = "UNKNOWN"
    elif degraded > 0:
        headline = "DEGRADED"
    elif blocked or human_blockers:
        headline = "HIGH"
    elif len(logical_only) > 0:
        headline = "MODERATE"
    else:
        headline = "LOW"

    source_count = int(bool(ledger)) + int(bool(spawn)) + int(bool(fronts)) + int(bool(runtime))
    coverage_state = "BOUNDED_INPUTS_ONLY"
    global_census = "UNPROVEN"

    projection_basis = {
        "sessions_from_shadow_ledger":len(sessions),
        "logical_contracts_from_spawn_plan":len(contracts),
        "front_registry_bound":fronts is not None,
        "runtime_facts_bound":runtime is not None,
    }

    return {
        "projection_id":"cofleet:" + sha256(
            json.dumps({"observed_at":observed_at,"basis":projection_basis},
                       sort_keys=True,separators=(",",":")).encode("utf-8")
        )[:24],
        "observed_at":observed_at,
        "observer":"CoFleetProjectionCompiler.R4A.v0.1",
        "coverage":{
            "state":coverage_state,
            "global_fleet_census":global_census,
            "source_count":source_count,
            "basis":projection_basis,
        },
        "workspaces":count_block(workspaces_count,workspaces_cov),
        "virtual_sessions":{
            "count":len(sessions),
            "coverage":"BOUND_SHADOW_LEDGER__NOT_GLOBAL_SESSION_CENSUS" if ledger else "NO_LEDGER_INPUT",
            "temperatures":temperatures,
        },
        "materialized_workers":count_block(workers_count,workers_cov),
        "provider_sessions":count_block(providers_count,providers_cov),
        "model_runtimes":count_block(models_count,models_cov),
        "fronts":count_block(front_n,front_cov),
        "effect_leases":count_block(lease_count,lease_cov),
        "currentness":currentness,
        "pressure":{"headline":headline,"dimensions":dimensions},
        "human_blockers":human_blockers,
        "exceptions":exceptions,
        "evidence_refs":evidence_refs,
        "nonclaims":[
            "FLEET_PROJECTION_NE_FLEET_TOTALITY",
            "COUNT_NE_GLOBAL_CENSUS",
            "LOGICAL_CONTRACT_NE_LIVE_WORKER",
            "EXCEPTION_NE_HUMAN_BLOCKER",
            "NO_PROVIDER_SESSION_DISCOVERY_WITHOUT_RUNTIME_FACT",
            "NO_RICKBAR_RUNTIME_BINDING_INFERRED",
        ],
    }


def selftest() -> int:
    ledger = {
        "coverage":{"source_sha256":"A"*64},
        "sessions":[
            {"session_id":"A","projection":"WORKING"},
            {"session_id":"B","projection":"DORMANT"},
            {"session_id":"C","projection":"CLOSE_SAFE"},
        ]
    }
    spawn = {
        "contracts":[
            {"spawn_id":"1","materialization_state":"LOGICAL_ONLY","lease":{"effect_lease":"NONE"}},
            {"spawn_id":"2","materialization_state":"BLOCKED","lease":{"effect_lease":"NONE"},"uncertainty":"CONFIDENTIALITY_PUBLIC_TARGET_COLLISION"},
        ]
    }
    p = compile_projection(ledger,spawn,None,None,"2026-09-23T11:36:00Z")
    assert p["virtual_sessions"]["count"] == 3
    assert p["virtual_sessions"]["temperatures"]["HOT"] == 1
    assert p["virtual_sessions"]["temperatures"]["DORMANT"] == 1
    assert p["virtual_sessions"]["temperatures"]["ARCHIVE"] == 1
    assert p["pressure"]["headline"] == "HIGH"
    assert p["human_blockers"] == []
    assert p["provider_sessions"]["count"] is None
    assert p["coverage"]["global_fleet_census"] == "UNPROVEN"
    print("SELFTEST=PASS_BOUNDED_COUNTS__BLOCKED_NE_HUMAN_BLOCKER__NO_GLOBAL_CENSUS__NO_PROVIDER_INFERENCE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ledger")
    ap.add_argument("--spawn-plan")
    ap.add_argument("--front-registry")
    ap.add_argument("--runtime-facts")
    ap.add_argument("--observed-at")
    ap.add_argument("--output")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.observed_at or not args.output:
        raise SystemExit("FAIL_CLOSED__OBSERVED_AT_AND_OUTPUT_REQUIRED")

    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    projection = compile_projection(
        load(args.ledger),
        load(args.spawn_plan),
        load(args.front_registry),
        load(args.runtime_facts),
        args.observed_at,
    )
    out.parent.mkdir(parents=True,exist_ok=True)
    encoded=(json.dumps(projection,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":"PASS_R4A_COFLEET_PROJECTION_COMPILED__BOUNDED_INPUTS_ONLY",
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256(encoded),
        "VIRTUAL_SESSIONS":projection["virtual_sessions"]["count"],
        "EXCEPTIONS":len(projection["exceptions"]),
        "HUMAN_BLOCKERS":len(projection["human_blockers"]),
        "GLOBAL_FLEET_CENSUS":projection["coverage"]["global_fleet_census"],
        "NEXT":"R4B_RICKBAR_RECEIVER_BINDING_AFTER_PROVEN_RUNTIME_ADAPTER"
    },separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
