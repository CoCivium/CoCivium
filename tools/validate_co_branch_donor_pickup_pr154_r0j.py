#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

MANIFEST = Path("fixtures/architecture/co_branch_donor_pickup_pr154_r0j.json")

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
            "User-Agent": "CoCivium-PR150-PR154-donor-pickup-r0j"
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

    pr = api_get("/repos/CoCivium/CoCivium/pulls/154", token)
    live_head = pr.get("head", {}).get("sha")
    if live_head != donor["exact_head_sha"]:
        fail("FAIL_PR154_CURRENT_HEAD_DRIFT:" + str(live_head))

    checked = git_text(root, "rev-parse", "HEAD")
    if checked != donor["exact_head_sha"]:
        fail("FAIL_PR154_DONOR_CHECKOUT_HEAD:" + checked)

    combined_text = ""
    readproofs = []
    for obj in donor["objects"]:
        path = obj["Provenance"]["path"]
        expected_blob = obj["ContentHash"].split(":", 1)[1]
        actual_blob = git_text(root, "rev-parse", "HEAD:" + path)
        if actual_blob != expected_blob:
            fail("FAIL_PR154_GIT_BLOB:" + path)
        raw = (root / path).read_bytes()
        combined_text += "\n" + raw.decode("utf-8", errors="replace")
        readproofs.append({
            "Identity": obj["Identity"],
            "donor_pr": 154,
            "path": path,
            "git_blob_sha1": actual_blob,
            "content_sha256": sha256(raw),
            "receiver_readproof": "PASS_EXACT_OBJECT_READBACK"
        })

    for delta in donor["selected_donor_deltas"]:
        if delta not in combined_text:
            fail("FAIL_PR154_DONOR_DELTA_MISSING:" + delta)

    for item in donor["negative_knowledge_to_preserve"]:
        if item not in combined_text:
            fail("FAIL_PR154_NEGATIVE_KNOWLEDGE_MISSING:" + item)

    fx = json.loads(
        (root / "fixtures/relations/cogenex_virtualsubstrate_convergespiral_r0.json")
        .read_text(encoding="utf-8")
    )
    if fx.get("runtime_effect") is not False:
        fail("FAIL_PR154_RUNTIME_EFFECT")
    if fx.get("public_effect") is not False:
        fail("FAIL_PR154_PUBLIC_EFFECT")
    theory = fx.get("theory", {})
    if theory.get("prelife_state") != "UNPROVEN":
        fail("FAIL_PR154_PRELIFE_OVERCLAIM")
    if theory.get("postdeath_reintegration") != "UNPROVEN":
        fail("FAIL_PR154_POSTDEATH_OVERCLAIM")
    finance = fx.get("finance", {})
    if finance.get("verified_crypto_balance") is not False:
        fail("FAIL_PR154_CRYPTO_BALANCE_OVERCLAIM")
    if finance.get("trade_effect") is not False:
        fail("FAIL_PR154_TRADE_EFFECT")
    if finance.get("budget_mutation") is not False:
        fail("FAIL_PR154_BUDGET_MUTATION")

    host_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoBranchDonorPickup.PR154.Readproof.R0J.v0.1",
        "STATE": "PASS_PR154_EXACT_DONOR_PICKUP_BY_PR150_RECEIVER_R0J",
        "checked_out_host_head_sha": host_head,
        "host_pr": 150,
        "receiver_identity": m["host"]["receiver_identity"],
        "donor_pr": 154,
        "donor_exact_head_sha": donor["exact_head_sha"],
        "donor_live_head_sha_at_read": live_head,
        "exact_object_count": len(readproofs),
        "readproofs": readproofs,
        "selected_donor_deltas_preserved": donor["selected_donor_deltas"],
        "negative_knowledge_preserved": donor["negative_knowledge_to_preserve"],
        "unique_proof_lane": donor["unique_proof_lane"],
        "convergence_relation": m["convergence_relation"],
        "integration_state": "UNPROVEN",
        "branch_retirement_authorized": False,
        "branch_close_authorized": False,
        "merge_authorized": False,
        "canon_state": "UNPROVEN",
        "coverage_boundary": m["coverage_boundary"],
        "nonclaims": m["nonclaims"]
    }

    if receipt["exact_object_count"] != 4:
        fail("FAIL_RECEIPT_CARDINALITY")

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_host_head_sha": host_head,
        "donor_pr": receipt["donor_pr"],
        "donor_exact_head_sha": receipt["donor_exact_head_sha"],
        "exact_object_count": receipt["exact_object_count"],
        "integration_state": receipt["integration_state"],
        "branch_retirement_authorized": receipt["branch_retirement_authorized"],
        "merge_authorized": receipt["merge_authorized"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
