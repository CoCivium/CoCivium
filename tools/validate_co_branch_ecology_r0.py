#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
P=Path("fixtures/architecture/co_branch_ecology_r0.json")
def fail(x): raise SystemExit(x)
def canonical_sha(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    prs=d["open_prs"]; nums=[p["number"] for p in prs]
    heads=[p["head_sha"] for p in prs]; refs=[p["head_ref"] for p in prs]
    if d["schema"]!="CoBranchEcology.R0B": fail("FAIL_SCHEMA")
    if len(prs)!=d["open_pr_count"]: fail("FAIL_OPEN_PR_COUNT")
    if d["open_pr_count"] < 26: fail("FAIL_R0B_PR_COUNT")
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
    allowed={"CANDIDATE_SCOPE_OVERLAP","CANDIDATE_FANIN_TO"}
    for r in d["candidate_relations"]:
        if r["from_pr"] not in known or r["to_pr"] not in known: fail("FAIL_REL_ENDPOINT")
        if r["relation"] not in allowed: fail("FAIL_RELATION_TYPE")
        if r["relation"]=="CANDIDATE_SCOPE_OVERLAP" and r["effect"]!="NO_SUPERSESSION_INFERENCE": fail("FAIL_OVERLAP_EFFECT")
        if r["relation"]=="CANDIDATE_FANIN_TO" and r["effect"]!="NO_MERGE_NO_CLOSE_NO_SUPERSESSION_INFERENCE": fail("FAIL_FANIN_EFFECT")
    fan=[r for r in d["candidate_relations"] if r["from_pr"]==151 and r["to_pr"]==150 and r["relation"]=="CANDIDATE_FANIN_TO"]
    if len(fan)!=1: fail("FAIL_PR151_PR150_FANIN_REL")
    required_deltas={
      "POTENTIAL_RELATION_NE_INSTANTIATED_RELATION",
      "COOMNI_NE_EVERY_RELATION_AT_ONCE",
      "MOVE_OFF_X2_NE_MOVE_TO_ONE_NEW_ROOT",
      "CANDIDATE_RECEIVER_NE_OUTREACH_AUTHORITY",
      "COUNTDOWN_NE_RELEASE_AUTHORITY"
    }
    if not required_deltas.issubset(set(fan[0].get("donor_deltas",[]))): fail("FAIL_DONOR_DELTAS")
    p=d["policy"]
    if not p["branch_reuse_preferred"] or not p["fanin_before_more_parallel_mutation"]: fail("FAIL_REUSE_FANIN_POLICY")
    if p["newest_wins"] or p["merge_automatic"] or p["close_automatic"]: fail("FAIL_AUTOMATIC_POLICY")
    if p["non_draft_review_sensitive_prs"] != [127]: fail("FAIL_REVIEW_SENSITIVE_SET")
    if p["current_branch_ecology_host_candidate"] != 150: fail("FAIL_HOST")
    s=d["snapshot_semantics"]
    if s["host_pr"]!=150: fail("FAIL_SNAPSHOT_HOST")
    if s["host_head_in_snapshot_interpretation"]!="OBSERVED_PRE_SNAPSHOT_MUTATION": fail("FAIL_SELF_REFERENCE_SEMANTICS")
    if not s["host_head_expected_to_change_when_snapshot_is_committed"]: fail("FAIL_SELF_REFERENCE_EXPECTATION")
    if not s["live_currentness_requires_fresh_query"]: fail("FAIL_LIVE_CURRENTNESS")
    required={
      "OPEN_PR_NE_ACTIVE_WORK","BRANCH_NE_AUTHORITY","CLUSTER_NE_DUPLICATE",
      "OVERLAP_NE_SUPERSESSION","FANIN_NE_MERGE","PR_COUNT_NE_PROGRESS",
      "NO_NEWEST_WINS","VALIDATION_IS_NOT_ACCEPTANCE",
      "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
      "SNAPSHOT_NE_LIVE_VIEW","HOST_HEAD_IN_SNAPSHOT_NE_POST_COMMIT_HEAD",
      "CANDIDATE_FANIN_TO_NE_MERGED","DONOR_DELTA_NE_ACCEPTED_DELTA"
    }
    if not required.issubset(set(d["nonclaims"])): fail("FAIL_NONCLAIMS")
    print(json.dumps({
      "STATE":"PASS_CO_BRANCH_ECOLOGY_R0B",
      "open_pr_count":len(prs),
      "cluster_count":len(d["clusters"]),
      "candidate_relation_count":len(d["candidate_relations"]),
      "pr151_to_pr150_fanin_relation_count":len(fan),
      "snapshot_source_branch_head":s["snapshot_source_branch_head"],
      "host_head_semantics":s["host_head_in_snapshot_interpretation"],
      "fixture_semantic_sha256":canonical_sha(d),
      "merge_authorized":False,"close_authorized":False,"canon_state":"UNPROVEN"
    },separators=(",",":")))
if __name__=="__main__": main()
