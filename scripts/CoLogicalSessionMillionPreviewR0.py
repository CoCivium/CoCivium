#!/usr/bin/env python3
"""Preview a very large logical-session population without materializing workers.

The preview is recipe-backed and bounded: it computes exact declared counts and
samples at most MAX_SAMPLE logical session descriptors. It starts no workers,
creates no provider sessions or accounts, and grants no authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import gcd
from pathlib import Path
from typing import Any


RECIPE = "CoLogicalSessionMillionPreview.R0.v0.1-candidate"
MAX_LOGICAL = 10**12
MAX_SAMPLE = 100
MAX_MATERIALIZATION_CEILING = 4096
SOURCE_PATHS = (
    "ai/virtual-session-policy.json",
    "schemas/cospawn-contract-v0.1.schema.json",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load_sources(root: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    documents = {}
    bindings = []
    for relative in SOURCE_PATHS:
        raw = (root / relative).read_bytes()
        documents[relative] = json.loads(raw.decode("utf-8"))
        bindings.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    policy = documents[SOURCE_PATHS[0]]
    spawn = documents[SOURCE_PATHS[1]]
    for key in ("morphologies", "persistence_modes"):
        values = policy.get(key)
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"{key} must be a nonempty list of nonblank strings")
        if len(set(values)) != len(values):
            raise ValueError(f"{key} contains duplicate values")
    roles = spawn.get("properties", {}).get("role", {}).get("enum")
    if not isinstance(roles, list) or not roles or any(
        not isinstance(value, str) or not value.strip() for value in roles
    ):
        raise ValueError("spawn role enum must be a nonempty list of nonblank strings")
    if len(set(roles)) != len(roles):
        raise ValueError("spawn role enum contains duplicate values")
    return policy, spawn, bindings


def _bounded_int(value: Any, minimum: int, maximum: int, label: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{label} must be an integer from {minimum} to {maximum}")
    return value


def sample_indices(count: int, sample_limit: int, seed_basis: dict[str, Any]) -> list[int]:
    sample_count = min(count, sample_limit)
    if sample_count == 0:
        return []
    digest = fingerprint(seed_basis)
    start = int(digest[:32], 16) % count
    stride = int(digest[32:], 16) % count or 1
    while gcd(stride, count) != 1:
        stride += 1
    return [(start + index * stride) % count for index in range(sample_count)]


def session_descriptor(
    index: int,
    seed: str,
    source_bindings: list[dict[str, Any]],
    policy: dict[str, Any],
    spawn: dict[str, Any],
) -> dict[str, Any]:
    basis = {
        "recipe": RECIPE,
        "seed": seed,
        "logical_index": index,
        "source_bindings": source_bindings,
    }
    digest = fingerprint(basis)
    roles = spawn["properties"]["role"]["enum"]
    morphologies = policy["morphologies"]
    persistence = policy["persistence_modes"]
    role = roles[int(digest[0:16], 16) % len(roles)]
    morphology = morphologies[int(digest[16:32], 16) % len(morphologies)]
    persistence_mode = persistence[int(digest[32:48], 16) % len(persistence)]
    return {
        "virtual_session_id": "covsession:" + fingerprint(basis),
        "logical_index": index,
        "role": role,
        "morphology": morphology,
        "persistence_mode": persistence_mode,
        "materialization_state": "LOGICAL_ONLY",
        "wake_condition": "UNBOUND_PREVIEW__NO_WAKE",
        "authority_ceiling": "NONE__PREVIEW_ONLY",
        "assessment": "UNASSESSED",
    }


def build_preview(
    root: Path,
    logical_count: int = 1_000_000,
    sample_limit: int = 12,
    materialization_ceiling: int = 64,
    seed: str = "0",
) -> dict[str, Any]:
    logical_count = _bounded_int(logical_count, 1, MAX_LOGICAL, "logical count")
    sample_limit = _bounded_int(sample_limit, 0, MAX_SAMPLE, "sample limit")
    materialization_ceiling = _bounded_int(
        materialization_ceiling, 0, MAX_MATERIALIZATION_CEILING,
        "materialization ceiling"
    )
    if not isinstance(seed, str):
        raise ValueError("seed must be a string")

    policy, spawn, bindings = load_sources(root)
    seed_basis = {
        "recipe": RECIPE,
        "logical_count": logical_count,
        "seed": seed,
        "source_bindings": bindings,
    }
    indices = sample_indices(logical_count, sample_limit, seed_basis)
    preview = [
        session_descriptor(index, seed, bindings, policy, spawn)
        for index in indices
    ]
    if len({item["virtual_session_id"] for item in preview}) != len(preview):
        raise ValueError("sample session identity collision")

    return {
        "schema": RECIPE,
        "state": "LOGICAL_POPULATION_PREVIEW__NO_MATERIALIZATION",
        "population_representation": "GENERATIVE_RECIPE_PLUS_BOUNDED_SAMPLE",
        "source_bindings": bindings,
        "logical_session_count": logical_count,
        "enumerated_session_records": len(preview),
        "sample_limit": sample_limit,
        "materialization_ceiling": materialization_ceiling,
        "eligible_materialization_count": None,
        "selected_for_materialization": [],
        "sampling": {
            "method": "SHA256_SEEDED_COPRIME_STRIDE_V1",
            "seed": seed,
            "sample_indices": indices,
            "coverage_claim": "NONE",
        },
        "preview": preview,
        "effects": {
            "workers_started": 0,
            "provider_sessions_created": 0,
            "accounts_created": 0,
            "messages_sent": 0,
            "external_mutations": 0,
            "authority_granted": 0,
        },
        "activation_policy": {
            "principle": "DEDUPE_THEN_DONATE_THEN_LOGICAL_RESERVE_THEN_MATERIALIZE_IF_JUSTIFIED",
            "materialization_requires": [
                "TASK_SPECIFIC_ELIGIBILITY",
                "CAPABILITY_FIT",
                "AUTHORITY",
                "CONFIDENTIALITY_COMPATIBILITY",
                "BUDGET",
                "FINITE_LEASE",
                "COLLISION_CHECK",
                "RECEIVER",
                "STOP_CONDITION",
            ],
            "anonymous_or_deceptive_identity_creation": "OUT_OF_SCOPE_AND_NOT_PERMITTED_BY_THIS_PREVIEW",
        },
        "next": "BIND_REAL_TASKS_AND_EVIDENCE_THEN_ELECT_A_SMALL_BOUNDED_ACTIVE_FRONTIER",
        "nonclaims": [
            "LOGICAL_SESSION_COUNT_NE_ACTIVE_PROCESS_COUNT",
            "LOGICAL_SESSION_COUNT_NE_PROVIDER_SESSION_COUNT",
            "LOGICAL_SESSION_COUNT_NE_ACCOUNT_COUNT",
            "MATERIALIZATION_CEILING_NE_SELECTION",
            "AVAILABLE_CAPACITY_NE_AUTHORITY_TO_SPAWN",
            "SAMPLE_NE_POPULATION_COVERAGE",
            "MODEL_COUNT_NE_INDEPENDENCE",
            "PREVIEW_NE_RUNTIME_ADOPTION",
            "PREVIEW_NE_RECEIVER_PICKUP",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--logical-count", type=int, default=1_000_000)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--materialization-ceiling", type=int, default=64)
    parser.add_argument("--seed", default="0")
    args = parser.parse_args()
    try:
        result = build_preview(
            args.repo_root,
            logical_count=args.logical_count,
            sample_limit=args.sample_limit,
            materialization_ceiling=args.materialization_ceiling,
            seed=args.seed,
        )
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
