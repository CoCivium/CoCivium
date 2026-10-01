#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/session/co_session_provider_saturation_r0.json")

def decide(signals):
    s=set(signals)
    maxlen="CONVERSATION_MAX_LENGTH_REACHED" in s
    pressure=bool(s & {
        "CONVERSATION_MAX_LENGTH_REACHED",
        "ACTIVE_TASK_LIMIT_REACHED",
        "PROVIDER_RATE_OR_QUOTA_PRESSURE",
        "REPEATED_PROVIDER_FAILURE_ALERTS"
    })
    return {
        "spawn_new_provider_task": not pressure,
        "successor_required": maxlen,
        "contract": pressure,
    }

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    cases=d.get("cases",[])
    if len(cases)!=5:
        raise SystemExit("FAIL: expected five cases")
    for c in cases:
        got=decide(c.get("signals",[]))
        if got!=c["expected"]:
            raise SystemExit(f"FAIL: {c['id']} got={got} expected={c['expected']}")
    rails=set(d.get("rails",[]))
    required={
        "SESSION_NE_WORK_IDENTITY",
        "ACTIVE_TASK_LIMIT_NE_NEED_MORE_TASKS",
        "SATURATION_NE_SPAWN_PERMISSION",
        "PROVIDER_PRESSURE_REQUIRES_CONTRACTION_BEFORE_EXPANSION",
        "SUCCESSOR_POINTER_NE_SUCCESSOR_PICKUP",
    }
    if not required.issubset(rails):
        raise SystemExit("FAIL: required rails missing")
    print("PASS: provider saturation contraction policy fixture (5 cases)")

if __name__=="__main__":
    main()
