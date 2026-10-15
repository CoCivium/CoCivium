#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/authority/coboss_authority_relations_r0.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    r=d["rules"]
    if r["worldly_unbounded_authority_allowed"] is not False:
        raise SystemExit("FAIL:worldly sovereignty")
    if r["ultimate_referent_is_executable_principal"] is not False:
        raise SystemExit("FAIL:referent became principal")
    if r["metaphysical_claim_grants_permission"] is not False:
        raise SystemExit("FAIL:metaphysical escalation")
    if r["claim_to_represent_ultimate_referent_grants_permission"] is not False:
        raise SystemExit("FAIL:representative escalation")
    if r["authority_is_scoped"] is not True:
        raise SystemExit("FAIL:scope")
    bad=[x for x in d["examples"] if "root authority" in x["claim"] and x["allowed"]]
    if bad:
        raise SystemExit("FAIL:root authority")
    print("PASS: CoBoss anti-sovereign authority relations R0")

if __name__=="__main__":
    main()
