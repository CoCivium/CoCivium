#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/cocivia/coall_optin_resource_field_r0.json")

def eligible(c):
    if c["grant_state"]!="ACTIVE":
        return False
    if not c.get("explicit_accept",False):
        return False
    if c["resource"]=="FUNDING":
        return False
    return True

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    cases=d.get("cases",[])
    if len(cases)!=7:
        raise SystemExit("FAIL: expected seven cases")
    for c in cases:
        got=eligible(c)
        if got is not c["expected_eligible"]:
            raise SystemExit(f"FAIL: {c['id']} got={got} expected={c['expected_eligible']}")
    rails=set(d.get("rails",[]))
    required={
      "DEFAULT_VISIBLE_NE_DEFAULT_GRANTED",
      "CAPACITY_NE_PERMISSION",
      "USER_DEVICE_NE_FREE_COMPUTE",
      "RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY",
      "REFERRAL_NE_RESOURCE_GRANT",
      "MENTION_NE_RESOURCE_WAKE"
    }
    if not required.issubset(rails):
        raise SystemExit("FAIL: required resource rails missing")
    print("PASS: CoAll opt-in resource field policy fixture (7 cases)")

if __name__=="__main__":
    main()
