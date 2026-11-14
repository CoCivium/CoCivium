#!/usr/bin/env python3
"""Independent *code path* reference for the CoFlow R1 retrospective output.

Deliberately does not import corun.py, use its DAG, scheduler, task helpers,
or reuse previously computed results. This is NOT independent evidence,
a different data source, a legacy product, or an independent human reviewer.
"""
from __future__ import annotations

from collections import Counter

SOURCE_SCHEMA = "CoCivium.CoFlowAnchorDeltaRetrospective.R1"
WORK_ID = "corun-coflow-priorgraph-r0"
STRATA = frozenset((
    "WORKED_SCOPED", "PARTIAL_OR_BLOCKED",
    "FAILED_HISTORICAL_REPAIRED", "FAILED_STILL_OBSERVED",
))
STATUSES = frozenset(("PASS", "FAIL", "HELD", "PARTIAL"))
CASE_FIELDS = ("id", "stratum", "ledger_status", "observed_at",
               "record_id", "release_test", "epistemic_boundary")


def independent_reference(source: dict) -> dict:
    """Direct sequential transform from CoFlow R1 source to result contract.

    No nodes, no tasks, no futures: iterates the source in a separate algorithm.
    Fails on material ambiguity instead of manufacturing a success.
    """
    if not isinstance(source, dict) or source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("oracle source schema mismatch")
    original = source.get("cases")
    if not isinstance(original, list) or not 1 <= len(original) <= 64:
        raise ValueError("oracle case budget exceeded")
    indexed = {}
    for item in original:
        if not isinstance(item, dict) or not all(k in item for k in CASE_FIELDS):
            raise ValueError("oracle missing case fields")
        key = item["id"]
        if not isinstance(key, str) or key in indexed or len(key) > 32:
            raise ValueError("oracle duplicate or invalid id")
        if item["stratum"] not in STRATA or item["ledger_status"] not in STATUSES:
            raise ValueError("oracle unrecognized source classification")
        for field in ("record_id", "release_test", "epistemic_boundary", "observed_at"):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValueError("oracle absent evidence field")
        mate = item.get("paired_case_id")
        if mate is not None and not isinstance(mate, str):
            raise ValueError("oracle invalid pair type")
        indexed[key] = item

    summaries = []
    link_pairs = set()
    for key in sorted(indexed):
        item = indexed[key]
        summaries.append({
            "id": key,
            "stratum": item["stratum"],
            "ledger_status": item["ledger_status"],
            "observed_at": item["observed_at"],
            "record_id": item["record_id"],
            "release_test": item["release_test"],
            "epistemic_boundary": item["epistemic_boundary"],
            "paired_case_id": item.get("paired_case_id"),
            "receiver_acceptance": "UNKNOWN",
        })
        partner = item.get("paired_case_id")
        if partner is not None:
            if partner not in indexed:
                raise ValueError("oracle pair target absent")
            link_pairs.add(tuple(sorted((key, partner))))

    relationships = []
    for left, right in sorted(link_pairs):
        a, b = indexed[left], indexed[right]
        relationships.append({
            "members": [left, right],
            "reciprocal_references":
                a.get("paired_case_id") == right and b.get("paired_case_id") == left,
            "statuses": {left: a["ledger_status"], right: b["ledger_status"]},
            "causal_claim": "NOT_PROVEN",
        })

    counts = dict(Counter(item["stratum"] for item in original))
    warnings = [
        "PURPOSIVE_SAMPLE_NOT_PROSPECTIVE_OR_CAUSAL",
        "SCOPED_PASS_NOT_RECEIVER_ADOPTION",
        "ONE_PIPELINE_NOT_INDEPENDENT_REPLICATION",
    ]
    if any(not relation["reciprocal_references"] for relation in relationships):
        warnings.append("NONRECIPROCAL_PAIR_REFERENCE")
    src = {
        "schema": SOURCE_SCHEMA,
        "selection_bias": source.get("sample_design", {}).get("selection_bias", "UNKNOWN"),
        "case_count": len(original),
        "source_state": source.get("state", "UNKNOWN"),
    }
    return {
        "work_id": WORK_ID,
        "source": src,
        "audit": {
            "cases": summaries,
            "pairs": relationships,
            "strata_counts": counts,
            "historical_sample_only": True,
        },
        "counterevidence": {
            "warnings": warnings,
            "independence": "NOT_ESTABLISHED",
            "human_minutes": None,
            "proposed_discriminators": [
                "independent receiver readproof",
                "prospective A/B task completion",
                "record human active minutes and corrections",
                "cold reconstruction under independent failure domain",
            ],
        },
        "effect_class": "READ_ONLY_LOCAL",
        "promotion": "HELD_PENDING_PROSPECTIVE_HUMAN_BENEFIT",
    }
