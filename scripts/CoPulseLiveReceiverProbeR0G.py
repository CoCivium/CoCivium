#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path

def cjson(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(b): return hashlib.sha256(b).hexdigest().upper()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receiver-id",required=True); p.add_argument("--virtual-session-id",required=True)
    p.add_argument("--participant-id",required=True); p.add_argument("--challenge",required=True)
    p.add_argument("--capacity",type=int,required=True); p.add_argument("--max-digest-summaries",type=int,default=4)
    p.add_argument("--sampled-at",required=True); p.add_argument("--observed-at",required=True); p.add_argument("--out-dir",required=True)
    a=p.parse_args()
    if a.capacity < 0 or a.max_digest_summaries < 1: raise SystemExit("INVALID_CAPACITY")
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    pid=os.getpid(); embodiment=f"process:{pid}"
    challenge_sha=sha(a.challenge.encode())
    response_basis={"receiver_id":a.receiver_id,"virtual_session_id":a.virtual_session_id,"participant_id":a.participant_id,"embodiment_id":embodiment,"challenge_sha256":challenge_sha}
    response_sha=sha(cjson(response_basis))
    bind_basis={**response_basis,"observed_at":a.observed_at}
    binding_id="receiver-binding:"+sha(cjson(bind_basis))[:24]
    pressure={
      "sample_id":"pressure:"+sha(cjson({"receiver_id":a.receiver_id,"sampled_at":a.sampled_at,"capacity":a.capacity}))[:24],
      "receiver_id":a.receiver_id,"sampled_at":a.sampled_at,"capacity_source":"SYNTHETIC_FIXTURE",
      "max_currentness_items":a.capacity,"max_digest_summaries":a.max_digest_summaries,
      "authority_ceiling":"CANDIDATE_ONLY","notes":["R0G live receiver self-report synthetic canary"]
    }
    pressure_bytes=(json.dumps(pressure,indent=2,sort_keys=True)+"\n").encode()
    pressure_path=out/"pressure.json"; pressure_path.write_bytes(pressure_bytes)
    binding={
      "schema":"CoPulseLiveReceiverBinding.R0G.v0.1-candidate","state":"PROVEN_LIVE_FOR_BOUNDED_LOCAL_CANARY",
      "binding_id":binding_id,"receiver_id":a.receiver_id,"virtual_session_id":a.virtual_session_id,
      "participant_id":a.participant_id,"participant_class":"RECEIVER","embodiment_id":embodiment,
      "embodiment_class":"LOCAL_PROCESS","observed_at":a.observed_at,
      "liveness_challenge":{"method":"STDIN_CHALLENGE_RESPONSE","challenge_sha256":challenge_sha,"response_sha256":response_sha},
      "authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PUBLIC","lifecycle_scope":"PROCESS_LIFETIME_ONLY",
      "nonclaims":["PROCESS_PID_NE_IDENTITY","LIVE_NOW_NE_PERSISTENT_RECEIVER","LIVENESS_NE_AUTHORITY"]
    }
    binding_path=out/"binding.json"; binding_path.write_text(json.dumps(binding,indent=2,sort_keys=True)+"\n")
    att_basis={"receiver_id":a.receiver_id,"receiver_binding_id":binding_id,"producer_instance_id":embodiment,"pressure_sample_sha256":sha(pressure_bytes)}
    attestation={
      "schema":"CoPulseCapacitySourceAttestation.R0G.v0.1-candidate","state":"PROVEN_SOURCE_BINDING__ACCURACY_UNPROVEN",
      "attestation_id":"capacity-attestation:"+sha(cjson(att_basis))[:24],
      "receiver_id":a.receiver_id,"receiver_binding_id":binding_id,"producer_instance_id":embodiment,
      "pressure_sample_sha256":sha(pressure_bytes),"capacity_source":"SYNTHETIC_FIXTURE",
      "source_class":"RECEIVER_SELF_REPORT_SYNTHETIC_CANARY","observation_method":"LIVE_PROCESS_CHALLENGE_RESPONSE",
      "observed_at":a.observed_at,"authority_ceiling":"CANDIDATE_ONLY",
      "nonclaims":["PROVENANCE_NE_ACCURACY","SELF_REPORT_NE_MEASUREMENT_TRUTH","CAPACITY_SOURCE_NE_AUTHORITY"]
    }
    att_path=out/"attestation.json"; att_path.write_text(json.dumps(attestation,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"state":"HELLO_LIVE_RECEIVER","pid":pid,"receiver_id":a.receiver_id,"binding_id":binding_id,"response_sha256":response_sha,"pressure_path":str(pressure_path),"binding_path":str(binding_path),"attestation_path":str(att_path)},separators=(",",":")),flush=True)
    line=sys.stdin.readline().rstrip("\n")
    if line != "ACK "+a.challenge: raise SystemExit("CHALLENGE_ACK_MISMATCH")
    print(json.dumps({"state":"ACK_CHALLENGE_CONFIRMED","receiver_id":a.receiver_id,"binding_id":binding_id,"response_sha256":response_sha},separators=(",",":")),flush=True)
    line=sys.stdin.readline().rstrip("\n")
    if line != "EXIT": raise SystemExit("EXPECTED_EXIT")
    print(json.dumps({"state":"EXIT_CONFIRMED","receiver_id":a.receiver_id},separators=(",",":")),flush=True)
if __name__=="__main__": main()
