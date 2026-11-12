#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/evolution/cofrontier_qwen3_0_6b_provenance_r0.json")
SELF = Path("tools/validate_cofrontier_qwen3_0_6b_provenance_r0.py")
DOC = Path("docs/Architecture/COFRONTIER_QWEN3_0_6B_PROVENANCE_R0.md")
WF = Path(".github/workflows/cofrontier-intake-r0.yml")

REV = "c1899de289a04d12100db370d81485cdf75e47ca"
MODEL_SHA = "f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b"
TOKENIZER_SHA = "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"

def fail(x):
    raise SystemExit(x)

def blob(p):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{p.as_posix()}"],text=True).strip()

def sem(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()

def is_hex(s,n):
    if not isinstance(s,str) or len(s) != n:
        return False
    try:
        int(s,16)
        return True
    except ValueError:
        return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    d=json.loads(P.read_text(encoding="utf-8"))

    c=d["candidate"]
    if c["repository"] != "Qwen/Qwen3-0.6B":
        fail("FAIL_REPOSITORY")
    if c["revision_sha"] != REV or not is_hex(c["revision_sha"],40):
        fail("FAIL_REVISION")
    if d["source_evidence"]["revision_api_reported_sha"] != REV:
        fail("FAIL_API_REVISION_BIND")

    arts={x["path"]:x for x in d["exact_core_artifacts"]}
    if set(arts) != {"model.safetensors","tokenizer.json"}:
        fail("FAIL_CORE_ARTIFACT_SET")
    if arts["model.safetensors"]["sha256"] != MODEL_SHA or not is_hex(MODEL_SHA,64):
        fail("FAIL_MODEL_HASH")
    if arts["tokenizer.json"]["sha256"] != TOKENIZER_SHA or not is_hex(TOKENIZER_SHA,64):
        fail("FAIL_TOKENIZER_HASH")

    lic=d["license_evidence"]
    if lic["declared_license_id"] != "apache-2.0":
        fail("FAIL_LICENSE_ID")
    if lic["license_text_identity"] != "Apache License Version 2.0, January 2004":
        fail("FAIL_LICENSE_TEXT_IDENTITY")
    if lic["license_source_verified"] is not True:
        fail("FAIL_LICENSE_SOURCE")
    if lic["requested_scope_legal_adjudication"] != "UNPERFORMED":
        fail("FAIL_FALSE_LEGAL_ADJUDICATION")
    if lic["license_ok_for_runtime_route"] is not False:
        fail("FAIL_RUNTIME_LICENSE_GATE")

    pkg=d["runtime_package"]
    for k in ["model_downloaded","tokenizer_downloaded","isolated_canary_executed","capability_evaluated","coall_related","routable_for_scope"]:
        if pkg[k] is not False:
            fail("FAIL_EFFECT_OR_STAGE_DRIFT:"+k)
    if pkg["complete_required_file_hash_manifest"] is not False:
        fail("FAIL_FULL_PACKAGE_OVERCLAIM")
    if not pkg["unhashed_or_not_independently_verified_components"]:
        fail("FAIL_MISSING_PACKAGE_GAP")

    lc=d["lifecycle"]
    if lc["provenance_state"] != "PROVENANCE_VERIFIED_FOR_PINNED_CORE_ARTIFACTS":
        fail("FAIL_PROVENANCE_STATE")
    if lc["next_gate"] != "COMPLETE_RUNTIME_PACKAGE_MANIFEST_AND_LICENSE_SCOPE_REVIEW_BEFORE_ISOLATED_CANARY":
        fail("FAIL_NEXT_GATE")

    if any(int(v) != 0 for v in d["effects"].values()):
        fail("FAIL_EXTERNAL_EFFECT_DRIFT")

    required={
      "CORE_ARTIFACT_HASH_METADATA_NE_FULL_PACKAGE_VERIFICATION",
      "LICENSE_SOURCE_VERIFIED_NE_LEGAL_SCOPE_ADJUDICATED",
      "PROVENANCE_VERIFIED_NE_CAPABILITY_VALIDATED",
      "MODEL_AVAILABLE_NE_PROVIDER_EXIT_READY",
      "VALIDATION_IS_NOT_ACCEPTANCE",
      "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
    }
    if not required.issubset(set(d["nonclaims"])):
        fail("FAIL_NONCLAIMS")

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    out={
      "schema":"CoFrontierIntake.RealModelProvenanceReadproof.v0.1",
      "STATE":"PASS_REAL_MODEL_CORE_PROVENANCE_R0",
      "checked_out_head_sha":head,
      "receiver_identity":"github-actions:cofrontier-intake-r0",
      "candidate_id":c["candidate_id"],
      "pinned_revision_sha":REV,
      "model_safetensors_sha256":MODEL_SHA.upper(),
      "tokenizer_json_sha256":TOKENIZER_SHA.upper(),
      "declared_license_id":"apache-2.0",
      "provenance_state":lc["provenance_state"],
      "complete_runtime_package_hash_manifest":False,
      "isolated_canary_executed":False,
      "model_downloads":0,
      "runtime_route_changes":0,
      "fixture_semantic_sha256":sem(d),
      "exact_object_readproof":{
        "fixture_blob_sha1":blob(P),
        "validator_blob_sha1":blob(SELF),
        "workflow_blob_sha1":blob(WF),
        "doc_blob_sha1":blob(DOC)
      },
      "next_gate":lc["next_gate"],
      "integration_state":"UNPROVEN",
      "coverage_boundary":[
        "PUBLIC_HUGGINGFACE_SOURCE_EVIDENCE_OBSERVED_2026_10_02",
        "PINNED_REPOSITORY_REVISION",
        "MODEL_AND_TOKENIZER_HASH_METADATA_ONLY",
        "LICENSE_SOURCE_IDENTITY_ONLY",
        "NO_MODEL_BYTES_DOWNLOADED_BY_THIS_CANARY",
        "NO_INFERENCE"
      ],
      "nonclaims":d["nonclaims"]
    }
    o=Path(a.output)
    if o.exists():
        fail("FAIL_NO_CLOBBER")
    o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,separators=(",",":")))

if __name__=="__main__":
    main()
