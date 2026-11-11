#!/usr/bin/env python3
"""CoMeasure candidate: declared UX placeholders, never fabricated telemetry.

This is a pure source/projection gate, not a sensor, transport measurement,
actual CoSpeedo UI, source authentication, receiver ACK or deployment.
A placeholder reserves a visible location for missing evidence. An actual
measurement requires a separate CoMeasure observation and proof chain.
"""
from __future__ import annotations

from copy import deepcopy

KINDS = {
    "CoIb": {
        "kind": "RELATIONAL_HANDOFF_UNMEASURED",
        "measurement_gate": "SAME_WORKID_SOURCE_AND_INDEPENDENT_RECEIVER_READBACK",
        "established_metric_ref": "CoMx.receiver_pickup_fraction",
    },
    "CoEther": {
        "kind": "TRANSPORT_QUALITY_UNMEASURED",
        "measurement_gate": "DEFINED_WINDOW_SOURCE_AND_RECEIVER_TIMES_TRANSPORT_LOSS_BASELINE",
        "established_metric_ref": "CoTime.source_age",
    },
    "CoAsym": {
        "kind": "CONCEPTUAL_RESEARCH_LABEL",
        "measurement_gate": "DEFINE_FALSIFIABLE_OBSERVATION_AND_QUANTITY_KIND_FIRST",
        "established_metric_ref": None,
    },
}
STATES = ("UNKNOWN", "AWAITING_EVIDENCE", "NOT_APPLICABLE", "RESEARCH_CONCEPT")
FIELDS = frozenset({
    "schema", "slot", "kind", "state", "display", "reason", "wake_condition",
    "value", "unit_id", "observed_at_utc", "evidence_refs", "receiver_ack",
    "measurement_verified", "established_metric_ref", "measurement_gate",
    "authority", "nonclaims",
})
NONCLAIMS = (
    "PLACEHOLDER_NE_MEASUREMENT",
    "UNKNOWN_NE_ZERO",
    "LOCAL_DISPLAY_NE_RECEIVER_ACK",
    "RESEARCH_LABEL_NE_TELEMETRY",
    "NO_NETWORK_DEVICE_OR_PUBLICATION_EFFECT",
)
DISPLAY = {
    "UNKNOWN": "Not yet measured",
    "AWAITING_EVIDENCE": "Awaiting independent evidence",
    "NOT_APPLICABLE": "Not applicable (declared, not independently verified)",
    "RESEARCH_CONCEPT": "Research concept; no numeric metric",
}


def require(condition, label):
    # Do not use assert: optimized Python must fail closed too.
    if not condition:
        raise ValueError("HOLD_" + label)


def validate_placeholder(item):
    """Validate a narrow typed candidate. No effect, no implicit promotion."""
    require(type(item) is dict and set(item) == FIELDS, "PLACEHOLDER_FIELDS")
    require(item["schema"] == "CoAll.CoMeasure.UXPlaceholder.R0", "SCHEMA")
    slot = item["slot"]
    require(type(slot) is str and slot in KINDS, "UNKNOWN_SLOT")
    spec = KINDS[slot]
    require(item["kind"] == spec["kind"], "KIND_MISMATCH")
    state = item["state"]
    require(type(state) is str and state in STATES, "STATE")
    if slot == "CoAsym":
        require(state == "RESEARCH_CONCEPT", "CONCEPT_CANNOT_IMPLY_METRIC")
    else:
        require(state in ("UNKNOWN", "AWAITING_EVIDENCE", "NOT_APPLICABLE"),
                "UNMEASURED_SLOT_CANNOT_IMPLY_MEASUREMENT")
    require(item["display"] == DISPLAY[state], "DISPLAY_MUST_BE_HONEST")
    require(item["value"] is None and item["unit_id"] is None
            and item["observed_at_utc"] is None, "PLACEHOLDER_VALUE_FORBIDDEN")
    require(type(item["evidence_refs"]) is list and not item["evidence_refs"],
            "PLACEHOLDER_IS_NOT_EVIDENCE")
    require(item["receiver_ack"] is False
            and item["measurement_verified"] is False, "FALSE_EVIDENCE_PROMOTION")
    require(item["measurement_gate"] == spec["measurement_gate"],
            "GATE_MISMATCH")
    require(item["established_metric_ref"] == spec["established_metric_ref"],
            "MUST_REUSE_KNOWN_METRIC_REFERENCE")
    require(item["authority"] == "NONE", "PLACEHOLDER_HAS_NO_AUTHORITY")
    require(type(item["nonclaims"]) is list and item["nonclaims"] == list(NONCLAIMS),
            "MISSING_NONCLAIMS")
    reason, wake = item["reason"], item["wake_condition"]
    require(reason is None or (type(reason) is str and 1 <= len(reason.strip()) <= 160),
            "INVALID_REASON")
    require(wake is None or (type(wake) is str and 1 <= len(wake.strip()) <= 160),
            "INVALID_WAKE")
    if state == "AWAITING_EVIDENCE":
        require(wake is not None, "EVIDENCE_PLACEHOLDER_NEEDS_WAKE")
    if state == "NOT_APPLICABLE":
        require(reason is not None, "NOT_APPLICABLE_NEEDS_REASON")
    if state == "UNKNOWN":
        require(wake is None, "UNKNOWN_NE_UNOBSERVED_SCHEDULE")
    if state == "RESEARCH_CONCEPT":
        require(reason is not None, "RESEARCH_LABEL_NEEDS_LIMIT")
    return deepcopy(item)


def new_placeholder(slot, state="UNKNOWN", *, reason=None, wake_condition=None):
    require(type(slot) is str and slot in KINDS, "UNKNOWN_SLOT")
    spec = KINDS[slot]
    item = {
        "schema": "CoAll.CoMeasure.UXPlaceholder.R0",
        "slot": slot,
        "kind": spec["kind"],
        "state": state,
        "display": DISPLAY.get(state),
        "reason": reason,
        "wake_condition": wake_condition,
        "value": None,
        "unit_id": None,
        "observed_at_utc": None,
        "evidence_refs": [],
        "receiver_ack": False,
        "measurement_verified": False,
        "established_metric_ref": spec["established_metric_ref"],
        "measurement_gate": spec["measurement_gate"],
        "authority": "NONE",
        "nonclaims": list(NONCLAIMS),
    }
    return validate_placeholder(item)


def initial_projections():
    """Three optional slots. Not a request to add three UI panels."""
    return (
        new_placeholder("CoIb", "AWAITING_EVIDENCE",
                        wake_condition="independent_receiver_readback_for_one_WorkID"),
        new_placeholder("CoEther", "UNKNOWN"),
        new_placeholder("CoAsym", "RESEARCH_CONCEPT",
                        reason="conceptual optionality, no validated observation procedure"),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(initial_projections(), sort_keys=True, indent=2))
