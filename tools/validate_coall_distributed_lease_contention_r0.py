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
    got="HOLD_NO_DUAL_AUTHORITY" if (
        not p["shared_authority_reachable"]
        and not p["scheduler_a_self_elects"]
        and not p["scheduler_b_self_elects"]
    ) else "FAIL_DUAL_AUTHORITY_RISK"
    if got!=p["expected"]:
        raise SystemExit(f"FAIL: {p['id']} got={got} expected={p['expected']}")

    # Expiry/takeover state machine:
    # an active lease blocks a successor before expiry; after expiry the old
    # reservation releases future capacity, a successor gets a newer fence,
    # and the stale predecessor fence is rejected.
    x=d["expiry_takeover"]
    current=None
    current_fence=x["initial_fence"]
    replay_by_request={}
    for e in x["events"]:
        op=e["op"]
        now=e["now"]

        expired_released=False
        if current is not None and now>=current["expires_at"]:
            current=None
            expired_released=True

        if op=="ACQUIRE":
            req=e["request"]
            if current is not None:
                got="CONTENDED_NO_SECOND_LEASE"
                got_fence=None
            elif req in replay_by_request and not expired_released:
                got="REPLAY_PRIOR_LEASE"
                got_fence=replay_by_request[req]
            else:
                current_fence+=1
                current={
                    "request": req,
                    "scheduler": e["scheduler"],
                    "fence": current_fence,
                    "expires_at": now+e["ttl"],
                }
                replay_by_request[req]=current_fence
                got="LEASE_GRANTED_AFTER_EXPIRY" if expired_released else "LEASE_GRANTED"
                got_fence=current_fence

            if got!=e["expected"]:
                raise SystemExit(f"FAIL: {e['id']} got={got} expected={e['expected']}")
            if got_fence!=e.get("expected_fence"):
                raise SystemExit(
                    f"FAIL: {e['id']} fence={got_fence} expected_fence={e.get('expected_fence')}"
                )

        elif op=="PRESENT_EFFECT":
            presented=e["presented_fence"]
            if (
                current is not None
                and now<current["expires_at"]
                and e["request"]==current["request"]
                and presented==current_fence
            ):
                got="ACCEPT_CURRENT_FENCE"
            else:
                got="REJECT_STALE_FENCE"
            if got!=e["expected"]:
                raise SystemExit(f"FAIL: {e['id']} got={got} expected={e['expected']}")
        else:
            raise SystemExit(f"FAIL: unknown expiry_takeover op {op!r}")

    if current_fence<=x["initial_fence"]:
        raise SystemExit("FAIL: takeover did not advance fencing epoch")

    print("PASS: distributed lease contention, expiry takeover, and fencing policy fixture")

if __name__=="__main__":
    main()
