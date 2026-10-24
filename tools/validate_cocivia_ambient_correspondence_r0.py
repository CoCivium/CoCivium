#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cocivia/co_cocivia_ambient_correspondence_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def route(c):
    if c["surface_class"] == "UNENROLLED_PRIVATE_SURFACE" or not c["surface_enrolled"]:
        return "DROP_NO_INGRESS_AUTHORITY"

    if c["surface_class"] == "PUBLIC_SEARCH_INDEX":
        if c["trigger_class"] == "CO_PREFIX_FAMILY":
            return "OBSERVE_CANDIDATE_ONLY"
        if c["trigger_class"] == "SYSTEM_MENTION":
            return "OBSERVE_CONTEXT_REQUIRED"
        return "OBSERVE_ONLY"

    if c["relationship"] in {"MUTED", "REVOKED"} or c["stop_signal"]:
        return "BLOCK"

    if c["trigger_class"] == "REFERRAL" and not c["explicit_invocation"]:
        return "DRAFT_ONLY_REFERRAL_NE_REPLY_CONSENT"

    if not c["explicit_invocation"]:
        return "DRAFT_ONLY_NO_CONVERSATIONAL_INVITATION"

    if not c["surface_write_authority"]:
        return "DRAFT_ONLY_NO_SURFACE_WRITE_AUTHORITY"

    if not c["disclosure_ready"]:
        return "DRAFT_ONLY_DISCLOSURE_NOT_READY"

    if not c["seat_materialized"]:
        return "DRAFT_ONLY_NO_MATERIALIZED_SEAT"

    if not c["effect_lease"]:
        return "DRAFT_ONLY_NO_EFFECT_LEASE"

    if not c["rate_available"]:
        return "HOLD_RATE_LIMIT"

    if not c["confidentiality_compatible"]:
        return "HOLD_CONFIDENTIALITY_MISMATCH"

    return "RESPOND_IF_EXPLICITLY_INVOKED"

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    checks = [
        ("cocivia_identity_path", "cocivia_identity_blob_sha"),
        ("cocivia_github_policy_path", "cocivia_github_policy_blob_sha"),
        ("cocivia_service_principal_path", "cocivia_service_principal_blob_sha"),
        ("cocivia_github_app_fixture_path", "cocivia_github_app_fixture_blob_sha"),
    ]
    for path_key, sha_key in checks:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    auth = d["current_authority"]
    if auth["seat_state"] != "NONE":
        fail("FAIL_CURRENT_SEAT_STATE")
    if auth["public_outreach_allowed"] is not False:
        fail("FAIL_CURRENT_OUTREACH_AUTHORITY")
    if auth["real_external_monitoring_activated"] is not False:
        fail("FAIL_CURRENT_MONITORING_STATE")

    cases = d.get("cases", [])
    if len(cases) != 10:
        fail("FAIL_CASE_COUNT")

    observed = []
    eligible = 0
    for c in cases:
        got = route(c)
        if got != c["expected"]:
            fail(f"FAIL:{c['id']}:got={got}:expected={c['expected']}")
        eligible += int(got == "RESPOND_IF_EXPLICITLY_INVOKED")
        observed.append({"id": c["id"], "decision": got})

    if eligible != 1:
        fail("FAIL_SYNTHETIC_REPLY_ELIGIBLE_COUNT")

    rails = set(d.get("rails", []))
    required = {
        "TRIGGER_WORD_NE_INVITATION",
        "MENTION_NE_CONSENT",
        "REFERRAL_NE_REPLY_CONSENT",
        "READABLE_NE_WRITABLE",
        "DRAFT_NE_SENT",
        "AUTOMATION_NE_CONSENT",
        "IDENTITY_NE_SEAT",
        "SEAT_NE_REPLY_AUTHORITY",
        "STOP_SIGNAL_GT_ENGAGEMENT_GOAL",
        "DESIGN_NE_MONITORING_ACTIVE"
    }
    if not required.issubset(rails):
        fail("FAIL_REQUIRED_RAILS")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COCIVIA_AMBIENT_CORRESPONDENCE_R0A",
        "checked_out_head_sha": head,
        "case_count": len(cases),
        "synthetic_reply_eligible_count": eligible,
        "current_real_external_reply_authority": False,
        "current_real_monitoring_activated": False,
        "fixture_semantic_sha256": canonical_sha(d),
        "observed": observed
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
