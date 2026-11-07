#!/usr/bin/env python3
"""CoPredict drift R0: deterministic, synthetic-only self-sorting counterfactual.

This is NOT a running scheduler, a real multi-session forecast, a proof of
independently observed sessions, or a new measurement-unit registry.
"""
from collections import defaultdict
from datetime import datetime
from typing import Mapping

REQUIRED = ("claim_id", "session_fixture", "sequence", "label",
            "definition_id", "quantity_kind", "unit_id", "method_id",
            "scope_id", "frame_id", "source_ref")
RULES = (
    "LOCAL_FIFO_NE_GLOBAL_CONSENSUS",
    "NAME_COLLISION_NE_SEMANTIC_EQUIVALENCE",
    "ALIAS_NE_CANON",
    "CO_NULL_NE_NUMERIC_ZERO",
    "CO_TICK_NE_UNIVERSAL_CONVERSION",
    "PIXEL_DELTA_NE_WORK_EFFECT",
    "FORECAST_NE_FACT",
    "NO_PREEMPTIVE_AUTOMATIC_FAIL_RULE",
    "NO_AUTOMATIC_OS_FALLBACK_REMOVAL",
    "NO_NEW_SCHEDULER",
)


def _require(ok, code):
    if not ok:
        raise ValueError(code)


def _utc(timestamp):
    _require(isinstance(timestamp, str) and timestamp.endswith("Z"),
             "UTC_TIMESTAMP_REQUIRED")
    try:
        return datetime.fromisoformat(timestamp[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc


def validate_proposals(proposals):
    """Check the synthetic fixture, never claim provenance authenticity."""
    _require(isinstance(proposals, list) and bool(proposals), "PROPOSALS_REQUIRED")
    ids = set()
    per_session = defaultdict(list)
    for p in proposals:
        _require(isinstance(p, Mapping) and all(k in p for k in REQUIRED),
                 "PROPOSAL_FIELDS_REQUIRED")
        for k in REQUIRED:
            if k == "sequence":
                _require(type(p[k]) is int and p[k] >= 0,
                         "SEQUENCE_REQUIRED")
            else:
                _require(isinstance(p[k], str) and bool(p[k].strip()),
                         "IDENTITY_OR_SCOPE_REQUIRED:" + k)
        _require(p["claim_id"] not in ids, "DUPLICATE_CLAIM_ID")
        ids.add(p["claim_id"])
        per_session[p["session_fixture"]].append(p["sequence"])
        _require(p.get("evidence_class") == "SYNTHETIC",
                 "UNVERIFIED_REAL_SESSION_CLAIM")
    _require(all(seq == sorted(seq) and len(seq) == len(set(seq))
                 for seq in per_session.values()), "LOCAL_SEQUENCE_NOT_ORDERED")
    return per_session


def signature(p):
    """Claimed semantic signature, not cryptographically authenticated truth."""
    return (p["definition_id"], p["quantity_kind"], p["unit_id"],
            p["method_id"], p["scope_id"], p["frame_id"])


def compare_sorting(proposals):
    """Compare name-only grouping with typed comparison, without elections."""
    sessions = validate_proposals(proposals)
    by_label, by_semantics = defaultdict(list), defaultdict(list)
    for p in proposals:
        by_label[p["label"].strip().casefold()].append(p)
        by_semantics[signature(p)].append(p)
    conflicts = sorted(
        label for label, rows in by_label.items()
        if len({signature(p) for p in rows}) > 1
    )
    aliases = sorted(
        {p["label"] for p in rows}
        for rows in by_semantics.values()
        if len({p["label"].strip().casefold() for p in rows}) > 1
    , key=lambda labels: sorted(labels)[0])
    return {
        "schema": "CoAll.CoPredictDriftCounterfactual.R0",
        "scope": "SYNTHETIC_FIXTURES_ONLY_NOT_A_REAL_SESSION_OBSERVATION",
        "local_queue_sequences_ordered": True,
        "simulated_session_count": len(sessions),
        "simulated_claim_count": len(proposals),
        "name_only_false_merge_labels": conflicts,
        "same_definition_different_label_aliases": [
            sorted(labels) for labels in aliases
        ],
        "name_only_false_merge_count": len(conflicts),
        "name_only_alias_split_count": len(aliases),
        "typed_conflict_holds": len(conflicts),
        "typed_aliases_preserved": len(aliases),
        "independent_receiver_ack_count": 0,
        "accepted_canonical_units": 0,
        "auto_executed_changes": 0,
        "outcome": "HOLD_CONFLICTS_PRESERVE_ALIASES",
        "nonclaims": list(RULES),
    }


def qualify_hypothesis(forecast, now_utc):
    """Validate preregistration; outcome remains pending/unscored by itself."""
    _require(isinstance(forecast, Mapping), "FORECAST_REQUIRED")
    required = ("schema", "forecast_id", "issued_date", "target_deadline_utc",
                "target_cohort", "exposure_condition", "event_definition",
                "observation_method", "status", "probability",
                "actual_outcome", "review_carrier", "no_preemptive_actuation")
    _require(all(k in forecast for k in required), "FORECAST_FIELDS_REQUIRED")
    _require(forecast["schema"] == "CoAll.CoPredictDriftHypothesis.R0",
             "FORECAST_SCHEMA")
    _require(forecast["status"] == "PRE_REGISTERED_UNCALIBRATED",
             "NO_FALSE_FORECAST_RESOLUTION")
    _require(forecast["probability"] is None,
             "UNSOURCED_NUMERIC_CONFIDENCE")
    _require(forecast["actual_outcome"] is None,
             "UNVERIFIED_HIT_OR_MISS")
    _require(forecast["no_preemptive_actuation"] is True,
             "UNAUTHORIZED_PREEMPTIVE_CONTROL")
    _require(forecast["review_carrier"] == "EXISTING_COMEASURE_NOV10_FANIN",
             "DUPLICATE_REVIEW_CARRIER")
    for k in ("forecast_id", "target_cohort", "exposure_condition",
              "event_definition", "observation_method"):
        _require(isinstance(forecast[k], str) and forecast[k].strip(),
                 "EMPTY_FORECAST_SCOPE:" + k)
    _require(isinstance(forecast["issued_date"], str)
             and forecast["issued_date"] == "2026-11-07",
             "ISSUE_DATE_NOT_FIXED")
    deadline = _utc(forecast["target_deadline_utc"])
    now = _utc(now_utc)
    if now < deadline:
        return "PENDING_HYPOTHESIS_NOT_SCORED"
    return "HOLD_CENSORED_OR_REQUIRES_INDEPENDENT_OUTCOME_AUDIT"


def decision_from_evidence(forecast, independent_receipts, now_utc):
    """A mere count of source-claimed sessions cannot promote a forecast."""
    state = qualify_hypothesis(forecast, now_utc)
    _require(isinstance(independent_receipts, list),
             "RECEIPT_COLLECTION_REQUIRED")
    # Even two different strings/names may be the same author/process.
    # External trust and true failure-domain independence require an
    # authorized identity/provenance verifier; this pure module lacks one.
    if state.startswith("PENDING"):
        return state
    return ("HOLD_EXTERNAL_RECEIVER_ATTESTATION_REQUIRED"
            if independent_receipts else
            "CENSORED_NO_INDEPENDENT_OBSERVATIONS")
