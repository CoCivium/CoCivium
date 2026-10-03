#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path
P=Path("fixtures/architecture/co_branch_ecology_r0.json")
def fail(code): raise SystemExit(code)
def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    prs=d["open_prs"]; nums=[p["number"] for p in prs]
    heads=[p["head_sha"] for p in prs]; refs=[p["head_ref"] for p in prs]
    if len(prs)!=d["open_pr_count"]: fail("FAIL_OPEN_PR_COUNT")
    if len(nums)!=len(set(nums)): fail("FAIL_DUPLICATE_PR_NUMBER")
    if len(heads)!=len(set(heads)): fail("FAIL_DUPLICATE_HEAD_SHA")
    if len(refs)!=len(set(refs)): fail("FAIL_DUPLICATE_HEAD_REF")
    if any(p["lifecycle_state"]!="LANDED_PUBLIC_CANDIDATE_BRANCH" for p in prs): fail("FAIL_LIFECYCLE")
    if any(p["integration_state"]!="UNPROVEN" or p["canon_state"]!="UNPROVEN" for p in prs): fail("FAIL_BOUNDARY")
    known=set(nums); covered=set()
    for c in d["clusters"]:
        m=set(c["members"])
        if not m.issubset(known): fail("FAIL_CLUSTER_UNKNOWN:"+c["id"])
        covered|=m
    if covered!=known: fail("FAIL_CLUSTER_COVERAGE")
    for r in d["candidate_relations"]:
        if r["from_pr"] not in known or r["to_pr"] not in known: fail("FAIL_REL_ENDPOINT")
        if r["relation"]!="CANDIDATE_SCOPE_OVERLAP" or r["effect"]!="NO_SUPERSESSION_INFERENCE": fail("FAIL_RELATION")
    p=d["policy"]
    if not p["branch_reuse_preferred"] or not p["fanin_before_more_parallel_mutation"]: fail("FAIL_REUSE_FANIN_POLICY")
    if p["newest_wins"] or p["merge_automatic"] or p["close_automatic"]: fail("FAIL_AUTOMATIC_POLICY")
    if p["non_draft_review_sensitive_prs"] != [127]: fail("FAIL_REVIEW_SENSITIVE_SET")
    if p["current_branch_ecology_host_candidate"] != 150: fail("FAIL_HOST")
    required={"OPEN_PR_NE_ACTIVE_WORK","BRANCH_NE_AUTHORITY","CLUSTER_NE_DUPLICATE","OVERLAP_NE_SUPERSESSION","FANIN_NE_MERGE","PR_COUNT_NE_PROGRESS","NO_NEWEST_WINS","VALIDATION_IS_NOT_ACCEPTANCE","NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"}
    if not required.issubset(set(d["nonclaims"])): fail("FAIL_NONCLAIMS")
    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({
      "STATE":"PASS_CO_BRANCH_ECOLOGY_R0",
      "checked_out_head_sha":head,
      "open_pr_count":len(prs),
      "cluster_count":len(d["clusters"]),
      "candidate_overlap_relation_count":len(d["candidate_relations"]),
      "non_draft_review_sensitive_prs":p["non_draft_review_sensitive_prs"],
      "current_branch_ecology_host_candidate":p["current_branch_ecology_host_candidate"],
      "fixture_semantic_sha256":canonical_sha(d),
      "merge_authorized":False,"close_authorized":False,"canon_state":"UNPROVEN"
    },separators=(",",":")))
if __name__=="__main__": main()
