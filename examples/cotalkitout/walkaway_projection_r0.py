"""CoTalkItOut R0: proof-bound walk-away status for a calm CoBar front.

Read-only deterministic projection. No filesystem/network/device mutation, model
calls, scheduler, login, implicit peer takeover or authority promotion. The
input is evidence *descriptions*, never a certificate or receiver ACK.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

SCHEMA = "CoAll.CoTalkItOut.WalkAwayEvidence.R0"
OUTPUT_SCHEMA = "CoAll.CoTalkItOut.WalkAwayProjection.R0"
GATES = (
    ("synthetic_replay", "Synthetic independent-runner replay", "CI_SYNTHETIC"),
    ("local_work", "Local model and fenced WorkID result", "X2_LOCAL"),
    ("receiver", "Exact WorkID acquired by independent receiver", "RECEIVER_ORIGIN"),
    ("wake", "Authorized unattended wake after interruption", "LIVE_WAKE"),
    ("cobar", "Native CoBar result, Stop and user acceptance", "LIVE_COBAR"),
    ("absence", "Safe useful work during human absence", "LIVE_ABSENCE"),
)
NEXT = {
    "synthetic_replay": "QUALIFY_EXISTING_SYNTHETIC_REPLAY",
    "local_work": "QUALIFY_EXISTING_LOCAL_WORKID",
    "receiver": "RECEIVER_ORIGIN_EXACT_OBJECT_READBACK_ISSUE_317",
    "wake": "TEST_INCUMBENT_WAKE_WITH_EXPIRED_LEASE",
    "cobar": "TEST_EXISTING_COBAR_INPUT_RESULT_STOP_ISSUE_453",
    "absence": "BOUNDED_PREAUTHORIZED_ABSENCE_DRILL",
}
EVIDENCE_SCOPES = {"UNOBSERVED", "CI_SYNTHETIC", "X2_LOCAL", "RECEIVER_ORIGIN",
                   "LIVE_WAKE", "LIVE_COBAR", "LIVE_ABSENCE"}
# Only a trusted external verifier could promote these observation claims.
# The projection intentionally does not accept user-supplied VERIFIED/ACK flags.
DEFAULT_INPUT = {
    "schema": SCHEMA,
    "work_id": "CoLocalFirstWorkID_20261114_R2",
    "observations": {
        "synthetic_replay": {
            "scope": "CI_SYNTHETIC",
            "source_ref": "https://github.com/CoCivium/CoCivium/actions/runs/43737845694",
            "note": "Synthetic fresh-runner replay; not exact X2 archive"
        },
        "local_work": {
            "scope": "X2_LOCAL",
            "source_ref": "CoLocalFirstWorkID_20261114_R2_X2_STAGED_UNPICKED",
            "note": "Historical X2 loopback canary; not present-tense health"
        },
        "receiver": {"scope": "UNOBSERVED"},
        "wake": {"scope": "UNOBSERVED"},
        "cobar": {"scope": "UNOBSERVED"},
        "absence": {"scope": "UNOBSERVED"}
    }
}

def project(raw: dict) -> dict:
    if not isinstance(raw, dict) or raw.get("schema") != SCHEMA:
        raise ValueError("INVALID_SCHEMA")
    work_id = raw.get("work_id")
    observations = raw.get("observations")
    if not isinstance(work_id, str) or not 1 <= len(work_id) <= 160:
        raise ValueError("INVALID_WORKID")
    if not isinstance(observations, dict) or set(observations) != {g[0] for g in GATES}:
        raise ValueError("MISSING_OR_UNKNOWN_GATES")
    gates = []
    for key, title, expected_scope in GATES:
        o = observations[key]
        if not isinstance(o, dict) or set(o) - {"scope", "source_ref", "note"}:
            raise ValueError("INVALID_OBSERVATION_" + key)
        scope = o.get("scope")
        if scope not in EVIDENCE_SCOPES or scope not in ("UNOBSERVED", expected_scope):
            raise ValueError("SCOPE_CONFLICT_" + key)
        ref = o.get("source_ref")
        if scope != "UNOBSERVED" and (not isinstance(ref, str) or not 1 <= len(ref) <= 512):
            raise ValueError("MISSING_PROVENANCE_" + key)
        if scope == "UNOBSERVED" and ref is not None:
            raise ValueError("REF_WITHOUT_OBSERVATION_" + key)
        note = o.get("note")
        if note is not None and (not isinstance(note, str) or len(note) > 280):
            raise ValueError("INVALID_NOTE_" + key)
        # A supplied observation is not a validated independent receiver receipt.
        state = "REPORTED_SCOPE_ONLY" if scope != "UNOBSERVED" else "UNKNOWN_NOT_OBSERVED"
        gates.append({"gate_id": key, "label": title, "scope": scope,
                      "state": state, "evidence_ref": ref or None,
                      "authority_effect": "NONE"})
    first_missing = next((g for g in gates if g["scope"] == "UNOBSERVED"), None)
    # Synthetic or self-reported evidence is never enough to claim absence readiness.
    if any(g["scope"] == "UNOBSERVED" for g in gates):
        status = "HOLD_NOT_WALKAWAY_READY"
    else:
        status = "HOLD_EXTERNAL_EVIDENCE_AUTHENTICATION_REQUIRED"
    next_id = first_missing["gate_id"] if first_missing else "receiver"
    next_action = NEXT[next_id]
    return {
        "schema": OUTPUT_SCHEMA, "work_id": work_id,
        "state": status,
        "cohere_now": "Existing test observations do not establish unattended, independently recovered operations.",
        "reported_observation_count": sum(g["scope"] != "UNOBSERVED" for g in gates),
        "qualified_live_gate_count": 0,
        "gates": gates, "next_safe_action": next_action,
        "next_owner": "#317" if next_id == "receiver" else "#453" if next_id == "cobar" else "#450",
        "human_relay_required_for_this_projection": False,
        "human_gate": "RETAIN_FOR_IRREVERSIBLE_PRIVACY_FINANCIAL_PUBLIC_AUTHORITY",
        "cobar": {
            "headline": "Recovery qualification in progress",
            "status": "Not yet safe to walk away from operations",
            "detail": "No independent exact-work receiver ACK or unattended wake proof",
            "action_label": "Inspect next proof",
            "action_is_read_only": True,
        },
        "nonclaims": [
            "OBSERVATION_NE_INDEPENDENT_AUTHENTICATION",
            "SYNTHETIC_CI_NE_LIVE_RUNTIME",
            "X2_SMB_STAGE_NE_RECEIVER_ACK",
            "CURRENT_SESSION_NE_PERSISTENT_WORKER",
            "PROJECTION_NE_COBAR_DEPLOYMENT",
            "NO_UNATTENDED_AUTONOMY_CANON_COEX_OR_PUBLIC_RELEASE",
        ],
    }

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, help="Public-safe evidence description JSON; omitted uses built-in historical sample")
    args = p.parse_args()
    try:
        obj = json.loads(args.input.read_text(encoding="utf-8")) if args.input else DEFAULT_INPUT
        result = project(obj)
    except (OSError, ValueError, TypeError) as e:
        print(json.dumps({"schema": OUTPUT_SCHEMA, "state": "HOLD_INVALID_EVIDENCE",
                          "reason": type(e).__name__, "next_safe_action": "REVIEW_SOURCE"}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
