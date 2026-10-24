#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/coq40_local_recurring_deed_canary_r0q.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if len(d["attempts"]) != 2: raise SystemExit("FAIL:attempt count")
    a1,a2=d["attempts"]
    if not a1["local_model_execution"] or a1["strict_output_contract"] is not False:
        raise SystemExit("FAIL:first attempt")
    if not a2["local_model_execution"] or a2["strict_output_contract"] is not True:
        raise SystemExit("FAIL:second attempt")
    if d["semantic_acceptance"]["accepted"] is not False:
        raise SystemExit("FAIL:semantic overclaim")
    if d["persistent_worker_installed"] or d["chatgpt_independence_proven"] or d["cross_failure_domain_independence_proven"]:
        raise SystemExit("FAIL:independence/persistence overclaim")
    if d["runtime_effects_beyond_bounded_canary"] != 0 or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: Q40 bounded local recurring-deed canary R0Q")
if __name__=="__main__": main()
