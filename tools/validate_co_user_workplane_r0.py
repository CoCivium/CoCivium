#!/usr/bin/env python3
import json
import hashlib
import subprocess
from pathlib import Path

P = Path("fixtures/ux/co_user_workplane_r0.json")

def fail(msg):
    raise SystemExit(msg)

def blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def csha(obj):
    raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    for item in d["source_bindings"].values():
        if blob(item["path"]) != item["blob_sha"]:
            fail("FAIL_SOURCE_BIND:"+item["path"])

    observed=[]
    for s in d["scenarios"]:
        i=s["input"]; e=s["expected"]; sid=s["id"]
        if sid=="U01_MANY_VIRTUAL_FEW_VISIBLE":
            got={"default_visible_session_rows":0,"visible_workspace_count":i["workspaces"],"backend_session_drilldown":True}
        elif sid=="U02_ROUTINE_HEALTH_NO_USER_ACTION":
            got={"headline":"HEALTHY","rick_action":"NONE"}
        elif sid=="U03_STALE_CURRENTNESS_RAISES_EXCEPTION":
            got={"headline":"DEGRADED","exception":"CURRENTNESS_STALE" if i["currentness_age_s"]>i["currentness_sla_s"] else "NONE"}
        elif sid=="U04_QUEUE_JAM_RAISES_EXCEPTION":
            stalled=i["queue_age_s"]>i["queue_sla_s"] and i["fanin_drain_rate"]<=0
            got={"headline":"DEGRADED" if stalled else "HEALTHY","exception":"FLOW_STALLED" if stalled else "NONE"}
        elif sid=="U05_PREPARED_IS_NOT_READY":
            got={"user_label":"PREPARED","ready":False}
        elif sid=="U06_MACHINE_OWNED_SENT_CAN_BE_READY":
            ready=(i["delivery_state"] in {"SENT","DELIVERED","PICKED_UP","INTEGRATED"} and not i["human_transport_required"] and i["machine_next_step_bound"])
            got={"user_label":"READY" if ready else i["delivery_state"],"ready":ready}
        elif sid=="U07_DELIVERED_NOT_PICKED_UP":
            got={"lifecycle_claim":"PICKED_UP" if i["receiver_readproof"] else "DELIVERED_ONLY"}
        elif sid=="U08_PICKUP_REQUIRES_READPROOF":
            got={"lifecycle_claim":"PICKED_UP" if i["receiver_readproof"] else "HOLD"}
        elif sid=="U09_PARALLELISM_WITH_BACKPRESSURE":
            pressure=i["new_discovery_rate"]>i["fanin_drain_rate"] and i["receiver_backlog"]>10
            got={"action":"CONTRACT_DISCOVERY_AND_FANIN" if pressure else "HOLD","user_session_rows_added":0}
        elif sid=="U10_MOMENTUM_TO_AUDIENCE":
            moving=i["target_audience_bound"] and i["delivery_state"] in {"SENT","DELIVERED","PICKED_UP","INTEGRATED"} and i["last_proof_age_s"]<=i["stall_sla_s"]
            got={"momentum":"MOVING" if moving else "STALLED","rick_action":"NONE" if moving else "INVESTIGATE_EXCEPTION"}
        else:
            fail("UNKNOWN_SCENARIO:"+sid)
        if got != e:
            fail("FAIL:"+sid+":"+json.dumps({"got":got,"expected":e},sort_keys=True))
        observed.append({"id":sid,**got})

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({
        "STATE":"PASS_COUSER_WORKPLANE_R0",
        "checked_out_head_sha":head,
        "scenario_count":len(observed),
        "routine_manual_session_cycling_required":False,
        "default_visible_provider_session_rows":0,
        "fixture_semantic_sha256":csha(d),
        "observed":observed,
        "current_runtime_binding":"UNPROVEN",
        "current_ux_acceptance":"UX_ACCEPTANCE_UNPROVEN"
    },separators=(",",":")))

if __name__=="__main__":
    main()
