#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

MANIFEST = Path("fixtures/architecture/co_branch_donor_pickup_pr152_pr153_r0i.json")

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
            "User-Agent": "CoCivium-PR150-PR152-PR153-donor-pickup-r0i"
        }
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def git_text(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

def check_effect_boundary(pr, root):
    if pr == 152:
        p = root / "fixtures/relations/codiscovery_compression_genexis_r0.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("runtime_effect") is not False:
            fail("FAIL_PR152_RUNTIME_EFFECT")
        if d.get("financial_effect") is not False:
            fail("FAIL_PR152_FINANCIAL_EFFECT")
        if d.get("public_effect") is not False:
            fail("FAIL_PR152_PUBLIC_EFFECT")
    elif pr == 153:
        p = root / "fixtures/relations/cogenexis_virtual_substrate_density_r0.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        if any(d.get("effects", {}).values()):
            fail("FAIL_PR153_EFFECT_BOUNDARY")
    else:
        fail("FAIL_UNKNOWN_DONOR_PR")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--donor-pr152-root", required=True)
    ap.add_argument("--donor-pr153-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        fail("FAIL_GITHUB_TOKEN_MISSING")

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    roots = {
        152: Path(args.donor_pr152_root),
        153: Path(args.donor_pr153_root),
    }
    readproofs = []
    donor_summaries = []

    for donor in m["donors"]:
        prn = int(donor["pr"])
        root = roots[prn]

        pr = api_get(f"/repos/CoCivium/CoCivium/pulls/{prn}", token)
        live_head = pr.get("head", {}).get("sha")
        if live_head != donor["exact_head_sha"]:
            fail(f"FAIL_PR{prn}_CURRENT_HEAD_DRIFT:" + str(live_head))

        checked = git_text(root, "rev-parse", "HEAD")
        if checked != donor["exact_head_sha"]:
            fail(f"FAIL_PR{prn}_DONOR_CHECKOUT_HEAD:" + checked)

        combined_text = ""
        donor_proofs = []
        for obj in donor["objects"]:
            path = obj["Provenance"]["path"]
            expected_blob = obj["ContentHash"].split(":", 1)[1]
            actual_blob = git_text(root, "rev-parse", "HEAD:" + path)
            if actual_blob != expected_blob:
                fail(f"FAIL_PR{prn}_GIT_BLOB:" + path)
            raw = (root / path).read_bytes()
            combined_text += "\n" + raw.decode("utf-8", errors="replace")
            proof = {
                "Identity": obj["Identity"],
                "donor_pr": prn,
                "path": path,
                "git_blob_sha1": actual_blob,
                "content_sha256": sha256(raw),
                "receiver_readproof": "PASS_EXACT_OBJECT_READBACK",
            }
            donor_proofs.append(proof)
            readproofs.append(proof)

        for delta in donor["selected_donor_deltas"]:
            if delta not in combined_text:
                fail(f"FAIL_PR{prn}_DONOR_DELTA_MISSING:" + delta)

        for item in donor["negative_knowledge_to_preserve"]:
            if item not in combined_text:
                fail(f"FAIL_PR{prn}_NEGATIVE_KNOWLEDGE_MISSING:" + item)

        check_effect_boundary(prn, root)

        donor_summaries.append({
            "donor_pr": prn,
            "donor_exact_head_sha": donor["exact_head_sha"],
            "donor_live_head_sha_at_read": live_head,
            "exact_object_count": len(donor_proofs),
            "selected_donor_deltas_preserved": donor["selected_donor_deltas"],
            "negative_knowledge_preserved": donor["negative_knowledge_to_preserve"],
            "unique_proof_lane": donor["unique_proof_lane"],
            "retirement_eligible_now": False,
        })

    host_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoBranchDonorPickup.PR152_PR153.Readproof.R0I.v0.1",
        "STATE": "PASS_PR152_PR153_EXACT_DONOR_PICKUP_BY_PR150_RECEIVER_R0I",
        "checked_out_host_head_sha": host_head,
        "host_pr": 150,
        "receiver_identity": m["host"]["receiver_identity"],
        "donor_count": len(donor_summaries),
        "exact_object_count": len(readproofs),
        "readproofs": readproofs,
        "donors": donor_summaries,
        "convergence_relation": m["convergence_relation"],
        "integration_state": "UNPROVEN",
        "branch_retirement_authorized": False,
        "branch_close_authorized": False,
        "merge_authorized": False,
        "canon_state": "UNPROVEN",
        "coverage_boundary": m["coverage_boundary"],
        "nonclaims": m["nonclaims"],
    }

    if receipt["donor_count"] != 2 or receipt["exact_object_count"] != 9:
        fail("FAIL_RECEIPT_CARDINALITY")

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_host_head_sha": host_head,
        "donor_count": receipt["donor_count"],
        "exact_object_count": receipt["exact_object_count"],
        "pr152_head": donor_summaries[0]["donor_exact_head_sha"],
        "pr153_head": donor_summaries[1]["donor_exact_head_sha"],
        "integration_state": receipt["integration_state"],
        "branch_retirement_authorized": receipt["branch_retirement_authorized"],
        "merge_authorized": receipt["merge_authorized"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
