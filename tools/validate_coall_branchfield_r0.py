#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/architecture/coall_branchfield_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if len(d["branches"]) < 10: raise SystemExit("FAIL:branch coverage")
    for k in ["runtime_effect","public_effect","financial_effect","authority_effect","trade_authority","metaphysical_truth_claim","cli_primary_ux"]:
        if d[k] is not False: raise SystemExit("FAIL:"+k)
    if d["cli_inspectable"] is not True: raise SystemExit("FAIL:inspectability")
    req={"METAPHYSICAL_MODEL_NE_ESTABLISHED_FACT","CLI_HIDDEN_NE_CLI_NONEXISTENT","COMPRESSION_NE_ERASURE","BUDGET_NE_MONEY_ONLY","LOOP_NE_SENTIENCE"}
    if not req.issubset(set(d["rails"])): raise SystemExit("FAIL:rails")
    print("PASS: CoAll BranchField R0")
if __name__=="__main__": main()
