#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
from typing import Any

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()

def load(path: Path) -> tuple[dict[str, Any], bytes]:
    raw=path.read_bytes(); obj=json.loads(raw.decode("utf-8"))
    if not isinstance(obj,dict): raise ValueError("FAIL_CLOSED__EXPECTED_OBJECT")
    return obj,raw

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--packet",required=True); ap.add_argument("--expected-sha256",required=True); ap.add_argument("--receiver-id",required=True); ap.add_argument("--output",required=True); args=ap.parse_args()
    out=Path(args.output).resolve()
    if out.exists(): raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")
    packet,raw=load(Path(args.packet).resolve()); actual=sha256_bytes(raw)
    if actual!=args.expected_sha256.upper(): raise SystemExit("FAIL_CLOSED__PACKET_SHA_MISMATCH")
    if packet.get("receiver_id")!=args.receiver_id: raise SystemExit("FAIL_CLOSED__WRONG_RECEIVER")
    if packet.get("state")!="EXACT_MATCH_PACKET_COMPILED__DELIVERED_CANDIDATE__PICKUP_UNPROVEN": raise SystemExit("FAIL_CLOSED__PACKET_STATE")
    if packet.get("candidate_deed",{}).get("execution_authorized") is not False: raise SystemExit("FAIL_CLOSED__EXECUTION_AUTHORITY_PRESENT")
    artifact={
        "schema":"CoEncounterMatchPacketReadproof.R0C.v0.1-candidate",
        "state":"PASS_EXACT_PACKET_READPROOF__PICKED_UP_BOUNDED",
        "receiver_id":args.receiver_id,
        "receiver_process_id":os.getpid(),
        "packet_id":packet["packet_id"],
        "packet_sha256":actual,
        "coverage":{"exact_bytes_read":True,"json_parse":True,"receiver_identity_match":True,"full_packet_object_read":True,"semantic_acceptance":"NOT_PROVEN","candidate_deed_execution_authorized":False},
        "effects":{"assignment":0,"notification":0,"authority_change":0,"execution":0,"provider_session_mutation":0},
        "next":"OPTIONAL_CONTRIBUTION_PROPOSAL_WITH_LINEAGE__NO_AUTO_ASSIGNMENT",
        "nonclaims":["PICKED_UP_NE_INTEGRATED","READPROOF_NE_SEMANTIC_ACCEPTANCE","PICKUP_NE_ASSIGNMENT","LOCAL_PROCESS_NE_DISTINCT_FAILURE_DOMAIN","NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"]
    }
    enc=(json.dumps(artifact,indent=2,ensure_ascii=False)+"\n").encode("utf-8"); out.write_bytes(enc)
    print(json.dumps({"STATE":artifact["state"],"OUTPUT":str(out),"OUTPUT_SHA256":sha256_bytes(enc),"PACKET_SHA256":actual,"PROCESS_ID":os.getpid(),"NEXT":artifact["next"]},separators=(",",":")))
    return 0
if __name__=="__main__": raise SystemExit(main())
