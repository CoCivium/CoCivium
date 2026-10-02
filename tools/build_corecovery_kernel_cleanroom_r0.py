#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

SPEC = Path("fixtures/resilience/corecovery_kernel_cleanroom_r0.json")
TRIPLE = Path("fixtures/resilience/codependency_census_triple_loss_r0.json")
EXIT = Path("fixtures/resilience/coprovexit_mutualaid_r0.json")
VERIFY_SOURCE = Path("tools/verify_corecovery_kernel_cleanroom_r0.py")

def fail(code):
    raise SystemExit(code)

def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"], text=True).strip()

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args=ap.parse_args()
    out=Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.mkdir(parents=True)

    spec=json.loads(SPEC.read_text(encoding="utf-8"))
    triple=json.loads(TRIPLE.read_text(encoding="utf-8"))
    ex=json.loads(EXIT.read_text(encoding="utf-8"))

    source_manifest=[]
    for src in spec["source_bindings"]:
        path=src["path"]
        if git_blob(path) != src["git_blob_sha"]:
            fail("FAIL_SOURCE_BLOB_DRIFT:" + path)
        raw=Path(path).read_bytes()
        target=out / "sources" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        source_manifest.append({
            "path":"sources/" + path,
            "source_path":path,
            "git_blob_sha":src["git_blob_sha"],
            "sha256":sha256(raw),
            "bytes":len(raw)
        })

    gaps=triple["priority_gaps"]
    if gaps != spec["required_priority_gaps"]:
        fail("FAIL_PRIORITY_GAP_DRIFT")

    pe=ex["provider_exit"]
    if any([
        pe["current_exit_authority"],
        pe["account_deletion_allowed"],
        pe["provider_tab_closure_allowed"]
    ]):
        fail("FAIL_EXIT_AUTHORITY_DRIFT")

    head=subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    orientation={
        "schema":"CoRecoveryKernel.Orientation.v0.1",
        "STATE":"CANDIDATE_RECOVERY_ORIENTATION__NO_DESTRUCTIVE_AUTHORITY",
        "system":"CoCivium/CoAll",
        "source_candidate_head_sha":head,
        "source_branch_role":"provider-exit-resilience-candidate",
        "authority":spec["authority"],
        "current_nonclaims":spec["current_nonclaims"],
        "priority_continuity_gaps":gaps,
        "first_safe_step":"Verify packet manifest and exact source hashes before trusting any continuation pointer or attempting mutation.",
        "stop_conditions":[
            "manifest hash mismatch",
            "source hash mismatch",
            "authority ambiguous",
            "private custody pointer unavailable",
            "candidate/global currentness ambiguous"
        ],
        "recovery_sequence":[
            "verify packet bytes",
            "read authority boundaries",
            "read continuity gaps",
            "recover public bootstrap from an available verified source",
            "resolve private custody only through a separately authorized route",
            "bind a provider-neutral reasoning/execution route",
            "reconcile against a fresher currentness source before mutation"
        ],
        "source_manifest":source_manifest,
        "rails":spec["rails"]
    }
    write_json(out/"orientation.json", orientation)

    recover = """CoCivium / CoAll clean-room recovery packet R0

FIRST SAFE STEP
Verify packet manifest and exact source hashes before trusting any continuation pointer or attempting mutation.

WHAT THIS PACKET DOES
It provides bounded orientation, authority limits, exact source copies, known continuity gaps, and recovery instructions without requiring a ChatGPT transcript or the X2 local machine.

WHAT IT DOES NOT PROVE
It does not prove the ChatGPT account is safe to delete.
It does not prove all chats are drained.
It does not prove private offsite custody.
It does not prove independence from GitHub.
It does not authorize billing, credential, data-deletion, account-deletion, public, financial, or security-sensitive effects.

KNOWN PRIORITY GAPS
- independent public/bootstrap mirror
- proven private offsite custody
- provider-independent reasoning route
- human-readable offline recovery packet beyond transient CI transport
- second source/provenance host or export

STOP
Stop if hashes disagree, authority is ambiguous, private custody cannot be resolved through an authorized route, or currentness cannot be reconciled.
"""
    (out/"RECOVER.txt").write_text(recover, encoding="utf-8")

    shutil.copy2(VERIFY_SOURCE, out/"verify.py")

    files=[]
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            raw=path.read_bytes()
            files.append({
                "path":path.relative_to(out).as_posix(),
                "sha256":sha256(raw),
                "bytes":len(raw)
            })

    manifest={
        "schema":"CoRecoveryKernel.PacketManifest.v0.1",
        "STATE":"PASS_RECOVERY_PACKET_BUILT_R0",
        "source_candidate_head_sha":head,
        "file_count":len(files),
        "files":files,
        "orientation_sha256":sha256((out/"orientation.json").read_bytes()),
        "recover_text_sha256":sha256((out/"RECOVER.txt").read_bytes()),
        "transport_class":"GITHUB_ACTIONS_ARTIFACT_30_DAY_RETENTION",
        "durable_offsite_custody_proven":False,
        "external_effects":0,
        "nonclaims":[
            "WORKFLOW_ARTIFACT_NE_DURABLE_OFFSITE_CUSTODY",
            "CLEAN_ROOM_READER_NE_FAILURE_DOMAIN_INDEPENDENCE",
            "SELF_CONTAINED_ORIENTATION_NE_ACCOUNT_CLOSE_SAFE"
        ]
    }
    write_json(out/"manifest.json", manifest)
    print(json.dumps({
        "STATE":manifest["STATE"],
        "checked_out_head_sha":head,
        "file_count":manifest["file_count"],
        "orientation_sha256":manifest["orientation_sha256"],
        "manifest_sha256":sha256((out/"manifest.json").read_bytes()),
        "durable_offsite_custody_proven":False,
        "external_effects":0
    }, separators=(",",":")))

if __name__=="__main__":
    main()
