#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/ux/corender_surface_gate_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    pipe=d["surface_pipeline"]
    required=["SOURCE_BIND","CI_VERIFY","BUILD","RECEIVER_PICKUP","RENDER_SMOKE","OBSERVER_READBACK","PROMOTE_CURRENT"]
    if any(x not in pipe for x in required): raise SystemExit("FAIL:pipeline")
    if d["ownership"]["session_is_surface"] or d["ownership"]["agent_is_surface"] or d["ownership"]["model_is_surface"]:
        raise SystemExit("FAIL:producer became surface")
    if d["promotion"]["ci_alone_sufficient"] is not False: raise SystemExit("FAIL:CI overclaim")
    if d["promotion"]["render_evidence_required"] is not True: raise SystemExit("FAIL:render")
    if d["cli"]["hidden_by_default"] is not True or d["cli"]["inspectable_on_diagnostic_or_recovery"] is not True:
        raise SystemExit("FAIL:CLI projection")
    if d["convergence"]["infinite_active_loop_required"] is not False:
        raise SystemExit("FAIL:infinite loop")
    if d["runtime_effect"] or d["public_deployment"]: raise SystemExit("FAIL:effect")
    print("PASS: CoRenderFabric / CoSurfaceGate R0")
if __name__=="__main__": main()
