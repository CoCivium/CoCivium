#!/usr/bin/env python3
"""CoPin/CoNeedle R0: review a separate observation without moving the policy pin.

Read-only source candidate for CoLocal/#317. The existing CoLocal role rebind
must first verify the frozen Git blob. A separately versioned JSON observation
may then be checked for chain integrity, identity and authority *claims*.
No observation is accepted into runtime, trusted as a human authorization,
published, or treated as an independently acknowledged receiver effect here.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

from scripts.CoLocalRoleRebindR0 import rebind

SCHEMA = "CoAll.CoNeedle.PendingObservation.R0"
PREFIX = "ai/observations/colocal/"
FIELDS = {
    "schema", "work_id", "incident_owner", "immutable_source_git_blob_sha1",
    "revision", "previous_observation_sha256", "observed_at_utc",
    "observer_claim", "evidence_ref", "observation_kind", "authorization",
    "receiver_ack", "runtime_accepted", "external_effect_verified",
    "privacy_reviewed",
}
KINDS = {"SOURCE_RECHECK", "CURRENTNESS_GAP", "RECEIVER_GAP"}
SOURCE_PIN = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
OBSERVER = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")
EVIDENCE = re.compile(
    r"https://github\.com/CoCivium/CoCivium/issues/181"
    r"(?:#issuecomment-[0-9]+)?\Z"
)


def _fail(code: str) -> None:
    raise ValueError("HOLD_" + code)


def _object_pairs(items):
    output = {}
    for name, value in items:
        if name in output:
            _fail("DUPLICATE_JSON_KEY")
        output[name] = value
    return output


def _read(root: Path, rel: str) -> bytes:
    if (not isinstance(rel, str) or not rel.startswith(PREFIX)
            or not rel.endswith(".json") or "\\" in rel
            or ".." in rel.split("/") or "//" in rel):
        _fail("UNSAFE_OBSERVATION_PATH")
    base = root.resolve()
    cursor = base
    for component in Path(rel).parts:
        cursor = cursor / component
        if cursor.is_symlink():
            _fail("MISSING_OR_LINKED_OBSERVATION")
    path = cursor.resolve()
    if not path.is_relative_to(base) or not path.is_file():
        _fail("MISSING_OR_LINKED_OBSERVATION")
    if not 0 < path.stat().st_size <= 8192:
        _fail("OBSERVATION_SIZE")
    raw = path.read_bytes()
    if not 0 < len(raw) <= 8192:
        _fail("OBSERVATION_SIZE")
    return raw


def _decode(raw: bytes, pin: dict) -> tuple[dict, datetime]:
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_pairs)
    except (UnicodeError, json.JSONDecodeError):
        _fail("BAD_OBSERVATION_JSON")
    if not isinstance(obj, dict) or set(obj) != FIELDS or obj["schema"] != SCHEMA:
        _fail("OBSERVATION_SCHEMA")
    if (obj["work_id"] != pin["work_id"]
            or obj["incident_owner"] != pin["incident_owner"]
            or obj["immutable_source_git_blob_sha1"] != pin["source_git_blob_sha1"]):
        _fail("POLICY_PIN_OR_IDENTITY_DRIFT")
    if (not isinstance(obj["immutable_source_git_blob_sha1"], str)
            or not SOURCE_PIN.fullmatch(obj["immutable_source_git_blob_sha1"])):
        _fail("POLICY_PIN_SHAPE")
    if type(obj["revision"]) is not int or not 1 <= obj["revision"] <= 100000:
        _fail("OBSERVATION_REVISION")
    if (not isinstance(obj["observer_claim"], str)
            or not OBSERVER.fullmatch(obj["observer_claim"])
            or not isinstance(obj["evidence_ref"], str)
            or not EVIDENCE.fullmatch(obj["evidence_ref"])
            or not isinstance(obj["observation_kind"], str)
            or obj["observation_kind"] not in KINDS):
        _fail("UNQUALIFIED_OBSERVER_OR_EVIDENCE")
    if (obj["authorization"] != "READ_ONLY_PROPOSAL"
            or obj["receiver_ack"] is not False
            or obj["runtime_accepted"] is not False
            or obj["external_effect_verified"] is not False
            or obj["privacy_reviewed"] is not False):
        _fail("AUTHORITY_INFLATION")
    prior = obj["previous_observation_sha256"]
    if prior is not None and (
            not isinstance(prior, str) or not DIGEST.fullmatch(prior)):
        _fail("PREDECESSOR_DIGEST_SHAPE")
    stamp = obj["observed_at_utc"]
    if not isinstance(stamp, str) or not re.fullmatch(
            r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z", stamp):
        _fail("OBSERVATION_TIMESTAMP")
    try:
        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        _fail("OBSERVATION_TIMESTAMP")
    if when.utcoffset().total_seconds() != 0:
        _fail("OBSERVATION_TIMESTAMP")
    return obj, when.astimezone(timezone.utc)


def review_observation(root: Path, role: str, candidate_path: str,
                       prior_path: str | None = None,
                       competing_paths: list[str] | None = None) -> dict:
    """Never writes. A syntactically valid chain is still unreviewed evidence."""
    result = {
        "schema": "CoAll.CoNeedle.SourceObservationReview.R0",
        "state": "HOLD_SOURCE_PIN_OR_OBSERVATION",
        "reason": "HOLD_NOT_QUALIFIED",
        "work_id": None,
        "source_pin_verified": False,
        "observation_chain_syntax_verified": False,
        "observation_receiver_ack": False,
        "observation_authority_verified": False,
        "runtime_accepted": False,
        "external_effect_verified": False,
        "operation_performed": False,
        "x2_shell_started": False,
        "needs_owner_semantic_review": True,
        "competing_sources_checked": 0,
        "complete_fork_census_proven": False,
        "branch_elected": False,
        "local_clock_future_sanity_checked": False,
        "trusted_time_attested": False,
    }
    try:
        root = Path(root)
        pin = rebind(root, role)
        if pin["state"] != "SOURCE_BOUND_REBIND_OWNER_REFRESH_REQUIRED":
            _fail("IMMUTABLE_POLICY_PIN_NOT_QUALIFIED")
        result["work_id"] = pin["work_id"]
        result["source_pin_verified"] = True
        current_raw = _read(root, candidate_path)
        current, current_time = _decode(current_raw, pin)
        # This only rejects obviously future-dated candidate claims relative
        # to the review worker's local clock. It is NOT trusted time
        # attestation, observer provenance, or observation admission.
        review_clock = datetime.now(timezone.utc)
        result["local_clock_future_sanity_checked"] = True
        if current_time > review_clock + timedelta(minutes=5):
            _fail("OBSERVATION_FUTURE_VS_UNATTESTED_REVIEW_CLOCK")
        if current["revision"] == 1:
            if prior_path is not None or current["previous_observation_sha256"] is not None:
                _fail("FIRST_REVISION_WITH_PREDECESSOR")
        else:
            if prior_path is None or prior_path == candidate_path:
                _fail("PRIOR_REQUIRED")
            prior_raw = _read(root, prior_path)
            previous, previous_time = _decode(prior_raw, pin)
            if (current["revision"] != previous["revision"] + 1
                    or current["previous_observation_sha256"] !=
                    hashlib.sha256(prior_raw).hexdigest()):
                _fail("PREDECESSOR_DIGEST_OR_REVISION_MISMATCH")
            if current_time <= previous_time:
                _fail("NONMONOTONIC_OBSERVATION_TIME")
        # This is a bounded *caller-supplied* sibling challenge, never a
        # complete history scan. A missing sibling cannot establish uniqueness.
        if competing_paths is not None:
            if (type(competing_paths) is not list or len(competing_paths) > 8
                    or any(not isinstance(x, str) for x in competing_paths)):
                _fail("UNBOUNDED_OR_MALFORMED_SIBLING_SCOPE")
            paths_seen = {candidate_path}
            for sibling_path in competing_paths:
                if sibling_path in paths_seen:
                    _fail("DUPLICATE_COMPARISON_PATH")
                paths_seen.add(sibling_path)
                sibling_raw = _read(root, sibling_path)
                sibling, _ = _decode(sibling_raw, pin)
                result["competing_sources_checked"] += 1
                if (sibling["revision"] == current["revision"]
                        and sibling_raw != current_raw):
                    _fail("SAME_REVISION_FORK_REQUIRES_OWNER")
        result.update({
            "state": "SOURCE_PIN_OK__OBSERVATION_CANDIDATE_REQUIRES_REVIEW",
            "reason": None,
            "immutable_source_git_blob_sha1": pin["source_git_blob_sha1"],
            "observation_sha256": hashlib.sha256(current_raw).hexdigest(),
            "observation_revision": current["revision"],
            "previous_observation_sha256": current["previous_observation_sha256"],
            "observation_chain_syntax_verified": True,
            "observer_claim_authenticated": False,
            "privacy_reviewed": False,
            "receiver_origin_readproof": False,
            "nonclaims": [
                "IMMUTABLE_PIN_NE_MUTABLE_OBSERVATION",
                "CLAIMED_EVIDENCE_REF_NE_AUTHENTICATED_WITNESS",
                "CHAIN_SYNTAX_NE_ACCEPTED_OBSERVATION",
                "LOCAL_WALL_CLOCK_SANITY_NE_TRUSTED_TIME_OR_SOURCE_FRESHNESS",
                "BOUNDED_SIBLING_CHECK_NE_COMPLETE_FORK_CENSUS",
                "MISSING_FORK_WITNESS_NE_UNIQUE_HISTORY",
                "SOURCE_REVIEW_NE_RUNTIME_OR_RECEIVER_ACK",
                "NO_PUBLICATION_OR_TASK_MUTATION",
            ],
        })
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as exc:
        result["reason"] = str(exc)[:128]
    return result
