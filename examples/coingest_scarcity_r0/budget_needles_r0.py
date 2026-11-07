#!/usr/bin/env python3
"""CoBudgetNeedles R0: scarce resource growth as a testable hypothesis.

Synthetic, bounded simulation only. NO new resource lease, permission,
worker, human obligation, financial spend or autonomous runtime.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from allocator import RESOURCE_KEYS, plan, qualified

NON_GROWABLE = frozenset(("cash_cents", "human_minutes"))
SIMULABLE = frozenset(RESOURCE_KEYS) - NON_GROWABLE

NEEDLES = (
    {"id":"more_cpu", "mode":"supply", "resource":"cpu_units", "delta":5,
     "reason":"Hypothesis: new independently measured CPU capacity becomes available"},
    {"id":"more_review", "mode":"supply", "resource":"reviewer_minutes", "delta":5,
     "reason":"Hypothesis: qualified review/verifier capacity expands"},
    {"id":"more_slots", "mode":"supply", "resource":"worker_slots", "delta":2,
     "reason":"Hypothesis: compatible authorized worker slots become usable"},
    {"id":"more_energy", "mode":"supply", "resource":"energy_units", "delta":4,
     "reason":"Hypothesis: actual energy capacity can support more computation"},
    {"id":"cache_cpu", "mode":"cost_reduction", "resource":"cpu_units", "delta":2,
     "target":"fresh_source_retrieval",
     "reason":"Hypothesis: verified cache lowers retrieval cost for this work item"},
)
NONCLAIMS = [
    "PREDICTED_NE_AVAILABLE",
    "FORECAST_NE_LEASE_OR_AUTHORIZATION",
    "SYNTHETIC_GAIN_NE_REAL_BENEFIT",
    "ZERO_HUMAN_MINUTES_NE_ABSENCE_OF_GOVERNANCE",
    "CASH_BUDGET_NE_SPENDING_AUTHORITY",
    "EFFICIENCY_NE_NEW_PHYSICAL_CAPACITY",
    "MANY_SLOTS_NE_INDEPENDENT_WORKERS",
    "SINGLE_NEEDLE_NE_ENTIRE_BOTTLENECK",
    "MARGINAL_GROWTH_NE_MONOTONIC_FOREVER",
    "SAME_PROVIDER_NE_INDEPENDENT_FAILURE_DOMAIN",
]

def check_budget(b):
    if not isinstance(b,dict) or set(b) != set(RESOURCE_KEYS):
        raise ValueError("EXACT_BUDGET_KEYS_REQUIRED")
    if any(type(v) is not int or v<0 for v in b.values()):
        raise ValueError("BAD_BUDGET_VALUE")
    return b

def apply_needle(budget, candidates, needle):
    """Return distinct forecast copies; caller's resource inventory never mutates."""
    check_budget(budget)
    if not isinstance(candidates,list) or not isinstance(needle,dict):
        raise ValueError("BAD_FORECAST_INPUT")
    if not all(isinstance(needle.get(k),str) and needle[k] for k in ("id","mode","resource","reason")):
        raise ValueError("FORECAST_PROVENANCE_MISSING")
    mode = needle["mode"]
    allowed={"id","mode","resource","reason","delta"} | ({"target"} if mode=="cost_reduction" else set())
    if set(needle)!=allowed:
        raise ValueError("UNDECLARED_FORECAST_FIELD")
    if needle["resource"] not in SIMULABLE:
        raise ValueError("CASH_OR_HUMAN_CAPACITY_HELD")
    delta=needle.get("delta")
    if type(delta) is not int or not 0<delta<=20:
        raise ValueError("BAD_FORECAST_DELTA")
    b=copy.deepcopy(budget)
    cs=copy.deepcopy(candidates)
    if mode=="supply":
        b[needle["resource"]] += delta
    elif mode=="cost_reduction":
        targets=[c for c in cs if c.get("work_id")==needle["target"]]
        if len(targets)!=1 or not isinstance(targets[0].get("resources"),dict):
            raise ValueError("UNBOUND_EFFICIENCY_TARGET")
        cost=targets[0]["resources"].get(needle["resource"])
        if type(cost) is not int or cost<delta:
            raise ValueError("BAD_EFFICIENCY_FLOOR")
        targets[0]["resources"][needle["resource"]]-=delta
    else:
        raise ValueError("UNKNOWN_MODE")
    return b,cs

