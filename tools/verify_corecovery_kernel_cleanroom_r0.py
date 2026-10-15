#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path

def fail(code):
    raise SystemExit(code)

def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("packet")
    ap.add_argument("--output", required=True)
    args=ap.parse_args()
    root=Path(args.packet)

    manifest_raw=(root/"manifest.json").read_bytes()
    manifest=json.loads(manifest_raw.decode("utf-8"))
    if manifest["STATE"] != "PASS_RECOVERY_PACKET_BUILT_R0":
        fail("FAIL_MANIFEST_STATE")
    if manifest["durable_offsite_custody_proven"] is not False:
        fail("FAIL_OFFSITE_OVERCLAIM")
    if manifest["external_effects"] != 0:
        fail("FAIL_EFFECT_DRIFT")

    for item in manifest["files"]:
        p=root/item["path"]
        raw=p.read_bytes()
        if len(raw) != item["bytes"]:
            fail("FAIL_BYTE_COUNT:" + item["path"])
        if sha256(raw) != item["sha256"]:
            fail("FAIL_FILE_HASH:" + item["path"])

    orientation_raw=(root/"orientation.json").read_bytes()
    if sha256(orientation_raw) != manifest["orientation_sha256"]:
        fail("FAIL_ORIENTATION_HASH")
    o=json.loads(orientation_raw.decode("utf-8"))

    if o["system"] != "CoCivium/CoAll":
        fail("FAIL_SYSTEM_IDENTITY")
    if len(o["source_candidate_head_sha"]) != 40:
        fail("FAIL_SOURCE_HEAD")
    if any(o["authority"].values()):
        fail("FAIL_AUTHORITY_DRIFT")
    if any(o["current_nonclaims"].values()):
        fail("FAIL_CURRENT_NONCLAIM_DRIFT")

    required_gaps={
        "INDEPENDENT_PUBLIC_BOOTSTRAP_MIRROR",
        "PROVEN_PRIVATE_OFFSITE_CUSTODY",
        "PROVIDER_INDEPENDENT_REASONING_ROUTE",
        "HUMAN_READABLE_OFFLINE_RECOVERY_PACKET",
        "SECOND_SOURCE_PROVENANCE_HOST_OR_EXPORT"
    }
    if set(o["priority_continuity_gaps"]) != required_gaps:
        fail("FAIL_PRIORITY_GAPS")
    if len(o["source_manifest"]) != 8:
        fail("FAIL_SOURCE_COUNT")
    if not o["first_safe_step"] or not o["stop_conditions"]:
        fail("FAIL_HUMAN_ORIENTATION")

    recover=(root/"RECOVER.txt").read_text(encoding="utf-8")
    if "FIRST SAFE STEP" not in recover or "\nSTOP\n" not in recover:
        fail("FAIL_HUMAN_RECOVERY_TEXT")

    receiver_os=os.environ.get("RUNNER_OS") or platform.system()
    receiver_arch=os.environ.get("RUNNER_ARCH") or platform.machine()
    readproof={
        "schema":"CoRecoveryKernel.CleanRoomReadproof.v0.1",
        "STATE":"PASS_CLEAN_ROOM_RECOVERY_ORIENTATION_R0",
        "receiver_id":f"{receiver_os}:{receiver_arch}",
        "receiver_os":receiver_os,
        "receiver_arch":receiver_arch,
        "packet_manifest_sha256":sha256(manifest_raw),
        "orientation_sha256":sha256(orientation_raw),
        "source_candidate_head_sha":o["source_candidate_head_sha"],
        "reconstructed_system":o["system"],
        "reconstructed_priority_gap_count":len(o["priority_continuity_gaps"]),
        "reconstructed_first_safe_step":o["first_safe_step"],
        "destructive_authority":False,
        "account_close_safe_claimed":False,
        "provider_account_required_for_packet_read":False,
        "x2_required_for_packet_read":False,
        "git_worktree_required_for_packet_read":False,
        "github_failure_domain_independence_proven":False,
        "durable_offsite_custody_proven":False,
        "external_effects":0,
        "coverage_boundary":[
            "PACKET_BYTES_ONLY_AFTER_DOWNLOAD",
            "NO_REPOSITORY_CHECKOUT_IN_READER_JOB",
            "NO_CHAT_HISTORY_REQUIRED",
            "NO_X2_REQUIRED",
            "GITHUB_ACTIONS_TRANSPORT_STILL_REQUIRED_FOR_THIS_CANARY"
        ]
    }
    out=Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.write_text(json.dumps(readproof, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(readproof, separators=(",",":")))

if __name__=="__main__":
    main()
