#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

P = Path("fixtures/architecture/co_branch_convergence_disposition_r0c.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))

    if d["schema"] != "CoBranchConvergenceDisposition.R0C":
        fail("FAIL_SCHEMA")
    if d["host"]["pr"] != 150:
        fail("FAIL_HOST")
    if d["host"]["superseder"] is not False:
        fail("FAIL_HOST_SUPERSEDER")
    if d["host"]["canon_state"] != "UNPROVEN":
        fail("FAIL_HOST_CANON_STATE")

    members = d["members"]
    nums = [m["pr"] for m in members]
    if nums != [146, 147, 148, 149, 151]:
        fail("FAIL_MEMBER_SET")
    if len({m["head_sha"] for m in members}) != len(members):
        fail("FAIL_DUPLICATE_HEAD_SHA")
    if any(len(m["head_sha"]) != 40 for m in members):
        fail("FAIL_HEAD_SHA_LENGTH")
    if any(m["retirement_eligible_now"] is not False for m in members):
        fail("FAIL_PREMATURE_RETIREMENT_ELIGIBILITY")

    by_pr = {m["pr"]: m for m in members}
    if by_pr[146]["disposition"] != "KEEP_ACTIVE_PROOF_DONOR":
        fail("FAIL_146_DISPOSITION")
    if by_pr[149]["relation_to_host"] != "CANDIDATE_FANIN_TO":
        fail("FAIL_149_FANIN")
    if by_pr[151]["relation_to_host"] != "CANDIDATE_FANIN_TO":
        fail("FAIL_151_FANIN")

    required_151 = {
        "POTENTIAL_RELATION_NE_INSTANTIATED_RELATION",
        "COOMNI_NE_EVERY_RELATION_AT_ONCE",
        "MOVE_OFF_X2_NE_MOVE_TO_ONE_NEW_ROOT",
        "CANDIDATE_RECEIVER_NE_OUTREACH_AUTHORITY",
        "COUNTDOWN_NE_RELEASE_AUTHORITY"
    }
    if not required_151.issubset(set(by_pr[151]["donor_deltas"])):
        fail("FAIL_151_DONOR_DELTAS")

    ladder = d["convergence_ladder"]
    if ladder[-1] != "ONLY_THEN_CONSIDER_BRANCH_RETIREMENT":
        fail("FAIL_RETIREMENT_LAST")
    if ladder.index("RECEIVER_EXACT_OBJECT_READPROOF") <= ladder.index("MANIFEST_EXACT_DONOR_DELTAS"):
        fail("FAIL_PICKUP_ORDER")
    if ladder.index("ONLY_THEN_CONSIDER_BRANCH_RETIREMENT") <= ladder.index("RECEIVER_EXACT_OBJECT_READPROOF"):
        fail("FAIL_RETIREMENT_ORDER")

    rc = d["retirement_proof_contract"]
    if not all([
        rc["requires_exact_donor_manifest"],
        rc["requires_host_receiver_readproof"],
        rc["requires_lineage_pointer"],
        rc["requires_negative_knowledge_preservation"],
        rc["requires_wake_condition_preservation"],
        rc["requires_no_unresolved_unique_proof_lane"]
    ]):
        fail("FAIL_RETIREMENT_CONTRACT")
    if rc["close_authorized_by_this_contract"] is not False:
        fail("FAIL_CLOSE_AUTHORITY")

    bp = d["branch_creation_policy"]
    if not bp["relate_before_branch"] or not bp["reuse_existing_compatible_host"]:
        fail("FAIL_BRANCH_REUSE_POLICY")
    if not bp["new_branch_requires_distinct_collision_domain_or_independent_canary"]:
        fail("FAIL_NEW_BRANCH_GATE")
    if bp["conceptual_branch_ne_git_branch"] is not True:
        fail("FAIL_CONCEPTUAL_BRANCH_SEPARATION")
    if bp["zero_open_branches_is_goal"] is not False:
        fail("FAIL_ZERO_BRANCH_GOAL")

    required_nonclaims = {
        "DISPOSITION_NE_MERGE",
        "DISPOSITION_NE_CLOSE",
        "FANIN_RELATION_NE_CONTENT_TRANSFER",
        "DONOR_MANIFEST_NE_RECEIVER_PICKUP",
        "PICKUP_NE_INTEGRATION",
        "RETIREMENT_CANDIDATE_NE_RETIREMENT_AUTHORITY",
        "BRANCH_CLOSE_NE_HISTORY_ERASURE",
        "CONCEPTUAL_BRANCH_NE_GIT_BRANCH",
        "PR_COUNT_NE_PROGRESS",
        "VALIDATION_IS_NOT_ACCEPTANCE",
        "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
    }
    if not required_nonclaims.issubset(set(d["nonclaims"])):
        fail("FAIL_NONCLAIMS")

    print(json.dumps({
        "STATE": "PASS_CO_BRANCH_CONVERGENCE_DISPOSITION_R0C",
        "host_pr": 150,
        "member_count": len(members),
        "active_proof_donor_count": sum(m["disposition"] == "KEEP_ACTIVE_PROOF_DONOR" for m in members),
        "fanin_candidate_count": sum(m["relation_to_host"] == "CANDIDATE_FANIN_TO" for m in members),
        "retirement_eligible_now_count": sum(m["retirement_eligible_now"] for m in members),
        "close_authorized": False,
        "merge_authorized": False,
        "fixture_semantic_sha256": canonical_sha(d)
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
