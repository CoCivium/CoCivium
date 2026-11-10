"""CoRel/CoBraid bounded dependency-wave planner.

Pure, read-only planning. It neither schedules nor executes work.
Receipt states must come from a different, qualified observer.
"""
from collections import defaultdict

STATES = {"PROVEN", "UNPROVEN", "HELD", "FAILED"}
MAX_NODES = 64

def plan(nodes, limit=8):
    """Return proof-safe ordered waves and visible blockers.

    A wave includes ONLY UNPROVEN nodes whose prerequisites are PROVEN
    or are earlier waves in this plan. The latter are *hypothetical*:
    later waves cannot execute until the previous wave's real receipts exist.
    """
    if not isinstance(nodes, list) or len(nodes) > MAX_NODES or limit < 1 or limit > 16:
        raise ValueError("invalid bounded graph or wave limit")
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)) or any(not isinstance(i,str) or not i for i in ids):
        raise ValueError("duplicate/empty node IDs")
    by_id={n["id"]:n for n in nodes}
    for n in nodes:
        if n.get("state") not in STATES:
            raise ValueError("unknown state")
        if not isinstance(n.get("deps"),list) or len(n["deps"]) != len(set(n["deps"])):
            raise ValueError("malformed prerequisites")
        if any(d not in by_id or d==n["id"] for d in n["deps"]):
            raise ValueError("unknown/self prerequisite")
        if not n.get("evidence_owner"):
            raise ValueError("missing evidence owner")
        if n["state"]=="PROVEN" and not n.get("receipt"):
            raise ValueError("PROVEN requires a receipt reference")
    proven={n["id"] for n in nodes if n["state"]=="PROVEN"}
    unproven={n["id"] for n in nodes if n["state"]=="UNPROVEN"}
    unresolved=set(unproven)
    hypothetical=set(proven)
    waves=[]
    for _ in range(limit):
        eligible=sorted(i for i in unresolved if set(by_id[i]["deps"]).issubset(hypothetical))
        if not eligible: break
        # Alternative lanes may prepare in parallel; effects are never started here.
        waves.append({"step":len(waves)+1,"candidate_parallel":eligible,
                      "state":"PLAN_ONLY_RECHECK_RECEIPTS_BEFORE_EACH_WAVE"})
        unresolved.difference_update(eligible)
        hypothetical.update(eligible)
    blocked={}
    for i in sorted(unresolved):
        missing=[d for d in by_id[i]["deps"] if d not in hypothetical]
        blocked[i]={"reason":"PREREQUISITE_NOT_QUALIFIED" if missing else "WAVE_BUDGET",
                    "unqualified":missing}
    for n in nodes:
        if n["state"] in {"HELD","FAILED"}:
            blocked[n["id"]]={"reason":n["state"],"unqualified":[]}
    # Cycle detection across all declared dependencies, including already PROVEN.
    visiting=set(); visited=set()
    def visit(i):
        if i in visiting: raise ValueError("dependency cycle")
        if i in visited:return
        visiting.add(i)
        for d in by_id[i]["deps"]: visit(d)
        visiting.remove(i);visited.add(i)
    for i in sorted(ids):visit(i)
    return {
       "schema":"CoRel.BraidWavePlan.R0","execution":"NONE",
       "proven_receipts":{i:by_id[i]["receipt"] for i in sorted(proven)},
       "waves":waves,"blocked":blocked,
       "warnings":["PLANNED_PREDECESSOR_NE_RECEIPTED_PREDECESSOR",
                   "PARALLEL_READINESS_NE_PARALLEL_EFFECT_AUTHORITY",
                   "SOURCE_CI_NE_RECEIVER_ACCEPTANCE"]
    }
