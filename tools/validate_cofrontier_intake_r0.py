#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

P = Path("fixtures/evolution/cofrontier_intake_r0.json")
DOC = Path("docs/Architecture/COFRONTIER_INTAKE_R0.md")
WF = Path(".github/workflows/cofrontier-intake-r0.yml")
SELF = Path("tools/validate_cofrontier_intake_r0.py")

def fail(x):
    raise SystemExit(x)

def blob(p):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{p.as_posix()}"],text=True).strip()

def sem(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()

def decide(c):
    if c["stage"] == "RUMOURED":
        return "HOLD"
    if c["stage"] == "PUBLICLY_AVAILABLE" and not c["hash_verified"]:
        return "QUARANTINED"
    if c["hash_verified"] and not c["license_ok"]:
        return "LICENSE_BLOCKED"
    if c["capability_pass"] and not c["related"]:
        return "HOLD"
    if all([
        c["stage"] == "ROUTABLE_FOR_SCOPE",
        c["hash_verified"],
        c["license_ok"],
        c["canary_pass"],
        c["capability_pass"],
        c["related"],
        c["reconstructible"],
        bool(c["route_scope"])
    ]):
        return "ROUTABLE_FOR_SCOPE"
    return "HOLD"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    d=json.loads(P.read_text(encoding="utf-8"))

    expected=[
      "RUMOURED","CREDIBLE_SIGNAL","ANNOUNCED","PUBLICLY_AVAILABLE",
      "PROVENANCE_VERIFIED","ISOLATED_CANARY","CAPABILITY_EVALUATED",
      "COALL_RELATED","ROUTABLE_FOR_SCOPE"
    ]
    if d["lifecycle"] != expected:
        fail("FAIL_LIFECYCLE")

    observed=[]
    routable=0
    for c in d["cases"]:
        got=decide(c)
        if got != c["expected"]:
            fail("FAIL_CASE:"+c["id"]+":"+got)
        routable += int(got == "ROUTABLE_FOR_SCOPE")
        observed.append({"id":c["id"],"decision":got})

    if routable != 1:
        fail("FAIL_ROUTABLE_COUNT")
    if any(int(v) != 0 for v in d["effects"].values()):
        fail("FAIL_EFFECT_DRIFT")

    required={
      "NEWER_NE_BETTER","BIGGER_NE_BETTER","MODEL_NAME_NE_MODEL_IDENTITY",
      "OPEN_WEIGHTS_NE_OFFLINE_READY","TWO_MODELS_NE_TWO_FAILURE_DOMAINS",
      "ROUTABLE_FOR_SCOPE_NE_DEFAULT_ROUTE"
    }
    if set(d["negative_controls"]) != required:
        fail("FAIL_NEGATIVE_CONTROLS")

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    out={
      "schema":"CoFrontierIntake.Readproof.v0.1",
      "STATE":"PASS_COFRONTIER_INTAKE_R0",
      "checked_out_head_sha":head,
      "receiver_identity":"github-actions:cofrontier-intake-r0",
      "exact_object_readproof":{
        "fixture_blob_sha1":blob(P),
        "validator_blob_sha1":blob(SELF),
        "workflow_blob_sha1":blob(WF),
        "doc_blob_sha1":blob(DOC)
      },
      "fixture_semantic_sha256":sem(d),
      "case_count":len(d["cases"]),
      "routable_case_count":routable,
      "model_downloads":0,
      "runtime_route_changes":0,
      "lifecycle_state_for_fixture":"PICKED_UP_BY_EXACT_VALIDATOR",
      "integration_state":"UNPROVEN",
      "coverage_boundary":[
        "SYNTHETIC_MODEL_CANDIDATES_ONLY",
        "NO_REAL_MODEL_DOWNLOAD",
        "NO_REAL_LICENSE_ADJUDICATION",
        "NO_REAL_CAPABILITY_BENCHMARK",
        "NO_RUNTIME_ROUTING_CHANGE"
      ],
      "nonclaims":[
        "MODEL_AVAILABLE_NE_PROVIDER_EXIT_READY",
        "VALIDATION_IS_NOT_ACCEPTANCE",
        "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
      ],
      "observed":observed
    }
    o=Path(a.output)
    if o.exists():
        fail("FAIL_NO_CLOBBER")
    o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,separators=(",",":")))

if __name__=="__main__":
    main()
