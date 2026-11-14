#!/usr/bin/env python3
"""CoUniStax+ R0: bounded cross-substrate pattern *analogy* shadow crosswalk.

Does not import, scan, publish or propagate real patterns. This is an
offline schema/translation discriminator over explicitly synthetic,
public-safe records. Same motif does not imply same mechanism, cause,
ontological equivalence, value or permission.
"""
from __future__ import annotations

import re

SCHEMA = "CoUniStax.PatternSyntheticR0"
FIELDS = {
    "schema", "pattern_id", "substrate", "motif", "mechanism",
    "source_family", "source_sha256", "epistemic", "privacy",
    "authority", "observed_at", "receiver_ack",
}
MOTIFS = {"FEEDBACK", "DIFFUSION", "BRANCHING", "SELECTION", "RECOVERY"}
MECHANISMS = {
    "BIOLOGICAL": {"NATURAL_SELECTION", "CELL_SIGNALLING"},
    "SOCIAL": {"IMITATION", "GROUP_NORM"},
    "TECHNICAL": {"CONTROL_LOOP", "RETRY_BACKOFF"},
    "INFORMATIONAL": {"GRAPH_ROUTING", "ERROR_CORRECTION"},
}
IDENT = re.compile(r"[a-z][a-z0-9_.:-]{2,80}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")

BASE = {
    "schema": "CoUniStax.ShadowCrosswalkR0",
    "effect": "NONE",
    "automated_spread": False,
    "claim_causal_transfer": False,
    "claim_universal_law": False,
    "independent_receiver_ack": "NOT_ESTABLISHED",
    "new_authority": "NONE",
    "privacy_released": False,
    "evidence_transfer": "PROHIBITED",
    "reversible_translation": "NOT_PROVEN",
    "future_prediction": "NOT_ESTABLISHED",
    "release_authorized": False,
    "nonclaims": [
        "PATTERN_SIMILARITY_NE_COMMON_CAUSE",
        "REPEATED_COPY_NE_INDEPENDENT_REPLICATION",
        "SAME_MOTIF_NE_SAME_MECHANISM",
        "TRANSLATION_NE_SEMANTIC_EQUIVALENCE",
        "PATTERN_SPREAD_NE_BENEFIT",
        "SOURCE_TEST_NE_COTHEORYALL_PROOF",
        "ABSTRACT_STRUCTURE_NE_CONSCIOUSNESS_OR_METAPHYSICAL_EVIDENCE",
    ],
}


def _valid(p: object, now: int, max_age: int) -> bool:
    if not isinstance(p, dict) or set(p) != FIELDS:
        return False
    if p["schema"] != SCHEMA:
        return False
    if any(not isinstance(p[k], str) or not IDENT.fullmatch(p[k])
           for k in ("pattern_id", "source_family")):
        return False
    if not isinstance(p["source_sha256"], str) or not DIGEST.fullmatch(p["source_sha256"]):
        return False
    domain = p["substrate"]
    if domain not in MECHANISMS or p["motif"] not in MOTIFS:
        return False
    if p["mechanism"] not in MECHANISMS[domain]:
        return False
    if (p["epistemic"] != "SYNTHETIC_FIXTURE"
            or p["privacy"] != "PUBLIC_SAFE"
            or p["authority"] != "NONE"
            or p["receiver_ack"] is not False):
        return False
    return (type(p["observed_at"]) is int
            and 0 <= p["observed_at"] <= now
            and now - p["observed_at"] <= max_age)


def compare(source: object, target: object, *, now: int, max_age: int = 86400) -> dict:
    """No more than two patterns; no hidden crawler, worker, router or effect."""
    held = {**BASE, "state": "HOLD", "holds": [],
            "pattern_ids": [], "motif": None, "lost_relations": [],
            "candidate_tests": []}
    if type(now) is not int or now < 0 or type(max_age) is not int or max_age < 1:
        return {**held, "holds": ["INVALID_TIME"]}
    if not _valid(source, now, max_age) or not _valid(target, now, max_age):
        return {**held, "holds": ["UNQUALIFIED_OR_NONPUBLIC_PATTERN"]}
    if source["pattern_id"] == target["pattern_id"]:
        return {**held, "holds": ["DUPLICATE_PATTERN_ID"]}
    if source["source_family"] == target["source_family"]:
        return {
            **held,
            "state": "COPY_FAMILY_NOT_INDEPENDENT",
            "pattern_ids": sorted([source["pattern_id"], target["pattern_id"]]),
            "holds": ["COMMON_ORIGIN_CANNOT_COUNT_AS_INDEPENDENT_SUPPORT"],
        }
    if source["source_sha256"] == target["source_sha256"]:
        return {
            **held,
            "state": "COPY_DIGEST_NOT_INDEPENDENT",
            "pattern_ids": sorted([source["pattern_id"], target["pattern_id"]]),
            "holds": ["SAME_EXACT_SOURCE_CANNOT_COUNT_AS_INDEPENDENT_SUPPORT"],
        }
    if source["motif"] != target["motif"]:
        return {
            **held,
            "state": "NO_SHARED_MOTIF",
            "pattern_ids": sorted([source["pattern_id"], target["pattern_id"]]),
            "holds": ["HYPOTHESIS_NOT_SUPPORTED_BY_THIS_STRUCTURAL_MAPPING"],
        }
    loss = [
        "SOURCE_MECHANISM_CONTEXT",
        "MEASUREMENT_UNIT_AND_TIMESCALE",
        "CAUSAL_IDENTIFICATION",
        "EVIDENCE_VALIDITY",
        "RECEIVER_AUTHORITY_AND_CONSENT",
        "INDEPENDENCE_AND_REPLICATION",
        "VALUE_AND_HARM",
    ]
    if source["substrate"] != target["substrate"]:
        loss.append("CROSS_SUBSTRATE_DOMAIN_ASSUMPTIONS")
    return {
        **held,
        "state": "SHADOW_ANALOGY_ONLY",
        "pattern_ids": sorted([source["pattern_id"], target["pattern_id"]]),
        "motif": source["motif"],
        "lost_relations": sorted(loss),
        "holds": ["UNINFERRED_COMMON_MECHANISM", "NO_INDEPENDENT_EMPIRICAL_CONFIRMATION"],
        "candidate_tests": [
            "PRE_REGISTER_DISCRIMINATING_MECHANISM_TEST",
            "TEST_NULL_RANDOM_MOTIF_MATCH_BASELINE",
            "TEST_INVERSE_OR_BREAK_PATH",
            "MEASURE_TRANSLATION_LOSS_AND_FALSE_POSITIVE_RATE",
        ],
    }
