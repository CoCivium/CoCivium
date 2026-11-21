#!/usr/bin/env python3
"""CoRel / CoBraid R0: deterministic review-only braid from explicit dependencies.

This is a single-pass logical planning projection, not a task runner. It uses
typed *review prerequisites* and never infers an execution dependency from
a causal-looking or noncausal relation alone. All "verified" sources in input
are caller-provided claims until a separate reader checks exact bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "CoRel.CoBraid.LogicalReviewWave.R0"
STATES = {"OPEN", "VERIFIED_SOURCE", "HELD"}
WORK_CLASSES = {"READ_ONLY", "SHADOW", "EFFECT_GATED"}
CAUSAL = {"causal", "non_causal", "possibly_causal", "mixed", "unknown"}
PREDICATES = {"REVIEW_DEPENDS_ON", "CAUSES", "POSSIBLY_CAUSES",
              "RELATED_TO", "CHALLENGES", "INVERTS", "PRECEDES"}
WORK_KEYS = {"work_id", "state", "work_class", "collision_domain",
             "source_sha256", "receipt_sha256"}
REL_KEYS = {"rel_id", "subject", "predicate", "object",
            "causal_status", "provenance"}
TOP_KEYS = {"schema", "scope", "max_parallel", "work", "relations"}
MAX_WORK = 32
MAX_RELATIONS = 96
NONCLAIMS = (
    "PLAN_NE_EXECUTION",
    "PARALLEL_LANES_NE_RUNNING_PROCESSES",
    "CAUSES_RELATION_NE_EXECUTION_DEPENDENCY",
    "REVIEW_DEPENDS_ON_NE_REAL_WORLD_CAUSATION",
    "SOURCE_RECEIPT_CLAIM_NE_INDEPENDENT_READBACK",
    "LOGICAL_COMPLETION_NE_RECEIVER_PICKUP",
    "SHADOW_PREVIEW_NE_EFFECT_AUTHORITY",
    "NO_RICK_PROMPT_NE_ALWAYS_ON_RUNTIME",
    "NO_CANON_NO_COEX_NO_PUBLIC_RELEASE",
)

class Hold(ValueError):
    pass

def _id(x):
    return isinstance(x,str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}",x) is not None

def _sha(x):
    return isinstance(x,str) and re.fullmatch(r"[0-9a-f]{64}",x) is not None

def _validate(obj):
    if not isinstance(obj,dict) or set(obj)!=TOP_KEYS or obj.get("schema")!=SCHEMA:
        raise Hold("HELD_CONTRACT_SCHEMA")
    if obj["scope"] != "SYNTHETIC_PUBLIC_ONLY":
        raise Hold("HELD_UNQUALIFIED_SCOPE")
    if type(obj["max_parallel"]) is not int or not 1<=obj["max_parallel"]<=4:
        raise Hold("HELD_UNBOUNDED_FANOUT")
    rows=obj["work"];edges=obj["relations"]
    if not isinstance(rows,list) or not 1<=len(rows)<=MAX_WORK:
        raise Hold("HELD_WORK_BOUND")
    if not isinstance(edges,list) or len(edges)>MAX_RELATIONS:
        raise Hold("HELD_RELATION_BOUND")
    work={}
    for w in rows:
        if not isinstance(w,dict) or set(w)!=WORK_KEYS:
            raise Hold("HELD_UNKNOWN_WORK_FIELDS")
        if not _id(w["work_id"]) or w["work_id"] in work:
            raise Hold("HELD_DUPLICATE_OR_INVALID_WORK_ID")
        if w["state"] not in STATES or w["work_class"] not in WORK_CLASSES:
            raise Hold("HELD_INVALID_WORK_STATE")
        if not _id(w["collision_domain"]):
            raise Hold("HELD_INVALID_COLLISION_DOMAIN")
        if w["state"]!="HELD" and not _sha(w["source_sha256"]):
            raise Hold("HELD_MISSING_SOURCE_PROOF_CLAIM")
        if w["state"]=="VERIFIED_SOURCE" and not _sha(w["receipt_sha256"]):
            raise Hold("HELD_MISSING_COMPLETION_RECEIPT_CLAIM")
        if w["state"]!="VERIFIED_SOURCE" and w["receipt_sha256"] is not None:
            raise Hold("HELD_RECEIPT_WITHOUT_VERIFIED_STATE")
        if w["source_sha256"] is not None and not _sha(w["source_sha256"]):
            raise Hold("HELD_BAD_SOURCE_DIGEST")
        work[w["work_id"]]=w
    relids=set()
    dep={key:set() for key in work}
    narrative=[]
    for edge in edges:
        if not isinstance(edge,dict) or set(edge)!=REL_KEYS:
            raise Hold("HELD_UNKNOWN_RELATION_FIELDS")
        rid=edge["rel_id"];subject=edge["subject"];other=edge["object"]
        if not _id(rid) or rid in relids:
            raise Hold("HELD_DUPLICATE_OR_INVALID_RELATION")
        relids.add(rid)
        if not _id(subject) or not _id(other) or subject not in work or other not in work:
            raise Hold("HELD_DANGLING_OR_RELATION_AS_WORK_ENDPOINT")
        if edge["predicate"] not in PREDICATES or edge["causal_status"] not in CAUSAL:
            raise Hold("HELD_UNKNOWN_PREDICATE_OR_CAUSAL_STATUS")
        prov=edge["provenance"]
        if not isinstance(prov,list) or not prov or len(prov)>8 or any(not _id(p) for p in prov):
            raise Hold("HELD_RELATION_PROVENANCE_REQUIRED")
        if edge["predicate"]=="REVIEW_DEPENDS_ON":
            if subject==other:
                raise Hold("HELD_SELF_DEPENDENCY")
            dep[subject].add(other)
        else:
            narrative.append(rid)
    return work,dep,tuple(sorted(narrative))

def _cycle_nodes(dependencies):
    """Return all nodes in actual directed cycles, not their dependents."""
    def reaches(start,current,visited):
        for n in dependencies[current]:
            if n==start:
                return True
            if n not in visited and reaches(start,n,visited|{n}):
                return True
        return False
    return {n for n in dependencies if reaches(n,n,{n})}

def plan(snapshot):
    work,dep,narrative=_validate(snapshot)
    cycles=_cycle_nodes(dep)
    blocked={}
    for wid,w in work.items():
        if w["state"]=="VERIFIED_SOURCE":
            continue
        if w["state"]=="HELD":
            blocked[wid]="HELD_SOURCE_OR_AUTHORITY"
        elif wid in cycles:
            blocked[wid]="HELD_REVIEW_DEPENDENCY_CYCLE"
    # A downstream branch is blocked if any prerequisite is held or circular.
    changed=True
    while changed:
        changed=False
        for wid in sorted(work):
            if wid in blocked or work[wid]["state"]=="VERIFIED_SOURCE":
                continue
            if any(d in blocked for d in dep[wid]):
                blocked[wid]="HELD_PREREQUISITE"
                changed=True
    ready=[]
    waiting=[]
    for wid in sorted(work):
        if work[wid]["state"]=="VERIFIED_SOURCE" or wid in blocked:
            continue
        if all(work[d]["state"]=="VERIFIED_SOURCE" for d in dep[wid]):
            ready.append(wid)
        else:
            waiting.append(wid)
    # Equal collision domains cannot share a logical parallel tranche.
    batch=[]
    used=set()
    deferred=[]
    for wid in ready:
        collision=work[wid]["collision_domain"]
        if len(batch)>=snapshot["max_parallel"] or collision in used:
            deferred.append(wid)
            continue
        used.add(collision)
        batch.append(wid)
    groups=[
        {"work_id":wid,
         "review_lane":"SHADOW_ONLY_NO_EFFECT_LEASE" if work[wid]["work_class"]=="EFFECT_GATED" else "READ_ONLY_LOGICAL_PREVIEW",
         "collision_domain":work[wid]["collision_domain"],
         "declared_prerequisites":sorted(dep[wid]),
         "source_sha256_claim":work[wid]["source_sha256"]}
        for wid in batch
    ]
    input_identity=hashlib.sha256(
        json.dumps(snapshot,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema":"CoRel.CoBraid.LogicalReviewWaveReceipt.R0",
        "state":"LOGICAL_REVIEW_PLAN_NOT_EXECUTED",
        "input_sha256":input_identity,
        "parallel_review_candidates":groups,
        "ready_but_deferred":deferred,
        "waiting_for_declared_source_receipts":waiting,
        "held":dict(sorted(blocked.items())),
        "already_source_verified_claims":sorted(
            wid for wid in work if work[wid]["state"]=="VERIFIED_SOURCE"),
        "actual_cycle_nodes":sorted(cycles),
        "nonordering_relation_ids":list(narrative),
        "logical_worker_count":len(groups),
        "executed_worker_count":0,
        "mutations":0,
        "external_effect_count":0,
        "receiver_ack":False,
        "source_bytes_refetched":False,
        "physical_scheduler_used":False,
        "nonclaims":NONCLAIMS,
    }

def main():
    ap=argparse.ArgumentParser(description="Read-only bounded CoRel/CoBraid logical next-review wave")
    ap.add_argument("--snapshot",type=Path,required=True)
    args=ap.parse_args()
    try:
        path=args.snapshot
        if path.is_symlink() or not path.is_file() or path.stat().st_size>80_000:
            raise Hold("HELD_SNAPSHOT_FILE_BOUNDARY")
        snapshot=json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps(plan(snapshot),sort_keys=True))
    except (Hold,OSError,UnicodeError,TypeError,ValueError) as error:
        state=str(error) if isinstance(error,Hold) else "HELD_INVALID_OR_UNREADABLE_SNAPSHOT"
        print(json.dumps({"state":state,"external_effect_count":0,"receiver_ack":False}))
        raise SystemExit(2)

if __name__=="__main__":
    main()
