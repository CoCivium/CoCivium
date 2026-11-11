#!/usr/bin/env python3
"""Source-only CoCarry public bootstrap check, not live browser/session custody.

Does not access browser profiles, tabs, provider accounts, credentials or mail.
Accepts one deliberately synthetic example and an existing public frontier index.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

SCHEMA = "cocivium.cocarry.session-recovery.r0"
FRONT_SCHEMA = "cocivium.frontier-index.r0"
LIFECYCLE = ("discovered", "qualified", "active", "sleeping",
             "blocked", "completed", "retired")
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SAFE_ID = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.:-]{0,127}\Z")
CLAIM = re.compile(r"[A-Z][A-Z0-9_]*\Z")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PUBLIC_URL_HOSTS = {"github.com"}
SENSITIVE_FIELD_NAMES = {
    "session_url", "chat_url", "cookie", "cookies", "access_token",
    "refresh_token", "password", "email_body", "message_body",
    "recipient_email", "private_transcript", "raw_conversation",
    "provider_session_id", "authorization", "api_key",
}
EXPECTED_RECORD_FIELDS = {
    "work_id", "front_ids", "objective", "state", "evidence_refs",
    "source_commit", "last_verified_at", "next_trigger", "lease",
    "blocked_claims", "supersedes", "custody"
}
REQUIRED_RAILS = (
    "Browser tabs are projections, never the durable work store",
    "Close-tab must not delete a durable work record",
    "An inaccessible chat cannot be represented as recovered",
    "Cross-session acknowledgment requires observed receipt, not quoted conversation",
)
REQUIRED_GATES = (
    "Read back the persisted record from an independent process",
    "Reopen work in Firefox or another browser without manual context paste",
    "Simulate browser crash and worker restart, then verify recovery",
)


class Hold(ValueError):
    pass


def require(predicate: bool, reason: str) -> None:
    if not predicate:
        raise Hold(reason)


def scan_privacy(node) -> None:
    """Public fixture must never carry raw chat locators, inbox or credentials."""
    if isinstance(node, dict):
        for key, value in node.items():
            require(isinstance(key, str), "HOLD_NONSTRING_KEY")
            require(key.casefold() not in SENSITIVE_FIELD_NAMES,
                    "HOLD_RAW_PRIVATE_FIELD")
            scan_privacy(value)
    elif isinstance(node, list):
        for item in node:
            scan_privacy(item)
    elif isinstance(node, str):
        require(not EMAIL.search(node), "HOLD_PRIVATE_ADDRESS")
        lower = node.casefold()
        require(not any(token in lower for token in (
            "mail.google.com/mail", "chatgpt.com/c/",
            "chat.openai.com/c/", "bearer ", "ghp_",
            "xoxb-", "sk-proj-", "sessionid=", "access_token="
        )), "HOLD_PRIVATE_LOCATOR_OR_TOKEN")


def public_pointer(url) -> bool:
    if not isinstance(url, str) or len(url) > 1024:
        return False
    parsed = urlsplit(url)
    return (parsed.scheme == "https" and parsed.netloc in PUBLIC_URL_HOSTS
            and parsed.username is None and parsed.password is None
            and not parsed.query and not parsed.fragment
            and parsed.path.startswith("/CoCivium/CoCivium/"))


def validate(contract: dict, frontier: dict) -> dict:
    require(isinstance(contract, dict) and contract.get("schema") == SCHEMA,
            "HOLD_BAD_COCARRY_SCHEMA")
    require(isinstance(frontier, dict)
            and frontier.get("schema") == FRONT_SCHEMA
            and isinstance(frontier.get("fronts"), list),
            "HOLD_BAD_FRONTIER_SOURCE")
    scan_privacy(contract)
    require("public synthetic" in contract.get("scope", "").lower(),
            "HOLD_NOT_PUBLIC_SYNTHETIC")
    require(isinstance(contract.get("goal"), str)
            and contract["goal"].strip(), "HOLD_GOAL")
    r = contract.get("session_record")
    require(isinstance(r, dict) and set(r) == EXPECTED_RECORD_FIELDS,
            "HOLD_RECORD_SHAPE")
    require(isinstance(r["work_id"], str) and bool(SAFE_ID.fullmatch(r["work_id"])),
            "HOLD_WORK_ID")
    require(r["state"] in LIFECYCLE and r["state"] == "sleeping",
            "HOLD_LIVE_OR_FINISHED_STATUS_UNPROVEN")
    require(r["custody"] == "public-synthetic" and r["lease"] is None,
            "HOLD_NO_REAL_AUTHORITY")
    require(isinstance(r["front_ids"], list) and bool(r["front_ids"])
            and len(r["front_ids"]) == len(set(r["front_ids"]))
            and all(isinstance(x, str) for x in r["front_ids"]),
            "HOLD_FRONT_REFS")
    declared = {x.get("id") for x in frontier["fronts"] if isinstance(x, dict)}
    require(set(r["front_ids"]).issubset(declared), "HOLD_UNRESOLVED_FRONT_REF")
    require(isinstance(r["objective"], str) and r["objective"].strip(),
            "HOLD_MISSING_OBJECTIVE")
    require(isinstance(r["evidence_refs"], list) and r["evidence_refs"]
            and all(public_pointer(x) for x in r["evidence_refs"]),
            "HOLD_NONPUBLIC_EVIDENCE_REF")
    require(r["source_commit"] is None and r["last_verified_at"] is None,
            "HOLD_SOURCE_VERIFICATION_NOT_PERFORMED")
    trigger = r["next_trigger"]
    require(isinstance(trigger, dict)
            and trigger.get("kind") == "new_verified_evidence"
            and trigger.get("ref") == r["work_id"],
            "HOLD_NO_RECOVERY_WAKE")
    require(isinstance(r["blocked_claims"], list)
            and {"LIVE_SESSION_RECOVERY", "X2_DEPLOYMENT"}.issubset(r["blocked_claims"])
            and len(r["blocked_claims"]) == len(set(r["blocked_claims"]))
            and all(isinstance(x, str) and CLAIM.fullmatch(x)
                    for x in r["blocked_claims"]),
            "HOLD_BLOCKERS_UNPRESERVED")
    require(r["supersedes"] == [], "HOLD_SUPERSESSION_UNPROVEN")
    require(contract.get("lifecycle") == list(LIFECYCLE),
            "HOLD_LIFECYCLE_DRIFT")
    require(isinstance(contract.get("invariants"), list)
            and all(rule in contract["invariants"] for rule in REQUIRED_RAILS),
            "HOLD_CONTINUITY_RAIL_MISSING")
    require(isinstance(contract.get("migration_gates"), list)
            and all(gate in contract["migration_gates"] for gate in REQUIRED_GATES),
            "HOLD_REOPEN_PROOF_GATES_MISSING")
    browser = contract.get("browser_policy")
    require(isinstance(browser, dict)
            and set(browser) == {"firefox", "edge", "future_cobrowser"}
            and all(isinstance(x, str) and x for x in browser.values()),
            "HOLD_BROWSER_POLICY_DRIFT")
    return {
        "schema": "CoCarry.PublicBootstrapValidation.R0",
        "state": "PASS_PUBLIC_SYNTHETIC_SOURCE_CONTRACT_ONLY",
        "work_id": r["work_id"],
        "bound_front_count": len(r["front_ids"]),
        "tab_closure_authorized": False,
        "firefox_reopen_verified": False,
        "live_session_inventory": "NOT_OBSERVED",
        "x2_receiver_readproof": "NOT_OBSERVED",
        "public_pointer_ne_receiver_ack": True,
        "discovered_set_is_not_complete_history": True,
        "nonclaims": [
            "PUBLIC_CONTRACT_NE_PRIVATE_SESSION_CUSTODY",
            "TAB_CLOSURE_NE_WORK_RETIREMENT",
            "SOURCE_POINTER_NE_RECEIVER_PICKUP",
            "FIREFOX_SURFACE_NE_INSTALLED_COBROWSER",
            "SYNTHETIC_RECORD_NE_REAL_SESSION_RECOVERY",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default=
                        "docs/Evolution/COCARRY_BROWSER_INDEPENDENT_RECOVERY_R0.json")
    parser.add_argument("--frontier", default=
                        "docs/Evolution/FRONTIER_EVIDENCE_INDEX_R0.json")
    args = parser.parse_args()
    source = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    frontier = json.loads(Path(args.frontier).read_text(encoding="utf-8"))
    print(json.dumps(validate(source, frontier), sort_keys=True))


if __name__ == "__main__":
    main()
