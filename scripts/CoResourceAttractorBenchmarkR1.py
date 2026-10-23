#!/usr/bin/env python3
"""CoResourceAttractor R1: deterministic descriptor ranking benchmark.

This tool ranks already-described resources. It does not discover the internet,
activate workers, call models, mutate external systems, or grant authority.
Null/anti/counterfactual/speculative resource classes remain representable but
must be explicitly allowed by the need being evaluated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any

FORMAT = "CoResourceAttractorBenchmarkR1"
ELIGIBLE_LIFECYCLE = {"QUALIFIED", "COMPOSABLE", "OPTIONAL", "SELECTED", "USED", "RECEIPTED", "REEVO"}
PRIVACY_ORDER = {"PUBLIC": 0, "SHARED_BOUNDED": 1, "PRIVATE": 2, "RESTRICTED": 3}
RESOURCE_CLASS_GROUPS = {
    "demonstrated": {
        "software","file","repository","device","model","tool","test","data",
        "service","historical_artifact","render"
    },
    "experimental": {
        "synthetic_environment","alternative_representation","counterfactual",
        "anti_resource","null_resource","hypothetical_substrate"
    },
    "speculative": {"non_material_representation","CoSpirit_hypothesis"},
}


class AttractorError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AttractorError(message)


def fingerprint(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def validate_fixture(payload: Any) -> dict[str, Any]:
    require(isinstance(payload, dict), "fixture must be object")
    require(payload.get("format") == FORMAT, "wrong format")
    resources = payload.get("resources")
    needs = payload.get("needs")
    require(isinstance(resources, list) and resources, "resources required")
    require(isinstance(needs, list) and needs, "needs required")

    ids = set()
    all_classes = set().union(*RESOURCE_CLASS_GROUPS.values())
    for resource in resources:
        require(isinstance(resource, dict), "resource must be object")
        rid = resource.get("resource_id")
        require(isinstance(rid, str) and rid and rid not in ids, "resource_id invalid/duplicate")
        ids.add(rid)
        require(resource.get("resource_class") in all_classes, f"unknown resource class: {rid}")
        require(resource.get("privacy_class") in PRIVACY_ORDER, f"bad privacy: {rid}")
        require(resource.get("lifecycle_state") in {
            "UNKNOWN","DISCOVERED","DESCRIBED","QUALIFIED","COMPOSABLE","OPTIONAL",
            "SELECTED","USED","RECEIPTED","REEVO"
        }, f"bad lifecycle: {rid}")
        require(isinstance(resource.get("capabilities"), list), f"capabilities required: {rid}")
        require(isinstance(resource.get("interfaces"), list), f"interfaces required: {rid}")
        require(type(resource.get("evidence_strength")) is int and 0 <= resource["evidence_strength"] <= 3, f"bad evidence: {rid}")
        require(type(resource.get("currentness_days")) is int and resource["currentness_days"] >= 0, f"bad currentness: {rid}")
        require(type(resource.get("cost_band")) is int and 0 <= resource["cost_band"] <= 3, f"bad cost: {rid}")
        require(type(resource.get("coordination_debt")) is int and 0 <= resource["coordination_debt"] <= 3, f"bad debt: {rid}")
        for flag in ("reversible","optionality_exit","provenance"):
            require(type(resource.get(flag)) is bool, f"{flag} must be bool: {rid}")

    need_ids = set()
    for need in needs:
        nid = need.get("need_id")
        require(isinstance(nid, str) and nid and nid not in need_ids, "need_id invalid/duplicate")
        need_ids.add(nid)
        require(type(need.get("top_k")) is int and need["top_k"] >= 1, f"bad top_k: {nid}")
        require(type(need.get("min_evidence_strength")) is int and 0 <= need["min_evidence_strength"] <= 3, f"bad min evidence: {nid}")
        require(type(need.get("max_currentness_days")) is int and need["max_currentness_days"] >= 0, f"bad freshness: {nid}")
        require(need.get("privacy_ceiling") in PRIVACY_ORDER, f"bad privacy ceiling: {nid}")
        require(set(need.get("gold_relevant_ids", [])).issubset(ids), f"unknown gold id: {nid}")
        require(set(need.get("allowed_resource_classes", [])).issubset(all_classes), f"unknown class in need: {nid}")
    return payload


def eligibility(resource: dict[str, Any], need: dict[str, Any], excluded: set[str] | None = None) -> tuple[bool, list[str]]:
    excluded = excluded or set()
    reasons = []
    if resource["resource_id"] in excluded:
        reasons.append("EXCLUDED_FOR_PROBE")
    if resource["lifecycle_state"] not in ELIGIBLE_LIFECYCLE:
        reasons.append("NOT_QUALIFIED_LIFECYCLE")
    if resource["resource_class"] not in set(need["allowed_resource_classes"]):
        reasons.append("RESOURCE_CLASS_NOT_ALLOWED")
    if resource["availability"] not in set(need["allowed_availability"]):
        reasons.append("AVAILABILITY_NOT_ALLOWED")
    if resource["authority_state"] not in set(need["allowed_authority"]):
        reasons.append("AUTHORITY_NOT_ALLOWED")
    if PRIVACY_ORDER[resource["privacy_class"]] > PRIVACY_ORDER[need["privacy_ceiling"]]:
        reasons.append("PRIVACY_EXCEEDS_CEILING")
    if resource["evidence_strength"] < need["min_evidence_strength"]:
        reasons.append("EVIDENCE_TOO_WEAK")
    if resource["currentness_days"] > need["max_currentness_days"]:
        reasons.append("STALE")
    required = set(need["required_capabilities"])
    if not required.issubset(set(resource["capabilities"])):
        reasons.append("MISSING_REQUIRED_CAPABILITY")
    return not reasons, reasons


def descriptor_score(resource: dict[str, Any], need: dict[str, Any]) -> int:
    caps = set(resource["capabilities"])
    interfaces = set(resource["interfaces"])
    preferred_caps = set(need["preferred_capabilities"])
    preferred_interfaces = set(need["preferred_interfaces"])
    freshness_bonus = max(0, 10 - resource["currentness_days"] // 7)
    return (
        30 * len(caps & preferred_caps)
        + 15 * len(interfaces & preferred_interfaces)
        + 12 * resource["evidence_strength"]
        + 10 * int(resource["provenance"])
        + 6 * int(resource["reversible"])
        + 6 * int(resource["optionality_exit"])
        + freshness_bonus
        - 4 * resource["cost_band"]
        - 3 * resource["coordination_debt"]
    )


def keyword_score(resource: dict[str, Any], need: dict[str, Any]) -> int:
    haystack = " ".join([
        resource["label"],
        resource["description"],
        " ".join(resource.get("tags", [])),
    ])
    return len(tokens(need["query"]) & tokens(haystack))


def eligible_resources(resources: list[dict[str, Any]], need: dict[str, Any], excluded: set[str] | None = None) -> list[dict[str, Any]]:
    return [r for r in resources if eligibility(r, need, excluded)[0]]


def deterministic_tiebreak(resource_id: str) -> str:
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()


def rank_descriptor(resources: list[dict[str, Any]], need: dict[str, Any], excluded: set[str] | None = None) -> list[str]:
    pool = eligible_resources(resources, need, excluded)
    return [
        r["resource_id"] for r in sorted(
            pool,
            key=lambda r: (-descriptor_score(r, need), deterministic_tiebreak(r["resource_id"]))
        )
    ]


def rank_keyword(resources: list[dict[str, Any]], need: dict[str, Any], excluded: set[str] | None = None) -> list[str]:
    pool = eligible_resources(resources, need, excluded)
    return [
        r["resource_id"] for r in sorted(
            pool,
            key=lambda r: (-keyword_score(r, need), deterministic_tiebreak(r["resource_id"]))
        )
    ]


def rank_random(resources: list[dict[str, Any]], need: dict[str, Any], seed: str, excluded: set[str] | None = None) -> list[str]:
    ids = [r["resource_id"] for r in eligible_resources(resources, need, excluded)]
    rng = random.Random(int(hashlib.sha256((seed + need["need_id"]).encode()).hexdigest()[:16], 16))
    rng.shuffle(ids)
    return ids


def metric(ranking: list[str], need: dict[str, Any]) -> dict[str, Any]:
    top = ranking[:need["top_k"]]
    gold = set(need["gold_relevant_ids"])
    hits = len(set(top) & gold)
    return {
        "top_k": need["top_k"],
        "selected": top,
        "hits": hits,
        "precision": hits / len(top) if top else 0.0,
        "recall": hits / len(gold) if gold else 1.0,
    }


def benchmark(payload: dict[str, Any]) -> dict[str, Any]:
    validate_fixture(payload)
    resources = payload["resources"]
    seed = fingerprint({"format": payload["format"], "resource_ids": [r["resource_id"] for r in resources]})
    methods = {"descriptor": [], "keyword": [], "random": []}
    failure_probes = []

    for need in payload["needs"]:
        rankings = {
            "descriptor": rank_descriptor(resources, need),
            "keyword": rank_keyword(resources, need),
            "random": rank_random(resources, need, seed),
        }
        for name, ranking in rankings.items():
            methods[name].append({"need_id": need["need_id"], **metric(ranking, need)})

        probe = need.get("failure_probe")
        if probe:
            excluded = set(probe["disable_resource_ids"])
            reranked = rank_descriptor(resources, need, excluded)
            top = reranked[:need["top_k"]]
            failure_probes.append({
                "need_id": need["need_id"],
                "disabled": sorted(excluded),
                "expected_fallback_id": probe["expected_fallback_id"],
                "selected": top,
                "pass": probe["expected_fallback_id"] in top,
            })

    summary = {}
    for name, rows in methods.items():
        total_hits = sum(row["hits"] for row in rows)
        total_slots = sum(len(row["selected"]) for row in rows)
        total_gold = sum(len(next(n["gold_relevant_ids"] for n in payload["needs"] if n["need_id"] == row["need_id"])) for row in rows)
        summary[name] = {
            "hits": total_hits,
            "selected_slots": total_slots,
            "gold_count": total_gold,
            "micro_precision": total_hits / total_slots if total_slots else 0.0,
            "micro_recall": total_hits / total_gold if total_gold else 1.0,
        }

    speculative_selected_in_standard_needs = []
    resource_by_id = {r["resource_id"]: r for r in resources}
    for row in methods["descriptor"]:
        for rid in row["selected"]:
            if resource_by_id[rid]["resource_class"] in RESOURCE_CLASS_GROUPS["speculative"]:
                speculative_selected_in_standard_needs.append({"need_id": row["need_id"], "resource_id": rid})

    return {
        "schema": "CoResourceAttractorBenchmarkReportR1",
        "state": "BOUNDED_PUBLIC_FIXTURE__ZERO_EXECUTION",
        "fixture_fingerprint": fingerprint(payload),
        "resource_count": len(resources),
        "need_count": len(payload["needs"]),
        "methods": methods,
        "summary": summary,
        "failure_probes": failure_probes,
        "all_failure_probes_pass": all(p["pass"] for p in failure_probes),
        "descriptor_beats_keyword_hits": summary["descriptor"]["hits"] > summary["keyword"]["hits"],
        "descriptor_not_worse_than_random_hits": summary["descriptor"]["hits"] >= summary["random"]["hits"],
        "speculative_selected_in_standard_needs": speculative_selected_in_standard_needs,
        "effects": {
            "workers_started": 0,
            "provider_sessions_created": 0,
            "external_mutations": 0,
            "authority_granted": 0,
            "network_calls": 0,
        },
        "nonclaims": [
            "SYNTHETIC_FIXTURE_NE_REAL_WORLD_RECALL",
            "MANUAL_GOLD_LABELS_NE_INDEPENDENT_GROUND_TRUTH",
            "DESCRIPTOR_SCORE_NE_TRUTH",
            "FINDABLE_NE_QUALIFIED",
            "OPTIONAL_NE_ACTIVE",
            "SPECULATIVE_NE_PHYSICAL",
            "NULL_RESOURCE_NE_AVAILABLE_TOOL",
            "BENCHMARK_PASS_NE_RUNTIME_ADOPTION",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.fixture.read_text(encoding="utf-8"))
        result = benchmark(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, AttractorError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
