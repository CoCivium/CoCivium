#!/usr/bin/env python3
"""CoAwards R0: deterministic source/policy gates, not a public award service.

Run: python -B examples/cobeacon_useful_doors_r0/check_awards.py
No network, external effect, personal data processing or issuance.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
AWARDS = ROOT / "ai/beacon/awards-criteria-r0.json"
HTML = ROOT / "examples/cobeacon_useful_doors_r0/index.html"
CATALOG = ROOT / "ai/beacon/experience-catalog-r0.json"
ID_RE = re.compile(r"^[a-z][a-z0-9-]{2,40}$")

def check(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)

def validate(awards: dict, html: str, catalog: dict) -> None:
    check(awards.get("schema") == "CoCivium.CoAwardsRecognitionCriteria.R0", "invalid schema")
    check(awards.get("state") == "PUBLIC_REVIEW_CANDIDATE__NO_AWARDS_ISSUED__NO_NOMINEE_LIST", "incorrect candidate status")
    classes = awards.get("recognition_classes")
    check(isinstance(classes, list) and len(classes) == 12, "expected 12 criteria categories")
    ids = [x.get("id", "") for x in classes]
    check(len(set(ids)) == len(ids), "duplicate categories")
    check(all(ID_RE.fullmatch(i) for i in ids), "invalid category id")
    check(all(all(bool(x.get(k)) for k in ("name", "promise", "evidence", "example")) for x in classes), "incomplete category")
    check(awards.get("sample_awards") == [], "fictional awards would need explicit fixtures and labels")
    check(awards.get("issued_awards") == [], "issuance requires separate authority and real proof")
    policy = awards.get("operational_policy", {})
    check(policy.get("nominations_open") is False, "false nomination availability")
    check(policy.get("public_submission_endpoint") == "NOT_CONFIGURED", "false intake endpoint")
    check(policy.get("public_award_issuance") == "HELD_NO_ACCOUNTABLE_ISSUER_OR_AWARD_REVIEW", "false issuance status")
    check(policy.get("opt_in") == "REQUIRED_FOR_IDENTIFIED_PERSON", "consent missing")
    for field in ("nomination_fees", "purchased_ranks", "auto_award_from_metrics"):
        check(policy.get(field) == "NOT_ALLOWED", "conflicted award policy: " + field)
    check(policy.get("recipient_can_decline") == "YES", "decline unavailable")
    stage_names = [x.get("state") for x in awards.get("stages", [])]
    check(stage_names == ["SUGGESTED", "NOMINATED", "QUALIFIED", "REVIEWED", "CONSENTED", "ISSUED", "REVISED_OR_WITHDRAWN"], "bad state sequence")
    kit = awards.get("projection_kit", {})
    check(kit.get("no_auto_publication") is True, "unapproved publication path")
    check({"issuer", "consent_scope", "source_identity", "evidence_ceiling"} <= set(kit.get("required", [])), "evidence projection incomplete")
    check("AWARD_NE_PROOF_OF_TRUTH" in awards.get("nonclaims", []), "truth inflation")
    check("NO_GOVERNANCE_AUTHORITY" in awards.get("nonclaims", []), "authority inflation")
    check("MASSIVE_EDITORIAL_NE_UNSOLICITED_BROADCAST" in catalog.get("nonclaims", []), "beacon broadcast boundary drift")
    check('id="recognition-title"' in html and "No nominations are open" in html, "missing public nonclaim")
    check("awards-criteria-r0.json" in html and "twelve opt-in recognition categories" in html.lower(), "public projection missing")
    check("has won our award" not in html.lower(), "false issued-award copy")

def self_test(a: dict, h: str, c: dict) -> int:
    validate(a,h,c)
    n = 1
    cases = [
        lambda x: x.update(state="AWARDS_ISSUED"),
        lambda x: x["recognition_classes"][0].update(id=x["recognition_classes"][1]["id"]),
        lambda x: x["recognition_classes"][0].update(evidence=""),
        lambda x: x.update(issued_awards=[{"name":"Unverified"}]),
        lambda x: x["operational_policy"].update(nominations_open=True),
        lambda x: x["operational_policy"].update(public_submission_endpoint="https://fake.example"),
        lambda x: x["operational_policy"].update(nomination_fees="ALLOWED"),
        lambda x: x["operational_policy"].update(opt_in="NOT_REQUIRED"),
        lambda x: x["operational_policy"].update(public_award_issuance="LIVE"),
        lambda x: x["projection_kit"].update(no_auto_publication=False),
        lambda x: x["nonclaims"].remove("NO_GOVERNANCE_AUTHORITY"),
    ]
    for mutate in cases:
        x = copy.deepcopy(a)
        mutate(x)
        try:
            validate(x,h,c)
        except ValueError:
            n += 1
        else:
            raise AssertionError("unsafe mutation passed validation")
    try:
        validate(a,h.replace("No nominations are open", "Nominations are open"),c)
    except ValueError:
        n += 1
    else:
        raise AssertionError("false UI availability passed validation")
    return n

if __name__ == "__main__":
    try:
        a = json.loads(AWARDS.read_text(encoding="utf-8"))
        h = HTML.read_text(encoding="utf-8")
        c = json.loads(CATALOG.read_text(encoding="utf-8"))
        print(json.dumps({"schema":"CoAwards.ValidatorReceipt.R0",
            "status":"PASS","checks":self_test(a,h,c),"award_categories":len(a["recognition_classes"]),
            "actual_awards_issued":0,
            "effects":{"public_awards":0,"messages":0,"paid_prizes":0},
            "nonclaims":["CATEGORY_NE_AWARD","NOMINATION_NE_CONSENT","AWARD_NE_AUTHORITY","TEST_PASS_NE_RECEIVER_ACCEPTANCE"]
        },sort_keys=True))
    except (OSError,ValueError,AssertionError,json.JSONDecodeError) as exc:
        print("CoAwards FAIL_SCOPED: "+str(exc),file=sys.stderr)
        sys.exit(1)
