#!/usr/bin/env python3
"""CoAlive R1: one finite, entirely synthetic CoObject heartbeat/wake *proposal*.

This is an offline deterministic test of event qualification, repair priorities,
resource reserves, dedupe, and dormancy. It is NOT a daemon, receiver ACK,
public event bus, provider heartbeat, proof of useful outcomes, or ET/G_d claim.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = "CoAll.CoObjectMetabolicHeartbeat.SyntheticShadow.R1"
RESULT_SCHEMA = "CoAll.CoObjectMetabolicHeartbeat.ShadowReceipt.R1"


def load_inputs():
    return (
        json.loads((ROOT / "heartbeat_fixture_r1.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "cohort.json").read_text(encoding="utf-8")),
    )


def require_integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("NONNEGATIVE_INTEGER_REQUIRED")
    return value


def validate(fixture, cohort):
    if fixture.get("schema") != SCHEMA:
        raise ValueError("BAD_HEARTBEAT_SCHEMA")
    if cohort.get("schema") != "CoAll.CoMetabolismAssetCohort.R0":
        raise ValueError("BAD_COHORT_SCHEMA")
    policy = fixture["policy"]
    for field in ("max_shadow_actions", "budget_units", "min_reserve_units",
                  "max_cascade_hops", "external_effects", "live_workers"):
        require_integer(policy[field])
    if (policy["max_shadow_actions"] > 3 or
            policy["min_reserve_units"] > policy["budget_units"] or
            policy["max_cascade_hops"] != 0 or
            policy["external_effects"] != 0 or
            policy["live_workers"] != 0 or
            policy["allow_network"] is not False or
            policy["default_receiver_ack"] is not False):
        raise ValueError("UNBOUNDED_OR_EFFECTFUL_POLICY")
    assets = {a["id"]: a for a in cohort["assets"]}
    profiles = fixture["objects"]
    if len(profiles) != 3 or {x["asset_id"] for x in profiles} != {"M05", "M07", "M08"}:
        raise ValueError("REQUIRED_THREE_UNLIKE_OBJECTS")
    if len({x["kind"] for x in profiles}) != 3:
        raise ValueError("NOT_UNLIKE_OBJECTS")
    for p in profiles:
        asset = assets[p["asset_id"]]
        if (asset["lifecycle"] != "UNASSESSED" or
                asset["receiver_use"] != "UNVERIFIED" or
                asset["verified_outcome"] is not False):
            raise ValueError("UNSUPPORTED_PROMOTION")
        require_integer(p["estimated_cost_units"], 1)
        if not p["wake_on"] or not p["repair_on"] or not p["stop_rule"]:
            raise ValueError("MISSING_METABOLIC_INTERFACE")
        if p["logical_state"] not in ("UNASSESSED", "UNASSESSED_NOT_PROVEN_DORMANT"):
            raise ValueError("FALSE_LIVENESS_STATE")
    if len(fixture["relations"]) > 4:
        raise ValueError("TOO_MANY_RELATIONS")
    for edge in fixture["relations"]:
        if (edge["from"] not in assets or edge["to"] not in assets or
                edge["automatic_cascade"] is not False or
                edge["authority"] != "NONE" or
                edge["recipient_acceptance"] != "UNVERIFIED"):
            raise ValueError("RELATION_CANNOT_SELF_AUTHORIZE")
    if len(fixture["events"]) > 16:
        raise ValueError("UNBOUNDED_EVENT_BATCH")
    seen = set()
    prior_cursor = -1
    for e in fixture["events"]:
        cursor = require_integer(e["cursor"], 1)
        if cursor <= prior_cursor or e["id"] in seen:
            raise ValueError("NONMONOTONIC_OR_DUPLICATE_PULSE")
        prior_cursor = cursor
        seen.add(e["id"])
        if e["subject"] not in assets:
            raise ValueError("UNKNOWN_SOURCE_ASSET")
        if e["evidence_class"] not in ("SYNTHETIC", "UNVERIFIED_READER_CLAIM"):
            raise ValueError("NONFIXTURE_EVIDENCE_NOT_ACCEPTED")
        if type(e["fixture_qualified"]) is not bool or type(e["public_safe"]) is not bool:
            raise ValueError("UNTYPED_EVIDENCE_GATE")
        if e["type"] not in (set(fixture["priority"]) | {"NO_CHANGE"}):
            raise ValueError("UNKNOWN_PULSE_KIND")
    return True


def shadow_tick(fixture=None, cohort=None, last_processed_cursor=0):
    if fixture is None or cohort is None:
        fixture, cohort = load_inputs()
    validate(fixture, cohort)
    require_integer(last_processed_cursor)
    assets = {a["id"]: a for a in cohort["assets"]}
    profiles = {p["asset_id"]: p for p in fixture["objects"]}
    policy = fixture["policy"]
    qualifying, held, ignored = [], [], []
    seen_events = [e for e in fixture["events"] if e["cursor"] > last_processed_cursor]
    for e in seen_events:
        p = profiles.get(e["subject"])
        if p is None or e["type"] == "NO_CHANGE" or e["type"] not in p["wake_on"]:
            ignored.append({"id": e["id"], "reason": "NO_QUALIFIED_OBJECT_RELATION"})
        elif not e["public_safe"]:
            held.append({"id": e["id"], "reason": "CONFIDENTIALITY_GATE"})
        elif e["evidence_class"] != "SYNTHETIC" or not e["fixture_qualified"]:
            held.append({"id": e["id"], "reason": "NO_QUALIFIED_FIXTURE_EVIDENCE"})
        else:
            qualifying.append(e)
    # Only one candidate per object, newest equally ranked event first.
    ordered = sorted(qualifying,
                     key=lambda e: (-fixture["priority"][e["type"]], -e["cursor"], e["subject"]))
    chosen, deferred = [], []
    used = set()
    spendable = policy["budget_units"] - policy["min_reserve_units"]
    spent = 0
    for e in ordered:
        p = profiles[e["subject"]]
        if e["subject"] in used:
            deferred.append({"id": e["id"], "reason": "DEDUPED_OBJECT_FRONTIER"})
            continue
        if len(chosen) >= policy["max_shadow_actions"] or (
                spent + p["estimated_cost_units"] > spendable):
            deferred.append({"id": e["id"], "reason": "BACKPRESSURE_OR_RESERVE"})
            continue
        used.add(e["subject"])
        spent += p["estimated_cost_units"]
        a = assets[e["subject"]]
        chosen.append({
            "asset_id": e["subject"],
            "source_path": a["source"]["path"],
            "source_git_blob_at_observation": a["source"]["git_blob_sha1"],
            "pulse_id": e["id"],
            "proposed_action": "REVIEW_CONTRADICTION" if e["type"] == "CONTRADICTION"
                               else p["candidate_action"],
            "proposal_state": "SHADOW_ONLY_NO_EXECUTION",
            "effort_units": p["estimated_cost_units"],
            "receiver_ack": "NOT_OBSERVED",
            "source_currentness": "UNVERIFIED_NOW",
            "epistemic_class": "SYNTHETIC",
        })
    status = {
        p["asset_id"]: ("REVIEW_CANDIDATE_ONLY" if p["asset_id"] in used
                         else "UNASSESSED_WITH_DORMANT_OPTION")
        for p in fixture["objects"]
    }
    projections = [{
        "asset_id": x["asset_id"],
        "kind": x["kind"],
        "observed_liveness": "UNKNOWN_NOT_POLLED",
        "lifecycle": assets[x["asset_id"]]["lifecycle"],
        "shadow_decision": status[x["asset_id"]],
        "wake_on": x["wake_on"],
        "stop_rule": x["stop_rule"],
    } for x in fixture["objects"]]
    body = {
        "schema": RESULT_SCHEMA,
        "classification": "OFFLINE_SYNTHETIC_SHADOW_NOT_A_HEARTBEAT_FROM_A_RUNNING_OBJECT",
        "selected_objects": len(profiles),
        "event_count": len(seen_events),
        "input_last_processed_cursor": last_processed_cursor,
        "candidate_processed_cursor_not_ack": max(
            [last_processed_cursor] + [e["cursor"] for e in seen_events]),
        "shadow_proposals": chosen,
        "deferred": deferred,
        "held": held,
        "ignored": ignored,
        "projections": projections,
        "resource_ledger": {
            "budget_units": policy["budget_units"],
            "reserve_units": policy["min_reserve_units"],
            "shadow_proposal_cost_units": spent,
            "unspent_units": policy["budget_units"] - spent,
            "is_synthetic_not_measured_energy": True,
        },
        "edge_fanout_count": 0,
        "receiver_readproof_count": 0,
        "actual_actions": 0,
        "actual_workers": 0,
        "network_calls": 0,
        "successor_changes": 0,
        "nonclaims": fixture["nonclaims"],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    body["deterministic_receipt_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return body


if __name__ == "__main__":
    print(json.dumps(shadow_tick(), sort_keys=True, indent=2))
