"""CoModelFabric provider exit readiness R0. Standard library, pure decision.

No model calls, network access, credential actions, scheduling, data export,
service cancellation, provider account access, or X2 mutation. This evaluates
supplied evidence only: a paper PASS is NOT a witnessed local runtime.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA = "CoAll.CoModelFabric.ProviderExitEvidence.R0"
RESULT_SCHEMA = "CoAll.CoModelFabric.ProviderExitDecision.R0"
ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,96}$")
HASH_RE = re.compile(r"^[a-fA-F0-9]{64}$")
PROVIDER_STATES = {"AVAILABLE", "LIMITED", "OUTAGE", "UNKNOWN"}
PROVIDER_EVIDENCE = {"USER_REPORTED", "ACCOUNT_UI_OBSERVED", "OFFICIAL_POLICY", "UNKNOWN"}
CONFIDENTIALITY = {"PUBLIC", "PRIVATE", "RESTRICTED", "UNKNOWN"}
EXPORT_STATES = {"NOT_REQUESTED", "REQUESTED", "RECEIVED", "NOT_SUPPORTED", "UNKNOWN"}
NONCLAIMS = [
    "SIMULATED_EVIDENCE_NE_X2_RUNTIME",
    "SOURCE_CODE_NE_LOCAL_MODEL_CANARY",
    "SUBSCRIPTION_CANCEL_REQUIRES_DISTINCT_EXPLICIT_HUMAN_ACTION",
    "EXPORT_REQUEST_NE_EXPORT_VERIFIED",
    "HOSTED_OUTAGE_NE_AUTHORITY_TO_TRANSFER_PRIVATE_DATA",
    "SAME_HOST_CHECKPOINT_NE_INDEPENDENT_RECEIVER",
    "PUBLIC_SOURCE_NE_COALL_CANON",
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
]


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    return result.astimezone(timezone.utc) if result.tzinfo is not None else None


def _bool(mapping: Mapping[str, Any], name: str) -> bool:
    if name not in mapping or type(mapping[name]) is not bool:
        raise ValueError("HOLD_NONBOOLEAN_OR_MISSING_" + name.upper())
    return mapping[name]


def _fail(reason: str) -> dict[str, Any]:
    return {
        "schema": RESULT_SCHEMA,
        "state": "HOLD_INVALID_OR_STALE_EVIDENCE",
        "reason": reason,
        "primary_route_eligible": False,
        "shadow_route_eligible": False,
        "subscription_retirement_authorized": False,
        "automatic_external_transfer_allowed": False,
        "recovery_claimed": False,
        "gates": {},
        "next_safe_deed": "REFRESH_SOURCE_BOUND_EVIDENCE_WITHOUT_BILLING_OR_RUNTIME_ACTION",
        "nonclaims": NONCLAIMS,
    }


def assess(evidence: Mapping[str, Any], *, at_utc: datetime) -> dict[str, Any]:
    """Evaluate bounded, independently supplied evidence; never perform effects."""
    if not isinstance(evidence, Mapping):
        return _fail("MISSING_CONTRACT")
    if evidence.get("schema") != SCHEMA:
        return _fail("UNSUPPORTED_SCHEMA")
    if not isinstance(at_utc, datetime) or at_utc.tzinfo is None:
        return _fail("REVIEW_TIME_MISSING_TIMEZONE")
    measured = _utc(evidence.get("observed_at_utc"))
    if measured is None:
        return _fail("EVIDENCE_TIME_MISSING_OR_NAIVE")
    age = (at_utc.astimezone(timezone.utc) - measured).total_seconds()
    if age < -5 or age > 600:
        return _fail("EVIDENCE_EXPIRED_OR_FROM_FUTURE")
    work_id = evidence.get("work_id")
    if not isinstance(work_id, str) or not ID_RE.fullmatch(work_id):
        return _fail("WORK_ID_NOT_QUALIFIED")
    try:
        provider = evidence["provider"]
        local = evidence["local"]
        custody = evidence["custody"]
        ui = evidence["surface"]
        export = evidence["export"]
        if not all(isinstance(x, Mapping) for x in (provider, local, custody, ui, export)):
            return _fail("MALFORMED_SECTION")
        if provider.get("availability") not in PROVIDER_STATES:
            return _fail("UNKNOWN_PROVIDER_STATE")
        if provider.get("limit_evidence") not in PROVIDER_EVIDENCE:
            return _fail("UNKNOWN_USAGE_LIMIT_EVIDENCE_CLASS")
        if evidence.get("confidentiality") not in CONFIDENTIALITY:
            return _fail("UNKNOWN_CONFIDENTIALITY")
        if export.get("state") not in EXPORT_STATES:
            return _fail("UNKNOWN_EXPORT_STATE")
        if export.get("account_class") not in ("PERSONAL", "MANAGED", "UNKNOWN"):
            return _fail("UNKNOWN_ACCOUNT_CLASS")
        fields = {
            "local_model_version_pinned": _bool(local, "model_version_pinned"),
            "local_license_checked": _bool(local, "license_checked"),
            "local_canary_executed": _bool(local, "canary_executed"),
            "local_task_quality_verified": _bool(local, "task_quality_verified"),
            "local_privacy_boundary_verified": _bool(local, "privacy_boundary_verified"),
            "checkpoint_readback": _bool(custody, "work_checkpoint_readback"),
            "same_workid_restart": _bool(custody, "same_workid_restart_verified"),
            "independent_receiver_readproof": _bool(custody, "independent_receiver_readproof"),
            "no_focus_theft": _bool(ui, "no_focus_theft_verified"),
            "native_fallback_usable": _bool(ui, "native_fallback_usable"),
            "private_archive_verified": _bool(export, "archive_received_and_hash_verified"),
            "archive_coverage_reviewed": _bool(export, "coverage_reviewed"),
            "export_permission_checked": _bool(export, "permissions_checked"),
        }
        local_time = _utc(local.get("canary_observed_at_utc"))
        if local_time is None:
            fields["fresh_local_canary"] = False
        else:
            freshness = (at_utc.astimezone(timezone.utc) - local_time).total_seconds()
            fields["fresh_local_canary"] = 0 <= freshness <= 600
        endpoint = local.get("endpoint")
        if endpoint not in ("127.0.0.1", "::1", "localhost"):
            fields["loopback_only"] = False
        else:
            fields["loopback_only"] = True
        checkpoint_sha = custody.get("checkpoint_sha256")
        fields["checkpoint_sha256_present"] = (
            isinstance(checkpoint_sha, str) and bool(HASH_RE.fullmatch(checkpoint_sha))
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _fail("INVALID_FIELD_" + type(exc).__name__)

    local_gate = all(fields[k] for k in (
        "local_model_version_pinned", "local_license_checked",
        "local_canary_executed", "local_task_quality_verified",
        "fresh_local_canary", "loopback_only",
    ))
    if evidence["confidentiality"] != "PUBLIC":
        local_gate = local_gate and fields["local_privacy_boundary_verified"]
    continuity_gate = all(fields[k] for k in (
        "checkpoint_readback", "checkpoint_sha256_present",
        "same_workid_restart", "independent_receiver_readproof",
    ))
    surface_gate = fields["no_focus_theft"] and fields["native_fallback_usable"]
    shadow = local_gate and fields["checkpoint_readback"] and fields["checkpoint_sha256_present"]
    primary = shadow and continuity_gate and surface_gate
    export_gate = (
        export.get("state") == "RECEIVED"
        and fields["private_archive_verified"] and fields["archive_coverage_reviewed"]
        and fields["export_permission_checked"]
    )
    # "Readiness for a human discussion" is not permission to cancel.
    review = primary and export_gate
    if not shadow:
        state = "HOLD_LOCAL_OR_CHECKPOINT_UNQUALIFIED"
        next_safe_deed = "RUN_ONE_AUTHORIZED_LOCAL_LOOPBACK_TASK_AND_CHECKPOINT_READBACK"
    elif not primary:
        state = "SHADOW_ONLY_PRIMARY_UNQUALIFIED"
        next_safe_deed = "VERIFY_RESTART_RECEIVER_READPROOF_AND_FOCUS_SAFE_NATIVE_FALLBACK"
    elif not review:
        state = "LOCAL_PRIMARY_PILOT_ELIGIBLE_EXPORT_HELD"
        next_safe_deed = "REVIEW_PRIVATE_DATA_EXPORT_AND_WORKSPACE_PERMISSIONS"
    else:
        state = "HUMAN_RETIREMENT_REVIEW_READY_NO_ACTION_AUTHORIZED"
        next_safe_deed = "HUMAN_CONFIRM_EXACT_SUBSCRIPTION_ACCOUNT_AND_BILLING_EFFECT_SEPARATELY"

    return {
        "schema": RESULT_SCHEMA,
        "state": state,
        "reason": "NO_EFFECT_EXECUTED",
        "provider_availability_class": provider["availability"],
        "provider_limit_evidence_class": provider["limit_evidence"],
        "confidentiality_class": evidence["confidentiality"],
        "primary_route_eligible": primary,
        "shadow_route_eligible": shadow,
        "subscription_retirement_review_ready": review,
        "subscription_retirement_authorized": False,
        "automatic_external_transfer_allowed": False,
        "recovery_claimed": False,
        "gates": {
            "local_canary": local_gate,
            "continuity_and_receiver": continuity_gate,
            "focus_and_fallback": surface_gate,
            "private_archive": export_gate,
            "evidence_current": True,
        },
        "next_safe_deed": next_safe_deed,
        "nonclaims": NONCLAIMS,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_file", help="local JSON evidence only; never put account exports in public repos")
    args = parser.parse_args(argv)
    try:
        with open(args.evidence_file, "r", encoding="utf-8") as handle:
            evidence = json.load(handle)
        result = assess(evidence, at_utc=datetime.now(timezone.utc))
    except (OSError, json.JSONDecodeError, UnicodeError):
        result = _fail("CANNOT_READ_EVIDENCE")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("primary_route_eligible") else 2


if __name__ == "__main__":
    sys.exit(main())
