#!/usr/bin/env python3
"""Bounded CoPre discovery over the EXISTING public graph. Read-only.

Reverse traversal is a navigation perspective, never reciprocal permissions,
evidence, communication, or effects. The graph is a partial public corpus.
"""
from __future__ import annotations
import argparse
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "ai/copre-seed-path-fabric-r0-20261109.json"
MAX_HOPS = 12

def index_graph(obj):
    nodes = obj.get("nodes")
    if not isinstance(nodes, list) or not nodes or len(nodes) > 1000:
        raise ValueError("INVALID_GRAPH_SIZE")
    forward = {}
    reverse = {}
    for item in nodes:
        if not isinstance(item, dict):
            raise ValueError("INVALID_NODE")
        ident = item.get("id")
        rels = item.get("relations")
        if not isinstance(ident, str) or not ident or ident in forward:
            raise ValueError("INVALID_OR_DUPLICATE_NODE_ID")
        if not isinstance(rels, list) or len(rels) > 200 or not all(isinstance(x, str) for x in rels):
            raise ValueError("INVALID_RELATIONS")
        forward[ident] = sorted(set(rels))
        reverse[ident] = []
    for origin, rels in forward.items():
        for target in rels:
            if target not in forward:
                raise ValueError("DANGLING_GRAPH_LINK:"+target)
            reverse[target].append(origin)
    for values in reverse.values():
        values.sort()
    return forward, reverse

def discover(obj, start, goal, *, direction="both", max_hops=8):
    if direction not in {"forward","reverse","both"} or type(max_hops) is not int or not 0<=max_hops<=MAX_HOPS:
        raise ValueError("INVALID_TRAVERSAL")
    forward, reverse = index_graph(obj)
    if start not in forward or goal not in forward:
        raise ValueError("UNKNOWN_NODE")
    q = deque([(start, [start])])
    visited = {start}
    while q:
        here, path = q.popleft()
        if here == goal:
            return {"status":"NAVIGABLE_SOURCE_POINTER_ONLY", "path":path,
                    "hops":len(path)-1, "direction":direction,
                    "authority_granted":False, "source_verification":False,
                    "recipient_ack":False, "integration":False}
        if len(path)-1 >= max_hops:
            continue
        choices = set()
        if direction in ("forward","both"):
            choices.update(forward[here])
        if direction in ("reverse","both"):
            choices.update(reverse[here])
        for next_id in sorted(choices):
            if next_id not in visited:
                visited.add(next_id)
                q.append((next_id, path+[next_id]))
    return {"status":"HELD_NO_ROUTE_WITHIN_BUDGET", "path":None,
            "hops":None, "direction":direction,
            "authority_granted":False,"source_verification":False,
            "recipient_ack":False,"integration":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("start")
    ap.add_argument("goal")
    ap.add_argument("--direction",choices=("forward","reverse","both"),default="both")
    ap.add_argument("--max-hops",type=int,default=8)
    ap.add_argument("--graph",type=Path,default=GRAPH)
    args=ap.parse_args()
    obj=json.loads(args.graph.read_text(encoding="utf-8"))
    print(json.dumps(discover(obj,args.start,args.goal,direction=args.direction,max_hops=args.max_hops),indent=2))

if __name__=="__main__":
    main()
