#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",",":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--output", required=True)
    args=ap.parse_args()

    files=sorted(Path(args.input_root).rglob("readproof.json"))
    if len(files) != 3:
        fail("FAIL_READPROOF_COUNT:" + str(len(files)))
    rs=[json.loads(p.read_text(encoding="utf-8")) for p in files]
    for r in rs:
        if r["STATE"] != "PASS_CLEAN_ROOM_RECOVERY_ORIENTATION_R0":
            fail("FAIL_READER_STATE")
        if r["destructive_authority"] is not False or r["external_effects"] != 0:
            fail("FAIL_READER_AUTHORITY")
        if r["github_failure_domain_independence_proven"] is not False:
            fail("FAIL_GITHUB_INDEPENDENCE_OVERCLAIM")
        if r["durable_offsite_custody_proven"] is not False:
            fail("FAIL_OFFSITE_OVERCLAIM")

    for key in ["packet_manifest_sha256","orientation_sha256","source_candidate_head_sha","reconstructed_system","reconstructed_priority_gap_count","reconstructed_first_safe_step"]:
        if len({json.dumps(r[key], sort_keys=True) for r in rs}) != 1:
            fail("FAIL_CROSS_READER_DRIFT:" + key)

    os_set={r["receiver_os"] for r in rs}
    if os_set != {"Linux","Windows","macOS"}:
        fail("FAIL_OS_SET:" + ",".join(sorted(os_set)))
    if len({r["receiver_id"] for r in rs}) != 3:
        fail("FAIL_RECEIVER_ID_DISTINCT")

    evidence=[{
        "receiver_id":r["receiver_id"],
        "packet_manifest_sha256":r["packet_manifest_sha256"],
        "orientation_sha256":r["orientation_sha256"],
        "source_candidate_head_sha":r["source_candidate_head_sha"]
    } for r in sorted(rs, key=lambda x:x["receiver_id"])]

    out_obj={
        "schema":"CoRecoveryKernel.CleanRoomFanin.v0.1",
        "STATE":"PASS_DISTINCT_READER_RECOVERY_ORIENTATION_CONVERGENCE_R0",
        "receiver_count":3,
        "receiver_os_set":sorted(os_set),
        "packet_manifest_sha256":rs[0]["packet_manifest_sha256"],
        "orientation_sha256":rs[0]["orientation_sha256"],
        "source_candidate_head_sha":rs[0]["source_candidate_head_sha"],
        "reconstructed_priority_gap_count":rs[0]["reconstructed_priority_gap_count"],
        "reader_evidence":evidence,
        "reader_evidence_semantic_sha256":canonical_sha(evidence),
        "self_contained_orientation_proven_for_packet":True,
        "provider_chat_required_for_reader":False,
        "x2_required_for_reader":False,
        "repository_worktree_required_for_reader":False,
        "github_failure_domain_independence_proven":False,
        "durable_second_domain_custody_proven":False,
        "account_close_safe":False,
        "integration_state":"UNPROVEN",
        "nonclaims":[
            "DISTINCT_RUNNER_OS_CLASSES_NE_FAILURE_DOMAIN_INDEPENDENCE",
            "SELF_CONTAINED_PACKET_NE_COMPLETE_HISTORY_DRAIN",
            "SELF_CONTAINED_PACKET_NE_ACCOUNT_CLOSE_SAFE",
            "WORKFLOW_ARTIFACT_NE_DURABLE_OFFSITE_CUSTODY",
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
        ]
    }
    out=Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_obj, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(out_obj, separators=(",",":")))

if __name__=="__main__":
    main()
