#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cosneak_failure_domain_diversity_audit_r0o.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if len(d["samples"]) != d["totals"]["sampled_proof_families"]:
        raise SystemExit("FAIL:sample count")
    if sum(1 for x in d["samples"] if x["receiver_or_process_count"]>1) != d["totals"]["multi_identity_families"]:
        raise SystemExit("FAIL:multiplicity count")
    if any(x["cross_failure_domain_proven"] for x in d["samples"]):
        raise SystemExit("FAIL:failure-domain overclaim")
    zero_keys=["cross_failure_domain_independence_proven","provider_independence_proven","distinct_credential_roots_proven","distinct_physical_hosts_proven","distinct_sites_proven","distinct_execution_substrates_proven"]
    if any(d["totals"][k] != 0 for k in zero_keys):
        raise SystemExit("FAIL:independence overclaim")
    if len(d["required_future_dimensions"]) < 8:
        raise SystemExit("FAIL:weak failure-domain vector")
    if d["sampled_scope_closed"] is not True or d["global_resilience_proven"] is not False:
        raise SystemExit("FAIL:scope")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: CoSneak Q14 failure-domain diversity audit R0O")
if __name__=="__main__": main()
