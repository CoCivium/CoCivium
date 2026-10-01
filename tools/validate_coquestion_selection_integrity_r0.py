#!/usr/bin/env python3
import itertools
import json
from pathlib import Path

P=Path("fixtures/cotime/coquestion_selection_integrity_r0.json")

def eligible(q):
    return not q["effect_gated"] and not q["privacy_hold"] and not q["authority_hold"]

def elect(d):
    qs=[q for q in d["questions"] if eligible(q)]
    # Bounded synthetic objective:
    # maximize discriminatory value, then minimize cost, then stable ID.
    ranked=sorted(qs,key=lambda q:(-q["discriminatory_value"],q["cost"],q["id"]))
    selected=[]
    covered=set()
    need_falsify=d["policy"]["require_falsification_coverage"]

    if need_falsify:
        falsifiers=[q for q in ranked if q["can_falsify_preferred"]]
        if falsifiers:
            selected.append(falsifiers[0])
            covered.update(falsifiers[0]["discriminates"])

    while len(selected)<d["policy"]["max_selected"]:
        remaining=[q for q in ranked if q["id"] not in {x["id"] for x in selected}]
        if not remaining:
            break
        remaining.sort(key=lambda q:(
            -len(set(q["discriminates"])-covered),
            -q["discriminatory_value"],
            q["cost"],
            q["id"]
        ))
        q=remaining[0]
        selected.append(q)
        covered.update(q["discriminates"])

    return sorted(q["id"] for q in selected)

def basic_valid_selection(d, ids):
    by={q["id"]:q for q in d["questions"]}
    if any(i not in by for i in ids):
        return False
    selected=[by[i] for i in ids]
    if not selected or len(selected)>d["policy"]["max_selected"]:
        return False
    if any(not eligible(q) for q in selected):
        return False
    if d["policy"]["require_falsification_coverage"] and not any(q["can_falsify_preferred"] for q in selected):
        return False
    covered=set()
    for q in selected:
        covered.update(q["discriminates"])
    if d["policy"]["require_live_alternative_coverage"] and not set(d["live_hypotheses"]).issubset(covered):
        return False
    return True

def valid_selection(d, ids):
    if not basic_valid_selection(d,ids):
        return False

    by={q["id"]:q for q in d["questions"]}
    selected=[by[i] for i in ids]
    selected_cost=sum(q["cost"] for q in selected)
    selected_value=sum(q["discriminatory_value"] for q in selected)

    # Reject a selection when another eligible bounded set preserves all hard
    # validity requirements, has at least as much synthetic discriminatory
    # value, and costs strictly less. This catches set-level domination that
    # per-question pairwise checks miss.
    pool=[q for q in d["questions"] if eligible(q)]
    for n in range(1,d["policy"]["max_selected"]+1):
        for combo in itertools.combinations(pool,n):
            alt_ids=[q["id"] for q in combo]
            if set(alt_ids)==set(ids):
                continue
            if not basic_valid_selection(d,alt_ids):
                continue
            alt_cost=sum(q["cost"] for q in combo)
            alt_value=sum(q["discriminatory_value"] for q in combo)
            if alt_cost < selected_cost and alt_value >= selected_value:
                return False
    return True

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    selected=elect(d)
    expected=sorted(d["expected"]["selected_ids"])
    if selected!=expected:
        raise SystemExit(f"FAIL:ELECTION got={selected} expected={expected}")
    if not valid_selection(d,selected):
        raise SystemExit("FAIL:BASELINE_SELECTION_INVALID")
    if d["policy"]["effect_authority_before"] is not False or d["policy"]["effect_authority_after"] is not False:
        raise SystemExit("FAIL:AUTHORITY_DRIFT")
    for n in d["negative_cases"]:
        got=valid_selection(d,n["selected_ids"])
        if got is not n["expected_valid"]:
            raise SystemExit("FAIL:"+n["id"])
    if "Q_HIGH_VALUE_GATED" in selected:
        raise SystemExit("FAIL:GATED_QUESTION_SELECTED_FOR_EXECUTION")
    if "Q_EXPENSIVE_REPLICATION" in selected:
        raise SystemExit("FAIL:EXPENSIVE_NEAR_EQUIVALENT_SELECTED")
    print("PASS: discriminating question selection preserves falsification, alternatives, set-level cost dominance and effect gates")

if __name__=="__main__":
    main()
