"""CoOmniPath R0: evidence-safe bidirectional discovery over explicit CoSeed graph.

Reverse traversal is for finding *who references me*, not for inverting the
meaning of a predicate or granting permission to mutate a source.
No provider sessions are contacted and no source is semantically integrated.
"""
from collections import deque
from pathlib import Path
import json


def load_registry(path=None):
    source = Path(path) if path else Path(__file__).with_name("co_seed_path_registry_r0.json")
    return json.loads(source.read_text(encoding="utf-8"))


def neighbors(registry, seed_id, *, directions=("out", "in"), max_hops=2,
              allowed_scopes=("PUBLIC",), max_results=40):
    """Bounded graph exploration with explicit orientation and provenance."""
    if max_hops < 0 or max_results < 1:
        raise ValueError("invalid bound")
    if not set(directions).issubset({"out", "in"}) or not directions:
        raise ValueError("direction must be out and/or in")
    nodes = {node["id"]: node for node in registry["nodes"]}
    if seed_id not in nodes:
        return {"seed_id": seed_id, "status": "UNKNOWN_SEED", "paths": [],
                "unvisited": None, "receiver_pickup_proven": False}
    if nodes[seed_id]["scope"] not in allowed_scopes:
        return {"seed_id": seed_id, "status": "SCOPE_HELD", "paths": [],
                "unvisited": None, "receiver_pickup_proven": False}
    graph = {key: [] for key in nodes}
    for edge in registry["edges"]:
        a, b = edge["from"], edge["to"]
        if a not in nodes or b not in nodes:
            raise ValueError("unresolved edge")
        # Direction of the source relation is retained in both traversals.
        if "out" in directions:
            graph[a].append((b, edge["predicate"], "OUTBOUND_SOURCE_RELATION"))
        if "in" in directions:
            graph[b].append((a, edge["predicate"], "INBOUND_REFERENCE_ONLY"))
    queue = deque([(seed_id, 0, ())])
    visited = {seed_id}
    paths = []
    truncated = False
    while queue:
        node, depth, hops = queue.popleft()
        if depth >= max_hops:
            continue
        for target, predicate, orientation in sorted(graph[node]):
            if target in visited or nodes[target]["scope"] not in allowed_scopes:
                continue
            if len(paths) >= max_results:
                truncated = True
                break
            visited.add(target)
            new_path = hops + ((node, target, predicate, orientation),)
            paths.append({
                "node_id": target,
                "source_path": nodes[target]["path"],
                "git_blob_sha1": nodes[target]["git_blob_sha1"],
                "front": nodes[target]["front"],
                "distance": depth + 1,
                "relation_trail": [
                    {"from": a, "to": b, "source_predicate": p,
                     "traversal_role": role}
                    for a, b, p, role in new_path
                ],
                "verified_receiver_accepted": False,
            })
            queue.append((target, depth + 1, new_path))
        if truncated:
            break
    return {"seed_id": seed_id, "status": "SOURCE_GRAPH_TRAVERSAL_ONLY",
            "paths": paths, "unvisited": "POSSIBLE" if truncated else "NOT_ASSERTED",
            "receiver_pickup_proven": False,
            "semantic_integration_proven": False,
            "full_history_covered": False}


def hypothesis_link(source_id, target_id, *, rationale, falsifier, evidence_ref=""):
    """Non-operational speculative relation. Never a proof edge."""
    if not source_id or not target_id or not rationale or not falsifier:
        return {"status": "HELD", "reason": "MISSING_HYPOTHESIS_BOUNDARY"}
    return {"from": source_id, "to": target_id, "kind": "HYPOTHESIS",
            "rationale": rationale, "falsifier": falsifier,
            "evidence_ref": evidence_ref or None, "authority": "NONE",
            "promote_to_verified_edge": False}
