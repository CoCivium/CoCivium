#!/usr/bin/env python3
"""Deterministic synthetic policy-selection SMOKE test, NOT a fair predictive benchmark."""
import json, random, argparse
DIMS=("agency","wellbeing","ecology","resilience","optionality","relational","worst_off")
WEIGHTS=(.14,.12,.24,.16,.13,.09,.12)

def run(seed=261108,trials=200):
    rng=random.Random(seed)
    names=("supply","demand","hybrid","gdside","random")
    totals={p:dict(utility=0.0,ecology=0.0,wins=0,unsafe=0) for p in names}
    counterexamples=[]
    for i in range(trials):
        actions=[]
        for j in range(8):
            vals=[rng.uniform(-1,1) for _ in DIMS]
            supply,demand,cost=rng.random(),rng.random(),rng.random()
            harm=max(0,-vals[2])*rng.random()
            permitted=(harm<.65 and cost<.9)
            utility=sum(v*w for v,w in zip(vals,WEIGHTS))-.18*cost-.2*harm
            actions.append(dict(id=j,values=vals,supply=supply,demand=demand,cost=cost,harm=harm,permitted=permitted,utility=utility))
        eligible=[a for a in actions if a["permitted"]]
        assert eligible
        scores={
            "supply":lambda a:a["supply"],
            "demand":lambda a:a["demand"],
            "hybrid":lambda a:.5*(a["supply"]+a["demand"]),
            "gdside":lambda a:sum(w*(v+rng.gauss(0,.30)) for v,w in zip(a["values"],WEIGHTS))-.18*a["cost"]-.2*a["harm"],
            "random":lambda a:rng.random()
        }
        selected={p:max(eligible,key=score) for p,score in scores.items()}
        oracle=max(eligible,key=lambda a:a["utility"])
        for p,a in selected.items():
            t=totals[p]
            t["utility"]+=a["utility"]
            t["ecology"]+=a["values"][2]
            t["wins"]+=int(a["id"]==oracle["id"])
            t["unsafe"]+=int(not a["permitted"])
        if selected["gdside"]["utility"]<selected["hybrid"]["utility"]:
            counterexamples.append(dict(trial=i,gdside=round(selected["gdside"]["utility"],5),hybrid=round(selected["hybrid"]["utility"],5)))
    return dict(schema="CoPullVectorSyntheticBenchmark.R0",seed=seed,trials=trials,synthetic=True,simulation_only=True,dimensions=DIMS,weights=WEIGHTS,scores={p:dict(mean_utility=round(v["utility"]/trials,6),mean_ecology=round(v["ecology"]/trials,6),oracle_selection_rate=round(v["wins"]/trials,4),unsafe_selections=v["unsafe"]) for p,v in totals.items()},gdside_loses_to_hybrid_count=len(counterexamples),first_counterexamples=counterexamples[:5],nonclaims=["NOT_REAL_WORLD_VALIDATION","NOT_MULTIMODEL_INDEPENDENCE","NOT_24_HOUR_SURVIVAL","NOT_RUNTIME_AUTHORITY"])

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,default=261108)
    parser.add_argument("--trials",type=int,default=200)
    args=parser.parse_args()
    print(json.dumps(run(args.seed,args.trials),indent=2))
