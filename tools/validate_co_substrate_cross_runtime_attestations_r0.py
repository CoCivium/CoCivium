#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else "cross-runtime-attestations")
    files=sorted(root.rglob("*.json"))
    if len(files)!=2:
        fail(f"expected 2 attestations, got {len(files)}")
    vals=[json.loads(p.read_text(encoding="utf-8")) for p in files]

    if {v["receiver"]["runtime"] for v in vals}!={"python","node"}:
        fail("expected python and node receivers")
    for key in ("semantic_sha256","object_id","semantic_version","authority_state","scope","source_git_sha","tested_checkout_sha","pr_head_sha","pr_base_sha","source_fixture_blob_sha"):
        if len({json.dumps(v[key],sort_keys=True) for v in vals})!=1:
            fail(f"{key} mismatch across runtimes")
    if any(v.get("accepted_for_scope") is not True for v in vals):
        fail("runtime receiver rejected continuity scope")

    required={
        "CROSS_LANGUAGE_RUNTIME_NE_MODEL_RUNTIME_MIGRATION",
        "SAME_SEMANTIC_DIGEST_NE_IDENTICAL_INSTANCE",
        "CI_RECEIVER_PROOF_NE_PRODUCTION_RUNTIME",
        "ATTESTATION_NE_SOURCE_BINDING_UNLESS_EXACT_REF"
    }
    for v in vals:
        if not required.issubset(set(v.get("nonclaims",[]))):
            fail("required nonclaims missing")

    print(json.dumps({
        "STATE":"PASS_CROSS_LANGUAGE_RUNTIME_RECEIVER_PROOF_R0",
        "semantic_sha256":vals[0]["semantic_sha256"],
        "runtimes":sorted(v["receiver"]["runtime"] for v in vals),
        "scope":vals[0]["scope"],
        "source_git_sha":vals[0]["source_git_sha"],
        "tested_checkout_sha":vals[0]["tested_checkout_sha"],
        "pr_head_sha":vals[0]["pr_head_sha"],
        "pr_base_sha":vals[0]["pr_base_sha"],
        "source_fixture_blob_sha":vals[0]["source_fixture_blob_sha"],
        "nonclaims":sorted(required)
    },separators=(",",":"),sort_keys=True))

if __name__=="__main__":
    main()
