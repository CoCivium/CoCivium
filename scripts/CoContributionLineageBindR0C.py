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
    ap=argparse.ArgumentParser(); ap.add_argument("--packet",required=True); ap.add_argument("--readproof",required=True); ap.add_argument("--contribution",required=True); ap.add_argument("--output",required=True); args=ap.parse_args()
    out=Path(args.output).resolve()
    if out.exists(): raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")
    packet,packet_raw=load(Path(args.packet).resolve()); proof,proof_raw=load(Path(args.readproof).resolve()); contribution,contrib_raw=load(Path(args.contribution).resolve())
    packet_sha=sha256_bytes(packet_raw)
    if proof.get("state")!="PASS_EXACT_PACKET_READPROOF__PICKED_UP_BOUNDED" or proof.get("packet_sha256")!=packet_sha: raise SystemExit("FAIL_CLOSED__READPROOF_NOT_BOUND")
    if proof.get("receiver_id")!=packet.get("receiver_id") or contribution.get("receiver_id")!=packet.get("receiver_id"): raise SystemExit("FAIL_CLOSED__RECEIVER_CHAIN_MISMATCH")
    if contribution.get("packet_id")!=packet.get("packet_id") or contribution.get("relation_id")!=packet.get("relation_id"): raise SystemExit("FAIL_CLOSED__CONTRIBUTION_CHAIN_MISMATCH")
    if contribution.get("state")!="PROPOSED_CONTRIBUTION_CANDIDATE__NOT_ACCEPTED": raise SystemExit("FAIL_CLOSED__CONTRIBUTION_STATE")
    artifact={
        "schema":"CoContributionLineage.R0C.v0.1-candidate",
        "state":"PASS_BOUNDED_LINEAGE_BINDING__PROPOSED_NOT_ACCEPTED__NO_AUTO_ASSIGNMENT",
        "lineage_id":"colineage:r0c:"+sha256_bytes((packet_sha+sha256_bytes(contrib_raw)).encode())[:24],
        "process_id":os.getpid(),
        "nodes":[
            {"type":"MATCH_PACKET","id":packet["packet_id"],"sha256":packet_sha},
            {"type":"RECEIVER_READPROOF","id":proof.get("receiver_id"),"sha256":sha256_bytes(proof_raw)},
            {"type":"CONTRIBUTION_CANDIDATE","id":contribution["contribution_id"],"sha256":sha256_bytes(contrib_raw)}
        ],
        "relations":[
            {"from":packet["packet_id"],"relation":"PICKED_UP_BY","to":proof["receiver_id"]},
            {"from":proof["receiver_id"],"relation":"PROPOSED","to":contribution["contribution_id"]},
            {"from":contribution["contribution_id"],"relation":"RESPONDS_TO_OPEN_RELATION","to":packet["relation_id"]}
        ],
        "acceptance_relation":None,
        "integration_relation":None,
        "effects":{"assignment":0,"notification":0,"authority_change":0,"integration":0,"public_mutation":0},
        "next":"ON_SEPARATE_ACCEPTANCE_APPEND_ACCEPTED_BY_WITH_EVIDENCE__DO_NOT_REWRITE_SOURCE_LINEAGE",
        "nonclaims":["LINEAGE_NE_ACCEPTANCE","PROPOSED_NE_ACCEPTED","ATTRIBUTION_NE_OWNERSHIP","PICKED_UP_NE_INTEGRATED","NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"]
    }
    enc=(json.dumps(artifact,indent=2,ensure_ascii=False)+"\n").encode("utf-8"); out.write_bytes(enc)
    print(json.dumps({"STATE":artifact["state"],"OUTPUT":str(out),"OUTPUT_SHA256":sha256_bytes(enc),"PROCESS_ID":os.getpid(),"NEXT":artifact["next"]},separators=(",",":")))
    return 0
if __name__=="__main__": raise SystemExit(main())
