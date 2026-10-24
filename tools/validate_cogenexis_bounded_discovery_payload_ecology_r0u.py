#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cogenexis_bounded_discovery_payload_ecology_r0u.json")
def main():
 d=json.loads(P.read_text(encoding="utf-8")); x=d["domains"]
 if not x["theory"]["metaphysics_hypothesis_only"]: raise SystemExit("FAIL:metaphysics")
 if x["theory"]["death_reintegration_proven"] or x["theory"]["omniscient_whole_proven"]: raise SystemExit("FAIL:cosmic overclaim")
 if x["authority"]["deity_term_grants_runtime_authority"]: raise SystemExit("FAIL:deity authority")
 if x["ux"]["cli_primary_user_experience"] or not x["ux"]["virtual_substrate_default"]: raise SystemExit("FAIL:ux")
 if not x["ux"]["expandable_meaning_required"] or not x["ux"]["recovery_path_required"]: raise SystemExit("FAIL:opaque compression")
 if x["loops"]["recursion_without_delta_action"]!="PARK": raise SystemExit("FAIL:loop")
 if x["finance"]["financial_authority_granted"] or x["finance"]["trading_effect"] or x["finance"]["wallet_effect"]: raise SystemExit("FAIL:finance")
 if d["runtime_effect"] or d["public_effect"] or d["canon_effect"]: raise SystemExit("FAIL:effect")
 print("PASS: CoGenExIs bounded discovery/payload ecology R0U")
if __name__=="__main__": main()
