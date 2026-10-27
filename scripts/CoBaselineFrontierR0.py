#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
from typing import Any

def key(rec: dict[str, Any], fields: list[str]) -> tuple:
    return tuple(rec[f] for f in fields)

def floor_ok(rec: dict[str, Any], floors: dict[str, float]) -> bool:
    return all(rec["metrics"].get(name, float("-inf")) >= floor for name, floor in floors.items())

def dominates(a: dict[str, Any], b: dict[str, Any], directions: dict[str, str]) -> bool:
    better_or_equal = True
    strictly_better = False
    for m, direction in directions.items():
        av, bv = a["metrics"][m], b["metrics"][m]
        if direction == "max":
            if av < bv: better_or_equal = False
            if av > bv: strictly_better = True
        else:
            if av > bv: better_or_equal = False
            if av < bv: strictly_better = True
    return better_or_equal and strictly_better

def run(fixture: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    dirs = fixture["metric_directions"]
    floors = fixture["hard_floors"]
    fields = policy["comparability_key"]

    groups = defaultdict(list)
    held = []
    for r in fixture["records"]:
        if r["state"] != "PASS":
            held.append({"result_id":r["result_id"],"reason":"NOT_PASS"})
            continue
        missing = [m for m in dirs if m not in r["metrics"]]
        if missing:
            held.append({"result_id":r["result_id"],"reason":"MISSING_METRICS","missing":missing})
            continue
        if not floor_ok(r, floors):
            held.append({"result_id":r["result_id"],"reason":"HARD_FLOOR_FAIL"})
            continue
        groups[key(r, fields)].append(r)

    families = []
    all_preserved = []
    for group_key, records in sorted(groups.items(), key=lambda x: str(x[0])):
        ordered = sorted(records, key=lambda r:r["observed_at"])
        frontier = []
        for r in ordered:
            if any(dominates(other, r, dirs) for other in ordered if other["result_id"] != r["result_id"]):
                pass
            else:
                frontier.append(r)

        latest = ordered[-1]
        best_recovery = max(ordered, key=lambda r:r["metrics"]["recovery_success"])
        labels = {}
        for r in ordered:
            rs = []
            if r["result_id"] == latest["result_id"]:
                rs.append("LAST_PROVEN")
            if any(r["result_id"] == f["result_id"] for f in frontier):
                rs += ["BEST_PROVEN","BEST_CURRENT","BEST_SAFE","BEST_RECEIVER"]
            if r["result_id"] == best_recovery["result_id"]:
                rs.append("BEST_RECOVERY")
            labels[r["result_id"]] = sorted(set(rs))

        families.append({
            "comparability_key": dict(zip(fields, group_key)),
            "record_ids":[r["result_id"] for r in ordered],
            "pareto_frontier_ids":[r["result_id"] for r in frontier],
            "champion_labels":labels
        })
        all_preserved.extend(r["result_id"] for r in ordered)

    return {
        "schema":"CoBaseline.FrontierReport.R0.v0.1",
        "state":"PASS_SYNTHETIC_BASELINE_FRONTIER_REGISTRY",
        "family_count":len(families),
        "families":families,
        "held":held,
        "preserved_result_ids":sorted(all_preserved + [h["result_id"] for h in held]),
        "effects":{"network_calls":0,"external_messages":0,"provider_mutations":0,"device_mutations":0},
        "rails":policy["rails"]
    }

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",type=Path,required=True)
    p.add_argument("--policy",type=Path,required=True)
    args=p.parse_args()
    report=run(json.loads(args.fixture.read_text()),json.loads(args.policy.read_text()))
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
