#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path

P=Path("fixtures/cocivia/coall_resource_convergence_challenge_r0.json")

def fail(x): raise SystemExit(x)
def blob(path): return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()
def csha(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    sb=d["source_bindings"]
    if blob(sb["convergence_map_path"])!=sb["convergence_map_blob_sha"]: fail("FAIL_MAP_BIND")
    if blob(sb["convergence_doc_path"])!=sb["convergence_doc_blob_sha"]: fail("FAIL_DOC_BIND")

    m=json.loads(Path(sb["convergence_map_path"]).read_text(encoding="utf-8"))
    owner_set={x["primary_owner"] for x in m["domains"]}

    pure=d["pure_cases"]
    if len(pure)!=d["expected"]["pure_case_count"]: fail("FAIL_PURE_COUNT")
    if any(x["expected_owner"] not in owner_set for x in pure): fail("FAIL_PURE_OWNER_OUTSIDE_MAP")
    if len({x["expected_owner"] for x in pure})!=9: fail("FAIL_PURE_OWNER_COVERAGE")

    multi=d["multi_domain_cases"]
    if len(multi)!=d["expected"]["multi_domain_case_count"]: fail("FAIL_MULTI_COUNT")
    for x in multi:
        if len(x["expected_owners"])<2: fail("FAIL_MULTI_COLLAPSED:"+x["id"])
        if any(o not in owner_set for o in x["expected_owners"]): fail("FAIL_MULTI_OWNER_OUTSIDE_MAP:"+x["id"])
        if x["expected_decision"]!="PRESERVE_MULTI_DOMAIN_RELATIONS": fail("FAIL_MULTI_DECISION:"+x["id"])

    rails=set(m["required_rails"])
    extra={
      "MENTION_NE_RESOURCE_WAKE",
      "RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY"
    }
    known=rails|extra
    forb=d["forbidden_collapses"]
    if len(forb)!=d["expected"]["forbidden_collapse_count"]: fail("FAIL_FORBIDDEN_COUNT")
    for x in forb:
        if not x["violates"]: fail("FAIL_FORBIDDEN_NO_RAIL:"+x["id"])
        if any(v not in known for v in x["violates"]): fail("FAIL_UNKNOWN_RAIL:"+x["id"])

    if d["expected"]["single_owner_for_multi_domain_count"]!=0: fail("FAIL_MULTI_SINGLE_OWNER_POLICY")
    for k in ["file_moves_authorized","renames_authorized","merges_authorized","runtime_changes_authorized"]:
        if d["expected"][k]!=0: fail("FAIL_MUTATION_AUTHORITY:"+k)

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    out={
      "STATE":"PASS_COALL_RESOURCE_CONVERGENCE_ADVERSARIAL_CHALLENGE_R0",
      "checked_out_head_sha":head,
      "pure_case_count":len(pure),
      "pure_owner_coverage_count":len({x["expected_owner"] for x in pure}),
      "multi_domain_case_count":len(multi),
      "multi_domain_preserved_count":len(multi),
      "forbidden_collapse_count":len(forb),
      "file_moves_authorized":0,
      "renames_authorized":0,
      "merges_authorized":0,
      "runtime_changes_authorized":0,
      "fixture_semantic_sha256":csha(d),
      "nonclaims":d["nonclaims"]
    }
    print(json.dumps(out,separators=(",",":")))

if __name__=="__main__": main()
