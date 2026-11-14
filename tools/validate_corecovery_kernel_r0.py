#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/resilience/corecovery_kernel_r0.json")
SECRET_KEYS={"password","api_key","apikey","token","bearer","private_key","recovery_code","secret"}

def walk_keys(x):
    if isinstance(x, dict):
        for k,v in x.items():
            yield str(k).lower()
            yield from walk_keys(v)
    elif isinstance(x, list):
        for v in x:
            yield from walk_keys(v)

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    for k in ["identity","authority","current_frontier","provenance","custody_pointers","reconstruction_recipe","exception_register","human_fallback","domain_cases"]:
        if k not in d:
            raise SystemExit("FAIL:missing:"+k)
    if any(d["authority"].values()):
        raise SystemExit("FAIL: authority drift")
    public_projection={
        "identity":d["identity"],
        "provenance":d["provenance"],
        "human_fallback":d["human_fallback"],
        "public_safe":d["custody_pointers"]["public_safe"]
    }
    for k in walk_keys(public_projection):
        if k in SECRET_KEYS:
            raise SystemExit("FAIL:secret-bearing key:"+k)
    for c in d["domain_cases"]:
        got=c["independent_domains"] >= 3
        if got is not c["expected_valid"]:
            raise SystemExit("FAIL:"+c["id"])
    if not d["current_frontier"]["unknowns"]:
        raise SystemExit("FAIL: unknowns erased")
    if not d["reconstruction_recipe"]["stop_conditions"]:
        raise SystemExit("FAIL: stop conditions absent")
    hf=d["human_fallback"]
    if not hf.get("first_safe_step") or not hf.get("do_not_guess"):
        raise SystemExit("FAIL: human fallback incomplete")
    for k in [
        "live_independent_reader_proof",
        "live_second_domain_readproof",
        "live_third_domain_readproof",
        "provider_account_not_required_proven",
        "primary_local_site_not_required_proven",
        "primary_git_host_not_required_proven"
    ]:
        if d[k] is not False:
            raise SystemExit("FAIL: overclaim:"+k)
    print("PASS: minimal recovery kernel structural canary preserves uncertainty and failure-domain boundaries")

if __name__=="__main__":
    main()
