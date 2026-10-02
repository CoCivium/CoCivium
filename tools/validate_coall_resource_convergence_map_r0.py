#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cocivia/coall_resource_convergence_map_r0.json")

def fail(code):
    raise SystemExit(code)

def blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"], text=True).strip()

def csha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    sb=d["source_bindings"]
    pairs=[
      ("pulsefield_path","pulsefield_blob_sha"),
      ("prelaunch_path","prelaunch_blob_sha"),
      ("substrate_path","substrate_blob_sha"),
      ("front_principal_path","front_principal_blob_sha"),
      ("correspondence_path","correspondence_blob_sha"),
      ("grant_field_path","grant_field_blob_sha"),
      ("lease_path","lease_blob_sha"),
      ("activation_path","activation_blob_sha"),
      ("failover_path","failover_blob_sha"),
      ("compaction_path","compaction_blob_sha")
    ]
    for pk,sk in pairs:
        if blob(sb[pk]) != sb[sk]:
            fail("FAIL_SOURCE_BIND:"+sb[pk])

    domains=d["domains"]
    names=[x["domain"] for x in domains]
    if len(names)!=len(set(names)):
        fail("FAIL_DUPLICATE_DOMAIN")
    if len(domains)!=9:
        fail("FAIL_DOMAIN_COUNT")

    primary=[x["primary_owner"] for x in domains]
    if any(not x for x in primary):
        fail("FAIL_MISSING_PRIMARY_OWNER")

    required_owners={
      "CoCiviaCorrespondence","CoResourceGrantLayer","CoEnerget+","CoPlan+/CoOps+",
      "CoResourceLease+","EffectLease","CoSubstrateField+",
      "CoOps+ResourceExecutionProjection","CoEnerget+Projection"
    }
    if set(primary)!=required_owners:
        fail("FAIL_OWNER_SET")

    if next(x for x in domains if x["domain"]=="RESOURCE_RESERVATION_FENCING_REVOCATION_AND_HANDOFF")["primary_owner"]!="CoResourceLease+":
        fail("FAIL_RESOURCE_LEASE_OWNER")
    if next(x for x in domains if x["domain"]=="EFFECT_PERMISSION_FOR_ACTION_CLASS")["primary_owner"]!="EffectLease":
        fail("FAIL_EFFECT_LEASE_OWNER")

    rails=set(d["required_rails"])
    must={
      "RESOURCE_LEASE_NE_EFFECT_LEASE",
      "SUBSTRATE_CAPABILITY_NE_RESOURCE_GRANT",
      "CORRESPONDENCE_TRIGGER_NE_RESOURCE_AUTHORITY",
      "CORESOURCEFIELD_CANDIDATE_RELATES_TO_COENERGET__NOT_AUTOMATIC_RENAME",
      "EXTRACTION_CANDIDATE_NE_EXTRACTION",
      "NEWEST_NE_WINNER",
      "VALIDATION_IS_NOT_ACCEPTANCE"
    }
    if not must.issubset(rails):
        fail("FAIL_RAIL_SET")

    if any(x["action"] not in {"REVIEW_FOR_EXTRACTION_NOT_MOVE_YET","REVIEW_FOR_FOLDING_NOT_RENAME_YET"} for x in d["extraction_candidates"]):
        fail("FAIL_EXTRACTION_ACTION")

    head=subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    out={
      "STATE":"PASS_COALL_RESOURCE_CONVERGENCE_MAP_R0",
      "checked_out_head_sha":head,
      "domain_count":len(domains),
      "existing_main_owner_count":sum(x["owner_status"]=="EXISTING_MAIN" for x in domains),
      "candidate_extraction_owner_count":sum(x["owner_status"]=="CANDIDATE_EXTRACTION" for x in domains),
      "pr137_specific_owner_count":sum(x["owner_status"]=="CANDIDATE_PR137" for x in domains),
      "extraction_candidate_count":len(d["extraction_candidates"]),
      "file_moves_authorized":0,
      "renames_authorized":0,
      "merges_authorized":0,
      "runtime_changes":0,
      "fixture_semantic_sha256":csha(d),
      "nonclaims":d["nonclaims"]
    }
    print(json.dumps(out,separators=(",",":")))

if __name__=="__main__":
    main()
