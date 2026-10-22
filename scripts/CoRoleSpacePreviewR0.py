#!/usr/bin/env python3
"""Count and sample declared configuration tuples; grant no roles or effects.

The axes mix operational roles, session forms, actor classes and assertion labels.
Their cross-product is not a census of meaningful roles or admissible contracts.
Only four local public registry files are read; no model, network or worker calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import gcd, prod
from pathlib import Path
from typing import Any


RECIPE = "CoRoleSpacePreview.R0.v0.1-candidate"
MAX_SAMPLE = 100
SOURCE_PATHS = (
    "schemas/cospawn-contract-v0.1.schema.json",
    "ai/virtual-session-policy.json",
    "ai/evolution-lanes.json",
    "schemas/coevo-delta-v0.1.schema.json",
)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


def load_axes(root: Path) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    documents = {}
    bindings = []
    for name in SOURCE_PATHS:
        raw = (root / name).read_bytes()
        documents[name] = json.loads(raw.decode("utf-8"))
        bindings.append({"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    spawn, policy, lanes, delta = (documents[name] for name in SOURCE_PATHS)
    lane_rows = lanes["domains"]
    if not isinstance(lane_rows, list) or any(
        not isinstance(row, list) or len(row) != 3 for row in lane_rows
    ):
        raise ValueError("evolution lanes must contain three-item domain rows")
    axes = {
        "operational_role": spawn["properties"]["role"]["enum"],
        "morphology": policy["morphologies"],
        "persistence_mode": policy["persistence_modes"],
        "participant_class": policy["participant_classes"],
        "domain": [row[0] for row in lane_rows],
        "epistemic_class": delta["properties"]["epistemic_class"]["enum"],
    }
    for name, values in axes.items():
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"{name} must be a nonempty list of nonblank strings")
        if len(set(values)) != len(values):
            raise ValueError(f"{name} contains duplicate values")
    return {name: sorted(values) for name, values in axes.items()}, bindings


def parse_filters(items: list[str]) -> dict[str, str]:
    filters = {}
    for item in items:
        name, separator, value = item.partition("=")
        if not separator or not name or not value:
            raise ValueError("filters must be exact AXIS=VALUE expressions")
        if name in filters:
            raise ValueError(f"duplicate filter axis: {name}")
        filters[name] = value
    return filters


def decode_rank(rank: int, axes: dict[str, list[str]]) -> dict[str, str]:
    """Decode one mixed-radix rank without enumerating the Cartesian product."""
    values = {}
    for name in reversed(axes):
        rank, index = divmod(rank, len(axes[name]))
        values[name] = axes[name][index]
    return {name: values[name] for name in axes}


def build_preview(root: Path, filters: dict[str, str] | None = None,
                  limit: int = 7, seed: str = "0") -> dict[str, Any]:
    if type(limit) is not int or not 0 <= limit <= MAX_SAMPLE:
        raise ValueError(f"limit must be an integer from 0 to {MAX_SAMPLE}")
    if not isinstance(seed, str):
        raise ValueError("seed must be a string")
    if filters is not None and not isinstance(filters, dict):
        raise ValueError("filters must be an axis-to-value object")
    filters = {} if filters is None else dict(filters)
    axes, bindings = load_axes(root)
    for name, value in filters.items():
        if name not in axes or not isinstance(value, str) or value not in axes[name]:
            raise ValueError(f"unknown axis or value: {name}={value}")
    selected = {name: [filters[name]] if name in filters else values for name, values in axes.items()}
    raw_count = prod(len(values) for values in axes.values())
    filtered_count = prod(len(values) for values in selected.values())
    sample_count = min(limit, filtered_count)
    # A coprime stride visits distinct ranks; at most MAX_SAMPLE are decoded.
    # This deterministic convenience sample makes no uniformity/coverage claim.
    seed_basis = {"recipe": RECIPE, "source_bindings": bindings, "filters": filters, "seed": seed}
    digest = fingerprint(seed_basis)
    start = int(digest[:32], 16) % filtered_count
    stride = int(digest[32:], 16) % filtered_count or 1
    while gcd(stride, filtered_count) != 1:
        stride += 1
    preview = []
    for index in range(sample_count):
        rank = (start + index * stride) % filtered_count
        facets = decode_rank(rank, selected)
        identity = {"recipe": RECIPE, "source_bindings": bindings, "facets": facets}
        preview.append({
            "configuration_id": "corole-preview:" + fingerprint(identity),
            "filtered_rank": rank,
            "facets": facets,
            "assessment": "UNASSESSED",
        })
    return {
        "schema": RECIPE,
        "state": "CANDIDATE_PREVIEW__NO_ASSIGNMENT_OR_MATERIALIZATION",
        "projection_policy": "ONE_VALUE_PER_AXIS__BEFORE_SEMANTIC_COMPATIBILITY_CHECKS",
        "source_bindings": bindings,
        "axis_counts": {name: len(values) for name, values in axes.items()},
        "raw_configuration_count": raw_count,
        "exact_filters": dict(sorted(filters.items())),
        "filtered_configuration_count": filtered_count,
        "eligible_configuration_count": None,
        "sample_count": sample_count,
        "sampling": {
            "method": "SHA256_SEEDED_COPRIME_STRIDE_V1", "seed": seed,
            "start": start, "stride": stride, "maximum_sample": MAX_SAMPLE,
            "coverage_claim": "NONE",
        },
        "preview": preview,
        "effects": {"actors_assigned": 0, "workers_started": 0, "permissions_granted": 0, "external_mutations": 0},
        "next": "TASK_SPECIFIC_SEMANTIC_REVIEW_THEN_EXISTING_AUTHORITY_AND_RECEIVER_GATES",
        "nonclaims": [
            "RAW_TUPLE_COUNT_NE_DISTINCT_ROLE_COUNT",
            "CONFIGURATION_NE_ELIGIBLE_CONTRACT",
            "PARTICIPANT_CLASS_NE_VERIFIED_ACTOR",
            "EPISTEMIC_LABEL_NE_EVIDENCE",
            "PERSISTENCE_LABEL_NE_RECONSTRUCTION_PROOF",
            "PREVIEW_NE_INDEPENDENT_PANEL_OR_LIVE_FLEET",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--filter", action="append", default=[], metavar="AXIS=VALUE")
    parser.add_argument("--limit", type=int, default=7)
    parser.add_argument("--seed", default="0")
    args = parser.parse_args()
    try:
        result = build_preview(args.repo_root, parse_filters(args.filter), args.limit, args.seed)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
