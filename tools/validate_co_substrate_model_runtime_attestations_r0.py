#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else "model-runtime-attestations")
    files=sorted(root.rglob("*.json"))
    if len(files)!=2:
        fail(f"expected 2 attestations, got {len(files)}")
    vals=[json.loads(p.read_text(encoding="utf-8")) for p in files]
    if {v["engine"] for v in vals}!={"onnxruntime","openvino"}:
        fail("expected onnxruntime and openvino engines")
    for key in ("model_sha256","fixture_semantic_sha256","input","output","authority_state","pr_head_sha","pr_base_sha","scope"):
        if len({json.dumps(v[key],sort_keys=True) for v in vals})!=1:
            fail(f"{key} mismatch across model runtimes")
    if any(v.get("accepted_for_scope") is not True for v in vals):
        fail("runtime rejected canary scope")
    required={
        "INFERENCE_ENGINE_DIVERSITY_NE_LLM_RUNTIME_DIVERSITY",
        "CI_MODEL_CANARY_NE_X2_LOCAL_MODEL_HANDOFF",
        "NUMERIC_OUTPUT_MATCH_NE_AGENT_IDENTITY"
    }
    for v in vals:
        if not required.issubset(set(v.get("nonclaims",[]))):
            fail("required nonclaims missing")
    print(json.dumps({
        "STATE":"PASS_DISTINCT_INFERENCE_ENGINE_CONTINUITY_R0",
        "engines":sorted(v["engine"] for v in vals),
        "model_sha256":vals[0]["model_sha256"],
        "fixture_semantic_sha256":vals[0]["fixture_semantic_sha256"],
        "authority_state":vals[0]["authority_state"],
        "scope":vals[0]["scope"],
        "pr_head_sha":vals[0]["pr_head_sha"],
        "pr_base_sha":vals[0]["pr_base_sha"],
        "nonclaims":sorted(required)
    },separators=(",",":"),sort_keys=True))

if __name__=="__main__":
    main()
