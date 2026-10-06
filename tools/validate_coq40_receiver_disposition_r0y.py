#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/coq40_receiver_disposition_r0y.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    s=d["source"]
    for k in ["task_sha256","target_sha256","receipt_sha256"]:
        if len(s[k]) != 64:
            raise SystemExit("FAIL:"+k)
    if d["receipt_accepted"] is not True:
        raise SystemExit("FAIL:receipt acceptance")
    if d["semantic_claim_promoted"] is not False:
        raise SystemExit("FAIL:semantic overclaim")
    if any(d[k] for k in ["signed_task_authenticity_proven","signed_receipt_authenticity_proven","chatgpt_independent_trigger_proven","provider_exit_complete"]):
        raise SystemExit("FAIL:authenticity/independence overclaim")
    if any(v != 0 for v in d["effect_counts"].values()):
        raise SystemExit("FAIL:effect")
    if d["persistent_worker_installed"]:
        raise SystemExit("FAIL:persistence")
    if d["semantic_disposition"] != "HOLD_UNDERLYING_STALENESS_CLASSIFICATION_AS_RECEIVER_RELATIVE":
        raise SystemExit("FAIL:semantic disposition")
    print("PASS: Q40 receiver disposition over machine receipt R0Y")
if __name__=="__main__": main()
