#!/usr/bin/env python3
"""CoStatusOffload R0: pure public-safe, hash-linked portable WorkID state.

No network, writes, remote storage, sessions, model invocation or lease acquisition.
Staging and merging are *candidate computations*, not authoritative head changes.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path

SCHEMA = "CoCivium.CoStatusOffload.R0.v0.1"
ALLOWED_SCOPES = ("task", "evidence", "recovery", "next", "meaning", "relations")
FIELDS = ("schema", "work_id", "sequence", "source_ref", "source_revision",
          "parent_sha256", "authority", "confidentiality", "owner",
          "next_wake", "stop_condition", "status", "sections")
CANDIDATE_FIELDS = ("schema", "candidate_id", "worker_id", "work_id",
                    "base_sha256", "source_revision", "authority", "confidentiality",
                    "changes", "evidence_refs")
MAX_SECTIONS = 6
MAX_CHANGE_FIELDS = 6


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def filled(x):
    return isinstance(x, str) and bool(x.strip()) and len(x) <= 256


def result(state, reason, **extra):
    return {"schema": SCHEMA, "state": state, "reason": reason,
            "effects_performed": 0, "receiver_ack": "UNPROVEN",
            "shared_head_committed": False, **extra}


def make_initial(work_id, source_ref, source_revision):
    """Fixture-friendly pure constructor; never asserts observed source currentness."""
    if not all(filled(v) for v in (work_id, source_ref, source_revision)):
        raise ValueError("invalid identity")
    core = {
        "schema": SCHEMA, "work_id": work_id, "sequence": 1,
        "source_ref": source_ref, "source_revision": source_revision,
        "parent_sha256": None, "authority": "READ_ONLY",
        "confidentiality": "PUBLIC", "owner": "UNASSIGNED",
        "next_wake": "verified material change", "stop_condition": "no qualified delta",
        "status": "CANDIDATE_ONLY", "sections": {},
    }
    return {**core, "checkpoint_sha256": sha256(core)}


def check_checkpoint(cp):
    if not isinstance(cp, dict) or set(cp) != set(FIELDS) | {"checkpoint_sha256"}:
        return "HOLD_SCHEMA_LOSS"
    if cp.get("schema") != SCHEMA or cp.get("authority") != "READ_ONLY" or cp.get("confidentiality") != "PUBLIC":
        return "HOLD_AUTHORITY_OR_PRIVACY"
    if cp.get("status") != "CANDIDATE_ONLY" or not all(filled(cp.get(k)) for k in
        ("work_id", "source_ref", "source_revision", "owner", "next_wake", "stop_condition")):
        return "HOLD_INVALID_STATE"
    if not isinstance(cp.get("sequence"), int) or isinstance(cp["sequence"], bool) or cp["sequence"] < 1:
        return "HOLD_INVALID_SEQUENCE"
    if cp["sequence"] > 1 and not filled(cp.get("parent_sha256")):
        return "HOLD_LOST_PARENT"
    if cp["sequence"] == 1 and cp.get("parent_sha256") is not None:
        return "HOLD_BAD_INITIAL_PARENT"
    sections=cp.get("sections")
    if not isinstance(sections, dict) or len(sections)>MAX_SECTIONS or any(
        k not in ALLOWED_SCOPES or not isinstance(v, dict) or len(v)>MAX_CHANGE_FIELDS
        or any(not filled(kk) or not isinstance(vv, str) or len(vv)>2048 for kk,vv in v.items())
        for k,v in sections.items()):
        return "HOLD_BAD_SECTIONS"
    if sha256({k:cp[k] for k in FIELDS}) != cp.get("checkpoint_sha256"):
        return "HOLD_DIGEST_MISMATCH"
    return "EXACT_STRUCTURAL_READBACK_ONLY"


def stage(cp, proposal):
    v=check_checkpoint(cp)
    if v!="EXACT_STRUCTURAL_READBACK_ONLY":
        return result("HOLD",v)
    if not isinstance(proposal, dict) or set(proposal) != set(CANDIDATE_FIELDS):
        return result("HOLD","INVALID_PROPOSAL_SCHEMA")
    if proposal["schema"] != SCHEMA:
        return result("HOLD","PROPOSAL_SCHEMA_DRIFT")
    if not all(filled(proposal.get(k)) for k in
        ("candidate_id","worker_id","work_id","base_sha256","source_revision")):
        return result("HOLD","INVALID_PROPOSAL_IDENTITY")
    if proposal["work_id"] != cp["work_id"] or proposal["source_revision"] != cp["source_revision"]:
        return result("HOLD","WRONG_WORK_OR_SOURCE")
    if proposal["base_sha256"] != cp["checkpoint_sha256"]:
        return result("HOLD","STALE_OR_WRONG_BASE")
    if proposal["authority"] != "READ_ONLY" or proposal["confidentiality"] != "PUBLIC":
        return result("HOLD","PROPOSAL_AUTHORITY_OR_PRIVACY")
    change=proposal["changes"]
    if not isinstance(change,dict) or not 1<=len(change)<=MAX_SECTIONS:
        return result("HOLD","INVALID_CHANGE_BOUND")
    for section,fields in change.items():
        if section not in ALLOWED_SCOPES or not isinstance(fields,dict) or not 1<=len(fields)<=MAX_CHANGE_FIELDS:
            return result("HOLD","INVALID_CHANGE_SCOPE")
        if any(not filled(k) or not isinstance(v,str) or len(v)>2048 for k,v in fields.items()):
            return result("HOLD","INVALID_CHANGE_VALUE")
    ev=proposal["evidence_refs"]
    if not isinstance(ev,list) or not ev or len(ev)>16 or not all(filled(e) for e in ev):
        return result("HOLD","NO_QUALIFIED_EVIDENCE_POINTER")
    return result("STAGED_CANDIDATE_ONLY","NO_SHARED_HEAD_MUTATED",
                  candidate_sha256=sha256(proposal),candidate_id=proposal["candidate_id"])


def merge_candidates(cp, proposals):
    """Pure merge proposal, returns draft candidate checkpoint, never writes head."""
    if check_checkpoint(cp)!="EXACT_STRUCTURAL_READBACK_ONLY":
        return result("HOLD","INVALID_BASE_CHECKPOINT")
    if not isinstance(proposals,list) or not 1<=len(proposals)<=8:
        return result("HOLD","INVALID_CANDIDATE_COUNT")
    ids=set()
    touched={}
    for p in proposals:
        s=stage(cp,p)
        if s["state"]!="STAGED_CANDIDATE_ONLY":
            return result("HOLD","UNQUALIFIED_STAGE",stage_reason=s["reason"])
        if p["candidate_id"] in ids:
            return result("HOLD","DUPLICATE_CANDIDATE_ID")
        ids.add(p["candidate_id"])
        for section,fields in p["changes"].items():
            for key in fields:
                path=(section,key)
                if path in touched:
                    return result("HOLD","OVERLAPPING_FIELD_WRITES",
                                  conflict_scope=section+"."+key)
                touched[path]=fields[key]
    successor=copy.deepcopy({k:cp[k] for k in FIELDS})
    successor["sequence"]=cp["sequence"]+1
    successor["parent_sha256"]=cp["checkpoint_sha256"]
    for (section,key),value in sorted(touched.items()):
        successor["sections"].setdefault(section,{})[key]=value
    successor["checkpoint_sha256"]=sha256(successor)
    if check_checkpoint(successor)!="EXACT_STRUCTURAL_READBACK_ONLY":
        return result("HOLD","SUCCESSOR_INVALID_OR_OVER_CAPACITY")
    return result("MERGE_CANDIDATE_ONLY","INDEPENDENT_REVIEW_AND_AUTHORIZED_CAS_REQUIRED",
                  candidate_checkpoint=successor,staged_candidates=len(proposals),
                  touched_field_count=len(touched),
                  parent_verified=cp["checkpoint_sha256"])


def cold_restore(expected_sha, raw_json):
    try:
        cp=json.loads(raw_json)
    except (ValueError,TypeError):
        return result("HOLD","UNREADABLE_CHECKPOINT")
    v=check_checkpoint(cp)
    if v!="EXACT_STRUCTURAL_READBACK_ONLY":
        return result("HOLD",v)
    if cp["checkpoint_sha256"] != expected_sha:
        return result("HOLD","WRONG_REQUESTED_CHECKPOINT")
    return result("RESTORE_CANDIDATE_ONLY","EXACT_BYTES_RECONSTRUCTED_NOT_RECEIVER_ACK",
                  work_id=cp["work_id"],checkpoint_sha256=expected_sha,
                  next_wake=cp["next_wake"],stop_condition=cp["stop_condition"])


def selftest():
    import subprocess
    import sys
    cp=make_initial("fixtureWork","fixture:source","sha:one")
    def prop(i,changes):
        return {"schema":SCHEMA,"candidate_id":i,"worker_id":"fixture:"+i,
          "work_id":cp["work_id"],"base_sha256":cp["checkpoint_sha256"],
          "source_revision":cp["source_revision"],"authority":"READ_ONLY",
          "confidentiality":"PUBLIC","changes":changes,"evidence_refs":["fixture:evidence:"+i]}
    a=prop("a",{"task":{"status":"pending"}})
    b=prop("b",{"evidence":{"source":"sha:proof"}})
    cases=0
    def assert_case(actual,state,reason=None):
        nonlocal cases
        assert actual["state"]==state,(actual,state)
        if reason: assert actual["reason"]==reason,(actual,reason)
        assert actual["effects_performed"]==0 and not actual["shared_head_committed"]
        assert actual["receiver_ack"]=="UNPROVEN"
        cases+=1
        return actual
    assert check_checkpoint(cp)=="EXACT_STRUCTURAL_READBACK_ONLY";cases+=1
    assert_case(stage(cp,a),"STAGED_CANDIDATE_ONLY")
    assert_case(stage(cp,{**a,"base_sha256":"wrong"}),"HOLD","STALE_OR_WRONG_BASE")
    assert_case(stage(cp,{**a,"work_id":"other"}),"HOLD","WRONG_WORK_OR_SOURCE")
    assert_case(stage(cp,{**a,"confidentiality":"PRIVATE"}),"HOLD","PROPOSAL_AUTHORITY_OR_PRIVACY")
    assert_case(stage(cp,{**a,"authority":"WRITE"}),"HOLD","PROPOSAL_AUTHORITY_OR_PRIVACY")
    assert_case(stage(cp,{**a,"evidence_refs":[]}),"HOLD","NO_QUALIFIED_EVIDENCE_POINTER")
    assert_case(stage(cp,{**a,"changes":{"bad":{"x":"y"}}}),"HOLD","INVALID_CHANGE_SCOPE")
    assert_case(merge_candidates(cp,[a,a]),"HOLD","DUPLICATE_CANDIDATE_ID")
    overlap=prop("c",{"task":{"status":"different"}})
    assert_case(merge_candidates(cp,[a,overlap]),"HOLD","OVERLAPPING_FIELD_WRITES")
    merged=assert_case(merge_candidates(cp,[a,b]),"MERGE_CANDIDATE_ONLY")
    nxt=merged["candidate_checkpoint"]
    assert nxt["parent_sha256"]==cp["checkpoint_sha256"] and nxt["sequence"]==2;cases+=1
    assert_case(merge_candidates(cp,[b,a]),"MERGE_CANDIDATE_ONLY")
    assert merge_candidates(cp,[a,b])["candidate_checkpoint"]["checkpoint_sha256"]==merge_candidates(cp,[b,a])["candidate_checkpoint"]["checkpoint_sha256"];cases+=1
    assert_case(cold_restore(cp["checkpoint_sha256"],canonical(cp)),"RESTORE_CANDIDATE_ONLY")
    assert_case(cold_restore("wrong",canonical(cp)),"HOLD","WRONG_REQUESTED_CHECKPOINT")
    corrupted=copy.deepcopy(cp);corrupted["sections"]={"task":{"evil":"surprise"}}
    assert_case(cold_restore(cp["checkpoint_sha256"],canonical(corrupted)),"HOLD","HOLD_DIGEST_MISMATCH")
    assert_case(cold_restore(cp["checkpoint_sha256"],"not json"),"HOLD","UNREADABLE_CHECKPOINT")
    stale=copy.deepcopy(cp);stale["source_revision"]="sha:two"
    assert_case(stage(stale,a),"HOLD","HOLD_DIGEST_MISMATCH")
    assert_case(merge_candidates(cp,[]),"HOLD","INVALID_CANDIDATE_COUNT")
    assert_case(merge_candidates(cp,[{**b,"changes":{"evidence":{"a":2}}}]),"HOLD","UNQUALIFIED_STAGE")
    assert_case(merge_candidates(cp,[{**b,"changes":{"task":{"status":"x"}}},a]),"HOLD","OVERLAPPING_FIELD_WRITES")
    # Re-run readback in a *separate Python interpreter*. No shared in-process globals.
    chk=subprocess.run([sys.executable,"-B",__file__,"--verify-selftest-checkpoint",
        cp["checkpoint_sha256"],canonical(cp)],capture_output=True,text=True,timeout=10,check=True)
    assert json.loads(chk.stdout)["state"]=="RESTORE_CANDIDATE_ONLY";cases+=1
    print(json.dumps({"schema":SCHEMA,"passed":cases,"cases":cases,
      "scope":"SYNTHETIC_PUBLIC_ONLY","effects":0,
      "remote_mirror":"NOT_TESTED","independent_receiver":"UNPROVEN",
      "shared_head_mutation":"NOT_PERFORMED"},sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--verify-selftest-checkpoint",nargs=2,metavar=("SHA","JSON"))
    p.add_argument("--inspect-json")
    a=p.parse_args()
    if a.selftest:
        selftest()
    elif a.verify_selftest_checkpoint:
        print(json.dumps(cold_restore(*a.verify_selftest_checkpoint),sort_keys=True))
    elif a.inspect_json:
        raw=Path(a.inspect_json).read_text(encoding="utf-8")
        try:obj=json.loads(raw)
        except ValueError:obj=None
        print(json.dumps({"schema":SCHEMA,"validation":check_checkpoint(obj)},sort_keys=True))
    else:
        p.error("specify --selftest or --inspect-json")
