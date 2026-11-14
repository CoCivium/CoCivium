#!/usr/bin/env python3
"""CoWaveOverlap R0: deterministic read-only overlap, resource and impact checks.

No scheduler/lease acquisition, no trading, no provider sessions, no runtime
mutations, no CoEx or receiver certification. Pure candidate evaluation.
"""
import argparse
import copy
import json
from pathlib import Path

SCHEMA="CoCivium.CoWaveOverlap.R0.v0.1"
KINDS={"READ","RESEARCH","CHALLENGE","SIMULATE","SOURCE_WRITE","EXTERNAL_EFFECT","FINANCIAL_EFFECT"}
NON_EFFECT={"READ","RESEARCH","CHALLENGE","SIMULATE"}
STATES={"PROPOSED","RUNNING_OBSERVED","COMPLETED_OBSERVED","HELD"}
RELATIONS={"DEPENDS_ON","PRODUCES","CONSUMES","MAY_AFFECT","CAUSALLY_VERIFIED","BLOCKED_BY"}
BANNED_TARGETS={"TRADE","SWAP","VALUE_TRANSFER","SPEND","ACCOUNT_CHANGE","DEVICE_MUTATION","PUBLIC_RELEASE"}
def txt(x):
    return isinstance(x,str) and bool(x.strip())
def evaluate(d):
    out={"schema":SCHEMA,"status":"HOLD","reason":"INVALID_INPUT","parallel_candidates":[],"serialized_conflict_pairs":[],"dependency_barriers":[],"impact_candidates":[],"effects_performed":0,"leases_acquired":0,"receiver_ack":"UNPROVEN","coex":"NOT_CERTIFIED"}
    if not isinstance(d,dict) or d.get("schema")!=SCHEMA:
        return out
    waves=d.get("waves")
    if not isinstance(waves,list) or not 1<=len(waves)<=24:
        out["reason"]="INVALID_WAVE_BOUND"
        return out
    ids=set()
    for w in waves:
        if not isinstance(w,dict) or any(not txt(w.get(k)) for k in ("wave_id","work_id","source_revision","collision_domain","receiver","authority","kind","state","failure_domain")):
            out["reason"]="MISSING_REQUIRED_WAVE_FIELD";return out
        if w["wave_id"] in ids:
            out["reason"]="DUPLICATE_WAVE_ID";return out
        ids.add(w["wave_id"])
        if w["kind"] not in KINDS or w["state"] not in STATES:
            out["reason"]="INVALID_WAVE_CLASS";return out
        if w.get("confidentiality")!="PUBLIC":
            out["reason"]="HOLD_PRIVACY";return out
        if w["kind"] in {"EXTERNAL_EFFECT","FINANCIAL_EFFECT"} or w.get("effect_target") in BANNED_TARGETS:
            out["reason"]="HOLD_EFFECT_GATE";return out
        if w["kind"]=="SOURCE_WRITE" and w["authority"]!="DRAFT_ONLY":
            out["reason"]="HOLD_WRITE_AUTHORITY";return out
        if w["kind"] in NON_EFFECT and w["authority"] not in ("READ_ONLY","DRAFT_ONLY"):
            out["reason"]="HOLD_UNKNOWN_AUTHORITY";return out
        if not isinstance(w.get("reads"),list) or not isinstance(w.get("writes"),list) or not all(txt(x) for x in w["reads"]+w["writes"]):
            out["reason"]="INVALID_ACCESS_SET";return out
        if w["kind"] in NON_EFFECT and w["writes"]:
            out["reason"]="READ_ONLY_WAVE_REQUESTED_WRITE";return out
        if w["kind"]=="SOURCE_WRITE" and not w["writes"]:
            out["reason"]="WRITE_WAVE_WITHOUT_TARGET";return out
        if not isinstance(w.get("budget"),int) or isinstance(w["budget"],bool) or not 1<=w["budget"]<=8:
            out["reason"]="INVALID_WORK_BUDGET";return out
    edges=d.get("edges",[])
    if not isinstance(edges,list) or len(edges)>64:
        out["reason"]="INVALID_EDGE_BOUND";return out
    for e in edges:
        if not isinstance(e,dict) or e.get("kind") not in RELATIONS or not txt(e.get("source")) or not txt(e.get("target")):
            out["reason"]="INVALID_EDGE";return out
        if e["kind"] in ("DEPENDS_ON","BLOCKED_BY") and (e["source"] not in ids or e["target"] not in ids):
            out["reason"]="UNRESOLVED_DEPENDENCY_REF";return out
        if e["kind"]=="CAUSALLY_VERIFIED" and not txt(e.get("causal_proof_ref")):
            out["reason"]="UNPROVEN_CAUSAL_EDGE";return out
    total=sum(w["budget"] for w in waves)
    if total>64:
        out["reason"]="RESOURCE_BUDGET_EXCEEDED";return out
    live=[w for w in waves if w["state"]=="RUNNING_OBSERVED"]
    conflict=set()
    pairs=[]
    for i,a in enumerate(live):
        for b in live[i+1:]:
            ab_write=set(a["writes"]) & (set(b["reads"])|set(b["writes"]))
            ba_write=set(b["writes"]) & (set(a["reads"])|set(a["writes"]))
            shared_write=bool(ab_write or ba_write)
            shared_domain=(a["collision_domain"]==b["collision_domain"] and (a["writes"] or b["writes"]))
            if shared_write or shared_domain:
                pairs.append(sorted([a["wave_id"],b["wave_id"]]))
                conflict.update((a["wave_id"],b["wave_id"]))
    out["serialized_conflict_pairs"]=sorted(pairs)
    out["parallel_candidates"]=sorted(w["wave_id"] for w in live if w["wave_id"] not in conflict and w["kind"] in NON_EFFECT)
    out["dependency_barriers"]=sorted([{"wave_id":e["source"],"waits_for":e["target"]} for e in edges if e["kind"] in ("DEPENDS_ON","BLOCKED_BY")],key=lambda x:(x["wave_id"],x["waits_for"]))
    out["impact_candidates"]=sorted([{"from":e["source"],"to":e["target"],"kind":e["kind"],"evidence":"NOT_VERIFIED_CAUSALITY" if e["kind"]!="CAUSALLY_VERIFIED" else "SCOPED_PROOF_REF_PRESENT"} for e in edges if e["kind"] in ("MAY_AFFECT","CAUSALLY_VERIFIED")],key=lambda x:(x["from"],x["to"]))
    out["status"]="REVIEW_ONLY"
    out["reason"]="CONFLICTS_HELD" if pairs else "NO_CONFLICT_DETECTED_IN_DECLARED_SCOPE"
    return out

