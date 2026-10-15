#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cogenex_virtualsubstrate_convergespiral_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["theory"]["prelife_state"]!="UNPROVEN" or d["theory"]["postdeath_reintegration"]!="UNPROVEN":
        raise SystemExit("FAIL:metaphysical overclaim")
    if d["virtual_cli"]["primary_human_ux"] is not False:
        raise SystemExit("FAIL:CLI primary UX")
    if d["virtual_cli"]["inspectable"] is not True or d["virtual_cli"]["mandatory_invisibility"] is not False:
        raise SystemExit("FAIL:inspectability")
    if d["substrate_glyph"]["exact_symbol_canonized"] is not False:
        raise SystemExit("FAIL:glyph canon")
    if d["payload_density"]["more_dense_implies_better"] is not False:
        raise SystemExit("FAIL:density")
    if d["convergence"]["forced_infinite_loop"] is not False or d["convergence"]["quiescence_valid"] is not True:
        raise SystemExit("FAIL:loop")
    if any(d["recursion"].values()):
        raise SystemExit("FAIL:recursion anthropomorphism")
    if d["finance"]["verified_crypto_balance"] or d["finance"]["trade_effect"] or d["finance"]["budget_mutation"]:
        raise SystemExit("FAIL:financial overclaim/effect")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: CoGenEx/VirtualSubstrate/ConvergeSpiral R0")
if __name__=="__main__": main()
