#!/usr/bin/env python3
import json
from pathlib import Path

FIXTURE=Path("fixtures/relations/co_rel_kernel_field_translation_canary_r0.json")
ADJ=Path("fixtures/relations/co_rel_kernel_field_adjudication_r0.json")

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def causal_translate(status):
    if status=="causal":
        return {"field_status":"CAUSAL_CANDIDATE","upgrade_blocked":True}
    if status=="possibly_causal":
        return {"field_status":"CAUSAL_CANDIDATE","upgrade_blocked":False}
    if status=="non_causal":
        return {"field_status":"NONCAUSAL","upgrade_blocked":False}
    if status=="unknown":
        return {"field_status":"UNKNOWN_CAUSAL_STATUS","not_applicable_blocked":True}
    if status=="mixed":
        return {"field_status":None,"requires_explicit_strategy":True}
    fail(f"unknown kernel causal status {status!r}")

def absence_translate(source, destination_need):
    if not destination_need.get("absence_participant"):
        return {"create_absence_relatum":False}
    prov=source.get("provenance")
    if not isinstance(prov,list) or not prov:
        fail("absence reification requires source provenance")
    return {
        "create_absence_relatum":True,
        "relatum_kind":"ABSENCE",
        "require_exact_source_provenance":True,
        "require_scope_preservation":True,
        "required_nonclaims":["ABSENCE_NE_NONEXISTENCE","PROJECTION_RELATUM_NE_SOURCE_ENTITY"]
    }

def main():
    if not FIXTURE.exists() or not ADJ.exists():
        fail("required translation inputs missing")
    fx=json.loads(FIXTURE.read_text(encoding="utf-8"))
    adj=json.loads(ADJ.read_text(encoding="utf-8"))
    dec={d["decision_id"] for d in adj.get("decisions",[])}
    if dec != set(fx["source_adjudication"]["expected_decisions"]):
        fail("adjudication decision set drift")

    cases=fx.get("cases",[])
    if len(cases)!=5:
        fail("expected exactly five translation canary cases")

    for c in cases:
        cid=c["id"]
        if cid.startswith("T0") and "CAUSAL" in cid or cid in {"T02_UNKNOWN_STAYS_UNKNOWN","T03_MIXED_FAILS_CLOSED"}:
            pass
        if cid in {"T01_CAUSAL_DEFAULTS_TO_CANDIDATE","T02_UNKNOWN_STAYS_UNKNOWN","T03_MIXED_FAILS_CLOSED"}:
            got=causal_translate(c["source"]["causal_status"])
        elif cid in {"T04_ABSENCE_NO_REIFICATION_WHEN_NOT_NEEDED","T05_ABSENCE_REIFY_ONLY_WHEN_NEEDED"}:
            got=absence_translate(c["source"],c["destination_need"])
        else:
            fail(f"unknown case {cid}")
        if got != c["expected"]:
            fail(f"{cid}: translation mismatch got={got} expected={c['expected']}")

    print("PASS: CoRelKernel -> CoRelationField translation canary validated (5 cases)")

if __name__=="__main__":
    main()
