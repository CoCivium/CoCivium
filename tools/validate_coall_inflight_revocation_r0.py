#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/cocivia/coall_inflight_revocation_r0.json")

def decide(c):
    if not c["revoked"]:
        return "NO_REVOCATION"
    if not c["started"]:
        return "BLOCK_START"
    cls=c["interrupt_class"]
    if cls=="CHECKPOINTABLE":
        return "STOP_AT_NEXT_SAFE_CHECKPOINT_PRESERVE_PRIOR_RECEIPT" if c.get("prior_receipt") else "STOP_AT_NEXT_SAFE_CHECKPOINT"
    if cls=="ATOMIC_SAFE_COMPLETE":
        return "COMPLETE_CURRENT_ATOMIC_UNIT_THEN_STOP"
    if cls=="EXTERNAL_HIGH_EFFECT":
        return "EXECUTE_PROVEN_ABORT_THEN_STOP" if c.get("abort_contract") else "HOLD_FAIL_CLOSED"
    raise SystemExit("FAIL: unknown interruption class")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    cases=d.get("cases",[])
    if len(cases)!=6:
        raise SystemExit("FAIL: expected six cases")
    for c in cases:
        got=decide(c)
        if got!=c["expected"]:
            raise SystemExit(f"FAIL: {c['id']} got={got} expected={c['expected']}")
        if c.get("partial") and c.get("publication_authority") is not False:
            raise SystemExit(f"FAIL: {c['id']} partial output publication authority drift")
    required={
        "REVOCATION_RECEIVED_NE_INSTANT_PHYSICAL_STOP",
        "IN_FLIGHT_NE_PERMISSION_TO_EXPAND_SCOPE",
        "SAFE_COMPLETION_NE_NEW_WORK",
        "HIGH_EFFECT_REVOCATION_REQUIRES_PROVEN_ABORT_OR_ROLLBACK",
        "PARTIAL_OUTPUT_NE_PUBLICATION_AUTHORITY",
        "REVOCATION_NE_HISTORY_ERASURE"
    }
    if not required.issubset(set(d.get("rails",[]))):
        raise SystemExit("FAIL: required rails missing")
    print("PASS: in-flight revocation interruption policy fixture (6 cases)")

if __name__=="__main__":
    main()
