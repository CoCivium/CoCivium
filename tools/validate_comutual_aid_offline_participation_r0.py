#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/resilience/comutual_aid_offline_participation_r0.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    if git_blob(src["mutual_aid_doc_path"]) != src["mutual_aid_doc_blob_sha"]:
        fail("FAIL_MUTUAL_AID_DOC_BIND")
    if git_blob(src["mutual_aid_fixture_path"]) != src["mutual_aid_fixture_blob_sha"]:
        fail("FAIL_MUTUAL_AID_FIXTURE_BIND")

    relay = d["relay_contract"]
    if relay["central_server_required"] is not False:
        fail("FAIL_CENTRAL_SERVER_REQUIRED")
    if relay["device_required_for_originator"] is not False:
        fail("FAIL_DEVICE_REQUIRED")
    if relay["outbound_effect_authority"] is not False:
        fail("FAIL_EFFECT_AUTHORITY")

    participants = {p["participant_id"]: p for p in d["participants"]}
    cases = {c["id"]: c for c in d["cases"]}

    o1 = cases["O01_DEVICELESS_ORIGINATOR_HUMAN_RELAY"]
    origin1 = participants[o1["message"]["origin_participant_id"]]
    if origin1["has_device"] is not False or origin1["consent_state"] != "ACTIVE":
        fail("FAIL_O1_ORIGIN")
    if o1["expected"] != "DELIVERED_SIMULATION":
        fail("FAIL_O1_EXPECTED")
    if any(m not in relay["allowed_media"] for m in o1["media"]):
        fail("FAIL_O1_MEDIA")

    o2 = cases["O02_NETWORK_DOWN_PRINTED_CARD"]
    origin2 = participants[o2["message"]["origin_participant_id"]]
    if origin2["has_device"] is not False or "PRINTED_CARD" not in o2["media"]:
        fail("FAIL_O2_OFFLINE_ROUTE")
    if o2["expected"] != "DELIVERED_SIMULATION":
        fail("FAIL_O2_EXPECTED")

    o3 = cases["O03_DUPLICATE_RELAYS_DEDUPED"]
    if len(o3["duplicate_routes"]) < 2:
        fail("FAIL_O3_ROUTE_COUNT")
    if o3["expected_unique_deliveries"] != 1:
        fail("FAIL_O3_DEDUPE")
    if relay["dedupe_key"] != "message_id":
        fail("FAIL_DEDUPE_KEY")

    o4 = cases["O04_REFERRAL_DOES_NOT_ENROL"]
    referred = participants[o4["referred_participant_id"]]
    if referred["consent_state"] != "OFFERED_NOT_ACCEPTED":
        fail("FAIL_O4_CONSENT")
    if o4["expected"] != "INVITATION_OFFER_ONLY":
        fail("FAIL_O4_EXPECTED")

    o5 = cases["O05_REVOKED_PARTICIPANT_NOT_ROUTED"]
    revoked = participants[o5["origin_participant_id"]]
    if revoked["consent_state"] != "REVOKED":
        fail("FAIL_O5_NOT_REVOKED")
    if o5["expected"] != "DROP_REVOKED_CONSENT":
        fail("FAIL_O5_EXPECTED")

    o6 = cases["O06_FRIENDSHIP_AFTER_COOPERATION_OPTIONAL"]
    if o6["expected"] != "SOCIAL_RELATION_CANDIDATE_ONLY":
        fail("FAIL_O6_FRIENDSHIP")

    o7 = cases["O07_SIMULATED_DISPATCH_ROLE_NO_REAL_AUTHORITY"]
    if o7["expected"] != "REJECT_REAL_AUTHORITY_ESCALATION":
        fail("FAIL_O7_AUTHORITY")

    o8 = cases["O08_PRIVATE_PAYLOAD_PUBLIC_RELAY_HOLD"]
    if o8["message"]["privacy_class"] != "PRIVATE_SIMULATED":
        fail("FAIL_O8_PRIVACY_CLASS")
    if "COMMUNITY_NOTICEBOARD" not in o8["media"]:
        fail("FAIL_O8_PUBLIC_MEDIUM")
    if o8["expected"] != "HOLD_PRIVACY_MISMATCH":
        fail("FAIL_O8_EXPECTED")

    expected = d["expected"]
    if len(d["cases"]) != expected["case_count"]:
        fail("FAIL_CASE_COUNT")
    if expected["device_less_success_count"] != 2:
        fail("FAIL_DEVICELESS_SUCCESS_COUNT")
    if expected["deduped_delivery_count"] != 1:
        fail("FAIL_DEDUPED_COUNT")
    for zero_key in [
        "auto_enrolment_count",
        "real_emergency_authority_count",
        "friendship_obligation_count",
        "external_effect_count"
    ]:
        if expected[zero_key] != 0:
            fail("FAIL_EXPECTED_ZERO:" + zero_key)

    required_rails = {
        "DEVICE_NE_PARTICIPATION_REQUIREMENT",
        "CENTRAL_SERVER_NE_GAME_CONTINUITY_ROOT",
        "OFFLINE_NE_NONPARTICIPANT",
        "REFERRAL_NE_ENROLMENT",
        "COOPERATION_NE_FRIENDSHIP_OBLIGATION",
        "SIMULATED_ROLE_NE_REAL_CREDENTIAL",
        "DUPLICATE_ROUTE_NE_DUPLICATE_DISPATCH",
        "CONSENT_REVOKED_NE_FUTURE_ROUTING_ALLOWED",
        "SIMULATION_NE_REAL_EMERGENCY",
        "VALIDATION_IS_NOT_ACCEPTANCE"
    }
    if not required_rails.issubset(set(d["rails"])):
        fail("FAIL_REQUIRED_RAILS")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COMUTUAL_AID_OFFLINE_PARTICIPATION_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "case_count": len(d["cases"]),
        "device_less_success_count": 2,
        "deduped_delivery_count": 1,
        "auto_enrolment_count": 0,
        "real_emergency_authority_count": 0,
        "friendship_obligation_count": 0,
        "external_effect_count": 0,
        "current_real_emergency_command": False,
        "current_public_deployment": False
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
