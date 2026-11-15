#!/usr/bin/env python3
"""Transparent synthetic allocation comparison. NOT an economic or divine law.
No external dependencies. Deterministic across seeds and scenarios.
"""
import argparse
import hashlib
import json
import math
import random
from statistics import mean
from pathlib import Path

POLICIES=("demand","supply","hybrid","gdside","random")
EFF=(0.90,1.05,1.25,1.50)
WEALTH=(0.60,0.86,1.14,1.60)
NEEDS=(32.0,39.0,45.0,53.0)
K=1800.0
STEPS=36

def weighted(parts, budget):
    total=sum(max(0,p) for p in parts)
    return [budget * max(0,p)/total for p in parts] if total else [0.0]*len(parts)

def max_min_alloc(need, productivity, budget):
    # Progressive equalization: raise all satisfaction ratios until the
    # next group's target is met or the resource budget is exhausted.
    req=[max(0,n)/max(e,1e-9) for n,e in zip(need,productivity)]
    tot=sum(req)
    q=min(1.0,budget/tot) if tot else 1.0
    result=[v*q for v in req]
    rem=max(0.0,budget-sum(result))
    # Extra resource is held in reserve rather than forced into waste.
    return result,rem

def policy_action(name,need,productivity,wealth,stock,rng):
    gross_req=sum(n/e for n,e in zip(need,productivity))
    # All methods see the same constraints: withdrawal <= 14% of stock and
    # <= gross requirements, and they operate under the same stochastic world.
    feasible=min(0.14*stock,gross_req)
    factor={"demand":1.00,"supply":1.00,"hybrid":0.92,"gdside":0.84,"random":1.00}[name]
    budget=feasible*factor
    if name=="demand":
        shares=[n*w/e for n,w,e in zip(need,wealth,productivity)]
    elif name=="supply":
        shares=[e*e for e in productivity]
    elif name=="hybrid":
        shares=[0.6*n/e + 0.4*30*e for n,e in zip(need,productivity)]
    elif name=="random":
        shares=[rng.random()+0.01 for _ in need]
    else:
        allocation,_=max_min_alloc(need,productivity,budget)
        return allocation
    return weighted(shares,budget)

def checked_extraction(allocation, stock, groups):
    """Fail-closed allocation boundary in ordinary AND optimized Python."""
    if type(allocation) not in (list, tuple) or len(allocation) != groups:
        raise ValueError("HOLD_ALLOCATION_SHAPE")
    if any(type(x) not in (int, float) or not math.isfinite(x) or x < 0
           for x in allocation):
        raise ValueError("HOLD_ALLOCATION_NONFINITE_OR_NEGATIVE")
    extraction = sum(allocation)
    if (not math.isfinite(extraction) or
        extraction > stock * 0.14 + 1e-7 or
        extraction > stock + 1e-7):
        raise ValueError("HOLD_EXTRACTION_CAP")
    return extraction

def conditions(seed,steps=STEPS):
    r=random.Random(seed)
    return [dict(demand=[max(0.7,r.gauss(1,0.15)) for _ in NEEDS],
                 productivity=[max(0.4,r.gauss(1,0.11)) for _ in NEEDS],
                 replenishment=max(-100,r.gauss(0,18)),
                 shock=r.random()<0.11) for _ in range(steps)]

