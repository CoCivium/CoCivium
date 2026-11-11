#!/usr/bin/env python3
"""CoCarry/CoBrowser R0: private session-ledger -> single foreground *proposal*.

Consumes a CoSessionShadowLedger output only. Does not read, open, close,
re-title, sync, log into or mutate any browser/provider session. Source-only
fixture: no X2 adoption, no automatic pickup, and no claim that all sessions
were enumerated. Output retains only row IDs plus aggregate state, never URLs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

SCHEMA = "CoSessionShadowLedger.R1.v0.1-candidate"
MAX_SESSIONS = 10000


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def evaluate(ledger, focus_id):
    if not isinstance(ledger, dict) or ledger.get("schema") != SCHEMA:
        raise ValueError("HOLD_WRONG_LEDGER_SCHEMA")
    rows = ledger.get("sessions")
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_SESSIONS:
        raise ValueError("HOLD_BOUNDED_INVENTORY_REQUIRED")
    if not isinstance(focus_id, str) or not focus_id.strip():
        raise ValueError("HOLD_FOCUS_ID_REQUIRED")
    seen, focus = set(), None
    states = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("HOLD_INVALID_LEDGER_ROW")
        identity = row.get("session_id")
        if not isinstance(identity, str) or not identity.strip() or identity in seen:
            raise ValueError("HOLD_DUPLICATE_OR_EMPTY_SESSION_ID")
        seen.add(identity)
        state = row.get("projection")
        if not isinstance(state, str) or not state:
            raise ValueError("HOLD_UNKNOWN_LIFECYCLE_PROJECTION")
        states[state] = states.get(state, 0) + 1
        if identity == focus_id:
            focus = row
    if focus is None:
        raise ValueError("HOLD_FOCUS_NOT_IN_SOURCE")
    # A provider's close-safe label is not independent recovery evidence.
    # Never automatically retire an off-screen tab from a source-only ledger.
    digest = hashlib.sha256(canonical(ledger).encode("ascii")).hexdigest()
    return {
        "schema": "CoCarry.BrowserFrontProjection.R0",
        "state": "PRIVATE_SOURCE_PROJECTION_NOT_BROWSER_RUNTIME",
        "source_sha256": digest,
        "source_schema": SCHEMA,
        "coverage": {
            "observed_session_rows": len(rows),
            "unique_session_ids": len(seen),
            "global_session_census": "UNPROVEN",
            "offscreen_session_rows_still_indexed": len(rows) - 1,
            "lifecycle_projection_counts": dict(sorted(states.items())),
        },
        "focus": {
            "session_id": focus_id,
            "desired_renderer": "FIREFOX_MANAGED",
            "status": "PROPOSED_NOT_REOPENED_OR_PICKED_UP",
            "work_identity": "UNBOUND_UNLESS_SEPARATELY_EVIDENCED",
            "unsent_input_custody": "UNKNOWN_NOT_CAPTURED",
            "checkpoint_readproof": "NOT_OBSERVED",
        },
        "edge_fallback": "PRESERVE_EXISTING_PROFILE_AND_TABS_UNTIL_RECOVERY_PROVED",
        "effects": {
            "tabs_opened": 0,
            "tabs_closed": 0,
            "provider_sessions_deleted": 0,
            "profile_changes": 0,
            "network_calls": 0,
            "messages_sent": 0,
            "public_uploads": 0,
        },
        "next_safe_action": "VERIFY_PRIVATE_SOURCE_INVENTORY_AND_ONE_REAL_FIREFOX_REOPEN",
        "nonclaims": [
            "LEDGER_NE_COMPLETE_SESSION_INVENTORY",
            "OFFSCREEN_NE_DORMANT_OR_CLOSED",
            "BROWSER_TAB_NE_WORK_IDENTITY",
            "CLOSE_SAFE_LABEL_NE_CUSTODY_OR_RECEIVER_ACK",
            "PUBLIC_BOOTSTRAP_NE_PRIVATE_SESSION_PUBLICATION",
            "FIREFOX_PROPOSAL_NE_X2_RUNTIME_ADOPTION",
        ],
    }


def write_private(path, report):
    """No clobber; caller must choose a private filesystem destination."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(str(target), flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--focus-id", required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    report = evaluate(ledger, args.focus_id)
    write_private(args.private_output, report)
    # No IDs or source references in stdout.
    print(json.dumps({"state": report["state"],
                      "observed_session_rows": report["coverage"]["observed_session_rows"],
                      "provider_mutations": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
