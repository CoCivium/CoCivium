#!/usr/bin/env python3
import json, hashlib
from pathlib import Path

P=Path("fixtures/relations/coq40_trigger_neutral_replay_r0x.json")

def decide(c):
    if not c["task_hash_matches"]:
        return "FAIL_CLOSED_IDENTITY_COLLISION", 0
    if c["receipt_exists"]:
        return "ALREADY_RECEIPTED_NO_EXECUTION", 0
    if c["active_lease"] and not c["lease_expired"]:
        return "HOLD_ACTIVE_LEASE", 0
    if c["active_lease"] and c["lease_expired"]:
        if not c["revalidation"]:
            return "HOLD_REVALIDATION_FAILED", 0
        return "LEASE_TAKEOVER_ELECTED", 1
    return "LEASE_CLAIMED", 1

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    seen=[]
    total_exec=0
    for c in d["cases"]:
        state, n=decide(c)
        if state != c["expected"] or n != c["executions"]:
            raise SystemExit("FAIL:"+c["id"]+":"+state)
        seen.append({"id":c["id"],"state":state,"executions":n})
        total_exec += n
    if len(seen) != 5:
        raise SystemExit("FAIL:case_count")
    if total_exec != 2:
        raise SystemExit("FAIL:execution_count")
    if d["persistent_trigger_installed"] or d["live_trigger_proven"]:
        raise SystemExit("FAIL:trigger_overclaim")
    if d["task_signature_proven"] or d["receiver_semantic_acceptance_proven"]:
        raise SystemExit("FAIL:acceptance_or_signature_overclaim")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    digest=hashlib.sha256(json.dumps(seen,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
    print(json.dumps({
      "STATE":"PASS_Q40_TRIGGER_NEUTRAL_REPLAY_R0X",
      "cases":len(seen),
      "synthetic_executions":total_exec,
      "duplicate_effects":0,
      "replay_sha256":digest
    },separators=(",",":")))

if __name__=="__main__":
    main()