def run_one(seed,policy,steps=STEPS,trace=False):
    if policy not in POLICIES:
        raise ValueError("HOLD_UNKNOWN_POLICY")
    if type(steps) is not int or steps <= 0:
        raise ValueError("HOLD_INVALID_STEPS")
    stock=1120.0
    rng=random.Random(seed+991832)
    world=conditions(seed,steps)
    group_sums=[0.0]*len(NEEDS)
    min_sats=[]
    mean_sats=[]
    outputs=[]
    rights_violations=0
    depleted=0
    rows=[]
    for t,w in enumerate(world):
        needs=[n*factor for n,factor in zip(NEEDS,w['demand'])]
        efficiency=[e*factor for e,factor in zip(EFF,w['productivity'])]
        allocation=policy_action(policy,needs,efficiency,WEALTH,stock,rng)
        extraction=checked_extraction(allocation,stock,len(NEEDS))
        produced=[a*e for a,e in zip(allocation,efficiency)]
        saturation=[min(1.0,p/n) for p,n in zip(produced,needs)]
        min_sats.append(min(saturation))
        mean_sats.append(mean(saturation))
        outputs.append(sum(produced))
        rights_violations+=sum(z<0.5 for z in saturation)
        group_sums=[v+z for v,z in zip(group_sums,saturation)]
        regeneration=0.27*stock*(1-stock/K)
        disruption=(-70.0 if w['shock'] else 0.0)+w['replenishment']
        stock=max(0.0,min(K,stock+regeneration-extraction+disruption))
        if stock<0.15*K: depleted+=1
        if trace:
            rows.append(dict(step=t+1,stock=round(stock,4),extraction=round(extraction,4),
                             min_satisfaction=round(min_sats[-1],5),
                             mean_satisfaction=round(mean_sats[-1],5),
                             output=round(outputs[-1],4)))
    return {"seed":seed,"policy":policy,"min_group_satisfaction":min(group_sums)/steps,
            "mean_satisfaction":mean(mean_sats),"mean_step_min":mean(min_sats),
            "mean_output":mean(outputs),"final_ecological_stock":stock,
            "rights_violations":rights_violations,"depletion_steps":depleted,
            "steps":steps,"trace":rows if trace else None}

def summarize(seeds,steps=STEPS):
    results={p:[run_one(seed,p,steps) for seed in seeds] for p in POLICIES}
    metrics=("min_group_satisfaction","mean_satisfaction","mean_step_min","mean_output",
             "final_ecological_stock","rights_violations","depletion_steps")
    return {p:{metric:round(mean(row[metric] for row in results[p]),5) for metric in metrics}
            for p in POLICIES}

def deterministic_sha(obj):
    payload=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def make_report(nseed=80,steps=STEPS):
    seeds=list(range(1,nseed+1))
    summary=summarize(seeds,steps)
    return {"schema":"CoAll.GdSide.SyntheticAllocationBenchmark.R0",
            "epistemic_class":"SYNTHETIC_TOY_MODEL_NOT_REAL_WORLD_ECONOMICS",
            "originality":"Illustrative original baseline implementation, not novel mathematical proof",
            "assumptions":{
                "groups":len(NEEDS),"efficiency":EFF,"wealth":WEALTH,"base_needs":NEEDS,
                "regeneration":"0.27*stock*(1-stock/1800)",
                "extraction_cap":"min(0.14*stock, total needs in resource-equivalent units)",
                "budgets":{"demand":1.0,"supply":1.0,"hybrid":0.92,"gdside":0.84,"random":1.0},
                "forecast":"none; stochastic scenarios shared by seed",
                "critical_warning":"The GdSide ecology/fairness priority is encoded in its allocation policy and extraction budget. Results cannot establish superiority outside these assumptions."},
            "fixed_seeds":seeds,"steps":steps,"summary":summary,
            "source_code_file":"simulate.py", "tests":"test_simulate.py",
            "evidence_boundary":"No field measurements, no value consensus, no divine/metaphysical inference, no human welfare policy recommendation"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seeds',type=int,default=80)
    ap.add_argument('--steps',type=int,default=STEPS)
    ap.add_argument('--out',type=Path,default=Path(__file__).parent/'results.json')
    args=ap.parse_args()
    report=make_report(args.seeds,args.steps)
    report['summary_sha256']=deterministic_sha(report['summary'])
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':'SYNTHETIC_COMPLETE','seeds':args.seeds,'steps':args.steps,
                      'summary_sha256':report['summary_sha256'],'summary':report['summary']},indent=2))
if __name__=='__main__':main()
