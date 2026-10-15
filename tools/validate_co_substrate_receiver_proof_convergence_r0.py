#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def load_all(root):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.rglob("*.json"))]

def main():
    host_root=Path(sys.argv[1] if len(sys.argv)>1 else "cross-host-attestations")
    runtime_root=Path(sys.argv[2] if len(sys.argv)>2 else "cross-runtime-attestations")

    hosts=load_all(host_root)
    runtimes=load_all(runtime_root)
    vals=hosts+runtimes

    if len(hosts)!=2 or len(runtimes)!=2:
        fail(f"expected 2 host + 2 runtime attestations, got {len(hosts)} + {len(runtimes)}")

    keys=[
        "semantic_sha256",
        "object_id",
        "semantic_version",
        "authority_state",
        "scope",
        "source_git_sha",
        "tested_checkout_sha",
        "pr_head_sha",
        "pr_base_sha",
        "source_fixture_blob_sha",
    ]
    for key in keys:
        values={json.dumps(v.get(key),sort_keys=True) for v in vals}
        if len(values)!=1:
            fail(f"{key} mismatch across proof lanes")

    if {v["receiver"]["os"] for v in hosts}!={"Linux","Windows"}:
        fail("cross-host lane missing Linux/Windows pair")
    if {v["receiver"]["runtime"] for v in runtimes}!={"python","node"}:
        fail("cross-runtime lane missing Python/Node pair")
    if any(v.get("accepted_for_scope") is not True for v in vals):
        fail("at least one receiver rejected scope")

    print(json.dumps({
        "STATE":"PASS_COSUBSTRATE_RECEIVER_PROOF_CONVERGENCE_R0",
        "semantic_sha256":vals[0]["semantic_sha256"],
        "object_id":vals[0]["object_id"],
        "semantic_version":vals[0]["semantic_version"],
        "authority_state":vals[0]["authority_state"],
        "scope":vals[0]["scope"],
        "pr_head_sha":vals[0]["pr_head_sha"],
        "pr_base_sha":vals[0]["pr_base_sha"],
        "tested_checkout_sha":vals[0]["tested_checkout_sha"],
        "source_fixture_blob_sha":vals[0]["source_fixture_blob_sha"],
        "host_receivers":["Linux","Windows"],
        "runtime_receivers":["node","python"],
        "nonclaims":[
            "PROOF_CONVERGENCE_NE_MODEL_RUNTIME_MIGRATION",
            "PROOF_CONVERGENCE_NE_PHYSICAL_FAILURE_DOMAIN_INDEPENDENCE",
            "CI_PASS_NE_RUNTIME_ADOPTION"
        ]
    },separators=(",",":"),sort_keys=True))

if __name__=="__main__":
    main()
