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
        # Open research umbrella, not a physical substance or an observed bridge.
        "kind": "OPEN_INTERSTICE_RESEARCH_PLACEHOLDER",
        "measurement_gate": "TYPE_HYPOTHESIS_AND_TEST_DOMAIN_SPECIFIC_EVIDENCE_BEFORE_MERGER",
        "established_metric_ref": None,
    },
    "CoEther.Transport": {
        # Measurable transport is one optional descendant, not all of CoEther.
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
    "MYTHOS_G_D_RELATION_NE_EMPIRICAL_CAUSE",
    "CANDIDATE_MERGER_NE_VERIFIED_IDENTITY",
)
DISPLAY = {
    "UNKNOWN": "Not yet measured",
    "AWAITING_EVIDENCE": "Awaiting independent evidence",
    "NOT_APPLICABLE": "Not applicable (declared, not independently verified)",
    "RESEARCH_CONCEPT": "Research concept; no numeric metric",
}
# Keep diverse candidate gaps visible without asserting a common mechanism.
ETHER_FACETS = (
    "PHYSICAL_OBSERVATION",
    "VIRTUAL_REPRESENTATION",
    "MYTHOS_NARRATIVE",
    "PHILOSOPHICAL_G_D_INQUIRY",
    "UNKNOWN_OBSERVER_GAP",
)
ETHER_DISPLAY = "Open questions; no empirical bridge established"
ETHER_REASON = (
    "Open relational space across physical observations, virtual models, "
    "mythos and philosophical inquiry; no verified common mechanism."
)


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
    if slot in ("CoAsym", "CoEther"):
        require(state == "RESEARCH_CONCEPT", "CONCEPT_CANNOT_IMPLY_METRIC")
    else:
        require(state in ("UNKNOWN", "AWAITING_EVIDENCE", "NOT_APPLICABLE"),
                "UNMEASURED_SLOT_CANNOT_IMPLY_MEASUREMENT")
    truthful_display = ETHER_DISPLAY if slot == "CoEther" else DISPLAY[state]
    require(item["display"] == truthful_display, "DISPLAY_MUST_BE_HONEST")
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