def selftest():
    def wave(i,kind="READ",reads=None,writes=None,domain=None,state="RUNNING_OBSERVED",auth=None):
        return {"wave_id":i,"work_id":"work:"+i,"source_revision":"fixture:sha","collision_domain":domain or ("dom:"+i),"receiver":"fixture:reader","authority":auth or ("DRAFT_ONLY" if kind=="SOURCE_WRITE" else "READ_ONLY"),"kind":kind,"state":state,"failure_domain":"fixture:host","confidentiality":"PUBLIC","reads":reads or [],"writes":writes or [],"budget":1}
    def doc(*waves,edges=None):
        return {"schema":SCHEMA,"waves":list(waves),"edges":edges or []}
    a=wave("a",reads=["asset:x"])
    b=wave("b",reads=["asset:x"])
    w=wave("w",kind="SOURCE_WRITE",reads=["asset:x"],writes=["asset:x"],domain="asset:x")
    w2=wave("w2",kind="SOURCE_WRITE",writes=["asset:x"],domain="asset:x")
    tests=[
     ("parallel-readers",doc(a,b),"REVIEW_ONLY","NO_CONFLICT_DETECTED_IN_DECLARED_SCOPE"),
     ("writer-reader",doc(a,w),"REVIEW_ONLY","CONFLICTS_HELD"),
     ("writer-writer",doc(w,w2),"REVIEW_ONLY","CONFLICTS_HELD"),
     ("independent-read-write",doc(b,wave("z",kind="SOURCE_WRITE",writes=["other"],domain="other")),"REVIEW_ONLY","NO_CONFLICT_DETECTED_IN_DECLARED_SCOPE"),
     ("duplicate-identity",doc(a,a),"HOLD","DUPLICATE_WAVE_ID"),
     ("private",doc({**a,"confidentiality":"PRIVATE"}),"HOLD","HOLD_PRIVACY"),
     ("financial",doc(wave("trade",kind="FINANCIAL_EFFECT")),"HOLD","HOLD_EFFECT_GATE"),
     ("trade-label",doc({**a,"effect_target":"TRADE"}),"HOLD","HOLD_EFFECT_GATE"),
     ("unsanctioned-write",doc({**w,"authority":"READ_ONLY"}),"HOLD","HOLD_WRITE_AUTHORITY"),
     ("read-write",doc({**a,"writes":["asset:x"]}),"HOLD","READ_ONLY_WAVE_REQUESTED_WRITE"),
     ("write-no-target",doc(wave("new",kind="SOURCE_WRITE")),"HOLD","WRITE_WAVE_WITHOUT_TARGET"),
     ("unbounded",doc({**a,"budget":100}),"HOLD","INVALID_WORK_BUDGET"),
     ("bad-edge",doc(a,edges=[{"source":"a","target":"missing","kind":"DEPENDS_ON"}]),"HOLD","UNRESOLVED_DEPENDENCY_REF"),
     ("causal-fraud",doc(a,edges=[{"source":"a","target":"b","kind":"CAUSALLY_VERIFIED"}]),"HOLD","UNPROVEN_CAUSAL_EDGE"),
     ("unknown-impact",doc(a,edges=[{"source":"a","target":"b","kind":"MAY_AFFECT"}]),"REVIEW_ONLY","NO_CONFLICT_DETECTED_IN_DECLARED_SCOPE"),
     ("real-dependency",doc(a,b,edges=[{"source":"a","target":"b","kind":"DEPENDS_ON"}]),"REVIEW_ONLY","NO_CONFLICT_DETECTED_IN_DECLARED_SCOPE"),
     ("two-conflict-domains",doc(w,wave("z",kind="SOURCE_WRITE",writes=["other"],domain="asset:x")),"REVIEW_ONLY","CONFLICTS_HELD"),
     ("source-class",doc({**a,"kind":"UNKNOWN"}),"HOLD","INVALID_WAVE_CLASS"),
     ("missing-receiver",doc({**a,"receiver":""}),"HOLD","MISSING_REQUIRED_WAVE_FIELD"),
     ("no-waves",doc(),"HOLD","INVALID_WAVE_BOUND"),
    ]
    for name,item,expect,reason in tests:
        before=copy.deepcopy(item)
        out=evaluate(item)
        assert out["status"]==expect and out["reason"]==reason,(name,out)
        assert item==before and out["effects_performed"]==out["leases_acquired"]==0
        assert out["receiver_ack"]=="UNPROVEN" and out["coex"]=="NOT_CERTIFIED"
    out=evaluate(doc(a,b));assert out["parallel_candidates"]==["a","b"]
    out=evaluate(doc(w,w2));assert out["serialized_conflict_pairs"]==[["w","w2"]]
    out=evaluate(doc(a,edges=[{"source":"a","target":"b","kind":"MAY_AFFECT"}]));assert out["impact_candidates"][0]["evidence"]=="NOT_VERIFIED_CAUSALITY"
    print(json.dumps({"schema":SCHEMA,"cases":len(tests)+3,"passed":len(tests)+3,"scope":"SYNTHETIC_ONLY","effects":0,"real_worker_leases":"UNPROVEN","receiver_ack":"UNPROVEN"},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--input")
    a=p.parse_args()
    if a.selftest:selftest()
    elif a.input: print(json.dumps(evaluate(json.loads(Path(a.input).read_text(encoding="utf-8"))),sort_keys=True,indent=2))
    else:p.error("use --selftest or --input")
