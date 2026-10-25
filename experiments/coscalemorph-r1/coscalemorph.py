"""CoScaleMorph R0: loss-aware, source-bound UI projections (not agent execution).

Pure Python, no network or provider integration. Public demonstration data only.
The projection is always recoverable only *by fetching the retained source*.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


class ScaleError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _unique_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ScaleError("DUPLICATE_JSON_KEY")
        out[k] = v
    return out


def validate_source(raw: bytes) -> dict:
    if type(raw) is not bytes or len(raw) > 1_000_000:
        raise ScaleError("INVALID_SOURCE_BYTES_OR_SIZE")
    try:
        x = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ScaleError("SOURCE_JSON_INVALID") from exc
    if not isinstance(x, dict) or x.get("schema") != "CoMapPulseGraph/R0":
        raise ScaleError("WRONG_SOURCE_SCHEMA")
    if x.get("source_policy") != "PUBLIC_ONLY__NO_SECRETS__NO_REMOTE_EFFECT":
        raise ScaleError("SOURCE_NOT_PUBLIC_SAFE")
    nodes, edges = x.get("nodes"), x.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list) or len(nodes)>500 or len(edges)>3000:
        raise ScaleError("GRAPH_SHAPE_OR_BUDGET")
    ids = [n.get("id") for n in nodes if isinstance(n, dict)]
    if len(ids) != len(nodes) or len(set(ids)) != len(ids) or any(not isinstance(z, str) or not z for z in ids):
        raise ScaleError("BAD_NODE_IDENTITIES")
    for n in nodes:
        if n.get("privacy", "PUBLIC") != "PUBLIC":
            raise ScaleError("NONPUBLIC_NODE_BLOCKED")
    for e in edges:
        if not isinstance(e, dict) or e.get("from") not in ids or e.get("to") not in ids:
            raise ScaleError("EDGE_ENDPOINT_MISSING")
        if e.get("epistemic") not in ("DOCUMENTED", "PROPOSED", "HELD"):
            raise ScaleError("BAD_EPISTEMIC_CLASS")
        if e.get("ack") not in ("NOT_APPLICABLE", "NOT_OBSERVED", "NO_RECEIVER_ACK"):
            raise ScaleError("UNVERIFIED_ACK_CLAIM")
    return x


def _capsule_body(capsule):
    return {k: v for k, v in capsule.items() if k != "capsule_sha256"}


def reduce_view(source: bytes, *, visible_budget: int, view="ORB") -> dict:
    """Create a compact observer projection, preserving the source hash.

    No hidden nodes or edges are deleted or independently asserted as known.
    """
    x = validate_source(source)
    if type(visible_budget) is not int or not 1 <= visible_budget <= min(20, len(x["nodes"])):
        raise ScaleError("BAD_VIEW_BUDGET")
    if view not in ("ORB", "MAP", "DETAIL"):
        raise ScaleError("UNKNOWN_VIEW")
    visible = x["nodes"][:visible_budget]
    selected = {n["id"] for n in visible}
    edges = [e for e in x["edges"] if e["from"] in selected and e["to"] in selected]
    capsule = {
        "schema": "CoScaleMorphCapsule/R0",
        "view": view,
        "scope_ceiling": "PUBLIC_READ",
        "source_sha256": sha(source),
        "source_byte_count": len(source),
        "source_schema": x["schema"],
        "reduction_type": "REVERSIBLE_VIEW_ONLY_SOURCE_REQUIRED",
        "source_retention": "REQUIRED_AND_NOT_PROVEN_BY_POINTER",
        "visible_nodes": [{"id": n["id"], "title": n["title"], "epistemic_state": n["status"]} for n in visible],
        "visible_relations": [{"id": e["id"], "from": e["from"], "to": e["to"], "epistemic": e["epistemic"]} for e in edges],
        "omitted_node_count": len(x["nodes"])-len(visible),
        "omitted_edge_count": len(x["edges"])-len(edges),
        "reconstruction_status": "PENDING_SOURCE_FETCH",
        "worker_processes_spawned": 0,
        "receiver_ack": "NOT_OBSERVED",
        "claim_limits": ["VIEW_COMPACTION_NE_DELETION", "VISIBLE_NE_ENTIRE_GRAPH", "SOURCE_HASH_NE_CUSTODY", "REHYDRATABLE_NE_REHYDRATED"],
    }
    capsule["capsule_sha256"] = sha(canonical(capsule))
    return capsule


def rehydrate(capsule: dict, source: bytes | None, *,
              authorization="PUBLIC_READ", tombstone=False) -> bytes:
    """Return exact source bytes only if available, unchanged, and authorized.

    Never reverse an inherently lossy summary, retention erasure, or revoked scope.
    """
    if not isinstance(capsule, dict) or capsule.get("schema") != "CoScaleMorphCapsule/R0":
        raise ScaleError("BAD_CAPSULE")
    if sha(canonical(_capsule_body(capsule))) != capsule.get("capsule_sha256"):
        raise ScaleError("TAMPERED_CAPSULE")
    if tombstone:
        raise ScaleError("ERASURE_OR_RETENTION_GATE")
    if authorization != "PUBLIC_READ" or capsule.get("scope_ceiling") != "PUBLIC_READ":
        raise ScaleError("AUTHORITY_GATE")
    if capsule.get("reduction_type") != "REVERSIBLE_VIEW_ONLY_SOURCE_REQUIRED":
        raise ScaleError("INHERENTLY_LOSSY_OR_UNSUPPORTED")
    if source is None:
        raise ScaleError("SOURCE_NOT_AVAILABLE")
    if type(source) is not bytes or len(source) != capsule.get("source_byte_count") or sha(source) != capsule.get("source_sha256"):
        raise ScaleError("SOURCE_MISMATCH")
    graph = validate_source(source)
    if graph["schema"] != capsule.get("source_schema"):
        raise ScaleError("SOURCE_NAMESPACE_DRIFT")
    if len(graph["nodes"]) - len(capsule.get("visible_nodes", [])) != capsule.get("omitted_node_count"):
        raise ScaleError("CAPSULE_GRAPH_SHAPE_MISMATCH")
    return source


def planning_frontier(logical_slots: int, requested_workers: int, *,
                      max_workers=2, actual_tasks=12, authority="LOCAL_TEST_ONLY") -> dict:
    """Huge address space, tiny bounded work frontier; no action performed."""
    if type(logical_slots) is not int or logical_slots <= 0 or logical_slots > 10**18:
        raise ScaleError("BAD_LOGICAL_CAPACITY")
    if type(requested_workers) is not int or requested_workers <= 0:
        raise ScaleError("BAD_REQUESTED_WORKERS")
    if type(max_workers) is not int or not 1 <= max_workers <= 4:
        raise ScaleError("BAD_CEILING")
    if type(actual_tasks) is not int or not 0 <= actual_tasks <= 100:
        raise ScaleError("BAD_TASK_BUDGET")
    if authority != "LOCAL_TEST_ONLY":
        raise ScaleError("AUTHORITY_GATE")
    active = min(requested_workers, max_workers, actual_tasks)
    return {
        "logical_slots": logical_slots,
        "requested_workers": requested_workers,
        "eligible_worker_ceiling": active,
        "sampled_task_count": actual_tasks,
        "not_materialized_slots": logical_slots - active,
        "actual_workers_spawned_by_planner": 0,
        "authority": authority,
        "claim_limits": ["LOGICAL_SLOTS_NE_ACTUAL_WORKERS", "ACTIVE_CEILING_NE_EXECUTED", "FINITE_BUDGETS_REQUIRED"],
    }
