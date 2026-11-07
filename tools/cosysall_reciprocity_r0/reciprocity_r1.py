#!/usr/bin/env python3
"""CoAll <> CoSysAll source-pinned, no-actuation CV01/CV05 local acceptance.

This is a READER/PROPOSAL adapter over R0. No OS control, no network, no
self-authenticated source hash, and no automatic CoEvoDelta promotion.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any
from reciprocity import Held, qualify_graph, public_node

SCOPE = "HISTORICAL_PUBLIC_GRAPH_SNAPSHOT_ONLY"
BUDGET_MAX = 100
FEEDBACK_FIELDS = {"reason", "observation_scope"}


def graph_digest(graph: dict[str, Any]) -> str:
    """Canonical JSON digest; must compare to a trusted out-of-band expected value."""
    return hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def qualified_pinned_graph(graph: dict, expected_sha256: str) -> dict:
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or not all(c in "0123456789abcdef" for c in expected_sha256):
        raise Held("A trusted, explicit, lowercase SHA-256 pin is required")
    index = qualify_graph(graph)
    if graph_digest(graph) != expected_sha256:
        raise Held("Source graph diverges from the explicit expected SHA-256; no self-attestation")
    # This verifies bytes against the provided pin, not that the pin came from
    # an independent or trusted publisher. That trust remains an external gate.
    for node in graph["nodes"]:
        if node.get("confidentiality", "PUBLIC") not in ("PUBLIC", "PRIVATE", "RESTRICTED", "UNKNOWN"):
            raise Held("Unqualified confidentiality")
    return index


def projection_triplet(graph: dict, focus_id: str, expected_sha256: str, limit: int = 12) -> dict:
    index = qualified_pinned_graph(graph, expected_sha256)
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0 or limit > BUDGET_MAX:
        raise Held("Invalid receiver rendering budget")
    if focus_id not in index or not public_node(index[focus_id]):
        raise Held("Protected/unregistered focus")
    candidates = []
    sources = {s["id"]:s for s in graph["sources"]}
    for e in graph["edges"]:
        if focus_id not in (e["from"], e["to"]):
            continue
        other=e["to"] if e["from"]==focus_id else e["from"]
        if not public_node(index[other]):
            continue
        src = sources[e["source"]]
        candidates.append({"id":e["id"],"from":e["from"],"to":e["to"],
                           "relation":e["relation"],"epistemic_state":e["state"],
                           "source_id":e["source"],"source_url":src.get("url"),
                           "direction_from_focus":"out" if e["from"]==focus_id else "in"})
    candidates.sort(key=lambda e:(e["id"], e["from"], e["to"]))
    selected=candidates[:limit]
    node_ids=({focus_id}|{e["from"] for e in selected}|{e["to"] for e in selected}) if limit else set()
    nodes=[{"id":i,"label":index[i].get("label",i),"kind":index[i].get("kind","UNKNOWN"),"source_id":index[i]["source"]} for i in sorted(node_ids)]
    claims={"source_sha256":expected_sha256,"source_claim":SCOPE,
            "nodes":nodes,"edges":selected,"candidate_is_authority":False,
            "source_live":False,"effect_authority":False}
    signature=hashlib.sha256(json.dumps(claims,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    visual={"surface":"visual_manifest","claims":claims,"claims_sha256":signature,
            "draw_requests":len(nodes)+len(selected)}
    accessible={"surface":"accessible_list","claims":claims,"claims_sha256":signature,
                "items":[f'{index[e["from"]].get("label",e["from"])} --{e["relation"]}--> {index[e["to"]].get("label",e["to"])} [{e["epistemic_state"]}]' for e in selected],"draw_requests":0}
    machine={"surface":"machine","claims":claims,"claims_sha256":signature,"draw_requests":0}
    none={"surface":"none","source_sha256":expected_sha256,"reason":"RECEIVER_SELECTED_NO_RENDER",
          "nodes":[],"edges":[],"draw_requests":0,"effect_authority":False}
    return {"schema":"CoSysAll.ReciprocityTriplet.R1","focus_id":focus_id,
            "eligible_relations":len(candidates),"included_relations":len(selected),
            "truncated_relations":max(0,len(candidates)-len(selected)),
            "views":{"visual_manifest":visual,"accessible_list":accessible,"machine":machine,"none":none}}


def bounded_feedback(graph:dict, expected_sha256:str, from_id:str, via_id:str, to_id:str,
                     edge_ids:list[str], delta_id:str, observed_at:str, feedback:dict) -> dict:
    index=qualified_pinned_graph(graph,expected_sha256)
    if not isinstance(feedback,dict) or set(feedback)-FEEDBACK_FIELDS:
        raise Held("Feedback cannot contain authority, action, or unknown fields")
    if feedback.get("observation_scope")!="LOCAL_FIXTURE" or not isinstance(feedback.get("reason"),str) or not (5 <= len(feedback["reason"].strip()) <= 400):
        raise Held("Feedback must have bounded local observation scope and reason")
    if not isinstance(delta_id,str) or not delta_id.strip():raise Held("Stable delta ID required")
    try:
        observed=dt.datetime.fromisoformat(observed_at.replace("Z","+00:00"))
        if observed.tzinfo is None:raise ValueError("Timezone missing")
    except (ValueError,TypeError,AttributeError) as e:
        raise Held("Explicit offset-aware observation time required") from e
    if not isinstance(edge_ids,list) or len(edge_ids)!=2 or edge_ids[0]==edge_ids[1]:
        raise Held("Two distinct registered source edges are required")
    if len({from_id,via_id,to_id})!=3 or any(i not in index or not public_node(index[i]) for i in (from_id,via_id,to_id)):
        raise Held("Invalid or privacy-protected candidate path")
    edges={e["id"]:e for e in graph["edges"]}
    if any(i not in edges or edges[i]["state"]!="SOURCE_REGISTERED" for i in edge_ids):
        raise Held("Unregistered or candidate edges cannot certify a proposal")
    a,b=(edges[i] for i in edge_ids)
    # This is deliberately an undirected shared-neighbor *hypothesis*, NOT a
    # directed path. Explicit orientation is preserved for an eventual reviewer.
    if {a["from"],a["to"]}!={from_id,via_id} or {b["from"],b["to"]}!={via_id,to_id}:
        raise Held("The source does not bind the proposed shared neighbor")
    src={s["id"]:s for s in graph["sources"]}
    refs=["https://github.com/CoCivium/CoCivium/blob/main/ai/comap-source-projection-r0.json",
          "canonical-graph-sha256:"+expected_sha256]
    refs.extend(sorted(src[e["source"]].get("url",e["source"]) for e in (a,b)))
    return {"delta_id":delta_id,"session_id":"OFFLINE_FIXTURE_NO_LIVE_SESSION_ACK",
            "observed_at":observed.isoformat().replace("+00:00","Z"),
            "domain":["CoAll+","CoUX+/CoSurface+"],"subject":from_id,
            "relation":"CANDIDATE_SHARED_NEIGHBOR_WITH:"+to_id,
            "epistemic_class":"HYPOTHESIS","source_refs":refs,
            "target_surfaces":["CoMap+","CoSysAll+"],"mutation_class":"PROPOSE",
            "authority_ceiling":"NO_EXTERNAL_EFFECTS__REVIEW_ONLY", "confidentiality":"PUBLIC",
            "confidence":None,"contradictions":["Undirected shared neighbor is not a directed path, semantic equivalence, causal statement, nor permission."],
            "tests":["REGISTERED_SOURCE_EDGE:%s:%s->%s"%(e["id"],e["from"],e["to"]) for e in (a,b)]+["LOCAL_FEEDBACK_REVIEW_ONLY"],
            "expected_benefit":"Review local navigation: "+feedback["reason"].strip(),
            "risks":["Historical snapshot; no live receiver or independent reviewer", "Feedback can be mistaken or biased"],
            "wake_conditions":["Independent source-backed semantic review accepts or rejects hypothesis", "Relevant graph/currentness changes"],
            "supersedes":[],"next_receiver":"ELIGIBLE_INDEPENDENT_SEMANTIC_REVIEWER_NOT_ELECTED"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graph',required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--focus',default='domain:CoStrategy+')
    p.add_argument('--limit',type=int,default=12)
    p.add_argument('--feedback',help='JSON file with reason + observation_scope=LOCAL_FIXTURE')
    p.add_argument('--from-id',default='repo:CoCivium/MasterPlan')
    p.add_argument('--via-id',default='domain:CoStrategy+')
    p.add_argument('--to-id',default='repo:CoCivium/CoCivium')
    p.add_argument('--edge-a',default='e1');p.add_argument('--edge-b',default='e2')
    p.add_argument('--delta-id',default='candidate:cosysall-reciprocity-r1')
    p.add_argument('--observed-at',help='Offset-aware ISO timestamp, required with --feedback')
    a=p.parse_args()
    graph=json.loads(Path(a.graph).read_text(encoding='utf-8'))
    try:
        result=bounded_feedback(graph,a.expected_sha256,a.from_id,a.via_id,a.to_id,[a.edge_a,a.edge_b],a.delta_id,a.observed_at,json.loads(Path(a.feedback).read_text())) if a.feedback else projection_triplet(graph,a.focus,a.expected_sha256,a.limit)
    except Held as e:p.exit(2,'HELD: '+str(e)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False))

if __name__=='__main__': main()