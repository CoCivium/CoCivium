#!/usr/bin/env python3
import json
from pathlib import Path

FIXTURE=Path("fixtures/substrate/co_substrate_migration_r0.json")
ADVERSARIAL=Path("fixtures/substrate/co_substrate_migration_r0.adversarial.json")

class ContractError(ValueError):
    pass

def reject(msg):
    raise ContractError(msg)

def evaluate(c):
    cls=c["portability_class"]
    src=c["source"]
    dst=c["destination"]

    if not src.get("provenance"):
        reject(f"{c['id']}: provenance required")
    if "authority_state" not in src or "authority_state" not in dst:
        reject(f"{c['id']}: authority state required on source and destination")
    if src["authority_state"] != dst["authority_state"]:
        reject(f"{c['id']}: authority state changed during migration")

    req=set(src.get("substrate_requirements",[]))
    caps=set(dst.get("capabilities",[]))

    if cls=="UNKNOWN":
        reject(f"{c['id']}: portability class UNKNOWN requires explicit adjudication")
    if cls=="SUBSTRATE_BOUND":
        return False
    if cls in {"PORTABLE","SUBSTRATE_CONSTRAINED"} and req and not req.issubset(caps):
        reject(f"{c['id']}: substrate requirements not satisfied")
    if cls not in {"PORTABLE","SUBSTRATE_CONSTRAINED","SUBSTRATE_BOUND"}:
        reject(f"{c['id']}: unsupported portability class {cls}")

    observed=dst.get("observed_invariants")
    if observed is not None:
        required=set(src.get("invariants",[]))
        if not required.issubset(set(observed)):
            reject(f"{c['id']}: required invariants not preserved")

    if any("required" in x.lower() for x in dst.get("declared_loss",[])):
        return False
    return True

def main():
    if not FIXTURE.exists() or not ADVERSARIAL.exists():
        raise SystemExit("FAIL: required fixture missing")

    data=json.loads(FIXTURE.read_text(encoding="utf-8"))
    cases=data.get("cases",[])
    if len(cases)!=5:
        raise SystemExit("FAIL: expected exactly five migration cases")
    ids={c.get("id") for c in cases}
    expected_ids={
        "portable_semantic_object",
        "substrate_constrained_object",
        "intentionally_substrate_bound_object",
        "lossy_migration",
        "failed_reconstruction_invariant",
    }
    if ids!=expected_ids:
        raise SystemExit("FAIL: case identity mismatch")

    results={}
    for c in cases:
        try:
            accepted=evaluate(c)
        except ContractError:
            accepted=False
        if accepted != c["expected"]["accepted"]:
            raise SystemExit(f"FAIL: {c['id']}: acceptance mismatch got={accepted} expected={c['expected']['accepted']}")
        results[c["id"]]=accepted

    neg=json.loads(ADVERSARIAL.read_text(encoding="utf-8")).get("cases",[])
    if len(neg)!=5:
        raise SystemExit("FAIL: expected exactly five adversarial cases")
    for c in neg:
        expected=c.get("expected_error","")
        try:
            evaluate(c)
        except ContractError as exc:
            if expected not in str(exc):
                raise SystemExit(f"FAIL: {c['id']}: wrong rejection: {exc}")
        else:
            raise SystemExit(f"FAIL: {c['id']}: malformed migration was accepted")

    if results["intentionally_substrate_bound_object"] is not False:
        raise SystemExit("FAIL: substrate-bound object escaped")
    if results["failed_reconstruction_invariant"] is not False:
        raise SystemExit("FAIL: failed reconstruction was accepted")
    if results["lossy_migration"] is not True:
        raise SystemExit("FAIL: declared non-invariant loss should remain acceptable")

    print("PASS: CoSubstrate migration R0 positive fixtures + 5 adversarial cases validated")

if __name__=="__main__":
    main()
