#!/usr/bin/env python3
"""CoDiscover+ R0: evidence-limited projection discovery on CoPriMath R0.

Show exactly which tested semantic distinctions survive each existing projection.
No crawling, provider calls, remote workers, new registry, or effectful action.
A collision proves information loss for the tested pair only, NOT in general.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve()
BRIDGE = HERE.with_name("CoPriMathNotationBridgeR0.py")
spec = importlib.util.spec_from_file_location("coprimath_r0_discovery_donor", BRIDGE)
if spec is None or spec.loader is None:
    raise RuntimeError("BRIDGE_IMPORT_UNAVAILABLE")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

SCHEMA = "CoDiscover.CoPriMathProjectionProbe.R0"
FACETS = (
    "source_ref", "observed_at_utc", "quantity_kind",
    "epistemic_state", "exact_base_value",
)
FORMATS = ("typed_json", "ascii", "presentation_mathml")
MAX_REQUIREMENTS = len(FACETS)


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def projection(measurement: dict, format_id: str) -> str:
    # Operate only on the tiny, registered CoPriMath source sublanguage.
    bridge.validate(measurement)
    if format_id == "typed_json":
        return json.dumps(bridge.canonical(measurement), sort_keys=True,
                          ensure_ascii=True, separators=(",", ":"))
    if format_id == "ascii":
        return bridge.ascii_projection(measurement)
    if format_id == "presentation_mathml":
        return bridge.mathml_presentation(measurement)
    raise bridge.Hold("UNKNOWN_PROJECTION_FORMAT")


def witness_pairs() -> dict:
    """Each pair differs in one declared, canonical-semantic facet.

    Exact_zero versus observed_zero is still a claim-state distinction,
    rather than a statement about any real instrument's precision.
    """
    origin = bridge.fixture("ratio", "1", 0)
    changes = {
        "source_ref": ("source_ref", "fixture:another-independent-source-claim"),
        "observed_at_utc": ("observed_at_utc", "2026-11-11T22:00:00Z"),
        "quantity_kind": ("quantity_kind", "probability"),
        "epistemic_state": ("epistemic_state", "EXACT_ZERO_CLAIM"),
        "exact_base_value": ("value", {"n": 1, "d": 1}),
    }
    pairs = {}
    for facet, (field, altered_value) in changes.items():
        altered = deepcopy(origin)
        altered[field] = altered_value
        bridge.validate(altered)
        # A distinction is material only when canonical meaning differs.
        if bridge.canonical_digest(origin) == bridge.canonical_digest(altered):
            raise bridge.Hold("BAD_WITNESS_PAIR_NO_SEMANTIC_CHANGE")
        pairs[facet] = (origin, altered)
    return pairs


def compare(required_facets: list[str]) -> dict:
    if type(required_facets) is not list or not 1 <= len(required_facets) <= MAX_REQUIREMENTS:
        raise bridge.Hold("INVALID_RECEIVER_REQUIREMENTS")
    if any(type(x) is not str or x not in FACETS for x in required_facets):
        raise bridge.Hold("UNKNOWN_RECEIVER_FACET")
    if len(set(required_facets)) != len(required_facets):
        raise bridge.Hold("DUPLICATE_REQUIREMENT")
    probes = witness_pairs()
    records = []
    for format_id in FORMATS:
        # The same source is projected three ways; no provider or device used.
        source = probes["source_ref"][0]
        rendered = projection(source, format_id)
        distinguish = {}
        for facet, (left, right) in probes.items():
            lhs = projection(left, format_id)
            rhs = projection(right, format_id)
            distinguish[facet] = lhs != rhs
        missing = sorted(facet for facet in required_facets
                         if not distinguish[facet])
        records.append({
            "format_id": format_id,
            "bytes_for_synthetic_example": len(rendered.encode("utf-8")),
            "projection_sha256": digest_text(rendered),
            "distinguished_facets_in_fixture": sorted(
                x for x, yes in distinguish.items() if yes),
            "collapsed_facets_in_fixture": sorted(
                x for x, yes in distinguish.items() if not yes),
            "receiver_required_facets_lost_in_fixture": missing,
            "qualifies_for_this_synthetic_probe": not missing,
            "loss_evidence": "PAIRWISE_OUTPUT_COLLISION_NOT_UNIVERSAL_PROOF",
        })
    return {
        "schema": SCHEMA,
        "state": "SYNTHETIC_READ_ONLY_FORMAT_COMPARISON",
        "semantic_source_sha256": bridge.canonical_digest(probes["source_ref"][0]),
        "receiver_requires": sorted(required_facets),
        "alternatives": records,
        "qualified_for_probe": sorted(x["format_id"] for x in records
                                      if x["qualifies_for_this_synthetic_probe"]),
        "deferred": sorted(x["format_id"] for x in records
                           if not x["qualifies_for_this_synthetic_probe"]),
        "resource_measurement": "UTF8_BYTES_ONLY_NOT_ENERGY_LATENCY_OR_USEFULNESS",
        "factual_source_validation": "NOT_TESTED",
        "independent_user_or_model_uptake": "NOT_TESTED",
        "effect_authority": "NONE",
        "processes_spawned": 0,
        "network_requests": 0,
        "external_receivers": 0,
        "rails": [
            "COLLISION_WITNESS_NE_UNIVERSAL_INCAPABILITY",
            "DISTINCT_OUTPUT_NE_SEMANTIC_ROUNDTRIP",
            "QUALIFIED_FIXTURE_NE_DEPLOYED_RECEIVER",
            "FORMAT_SIZE_NE_LIFECYCLE_COST",
            "ONE_SEMANTIC_SOURCE_MANY_PROJECTED_VIEWS",
        ],
    }


def main() -> None:
    profiles = {
        "human_quick_explanation": [
            "quantity_kind", "epistemic_state", "exact_base_value"],
        "machine_source_audit": list(FACETS),
        "visual_formula_only": ["exact_base_value"],
    }
    print(json.dumps({name: compare(requirements)
                      for name, requirements in profiles.items()},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
