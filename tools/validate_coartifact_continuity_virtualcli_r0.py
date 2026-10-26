#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/ux/coartifact_continuity_virtualcli_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    a=d["artifact_continuity"]; c=d["virtual_cli"]; s=d["substrate_mark"]
    if a["downloadable_is_durable_custody"] or a["session_attachment_is_durable_custody"]:
        raise SystemExit("FAIL:ephemeral treated durable")
    if a["session_termination_retires_artifact"] or a["human_transport_default"]:
        raise SystemExit("FAIL:session/human transport")
    if c["cli_is_user_workflow_default"] or c["virtualization_removes_cli"] or c["hidden_means_unauditable"]:
        raise SystemExit("FAIL:cli projection")
    if s["redefines_math_symbol"] or s["literal_keypress"] or s["compression_erases_provenance"]:
        raise SystemExit("FAIL:substrate mark")
    if d["surface_density"]["more_visible_state_implies_more_currentness"]:
        raise SystemExit("FAIL:density/currentness")
    if d["converge_spiral"]["permanent_active_loop_required"]:
        raise SystemExit("FAIL:permanent loop")
    if d["mythops_bridge"]["speculative_candidate_implies_operational_truth"] or d["mythops_bridge"]["speculation_grants_execution_authority"]:
        raise SystemExit("FAIL:mythops escalation")
    if d["parallelism"]["more_parallel_implies_more_progress"]:
        raise SystemExit("FAIL:parallelism")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: CoArtifactContinuity + CoVirtualCLI R0")
if __name__=="__main__": main()
