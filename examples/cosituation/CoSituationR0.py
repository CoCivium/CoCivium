"""CoSituation R0: pure, fail-closed universal relation/candidate envelope.

The input is explicitly supplied data, NOT an observer, executor, authorization,
source verifier, scheduler, or independent receiver. Every return is shadow only.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

SCHEMA = "CoAll.CoSituation.R0"
SUBSTRATE = {
    "SOFTWARE": "DIGITAL_EXECUTABLE",
    "DEVICE": "PHYSICAL_DEVICE",
    "SESSION": "LOGICAL_WORK",
    "FUTURE_BRANCH": "COUNTERFACTUAL",
    "MYTHIC_OBJECT": "SYMBOLIC",
}
EPISTEMIC = {"SOURCE_REPORT", "HYPOTHESIS", "SYMBOLIC", "UNKNOWN", "SIMULATION"}
PRIVACY = {"PUBLIC", "PRIVATE_LOCAL", "SENSITIVE", "UNKNOWN"}
LIFECYCLE = {"ACTIVE", "QUIESCENT", "COOL", "DORMANT", "COTWILIGHT", "CLOSE_SAFE", "ARCHIVE"}
WAKE = {"SOURCE_REVISION_CHANGED", "RECEIVER_READPROOF_ADDED", "FRESH_OBSERVER_READBACK", "EXPLICIT_INTENT"}
NONCLAIMS = (
    "SAME_ENVELOPE_NE_SAME_ONTOLOGY", "OBJECTABLE_NE_OWNABLE_OR_SENTIENT",
    "RELATION_OF_RELATION_NE_CAUSAL_PROOF", "SYMBOLIC_NE_PHYSICAL_PROOF",
    "REVERENCE_NE_AUTHORITY", "COSIT_NE_FORGOTTEN", "DORMANT_NE_STALE_TRUTH",
    "WAKE_NE_EXECUTE", "STRUCTURAL_REVALIDATION_NE_SOURCE_READPROOF",
    "SOURCE_POINTER_NE_SOURCE_BYTES", "PREVIEW_NE_RUNTIME_OR_COEX",
)
ZERO_EFFECTS = {"file": 0, "device": 0, "network": 0, "model": 0, "send": 0, "workers": 0}
_SHA = re.compile(r"^sha256:[a-f0-9]{64}$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,127}$")


def reject(code: str) -> None:
    raise ValueError(code)


def mapping(obj: Any, code: str) -> dict:
    if not isinstance(obj, dict):
        reject(code)
    return obj


def ident(obj: Any, code: str) -> str:
    if not isinstance(obj, str) or not _ID.fullmatch(obj):
        reject(code)
    return obj


def sha(obj: Any, code: str) -> str:
    if not isinstance(obj, str) or not _SHA.fullmatch(obj):
        reject(code)
    return obj


def moment(obj: Any, code: str) -> datetime:
    if not isinstance(obj, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", obj):
        reject(code)
    try:
        result = datetime.strptime(obj, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        reject(code)
    return result


def validate(record: Any) -> dict:
    """Read-only structural qualification. It cannot attest source truth or access."""
    d = mapping(record, "INVALID_SITUATION")
    if d.get("schema") != SCHEMA:
        reject("INVALID_SCHEMA")
    ident(d.get("situation_id"), "INVALID_SITUATION_ID")
    subject = mapping(d.get("subject"), "INVALID_SUBJECT")
    ident(subject.get("id"), "INVALID_SUBJECT_ID")
    kind = subject.get("kind")
    if not isinstance(kind, str) or kind not in SUBSTRATE or subject.get("substrate") != SUBSTRATE.get(kind):
        reject("SUBSTRATE_KIND_MISMATCH")
    if not isinstance(subject.get("epistemic"), str) or subject.get("epistemic") not in EPISTEMIC:
        reject("INVALID_EPISTEMIC")
    if kind == "MYTHIC_OBJECT" and subject["epistemic"] != "SYMBOLIC":
        reject("MYTHIC_CANNOT_PROMOTE_TO_OBSERVED")
    if kind == "FUTURE_BRANCH" and subject["epistemic"] not in {"HYPOTHESIS", "SIMULATION"}:
        reject("FUTURE_CANNOT_PROMOTE_TO_PRESENT_FACT")
    source = mapping(d.get("source"), "INVALID_SOURCE")
    ident(source.get("ref"), "INVALID_SOURCE_REF")
    sha(source.get("sha256"), "INVALID_DECLARED_SOURCE_SHA")
    if source.get("readproof") != "DECLARED_NOT_VERIFIED":
        reject("SOURCE_READPROOF_CANNOT_BE_ASSERTED")
    observer = mapping(d.get("observer"), "INVALID_OBSERVER")
    ident(observer.get("id"), "INVALID_OBSERVER_ID")
    if observer.get("proof") != "SYNTHETIC_FIXTURE_ONLY":
        reject("UNVERIFIED_OBSERVER_EVIDENCE")
    ts = mapping(d.get("time"), "INVALID_TIME")
    src, seen, stale = (moment(ts.get(k), "INVALID_"+k.upper()) for k in ("source_at", "observed_at", "stale_after"))
    if src > seen or seen > stale:
        reject("INCONSISTENT_TEMPORAL_ORDER")
    if not isinstance(d.get("privacy"), str) or d.get("privacy") not in PRIVACY:
        reject("INVALID_PRIVACY")
    authority = mapping(d.get("authority"), "INVALID_AUTHORITY")
    if authority.get("effect") != "NONE" or authority.get("granted") is not False:
        reject("NO_EFFECT_AUTHORITY_IN_FIXTURE")
    if not isinstance(d.get("lifecycle"), str) or d.get("lifecycle") not in LIFECYCLE:
        reject("INVALID_LIFECYCLE")
    sit = mapping(d.get("sit"), "INVALID_COSIT")
    if sit.get("lifecycle_mode") != d["lifecycle"]:
        reject("COSIT_CANNOT_REPLACE_LIFECYCLE")
    if sit.get("lifecycle_mode") not in {"QUIESCENT", "COOL", "DORMANT", "COTWILIGHT", "CLOSE_SAFE", "ARCHIVE"}:
        reject("COSIT_EXPECTS_QUIESCENCE")
    if not isinstance(sit.get("wake_on"), str) or sit.get("wake_on") not in WAKE:
        reject("INVALID_WAKE_PREDICATE")
    if sit.get("revalidate_before_effect") is not True:
        reject("MISSING_REVALIDATION_GATE")
    rels = d.get("relations")
    if not isinstance(rels, list) or len(rels) > 32:
        reject("INVALID_RELATIONS")
    seen_rel = set()
    for rel in rels:
        mapping(rel, "INVALID_RELATION")
        rel_id = ident(rel.get("id"), "INVALID_RELATION_ID")
        ident(rel.get("target_id"), "INVALID_RELATION_TARGET")
        if rel_id in seen_rel:
            reject("DUPLICATE_RELATION_ID")
        seen_rel.add(rel_id)
        if not isinstance(rel.get("epistemic"), str) or rel.get("epistemic") not in EPISTEMIC:
            reject("INVALID_RELATION_EPISTEMIC")
        if not isinstance(rel.get("type"), str) or rel.get("type") not in {"DEPENDS_ON", "RELATES_TO", "EVOLVES_AS_CANDIDATE", "ABOUT_RELATION", "CONTRADICTS", "REQUIRES_PROOF"}:
            reject("INVALID_RELATION_TYPE")
        if kind == "MYTHIC_OBJECT" and rel["epistemic"] == "SOURCE_REPORT" and rel["type"] == "REQUIRES_PROOF":
            reject("SYMBOLIC_PROOF_ESCALATION")
    for rel in rels:
        if rel["type"] == "ABOUT_RELATION" and rel["target_id"] not in seen_rel:
            reject("UNGROUNDED_META_RELATION")
    # Meta-relations may refer to relations but must have finite acyclic depth.
    meta_targets = {r["id"]: r["target_id"] for r in rels if r["type"] == "ABOUT_RELATION"}
    for start in meta_targets:
        cursor, visited, depth = start, set(), 0
        while cursor in meta_targets:
            if cursor in visited:
                reject("CYCLIC_META_RELATION")
            visited.add(cursor)
            depth += 1
            if depth > 2:
                reject("META_RELATION_DEPTH_EXCEEDED")
            cursor = meta_targets[cursor]
    rv = d.get("reverence")
    if rv is not None:
        rv = mapping(rv, "INVALID_REVERENCE")
        if rv.get("role") != "INTERPRETATION_OR_PRESERVATION" or rv.get("effect_authority") != "NONE":
            reject("REVERENCE_CANNOT_GRANT_AUTHORITY")
        if not isinstance(rv.get("basis"), str) or not rv["basis"].strip() or len(rv["basis"]) > 160:
            reject("INVALID_REVERENCE_BASIS")
    return {
        "schema": SCHEMA, "situation_id": d["situation_id"], "kind": kind,
        "substrate": subject["substrate"], "epistemic": subject["epistemic"],
        "source_readproof": "UNVERIFIED", "authority": "NONE", "privacy": d["privacy"],
        "lifecycle": d["lifecycle"], "relation_count": len(rels),
        "meta_relation_count": sum(x["type"] == "ABOUT_RELATION" for x in rels),
        "wake_on": sit["wake_on"], "evolution_allowed_as_candidate": True,
        "effects": dict(ZERO_EFFECTS), "nonclaims": list(NONCLAIMS),
    }


def wake_preview(record: Any, event: Any = None) -> dict:
    """Preview a wake/revalidation decision, never mutation or source validation."""
    base = validate(record)
    result = {"schema": "CoAll.CoSituation.WakePreview.R0", "situation_id": base["situation_id"],
              "state": "DORMANT_AWAIT_WAKE", "authority": "NONE", "effects": dict(ZERO_EFFECTS),
              "source_readproof": "UNVERIFIED", "receiver_ack": False,
              "can_execute": False, "nonclaims": list(NONCLAIMS)}
    if event is None:
        return result
    e = mapping(event, "INVALID_EVENT")
    if e.get("situation_id") != record["situation_id"]:
        result["state"] = "HELD_UNBOUND_WAKE_EVENT"; return result
    if e.get("kind") != record["sit"]["wake_on"]:
        result["state"] = "DORMANT_UNRELATED_EVENT"; return result
    event_time = moment(e.get("observed_at"), "INVALID_EVENT_TIME")
    stale = moment(record["time"]["stale_after"], "INVALID_STALE_DATE")
    old = moment(record["time"]["observed_at"], "INVALID_OBSERVATION_DATE")
    if event_time < old:
        result["state"] = "HELD_EVENT_OLDER_THAN_SNAPSHOT"; return result
    if e.get("source_sha256") != record["source"]["sha256"]:
        result["state"] = "HELD_SOURCE_REVISION_CHANGED_REBIND_REQUIRED"; return result
    if event_time > stale and e.get("readproof") is None:
        result["state"] = "HELD_STALE_REVALIDATION_REQUIRED"; return result
    receipt = e.get("readproof")
    if not isinstance(receipt, dict) or receipt.get("kind") != "SYNTHETIC_SOURCE_READBACK" or receipt.get("source_sha256") != record["source"]["sha256"]:
        result["state"] = "HELD_READPROOF_NOT_BOUND"; return result
    if receipt.get("observed_at") != e.get("observed_at"):
        result["state"] = "HELD_READPROOF_NOT_CURRENT"; return result
    result["state"] = "SHADOW_REVALIDATION_CANDIDATE_EFFECTS_HELD"
    result["source_readproof"] = "SYNTHETIC_ONLY_NOT_INDEPENDENT"
    return result


__all__ = ("SCHEMA", "SUBSTRATE", "validate", "wake_preview")