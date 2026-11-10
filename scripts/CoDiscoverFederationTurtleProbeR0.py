#!/usr/bin/env python3
"""CoDiscover+ CoFed/CoTurtle/CoInverse R0: public-safe graph probe.

Synthetic declarations only. Traverse nested discoverable systems/federations
without treating discoverability as membership, consent, trust or execution.
Never output private node identifiers, edges or contents. No network, writes,
worker spawning, controller registration or provider actions.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
import re

SCHEMA = "CoDiscover.FederatedDiscoveryFixture.R0"
OUTPUT_SCHEMA = "CoDiscover.FederatedView.R0"
CLASSES = {"FEDERATION", "SYSTEM", "SUBSTRATE"}
RELATIONS = {"DISCOVERS", "DISCOVERED_BY", "PEERS_WITH",
             "CONTAINS", "MEMBER_OF"}
INVERSE = {
    "DISCOVERS": "DISCOVERED_BY",
    "DISCOVERED_BY": "DISCOVERS",
    "PEERS_WITH": "PEERS_WITH",
    "CONTAINS": "MEMBER_OF",
    "MEMBER_OF": "CONTAINS",
}
IDENTIFIER = re.compile(r"^(fed|system|substrate):[A-Za-z0-9_-]{1,64}$")
HEX = re.compile(r"^[0-9a-f]{64}$")
NODE_FIELDS = {"id", "class", "visibility", "source_ref",
               "source_sha256", "edges"}
MAX_INPUT_NODES = 32
MAX_INPUT_EDGES = 96
MAX_DEPTH = 5
MAX_OUTPUT_NODES = 24


class Hold(ValueError):
    pass


def require(condition: bool, error: str) -> None:
    if not condition:
        raise Hold(error)


def parse(graph: dict) -> dict:
    require(type(graph) is dict and set(graph) == {"schema", "nodes"},
            "INVALID_GRAPH_FIELDS")
    require(graph["schema"] == SCHEMA, "INVALID_GRAPH_SCHEMA")
    nodes = graph["nodes"]
    require(type(nodes) is list and 1 <= len(nodes) <= MAX_INPUT_NODES,
            "INPUT_NODE_BUDGET")
    index: dict[str, dict] = {}
    for node in nodes:
        require(type(node) is dict and set(node) == NODE_FIELDS,
                "INVALID_NODE_FIELDS")
        ident = node["id"]
        require(type(ident) is str and IDENTIFIER.fullmatch(ident),
                "INVALID_NODE_ID")
        require(ident not in index, "DUPLICATE_NODE_ID")
        prefix, _ = ident.split(":", 1)
        require(node["class"] in CLASSES
                and node["class"] == {"fed": "FEDERATION",
                                     "system": "SYSTEM",
                                     "substrate": "SUBSTRATE"}[prefix],
                "NODE_CLASS_MISMATCH")
        require(node["visibility"] in {"PUBLIC", "PRIVATE"},
                "INVALID_VISIBILITY")
        require(type(node["source_ref"]) is str
                and node["source_ref"] == "fixture:" + ident,
                "UNBOUND_SOURCE_REF")
        require(type(node["source_sha256"]) is str
                and HEX.fullmatch(node["source_sha256"]),
                "INVALID_SOURCE_DIGEST")
        require(type(node["edges"]) is list, "INVALID_EDGES")
        index[ident] = node
    edge_count = 0
    for node in nodes:
        seen = set()
        for e in node["edges"]:
            require(type(e) is dict and set(e) == {"to", "relation"},
                    "INVALID_EDGE_FIELDS")
            target = e["to"]
            relation = e["relation"]
            require(type(target) is str and target in index,
                    "UNKNOWN_EDGE_TARGET")
            require(type(relation) is str and relation in RELATIONS,
                    "UNKNOWN_EDGE_RELATION")
            ident = (target, relation)
            require(ident not in seen, "DUPLICATE_EDGE")
            seen.add(ident)
            edge_count += 1
    require(edge_count <= MAX_INPUT_EDGES, "INPUT_EDGE_BUDGET")
    return index


def discover(graph: dict, root: str,
             depth_limit: int = 3, node_limit: int = 12) -> dict:
    index = parse(graph)
    require(type(root) is str and root in index, "UNKNOWN_ROOT")
    require(index[root]["visibility"] == "PUBLIC", "ROOT_NOT_PUBLIC")
    require(type(depth_limit) is int and 0 <= depth_limit <= MAX_DEPTH,
            "INVALID_DEPTH_BUDGET")
    require(type(node_limit) is int and 1 <= node_limit <= MAX_OUTPUT_NODES,
            "INVALID_OUTPUT_BUDGET")

    queue = deque([(root, 0)])
    enqueued = {root}
    selected: dict[str, int] = {}
    budget_held = False
    while queue:
        ident, depth = queue.popleft()
        if len(selected) >= node_limit:
            budget_held = True
            break
        selected[ident] = depth
        if depth >= depth_limit:
            continue
        # An edge to PRIVATE must not leak its target or be counted in output.
        for edge in sorted(index[ident]["edges"],
                           key=lambda e: (e["to"], e["relation"])):
            target = edge["to"]
            if index[target]["visibility"] != "PUBLIC":
                continue
            if target in selected or target in enqueued:
                continue
            enqueued.add(target)
            queue.append((target, depth + 1))

    visible_nodes = [
        {
            "id": ident, "class": index[ident]["class"],
            "source_ref": index[ident]["source_ref"],
            "declared_source_sha256": index[ident]["source_sha256"],
            "minimum_discovery_hops": depth,
            "source_bytes_independently_read": False,
            "identity_or_ownership_attested": False,
        }
        for ident, depth in sorted(selected.items(),
                                   key=lambda x: (x[1], x[0]))
    ]

    visible_edges = []
    for ident in selected:
        for edge in index[ident]["edges"]:
            if edge["to"] not in selected:
                continue
            reverse = any(
                r["to"] == ident and r["relation"] == INVERSE[edge["relation"]]
                for r in index[edge["to"]]["edges"]
            )
            visible_edges.append({
                "from": ident, "to": edge["to"],
                "declared_relation": edge["relation"],
                "inverse_required_for_reciprocity": INVERSE[edge["relation"]],
                "inverse_evidence": (
                    "REVERSE_DECLARED_ONLY_UNVERIFIED" if reverse
                    else "REVERSE_NOT_DECLARED"
                ),
                "membership_granted": False,
                "trust_granted": False,
                "effect_authority_granted": False,
            })
    visible_edges.sort(key=lambda x: (
        x["from"], x["to"], x["declared_relation"]))

    public_payload = {
        "schema": OUTPUT_SCHEMA,
        "state": "SYNTHETIC_PUBLIC_DISCOVERY__NO_RUNTIME",
        "root": root,
        "depth_limit": depth_limit,
        "node_limit": node_limit,
        "budget_held": budget_held,
        "nodes": visible_nodes,
        "edges": visible_edges,
        # No total input-node count, count of PRIVATE edges, full input
        # digest, private ID, private path or presence-sensitive error.
        "private_topology": "NOT_DISCLOSED",
        "actual_independent_failure_domains": "NOT_TESTED",
        "receiver_ack": "NOT_OBSERVED",
        "actual_remote_discovery": "NOT_TESTED",
        "membership_election": "NONE",
        "runtime_workers": 0,
        "provider_requests": 0,
        "effects": 0,
        "rails": [
            "FEDERATION_NE_CONTROLLER",
            "DISCOVERABLE_NE_IN_SCOPE",
            "DISCOVERS_A_TO_B_NE_B_DISCOVERS_A",
            "INVERSE_EDGE_DECLARED_NE_MUTUAL_CONSENT",
            "NESTED_TURTLES_NE_INFINITE_ACTIVE_WORKERS",
            "MULTIPLE_ROUTES_NE_INDEPENDENT_EVIDENCE",
            "PUBLIC_OUTPUT_NE_PRIVATE_TOPOLOGY",
        ],
    }
    public_payload["public_view_sha256"] = hashlib.sha256(
        json.dumps(public_payload, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return public_payload


def fixture() -> dict:
    def n(ident, klass, edges=(), visibility="PUBLIC"):
        return {
            "id": ident, "class": klass,
            "visibility": visibility,
            "source_ref": "fixture:" + ident,
            "source_sha256": "a" * 64,
            "edges": [{"to": to, "relation": rel} for to, rel in edges],
        }
    return {
        "schema": SCHEMA,
        "nodes": [
            n("fed:root", "FEDERATION", [
                ("fed:regional", "DISCOVERS"),
                ("system:local", "DISCOVERS"),
                ("fed:mirror", "PEERS_WITH"),
                ("system:private", "DISCOVERS"),
            ]),
            n("fed:regional", "FEDERATION", [
                ("fed:nested", "CONTAINS"),
                ("fed:root", "DISCOVERED_BY"),
            ]),
            n("fed:nested", "FEDERATION", [
                ("substrate:edge", "DISCOVERS"),
                ("fed:regional", "MEMBER_OF"),
            ]),
            n("substrate:edge", "SUBSTRATE"),
            n("system:local", "SYSTEM"),
            n("fed:mirror", "FEDERATION", [
                ("fed:root", "PEERS_WITH"),
            ]),
            n("system:private", "SYSTEM", [
                ("system:even-more-private", "CONTAINS")
            ], "PRIVATE"),
            n("system:even-more-private", "SYSTEM", visibility="PRIVATE"),
        ],
    }


if __name__ == "__main__":
    print(json.dumps(discover(fixture(), "fed:root"), indent=2,
                     sort_keys=True))
