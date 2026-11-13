#!/usr/bin/env python3
"""CoAll CoResourceFrontier R0: deterministic, side-effect-free shadow allocation.

Only caller-declared metadata and synthetic examples. No resources are probed,
started, licensed, spent, harvested, or remotely accessed. No infinite recursion.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from typing import Any

SCHEMA = "CoAll.CoResourceFrontier.ShadowAllocation.R0"
PRIVACY = ("PUBLIC", "PRIVATE_LOCAL")
RESOURCE_STATES = ("ONLINE_DECLARED", "OFFLINE_DECLARED", "UNKNOWN")
RESOURCE_HEALTH = ("HEALTHY_DECLARED", "DEGRADED_DECLARED", "UNKNOWN")
RESOURCE_TYPES = ("CPU", "GPU", "MODEL", "DEVICE", "HUMAN", "CACHE", "OTHER")
RESOURCE_BASIS = ("SYNTHETIC", "INSTRUMENT_REPORTED", "DECLARED_UNVERIFIED")
WORK_CLASSES = ("RECOVERY", "USER_VALUE", "MAINTENANCE", "RESEARCH", "EXPERIMENT")
METRICS = ("cpu_ms", "energy_mwh", "attention_s", "cost_cents")
MAX_BODY = 256 * 1024
MAX_IDS = 96


def positive_int(value: Any, name: str, minimum: int = 0, maximum: int = 10**8) -> int:
    if type(value) is not int or value < minimum or value > maximum:
        raise ValueError("INVALID_" + name.upper())
    return value


def ident(value: Any, name: str) -> str:
    if not isinstance(value, str) or not (1 <= len(value) <= MAX_IDS):
        raise ValueError("INVALID_" + name.upper())
    if not all(ch.isascii() and (ch.isalnum() or ch in "_-:.") for ch in value):
        raise ValueError("INVALID_" + name.upper())
    return value


def choice(value: Any, values: tuple, name: str) -> str:
    if value not in values or not isinstance(value, str):
        raise ValueError("INVALID_" + name.upper())
    return value


def mapping(value: Any, name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError("INVALID_" + name.upper())
    return value


def timestamp(raw: Any) -> dt.datetime:
    if not isinstance(raw, str) or len(raw) > 40:
        raise ValueError("INVALID_TIMESTAMP")
    try:
        parsed = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("INVALID_TIMESTAMP")
    return parsed.astimezone(dt.timezone.utc)


def cost_values(obj: Any, *, allow_unknown: bool) -> dict[str, int | None]:
    m = mapping(obj, "METRICS")
    if set(m) != set(METRICS):
        raise ValueError("INVALID_METRIC_FIELDS")
    return {
        key: (None if allow_unknown and m[key] is None else positive_int(m[key], key))
        for key in METRICS
    }


def _validate(raw: Any) -> dict:
    root = mapping(raw, "ROOT")
    if root.get("schema") != SCHEMA:
        raise ValueError("INVALID_SCHEMA")
    as_of = timestamp(root.get("as_of"))
    work_id = ident(root.get("work_id"), "WORK_ID")
    output_privacy = choice(root.get("output_privacy"), PRIVACY, "OUTPUT_PRIVACY")
    policy = mapping(root.get("policy"), "POLICY")
    slots = positive_int(policy.get("max_selected"), "MAX_SELECTED", 1, 8)
    per_resource = positive_int(policy.get("per_resource_max"), "PER_RESOURCE_MAX", 1, 8)
    per_domain = positive_int(policy.get("per_domain_max"), "PER_DOMAIN_MAX", 1, 8)
    reserve = positive_int(policy.get("reserve_percent"), "RESERVE_PERCENT", 0, 95)
    max_age = positive_int(policy.get("max_observation_age_s"), "OBSERVATION_AGE", 1, 604800)
    total = cost_values(policy.get("total_budget"), allow_unknown=False)
    raw_protected = policy.get("protected_ids")
    if not isinstance(raw_protected, list) or len(raw_protected) > 32:
        raise ValueError("INVALID_PROTECTED_IDS")
    protected = {ident(z, "PROTECTED_ID") for z in raw_protected}
    if len(protected) != len(raw_protected):
        raise ValueError("DUPLICATE_PROTECTED_ID")
    resources = root.get("resources")
    tasks = root.get("tasks")
    if not isinstance(resources, list) or len(resources) > 32:
        raise ValueError("INVALID_RESOURCE_COUNT")
    if not isinstance(tasks, list) or len(tasks) > 64:
        raise ValueError("INVALID_TASK_COUNT")
    resources_out, tasks_out, seen = [], [], set()
    for res in resources:
        r = mapping(res, "RESOURCE")
        rid = ident(r.get("id"), "RESOURCE_ID")
        if rid in seen:
            raise ValueError("DUPLICATE_RESOURCE_ID")
        seen.add(rid)
        kind = choice(r.get("type"), RESOURCE_TYPES, "RESOURCE_TYPE")
        state = choice(r.get("state"), RESOURCE_STATES, "RESOURCE_STATE")
        health = choice(r.get("health"), RESOURCE_HEALTH, "RESOURCE_HEALTH")
        basis = choice(r.get("basis"), RESOURCE_BASIS, "RESOURCE_BASIS")
        location = choice(r.get("location"), ("LOCAL", "REMOTE"), "RESOURCE_LOCATION")
        privacy = choice(r.get("privacy"), PRIVACY, "RESOURCE_PRIVACY")
        domain = ident(r.get("failure_domain"), "FAILURE_DOMAIN")
        caps = r.get("capabilities")
        if not isinstance(caps, list) or len(caps) > 16:
            raise ValueError("INVALID_CAPABILITIES")
        cs = {ident(c, "CAPABILITY") for c in caps}
        if len(cs) != len(caps):
            raise ValueError("DUPLICATE_CAPABILITY")
        last_seen = timestamp(r.get("observed_at"))
        if last_seen > as_of:
            raise ValueError("OBSERVATION_IN_FUTURE")
        budget = cost_values(r.get("available"), allow_unknown=True)
        ram = r.get("memory_mib")
        if ram is not None:
            ram = positive_int(ram, "MEMORY_MIB")
        resources_out.append({"id": rid, "type": kind, "state": state, "health": health,
                              "basis": basis, "location": location, "privacy": privacy,
                              "failure_domain": domain, "capabilities": cs,
                              "age_s": int((as_of - last_seen).total_seconds()),
                              "available": budget, "memory_mib": ram})
    seen = set()
    for task in tasks:
        t = mapping(task, "TASK")
        tid = ident(t.get("id"), "TASK_ID")
        if tid in seen:
            raise ValueError("DUPLICATE_TASK_ID")
        seen.add(tid)
        capability = ident(t.get("capability"), "TASK_CAPABILITY")
        kind = choice(t.get("kind"), ("WORK", "UNVERIFIED_ENERGY", "SYMBOLIC", "UNKNOWN"), "TASK_KIND")
        work_class = choice(t.get("work_class"), WORK_CLASSES, "WORK_CLASS")
        privacy = choice(t.get("privacy"), PRIVACY, "TASK_PRIVACY")
        effects = choice(t.get("effect_class"),
                         ("NONE", "DEVICE_MUTATION", "EXTERNAL_SEND", "FINANCIAL", "SECURITY_SENSITIVE"),
                         "EFFECT_CLASS")
        estimated = cost_values(t.get("estimated"), allow_unknown=True)
        memory = t.get("memory_mib")
        if memory is not None:
            memory = positive_int(memory, "MEMORY_MIB")
        value = mapping(t.get("benefit"), "BENEFIT")
        if set(value) != {"receiver", "information", "recovery", "challenge"}:
            raise ValueError("INVALID_BENEFIT_FIELDS")
        benefits = {k: positive_int(v, "BENEFIT_" + k, 0, 10) for k, v in value.items()}
        tasks_out.append({"id": tid, "capability": capability, "kind": kind,
                          "work_class": work_class, "privacy": privacy,
                          "effect_class": effects, "estimated": estimated,
                          "memory_mib": memory, "benefit": benefits})
    if output_privacy == "PUBLIC" and any(x["privacy"] == "PRIVATE_LOCAL" for x in tasks_out):
        raise ValueError("HELD_PRIVATE_TASK_IN_PUBLIC_OUTPUT")
    if output_privacy == "PUBLIC" and any(x["privacy"] == "PRIVATE_LOCAL" for x in resources_out):
        raise ValueError("HELD_PRIVATE_RESOURCE_IN_PUBLIC_OUTPUT")
    return {"work_id": work_id, "output_privacy": output_privacy,
            "as_of": as_of.isoformat(), "policy": {"max_selected": slots,
            "per_resource_max": per_resource, "per_domain_max": per_domain,
            "reserve_percent": reserve, "max_observation_age_s": max_age,
            "protected_ids": protected, "total_budget": total},
            "resources": resources_out, "tasks": tasks_out}


def _resource_eligibility(task: dict, res: dict, policy: dict) -> str | None:
    if res["id"] in policy["protected_ids"]:
        return "OPERATOR_PROTECTED_RESOURCE"
    if res["state"] != "ONLINE_DECLARED":
        return "RESOURCE_NOT_ONLINE"
    if res["health"] != "HEALTHY_DECLARED":
        return "RESOURCE_DEGRADED_OR_UNKNOWN"
    if res["age_s"] > policy["max_observation_age_s"]:
        return "STALE_RESOURCE_OBSERVATION"
    if res["basis"] == "DECLARED_UNVERIFIED":
        return "UNVERIFIED_CAPACITY"
    if task["capability"] not in res["capabilities"]:
        return "NO_COMPATIBLE_CAPABILITY"
    if task["privacy"] == "PRIVATE_LOCAL" and (res["location"] != "LOCAL" or res["privacy"] != "PRIVATE_LOCAL"):
        return "PRIVACY_LOCALITY_HOLD"
    if task["memory_mib"] is None or res["memory_mib"] is None:
        return "UNKNOWN_MEMORY_PRESSURE"
    if task["memory_mib"] > (res["memory_mib"] * (100 - policy["reserve_percent"])) // 100:
        return "INSUFFICIENT_MEMORY_HEADROOM"
    for key in METRICS:
        if res["available"][key] is None:
            return "UNKNOWN_RESOURCE_CAPACITY"
        if task["estimated"][key] > (res["available"][key] * (100 - policy["reserve_percent"])) // 100:
            return "INSUFFICIENT_RESOURCE_HEADROOM"
    return None


def _preflight(t: dict) -> str | None:
    if t["kind"] != "WORK":
        return "SPECULATIVE_OR_SYMBOLIC_NOT_EXECUTABLE_RESOURCE"
    if t["effect_class"] != "NONE":
        return "CONSEQUENTIAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY"
    if t["memory_mib"] is None or any(t["estimated"][key] is None for key in METRICS):
        return "UNKNOWN_ESTIMATED_COST"
    return None


def _rank(t: dict, r: dict) -> tuple:
    priority = {"RECOVERY": 5, "USER_VALUE": 4, "MAINTENANCE": 3,
                "RESEARCH": 2, "EXPERIMENT": 1}[t["work_class"]]
    v = t["benefit"]
    benefit = 4*v["receiver"] + 3*v["recovery"] + 2*v["information"] + 2*v["challenge"]
    cost = t["estimated"]
    expense = (math.ceil(cost["cpu_ms"]/1000) + math.ceil(cost["energy_mwh"]/100)
               + math.ceil(cost["attention_s"]/15) + cost["cost_cents"])
    # Explicit illustrative lexicographic ranking; NOT a measured optimizer.
    return priority, benefit - expense, -expense, r["id"]


def plan(raw: Any) -> dict:
    """Return one deterministic, authority-free proposal. Never probe or mutate a device."""
    obj = _validate(raw)
    p = obj["policy"]
    resources, tasks = obj["resources"], obj["tasks"]
    held, edges, selected = {}, {}, []
    for t in tasks:
        rejection = _preflight(t)
        if rejection:
            held[t["id"]] = rejection
            continue
        compatible = []
        for r in resources:
            reason = _resource_eligibility(t, r, p)
            if reason is None:
                compatible.append(r)
        if not compatible:
            # Do not expose private source content; all public fixture IDs are synthetic.
            held[t["id"]] = "NO_CURRENT_ELIGIBLE_RESOURCE"
        else:
            edges[t["id"]] = compatible
    remaining = dict(p["total_budget"])
    resource_remaining = {r["id"]: {key: (None if r["available"][key] is None else
                            (r["available"][key]*(100-p["reserve_percent"])) // 100)
                         for key in METRICS} for r in resources}
    memory_remaining = {r["id"]: None if r["memory_mib"] is None else
                        (r["memory_mib"] * (100-p["reserve_percent"])) // 100
                        for r in resources}
    used_resource = {r["id"]: 0 for r in resources}
    used_domain = {r["failure_domain"]: 0 for r in resources}
    used_tasks = set()
    pairs = [(t, r) for t in tasks for r in edges.get(t["id"], [])]
    pairs.sort(key=lambda z: (-_rank(z[0],z[1])[0], -_rank(z[0],z[1])[1],
                              -_rank(z[0],z[1])[2], z[0]["id"], z[1]["id"]))
    for t,r in pairs:
        if len(selected) >= p["max_selected"]:
            break
        tid, rid, domain = t["id"],r["id"],r["failure_domain"]
        if tid in used_tasks:
            continue
        if used_resource[rid] >= p["per_resource_max"] or used_domain[domain] >= p["per_domain_max"]:
            continue
        cost = t["estimated"]
        if t["memory_mib"] > memory_remaining[rid]:
            continue
        if any(cost[k] > remaining[k] or cost[k] > resource_remaining[rid][k] for k in METRICS):
            continue
        for k in METRICS:
            remaining[k] -= cost[k]
            resource_remaining[rid][k] -= cost[k]
        memory_remaining[rid] -= t["memory_mib"]
        used_resource[rid] += 1
        used_domain[domain] += 1
        used_tasks.add(tid)
        selected.append({"task_id":tid,"resource_id":rid,"failure_domain":domain,
                         "estimated_consumption": dict(cost),"memory_mib_reserved":t["memory_mib"],"class":t["work_class"],
                         "status":"SHADOW_PROPOSAL_ONLY","authority":"NONE"})
    for t in tasks:
        if t["id"] not in used_tasks and t["id"] not in held:
            held[t["id"]] = "BUDGET_OR_COLLISION_BACKPRESSURE"
    state = "SHADOW_PROPOSALS_WITH_HELD" if selected and held else (
        "SHADOW_PROPOSALS" if selected else "HELD_NO_ELIGIBLE_WORK")
    return {
        "schema": SCHEMA,"state": state,"work_id": obj["work_id"],
        "output_privacy":obj["output_privacy"],"as_of":obj["as_of"],
        "selected": selected,
        "held": [{"task_id":k,"reason":v} for k,v in sorted(held.items())],
        "remaining_global_budget": remaining,
        "resource_count": len(resources),"task_count": len(tasks),
        "effect_totals": {"device":0,"network":0,"model":0,"send":0,"files":0,"workers":0,"energy_harvested_mwh":0},
        "authority":"NONE","receiver_ack":False,
        "source_evidence":"CALLER_DECLARED_NOT_INDEPENDENTLY_VERIFIED",
        "optimization":"ILLUSTRATIVE_LEXICOGRAPHIC_PRIORITY_NOT_REAL_MEASURED_OPTIMUM",
        "nonclaims":["PLANNED_NE_EXECUTED","DECLARED_ONLINE_NE_CONNECTED",
                     "REPORTED_CAPACITY_NE_PHYSICAL_ENERGY_CREATION",
                     "HYPOTHESIS_NE_POWER_SOURCE","METADATA_NE_REAL_PROCESS_INSPECTION",
                     "ACTIVE_SELECTION_NE_ALWAYS_RUNNING"]}


def main():
    try:
        body = sys.stdin.buffer.read(MAX_BODY + 1)
        if len(body)>MAX_BODY:
            raise ValueError("INPUT_TOO_LARGE")
        raw = json.loads(body)
        print(json.dumps(plan(raw),ensure_ascii=False,separators=(",", ":"),sort_keys=True))
    except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as e:
        # Never echo untrusted resource labels/secret input.
        code=str(e)
        if not (code.startswith("INVALID_") or code in ("INPUT_TOO_LARGE","OBSERVATION_IN_FUTURE","DUPLICATE_RESOURCE_ID","DUPLICATE_TASK_ID","DUPLICATE_CAPABILITY","DUPLICATE_PROTECTED_ID",
                         "HELD_PRIVATE_TASK_IN_PUBLIC_OUTPUT", "HELD_PRIVATE_RESOURCE_IN_PUBLIC_OUTPUT")):
            code="INVALID_INPUT"
        print("HELD_"+code,file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
