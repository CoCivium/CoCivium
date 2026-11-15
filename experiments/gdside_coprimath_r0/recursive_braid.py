"""CoGoldenBraid R0: bounded typed relation traversal, synthetic only.

Not a causal engine, welfare oracle, or real allocator. A reachable need is
not automatically valid: the caller must compare claimed edges to evidence.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Iterable

SIDES = frozenset({"supply", "demand", "gdside"})
RELATIONS = frozenset({"enables", "needs", "threatens", "suggests"})
MAX_DEPTH = 3
MAX_NODES = 48

@dataclass(frozen=True)
class Node:
    id: str
    side: str
    source: str

@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    relation: str
    source: str
    observed: bool = False  # not a guarantee of causality

def query(nodes: Iterable[Node], edges: Iterable[Edge], *, roots: set[str],
          max_depth: int, budget: int = 48) -> dict:
    ns = list(nodes)
    es = list(edges)
    if not 0 <= max_depth <= MAX_DEPTH or not 1 <= budget <= MAX_NODES:
        raise ValueError("BOUNDED_QUERY_REQUIRED")
    ids = [n.id for n in ns]
    if len(ids) != len(set(ids)) or len(ns) > MAX_NODES:
        raise ValueError("DUPLICATE_OR_EXCESS_NODES")
    if any(n.side not in SIDES or not n.source or not n.id for n in ns):
        raise ValueError("INVALID_NODE")
    if not roots or not roots.issubset(ids):
        raise ValueError("INVALID_ROOTS")
    if any(e.src not in ids or e.dst not in ids or e.relation not in RELATIONS
           or not e.source for e in es):
        raise ValueError("UNBOUND_OR_INVALID_EDGE")
    adj = {k: [] for k in ids}
    for edge in es:
        adj[edge.src].append(edge)
    queue = deque((root, 0) for root in sorted(roots))
    found = set()
    used = []
    while queue:
        if len(found) >= budget:
            break
        node, depth = queue.popleft()
        if node in found:
            continue
        found.add(node)
        if depth == max_depth:
            continue
        for e in sorted(adj[node], key=lambda e: (e.dst, e.relation)):
            used.append(e)
            if e.dst not in found:
                queue.append((e.dst, depth + 1))
    return {
        "nodes": sorted(found),
        "edges": [(e.src, e.relation, e.dst, e.source) for e in used],
        "budget_exhausted": len(found) >= budget and bool(queue),
        "evidence_warning": "REACHABILITY_NOT_CAUSATION_OR_VALUE",
        "runtime_authority": False,
    }

def compare_fixture(include_false_edge: bool = False) -> dict:
    """Same declared inputs and budget, flat 1 hop vs braid 2 hops.

    Controlled synthetic world. 'Hidden need' is defined externally as need_y,
    not selected by the algorithm. A false edge is a known negative control.
    """
    nodes = [
        Node("resource_x", "supply", "fixture:stock"),
        Node("service_x", "supply", "fixture:capacity"),
        Node("need_y", "demand", "fixture:unheard_need"),
        Node("future_z", "gdside", "fixture:optional_regeneration"),
        Node("decoy_w", "demand", "fixture:known_false_need"),
    ]
    edges = [
        Edge("resource_x", "service_x", "enables", "fixture:engineering"),
        Edge("service_x", "need_y", "needs", "fixture:survey"),
        Edge("need_y", "future_z", "suggests", "fixture:forecast"),
    ]
    if include_false_edge:
        edges.append(Edge("service_x", "decoy_w", "suggests", "fixture:false_edge"))
    flat = query(nodes, edges, roots={"resource_x"}, max_depth=1)
    braid = query(nodes, edges, roots={"resource_x"}, max_depth=2)
    true_positive = "need_y" in braid["nodes"]
    false_positive = "decoy_w" in braid["nodes"]
    return {
        "flat_retrieves_unheard_need": "need_y" in flat["nodes"],
        "braid_retrieves_unheard_need": true_positive,
        "braid_false_positive": false_positive,
        "flat": flat,
        "braid": braid,
        "synthetic_only": True,
        "independent_receiver_ack": False,
    }
