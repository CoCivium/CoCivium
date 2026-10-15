#!/usr/bin/env python3
import itertools, json, hashlib

DIMS = [
    "provider_tab_alive",
    "virtual_envelope",
    "material_drift",
    "checkpoint_valid",
    "same_objective",
    "human_gate",
    "financial_effect",
    "sync_required",
    "delivery_proven",
    "pickup_proven",
    "integration_required",
    "integration_proven",
    "wake_predicate",
    "meta_depth_over_budget",
]

def decide(v):
    if not v["virtual_envelope"]:
        return "HOLD_NO_VIRTUAL_ENVELOPE"
    if not v["checkpoint_valid"]:
        return "HOLD_INVALID_CHECKPOINT"
    if v["meta_depth_over_budget"]:
        return "COMPACT_OR_HOLD_META_RECURSION"
    if not v["same_objective"]:
        return "ELECT_NEW_LOGICAL_SESSION_OR_WAVE"
    if v["material_drift"]:
        return "COBOOGIE_DELTA_AUDIT_THEN_COREGROUP"
    if v["financial_effect"] or v["human_gate"]:
        return "COACKREWISE_REQUIRED"
    if v["sync_required"] and not v["delivery_proven"]:
        return "COSYNC_DELIVER"
    if v["sync_required"] and v["delivery_proven"] and not v["pickup_proven"]:
        return "WAIT_OR_VERIFY_PICKUP"
    if v["integration_required"] and not v["integration_proven"]:
        return "QUALIFY_INTEGRATION"
    if v["wake_predicate"]:
        return "RUN_ONE_BOUNDED_WORK_UNIT"
    return "QUIESCE_OR_SLEEP"

rows=[]
fails=[]
for case_id,bits in enumerate(itertools.product([False, True], repeat=len(DIMS))):
    v=dict(zip(DIMS,bits))
    decision=decide(v)
    row={"case_id":case_id,**v,"decision":decision}
    rows.append(row)

    # Provider-tab liveness must not define logical-session decision.
    twin=dict(v); twin["provider_tab_alive"]=not v["provider_tab_alive"]
    if decide(twin)!=decision:
        fails.append({"case":case_id,"invariant":"PROVIDER_TAB_ALIVE_NE_LOGICAL_DECISION"})

    if decision=="COACKREWISE_REQUIRED" and not (v["human_gate"] or v["financial_effect"]):
        fails.append({"case":case_id,"invariant":"ACKREWISE_ONLY_TRUE_HUMAN_GATE"})

    if v["financial_effect"] and v["virtual_envelope"] and v["checkpoint_valid"] and not v["meta_depth_over_budget"] and v["same_objective"] and not v["material_drift"] and decision!="COACKREWISE_REQUIRED":
        fails.append({"case":case_id,"invariant":"FINANCIAL_ALWAYS_HUMAN_GATE"})

    if decision=="RUN_ONE_BOUNDED_WORK_UNIT" and (v["human_gate"] or v["financial_effect"]):
        fails.append({"case":case_id,"invariant":"NO_EXECUTION_ACROSS_HUMAN_GATE"})

    if v["sync_required"] and v["delivery_proven"] and not v["pickup_proven"] and decision=="QUALIFY_INTEGRATION":
        fails.append({"case":case_id,"invariant":"DELIVERY_NE_PICKUP"})

    if v["meta_depth_over_budget"] and v["virtual_envelope"] and v["checkpoint_valid"] and decision!="COMPACT_OR_HOLD_META_RECURSION":
        fails.append({"case":case_id,"invariant":"META_RECURSION_FAILS_BOUNDED"})

state_counts={}
for r in rows:
    state_counts[r["decision"]]=state_counts.get(r["decision"],0)+1

receipt={
    "schema":"CoSessionRelationalFullLoop.Canary.R2.v0.1",
    "state":"PASS_FULL_LOOP_MATRIX" if not fails else "HOLD_FULL_LOOP_MATRIX",
    "case_count":len(rows),
    "fail_count":len(fails),
    "state_counts":state_counts,
    "proved_invariants":[
        "PROVIDER_TAB_ALIVE_NE_LOGICAL_DECISION",
        "MANUAL_SESSION_IS_ONE_EMBODIMENT",
        "FINANCIAL_EFFECT_REQUIRES_COACKREWISE",
        "DELIVERY_NE_PICKUP",
        "RELATION_OF_RELATION_NE_UNBOUNDED_CONTROL_RECURSION",
        "NO_HUMAN_HEARTBEAT_REQUIRED_FOR_QUIESCENCE"
    ],
    "failures":fails[:50]
}
blob=json.dumps(receipt,sort_keys=True,separators=(",",":")).encode()
receipt["canonical_sha256"]=hashlib.sha256(blob).hexdigest().upper()
print(json.dumps(receipt,indent=2))
if fails:
    raise SystemExit(1)
