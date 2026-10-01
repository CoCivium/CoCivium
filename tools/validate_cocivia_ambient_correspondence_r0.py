#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/cocivia/co_cocivia_ambient_correspondence_r0.json")

def route(c):
    rel=c["relationship"]
    write=bool(c["surface_write_authority"])
    explicit=bool(c["explicit_invocation"])
    if rel in {"MUTED","REVOKED"}:
        return "BLOCK"
    if not write:
        if rel in {"DIRECTLY_INVITED","OPTED_IN_TO_CONTEXTUAL_REPLY","ACTIVE_THREAD_PARTICIPANT"}:
            return "DRAFT_ONLY"
        return "OBSERVE_ONLY"
    if explicit and rel in {"OPTED_IN_TO_CONTEXTUAL_REPLY","DIRECTLY_INVITED","ACTIVE_THREAD_PARTICIPANT"}:
        return "RESPOND_IF_EXPLICITLY_INVOKED"
    if rel=="OPTED_IN_TO_CONTEXTUAL_REPLY":
        return "RESPOND_IF_RELATIONALLY_OPTED_IN"
    return "OBSERVE_ONLY"

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    cases=d.get("cases",[])
    if len(cases)!=6:
        raise SystemExit("FAIL: expected six cases")
    for c in cases:
        got=route(c)
        if got!=c["expected"]:
            raise SystemExit(f"FAIL: {c['id']} got={got} expected={c['expected']}")
    rails=set(d.get("rails",[]))
    required={
      "TRIGGER_WORD_NE_INVITATION",
      "MENTION_NE_CONSENT",
      "REFERRAL_NE_THIRD_PARTY_CONSENT",
      "READABLE_NE_WRITABLE",
      "DRAFT_NE_SENT",
      "AUTOMATION_NE_CONSENT"
    }
    if not required.issubset(rails):
        raise SystemExit("FAIL: required rails missing")
    print("PASS: CoCivia ambient correspondence policy fixture (6 cases)")

if __name__=="__main__":
    main()
