#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/relations/coq40_trigger_neutral_inbox_lease_receipt_r0w.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    p=d["protocol"]
    if p["persistent_trigger_installed"] is not False or p["trigger_class_elected"] is not None:
        raise SystemExit("FAIL:persistence_or_trigger_election")

    by={x["id"]:x for x in d["cases"]}
    expected={
      "clean_claim":"CLAIM_ONE_LEASE",
      "concurrent_claim_collision":"HOLD_EXISTING_LEASE",
      "stale_lease_takeover":"TAKEOVER_ALLOWED_BOUNDED",
      "already_receipted_duplicate_wake":"NO_EXECUTION_ALREADY_RECEIPTED",
      "identity_collision":"FAIL_CLOSED_IDENTITY_COLLISION",
    }
    if set(by)!=set(expected):
        raise SystemExit("FAIL:case_set")
    for k,v in expected.items():
        if by[k]["expected"] != v:
            raise SystemExit("FAIL:case:"+k)

    if by["concurrent_claim_collision"]["lease_expired"] is not False:
        raise SystemExit("FAIL:current_lease_not_current")
    if by["stale_lease_takeover"].get("authority_revalidated") is not True:
        raise SystemExit("FAIL:takeover_without_revalidation")
    if by["already_receipted_duplicate_wake"]["prior_receipt"] is not True:
        raise SystemExit("FAIL:duplicate_receipt_case")
    if by["identity_collision"]["task_hash_matches"] is not False:
        raise SystemExit("FAIL:identity_collision_not_modeled")

    r=d["rules"]
    if r["many_watchers_one_elected_actuator"] is not True:
        raise SystemExit("FAIL:actuator_rule")
    for k in [
      "lease_grants_authority",
      "inbox_presence_grants_execution_permission",
      "duplicate_trigger_grants_duplicate_effect",
      "receipt_implies_semantic_acceptance",
      "hash_is_signature",
      "persistent_worker_proven",
      "independent_trigger_proven"
    ]:
        if r[k] is not False:
            raise SystemExit("FAIL:overclaim:"+k)

    if d["runtime_effect"] or d["public_effect"] or d["authority_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: Q40 trigger-neutral inbox/lease/receipt protocol R0W")

if __name__=="__main__":
    main()
