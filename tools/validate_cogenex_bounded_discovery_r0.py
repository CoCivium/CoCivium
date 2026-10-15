#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/theory/cogenex_bounded_discovery_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    h=d["hypotheses"]
    if h["prelife_choice_proven"] or h["postdeath_recomposition_proven"] or h["personal_continuity_after_death_proven"]:
        raise SystemExit("FAIL:metaphysical overclaim")
    if d["costonk"]["value_equals_price"] or d["costonk"]["optionality_implies_intent"]:
        raise SystemExit("FAIL:value/intent collapse")
    if d["warchest"]["trading_authority"]:
        raise SystemExit("FAIL:financial authority")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    if len(d["cobudget_dimensions"]) < 10:
        raise SystemExit("FAIL:budget too narrow")
    print("PASS: CoGenEx bounded-discovery relation model R0")
if __name__=="__main__": main()
