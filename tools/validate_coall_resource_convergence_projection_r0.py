#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cocivia/coall_resource_convergence_projection_r0.json")

def fail(code):
    raise SystemExit(code)

def blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"], text=True).strip()

def csha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",",":")).encode()
    ).hexdigest().upper()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    sb = d["source_bindings"]

    pairs = [
      ("convergence_map_path","convergence_map_blob_sha"),
      ("convergence_challenge_path","convergence_challenge_blob_sha"),
      ("correspondence_path","correspondence_blob_sha"),
      ("grant_path","grant_blob_sha"),
      ("lease_path","lease_blob_sha"),
      ("activation_path","activation_blob_sha"),
      ("compaction_path","compaction_blob_sha"),
      ("composition_path","composition_blob_sha"),
      ("failover_path","failover_blob_sha"),
      ("pulsefield_path","pulsefield_blob_sha"),
      ("prelaunch_path","prelaunch_blob_sha"),
      ("substrate_path","substrate_blob_sha")
    ]
    for pk, sk in pairs:
        if blob(sb[pk]) != sb[sk]:
            fail("FAIL_SOURCE_BIND:" + sb[pk])

    cmap = json.loads(Path(sb["convergence_map_path"]).read_text(encoding="utf-8"))
    challenge = json.loads(Path(sb["convergence_challenge_path"]).read_text(encoding="utf-8"))

    map_owner_by_domain = {x["domain"]: x["primary_owner"] for x in cmap["domains"]}
    ps = d["projections"]
    if len(ps) != d["expected"]["projection_count"]:
        fail("FAIL_PROJECTION_COUNT")
    if len({x["projection_id"] for x in ps}) != len(ps):
        fail("FAIL_DUPLICATE_PROJECTION_ID")

    for p in ps:
        domain = p["semantic_domain"]
        if domain not in map_owner_by_domain:
            fail("FAIL_DOMAIN_NOT_IN_MAP:" + domain)
        if p["target_owner"] != map_owner_by_domain[domain]:
            fail("FAIL_OWNER_DRIFT:" + domain)

    candidate_interfaces = [
        p for p in ps if p["mutation_action"] == "INTERFACE_EXTRACTION_CANDIDATE_ONLY"
    ]
    candidate_projections = [
        p for p in ps if p["mutation_action"] == "PROJECTION_CANDIDATE_ONLY"
    ]
    existing_refs = [
        p for p in ps if p["mutation_action"] == "NONE"
        and p["relation"] == "REFERENCE_EXISTING_OWNER"
    ]
    cocivia_keep = [
        p for p in ps if p["mutation_action"] == "NONE"
        and p["relation"] == "KEEP_AS_COCIVIA_SPECIFIC_LAYER"
    ]

    if len(candidate_interfaces) != d["expected"]["candidate_interface_count"]:
        fail("FAIL_INTERFACE_COUNT")
    if len(candidate_projections) != d["expected"]["candidate_projection_count"]:
        fail("FAIL_PROJECTION_CANDIDATE_COUNT")
    if len(existing_refs) != d["expected"]["existing_owner_reference_count"]:
        fail("FAIL_EXISTING_REF_COUNT")
    if len(cocivia_keep) != d["expected"]["cocivia_specific_keep_count"]:
        fail("FAIL_COCIVIA_KEEP_COUNT")

    required_interface_fields = {
      "P-GRANT": {"grant_id","participant_or_owner","resource_class","scope_or_purpose",
                  "privacy_or_confidentiality_scope","state","capacity_or_cap","revocation","provenance"},
      "P-LEASE": {"lease_id","resource_id","work_or_holder_id","fence_or_epoch",
                  "lease_state","expiry_or_revalidation_condition","revocation_state","provenance"}
    }
    by_id = {p["projection_id"]: p for p in ps}
    for pid, fields in required_interface_fields.items():
        if set(by_id[pid].get("required_fields", [])) != fields:
            fail("FAIL_INTERFACE_FIELDS:" + pid)

    mixed = d["mixed_relation_reconstructions"]
    if len(mixed) != d["expected"]["mixed_relation_reconstruction_count"]:
        fail("FAIL_MIXED_COUNT")
    challenge_multi = {x["id"]: x for x in challenge["multi_domain_cases"]}
    expected_case_map = {"R-M01":"M01","R-M02":"M02"}
    for x in mixed:
        source_case = challenge_multi[expected_case_map[x["case_id"]]]
        if not set(source_case["expected_owners"]).issubset(set(x["ordered_relation_chain"])):
            fail("FAIL_MIXED_OWNER_COVERAGE:" + x["case_id"])
        if len(x["ordered_relation_chain"]) != len(set(x["ordered_relation_chain"])):
            fail("FAIL_MIXED_DUPLICATE_OWNER:" + x["case_id"])

    if d["future_extraction_contract"]["source_docs_remain_provenance_donors"] is not True:
        fail("FAIL_SOURCE_DONOR_RETENTION")
    if d["future_extraction_contract"]["new_interface_must_reference_source_blob"] is not True:
        fail("FAIL_INTERFACE_SOURCE_BIND_POLICY")
    if d["future_extraction_contract"]["new_projection_must_preserve_nonclaims"] is not True:
        fail("FAIL_NONCLAIM_PRESERVATION_POLICY")

    for key in ["file_moves_authorized","renames_authorized","merges_authorized","runtime_changes_authorized"]:
        if d["expected"][key] != 0:
            fail("FAIL_MUTATION_AUTHORITY:" + key)

    rails = set(d["rails"])
    required = {
      "RESOURCE_GRANT_NE_CAPACITY_FIELD",
      "RESOURCE_LEASE_NE_EFFECT_LEASE",
      "SUBSTRATE_CAPABILITY_NE_RESOURCE_GRANT",
      "MENTION_NE_RESOURCE_WAKE",
      "PROJECTION_NE_SCHEMA_MERGE",
      "EXTRACTION_CONTRACT_NE_EXTRACTION",
      "SOURCE_DONOR_NE_DEPRECATED",
      "NEWEST_NE_WINNER",
      "VALIDATION_IS_NOT_ACCEPTANCE"
    }
    if not required.issubset(rails):
        fail("FAIL_RAIL_SET")

    head = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    out = {
      "STATE":"PASS_COALL_RESOURCE_CONVERGENCE_PROJECTION_R0",
      "checked_out_head_sha":head,
      "projection_count":len(ps),
      "candidate_interface_count":len(candidate_interfaces),
      "candidate_projection_count":len(candidate_projections),
      "existing_owner_reference_count":len(existing_refs),
      "cocivia_specific_keep_count":len(cocivia_keep),
      "mixed_relation_reconstruction_count":len(mixed),
      "file_moves_authorized":0,
      "renames_authorized":0,
      "merges_authorized":0,
      "runtime_changes_authorized":0,
      "fixture_semantic_sha256":csha(d),
      "rails":d["rails"]
    }
    print(json.dumps(out,separators=(",",":")))

if __name__ == "__main__":
    main()
