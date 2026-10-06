#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path
P=Path("fixtures/ux/co_session_regroup_loop_r0.json")
def fail(x): raise SystemExit(x)
def blob(path): return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()
def csha(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def classify(c):
    k=c["kind"]
    if k=="TAB_RETIRE":
        if c["unique_unexternalized_state"]: return "HOLD_EXTERNALIZE_UNIQUE_STATE"
        if c["virtual_recoverable"] and c["receiver_pickup_proven"] and not c["material_wake"]:
            return "RETIRE_TAB_SAFE_CANDIDATE_AND_PARK_DORMANT"
    if k=="ACK_REWISE" and c["new_input"] and c["ambiguous_or_conflicting"] and c["proven_history_exists"]:
        return "COACKREWISE_PRESERVE_HISTORY"
    if k=="SYNC" and c["pointer_emitted"] and not c["receiver_readproof"]:
        return "POINTER_ONLY_NOT_PICKED_UP"
    if k=="TURTLE" and c["depth"]>=4 and c["more_relations_exist"] and not c["material_delta_found"]:
        return "STOP_PRESERVE_UNTRAVERSED_FRONTIER"
    if k=="DORMANCY" and c["virtual_recoverable"] and not c["wake_predicate_true"]:
        return "DORMANT_OPTION_ALIVE"
    if k=="CLOSE_SAFE" and c["close_safe"] and not c["wake_predicate_true"] and c["generic_ping_only"]:
        return "REMAIN_DORMANT_OPTION"
    if k=="FULL_LOOP" and c["regroup_complete"] and c["receiver_readproof"] and c["bounded_deed_proven"] and not c["material_wake"]:
        return "FULL_LOOP_VERIFIED_QUIET_RICK_ACTION_NONE"
    return "FAIL"
def main():
    d=json.loads(P.read_text())
    for x in d["source_bindings"].values():
        if blob(x["path"])!=x["blob_sha"]: fail("FAIL_SOURCE_BIND:"+x["path"])
    if d["next_deed_policy"]["default"]!="HIGHEST_VALUE_BOUNDED_PROOF_ACTION": fail("FAIL_NEXT_DEED_DEFAULT")
    if d["next_deed_policy"]["smallest_safe_deed"]!="NARROW_FAILSAFE_ONLY": fail("FAIL_SMALLEST_FAILSAFE")
    t=d["turtle_policy"]
    if t["max_depth_per_pass"]!=4 or t["max_nodes_per_pass"]!=64 or not t["preserve_untraversed_frontier"]:
        fail("FAIL_TURTLE_BOUNDS")
    obs=[]
    for c in d["scenarios"]:
        got=classify(c)
        if got!=c["expected"]: fail("FAIL:"+c["id"]+":"+got)
        obs.append({"id":c["id"],"decision":got})
    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({
        "STATE":"PASS_COSESSION_REGROUP_FULL_LOOP_R0",
        "checked_out_head_sha":head,
        "scenario_count":len(obs),
        "fixture_semantic_sha256":csha(d),
        "runtime_actuation":False,
        "provider_ui_mutation":False,
        "observed":obs,
        "rails":d["rails"]
    },separators=(",",":")))
if __name__=="__main__": main()
