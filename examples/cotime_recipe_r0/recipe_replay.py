#!/usr/bin/env python3
"""Synthetic CoTime x CoRecipeCache replay; deterministic, offline and read-only."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

CLASSES = {"OBSERVED", "SCENARIO", "HYPOTHESIS", "COUNTERFACTUAL", "UNKNOWN"}
LANES = {"software", "symbolic"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def parse_time(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC timestamp required")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def validate(records):
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    seen = set()
    keys = ("id", "domain", "class", "lane", "event_at", "recorded_at", "predicate", "source_ref")
    for item in records:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k] for k in keys):
            raise ValueError("incomplete source record")
        if item["id"] in seen:
            raise ValueError("duplicate source identity")
        seen.add(item["id"])
        if item["class"] not in CLASSES or item["lane"] not in LANES:
            raise ValueError("unsupported evidence class or lane")
        if not item["source_ref"].startswith("fixture://"):
            raise ValueError("only synthetic fixture provenance allowed")
        if parse_time(item["recorded_at"]) < parse_time(item["event_at"]):
            raise ValueError("recorded before event")


def replay(records, as_of):
    validate(records)
    cutoff = parse_time(as_of)
    available = sorted([x for x in records if parse_time(x["recorded_at"]) <= cutoff], key=lambda x: x["id"])
    observed = [x for x in available if x["class"] == "OBSERVED" and x["lane"] == "software"]
    indexes = [x for x in observed if x["domain"] == "indexing" and x["predicate"] == "success_signal_without_effect_proof"]
    audio = [x for x in observed if x["domain"] == "audio" and x["predicate"] == "playback_queued_without_hearing_proof"]
    mock = [x for x in observed if x["domain"] == "indexing" and x["predicate"] == "isolated_mock_canary_pass"]
    lineage = [x["id"] for x in indexes[:1] + audio[:1]]
    candidates = []
    if len(lineage) == 2:
        candidates.append({
            "id": "recipe/evidence-bound-status",
            "operation": "CoCompose",
            "state": "PROPOSED",
            "source_ids": lineage,
            "need": "Avoid success messages that imply effects never observed.",
            "preconditions": ["exact source provenance", "status event boundary", "reversible test"],
            "test": "Inject a successful-looking event without downstream receipt; require UNKNOWN/HOLD.",
            "falsifier": "A supported case where the signal itself proves the downstream effect.",
            "effect": "NONE",
            "authority": "RESEARCH_ONLY"
        })
    candidates.extend([
        {"id": "branch/null", "operation": "CoNull", "state": "RESERVED", "source_ids": [], "effect": "NONE", "authority": "RESEARCH_ONLY"},
        {"id": "branch/inverse", "operation": "CoInvert", "state": "CHALLENGE", "source_ids": lineage, "effect": "NONE", "authority": "RESEARCH_ONLY"}
    ])
    symbolic = [x for x in available if x["lane"] == "symbolic"]
    if symbolic:
        candidates.append({"id": "branch/gnosis-g_d-symbolic", "operation": "CoReframe",
                           "state": "HYPOTHESIS_ONLY", "source_ids": [x["id"] for x in symbolic],
                           "effect": "NONE", "authority": "NONE"})
    state = "INSUFFICIENT_CROSS_DOMAIN_EVIDENCE"
    if len(lineage) == 2:
        state = "MOCK_TEST_PASSED_LIMITED_SCOPE" if mock else "UNTESTED_CROSS_DOMAIN_CANDIDATE"
    artifact = {
        "schema": "CoTimeRecipeReplay.R0", "as_of": as_of,
        "source_manifest_sha256": sha256(records),
        "evidence_class": "SYNTHETIC_FIXTURE", "external_effects": 0,
        "visible_sources": [
            {"id": x["id"], "class": x["class"], "source_sha256": sha256(x),
             "event_at": x["event_at"], "recorded_at": x["recorded_at"]} for x in available],
        "historical_interpretation": {
            "object": "interpretation/ambiguous-status", "state": state,
            "historical_events_modified": False,
            "supporting_sources": lineage + [x["id"] for x in mock],
            "production_effect_proven": False
        },
        "future_branches": [
            {"class": "SCENARIO", "target": "2027-01-01T00:00:00Z",
             "question": "Will boundary-labeled status reduce false successes?", "state": "UNTESTED"},
            {"class": "COUNTERFACTUAL", "target": "2027-01-01T00:00:00Z",
             "question": "What if the success signal remained unqualified?", "state": "NOT_HISTORY"}],
        "candidates": candidates,
        "elected": [x["id"] for x in candidates if x["state"] == "PROPOSED"][:1],
        "residuals": ["No independently measured earbud delivery",
                      "No proven production index coverage", "No measured real-world benefit"],
        "rails": ["PAST_EVENT_NE_EDITABLE", "SCENARIO_NE_FACT",
                  "MOCK_PASS_NE_PRODUCTION", "SYMBOLIC_NE_OBSERVED",
                  "RECIPE_NE_PROVEN_SYNERGY"]
    }
    artifact["receipt_sha256"] = sha256(artifact)
    return artifact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=Path(__file__).with_name("fixture.json"))
    parser.add_argument("--as-of", default="2026-11-02T22:00:00Z")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(replay(json.loads(args.fixture.read_text(encoding="utf-8")), args.as_of),
                        indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
