#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_RIGHTS = {
    "USER_AUTHORED_OR_USER_LICENSED",
    "COCIVIUM_ORIGINAL",
    "VERIFIED_PUBLIC_DOMAIN",
    "VERIFIED_OPEN_LICENSE",
    "POINTER_ONLY",
}

def score(o: dict[str, Any]) -> int:
    s = o["scores"]
    positive = (
        s["relevance"] + s["decision_value"] + s["recurrence_value"] +
        s["contradiction_value"] + s["novelty"] + s["evidence_quality"] +
        s["recovery_value"] + s["human_time_saved"]
    )
    negative = (
        s["attention_cost"] + s["repetition"] + s["ambiguity"] +
        s["staleness"] + s["manipulation_risk"]
    )
    return positive - negative

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--policy", type=Path, required=True)
    args = p.parse_args()

    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    policy = json.loads(args.policy.read_text(encoding="utf-8"))

    assert corpus["schema"] == "CoWisdomCorpus.R0.v0.1"
    assert len(corpus["objects"]) == 12
    assert policy["default_projection"]["primary_insights"] == 1
    assert policy["default_projection"]["counterpoints_or_limits"] == 1

    held = []
    eligible = []
    by_id = {o["wisdom_id"]: o for o in corpus["objects"]}

    for o in corpus["objects"]:
        if o["rights_state"] not in ALLOWED_RIGHTS or o["privacy"] != "PUBLIC":
            held.append(o)
            continue
        eligible.append(o)

    primary_candidates = [o for o in eligible if o["surface_budget"] == "PRIMARY_ELIGIBLE"]
    assert primary_candidates
    primary = max(primary_candidates, key=score)

    counter_candidates = [
        o for o in eligible
        if o.get("counterpoint_of") == primary["wisdom_id"]
        or o["wisdom_id"] in primary.get("counterpoints", [])
    ]
    assert counter_candidates, "primary must have an eligible counterpoint"
    counterpoint = max(counter_candidates, key=score)

    deeper_candidates = [
        o for o in eligible
        if o["wisdom_id"] not in {primary["wisdom_id"], counterpoint["wisdom_id"]}
        and o["surface_budget"] in {"DEEPER_ELIGIBLE","AMBIENT_LOW_FREQUENCY"}
    ]
    assert deeper_candidates
    deeper = max(deeper_candidates, key=score)

    assert all(o["wisdom_id"] != "cw-011" for o in [primary,counterpoint,deeper])
    assert any(o["wisdom_id"] == "cw-011" for o in held)

    report = {
        "schema": "CoWisdomProjectionReport.R0.v0.1",
        "state": "BOUNDED_ORIGINAL_CORPUS_PASS__NO_EXTERNAL_INGESTION",
        "corpus_count": len(corpus["objects"]),
        "eligible_count": len(eligible),
        "held_count": len(held),
        "projection": {
            "primary": primary["wisdom_id"],
            "counterpoint": counterpoint["wisdom_id"],
            "deeper": deeper["wisdom_id"],
        },
        "held_ids": [o["wisdom_id"] for o in held],
        "addressable_not_displayed_ids": [
            o["wisdom_id"] for o in eligible
            if o["wisdom_id"] not in {primary["wisdom_id"], counterpoint["wisdom_id"], deeper["wisdom_id"]}
        ],
        "effects": {
            "network_calls": 0,
            "external_sends": 0,
            "provider_mutations": 0,
            "account_changes": 0,
            "background_workers_started": 0,
        },
        "rails": [
            "ADDRESSABLE_NE_DISPLAYED",
            "MORE_QUOTES_NE_MORE_WISDOM",
            "RIGHTS_UNKNOWN_HELD",
            "PRIMARY_REQUIRES_COUNTERPOINT",
            "HARD_GATES_BEFORE_RANKING",
            "CONTINUAL_NE_ALWAYS_RUNNING",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
