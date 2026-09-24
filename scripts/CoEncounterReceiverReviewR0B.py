#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


COST_RANK={"LOW":0,"MEDIUM":1,"HIGH":2}
CURRENT={"CURRENT"}
OBSERVE_AUTHORITIES={"OBSERVE_ONLY","OBSERVE_AND_PROPOSE_ONLY","PROPOSE_ONLY"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_obj(path: Path) -> tuple[dict[str, Any], bytes]:
    raw=path.read_bytes()
    obj=json.loads(raw.decode("utf-8"))
    if not isinstance(obj,dict):
        raise ValueError(f"expected object: {path}")
    return obj,raw


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--encounters",required=True)
    ap.add_argument("--receivers",required=True)
    ap.add_argument("--receiver-id",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    out=Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    encounters,enc_raw=load_obj(Path(args.encounters).resolve())
    receivers,rec_raw=load_obj(Path(args.receivers).resolve())

    rows=list(encounters.get("encounters") or [])
    pool=list(receivers.get("receivers") or [])
    receiver=next((r for r in pool if r.get("receiver_id")==args.receiver_id),None)
    if receiver is None:
        raise SystemExit("FAIL_CLOSED__RECEIVER_NOT_FOUND")

    required=["receiver_id","receiver_class","capabilities","relation_interests","authority_classes",
              "consent_to_candidate_deeds","cost_class","max_acceptable_cost_class","currentness"]
    missing=[k for k in required if k not in receiver]
    if missing:
        raise SystemExit("FAIL_CLOSED__RECEIVER_FIELDS="+",".join(missing))

    if receiver["cost_class"] not in COST_RANK or receiver["max_acceptable_cost_class"] not in COST_RANK:
        raise SystemExit("FAIL_CLOSED__COST_CLASS")

    reviews=[]
    routes=[]
    for e in rows:
        eid=str(e.get("encounter_id") or "")
        if not eid:
            raise SystemExit("FAIL_CLOSED__ENCOUNTER_ID")
        public_safe=e.get("confidentiality")=="PUBLIC"
        can_observe=bool(set(receiver["authority_classes"]) & OBSERVE_AUTHORITIES)
        current_ok=receiver["currentness"] in CURRENT
        review_state="REVIEWED_BOUNDED_STRUCTURE" if (public_safe and can_observe and current_ok) else "HELD"
        held=[]
        if not public_safe: held.append("NONPUBLIC_ENCOUNTER")
        if not can_observe: held.append("NO_OBSERVE_AUTHORITY")
        if not current_ok: held.append("STALE_OR_UNKNOWN_CURRENTNESS")
        reviews.append({
            "encounter_id":eid,
            "receiver_id":receiver["receiver_id"],
            "review_state":review_state,
            "held_reasons":held,
            "yield_count":len(e.get("yields") or []),
            "open_relation_count":len(e.get("open_relations") or []),
            "semantic_acceptance":"NOT_PROVEN",
            "truth_disposition":"NOT_EVALUATED",
            "authority_change":False,
            "nonclaims":[
                "STRUCTURAL_REVIEW_NE_SEMANTIC_ACCEPTANCE",
                "REVIEW_NE_TRUTH",
                "SENSING_SCALE_NE_AUTHORITY_SCALE"
            ]
        })

        for rel in list(e.get("open_relations") or []):
            rid=str(rel.get("relation_id") or "")
            capability_hint=rel.get("capability_hint")
            capability_match=(capability_hint in receiver["capabilities"]) if capability_hint is not None else True
            interest_match=rid in receiver["relation_interests"]
            consent_ok=bool(receiver["consent_to_candidate_deeds"])
            authority_ok=str(rel.get("authority_required")) in set(receiver["authority_classes"])
            cost_ok=COST_RANK[receiver["cost_class"]] <= COST_RANK[receiver["max_acceptable_cost_class"]]
            currentness_ok=receiver["currentness"]=="CURRENT"
            status_open=rel.get("status")=="OPEN"
            gates={
                "status_open":status_open,
                "capability_match":capability_match,
                "interest_match":interest_match,
                "consent_ok":consent_ok,
                "authority_ok":authority_ok,
                "cost_ok":cost_ok,
                "currentness_ok":currentness_ok,
            }
            eligible=all(gates.values())
            held_reasons=[k for k,v in gates.items() if not v]
            routes.append({
                "relation_id":rid,
                "encounter_id":eid,
                "receiver_id":receiver["receiver_id"],
                "route_state":"MATCH_CANDIDATE" if eligible else "HELD",
                "gates":gates,
                "held_reasons":held_reasons,
                "candidate_deed":{
                    "deed_class":"PROPOSE_OPEN_RELATION_TRANSFORMATION",
                    "need":rel.get("need"),
                    "effect_authority":"NONE",
                    "execution_authorized":False
                } if eligible else None,
                "assignment_executed":False,
                "notification_executed":False,
                "authority_change":False,
                "nonclaims":[
                    "MATCH_NE_ASSIGNMENT_AUTHORITY",
                    "AVAILABLE_CAPABILITY_NE_FREE_COMPUTE",
                    "ROUTE_CANDIDATE_NE_RECEIVER_ACCEPTANCE"
                ]
            })

    artifact={
        "schema":"CoEncounterIndependentReview.R0B.v0.1-candidate",
        "state":"BOUNDED_RECEIVER_REVIEW_COMPLETE__OPEN_RELATION_MATCH_CANDIDATES_ONLY",
        "receiver":{
            "receiver_id":receiver["receiver_id"],
            "receiver_class":receiver["receiver_class"],
            "process_id":os.getpid(),
            "currentness":receiver["currentness"],
            "cost_class":receiver["cost_class"],
        },
        "source_bindings":{
            "encounter_fixture_sha256":sha256_bytes(enc_raw),
            "receiver_fixture_sha256":sha256_bytes(rec_raw),
        },
        "reviews":reviews,
        "open_relation_routes":routes,
        "effects":{
            "assignments":0,
            "notifications":0,
            "authority_changes":0,
            "repo_mutations":0,
            "provider_session_mutations":0
        },
        "next":"INDEPENDENT_FANIN_AND_EXACT_ROUTE_PACKET_READPROOF",
        "nonclaims":[
            "REVIEW_NE_ACCEPTANCE",
            "MATCH_NE_ASSIGNMENT_AUTHORITY",
            "ROUTE_CANDIDATE_NE_PICKUP",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
        ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    enc=(json.dumps(artifact,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(enc)
    print(json.dumps({
        "STATE":artifact["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(enc),
        "RECEIVER_ID":receiver["receiver_id"],
        "PROCESS_ID":artifact["receiver"]["process_id"],
        "REVIEWS":len(reviews),
        "ROUTES":len(routes),
        "MATCH_CANDIDATES":sum(1 for x in routes if x["route_state"]=="MATCH_CANDIDATE"),
        "NEXT":artifact["next"]
    },separators=(",",":")))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
