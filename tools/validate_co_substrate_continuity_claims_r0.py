#!/usr/bin/env python3
import json
from pathlib import Path

CLAIMS=Path("fixtures/substrate/co_substrate_continuity_claims_r0.json")
MIGRATION=Path("fixtures/substrate/co_substrate_migration_r0.json")

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def decide(case, allowed, forbidden):
    requested=set(case.get("requested_claims",[]))
    if requested & forbidden:
        return "REJECT"
    if "FUNCTIONAL_CONTINUITY_IF_VALIDATED" in requested and not case.get("functional_validation_present",False):
        return "HOLD"
    if "AUTHORITY_CONTINUITY_IF_AUTHORITY_UNCHANGED" in requested and not case.get("authority_unchanged",False):
        return "HOLD"
    if not requested.issubset(allowed):
        return "REJECT"
    return "ALLOW"

def main():
    if not CLAIMS.exists() or not MIGRATION.exists():
        fail("required fixture missing")
    cdata=json.loads(CLAIMS.read_text(encoding="utf-8"))
    mdata=json.loads(MIGRATION.read_text(encoding="utf-8"))
    mids={c["id"] for c in mdata.get("cases",[])}
    allowed=set(cdata.get("allowed_claims_after_accepted_migration",[]))
    forbidden=set(cdata.get("forbidden_automatic_claims",[]))
    if not allowed or not forbidden or allowed & forbidden:
        fail("claim sets invalid")
    cases=cdata.get("cases",[])
    if len(cases)!=5:
        fail("expected five continuity claim cases")
    for c in cases:
        if c.get("migration_case") not in mids:
            fail(f"{c['id']}: missing migration binding")
        got=decide(c,allowed,forbidden)
        if got!=c.get("expected_decision"):
            fail(f"{c['id']}: decision mismatch got={got}")
    print("PASS: CoSubstrate continuity claim guard validated (5 cases)")

if __name__=="__main__":
    main()
