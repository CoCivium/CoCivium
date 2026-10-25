#!/usr/bin/env python3
"""CoTouchEvo R0: pure, bounded relation-impact proposals; never dispatches effects.

Synthetic/scope-limited reference for existing CoEvoDelta, CoSourceGraph, and
CoSubscriptionEcology contracts. No external access, writes, workers, or logging.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import deque

SCHEMA = "CoAll.CoTouchEvo.ImpactProposal.R0"
LEVEL = {"PUBLIC": 0, "PRIVATE": 1, "RESTRICTED": 2}
WAKE_EDGES = {"DEPENDS_ON", "DERIVED_FROM", "RENDERS_FROM", "VALIDATES_INPUT"}
NONWAKE_EDGES = {"INSPIRED_BY", "RELATED_TO", "CONTRADICTS", "SYMBOLIZES"}
MODES = {"WAKE_ONLY", "DIGEST", "LATEST_POINTER"}


def _valid_id(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9_.:/-]{1,120}", value))


def _require(ok, label):
    if not ok:
        raise ValueError(label)


def _hash_of(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _validate(data):
    _require(isinstance(data, dict) and data.get("schema") == SCHEMA, "bad schema")
    change = data.get("change")
    _require(isinstance(change, dict) and set(change) == {"subject", "event_id", "revision_sha256", "evidence"}, "bad change")
    _require(_valid_id(change["subject"]) and _valid_id(change["event_id"]), "bad change identity")
    _require(isinstance(change["revision_sha256"], str) and bool(re.fullmatch(r"[0-9a-f]{64}", change["revision_sha256"])), "bad change revision")
    _require(change["evidence"] in {"SYNTHETIC", "OBSERVED", "HYPOTHESIS"}, "bad change evidence")
    nodes = data.get("nodes")
    _require(isinstance(nodes, list) and 1 <= len(nodes) <= 250, "bad nodes")
    node_map = {}
    for item in nodes:
        _require(isinstance(item, dict) and set(item) == {"id", "classification"}, "bad node shape")
        _require(_valid_id(item["id"]) and item["classification"] in LEVEL, "bad node")
        _require(item["id"] not in node_map, "duplicate node")
        node_map[item["id"]] = item
    _require(change["subject"] in node_map, "missing source")
    edges = data.get("edges")
    _require(isinstance(edges, list) and len(edges) <= 500, "bad edges")
    for edge in edges:
        _require(isinstance(edge, dict) and set(edge) == {"dependent", "dependency", "relation", "evidence"}, "bad edge shape")
        _require(edge["dependent"] in node_map and edge["dependency"] in node_map, "missing edge endpoint")
        _require(edge["relation"] in WAKE_EDGES | NONWAKE_EDGES and edge["evidence"] in {"GROUNDED", "PROPOSED"}, "bad edge type")
    receivers = data.get("receivers")
    _require(isinstance(receivers, list) and len(receivers) <= 50, "bad receivers")
    seen = set()
    for receiver in receivers:
        _require(isinstance(receiver, dict) and set(receiver) == {"id", "clearance", "mode", "targets", "last_acked_event_id", "max_items"}, "bad receiver")
        _require(_valid_id(receiver["id"]) and receiver["id"] not in seen, "bad receiver id")
        seen.add(receiver["id"])
        _require(receiver["clearance"] in LEVEL and receiver["mode"] in MODES, "bad receiver mode")
        _require(isinstance(receiver["targets"], list) and all(t in node_map for t in receiver["targets"]), "bad targets")
        _require(len(receiver["targets"]) <= 100, "too many targets")
        _require(receiver["last_acked_event_id"] is None or _valid_id(receiver["last_acked_event_id"]), "bad ack")
        _require(type(receiver["max_items"]) is int and 0 <= receiver["max_items"] <= 12, "bad item limit")
    lim = data.get("limits")
    _require(isinstance(lim, dict) and set(lim) == {"max_hops", "max_visits", "max_proposals", "max_review"}, "bad limits")
    _require(type(lim["max_hops"]) is int and 0 <= lim["max_hops"] <= 3, "max_hops")
    _require(type(lim["max_visits"]) is int and 1 <= lim["max_visits"] <= 64, "max_visits")
    _require(type(lim["max_proposals"]) is int and 0 <= lim["max_proposals"] <= 20, "max_proposals")
    _require(type(lim["max_review"]) is int and 0 <= lim["max_review"] <= 12, "max_review")
    return change, node_map, edges, receivers, lim


def propose(data):
    """Return shadow suggestions only, without dispatch, new ACKs, or context transfers."""
    change, nodes, edges, receivers, lim = _validate(data)
    basis = _hash_of(data)
    adj = {}
    seen_edges = set()
    nonwake = 0
    nongrounded = 0
    private_barriers = 0
    for e in sorted(edges, key=lambda e: (e["dependency"], e["dependent"], e["relation"], e["evidence"])):
        identity = (e["dependent"], e["dependency"], e["relation"], e["evidence"])
        if identity in seen_edges:
            continue
        seen_edges.add(identity)
        if e["relation"] not in WAKE_EDGES:
            nonwake += 1
            continue
        if e["evidence"] != "GROUNDED":
            nongrounded += 1
            continue
        if LEVEL[nodes[e["dependency"]]["classification"]] > LEVEL[nodes[e["dependent"]]["classification"]]:
            private_barriers += 1
            continue
        adj.setdefault(e["dependency"], []).append(e["dependent"])
    for value in adj.values():
        value.sort()
    changed = change["subject"]
    q = deque([(changed, 0)])
    visited = {changed: 0}
    truncated = False
    while q:
        node, depth = q.popleft()
        if depth >= lim["max_hops"]:
            continue
        for target in adj.get(node, []):
            if target in visited:
                continue
            if len(visited) >= lim["max_visits"]:
                truncated = True
                break
            visited[target] = depth + 1
            q.append((target, depth + 1))
        if truncated:
            break
    # A related inspiration or counterexample is an explicitly non-operational
    # suggestion. Never expose private names in the public-safe review projection.
    review_only = []
    seen_reviews = set()
    for e in sorted(edges, key=lambda e: (e["dependency"], e["dependent"], e["relation"])):
        if e["dependency"] != changed or e["relation"] not in NONWAKE_EDGES or e["evidence"] != "GROUNDED":
            continue
        if nodes[changed]["classification"] != "PUBLIC" or nodes[e["dependent"]]["classification"] != "PUBLIC":
            continue
        key = (e["dependent"], e["relation"])
        if key in seen_reviews:
            continue
        seen_reviews.add(key)
        if len(review_only) >= lim["max_review"]:
            truncated = True
            break
        review_only.append({"subject": e["dependent"], "relation": e["relation"], "state": "REVIEW_CANDIDATE_NOT_WAKE"})
    proposals = []
    receiver_details = []
    evidence_gate = change["evidence"] != "HYPOTHESIS"
    for receiver in sorted(receivers, key=lambda r: r["id"]):
        candidates = sorted((t for t in set(receiver["targets"]) if t in visited and t != changed and LEVEL[nodes[t]["classification"]] <= LEVEL[receiver["clearance"]] and LEVEL[nodes[changed]["classification"]] <= LEVEL[receiver["clearance"]]), key=lambda t:(visited[t],t))
        already_acked = receiver["last_acked_event_id"] == change["event_id"]
        count = 0
        for target in candidates:
            if already_acked or not evidence_gate:
                continue
            if len(proposals) >= lim["max_proposals"] or count >= receiver["max_items"]:
                truncated = True
                break
            proposals.append({"receiver": receiver["id"], "subject": target, "distance": visited[target], "mode": receiver["mode"], "state": "SHADOW_PROPOSAL_NO_EFFECT"})
            count += 1
        receiver_details.append({"receiver": receiver["id"], "eligible_count": len(candidates), "proposals": count, "ack_unchanged": True, "already_acked": already_acked})
    return {
        "schema": "CoAll.CoTouchEvo.ImpactProposalReceipt.R0",
        "input_digest": basis,
        "evidence": change["evidence"],
        "status": "TRUNCATED_HELD" if truncated else ("HYPOTHESIS_ONLY_HELD" if not evidence_gate else "SHADOW_ONLY"),
        "visited_count": len(visited),
        "propagation_hops_limit": lim["max_hops"],
        "proposals": proposals,
        "review_only": review_only,
        "receiver_summaries": receiver_details,
        "gates": {"nonwake_edges": nonwake, "ungrounded_edges": nongrounded, "privacy_barrier_edges": private_barriers},
        "effects": {"worker_starts": 0, "network_calls": 0, "provider_calls": 0, "external_writes": 0, "ack_advances": 0},
        "nonclaims": [
            "SHADOW_PROPOSAL_NE_SCHEDULED_TASK", "DEPENDS_ON_NE_AUTOMATIC_MUTATION",
            "INSPIRED_BY_NE_CHANGE_DEPENDENCY", "SUBSCRIPTION_NE_AUTHORITY",
            "RECEIPT_NE_RECEIVER_READPROOF", "STATIC_PINS_NE_SOURCE_VERIFICATION",
            "BOUNDED_GRAPH_NE_COMPLETE_RELATION_UNIVERSE"
        ]
    }


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser(description="Read a fixture, print a shadow impact plan; never dispatch.")
    p.add_argument("fixture", type=Path)
    args = p.parse_args()
    print(json.dumps(propose(json.loads(args.fixture.read_text(encoding="utf-8"))), indent=2, sort_keys=True))
