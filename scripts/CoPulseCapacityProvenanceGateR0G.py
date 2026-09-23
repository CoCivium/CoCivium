#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def cjson(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(b): return hashlib.sha256(b).hexdigest().upper()
def load(path):
    raw=Path(path).read_bytes(); obj=json.loads(raw.decode())
    if not isinstance(obj,dict): raise ValueError("NOT_OBJECT")
    return obj,raw

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--binding",required=True); p.add_argument("--pressure",required=True); p.add_argument("--attestation",required=True)
    p.add_argument("--challenge",required=True); p.add_argument("--output",required=True)
    a=p.parse_args(); out=Path(a.output)
    if out.exists(): raise SystemExit("FAIL_CLOSED__NO_CLOBBER")
    try:
      b,_=load(a.binding); pr,pr_raw=load(a.pressure); at,_=load(a.attestation)
    except Exception as e: raise SystemExit("FAIL_CLOSED__LOAD="+str(e))
    failures=[]
    if b.get("state")!="PROVEN_LIVE_FOR_BOUNDED_LOCAL_CANARY": failures.append("BINDING_STATE")
    if b.get("lifecycle_scope")!="PROCESS_LIFETIME_ONLY": failures.append("LIFECYCLE_SCOPE")
    if b.get("participant_class")!="RECEIVER": failures.append("PARTICIPANT_CLASS")
    if pr.get("receiver_id")!=b.get("receiver_id"): failures.append("PRESSURE_RECEIVER_MISMATCH")
    if at.get("receiver_id")!=b.get("receiver_id"): failures.append("ATTESTATION_RECEIVER_MISMATCH")
    if at.get("receiver_binding_id")!=b.get("binding_id"): failures.append("BINDING_ID_MISMATCH")
    if at.get("producer_instance_id")!=b.get("embodiment_id"): failures.append("PRODUCER_INSTANCE_MISMATCH")
    if at.get("capacity_source")!=pr.get("capacity_source"): failures.append("CAPACITY_SOURCE_MISMATCH")
    pressure_sha=sha(pr_raw)
    if at.get("pressure_sample_sha256")!=pressure_sha: failures.append("PRESSURE_SHA_MISMATCH")
    challenge_sha=sha(a.challenge.encode())
    lc=b.get("liveness_challenge") or {}
    if lc.get("challenge_sha256")!=challenge_sha: failures.append("CHALLENGE_SHA_MISMATCH")
    basis={"receiver_id":b.get("receiver_id"),"virtual_session_id":b.get("virtual_session_id"),"participant_id":b.get("participant_id"),"embodiment_id":b.get("embodiment_id"),"challenge_sha256":challenge_sha}
    expected_response=sha(cjson(basis))
    if lc.get("response_sha256")!=expected_response: failures.append("RESPONSE_SHA_MISMATCH")
    if failures: raise SystemExit("FAIL_CLOSED__PROVENANCE="+",".join(sorted(failures)))
    result={
      "schema":"CoPulseCapacityProvenanceGate.R0G.v0.1-candidate",
      "state":"PASS_CAPACITY_SOURCE_PROVENANCE__LIVENESS_SCOPE_BOUND",
      "receiver_id":b["receiver_id"],"receiver_binding_id":b["binding_id"],"embodiment_id":b["embodiment_id"],
      "pressure_sample_sha256":pressure_sha,"capacity_source":pr["capacity_source"],
      "source_class":at["source_class"],"observed_at":at["observed_at"],
      "effects":{"capacity_mutation":0,"receiver_context_mutation":0,"ack_cursor_mutation":0,"authority_change":0},
      "next":"R0F_FRESHNESS_THEN_R0E_BUDGET_ELECTION_WHILE_RECEIVER_BINDING_IS_LIVE",
      "nonclaims":["PROVENANCE_NE_ACCURACY","LIVENESS_SCOPE_BOUND_NE_PERSISTENT_RECEIVER","PROCESS_PID_NE_IDENTITY","CAPACITY_SOURCE_NE_AUTHORITY"]
    }
    result["gate_sha256"]=sha(cjson(result))
    out.parent.mkdir(parents=True,exist_ok=True); enc=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode(); out.write_bytes(enc)
    print(json.dumps({"STATE":result["state"],"OUTPUT":str(out),"OUTPUT_SHA256":sha(enc),"GATE_SHA256":result["gate_sha256"],"ACK_CURSOR_MUTATION":0},separators=(",",":")))
if __name__=="__main__": main()
