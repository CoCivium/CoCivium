#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/architecture/cofield_mesh_bridge_r0g.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def route(b):
    if b["read_authority"] == "REVOKED" or b["write_authority"] == "REVOKED":
        return "HOLD_REVOKED"
    if b["confidentiality"] != "COMPATIBLE":
        return "HOLD_CONFIDENTIALITY"
    if b["discovery"] != "DISCOVERED":
        return "IGNORE_UNDISCOVERED"
    if b["capability"] != "CAPABLE":
        return "HOLD_INCAPABLE"
    if b["read_authority"] != "AUTHORIZED":
        return "HOLD_NO_READ_AUTHORITY"
    if b["connectivity"] == "DISCONNECTED":
        return "HOLD_DISCONNECTED"
    if b["currentness"] == "STALE":
        return "HOLD_STALE"
    if b["proof"] != "PROVEN":
        return "OBSERVE_UNPROVEN"
    if b["connectivity"] == "DEGRADED":
        return "DEGRADED_READ_ONLY"
    if b["write_authority"] != "AUTHORIZED":
        return "READ_ONLY_PROVEN"
    if not b["invitation"]:
        return "DRAFT_ONLY_NO_INVITATION"
    if b["seat"] != "MATERIALIZED":
        return "DRAFT_ONLY_NO_SEAT"
    if not b["effect_lease"]:
        return "DRAFT_ONLY_NO_EFFECT_LEASE"
    return "BOUNDED_WRITE_ELIGIBLE"

def attention(route_state):
    if route_state == "READ_ONLY_PROVEN":
        return "QUIET"
    if route_state in {"OBSERVE_UNPROVEN", "DEGRADED_READ_ONLY"}:
        return "WATCH"
    return "ACTIONABLE"

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    checks = [
        ("branchfield_doc_path", "branchfield_doc_blob_sha"),
        ("cocatchup_doc_path", "cocatchup_doc_blob_sha"),
        ("cocatchup_projection_path", "cocatchup_projection_blob_sha"),
    ]
    for path_key, sha_key in checks:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    observed = []
    counts = {"BOUNDED_WRITE_ELIGIBLE": 0, "QUIET": 0, "WATCH": 0, "ACTIONABLE": 0}
    for b in d["bridges"]:
        got_route = route(b)
        got_attention = attention(got_route)
        if got_route != b["expected_route"]:
            fail(f"FAIL_ROUTE:{b['id']}:got={got_route}:expected={b['expected_route']}")
        if got_attention != b["expected_attention"]:
            fail(f"FAIL_ATTENTION:{b['id']}:got={got_attention}:expected={b['expected_attention']}")
        counts["BOUNDED_WRITE_ELIGIBLE"] += int(got_route == "BOUNDED_WRITE_ELIGIBLE")
        counts[got_attention] += 1
        observed.append({
            "id": b["id"],
            "surface_id": b["surface_id"],
            "route": got_route,
            "attention": got_attention
        })

    exp = d["expected"]
    if len(d["bridges"]) != exp["bridge_count"]:
        fail("FAIL_BRIDGE_COUNT")
    if counts["BOUNDED_WRITE_ELIGIBLE"] != exp["write_eligible_count"]:
        fail("FAIL_WRITE_ELIGIBLE_COUNT")
    if counts["QUIET"] != exp["quiet_count"]:
        fail("FAIL_QUIET_COUNT")
    if counts["ACTIONABLE"] != exp["actionable_count"]:
        fail("FAIL_ACTIONABLE_COUNT")
    if counts["WATCH"] != exp["watch_count"]:
        fail("FAIL_WATCH_COUNT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_COFIELD_MESH_BRIDGE_R0G",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "bridge_count": len(d["bridges"]),
        "write_eligible_synthetic_count": counts["BOUNDED_WRITE_ELIGIBLE"],
        "attention_counts": {
            "QUIET": counts["QUIET"],
            "WATCH": counts["WATCH"],
            "ACTIONABLE": counts["ACTIONABLE"]
        },
        "real_external_effect_authority": False,
        "observed": observed,
        "rails": d["rails"]
    }
    print(json.dumps(receipt, separators=(",", ":")))

if __name__ == "__main__":
    main()
