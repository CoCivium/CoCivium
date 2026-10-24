#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/coq40_changed_contract_local_semantic_pass_r0t.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["attempt_count"] != 1: raise SystemExit("FAIL:attempt count")
    if not d["checks"]["strict_json"] or not d["checks"]["changed_output_structure"] or not d["checks"]["semantic_acceptance"]:
        raise SystemExit("FAIL:acceptance chain")
    if d["checks"]["semantic_rejection_reason_count"] != 0: raise SystemExit("FAIL:rejection reasons")
    p=d["candidate"]["next_probe"]
    for f in ["kind","target","evidence_surface","expected_evidence","negative_evidence","stop_condition"]:
        if not isinstance(p.get(f),str) or not p[f].strip(): raise SystemExit("FAIL:probe:"+f)
    if d["candidate"]["nonclaim"] != "STALE_FILE_NE_STALE_SEMANTIC_STATE": raise SystemExit("FAIL:nonclaim")
    if d["q40_bounded_target_closed"] is not True: raise SystemExit("FAIL:q40 disposition")
    for k in ["persistent_worker_installed","receiver_execution_proven","integration_proven","chatgpt_independence_proven","provider_exit_complete","cross_failure_domain_independence_proven"]:
        if d[k] is not False: raise SystemExit("FAIL:overclaim:"+k)
    if d["runtime_effects_beyond_canary"] != 0 or d["public_effect"]: raise SystemExit("FAIL:effect")
    print("PASS: Q40 changed-contract local semantic pass R0T")
if __name__=="__main__": main()
