#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path
P=Path("fixtures/virtual-session/coliving_work_field_r0.json")
def fail(x): raise SystemExit(x)
def blob(path): return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()
def csha(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def alive(state): return state in {"RECOVERABLE","WAKEABLE","MATERIALIZED","DORMANT"}
def main():
    d=json.loads(P.read_text())
    s=d["source_bindings"]
    if blob(s["liveness_doc_path"]) != s["liveness_doc_blob_sha"]: fail("FAIL_LIVENESS_DOC_BIND")
    if blob(s["liveness_fixture_path"]) != s["liveness_fixture_blob_sha"]: fail("FAIL_LIVENESS_FIXTURE_BIND")
    vis=[x for x in d["work_objects"] if not x["retired"]]
    vis.sort(key=lambda x:(-x["priority"],x["id"]))
    ids=[x["id"] for x in vis]
    if "W6" in ids: fail("FAIL_RETIRED_VISIBLE")
    if ids.index("W3") > ids.index("W1"): fail("FAIL_DEPENDENCY_ORDER")
    for x in ("W2","W4","W5"):
        if x not in ids: fail("FAIL_NON_TASK_OBJECT_LOST:"+x)
    obs=[]
    for c in d["ux_cases"]:
        p="STALE_PROJECTION" if c["projection_age_seconds"] > c["projection_ttl_seconds"] else "FRESH_PROJECTION"
        a=alive(c["virtual_state"])
        e=c["expected"]
        if p != e["projection_state"]: fail("FAIL_PROJECTION:"+c["id"])
        if c["virtual_state"] != e["display_session_state"]: fail("FAIL_DISPLAY:"+c["id"])
        if a != e["session_alive"]: fail("FAIL_ALIVE:"+c["id"])
        obs.append({"id":c["id"],"projection_state":p,"display_session_state":c["virtual_state"],"session_alive":a})
    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({"STATE":"PASS_COLIVING_WORK_FIELD_R0","checked_out_head_sha":head,"projected_order":ids,"ux_cases":obs,"fixture_semantic_sha256":csha(d),"ux_state":"UX_ACCEPTANCE_UNPROVEN","rails":d["rails"]},separators=(",",":")))
if __name__=="__main__": main()
