#!/usr/bin/env python3
import json
from pathlib import Path

FIXTURE=Path("fixtures/substrate/co_substrate_migration_r0.json")

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def main():
    if not FIXTURE.exists():
        fail("fixture missing")
    data=json.loads(FIXTURE.read_text(encoding="utf-8"))
    cases=data.get("cases",[])
    if len(cases)!=5:
        fail("expected exactly five migration cases")

    ids={c.get("id") for c in cases}
    expected_ids={
        "portable_semantic_object",
        "substrate_constrained_object",
        "intentionally_substrate_bound_object",
        "lossy_migration",
        "failed_reconstruction_invariant",
    }
    if ids!=expected_ids:
        fail("case identity mismatch")

    results={}
    for c in cases:
        cls=c["portability_class"]
        src=c["source"]
        dst=c["destination"]
        exp=c["expected"]["accepted"]

        if not src.get("provenance"):
            fail(f"{c['id']}: provenance required")
        if "authority_state" not in src:
            fail(f"{c['id']}: authority state required")

        if cls=="SUBSTRATE_BOUND":
            accepted=False
        elif cls=="SUBSTRATE_CONSTRAINED":
            req=set(src.get("substrate_requirements",[]))
            caps=set(dst.get("capabilities",[]))
            accepted=req.issubset(caps)
        elif cls=="PORTABLE":
            accepted=True
            observed=dst.get("observed_invariants")
            if observed is not None:
                required=set(src.get("invariants",[]))
                accepted=required.issubset(set(observed))
            if any("required" in x.lower() for x in dst.get("declared_loss",[])):
                accepted=False
        else:
            fail(f"{c['id']}: unsupported portability class {cls}")

        if accepted != exp:
            fail(f"{c['id']}: acceptance mismatch got={accepted} expected={exp}")
        results[c["id"]]=accepted

    if results["intentionally_substrate_bound_object"] is not False:
        fail("substrate-bound object escaped")
    if results["failed_reconstruction_invariant"] is not False:
        fail("failed reconstruction was accepted")
    if results["lossy_migration"] is not True:
        fail("declared non-invariant loss should remain acceptable")

    print("PASS: CoSubstrate migration R0 fixture validated (5 cases)")

if __name__=="__main__":
    main()
