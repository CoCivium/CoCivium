#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

MANIFEST = Path("fixtures/architecture/co_branch_donor_pickup_pr151_r0d.json")

def fail(code):
    raise SystemExit(code)

def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()

def api_get(path, token):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CoCivium-PR150-PR151-donor-pickup-r0d"
        }
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def git_text(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--donor-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        fail("FAIL_GITHUB_TOKEN_MISSING")

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    donor = m["donor"]
    root = Path(args.donor_root)

    pr = api_get("/repos/CoCivium/CoCivium/pulls/151", token)
    live_head = pr.get("head", {}).get("sha")
    if live_head != donor["exact_head_sha"]:
        fail("FAIL_PR151_CURRENT_HEAD_DRIFT:" + str(live_head))

    checked = git_text(root, "rev-parse", "HEAD")
    if checked != donor["exact_head_sha"]:
        fail("FAIL_DONOR_CHECKOUT_HEAD:" + checked)

    readproofs = []
    combined_text = ""
    for obj in donor["objects"]:
        path = obj["Provenance"]["path"]
        expected_blob = obj["ContentHash"].split(":", 1)[1]
        actual_blob = git_text(root, "rev-parse", "HEAD:" + path)
        if actual_blob != expected_blob:
            fail("FAIL_GIT_BLOB:" + path)
        raw = (root / path).read_bytes()
        combined_text += "\n" + raw.decode("utf-8", errors="replace")
        readproofs.append({
            "Identity": obj["Identity"],
            "path": path,
            "git_blob_sha1": actual_blob,
            "content_sha256": sha256(raw),
            "receiver_readproof": "PASS_EXACT_OBJECT_READBACK"
        })

    for delta in donor["selected_donor_deltas"]:
        if delta not in combined_text:
            fail("FAIL_DONOR_DELTA_MISSING:" + delta)

    for item in donor["negative_knowledge_to_preserve"]:
        if item not in combined_text:
            fail("FAIL_NEGATIVE_KNOWLEDGE_MISSING:" + item)

    fixture_path = root / "fixtures/relations/coall_bounded_discovery_projection_r0.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    if fixture.get("runtime_effect") is not False:
        fail("FAIL_DONOR_RUNTIME_EFFECT_BOUNDARY")
    if fixture.get("public_effect") is not False:
        fail("FAIL_DONOR_PUBLIC_EFFECT_BOUNDARY")
    if fixture.get("convergence", {}).get("wake_on_delta") is not True:
        fail("FAIL_WAKE_ON_DELTA_NOT_PRESERVED")

    host_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoBranchDonorPickup.PR151.Readproof.R0D.v0.1",
        "STATE": "PASS_PR151_EXACT_DONOR_PICKUP_BY_PR150_RECEIVER_R0D",
        "checked_out_host_head_sha": host_head,
        "host_pr": 150,
        "receiver_identity": m["host"]["receiver_identity"],
        "donor_pr": 151,
        "donor_exact_head_sha": donor["exact_head_sha"],
        "donor_live_head_sha_at_read": live_head,
        "exact_object_count": len(readproofs),
        "readproofs": readproofs,
        "selected_donor_deltas_preserved": donor["selected_donor_deltas"],
        "negative_knowledge_preserved": donor["negative_knowledge_to_preserve"],
        "wake_relation_preserved": donor["wake_relation_to_preserve"],
        "runtime_effect": False,
        "public_effect": False,
        "integration_state": "UNPROVEN",
        "branch_retirement_authorized": False,
        "branch_close_authorized": False,
        "merge_authorized": False,
        "canon_state": "UNPROVEN",
        "coverage_boundary": m["coverage_boundary"],
        "nonclaims": m["nonclaims"]
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_host_head_sha": host_head,
        "donor_exact_head_sha": donor["exact_head_sha"],
        "exact_object_count": receipt["exact_object_count"],
        "selected_donor_delta_count": len(receipt["selected_donor_deltas_preserved"]),
        "negative_knowledge_count": len(receipt["negative_knowledge_preserved"]),
        "wake_relation_preserved": receipt["wake_relation_preserved"],
        "integration_state": receipt["integration_state"],
        "branch_retirement_authorized": receipt["branch_retirement_authorized"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
