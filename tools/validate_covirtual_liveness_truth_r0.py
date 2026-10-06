#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path

P=Path("fixtures/virtual-session/covirtual_liveness_truth_r0.json")

def fail(x): raise SystemExit(x)
def blob(path): return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()
def csha(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()

def classify(s):
    if s.get("retired"):
        return "RETIRED", False, bool(s["checkpoint_present"])
    live_any = any(e["state"]=="LIVE" for e in s["embodiments"])
    recoverable = bool(s["checkpoint_present"] and s["currentness_cursor_present"])
    wakeable = bool(recoverable and s["wake_conditions_present"])

    if live_any:
        return "MATERIALIZED", True, recoverable
    if wakeable:
        if len(s["embodiments"])==0:
            return "DORMANT", True, recoverable
        return "WAKEABLE", True, recoverable
    return "BLOCKED", False, recoverable

def main():
    d=json.loads(P.read_text())
    src=d["source_bindings"]
    for pkey,skey in [
        ("morphology_doc_path","morphology_doc_blob_sha"),
        ("virtual_policy_path","virtual_policy_blob_sha"),
        ("copulse_doc_path","copulse_doc_blob_sha")
    ]:
        if blob(src[pkey]) != src[skey]:
            fail("FAIL_SOURCE_BIND:"+src[pkey])

    obs=[]
    for s in d["scenarios"]:
        state,alive,recoverable=classify(s)
        if state != s["expected_virtual_state"]:
            fail("FAIL_STATE:"+s["id"]+":"+state)
        if alive != s["expected_alive"]:
            fail("FAIL_ALIVE:"+s["id"])
        if "expected_recoverable" in s and recoverable != s["expected_recoverable"]:
            fail("FAIL_RECOVERABLE:"+s["id"])
        obs.append({"id":s["id"],"virtual_state":state,"alive":alive,"recoverable":recoverable})

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({
        "STATE":"PASS_COVIRTUAL_LIVENESS_TRUTH_R0",
        "checked_out_head_sha":head,
        "scenario_count":len(obs),
        "fixture_semantic_sha256":csha(d),
        "observed":obs,
        "rails":d["rails"]
    },separators=(",",":")))

if __name__=="__main__": main()
