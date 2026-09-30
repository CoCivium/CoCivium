#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_multi_embodiment_r0.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--embodiment-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    matches = [e for e in doc["embodiments"] if e["embodiment_id"] == args.embodiment_id]
    if len(matches) != 1:
        fail("FAIL_EMBODIMENT_BIND")
    e = matches[0]
    lane = doc["logical_lane"]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

    receipt = {
        "schema": "CoModelSubstrateLight.MultiEmbodimentBranchReceipt.v0.1",
        "STATE": "PASS_SYNTHETIC_MULTI_EMBODIMENT_BRANCH",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(doc),
        "logical_lane_id": lane["logical_lane_id"],
        "completed_step_ids_observed": lane["completed_step_ids"],
        "replayed_completed_step_ids": [],
        "authority_ceiling": lane["authority_ceiling"],
        "confidentiality": lane["confidentiality"],
        "effect_ceiling": lane["effect_ceiling"],
        "effect_execution_total": 0,
        "embodiment_id": e["embodiment_id"],
        "route_class": e["route_class"],
        "failure_domain_label": e["failure_domain_label"],
        "lens": e["lens"],
        "shared_assertions": doc["shared_assertions_required"],
        "decision_key": doc["decision_key"],
        "candidate_decision": e["candidate_decision"],
        "candidate_claims": e["candidate_claims"],
        "provenance": [
            "fixture:model_substrate_light_multi_embodiment_r0",
            "branch:" + e["embodiment_id"],
            "head:" + head
        ],
        "nonclaims": doc["nonclaims"]
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_head_sha": head,
        "logical_lane_id": receipt["logical_lane_id"],
        "embodiment_id": receipt["embodiment_id"],
        "candidate_decision": receipt["candidate_decision"],
        "effect_execution_total": 0,
        "fixture_semantic_sha256": receipt["fixture_semantic_sha256"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