def new_placeholder(slot, state=None, *, reason=None, wake_condition=None):
    require(type(slot) is str and slot in KINDS, "UNKNOWN_SLOT")
    if state is None:
        state = "RESEARCH_CONCEPT" if slot in ("CoEther", "CoAsym") else "UNKNOWN"
    if slot == "CoEther" and state == "RESEARCH_CONCEPT" and reason is None:
        reason = ETHER_REASON
    spec = KINDS[slot]
    item = {
        "schema": "CoAll.CoMeasure.UXPlaceholder.R0",
        "slot": slot,
        "kind": spec["kind"],
        "state": state,
        "display": ETHER_DISPLAY if slot == "CoEther" else DISPLAY.get(state),
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


# A separate thought experiment can relate CoEther facets, but it cannot
# turn metaphor, representation or correlation into causal proof.
RELATION_EDGES = ("ANALOGY_TO", "INTERPRETED_AS", "MODELS", "MERGER_HYPOTHESIS")
RELATION_NONCLAIMS = (
    "SYNTHETIC_PROPOSAL_NE_EXTERNAL_OBSERVATION",
    "ANALOGY_NE_CAUSE",
    "CANDIDATE_MERGER_NE_IDENTITY",
    "NO_INDEPENDENT_RECEIVER_OR_PUBLICATION",
)
RELATION_FIELDS = frozenset({
    "schema", "proposal_id", "source_facet", "target_facet",
    "edge_type", "interpretation_domain", "hypothesis",
    "discriminator", "ordinary_alternative", "status",
    "source_scope", "evidence_refs", "receiver_ack",
    "verified_bridge", "authority", "nonclaims",
})
EMPIRICAL_EDGES = frozenset({"MODELS", "MERGER_HYPOTHESIS"})
SYMBOLIC_EDGES = frozenset({"ANALOGY_TO", "INTERPRETED_AS"})
EMPIRICAL_FACETS = frozenset({
    "PHYSICAL_OBSERVATION", "VIRTUAL_REPRESENTATION", "UNKNOWN_OBSERVER_GAP",
})


def validate_relation_proposal(item):
    """Admit bounded *hypotheses*, never proven cross-domain mergers."""
    require(type(item) is dict and set(item) == RELATION_FIELDS,
            "RELATION_FIELDS")
    require(item["schema"] == "CoAll.CoEther.RelationProposal.R0",
            "RELATION_SCHEMA")
    identifier = item["proposal_id"]
    require(type(identifier) is str and identifier.startswith("synthetic:")
            and 11 <= len(identifier) <= 80
            and all(c.isalnum() or c in "._:-" for c in identifier),
            "RELATION_ID")
    left, right = item["source_facet"], item["target_facet"]
    require(type(left) is str and type(right) is str
            and left in ETHER_FACETS and right in ETHER_FACETS
            and left != right, "DISTINCT_REGISTERED_FACETS_REQUIRED")
    edge = item["edge_type"]
    require(type(edge) is str and edge in RELATION_EDGES, "RELATION_EDGE")
    require(type(item["hypothesis"]) is str
            and 10 <= len(item["hypothesis"].strip()) <= 200,
            "BOUNDED_HYPOTHESIS")
    require(item["status"] == "PROPOSED_UNVERIFIED"
            and item["source_scope"] == "SYNTHETIC_FIXTURE_ONLY",
            "RELATION_CANNOT_SELF_PROMOTE")
    require(type(item["evidence_refs"]) is list and not item["evidence_refs"]
            and item["receiver_ack"] is False
            and item["verified_bridge"] is False
            and item["authority"] == "NONE",
            "RELATION_NO_FALSE_EVIDENCE_OR_AUTHORITY")
    require(item["nonclaims"] == list(RELATION_NONCLAIMS),
            "RELATION_NONCLAIMS")
    discriminant = item["discriminator"]
    alternative = item["ordinary_alternative"]
    if edge in EMPIRICAL_EDGES:
        require(item["interpretation_domain"] == "EMPIRICAL_TEST_PROPOSAL",
                "EMPIRICAL_DOMAIN")
        require(left in EMPIRICAL_FACETS and right in EMPIRICAL_FACETS,
                "NO_EMPIRICAL_MERGER_WITH_MYTHOS_OR_G_D")
        if edge == "MODELS":
            require(left == "VIRTUAL_REPRESENTATION"
                    and right == "PHYSICAL_OBSERVATION",
                    "MODEL_DIRECTION")
        require(type(discriminant) is str
                and 15 <= len(discriminant.strip()) <= 240
                and type(alternative) is str
                and 10 <= len(alternative.strip()) <= 240,
                "REQUIRES_DISCRIMINATOR_AND_ALTERNATIVE")
    else:
        require(item["interpretation_domain"] == "NARRATIVE_OR_PHILOSOPHICAL"
                and discriminant is None and alternative is None,
                "SYMBOLIC_RELATION_NE_INSTRUMENT_RESULT")
        if edge == "INTERPRETED_AS":
            require(right in ("MYTHOS_NARRATIVE", "PHILOSOPHICAL_G_D_INQUIRY"),
                    "INTERPRETATION_TARGET")
    return deepcopy(item)


def propose_relation(proposal_id, source_facet, target_facet, edge_type,
                     hypothesis, *, discriminator=None, ordinary_alternative=None):
    """Build synthetic unverified proposals only; no cross-domain conclusion."""
    edge_domain = ("EMPIRICAL_TEST_PROPOSAL" if edge_type in EMPIRICAL_EDGES
                   else "NARRATIVE_OR_PHILOSOPHICAL")
    item = {
        "schema": "CoAll.CoEther.RelationProposal.R0",
        "proposal_id": proposal_id,
        "source_facet": source_facet,
        "target_facet": target_facet,
        "edge_type": edge_type,
        "interpretation_domain": edge_domain,
        "hypothesis": hypothesis,
        "discriminator": discriminator,
        "ordinary_alternative": ordinary_alternative,
        "status": "PROPOSED_UNVERIFIED",
        "source_scope": "SYNTHETIC_FIXTURE_ONLY",
        "evidence_refs": [],
        "receiver_ack": False,
        "verified_bridge": False,
        "authority": "NONE",
        "nonclaims": list(RELATION_NONCLAIMS),
    }
    return validate_relation_proposal(item)


def initial_projections():
    """Three optional slots. Not a request to add three UI panels."""
    return (
        new_placeholder("CoIb", "AWAITING_EVIDENCE",
                        wake_condition="independent_receiver_readback_for_one_WorkID"),
        new_placeholder("CoEther"),
        new_placeholder("CoAsym", "RESEARCH_CONCEPT",
                        reason="conceptual optionality, no validated observation procedure"),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(initial_projections(), sort_keys=True, indent=2))
