#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any


# Required-core planner profile, not full v0.1/v0.2 schema validation.
# Unknown extensions remain part of raw payload identity.
CORE_STRING_FIELDS = (
    "delta_id", "session_id", "observed_at", "subject", "relation",
    "epistemic_class", "mutation_class", "authority_ceiling",
    "confidentiality", "next_receiver",
)
CORE_ARRAY_FIELDS = ("domain", "source_refs", "target_surfaces")
ENUM_FIELDS = {
    "epistemic_class": frozenset({
        "OBSERVED", "INFERRED", "HYPOTHESIS", "PREDICTED", "PLANNED", "PREFERRED",
        "METAPHORICAL", "MYTHIC", "HUMOROUS", "COUNTERFACTUAL", "UNKNOWN",
    }),
    "mutation_class": frozenset({
        "OBSERVE", "PROPOSE", "BRANCH_MUTATE", "REVIEW_CHALLENGE",
        "MERGE_LOW_EFFECT", "EFFECT_GATED",
    }),
    "confidentiality": frozenset({"PUBLIC", "PRIVATE", "RESTRICTED", "UNKNOWN"}),
}
TIMESTAMP_SHAPE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt](?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)


def stable_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_deltas(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        rows = value
    elif isinstance(value, dict) and isinstance(value.get("deltas"), list):
        rows = value["deltas"]
    else:
        raise ValueError("deltas input must be an array or an object with deltas[]")
    if not all(isinstance(x, dict) for x in rows):
        raise ValueError("every delta must be an object")
    return rows


def lane_map(lanes: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in lanes.get("domains", []):
        if not isinstance(row, list) or len(row) != 3:
            continue
        domain, repos, mode = row
        out[str(domain)] = {"repositories": list(repos), "mode": str(mode)}
    return out


def repo_visibility_map(repo_map_obj: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in repo_map_obj.get("repositories", []):
        repo = str(row.get("repo", ""))
        name = repo.split("/", 1)[-1] if repo else ""
        if name:
            out[name] = str(row.get("visibility", "unknown"))
    return out


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def nonblank_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def projected_string(delta: dict[str, Any], key: str) -> str:
    """Display-only fallback for blocked output; never repairs the raw input."""
    value = delta.get(key)
    return value if nonblank_string(value) else "INVALID_" + key.upper()


def string_items(delta: dict[str, Any], key: str) -> list[str]:
    """Guard projections; malformed values still participate in raw hashes."""
    value = delta.get(key)
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def valid_timestamp(value: Any) -> bool:
    """Bounded RFC 3339 shape/calendar check, not freshness or full RFC support.

    Requires an explicit zone; leap seconds and year 0000 are held for review.
    Exact raw text, including its offset and fraction, is never normalized in identity.
    """
    if not isinstance(value, str) or TIMESTAMP_SHAPE.fullmatch(value) is None:
        return False
    parsed = value[:10] + "T" + value[11:]
    if parsed[-1] in "Zz":
        parsed = parsed[:-1] + "+00:00"
    try:
        datetime.fromisoformat(parsed)
    except ValueError:
        return False
    return True


def projected_confidentiality(delta: dict[str, Any]) -> str:
    value = delta.get("confidentiality")
    return value if isinstance(value, str) and value in ENUM_FIELDS["confidentiality"] else "UNKNOWN"


def claim_slot_basis(delta: dict[str, Any]) -> dict[str, Any]:
    """A coarse review slot, never evidence that two deltas are equivalent."""
    return {
        "domain": sorted(string_items(delta, "domain")),
        "subject": normalize_text(delta.get("subject")),
        "relation": normalize_text(delta.get("relation")),
        "targets": sorted(string_items(delta, "target_surfaces")),
        "confidentiality": str(delta.get("confidentiality", "UNKNOWN")),
    }


def claim_body_basis(delta: dict[str, Any]) -> dict[str, Any]:
    """Compare claim bodies without discarding nested fields or extensions.

    These root-level annotations may vary between independent observations.
    They still participate in exact dedupe, so their inputs remain separate.
    Source references are not resolved here; this is not a currentness check.
    """
    annotations = {
        "delta_id", "session_id", "observed_at", "source_refs", "confidence",
        "tests", "risks", "wake_conditions",
    }
    body = {key: value for key, value in delta.items() if key not in annotations}
    for key in ("domain", "target_surfaces"):
        if isinstance(body.get(key), list):
            body[key] = sorted(body[key], key=lambda item: json.dumps(
                item, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ))
    return body


def choose_role(delta: dict[str, Any]) -> str:
    mutation = str(delta.get("mutation_class", ""))
    epistemic = str(delta.get("epistemic_class", ""))
    targets = string_items(delta, "target_surfaces")
    if mutation == "OBSERVE":
        return "OBSERVER"
    if mutation == "REVIEW_CHALLENGE":
        return "CHALLENGER"
    if mutation == "EFFECT_GATED":
        return "VERIFIER"
    if epistemic in {"HYPOTHESIS", "PREDICTED", "COUNTERFACTUAL", "UNKNOWN"}:
        return "RESEARCH_DONOR"
    if len(targets) > 1:
        return "PROJECTION_COMPILER"
    return "WORKER"


def validate_delta(delta: dict[str, Any], lanes: dict[str, dict[str, Any]], vis: dict[str, str]) -> list[str]:
    required = CORE_STRING_FIELDS + CORE_ARRAY_FIELDS
    issues = [f"MISSING_{x}" for x in required if x not in delta or delta.get(x) in (None, "")]
    for key in CORE_STRING_FIELDS:
        if not nonblank_string(delta.get(key)):
            issues.append("INVALID_NONBLANK_STRING:" + key)
    for key in CORE_ARRAY_FIELDS:
        value = delta.get(key)
        if not isinstance(value, list):
            issues.append("INVALID_STRING_ARRAY:" + key)
            continue
        if key == "domain" and not value:
            issues.append("EMPTY_DOMAIN_ARRAY")
        issues.extend(f"INVALID_STRING_ITEM:{key}:{i}" for i, item in enumerate(value)
                      if not isinstance(item, str))
    for key, values in ENUM_FIELDS.items():
        value = delta.get(key)
        if isinstance(value, str) and value not in values:
            issues.append("INVALID_ENUM:" + key)
    if not valid_timestamp(delta.get("observed_at")):
        issues.append("INVALID_TIMESTAMP:observed_at")
    issues.extend(f"UNKNOWN_DOMAIN:{d}" for d in string_items(delta, "domain") if d not in lanes)

    confidentiality = projected_confidentiality(delta)
    if confidentiality in {"PRIVATE", "RESTRICTED", "UNKNOWN"}:
        for target in string_items(delta, "target_surfaces"):
            name = target.split("/", 1)[-1]
            if vis.get(name) == "public":
                issues.append(f"CONFIDENTIALITY_PUBLIC_TARGET_COLLISION:{name}")
    return issues


def compile_plan(deltas: list[dict[str, Any]], lanes_obj: dict[str, Any], repo_map_obj: dict[str, Any]) -> dict[str, Any]:
    lanes = lane_map(lanes_obj)
    vis = repo_visibility_map(repo_map_obj)

    # Invalid IDs have diagnostic references, not coerced caller identities.
    # Avoid even an intentional caller collision with a generated reference.
    used_ids = {delta["delta_id"] for delta in deltas if nonblank_string(delta.get("delta_id"))}
    invalid_refs = {}
    for fingerprint in sorted({stable_hash(delta) for delta in deltas
                               if not nonblank_string(delta.get("delta_id"))}):
        reference = "INVALID_DELTA_ID:" + fingerprint
        while reference in used_ids:
            reference = "_" + reference
        invalid_refs[fingerprint] = reference
        used_ids.add(reference)

    def record_id(delta: dict[str, Any]) -> str:
        value = delta.get("delta_id")
        return value if nonblank_string(value) else invalid_refs[stable_hash(delta)]

    groups: dict[str, list[dict[str, Any]]] = {}
    collision_groups: dict[str, list[str]] = {}
    validation: dict[str, list[str]] = {}
    payloads_by_id: dict[str, set[str]] = {}
    claim_variants: dict[str, set[str]] = {}
    claim_members: dict[str, set[str]] = {}

    for delta in deltas:
        did = record_id(delta)
        issues = validate_delta(delta, lanes, vis)
        validation.setdefault(did, []).extend(issues)
        payloads_by_id.setdefault(did, set()).add(stable_hash(delta))

        # Only an exact JSON body, except its record identifier, is eligible
        # for equivalence donation. Unknown extensions are part of identity.
        dedupe_basis = {key: value for key, value in delta.items() if key != "delta_id"}
        dedupe_key = (stable_hash(dedupe_basis) if nonblank_string(delta.get("delta_id"))
                      else "INVALID_ID:" + stable_hash(delta))
        groups.setdefault(dedupe_key, []).append(delta)

        slot_basis = claim_slot_basis(delta)
        slot_key = stable_hash(slot_basis)
        claim_variants.setdefault(slot_key, set()).add(stable_hash(claim_body_basis(delta)))
        claim_members.setdefault(slot_key, set()).add(did)

        collision_basis = {
            "domain": slot_basis["domain"],
            "subject": slot_basis["subject"],
            "targets": slot_basis["targets"],
        }
        collision_key = stable_hash(collision_basis)[:24]
        collision_groups.setdefault(collision_key, []).append(did)

    for did, payloads in payloads_by_id.items():
        if len(payloads) > 1:
            validation[did].append("DELTA_ID_REUSED_WITH_DIFFERENT_PAYLOAD:" + did)

    for slot_key, variants in claim_variants.items():
        if len(variants) > 1:
            # Different bodies may represent successive observations or valid
            # alternatives. No chronology or authority rule here selects one.
            issue = "AMBIGUOUS_CLAIM_BODY_REQUIRES_RECONCILIATION:" + slot_key[:24]
            for did in claim_members[slot_key]:
                validation[did].append(issue)

    validation = {did: sorted(set(issues)) for did, issues in sorted(validation.items())}

    contracts: list[dict[str, Any]] = []
    donations: list[dict[str, Any]] = []

    for dedupe_key in sorted(groups):
        group = sorted(groups[dedupe_key], key=lambda x: (projected_string(x, "observed_at"), record_id(x)))
        primary = group[0]
        primary_id = record_id(primary)
        group_ids = sorted({record_id(item) for item in group})
        all_issues = sorted({issue for item in group for issue in validation[record_id(item)]})

        collision_basis = {
            "domain": sorted(string_items(primary, "domain")),
            "subject": normalize_text(primary.get("subject")),
            "targets": sorted(string_items(primary, "target_surfaces")),
        }
        collision_domain = "coevo:" + stable_hash(collision_basis)[:24]
        role = choose_role(primary)
        mutation_class = str(primary.get("mutation_class", ""))
        blocked = bool(all_issues)
        materialization_state = (
            "BLOCKED" if blocked
            else "SHADOW" if mutation_class == "EFFECT_GATED"
            else "LOGICAL_ONLY"
        )
        lease_mode = "SHADOW" if materialization_state == "SHADOW" else "LOGICAL_ONLY"

        input_bindings = []
        for item in group:
            input_bindings.extend(string_items(item, "source_refs"))
        input_bindings = sorted(set(input_bindings))

        contract = {
            "spawn_id": "cospawn:" + stable_hash({"primary": primary_id, "dedupe": dedupe_key})[:24],
            "purpose": f"Process bounded CoEvoDelta group led by {primary_id}",
            "parent_identity": projected_string(primary, "session_id"),
            "role": role,
            "scope": f"domains={','.join(string_items(primary, 'domain'))}; subject={projected_string(primary, 'subject')}",
            "input_bindings": input_bindings,
            "authority_ceiling": projected_string(primary, "authority_ceiling"),
            "confidentiality": projected_confidentiality(primary),
            "effect_classes": [mutation_class] if mutation_class in ENUM_FIELDS["mutation_class"] else [],
            "budget": {"max_live_embodiments": 0, "max_effectful_mutations": 0, "logical_work_units": 1},
            "lease": {"mode": lease_mode, "effect_lease": "NONE"},
            "idempotency_key": "dedupe:" + dedupe_key,
            "collision_domain": collision_domain,
            "receiver": projected_string(primary, "next_receiver"),
            "success_condition": "RECEIVER_DISPOSITION_AND_EVIDENCE_RECORDED",
            "stop_condition": "AUTHORITY_CONFIDENTIALITY_OR_COLLISION_AMBIGUITY",
            "checkpoint": None,
            "recovery_pointer": primary_id,
            "failure_domain": None,
            "handoff_rule": "DONATE_EQUIVALENT_DELTAS_TO_PRIMARY_AND_PRESERVE_SOURCE_REFS",
            "retirement_condition": "PRIMARY_DELTA_DISPOSITION_RECORDED_AND_DONATED_EQUIVALENTS_BOUND",
            "provenance": group_ids,
            "currentness": primary["observed_at"] if valid_timestamp(primary.get("observed_at")) else "INVALID_OBSERVED_AT",
            "uncertainty": ";".join(all_issues) if all_issues else None,
            "materialization_state": materialization_state,
        }
        contracts.append(contract)

        # A reused identifier or other validation failure must not create an
        # apparently usable equivalence handoff, even from a blocked contract.
        if blocked:
            continue
        for duplicate_id in group_ids:
            if duplicate_id == primary_id:
                continue
            donations.append({
                "donor_delta_id": duplicate_id,
                "receiver_delta_id": primary_id,
                "relation": "EQUIVALENT_DEDUPE_DONATION",
                "dedupe_key": dedupe_key,
                "nonclaims": ["DONATION_NE_SEMANTIC_IDENTITY_TOTALITY", "DEDUPE_NE_DELETE"]
            })

    collisions = []
    for key, ids in sorted(collision_groups.items()):
        unique_ids = sorted(set(ids))
        if len(unique_ids) > 1:
            collisions.append({
                "collision_domain": "coevo:" + key,
                "delta_ids": unique_ids,
                "state": "SERIAL_REVIEW_REQUIRED_IF_RELATIONS_DIFFER_OR_EFFECTS_COLLIDE"
            })

    return {
        "schema": "CoLogicalSpawnPlanner.R2.v0.1-candidate",
        "state": "LOGICAL_SPAWN_PLAN_COMPILED__NO_LIVE_MATERIALIZATION",
        "coverage": {
            "input_deltas": len(deltas),
            "logical_contracts": len(contracts),
            "dedupe_donations": len(donations),
            "collision_groups": len(collisions),
            "shadow_contracts": sum(1 for c in contracts if c.get("materialization_state") == "SHADOW"),
            "blocked_contracts": sum(1 for c in contracts if c.get("materialization_state") == "BLOCKED"),
        },
        "contracts": contracts,
        "donations": donations,
        "collisions": collisions,
        "validation": validation,
        "effects": {
            "live_workers_started": 0,
            "provider_sessions_created": 0,
            "provider_titles_mutated": 0,
            "provider_tabs_closed": 0,
            "repo_mutations_executed": 0,
            "authority_changes": 0,
        },
        "next": "R2B_SHADOW_VERIFIER_CANARY_THEN_R3_ONLY_FOR_AUTHORIZED_LOGICAL_ONLY_CONTRACT",
        "nonclaims": [
            "SPAWN_NE_NEW_CHAT",
            "LOGICAL_RESERVE_NE_LIVE_WORKER",
            "DEDUPE_NE_DELETE",
            "MODEL_NE_AUTHORITY",
            "GITHUB_WRITE_ACCESS_NE_GLOBAL_AUTHORITY",
            "EFFECT_GATED_NE_WORK_BLOCKED",
            "SHADOW_WORK_NE_EFFECT_AUTHORITY",
            "VIRTUAL_ARMADA_NE_AUTHORITY_MULTIPLICATION",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deltas", required=True)
    ap.add_argument("--lanes", required=True)
    ap.add_argument("--repo-map", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    plan = compile_plan(
        as_deltas(load_json(Path(args.deltas))),
        load_json(Path(args.lanes)),
        load_json(Path(args.repo_map)),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(plan, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE": plan["state"],
        "OUTPUT": str(out),
        "OUTPUT_SHA256": hashlib.sha256(encoded).hexdigest().upper(),
        "INPUT_DELTAS": plan["coverage"]["input_deltas"],
        "LOGICAL_CONTRACTS": plan["coverage"]["logical_contracts"],
        "DONATIONS": plan["coverage"]["dedupe_donations"],
        "COLLISION_GROUPS": plan["coverage"]["collision_groups"],
        "LIVE_WORKERS_STARTED": 0,
        "NEXT": plan["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
