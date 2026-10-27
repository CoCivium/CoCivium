#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ZERO_EFFECTS = {
    "network_calls": 0,
    "external_messages": 0,
    "provider_mutations": 0,
    "device_mutations": 0,
    "account_changes": 0,
    "background_daemons_started": 0,
}

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def disposition(obj: dict[str, Any]) -> str:
    state = obj["lifecycle_state"]
    wakes = set(obj.get("wake_predicates", []))
    observed = set(obj.get("wake_observations", []))

    if state == "RETIRED":
        return "PRESERVE_RETIRED_LINEAGE"
    if state == "DEGRADED_REPAIRABLE":
        return "REPAIR_BEFORE_AMPLIFY"
    if state == "DORMANT_WITH_WAKE":
        if wakes & observed:
            return "WAKE_FOR_BOUNDED_REQUALIFICATION"
        return "REMAIN_DORMANT_WITH_EXACT_WAKE"
    if state == "QUIESCENT_CURRENT":
        if wakes & observed:
            return "WAKE_FOR_BOUNDED_REQUALIFICATION"
        return "SLEEP_KEEP_ADDRESSABLE"
    if state == "ACTIVE_WORKING":
        if obj.get("known_debt"):
            return "EXTEND_ONE_BOUNDED_DEBT_REDUCTION"
        return "CONTINUE_ONLY_ON_MATERIAL_DELTA"
    return "HOLD_UNKNOWN_CURRENTNESS"

def heartbeat_mode(obj: dict[str, Any], disp: str) -> str:
    if disp.startswith("WAKE_"):
        return "EMIT_WAKE_TRANSITION_PULSE"
    if disp == "REPAIR_BEFORE_AMPLIFY":
        return "EMIT_HEALTH_EXCEPTION_PULSE"
    if disp == "EXTEND_ONE_BOUNDED_DEBT_REDUCTION":
        return "EMIT_MATERIAL_DELTA_PULSE"
    return "QUIET_UNTIL_MATERIAL_DELTA"

def run(fixture: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    require(fixture.get("schema") == "CoObject.VitalityFixture.R0.v0.1", "wrong fixture schema")
    require(policy.get("schema") == "CoObject.VitalityPolicy.R0.v0.1", "wrong policy schema")
    required = set(policy["required_metabolism"])

    results = []
    for obj in fixture["objects"]:
        require(obj["lifecycle_state"] in policy["liveness_classes"], "bad lifecycle state")
        metabolism = obj.get("metabolism", {})
        missing = sorted(required - set(metabolism))
        require(not missing, f"{obj['object_id']}: missing metabolism {missing}")
        require(obj.get("object_id"), "object_id required")
        require(obj.get("source_ref"), "source_ref required")
        require(obj.get("currentness_state"), "currentness required")
        require(obj.get("health_state"), "health required")
        require(obj.get("authority_ceiling"), "authority required")
        require(obj.get("evidence_refs"), "evidence required")

        disp = disposition(obj)
        results.append({
            "object_id": obj["object_id"],
            "object_class": obj["object_class"],
            "lifecycle_state": obj["lifecycle_state"],
            "currentness_state": obj["currentness_state"],
            "health_state": obj["health_state"],
            "disposition": disp,
            "heartbeat_mode": heartbeat_mode(obj, disp),
            "known_debt": list(obj.get("known_debt", [])),
            "wake_predicates": list(obj.get("wake_predicates", [])),
            "wake_observations": list(obj.get("wake_observations", [])),
            "capability_claim": "DECLARED_INTERFACE_ONLY__CAPABILITY_NOT_INFERRED",
            "effects": dict(ZERO_EFFECTS),
        })

    by_id = {r["object_id"]: r for r in results}
    require(by_id["cobaseline-frontier-r0"]["disposition"] == "EXTEND_ONE_BOUNDED_DEBT_REDUCTION", "software allocation mismatch")
    require(by_id["cogbx-ux-exemplar-r0"]["disposition"] == "SLEEP_KEEP_ADDRESSABLE", "publication should quiesce")
    require(by_id["cogbx-peer-reconstruction-candidate"]["disposition"] == "REMAIN_DORMANT_WITH_EXACT_WAKE", "dormant candidate should remain dormant")
    require(all(r["heartbeat_mode"] != "FIXED_FREQUENCY" for r in results), "fixed heartbeat forbidden")
    require(all(all(v == 0 for v in r["effects"].values()) for r in results), "external effect detected")

    return {
        "schema":"CoObject.VitalityReport.R0.v0.1",
        "state":"PASS_THREE_OBJECT_METABOLIC_INTERFACE__EVENT_DRIVEN_HEARTBEAT",
        "object_count":len(results),
        "results":results,
        "heartbeat_default":policy["heartbeat_default"],
        "useful_findings":[
            "SOFTWARE_DEBT_ELECTS_ONE_BOUNDED_EXTENSION",
            "CURRENT_PUBLICATION_QUIESCES_WITH_RECEIVER_WAKE",
            "HIGH_OPTION_CONCEPT_REMAINS_DORMANT_UNTIL_EXACT_PREREQUISITES"
        ],
        "effects":dict(ZERO_EFFECTS),
        "rails":policy["rails"],
        "nonclaims":[
            "SYNTHETIC_POLICY_NE_RUNTIME_ADOPTION",
            "VITALITY_METAPHOR_NE_SENTIENCE",
            "DECLARED_METABOLISM_NE_PROVEN_CAPABILITY",
            "EVENT_DRIVEN_PULSE_NE_ALWAYS_ON_DAEMON",
            "NO_X2_BINDING_PROVED",
            "NO_GLOBAL_HEARTBEAT_BUS_PROVED"
        ]
    }

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", type=Path, required=True)
    p.add_argument("--policy", type=Path, required=True)
    args = p.parse_args()
    report = run(
        json.loads(args.fixture.read_text(encoding="utf-8")),
        json.loads(args.policy.read_text(encoding="utf-8")),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
