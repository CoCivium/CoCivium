#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cocivia/cocivia_public_onboarding_placeholder_r0.json")

def fail(code):
    raise SystemExit(code)

def blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",",":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    s=d["source_bindings"]
    checks=[
        ("ambient_correspondence_doc_path","ambient_correspondence_doc_blob_sha"),
        ("optin_resource_doc_path","optin_resource_doc_blob_sha"),
        ("ambient_correspondence_fixture_path","ambient_correspondence_fixture_blob_sha")
    ]
    for pkey,skey in checks:
        if blob(s[pkey]) != s[skey]:
            fail("FAIL_SOURCE_BIND:"+s[pkey])

    fd=d["front_door"]
    if fd["public_observe_without_account"] is not True:
        fail("FAIL_OBSERVE_WITHOUT_ACCOUNT")
    if fd["participation_requires_resource_contribution"] is not False:
        fail("FAIL_FORCED_RESOURCE_CONTRIBUTION")
    if fd["chatgpt_account_required"] is not False or fd["provider_account_required"] is not False:
        fail("FAIL_PROVIDER_DEPENDENCY")
    if fd["device_ownership_required"] is not False:
        fail("FAIL_DEVICE_OWNERSHIP_REQUIREMENT")

    defaults=d["recommended_defaults"]
    if defaults["preview_required"] is not True or defaults["explicit_accept_required"] is not True:
        fail("FAIL_DEFAULT_CONSENT_SHAPE")
    if defaults["individually_inspectable"] is not True or defaults["individually_revocable"] is not True:
        fail("FAIL_DEFAULT_GRANT_TRANSPARENCY")
    forbidden={"BACKGROUND_COMPUTE","PRIVATE_MESSAGES","CONTACTS","MICROPHONE","CAMERA","LOCATION","CREDENTIALS","FINANCIAL_EFFECTS","AUTONOMOUS_EXTERNAL_POSTING"}
    if not forbidden.issubset(set(defaults["excluded"])):
        fail("FAIL_SENSITIVE_DEFAULT_EXCLUSIONS")

    em=d["emergency_mode"]
    if em["default"] != "SIMULATION_ONLY":
        fail("FAIL_EMERGENCY_DEFAULT")
    if len(em["real_incident_effect_requires"]) < 5:
        fail("FAIL_REAL_INCIDENT_GATE_SET")

    ex=d["exit"]
    if ex["future_grants_revocable"] is not True:
        fail("FAIL_REVOCATION")
    if ex["account_delete_claimed"] is not False or ex["provider_data_delete_claimed"] is not False:
        fail("FAIL_UNPROVEN_DELETE_CLAIM")
    if ex["historical_receipts_erased_by_revocation"] is not False:
        fail("FAIL_HISTORY_ERASURE")

    brand=d["brand_relations"]
    if brand["family_mark_may_be_shared"] is not True or brand["front_roles_must_remain_distinguishable"] is not True:
        fail("FAIL_BRAND_RELATION")

    expected={
      "O01_OBSERVE_WITHOUT_ACCOUNT":"PUBLIC_OBSERVE_ONLY",
      "O02_JOIN_WITHOUT_RESOURCE_CONTRIBUTION":"PARTICIPANT_CANDIDATE_NO_RESOURCE_GRANT",
      "O03_DEFAULTS_VISIBLE_NOT_ACCEPTED":"NO_DEFAULT_GRANTS_CREATED",
      "O04_LOW_RISK_DEFAULTS_ACCEPTED":"LOW_RISK_GRANTS_ACTIVE_CANDIDATE",
      "O05_SENSITIVE_DEFAULT_REMAINS_OFF":"REJECT_NOT_IN_RECOMMENDED_DEFAULTS",
      "O06_EXPLICIT_COMPUTE_GRANT_NOT_EXECUTION":"RESOURCE_CANDIDATE_ONLY_NO_EXECUTION",
      "O07_EMERGENCY_PRACTICE_DEFAULT":"SIMULATION_ONLY",
      "O08_REAL_EMERGENCY_WITHOUT_AUTHORITY":"HOLD_NO_REAL_INCIDENT_AUTHORITY",
      "O09_INVITE_COCIVIA_WITHOUT_SEAT":"DRAFT_ONLY_NO_COCIVIA_SEAT",
      "O10_EXIT_REVOKES_FUTURE_GRANTS":"EXPORT_OPTION_PLUS_REVOKE_FUTURE_GRANTS",
      "O11_OFFLINE_HUMAN_PARTICIPATION":"PARTICIPATION_ALLOWED_WITHOUT_DEVICE_GRANT",
      "O12_RESOURCE_SIZE_NO_GOVERNANCE_WEIGHT":"NO_GOVERNANCE_POWER_FROM_RESOURCE_SIZE"
    }
    cases={c["id"]:c for c in d["scenarios"]}
    if set(cases)!=set(expected):
        fail("FAIL_SCENARIO_SET")
    for cid,val in expected.items():
        if cases[cid]["expected"] != val:
            fail("FAIL_SCENARIO_EXPECTATION:"+cid)

    if cases["O03_DEFAULTS_VISIBLE_NOT_ACCEPTED"]["resource_grants"] != []:
        fail("FAIL_VISIBLE_DEFAULT_CREATED_GRANT")
    if cases["O05_SENSITIVE_DEFAULT_REMAINS_OFF"]["resource_grants"] != ["BACKGROUND_COMPUTE"]:
        fail("FAIL_SENSITIVE_CASE")
    if cases["O12_RESOURCE_SIZE_NO_GOVERNANCE_WEIGHT"]["governance_weight_from_contribution"] != 0:
        fail("FAIL_RESOURCE_GOVERNANCE_WEIGHT")

    rails=set(d["rails"])
    required={
      "PLACEHOLDER_NE_DEPLOYED_PUBLIC_SURFACE",
      "DEFAULT_VISIBLE_NE_DEFAULT_GRANTED",
      "PARTICIPATION_NE_RESOURCE_CONTRIBUTION",
      "PARTICIPATION_NE_DEVICE_OWNERSHIP",
      "CHATGPT_ACCOUNT_NE_COCIVIUM_DEPENDENCY",
      "RESOURCE_GRANT_NE_EXECUTION_AUTHORITY",
      "EMERGENCY_GAME_NE_REAL_EMERGENCY_DISPATCH",
      "INVITE_NE_REPLY_SEAT",
      "EXPORT_NE_PROVIDER_DATA_DELETION",
      "RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY",
      "SHARED_BRAND_NE_SHARED_ROLE",
      "VALIDATION_IS_NOT_ACCEPTANCE"
    }
    if not required.issubset(rails):
        fail("FAIL_REQUIRED_RAILS")

    head=subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    print(json.dumps({
      "STATE":"PASS_COCIVIA_PUBLIC_ONBOARDING_PLACEHOLDER_R0",
      "checked_out_head_sha":head,
      "scenario_count":len(cases),
      "public_observe_without_account":True,
      "participation_without_resource_grant":True,
      "participation_without_device_ownership":True,
      "recommended_defaults_require_explicit_accept":True,
      "emergency_default":"SIMULATION_ONLY",
      "real_external_effect_count":0,
      "runtime_authority":False,
      "fixture_semantic_sha256":canonical_sha(d)
    }, separators=(",",":")))

if __name__=="__main__":
    main()
