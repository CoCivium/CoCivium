#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path

OBJ=Path("fixtures/substrate/co_substrate_cross_host_object_r0.json")

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def canonical_sha(value):
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    data=json.loads(OBJ.read_text(encoding="utf-8"))

    if data.get("authority_state")!="READ_ONLY":
        fail("authority drift")
    if not data.get("provenance"):
        fail("provenance missing")
    if len(data.get("relations",[]))!=3:
        fail("relation-count invariant failed")

    required=set(data.get("required_invariants",[]))
    observed={
        f"relation_count={len(data.get('relations',[]))}",
        f"authority_state={data.get('authority_state')}",
        "provenance_present" if data.get("provenance") else "provenance_missing",
    }
    if not required.issubset(observed):
        fail("required invariants not preserved")

    attestation={
        "schema":"CoSubstrateIndependence.CrossHostAttestation.R0",
        "object_id":data["object_id"],
        "semantic_version":data["semantic_version"],
        "semantic_sha256":canonical_sha(data),
        "authority_state":data["authority_state"],
        "source_git_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "tested_checkout_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "pr_head_sha":os.environ.get("CO_PR_HEAD_SHA",""),
        "pr_base_sha":os.environ.get("CO_PR_BASE_SHA",""),
        "source_fixture_blob_sha":subprocess.check_output(["git","hash-object",str(OBJ)],text=True).strip(),
        "required_invariants":sorted(required),
        "observed_invariants":sorted(observed),
        "receiver":{
            "os":platform.system(),
            "os_release":platform.release(),
            "python":platform.python_version()
        },
        "accepted_for_scope":True,
        "scope":"REPRESENTATIONAL_CONTINUITY_PLUS_INVARIANT_AND_AUTHORITY_PRESERVATION",
        "nonclaims":[
            "CROSS_OS_CI_NE_MODEL_RUNTIME_MIGRATION",
            "SAME_SEMANTIC_DIGEST_NE_IDENTICAL_INSTANCE",
            "CI_RECEIVER_PROOF_NE_PRODUCTION_RUNTIME",
            "ATTESTATION_NE_SOURCE_BINDING_UNLESS_EXACT_REF"
        ]
    }
    Path(args.out).write_text(json.dumps(attestation,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(attestation,separators=(",",":"),sort_keys=True))

if __name__=="__main__":
    main()
