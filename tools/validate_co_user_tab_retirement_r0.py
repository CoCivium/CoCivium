#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
P=Path("fixtures/ux/co_user_tab_retirement_r0.json")
def fail(x): raise SystemExit(x)
def blob(p): return subprocess.check_output(["git","rev-parse",f"HEAD:{p}"],text=True).strip()
def csha(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def decide(i):
    if not i["provider_tab_open"]: return "NO_TAB_ACTION_NEEDED"
    if i["unique_unexternalized_state"] or not i["durable_continuation_pointer"]: return "HOLD_EXTERNALIZE_UNIQUE_STATE"
    if not i["alternate_route_or_reconstruction"]: return "HOLD_NO_ALTERNATE_ROUTE"
    if i["required_receiver_pickup_missing"]: return "HOLD_RECEIVER_PICKUP_REQUIRED"
    if i["pending_human_only_effect"]: return "HOLD_HUMAN_EFFECT_PENDING"
    return "RETIRE_TAB_SAFE_CANDIDATE"
def main():
    d=json.loads(P.read_text())
    for x in d["source_bindings"].values():
        if blob(x["path"])!=x["blob_sha"]: fail("FAIL_SOURCE_BIND:"+x["path"])
    seen=[]
    for s in d["scenarios"]:
        got=decide(s["input"])
        if got!=s["expected"]: fail("FAIL:"+s["id"]+":"+got)
        seen.append({"id":s["id"],"decision":got})
    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({
      "STATE":"PASS_COUSER_TAB_RETIREMENT_R0",
      "checked_out_head_sha":head,
      "scenario_count":len(seen),
      "provider_tab_action_executed":False,
      "account_mutation_executed":False,
      "logical_work_continues":True,
      "fixture_semantic_sha256":csha(d),
      "current_runtime_binding":"UNPROVEN",
      "observed":seen
    },separators=(",",":")))
if __name__=="__main__": main()
