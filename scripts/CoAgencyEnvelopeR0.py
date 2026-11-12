#!/usr/bin/env python3
"""CoAgencyEnvelope R0: static, source-bound, no-amplification validation.

This composes existing participant, node-participation and standing-authorization
objects. It does not grant authority, authenticate consent, elect a live worker,
execute an effect or prove receiver pickup. Explicit authorization is accepted
only through a caller-supplied independent verifier; the CLI supplies none.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable


SCHEMA = "CoAgencyEnvelope.R0"
REPORT_SCHEMA = "CoAgencyEnvelope.R0.Report"
STANDING_PATH = "ai/currentness/standing-authorization-latch-r2-20261025.json"
DEPENDENCY_SHA256 = {
    "schemas/conode-participation-v0.1.schema.json":
        "fa114fabfcc9520e16c10fd61c0bbe31bd3454470a47f2622ca50ee96f77fa1b",
    "schemas/coparticipant-principal-v0.1.schema.json":
        "66a87067374e7cdd922c11576bfb8fe5cb0758f9d781da21d65345fee8524fc9",
    STANDING_PATH:
        "dc5cac2704833b326d190b28784bb1374cece827130acd76674cc45578adef34",
}
EXPECTED_STANDING_CANONICAL_SHA256 = \
    "53b927164e986fdf04f82c1fc1405c91f0138ba32ccbe2427c7af1479895579a"
MAX_ENVELOPES = 64
MAX_DEPTH = 16
MAX_LEASE = timedelta(hours=24)
MAX_INPUT_BYTES = 262_144
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
SHA = re.compile(r"^[0-9a-f]{64}$")

FIELDS = {
    "schema", "envelope_id", "parent_envelope_id", "root_work_id",
    "participant_id", "source_bindings", "mode", "supervision_topology",
    "authorization_basis", "authorization_ref", "authority_ceiling",
    "allowed_actions", "effect_ceiling", "collision_domain", "actuator_id",
    "lease", "break_glass", "receipts", "nonclaims",
}
SOURCE_FIELDS = {
    "participant_canonical_sha256", "participation_canonical_sha256",
    "standing_authorization_canonical_sha256",
}
MODES = {"SHADOW", "PROPOSE", "ATTENDED", "DELEGATED", "WITNESSED", "QUIET", "HELD"}
TOPOLOGIES = {"IN_LOOP", "ON_LOOP", "ON_CALL", "AFTER_LOOP", "ABSENT"}
AUTH_BASES = {"NONE", "STANDING_BOUNDED", "EXPLICIT_CURRENT"}
EFFECTS = {"OBSERVE_ONLY", "LOCAL_REVERSIBLE", "BOUNDED_SHARED_WRITE", "EFFECT_GATED"}
BREAK_GLASS = {"OFF", "FREEZE", "RECOVER"}
PARTICIPANT_CLASSES = {
    "HUMAN_PRINCIPAL", "ORG_PRINCIPAL", "SYNTH_PARTICIPANT", "MODEL_INSTANCE",
    "SERVICE_PRINCIPAL", "COALL_SYSTEM_PARTICIPANT", "DELEGATE", "OBSERVER",
    "RECEIVER", "EXECUTOR", "REPRESENTATIVE", "UNKNOWN_PARTICIPANT_CLASS",
}
PARTICIPANT_REQUIRED = {
    "participant_id", "participant_class", "roles", "authority_ceiling",
    "identity_basis", "effect_scope",
}
PARTICIPANT_ALLOWED = PARTICIPANT_REQUIRED | {
    "principal_id", "represents", "confidentiality_ceiling", "capabilities",
    "preferences", "consent_or_policy_refs", "challengeable", "revocable", "nonclaims",
}
PARTICIPATION_REQUIRED = {
    "schema", "node_id", "lifecycle_state", "participant_scope", "privacy_domain",
    "capabilities", "allowed_transports", "effect_ceiling", "external_provider_policy",
    "public_internet_exposure", "receipt_route", "human_projection",
}
PARTICIPATION_ALLOWED = PARTICIPATION_REQUIRED | {"local_models", "notes"}

# EFFECT_GATED is a lock, not a higher permission. A descendant cannot turn it
# into a write ceiling merely by calling itself narrower.
EFFECT_DESCENDANTS = {
    "OBSERVE_ONLY": {"OBSERVE_ONLY"},
    "LOCAL_REVERSIBLE": {"OBSERVE_ONLY", "LOCAL_REVERSIBLE"},
    "BOUNDED_SHARED_WRITE": {"OBSERVE_ONLY", "LOCAL_REVERSIBLE", "BOUNDED_SHARED_WRITE"},
    "EFFECT_GATED": {"OBSERVE_ONLY", "EFFECT_GATED"},
}
MODE_NEXT = {
    "SHADOW": {"SHADOW", "PROPOSE", "QUIET", "HELD"},
    "PROPOSE": {"PROPOSE", "ATTENDED", "DELEGATED", "WITNESSED", "QUIET", "HELD"},
    "ATTENDED": {"ATTENDED", "DELEGATED", "WITNESSED", "QUIET", "HELD"},
    "DELEGATED": {"DELEGATED", "WITNESSED", "QUIET", "HELD"},
    "WITNESSED": {"WITNESSED", "QUIET", "HELD"},
    "QUIET": {"QUIET"},
    "HELD": {"HELD"},
}
BREAK_GLASS_NEXT = {
    "OFF": {"OFF", "FREEZE", "RECOVER"},
    "FREEZE": {"FREEZE"},
    "RECOVER": {"RECOVER", "FREEZE"},
}
NONCLAIMS = {
    "ENVELOPE_NE_AUTHORITY_GRANT",
    "HUMAN_PRESENCE_NE_CONSENT",
    "VISIBILITY_NE_ACK",
    "DELIVERY_NE_READPROOF",
    "VALIDATION_NE_RUNTIME",
    "BREAK_GLASS_NE_AUTHORITY_AMPLIFICATION",
    "CHILD_NE_INDEPENDENT_AUTHORITY",
}
RECOVERY_ACTIONS = {
    "READ_SEARCH_INSPECT_COMPARE_RECONCILE",
    "DETERMINISTIC_VALIDATION",
    "PREPARE_ROLLBACK_CONTAINMENT_AND_POST_EFFECT_VERIFICATION",
    "REUSE_REPAIR_REDUCE_SUBSTITUTE_BEFORE_NEW_DEPENDENCY",
    "CONTINUE_ORTHOGONAL_SAFE_WORK_WHEN_ONE_EDGE_IS_GATED",
}


class Held(ValueError):
    """Fail-closed validation result."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Held(reason)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def parse_time(value: Any) -> datetime:
    require(isinstance(value, str), "TIME_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Held("INVALID_TIME") from exc
    require(parsed.tzinfo is not None, "TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def string_set(value: Any, reason: str, *, maximum: int = 32) -> set[str]:
    require(isinstance(value, list) and len(value) <= maximum,
            reason)
    require(all(isinstance(item, str) and 0 < len(item) <= 512 for item in value),
            reason)
    require(len(value) == len(set(value)), reason + "_DUPLICATE")
    return set(value)


def participant_map(value: Any) -> dict[str, dict[str, Any]]:
    rows = value if isinstance(value, list) else [value]
    require(0 < len(rows) <= MAX_ENVELOPES and all(isinstance(row, dict) for row in rows),
            "PARTICIPANT_MANIFESTS_REQUIRED")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        require(PARTICIPANT_REQUIRED <= set(row) <= PARTICIPANT_ALLOWED,
                "PARTICIPANT_FIELDS_INVALID")
        pid = row.get("participant_id")
        require(isinstance(pid, str) and pid and pid not in out,
                "PARTICIPANT_ID_INVALID_OR_DUPLICATE")
        require(isinstance(row.get("authority_ceiling"), str) and row["authority_ceiling"],
                "PARTICIPANT_AUTHORITY_CEILING_REQUIRED")
        require(row.get("participant_class") in PARTICIPANT_CLASSES,
                "PARTICIPANT_CLASS_INVALID")
        string_set(row.get("roles"), "PARTICIPANT_ROLES_INVALID")
        string_set(row.get("identity_basis"), "PARTICIPANT_IDENTITY_BASIS_INVALID")
        string_set(row.get("effect_scope"), "PARTICIPANT_EFFECT_SCOPE_INVALID")
        for key in ("capabilities", "preferences", "consent_or_policy_refs", "nonclaims"):
            if key in row:
                string_set(row[key], "PARTICIPANT_" + key.upper() + "_INVALID")
        for key in ("principal_id", "represents", "confidentiality_ceiling"):
            if key in row:
                require(row[key] is None or isinstance(row[key], str),
                        "PARTICIPANT_" + key.upper() + "_INVALID")
        for key in ("challengeable", "revocable"):
            if key in row:
                require(isinstance(row[key], bool),
                        "PARTICIPANT_" + key.upper() + "_INVALID")
        out[pid] = row
    return out


def validate_sources(participation: Any, standing: Any) -> None:
    require(isinstance(participation, dict) and
            PARTICIPATION_REQUIRED <= set(participation) <= PARTICIPATION_ALLOWED and
            participation.get("schema") == "CoNodeParticipation.v0.1",
            "NODE_PARTICIPATION_CONTRACT_REQUIRED")
    require(isinstance(participation.get("node_id"), str) and participation["node_id"] and
            isinstance(participation.get("participant_scope"), str) and
            participation["participant_scope"] and
            isinstance(participation.get("receipt_route"), str) and
            participation["receipt_route"] and
            isinstance(participation.get("human_projection"), str) and
            participation["human_projection"],
            "NODE_PARTICIPATION_IDENTIFIERS_INVALID")
    require(participation.get("lifecycle_state") in {
        "DISCOVERED", "CANDIDATE", "READY_LOCAL", "PARTICIPATING",
        "DEGRADED", "DORMANT", "RETIRED",
    }, "NODE_LIFECYCLE_INVALID")
    require(participation.get("privacy_domain") in {
        "PRIVATE_PARTICIPANT", "PRIVATE_COCIVIUM", "SHARED_BOUNDED", "PUBLIC_SAFE",
    }, "NODE_PRIVACY_DOMAIN_INVALID")
    string_set(participation.get("capabilities"), "NODE_CAPABILITIES_INVALID")
    string_set(participation.get("allowed_transports"), "NODE_TRANSPORTS_INVALID")
    if "local_models" in participation:
        string_set(participation["local_models"], "NODE_LOCAL_MODELS_INVALID")
    if "notes" in participation:
        string_set(participation["notes"], "NODE_NOTES_INVALID")
    require(participation.get("effect_ceiling") in EFFECTS,
            "NODE_EFFECT_CEILING_INVALID")
    provider = participation.get("external_provider_policy")
    require(isinstance(provider, dict) and set(provider) == {
        "provider_is_control_plane", "unrestricted_remote_control",
        "prefer_local_when_sufficient",
    } and provider.get("provider_is_control_plane") is False and
            provider.get("unrestricted_remote_control") is False and
            isinstance(provider.get("prefer_local_when_sufficient"), bool),
            "NODE_EXTERNAL_PROVIDER_POLICY_INVALID")
    require(participation.get("public_internet_exposure") in
            {"NONE_BY_DEFAULT", "BOUNDED_ELECTED"},
            "NODE_PUBLIC_EXPOSURE_INVALID")
    require(isinstance(standing, dict) and
            standing.get("schema") == "CoAll.StandingAuthorizationLatch.v2" and
            standing.get("state") ==
            "PUBLIC_MACHINE_READABLE_STANDING_DELEGATION__NO_AUTHORITY_AMPLIFICATION",
            "STANDING_AUTHORIZATION_CONTRACT_REQUIRED")
    require(digest(standing) == EXPECTED_STANDING_CANONICAL_SHA256,
            "STANDING_AUTHORIZATION_CONTENT_MISMATCH")
    defaults = string_set(standing.get("default_authorized_actions"),
                          "STANDING_ACTIONS_INVALID", maximum=64)
    require(bool(defaults), "STANDING_ACTIONS_EMPTY")
    rails = string_set(standing.get("approval_semantics"),
                       "STANDING_SEMANTICS_INVALID", maximum=64)
    require("VIRTUAL_OR_CLONE_COUNT_NE_AUTHORITY_MULTIPLICATION" in rails,
            "STANDING_NO_AMPLIFICATION_RAIL_MISSING")
    string_set(standing.get("gated_effects"), "STANDING_GATED_EFFECTS_INVALID", maximum=64)


def validate_dependencies(root_value: str | Path) -> dict[str, str]:
    root = Path(root_value).resolve(strict=True)
    require(root.is_dir(), "CONTRACT_ROOT_INVALID")
    observed: dict[str, str] = {}
    for relative, expected in DEPENDENCY_SHA256.items():
        path = root / relative
        require(path.is_file() and not path.is_symlink() and
                0 < path.stat().st_size <= MAX_INPUT_BYTES,
                "DEPENDENCY_NOT_BOUNDED_REGULAR_FILE:" + relative)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == expected, "DEPENDENCY_SHA256_MISMATCH:" + relative)
        observed[relative] = actual
    return observed


def validate_envelope_shape(envelope: Any) -> None:
    require(isinstance(envelope, dict) and set(envelope) == FIELDS,
            "ENVELOPE_FIELDS_INVALID")
    require(envelope.get("schema") == SCHEMA, "ENVELOPE_SCHEMA_INVALID")
    for key in ("envelope_id", "root_work_id"):
        require(isinstance(envelope.get(key), str) and ID.fullmatch(envelope[key]) is not None,
                key.upper() + "_INVALID")
    parent = envelope.get("parent_envelope_id")
    require(parent is None or isinstance(parent, str) and ID.fullmatch(parent) is not None,
            "PARENT_ENVELOPE_ID_INVALID")
    require(parent != envelope["envelope_id"], "SELF_PARENT_NOT_ALLOWED")
    require(isinstance(envelope.get("participant_id"), str) and envelope["participant_id"],
            "PARTICIPANT_ID_REQUIRED")
    bindings = envelope.get("source_bindings")
    require(isinstance(bindings, dict) and set(bindings) == SOURCE_FIELDS and
            all(isinstance(v, str) and SHA.fullmatch(v) is not None for v in bindings.values()),
            "SOURCE_BINDINGS_INVALID")
    require(envelope.get("mode") in MODES, "MODE_INVALID")
    require(envelope.get("supervision_topology") in TOPOLOGIES,
            "SUPERVISION_TOPOLOGY_INVALID")
    require(envelope.get("authorization_basis") in AUTH_BASES,
            "AUTHORIZATION_BASIS_INVALID")
    auth_ref = envelope.get("authorization_ref")
    require(auth_ref is None or isinstance(auth_ref, str) and 0 < len(auth_ref) <= 512,
            "AUTHORIZATION_REF_INVALID")
    require(isinstance(envelope.get("authority_ceiling"), str) and
            0 < len(envelope["authority_ceiling"]) <= 256,
            "AUTHORITY_CEILING_INVALID")
    string_set(envelope.get("allowed_actions"), "ALLOWED_ACTIONS_INVALID")
    require(envelope.get("effect_ceiling") in EFFECTS, "EFFECT_CEILING_INVALID")
    require(isinstance(envelope.get("collision_domain"), str) and
            0 < len(envelope["collision_domain"]) <= 256,
            "COLLISION_DOMAIN_INVALID")
    actuator = envelope.get("actuator_id")
    require(actuator is None or isinstance(actuator, str) and ID.fullmatch(actuator) is not None,
            "ACTUATOR_ID_INVALID")
    require(envelope.get("break_glass") in BREAK_GLASS, "BREAK_GLASS_INVALID")
    string_set(envelope.get("receipts"), "RECEIPTS_INVALID")
    nonclaims = string_set(envelope.get("nonclaims"), "NONCLAIMS_INVALID")
    require(NONCLAIMS <= nonclaims, "REQUIRED_NONCLAIMS_MISSING")


def validate_forest(
    envelopes: list[dict[str, Any]],
    participants: Any,
    participation: dict[str, Any],
    standing: dict[str, Any],
    *,
    as_of: str,
    explicit_authorization_verifier: Callable[[str, dict[str, Any]], bool] | None = None,
    contract_root: str | Path = ".",
) -> dict[str, Any]:
    """Validate a bounded envelope forest without executing any represented action."""
    now = parse_time(as_of)
    require(isinstance(envelopes, list) and 0 < len(envelopes) <= MAX_ENVELOPES,
            "BOUNDED_ENVELOPE_SET_REQUIRED")
    dependency_hashes = validate_dependencies(contract_root)
    validate_sources(participation, standing)
    people = participant_map(participants)
    records: dict[str, dict[str, Any]] = {}
    for envelope in envelopes:
        validate_envelope_shape(envelope)
        eid = envelope["envelope_id"]
        require(eid not in records, "DUPLICATE_ENVELOPE_ID")
        records[eid] = envelope

    participation_hash = digest(participation)
    standing_hash = digest(standing)
    standing_ref = "standing:sha256:" + standing_hash
    standing_actions = set(standing["default_authorized_actions"])
    verified_explicit = 0

    for envelope in records.values():
        participant = people.get(envelope["participant_id"])
        require(participant is not None, "PARTICIPANT_NOT_BOUND")
        bindings = envelope["source_bindings"]
        require(bindings["participant_canonical_sha256"] == digest(participant),
                "PARTICIPANT_SOURCE_BINDING_MISMATCH")
        require(bindings["participation_canonical_sha256"] == participation_hash,
                "PARTICIPATION_SOURCE_BINDING_MISMATCH")
        require(bindings["standing_authorization_canonical_sha256"] == standing_hash,
                "STANDING_SOURCE_BINDING_MISMATCH")
        require(envelope["authority_ceiling"] == participant["authority_ceiling"],
                "PARTICIPANT_AUTHORITY_CEILING_MISMATCH")
        actions = set(envelope["allowed_actions"])
        require(actions <= set(participant["effect_scope"]),
                "ACTION_OUTSIDE_PARTICIPANT_SCOPE")
        require(envelope["effect_ceiling"] in
                EFFECT_DESCENDANTS[participation["effect_ceiling"]],
                "EFFECT_EXCEEDS_NODE_CEILING")

        basis = envelope["authorization_basis"]
        auth_ref = envelope["authorization_ref"]
        if basis == "NONE":
            require(auth_ref is None and not actions and
                    envelope["effect_ceiling"] == "OBSERVE_ONLY",
                    "NONE_BASIS_MUST_BE_EFFECTLESS")
        elif basis == "STANDING_BOUNDED":
            require(auth_ref == standing_ref, "STANDING_AUTHORIZATION_REF_MISMATCH")
            require(actions <= standing_actions, "ACTION_OUTSIDE_STANDING_AUTHORIZATION")
            require(envelope["effect_ceiling"] in {"OBSERVE_ONLY", "LOCAL_REVERSIBLE"},
                    "STANDING_AUTHORIZATION_EFFECT_AMPLIFICATION")
        else:
            require(envelope["supervision_topology"] not in {"AFTER_LOOP", "ABSENT"},
                    "EXPLICIT_CURRENT_REQUIRES_CURRENT_HUMAN_TOPOLOGY")
            require(isinstance(auth_ref, str) and auth_ref,
                    "EXPLICIT_AUTHORIZATION_REF_REQUIRED")
            require(callable(explicit_authorization_verifier) and
                    explicit_authorization_verifier(auth_ref, envelope) is True,
                    "EXPLICIT_AUTHORIZATION_UNVERIFIED")
            verified_explicit += 1

        mode = envelope["mode"]
        actuator = envelope["actuator_id"]
        lease = envelope["lease"]
        if actuator is None:
            require(lease is None, "LEASE_WITHOUT_ACTUATOR")
        else:
            require(mode in {"ATTENDED", "DELEGATED"}, "MODE_CANNOT_ACTUATE")
            require(basis != "NONE", "ACTUATOR_WITHOUT_AUTHORIZATION")
            require(envelope["effect_ceiling"] in
                    {"LOCAL_REVERSIBLE", "BOUNDED_SHARED_WRITE"},
                    "ACTUATOR_EFFECT_CEILING_NOT_ACTIONABLE")
            require(isinstance(lease, dict) and set(lease) == {"starts_at", "expires_at"},
                    "ACTUATOR_LEASE_REQUIRED")
            starts = parse_time(lease["starts_at"])
            expires = parse_time(lease["expires_at"])
            require(starts <= now < expires, "ACTUATOR_LEASE_NOT_CURRENT")
            require(timedelta(0) < expires - starts <= MAX_LEASE,
                    "ACTUATOR_LEASE_NOT_BOUNDED")
            if envelope["supervision_topology"] == "ABSENT":
                require(mode == "DELEGATED" and basis == "STANDING_BOUNDED",
                        "ABSENT_ACTUATION_REQUIRES_BOUND_DELEGATION")

        if mode in {"SHADOW", "PROPOSE", "WITNESSED", "QUIET", "HELD"}:
            require(actuator is None, "NONACTUATING_MODE_HAS_ACTUATOR")
        if mode == "QUIET":
            require(not actions, "QUIET_MODE_HAS_ACTIONS")

        glass = envelope["break_glass"]
        if glass == "FREEZE":
            require(actuator is None and envelope["effect_ceiling"] == "OBSERVE_ONLY" and
                    actions <= RECOVERY_ACTIONS,
                    "BREAK_GLASS_FREEZE_MUST_NARROW")
        elif glass == "RECOVER":
            require(envelope["effect_ceiling"] in {"OBSERVE_ONLY", "LOCAL_REVERSIBLE"} and
                    actions <= RECOVERY_ACTIONS,
                    "BREAK_GLASS_RECOVERY_MUST_BE_BOUNDED")

    depths: dict[str, int] = {}

    def depth_of(eid: str, trail: tuple[str, ...] = ()) -> int:
        require(eid not in trail, "ENVELOPE_LINEAGE_CYCLE")
        if eid in depths:
            return depths[eid]
        envelope = records[eid]
        parent_id = envelope["parent_envelope_id"]
        if parent_id is None:
            depth = 0
        else:
            require(parent_id in records, "PARENT_ENVELOPE_NOT_FOUND")
            parent = records[parent_id]
            require(envelope["mode"] in MODE_NEXT[parent["mode"]],
                    "MODE_TRANSITION_NOT_ALLOWED")
            require(envelope["root_work_id"] == parent["root_work_id"],
                    "ROOT_WORK_ID_CHANGED_IN_LINEAGE")
            require(envelope["collision_domain"] == parent["collision_domain"],
                    "COLLISION_DOMAIN_CHANGED_IN_LINEAGE")
            require(set(envelope["allowed_actions"]) <= set(parent["allowed_actions"]),
                    "TURTLE_ACTION_AMPLIFICATION")
            require(envelope["effect_ceiling"] in
                    EFFECT_DESCENDANTS[parent["effect_ceiling"]],
                    "TURTLE_EFFECT_AMPLIFICATION")
            require(envelope["authorization_basis"] in
                    {"NONE", parent["authorization_basis"]},
                    "TURTLE_AUTHORIZATION_BASIS_AMPLIFICATION")
            require(envelope["break_glass"] in BREAK_GLASS_NEXT[parent["break_glass"]],
                    "TURTLE_BREAK_GLASS_CLEARED_OR_ESCALATED")
            parent_bindings = parent["source_bindings"]
            child_bindings = envelope["source_bindings"]
            require(child_bindings["participation_canonical_sha256"] ==
                    parent_bindings["participation_canonical_sha256"] and
                    child_bindings["standing_authorization_canonical_sha256"] ==
                    parent_bindings["standing_authorization_canonical_sha256"],
                    "TURTLE_CONTROL_SOURCE_CHANGED")
            depth = depth_of(parent_id, trail + (eid,)) + 1
        require(depth <= MAX_DEPTH, "ENVELOPE_LINEAGE_TOO_DEEP")
        depths[eid] = depth
        return depth

    for eid in records:
        depth_of(eid)

    collision_actuators: dict[str, set[str]] = {}
    for envelope in records.values():
        actuator = envelope["actuator_id"]
        if actuator is not None:
            collision_actuators.setdefault(envelope["collision_domain"], set()).add(actuator)
    require(all(len(ids) <= 1 for ids in collision_actuators.values()),
            "MULTIPLE_ACTUATORS_IN_COLLISION_DOMAIN")

    report: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "state": "PASS_BOUNDED_STATIC_COMPOSITION_ONLY",
        "as_of": now.isoformat(),
        "envelopes_validated": len(records),
        "roots": sum(1 for item in records.values() if item["parent_envelope_id"] is None),
        "max_depth": max(depths.values()),
        "active_collision_domains": len(collision_actuators),
        "active_actuators": sum(len(ids) for ids in collision_actuators.values()),
        "explicit_authorizations_verified": verified_explicit,
        "effects_executed": 0,
        "runtime_bindings_proven": 0,
        "receiver_ack_proven": False,
        "canon_or_coex_proven": False,
        "source_bindings": {
            "dependency_file_sha256": dependency_hashes,
            "participation_canonical_sha256": participation_hash,
            "standing_authorization_canonical_sha256": standing_hash,
        },
        "nonclaims": sorted(NONCLAIMS),
    }
    report["receipt_sha256"] = hashlib.sha256(canonical(report)).hexdigest()
    return report


def read_json(path_value: str) -> Any:
    path = Path(path_value)
    require(path.is_file() and not path.is_symlink() and
            0 < path.stat().st_size <= MAX_INPUT_BYTES,
            "INPUT_NOT_BOUNDED_REGULAR_FILE")
    try:
        return json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise Held("INPUT_JSON_INVALID") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate static CoAgency envelopes")
    parser.add_argument("--envelopes", required=True)
    parser.add_argument("--participants", required=True)
    parser.add_argument("--participation", required=True)
    parser.add_argument("--standing-authorization", default=STANDING_PATH)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args()
    try:
        report = validate_forest(
            read_json(args.envelopes), read_json(args.participants),
            read_json(args.participation), read_json(args.standing_authorization),
            as_of=args.as_of,
        )
        print(json.dumps(report, sort_keys=True))
        return 0
    except (Held, OSError, TypeError, ValueError) as exc:
        print(json.dumps({
            "schema": REPORT_SCHEMA, "state": "HELD", "reason": str(exc)[:160],
            "effects_executed": 0, "runtime_bindings_proven": 0,
            "receiver_ack_proven": False,
        }, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
