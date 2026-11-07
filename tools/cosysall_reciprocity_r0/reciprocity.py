#!/usr/bin/env python3
"""CoSysAll+ <-> CoAll R0: local, source-bound, non-actuating bridge.

Accepts an existing CoMap graph snapshot, projects it for a nonvisual receiver,
then produces CoEvoDelta PROPOSE packets from candidate two-hop relations.
No network, persistent state, authority mutation, or automatic promotion.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

GRAPH_SCHEMA = "CoAll.CoMapProjection.R0"
GRAPH_STATE = "PUBLIC_SOURCE_BOUND_PROJECTION_NOT_CANON_OR_RUNTIME"
EPISTEMIC = "HYPOTHESIS"
AUTHORITY = "NO_EXTERNAL_EFFECTS__REVIEW_ONLY"
MAX_ITEMS = 100

class Held(ValueError):
    """Unqualified source, privacy, path, or proposed effect: fail closed."""


def _ids_unique(items: list[dict], key: str) -> bool:
    values = [x.get(key) for x in items]
    return all(isinstance(x, str) and bool(x) for x in values) and len(set(values)) == len(values)


def qualify_graph(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if graph.get("schema") != GRAPH_SCHEMA or graph.get("state") != GRAPH_STATE:
        raise Held("Unqualified graph schema or provenance state")
    nodes, edges, sources = [graph.get(k) for k in ("nodes", "edges", "sources")]
    if not all(isinstance(v, list) for v in (nodes, edges, sources)):
        raise Held("Missing structured node/edge/source registry")
    if not all(_ids_unique(v, "id") for v in (nodes, edges, sources)):
        raise Held("Duplicate or missing source graph identifiers")
    node_index = {v["id"]: v for v in nodes}
    source_ids = {v["id"] for v in sources}
    for node in nodes:
        if node.get("source") not in source_ids:
            raise Held("Unbound node source: " + str(node.get("id")))
    for edge in edges:
        if edge.get("from") not in node_index or edge.get("to") not in node_index:
            raise Held("Dangling relation")
        if edge.get("source") not in source_ids:
            raise Held("Unbound relation source")
        if edge.get("state") not in ("SOURCE_REGISTERED", "CONTEXTUAL_LINK", "CANDIDATE"):
            raise Held("Unqualified relation state")
    return node_index


def public_node(node: dict) -> bool:
    """No secret/private payloads. Publicly registered *repo names* remain names."""
    return node.get("confidentiality", "PUBLIC") == "PUBLIC" and node.get("privacy", "PUBLIC") == "PUBLIC"


def project(graph: dict, focus_id: str, surface: str = "machine", limit: int = 20) -> dict:
    index = qualify_graph(graph)
    if surface not in ("machine", "accessible_list", "none"):
        raise Held("Renderer not available; use an existing visual viewer")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= MAX_ITEMS:
        raise Held("Invalid rendering budget")
    if focus_id not in index or not public_node(index[focus_id]):
        raise Held("Unknown, protected or unavailable focus")
    neighbors = []
    for e in graph["edges"]:
        if e["from"] == focus_id or e["to"] == focus_id:
            candidate = e["to"] if e["from"] == focus_id else e["from"]
            if not public_node(index[candidate]):
                continue
            neighbors.append({"node_id": candidate, "edge_id": e["id"], "relation": e["relation"], "edge_state": e["state"], "direction": "out" if e["from"] == focus_id else "in"})
    neighbors.sort(key=lambda e:(e["node_id"],e["edge_id"]))
    # "none" does not request payload/detail; even accessible metadata is suppressed.
    result = {"schema":"CoSysAll.CoAllReciprocity.R0", "source_schema": GRAPH_SCHEMA,
              "source_claim": GRAPH_STATE, "focus_id": focus_id, "surface":surface,
              "eligible_neighbors":len(neighbors),"planned_visible_nodes":0,
              "actual_draw_calls":0,"network_fetches":0,
              "source_snapshot_live":False,"grants_effect_authority":False,
              "mode":"LOCAL_PROJECTION_ONLY"}
    if surface == "none":
        result.update({"reason":"USER_OR_RECEIVER_REQUESTED_NO_RENDER", "nodes":[], "relations":[]})
    else:
        selected = neighbors[:limit]
        seen = ({focus_id} | {x["node_id"] for x in selected}) if limit > 0 else set()
        # Whitelist public projection fields; never forward arbitrary source properties.
        result["nodes"] = [{"id":i,"label":index[i].get("label",i),"kind":index[i].get("kind","UNKNOWN") } for i in sorted(seen)]
        result["relations"] = selected
        result["planned_visible_nodes"] = len(seen)
        result["truncated_relations"] = max(0,len(neighbors)-len(selected))
    return result


def make_proposal(graph: dict, from_id: str, via_id: str, to_id: str,
                  edge_a: str, edge_b: str, delta_id: str, observed_at: str) -> dict:
    index=qualify_graph(graph)
    # Date is an observed emission timestamp supplied by the caller, not source freshness.
    try:
        observed=dt.datetime.fromisoformat(observed_at.replace("Z","+00:00"))
        if observed.tzinfo is None: raise ValueError("timezone missing")
    except (TypeError, ValueError) as exc:
        raise Held("Observation time must be an offset-aware ISO 8601 timestamp") from exc
    if not isinstance(delta_id,str) or not delta_id.strip():
        raise Held("Stable delta ID required")
    if any(i not in index for i in (from_id,via_id,to_id)):
        raise Held("Unknown CoAll/CoSysAll object")
    if any(not public_node(index[i]) for i in (from_id,via_id,to_id)):
        raise Held("Protected/unknown privacy object: no public proposal")
    if len({from_id,via_id,to_id}) != 3 or edge_a==edge_b:
        raise Held("Need a distinct source-backed two-hop path")
    edges={e["id"]:e for e in graph["edges"]}
    if edge_a not in edges or edge_b not in edges:
        raise Held("An unregistered edge cannot prove a path")
    x,y=edges[edge_a],edges[edge_b]
    if x["state"] != "SOURCE_REGISTERED" or y["state"] != "SOURCE_REGISTERED":
        raise Held("Candidate/contextual edges cannot certify new proposals")
    if {x["from"],x["to"]}!={from_id,via_id} or {y["from"],y["to"]}!={via_id,to_id}:
        raise Held("Edge directions/subjects do not establish proposed two-hop path")
    src_ids={x["source"], y["source"]}
    source_map={s["id"]:s for s in graph["sources"]}
    canonical_graph = json.dumps(graph, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    source_digest = hashlib.sha256(canonical_graph).hexdigest()
    refs=["https://github.com/CoCivium/CoCivium/blob/main/ai/comap-source-projection-r0.json", "canonical-graph-sha256:"+source_digest]
    refs.extend(sorted(source_map[i].get("url",i) for i in src_ids))
    # Strictly existing CoEvoDelta v0.1 fields; no promotion, receiver ACK, or effect claim.
    return {"delta_id":delta_id,"session_id":"OFFLINE_FIXTURE_NO_LIVE_SESSION_ACK",
            "observed_at":observed.isoformat().replace("+00:00","Z"),
            "domain":["CoAll+","CoUX+/CoSurface+"],"subject":from_id,
            "relation":"CANDIDATE_CONTEXTUAL_PATH_TO:"+to_id,
            "epistemic_class":EPISTEMIC,"source_refs":refs,
            "target_surfaces":["CoMap+","CoSysAll+"],"mutation_class":"PROPOSE",
            "authority_ceiling":AUTHORITY,"confidentiality":"PUBLIC",
            "confidence":None,
            "contradictions":["Two-hop proximity does not prove an independent relation, shared meaning, causal connection or permission."],
            "tests":["SOURCE_REGISTERED_EDGES:"+edge_a,"SOURCE_REGISTERED_EDGES:"+edge_b,"TWO_HOP_PATH_STRUCTURAL_ONLY"],
            "expected_benefit":"Candidate source-bound relationship for independent review and useful-view testing, not an automatic CoAll update",
            "risks":["Conflation of source association with verified relation or authority","Historical snapshot may be stale"],
            "wake_conditions":["Qualified independent reviewer verifies a new source-backed relation", "Actual source/currentness change"],
            "supersedes":[],"next_receiver":"ELIGIBLE_INDEPENDENT_SEMANTIC_REVIEWER_NOT_ELECTED"}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph",required=True,help="Source-controlled ai/comap-source-projection-r0.json")
    ap.add_argument("--surface",choices=["machine","accessible_list","none"],default="machine")
    ap.add_argument("--focus",default="domain:CoStrategy+")
    ap.add_argument("--limit",type=int,default=20)
    ap.add_argument("--propose",nargs=5,metavar=("FROM","VIA","TO","EDGE_A","EDGE_B"))
    ap.add_argument("--delta-id",default="candidate:cosysall-source-path-r0")
    ap.add_argument("--observed-at",default=None,help="Required for a proposal; explicit time, never silently use old fixture time")
    ns=ap.parse_args()
    graph=json.loads(Path(ns.graph).read_text(encoding="utf-8"))
    try:
        result=make_proposal(graph,*ns.propose,ns.delta_id,ns.observed_at) if ns.propose else project(graph,ns.focus,ns.surface,ns.limit)
    except Held as e:
        ap.exit(2,"HELD: "+str(e)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":main()