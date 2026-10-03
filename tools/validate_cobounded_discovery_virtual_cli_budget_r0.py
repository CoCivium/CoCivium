#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cobounded_discovery_virtual_cli_budget_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["bounded_discovery"]["metaphysical_truth_claim"] or d["bounded_discovery"]["global_omniscience_claim"]:
        raise SystemExit("FAIL:metaphysical overclaim")
    if d["virtual_cli"]["default_user_visibility"] != "VIRTUAL_INTERNAL":
        raise SystemExit("FAIL:cli default")
    if d["virtual_cli"]["hidden_ne_unauditable"] is not True:
        raise SystemExit("FAIL:auditability")
    b=d["budget"]
    if b["financial_authority_granted"] or b["personal_asset_equals_treasury"] or b["market_analysis_equals_trade_authority"]:
        raise SystemExit("FAIL:financial authority drift")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: bounded discovery + virtual CLI + budget relations R0")
if __name__=="__main__": main()
