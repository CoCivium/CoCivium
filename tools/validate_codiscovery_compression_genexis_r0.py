#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/codiscovery_compression_genexis_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["genexis"]["established_fact"] or d["genexis"]["death_reintegration_proven"] or d["genexis"]["prelife_state_proven"]:
        raise SystemExit("FAIL: metaphysical overclaim")
    if d["cli"]["user_visible_by_default"] is not False or d["cli"]["effect_visibility_required"] is not True:
        raise SystemExit("FAIL: cli UX")
    if d["compression"]["canonical"] or d["compression"]["collision_review_required"] is not True:
        raise SystemExit("FAIL: glyph canon/collision")
    if d["budget"]["budget_grants_spend_authority"]:
        raise SystemExit("FAIL: budget authority")
    if d["stonk"]["every_value_relation_is_financial_asset"] or d["stonk"]["trade_authority_implied"]:
        raise SystemExit("FAIL: stonk collapse")
    if d["exos"]["installed_os_claim"]:
        raise SystemExit("FAIL: exos overclaim")
    if d["looping"]["sentience_implied"] or d["looping"]["convergence_implies_truth"]:
        raise SystemExit("FAIL: loop epistemic overclaim")
    if d["runtime_effect"] or d["financial_effect"] or d["public_effect"]:
        raise SystemExit("FAIL: effects")
    print("PASS: CoDiscovery/Compression/GenExIs relational synthesis R0")
if __name__=="__main__": main()
