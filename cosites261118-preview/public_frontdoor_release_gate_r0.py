"""CoSites public-front-door readiness HOLD gate R0.

Consumes ONLY the existing six-root, redacted, no-shard public observation.
Does not fetch URLs, administer host accounts, deploy, authorize publication,
start a watcher or infer safety from a diagnostic workflow being green.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from host_root_privacy_probe_r0 import MAX_BODY_BYTES, ROOTS, SCHEMA as INPUT_SCHEMA

OUTPUT_SCHEMA = "CoSites.PublicFrontDoor.ReadinessHoldGate.R0"
MAX_REPORT_BYTES = 65536
MAX_AGE = timedelta(minutes=45)
ALLOWED_KEYS = frozenset((site, role, host) for site, role, host in ROOTS)
HEX64 = re.compile(r"^[a-f0-9]{64}$")
HEX40 = re.compile(r"^[a-f0-9]{40}$")


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or len(value) > 48:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo is not None else None


# Only class names, never origin URLs, shard names, paths or response bodies.
# Source-only observations cannot independently validate hosting ownership,
# origin alias inventory, redaction or publisher authority.
LEGACY_ORIGIN_SCHEMA = "CoSites.LegacyOriginContainmentEvidence.R0"
LEGACY_SURFACES = frozenset({
    "CUSTOM_DOMAIN", "PAGES_PRODUCTION", "IMMUTABLE_DEPLOYMENT",
    "PREVIEW_ALIAS", "SHARD_ROUTE", "EDGE_CACHE",
})
LEGACY_STATUSES = frozenset({
    "NO_LEGACY_CONTENT", "LEGACY_METADATA_PUBLIC", "FETCH_UNAVAILABLE",
})


def evaluate_legacy_origin_boundary(evidence: Any, *, now: datetime) -> dict[str, Any]:
    """Fail closed: clean roots, DNS redirects and unreachable origins prove no containment.

    This function has no fetch/host privileges and never promotes submitted
    claims to a real owner attestation or independent receiver readproof.
    """
    reasons = {"HOLD_OWNER_AND_EXTERNAL_RECEIVER_ATTESTATION"}
    seen: set[str] = set()
    if not isinstance(evidence, dict) or evidence.get("schema") != LEGACY_ORIGIN_SCHEMA:
        reasons.add("HOLD_ORIGIN_EVIDENCE_MISSING_OR_INVALID")
    else:
        observed = _utc(evidence.get("observed_utc"))
        if observed is None or not timedelta(0) <= now - observed <= MAX_AGE:
            reasons.add("HOLD_ORIGIN_OBSERVATION_STALE_OR_FUTURE")
        if evidence.get("release_authorized") is not False:
            reasons.add("HOLD_UNTRUSTED_ORIGIN_RELEASE_ASSERTION")
        rows = evidence.get("surfaces")
        if not isinstance(rows, list) or len(rows) != len(LEGACY_SURFACES):
            reasons.add("HOLD_ORIGIN_SURFACE_COUNT")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    reasons.add("HOLD_ORIGIN_SURFACE_MALFORMED")
                    continue
                kind, status = row.get("kind"), row.get("status")
                if not isinstance(kind, str) or kind not in LEGACY_SURFACES or kind in seen:
                    reasons.add("HOLD_ORIGIN_SURFACE_DUPLICATE_OR_UNKNOWN")
                    continue
                seen.add(kind)
                if status == "LEGACY_METADATA_PUBLIC":
                    reasons.add("HOLD_LEGACY_METADATA_STILL_PUBLIC")
                elif status == "FETCH_UNAVAILABLE":
                    reasons.add("HOLD_UNOBSERVABLE_NOT_CONTAINED")
                elif status not in LEGACY_STATUSES:
                    reasons.add("HOLD_ORIGIN_REACHABILITY_UNVERIFIED")
            if seen != LEGACY_SURFACES:
                reasons.add("HOLD_ORIGIN_SURFACE_SET_INCOMPLETE")
    return {
        "state": "HOLD_ORIGIN_AND_ALIAS_CONTAINMENT",
        "reason_codes": sorted(reasons),
        "surface_classes_required": sorted(LEGACY_SURFACES),
        "surface_classes_observed": sorted(seen),
        "publisher_authority": "NOT_AUTHENTICATED",
        "independent_receiver_ack": False,
        "legacy_containment_confirmed": False,
        "public_changes": 0,
    }


def evaluate(source: Any, *, now: datetime, source_commit: str | None = None,
             origin_evidence: Any = None) -> dict[str, Any]:
    """Fail-closed, no-effect, one-authority-root source assessment.

    Never echo raw HTML, paths, filenames, request headers, arbitrary upstream
    flags, URLs, untrusted titles or serialized source records.
    """
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("HOLD_NOW_NOT_AWARE")
    now = now.astimezone(timezone.utc)
    issues: set[str] = set()
    per_root: list[dict[str, str]] = []
    observation = None

    if not isinstance(source, dict) or source.get("schema") != INPUT_SCHEMA:
        issues.add("HOLD_SOURCE_SCHEMA")
    else:
        observation = _utc(source.get("observed_utc"))
        if observation is None or not timedelta(0) <= now - observation <= MAX_AGE:
            issues.add("HOLD_OBSERVATION_STALE_OR_FUTURE")
        scope = source.get("scope")
        expected_hosts = {host for _, _, host in ROOTS}
        if not isinstance(scope, dict) or any(
            scope.get(name) is not True
            for name in ("no_follow_redirect", "no_shard_traversal",
                         "no_raw_body_export", "no_auth_or_config_writes")
        ) or type(scope.get("https_roots_checked")) is not int or scope.get("https_roots_checked") != len(ROOTS) or set(scope.get("approved_hostnames", [])) != expected_hosts:
            issues.add("HOLD_SOURCE_SCOPE_UNQUALIFIED")
        if source.get("release_authorized") is not False or source.get("privacy_cleared") is not False or source.get("human_first_use_accepted") is not False:
            issues.add("HOLD_SPOOFED_SOURCE_AUTHORITY")
        rows = source.get("records")
        if not isinstance(rows, list) or len(rows) != len(ROOTS):
            issues.add("HOLD_INCOMPLETE_ROOT_SET")
        else:
            seen = set()
            for row in rows:
                if not isinstance(row, dict):
                    issues.add("HOLD_MALFORMED_ROOT")
                    continue
                key = (row.get("site"), row.get("variant"), row.get("hostname"))
                if key not in ALLOWED_KEYS or key in seen:
                    issues.add("HOLD_UNEXPECTED_OR_DUPLICATE_ROOT")
                    continue
                seen.add(key)
                codes: list[str] = []
                status = row.get("http_status")
                flags = row.get("privacy_review_flags")
                if status != 200 or type(status) is not int:
                    codes.append("HOLD_ROOT_NOT_HTML200")
                if (row.get("content_type") != "TEXT_HTML" or
                    not isinstance(row.get("html_bytes"), int) or
                    type(row.get("html_bytes")) is bool or
                    not 1 <= row["html_bytes"] <= MAX_BODY_BYTES or
                    not isinstance(row.get("html_sha256"), str) or
                    HEX64.fullmatch(row["html_sha256"]) is None):
                    codes.append("HOLD_ROOT_CONTENT_UNQUALIFIED")
                if not isinstance(flags, list) or flags:
                    codes.append("HOLD_ROOT_PRIVACY_OR_FIRST_USE_FLAGS")
                if row.get("classification") != "HTTP_200_HTML_STRUCTURE_OBSERVED_NOT_ACCEPTED":
                    codes.append("HOLD_ROOT_CLASSIFICATION")
                if row.get("source_first_use_sufficient") is not False or row.get("human_first_use_accepted") is not False:
                    codes.append("HOLD_UNTRUSTED_ACCEPTANCE_CLAIM")
                if codes:
                    issues.update(codes)
                per_root.append({
                    "site": key[0], "variant": key[1],
                    "readiness": "HOLD" if codes else "STRUCTURAL_CANDIDATE_ONLY",
                })
            if seen != ALLOWED_KEYS:
                issues.add("HOLD_ROOT_SET_NOT_EXACT")
    if source_commit is not None and (
        not isinstance(source_commit, str) or HEX40.fullmatch(source_commit) is None
    ):
        issues.add("HOLD_INVALID_SOURCE_COMMIT")

    origin_boundary = evaluate_legacy_origin_boundary(origin_evidence, now=now)
    issues.update(origin_boundary["reason_codes"])
    held = bool(issues)
    # A structural PASS is NOT a deployment or human/privacy acceptance.
    return {
        "schema": OUTPUT_SCHEMA,
        "state": ("HOLD_PUBLIC_FRONTDOOR_READINESS" if held
                  else "STRUCTURAL_SIX_ROOT_CANDIDATE_NOT_RELEASED"),
        "existing_security_owner": "CoCivium/CoToolbelt#5",
        "existing_domain_owner": "CoCivium/CoSteward#60",
        "observed_at_utc": (observation.isoformat().replace("+00:00", "Z")
                            if observation else None),
        "source_commit": source_commit,
        "source_scope": "SIX_HTTPS_ROOTS_ONLY__NO_SHARDS__ONE_CI_ROOT",
        "legacy_origin_boundary": origin_boundary,
        "root_results": sorted(per_root, key=lambda x: (x["site"], x["variant"])),
        "hold_reason_codes": sorted(issues),
        "private_metadata_review_required": True,
        "security_owner_acceptance": "NOT_ATTESTED",
        "domain_ownership_and_rollback": "NOT_ATTESTED",
        "human_visitor_acceptance": "NOT_ATTESTED",
        "release_authorized": False,
        "public_deployment_performed": False,
        "actual_independent_failure_domains": 1,
        "effects": {
            "network_requests": 0, "host_mutations": 0,
            "dns_changes": 0, "source_mutations": 0, "credential_access": 0,
            "runtime_installation": 0
        },
        "nonclaims": [
            "STRUCTURAL_PASS_NE_RELEASE_AUTHORITY",
            "ONE_GITHUB_RUN_NE_THREE_INDEPENDENT_ROOTS",
            "DIAGNOSTIC_CI_GREEN_NE_PRIVACY_PASS",
            "METADATA_EXPOSURE_NE_FILE_CONTENT_OR_CREDENTIAL_DISCLOSURE",
            "NO_SHARD_TRAVERSAL",
            "LOCAL_IS_NOT_LANDED", "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
            "NO_PHANTOM_ACK",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-commit", default=None)
    args = parser.parse_args()
    try:
        raw = Path(args.input).read_bytes()
        if len(raw) > MAX_REPORT_BYTES:
            raise ValueError("OVERSIZE")
        source = json.loads(raw)
        result = evaluate(source, now=datetime.now(timezone.utc),
                          source_commit=args.source_commit)
    except (ValueError, TypeError, OSError, json.JSONDecodeError):
        result = evaluate(None, now=datetime.now(timezone.utc),
                          source_commit=args.source_commit)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "state": result["state"],
        "hold_reason_codes": result["hold_reason_codes"],
        "public_release_authorized": False,
        "actual_deployment": False,
    }, sort_keys=True))
    return 2 if result["state"] == "HOLD_PUBLIC_FRONTDOOR_READINESS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
