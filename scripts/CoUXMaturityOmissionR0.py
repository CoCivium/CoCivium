#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ALLOWED_STATES = {
    "PROVEN_BOUNDED",
    "PARTIAL",
    "READY_NOT_LANDED",
    "READY_TO_HARVEST",
    "HELD_CURRENTNESS",
    "HELD_RECEIVER",
    "HELD_PROOF",
    "HELD_PUBLIC_CURRENTNESS",
    "DORMANT_WITH_WAKE",
    "MISSING_PROOF",
    "MISSING_RUNTIME",
    "MISSING_IMPLEMENTATION",
    "MISSING_ACCEPTANCE",
    "MISSING_DEPLOYMENT",
    "MISSING_PILOT",
    "MISSING_INTEGRATION",
}

REQUIRED_NONCLAIMS = {
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
}

REQUIRED_LANE_FIELDS = {
    "lane_id","domain","goal","maturity_state","proof_scope","source_state",
    "runtime_state","receiver_state","ux_state","priority","ongoing_expected",
    "ongoing_mechanism","blockers","why_not_ongoing","wake_conditions",
    "next_safe_deed","evidence_refs"
}

def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)

def run(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == "CoUX.MaturityOmissionRegistry.R0.v0.1", "wrong schema")
    lanes = payload.get("lanes")
    require(isinstance(lanes, list) and len(lanes) >= 20, "registry must seed at least 20 lanes")
    require(REQUIRED_NONCLAIMS.issubset(set(payload.get("required_nonclaims", []))), "required nonclaims missing")

    ids = []
    maturity = Counter()
    domains = Counter()
    ongoing_gaps = []
    dormant = []
    held = []
    missing = []
    proven = []

    for lane in lanes:
        missing_fields = REQUIRED_LANE_FIELDS - set(lane)
        require(not missing_fields, f"{lane.get('lane_id')}: missing fields {sorted(missing_fields)}")
        lane_id = lane["lane_id"]
        require(isinstance(lane_id, str) and lane_id, "lane_id required")
        ids.append(lane_id)
        require(lane["maturity_state"] in ALLOWED_STATES, f"{lane_id}: bad maturity state")
        require(isinstance(lane["priority"], int) and 0 <= lane["priority"] <= 100, f"{lane_id}: bad priority")
        require(isinstance(lane["blockers"], list), f"{lane_id}: blockers must be list")
        require(isinstance(lane["wake_conditions"], list), f"{lane_id}: wake_conditions must be list")
        require(isinstance(lane["evidence_refs"], list) and lane["evidence_refs"], f"{lane_id}: evidence refs required")
        require(isinstance(lane["next_safe_deed"], str) and lane["next_safe_deed"], f"{lane_id}: next deed required")
        require(isinstance(lane["why_not_ongoing"], str) and lane["why_not_ongoing"], f"{lane_id}: why_not_ongoing required")

        maturity[lane["maturity_state"]] += 1
        domains[lane["domain"]] += 1

        if lane["maturity_state"] == "PROVEN_BOUNDED":
            proven.append(lane_id)
        if lane["maturity_state"].startswith("HELD_"):
            held.append(lane_id)
        if lane["maturity_state"].startswith("MISSING_"):
            missing.append(lane_id)
        if lane["maturity_state"] == "DORMANT_WITH_WAKE":
            require(lane["wake_conditions"], f"{lane_id}: dormant lane requires wake conditions")
            require(lane["ongoing_expected"] is False, f"{lane_id}: dormant lane should not claim ongoing execution")
            dormant.append({
                "lane_id": lane_id,
                "wake_conditions": lane["wake_conditions"],
                "next_safe_deed": lane["next_safe_deed"]
            })

        if lane["ongoing_expected"] and (
            lane["ongoing_mechanism"].startswith("NONE_")
            or lane["ongoing_mechanism"] in {
                "CONTRACT_ONLY","SOURCE_ONLY","SYNTHETIC_ONLY","BRANCH_ONLY",
                "DONOR_ONLY","NO_CURRENT_RUNTIME_PROOF","NO_UNIFIED_RUNTIME",
                "NO_CURRENT_DEVICE_PROOF","COMPONENT_ONLY","EVENT_DRIVEN_CONTRACT_ONLY",
                "TESTED_SOURCE_ONLY","LOCAL_INTERACTIVE_ONLY","WAITING_FOR_PHYSICAL_READPROOF"
            }
        ):
            ongoing_gaps.append({
                "lane_id": lane_id,
                "priority": lane["priority"],
                "mechanism": lane["ongoing_mechanism"],
                "why": lane["why_not_ongoing"],
                "next_safe_deed": lane["next_safe_deed"]
            })

    require(len(ids) == len(set(ids)), "duplicate lane_id")

    obs_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for obs in payload.get("currentness_observations", []):
        obs_by_subject[obs["subject"]].append(obs)

    conflicts = []
    for subject, observations in obs_by_subject.items():
        results = {x["result"] for x in observations}
        if len(results) > 1:
            conflicts.append({
                "subject": subject,
                "observations": [
                    {
                        "observation_id": x["observation_id"],
                        "observer": x["observer"],
                        "result": x["result"],
                        "confidence": x["confidence"],
                        "nonclaim": x["nonclaim"],
                    }
                    for x in observations
                ]
            })

    active_frontier = sorted(
        [
            {
                "lane_id": x["lane_id"],
                "domain": x["domain"],
                "priority": x["priority"],
                "maturity_state": x["maturity_state"],
                "next_safe_deed": x["next_safe_deed"],
                "blockers": x["blockers"],
            }
            for x in lanes
            if x["maturity_state"] != "DORMANT_WITH_WAKE"
        ],
        key=lambda x: (-x["priority"], x["lane_id"])
    )[:12]

    require(active_frontier[0]["lane_id"] == "x2-currentness-observer", "X2 currentness should remain top gate")
    require("x2-coorb-calm-front" in {x["lane_id"] for x in active_frontier[:5]}, "X2 calm front should remain top-five")
    require("recovery-drill-visible" in {x["lane_id"] for x in active_frontier[:5]}, "recovery drill should remain top-five")
    require(any(c["subject"] == "X2" for c in conflicts), "X2 split-currentness conflict must remain explicit")
    require("metabolic-wake-selector-r0a" in ids, "R0A wake-selector lane required")
    r0a = next(x for x in lanes if x["lane_id"] == "metabolic-wake-selector-r0a")
    require(r0a["maturity_state"] == "PROVEN_BOUNDED", "R0A should be landed and proven")
    require(r0a["source_state"] == "LANDED_TO_MAIN", "R0A source state stale")
    require("accessibility-acceptance" in ids, "accessibility lane required")
    require("receiver-first-use" in ids, "receiver lane required")

    return {
        "schema":"CoUX.MaturityOmissionReport.R0.v0.1",
        "state":"PASS_COUX_MATURITY_OMISSION_REGISTRY_R0",
        "lane_count":len(lanes),
        "domain_count":len(domains),
        "maturity_counts":dict(sorted(maturity.items())),
        "domain_counts":dict(sorted(domains.items())),
        "proven_bounded":sorted(proven),
        "held_lanes":sorted(held),
        "missing_lanes":sorted(missing),
        "ongoing_mechanism_gaps":sorted(ongoing_gaps,key=lambda x:(-x["priority"],x["lane_id"])),
        "dormant_with_wake":dormant,
        "currentness_conflicts":conflicts,
        "active_frontier":active_frontier,
        "required_nonclaims":payload["required_nonclaims"],
    }

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--registry",type=Path,required=True)
    args=p.parse_args()
    payload=json.loads(args.registry.read_text(encoding="utf-8"))
    print(json.dumps(run(payload),indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
