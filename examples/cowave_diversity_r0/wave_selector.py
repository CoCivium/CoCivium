#!/usr/bin/env python3
"""CoWave diversity selector R0: synthetic, pure, source-free, no scheduling/effects."""
from __future__ import annotations
from collections import Counter

REQUIRED = ("id","front","method","substrate","failure_domain","evidence_target","expected_value","cost","eligible")

def choose(candidates, history, *, budget=3, protected_fronts=()):
    """Elect bounded differentiated experiments, not workers or permissions.

    History contains accepted/attempted wave signatures. Repetition is allowed
    when required for evidence, recovery, regression or a protected front.
    """
    if not isinstance(candidates,list) or not isinstance(history,list) or len(candidates)>1000 or len(history)>1000:
        raise ValueError("BOUNDED_INPUT_REQUIRED")
    if type(budget) is not int or budget<0 or budget>100:
        raise ValueError("INVALID_BUDGET")
    seen=set()
    valid=[]
    for c in candidates:
        if not isinstance(c,dict) or any(k not in c for k in REQUIRED):
            raise ValueError("INVALID_CANDIDATE")
        if not all(isinstance(c[k],str) and c[k] for k in REQUIRED[:6]):
            raise ValueError("INVALID_CANDIDATE_IDENTITY")
        if c["id"] in seen:
            raise ValueError("DUPLICATE_CANDIDATE")
        seen.add(c["id"])
        if type(c["eligible"]) is not bool or not isinstance(c["expected_value"],(int,float)) or not isinstance(c["cost"],(int,float)):
            raise ValueError("INVALID_METRICS")
        if not (0<=c["expected_value"]<=1 and 0<=c["cost"]<=1):
            raise ValueError("METRIC_RANGE")
        if c["eligible"]:
            valid.append(c)
    if any(not isinstance(h,(list,tuple)) or len(h)!=4 or not all(isinstance(v,str) for v in h) for h in history):
        raise ValueError("INVALID_HISTORY")
    historic={tuple(h) for h in history}
    selected=[]; used=set()
    protected=set(protected_fronts)
    while len(selected)<budget:
        ranked=[]
        for c in valid:
            if c["id"] in used:
                continue
            signature=(c["front"],c["method"],c["substrate"],c["failure_domain"])
            prior=signature in historic
            active={x["front"] for x in selected}
            diversity=sum(1 for k in ("method","substrate","failure_domain") if c[k] not in {x[k] for x in selected})
            score=(2.0 if c["front"] in protected and c["front"] not in active else 0.0) + (0.7 if not prior else 0.0) + diversity*0.16 + c["expected_value"] - c["cost"]*0.5
            ranked.append((round(score,6),c["id"],c))
        if not ranked:
            break
        ranked.sort(key=lambda x:(-x[0],x[1]))
        best=ranked[0][2]
        used.add(best["id"]);selected.append(best)
    return {"schema":"CoWave.DiversitySelection.R0","selected_ids":[c["id"] for c in selected],
            "protected_fronts_covered":sorted({c["front"] for c in selected}&protected),
            "uncovered_protected_fronts":sorted(protected-{c["front"] for c in selected}),
            "repeat_signatures":sum((c["front"],c["method"],c["substrate"],c["failure_domain"]) in historic for c in selected),
            "effect_count":0,"state":"PROPOSAL_ONLY",
            "nonclaims":["NOVELTY_NE_USEFULNESS","DIVERSITY_NE_INDEPENDENCE","SELECTION_NE_RUNTIME","FRONT_NOT_SELECTED_NE_RETIRED"]}
