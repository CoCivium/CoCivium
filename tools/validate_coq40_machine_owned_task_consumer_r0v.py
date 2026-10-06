#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/coq40_machine_owned_task_consumer_r0v.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    for k in ["preexisting_task_consumption_proven","deterministic_readonly_execution_proven","hashed_receipt_proven"]:
        if d[k] is not True: raise SystemExit("FAIL:"+k)
    if d["model_call_required_for_execution_step"] is not False:
        raise SystemExit("FAIL:model dependency")
    for k in ["persistent_worker_installed","trigger_independence_proven","task_signature_present","receiver_acceptance_proven","cross_failure_domain_independence_proven"]:
        if d[k] is not False: raise SystemExit("FAIL:overclaim:"+k)
    if any(d["runtime_effects"].values()):
        raise SystemExit("FAIL:runtime effect")
    for k in ["task_sha256","target_sha256","receipt_sha256"]:
        if len(d[k]) != 64: raise SystemExit("FAIL:sha:"+k)
    print("PASS: Q40 machine-owned task consumer R0V")
if __name__=="__main__": main()
