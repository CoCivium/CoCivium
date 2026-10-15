#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cosneak_pass_without_pickup_audit_r0i.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["sample_size"] != len(d["objects"]):
        raise SystemExit("FAIL:sample size")
    pp=sum(1 for x in d["objects"] if x["pickup_state"].startswith("PICKUP_PROVEN"))
    un=sum(1 for x in d["objects"] if "PICKUP_UNPROVEN" in x["pickup_state"])
    if pp!=d["totals"]["pickup_proven"] or un!=d["totals"]["pass_with_pickup_unproven"]:
        raise SystemExit("FAIL:totals")
    for x in d["objects"]:
        if not x["producer_pass"]:
            raise SystemExit("FAIL:not PASS sample:"+x["id"])
        if x["pickup_state"].startswith("PICKUP_PROVEN") and not x["exact_readproof_bound"]:
            raise SystemExit("FAIL:pickup without readproof:"+x["id"])
        if x["semantic_acceptance_proven"] or x["integration_proven"]:
            raise SystemExit("FAIL:acceptance/integration overclaim:"+x["id"])
    if d["sampled_scope_closed"] is not True or d["global_census_complete"] is not False:
        raise SystemExit("FAIL:scope")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: CoSneak PASS-without-pickup bounded audit R0I")
if __name__=="__main__": main()
