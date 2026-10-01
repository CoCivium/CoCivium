#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/cocivia/coall_distributed_lease_contention_r0.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))

    active={}
    replay={}
    for c in d["exclusive_cases"]:
        key=c["resource"]
        req=c["request"]
        if req in replay:
            got="REPLAY_PRIOR_LEASE"
        elif key in active:
            got="CONTENDED_NO_SECOND_LEASE"
        else:
            active[key]=req
            replay[req]=c.get("fence")
            got="LEASE_GRANTED"
        if got!=c["expected"]:
            raise SystemExit(f"FAIL: {c['id']} got={got} expected={c['expected']}")

    used=0
    cap=d["shareable"]["grant_capacity"]
    for r in d["shareable"]["reservations"]:
        if used+r["amount"]<=cap:
            used+=r["amount"]
            got="LEASE_GRANTED"
        else:
            got="DENY_CAPACITY_EXCEEDED"
        if got!=r["expected"]:
            raise SystemExit(f"FAIL: {r['id']} got={got} expected={r['expected']}")
    if used>cap:
        raise SystemExit("FAIL: active reservations exceeded grant capacity")

    for f in d["fencing"]:
        got="ACCEPT_CURRENT_FENCE" if f["presented"]==f["current"] else "REJECT_STALE_FENCE"
        if got!=f["expected"]:
            raise SystemExit(f"FAIL: {f['id']} got={got} expected={f['expected']}")

    p=d["partition_case"]
    got="HOLD_NO_DUAL_AUTHORITY" if (not p["shared_authority_reachable"] and not p["scheduler_a_self_elects"] and not p["scheduler_b_self_elects"]) else "FAIL_DUAL_AUTHORITY_RISK"
    if got!=p["expected"]:
        raise SystemExit(f"FAIL: {p['id']} got={got} expected={p['expected']}")

    print("PASS: distributed lease contention and fencing policy fixture")

if __name__=="__main__":
    main()
