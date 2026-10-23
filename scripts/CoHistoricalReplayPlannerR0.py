#!/usr/bin/env python3
"""Compile a bounded historical replay plan without executing models."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

FORMAT = "CoHistoricalReplaySpecR0"
PLAN = "CoHistoricalReplayPlan.R0.v0.1-candidate"
ALLOWED_LANES = {
    "DETERMINISTIC_BASELINE",
    "LOCAL_MODEL",
    "CLAUDE",
    "OPENAI_COMPATIBLE",
    "HISTORICAL_RUNTIME_IF_AVAILABLE",
}
ALLOWED_DIMENSIONS = {
    "SOURCE_FIDELITY",
    "FACTUALITY",
    "EVIDENCE_QUALITY",
    "UNCERTAINTY_CALIBRATION",
    "COUNTEREVIDENCE_HANDLING",
    "CONTRADICTION_HANDLING",
    "REASONING_STRUCTURE",
    "SAFETY_AUTHORITY_BOUNDARY",
    "REPRODUCIBILITY",
}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")


class ReplayError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def normalized_relative_path(value: Any) -> PurePosixPath:
    require(isinstance(value, str) and value and "\\" not in value,
            "source path must be a nonblank POSIX relative path")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute()
        and parsed.as_posix() == value
        and all(part not in {".", ".."} for part in parsed.parts),
        "source path must be normalized and relative",
    )
    return parsed


def validate_spec(spec: Any) -> dict[str, Any]:
    require(isinstance(spec, dict), "spec must be an object")
    require(spec.get("format") == FORMAT, "wrong replay spec format")

    source = spec.get("source")
    require(isinstance(source, dict), "source must be an object")
    normalized_relative_path(source.get("path"))
    blob = source.get("git_blob_sha1")
    require(isinstance(blob, str) and HEX40.fullmatch(blob),
            "source git blob must be lowercase SHA-1")
    for key in ("source_ref", "artifact_kind"):
        require(isinstance(source.get(key), str) and source[key].strip(),
                f"source {key} required")

    historical = spec.get("historical_environment")
    require(isinstance(historical, dict), "historical_environment must be an object")
    for key in ("provider", "model_id", "model_version", "tool_environment"):
        value = historical.get(key)
        require(value is None or (isinstance(value, str) and value.strip()),
                f"historical {key} must be null or a nonblank string")
    require(historical.get("completeness") in {"KNOWN", "PARTIAL", "UNKNOWN"},
            "historical completeness must be KNOWN, PARTIAL or UNKNOWN")

    lanes = spec.get("target_lanes")
    require(isinstance(lanes, list) and 1 <= len(lanes) <= 12,
            "target_lanes must be a bounded nonempty list")
    require(all(isinstance(item, str) and item in ALLOWED_LANES for item in lanes),
            "unknown target lane")
    require(len(lanes) == len(set(lanes)), "duplicate target lane")

    dimensions = spec.get("evaluation_dimensions")
    require(isinstance(dimensions, list) and 1 <= len(dimensions) <= 16,
            "evaluation_dimensions must be a bounded nonempty list")
    require(all(
        isinstance(item, str) and item in ALLOWED_DIMENSIONS
        for item in dimensions
    ), "unknown evaluation dimension")
    require(len(dimensions) == len(set(dimensions)),
            "duplicate evaluation dimension")

    require(spec.get("preserve_original") is True,
            "historical replay requires preserve_original=true")
    require(spec.get("execution_policy") == "PLAN_ONLY",
            "execution_policy must be PLAN_ONLY")
    return spec


def load_source(root: Path, spec: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    source = spec["source"]
    root = root.resolve(strict=True)
    relative = normalized_relative_path(source["path"])
    path = root.joinpath(*relative.parts).resolve(strict=True)
    require(path.is_relative_to(root) and path.is_file(),
            "source path leaves repo root or is not a regular file")
    raw = path.read_bytes()
    actual_blob = git_blob_sha1(raw)
    require(actual_blob == source["git_blob_sha1"],
            "source bytes do not match declared Git blob")
    return raw, {
        "path": relative.as_posix(),
        "bytes": len(raw),
        "sha256": sha256(raw),
        "git_blob_sha1": actual_blob,
        "source_ref": source["source_ref"],
        "artifact_kind": source["artifact_kind"],
    }


def build_plan(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    validate_spec(spec)
    raw, binding = load_source(root, spec)
    historical = copy.deepcopy(spec["historical_environment"])
    dimensions = list(spec["evaluation_dimensions"])
    cells = []
    for lane in spec["target_lanes"]:
        identity = {
            "plan": PLAN,
            "source_sha256": binding["sha256"],
            "lane": lane,
            "dimensions": dimensions,
        }
        cells.append({
            "replay_cell_id": "coreplay:" + sha256(canonical(identity)),
            "lane": lane,
            "state": "PLANNED__NOT_EXECUTED",
            "source_sha256": binding["sha256"],
            "evaluation_dimensions": dimensions,
            "historical_equivalence": "NOT_CLAIMED",
            "evidence_independence": "UNKNOWN__SHARED_SOURCE_ARTIFACT",
            "result": None,
        })

    require(len(raw) == binding["bytes"], "source byte count changed")
    unknown_fields = [
        key for key in ("provider", "model_id", "model_version", "tool_environment")
        if historical.get(key) is None
    ]
    identity = {
        "plan": PLAN,
        "source_binding": binding,
        "historical_environment": historical,
        "target_lanes": spec["target_lanes"],
        "dimensions": dimensions,
    }
    return {
        "schema": PLAN,
        "state": "HISTORICAL_REPLAY_PLAN__ZERO_EXECUTION",
        "plan_id": "coreplay-plan:" + sha256(canonical(identity)),
        "source_binding": binding,
        "original_artifact": {
            "preserved": True,
            "baseline_role": "HISTORICAL_REFERENCE__NOT_TRUTH_AUTHORITY",
        },
        "historical_environment": historical,
        "historical_unknown_fields": unknown_fields,
        "comparison_policy": {
            "same_prompt_same_experiment": False,
            "newer_model_implies_better": False,
            "provider_diversity_implies_independent_evidence": False,
            "old_result_overwritten": False,
            "evaluation_dimensions": dimensions,
        },
        "replay_cells": cells,
        "execution_performed": False,
        "external_effects": 0,
        "next": "AUTHORIZE_ONE_CELL_THEN_BIND_OUTPUT_AND_COMPARE_WITH_FIXED_CRITERIA",
        "nonclaims": [
            "PLAN_NE_EXECUTION",
            "SOURCE_ARTIFACT_NE_TRUTH",
            "SAME_PROMPT_NE_SAME_EXPERIMENT",
            "NEWER_MODEL_NE_BETTER_RESULT",
            "MODEL_COUNT_NE_INDEPENDENCE",
            "PROVIDER_DIVERSITY_NE_EVIDENCE_INDEPENDENCE",
            "REPLAY_NE_RECEIVER_PICKUP",
            "REPLAY_NE_RUNTIME_ADOPTION",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        result = build_plan(args.repo_root, spec)
    except (OSError, UnicodeError, json.JSONDecodeError, ReplayError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
