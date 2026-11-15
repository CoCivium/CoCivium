"""Synthetic epistemic membrane for G_dSide/CoTheoryAll candidate claims.

This is NOT a new ontology, mind sensor, physical-energy model, spiritual
authority, verified consent, evidence authentication, or executable control
plane. A source string or control label can be forged. This module only
refuses unsafe inference and unbounded meta traversal in test fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

REFERENTS = frozenset({
    "PHYSICAL", "ABSTRACT", "SOCIAL_NORMATIVE", "EXPERIENTIAL",
    "SYMBOLIC", "CLAIMED_NONMATERIAL", "UNKNOWN",
})
EPISTEMIC = frozenset({
    "INSTRUMENT_OBSERVATION", "FORMAL_DERIVATION", "HUMAN_REPORT",
    "MODEL_INFERENCE", "SYMBOLIC_INTERPRETATION",
    "METAPHYSICAL_INTERPRETATION", "HYPOTHESIS",
    "CALIBRATED_INDEPENDENT_REPLICATION", "UNKNOWN",
})
NULL_STATES = frozenset({
    "NOT_APPLICABLE", "UNKNOWN", "NOT_OBSERVED", "EXPLICITLY_ABSENT",
    "BELOW_DETECTION", "WITHHELD", "CONTRADICTED",
    "NEGATIVE_WITH_DEFINED_SENSITIVITY",
})
REVIEW_CONTROLS = frozenset({
    "PREREGISTERED", "BLINDED", "ORDINARY_CAUSES_TESTED",
    "LEAKAGE_CONTROLLED", "INDEPENDENT_REPLICATION",
})


@dataclass(frozen=True)
class Claim:
    id: str
    referent: str
    epistemic: str
    source_ref: str
    asserts_external_cause: bool = False
    controls: frozenset[str] = frozenset()
    null_state: str = "NOT_APPLICABLE"
    effect_authority: str = "NONE"


def assess(claim: Claim) -> dict:
    """Preserve candidate interpretations; never infer external causation.

    REVIEW_ELIGIBLE is only a synthetic *structural* label. It does not
    verify a measurement, calibrate an instrument, or certify an investigator.
    """
    if not all(isinstance(x, str) and x.strip()
               for x in (claim.id, claim.source_ref)):
        raise ValueError("CLAIM_SOURCE_REQUIRED")
    if claim.referent not in REFERENTS or claim.epistemic not in EPISTEMIC:
        raise ValueError("EPISTEMIC_CLASS_UNKNOWN")
    if claim.null_state not in NULL_STATES:
        raise ValueError("NULL_STATE_UNKNOWN")
    if claim.effect_authority != "NONE":
        raise ValueError("NO_EFFECT_AUTHORITY_FROM_CLAIM")
    if not isinstance(claim.asserts_external_cause, bool):
        raise ValueError("CAUSE_FLAG_INVALID")
    if not isinstance(claim.controls, frozenset) or not all(
        isinstance(x, str) and x.strip() for x in claim.controls
    ):
        raise ValueError("CONTROLS_INVALID")
    if not claim.asserts_external_cause:
        causal_status = "NOT_ASSERTED"
    elif (claim.referent == "PHYSICAL"
          and claim.epistemic == "CALIBRATED_INDEPENDENT_REPLICATION"
          and REVIEW_CONTROLS.issubset(claim.controls)
          and claim.null_state == "NOT_APPLICABLE"):
        causal_status = "STRUCTURALLY_REVIEW_ELIGIBLE_NOT_VERIFIED"
    else:
        causal_status = "EXTERNAL_CAUSATION_NOT_ESTABLISHED"
    return {
        "claim_id": claim.id,
        "referent": claim.referent,
        "epistemic": claim.epistemic,
        "null_state": claim.null_state,
        "causal_status": causal_status,
        "interpretation_preserved": True,
        "effect_authority": "NONE",
        "source_authenticated": False,
        "mode": "SYNTHETIC_SOURCE_ONLY",
    }


def bounded_meta_walk(
    edges: Mapping[str, tuple[str, ...]],
    root: str,
    *,
    max_depth: int = 3,
    max_nodes: int = 8,
) -> dict:
    """Bounded read-only META_OF traversal; a cycle is not an infinite job.

    Revisiting a node on the current path is a cycle. A shared descendant
    from two branches is not automatically a cycle. Unvisited nodes remain
    addressable, not falsely declared absent.
    """
    if not isinstance(root, str) or not root.strip():
        raise ValueError("META_ROOT_REQUIRED")
    if (type(max_depth) is not int or not 0 <= max_depth <= 4 or
        type(max_nodes) is not int or not 1 <= max_nodes <= 32):
        raise ValueError("META_BUDGET_INVALID")
    stack = [(root, 0, (root,))]
    visited = []
    seen = set()
    cycle = False
    truncated = False
    while stack:
        node, depth, path = stack.pop()
        if node in seen:
            continue
        if len(visited) >= max_nodes:
            truncated = True
            break
        seen.add(node)
        visited.append(node)
        neighbors = edges.get(node, ())
        if not isinstance(neighbors, (tuple, list)):
            raise ValueError("META_EDGES_INVALID")
        if depth >= max_depth:
            truncated |= bool(neighbors)
            continue
        for child in reversed(neighbors):
            if not isinstance(child, str) or not child.strip():
                raise ValueError("META_NODE_INVALID")
            if child in path:
                cycle = True
            elif child not in seen:
                stack.append((child, depth + 1, path + (child,)))
    return {
        "visited": tuple(visited),
        "cycle_seen": cycle,
        "truncated": truncated,
        "effect_authority": "NONE",
        "mode": "SYNTHETIC_READ_ONLY",
    }