def insertion_deficits(candidates, budget, selected):
    """Local insertion diagnostics, NOT a claim of globally optimal shadow prices."""
    valid,_ = qualified(candidates)
    chosen=[c for c in valid if c["work_id"] in selected]
    selected_domains={c["collision_domain"] for c in chosen}
    used={k:sum(c["resources"][k] for c in chosen) for k in RESOURCE_KEYS}
    out={}
    for c in valid:
        if c["work_id"] in selected:
            continue
        out[c["work_id"]]={
            "resource_deficits":{k:used[k]+c["resources"][k]-budget[k] for k in RESOURCE_KEYS
                                 if used[k]+c["resources"][k]>budget[k]},
            "collision_with_selected":c["collision_domain"] in selected_domains,
        }
    return out

def compare(fixture):
    if not isinstance(fixture,dict) or not isinstance(fixture.get("candidates"),list):
        raise ValueError("FIXTURE_REQUIRED")
    base=copy.deepcopy(check_budget(fixture.get("budget")))
    candidates=copy.deepcopy(fixture["candidates"])
    actual=plan(candidates,base,policy="frontier")
    forecasts=[]
    for needle in NEEDLES:
        b,cs=apply_needle(base,candidates,needle)
        forecast=plan(cs,b,policy="frontier")
        forecasts.append({
            "id":needle["id"],
            "mode":needle["mode"],
            "resource":needle["resource"],
            "hypothesis":needle["reason"],
            "forecast_budget":b,
            "projected_selected":forecast["selected"],
            "projected_score":forecast["projected_utility_score_pctpoints"],
            "projected_gain":forecast["projected_utility_score_pctpoints"]-actual["projected_utility_score_pctpoints"],
            "changed_optimal_selection":forecast["selected"]!=actual["selected"],
            "forecast_only":True,
            "observed_new_resource":"NOT_OBSERVED",
            "authorization":"NOT_GRANTED",
        })
    b,cs=copy.deepcopy(base),copy.deepcopy(candidates)
    for n in NEEDLES:
        b,cs=apply_needle(b,cs,n)
    combined=plan(cs,b,policy="frontier")
    return {
        "schema":"CoAll.CoBudgetNeedles.R0.synthetic",
        "current_known_budget_source":"SYNTHETIC_FIXTURE_NOT_LIVE_INVENTORY",
        "baseline_budget":base,
        "baseline_selected":actual["selected"],
        "baseline_projected_score":actual["projected_utility_score_pctpoints"],
        "insertion_deficits_not_shadow_prices":insertion_deficits(candidates,base,actual["selected"]),
        "forecast_cases":forecasts,
        "joint_forecast":{
            "budget_if_all_available":b,
            "projected_selected":combined["selected"],
            "projected_score":combined["projected_utility_score_pctpoints"],
            "projected_gain":combined["projected_utility_score_pctpoints"]-actual["projected_utility_score_pctpoints"],
            "sum_of_separate_gains":sum(f["projected_gain"] for f in forecasts),
        },
        "live_budget_increase":0, "new_workers_started":0,
        "cash_spent_cents":0, "actual_human_minutes":0,
        "empirical_efficiency_improvement":"NOT_MEASURED",
        "nonclaims":NONCLAIMS,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    src=args.fixture.read_bytes()
    report=compare(json.loads(src.decode("utf-8")))
    report["fixture_sha256"]=hashlib.sha256(src).hexdigest()
    if args.output.exists():
        raise SystemExit("HOLD: output exists, no clobber")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True))
if __name__=="__main__":
    main()
