#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else "cross-host-attestations")
    files=sorted(root.rglob("*.json"))
    if len(files)!=2:
        fail(f"expected 2 attestations, got {len(files)}")

    vals=[json.loads(p.read_text(encoding="utf-8")) for p in files]
    if len({v["semantic_sha256"] for v in vals})!=1:
        fail("semantic digest mismatch across receivers")
    if len({v["object_id"] for v in vals})!=1:
        fail("object identity mismatch across receivers")
    if len({v["semantic_version"] for v in vals})!=1:
        fail("semantic version mismatch across receivers")
    if len({v["authority_state"] for v in vals})!=1:
        fail("authority mismatch across receivers")
    if len({v["source_git_sha"] for v in vals})!=1:
        fail("source git SHA mismatch across receivers")
    if len({v["source_fixture_blob_sha"] for v in vals})!=1:
        fail("source fixture blob mismatch across receivers")
    if any(v.get("accepted_for_scope") is not True for v in vals):
        fail("receiver rejected continuity scope")
    if len({v["receiver"]["os"] for v in vals})!=2:
        fail("expected two distinct receiver OS families")

    for v in vals:
        if v["scope"]!="REPRESENTATIONAL_CONTINUITY_PLUS_INVARIANT_AND_AUTHORITY_PRESERVATION":
            fail("unexpected continuity scope")
        claims=set(v.get("nonclaims",[]))
        required={
            "CROSS_OS_CI_NE_MODEL_RUNTIME_MIGRATION",
            "SAME_SEMANTIC_DIGEST_NE_IDENTICAL_INSTANCE",
            "CI_RECEIVER_PROOF_NE_PRODUCTION_RUNTIME",
            "ATTESTATION_NE_SOURCE_BINDING_UNLESS_EXACT_REF"
        }
        if not required.issubset(claims):
            fail("required nonclaims missing")

    print(json.dumps({
        "STATE":"PASS_CROSS_OS_CI_RECEIVER_PROOF_R0",
        "semantic_sha256":vals[0]["semantic_sha256"],
        "receivers":[v["receiver"]["os"] for v in vals],
        "scope":vals[0]["scope"],
        "source_git_sha":vals[0]["source_git_sha"],
        "source_fixture_blob_sha":vals[0]["source_fixture_blob_sha"],
        "nonclaims":[
            "CROSS_OS_CI_NE_MODEL_RUNTIME_MIGRATION",
            "SAME_SEMANTIC_DIGEST_NE_IDENTICAL_INSTANCE",
            "CI_RECEIVER_PROOF_NE_PRODUCTION_RUNTIME",
            "ATTESTATION_NE_SOURCE_BINDING_UNLESS_EXACT_REF"
        ]
    },separators=(",",":"),sort_keys=True))

if __name__=="__main__":
    main()
