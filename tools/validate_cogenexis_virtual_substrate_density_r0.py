#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cogenexis_virtual_substrate_density_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    t=d["theory"]; v=d["virtual_substrate"]; x=d["density"]; b=d["budget"]; c=d["convergence"]
    if any([t["prior_total_knowledge_established"],t["cosmic_choice_established"],t["prelife_established"],t["death_reintegration_established"]]):
        raise SystemExit("FAIL: metaphysical overclaim")
    if v["cli_user_visible_default"] is not False or v["substrate_inspectable_on_demand"] is not True or v["hidden_authority_allowed"] is not False:
        raise SystemExit("FAIL: virtual substrate")
    if v["marker_has_command_authority"] is not False:
        raise SystemExit("FAIL: marker authority")
    if x["shorter_is_always_better"] or x["compression_may_erase"] or x["inventory_count_equals_active_work"]:
        raise SystemExit("FAIL: density/bloat")
    if b["spend_authority_inferred"] or b["current_crypto_balance_known"]:
        raise SystemExit("FAIL: finance overclaim")
    if c["endless_active_loop"] or not c["requires_delta_condition"] or not c["requires_stop_or_park"] or not c["requires_wake_condition"]:
        raise SystemExit("FAIL: loop metabolism")
    if any(d["effects"].values()):
        raise SystemExit("FAIL: effects")
    print("PASS: CoGenExIs + virtual substrate + density + convergence R0")
if __name__=="__main__": main()
