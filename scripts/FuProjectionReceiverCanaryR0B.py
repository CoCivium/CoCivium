#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPECTED_FAMILIES = {
    "HUMAN_READABLE_2D",
    "HUMAN_OR_MACHINE_3D_NEIGHBORHOOD",
    "COTIME_TRAJECTORY",
    "COPRIMATH_STYLE_CANDIDATE",
    "COGIBBERTRU_STYLE_CANDIDATE",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise SystemExit(f"FAIL_CLOSED__JSON_OBJECT_REQUIRED={path}")
    return obj


def write_json(path: Path, obj: dict[str, Any]) -> str:
    data = (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(data)
    return sha256_bytes(data)


def worker(projection_path: Path, output_path: Path) -> int:
    p = load_json(projection_path)
    required = [
        "projection_id",
        "projection_family",
        "candidate_identity",
        "symbol",
        "epistemic_class",
        "authority_ceiling",
        "receiver_scope",
        "rendering",
        "projection_loss",
    ]
    missing = [key for key in required if key not in p]
    if missing:
        raise SystemExit("FAIL_CLOSED__PROJECTION_FIELDS_MISSING=" + ",".join(missing))

    loss = p.get("projection_loss")
    if not isinstance(loss, list) or not loss:
        raise SystemExit("FAIL_CLOSED__PROJECTION_LOSS_UNDECLARED")

    observation = {
        "schema": "CoAll.FuProjectionReceiverObservation.R0B.v0.1-candidate",
        "state": "BOUNDED_PROJECTION_ONLY_RECEIVER_OBSERVATION",
        "process_id": os.getpid(),
        "projection_id": str(p["projection_id"]),
        "projection_family": str(p["projection_family"]),
        "core_observation": {
            "candidate_identity": str(p["candidate_identity"]),
            "symbol": str(p["symbol"]),
            "epistemic_class": str(p["epistemic_class"]),
            "authority_ceiling": str(p["authority_ceiling"]),
        },
        "declared_projection_loss": [str(x) for x in loss],
        "input_scope": "ONE_PROJECTION_OBJECT_ONLY",
        "source_object_visible_to_worker": False,
        "semantic_equivalence_claim": "NOT_PROVEN",
        "nonclaims": [
            "STRUCTURAL_RECOVERY_NE_SEMANTIC_EQUIVALENCE",
            "DISTINCT_PROCESS_NE_DISTINCT_FAILURE_DOMAIN",
            "PROJECTION_ONLY_RECEIVER_NE_INDEPENDENT_MODEL",
        ],
    }
    digest = write_json(output_path, observation)
    print(json.dumps({
        "STATE": observation["state"],
        "PROCESS_ID": observation["process_id"],
        "PROJECTION_ID": observation["projection_id"],
        "OUTPUT_SHA256": digest,
    }, separators=(",", ":")))
    return 0


def run_worker(script_path: Path, projection: dict[str, Any], root: Path, label: str) -> dict[str, Any]:
    inp = root / f"{label}.input.json"
    out = root / f"{label}.observation.json"
    write_json(inp, projection)
    cp = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--worker",
            "--projection",
            str(inp),
            "--output",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    terminal = json.loads(cp.stdout.strip().splitlines()[-1])
    artifact = load_json(out)
    return {
        "terminal": terminal,
        "artifact": artifact,
        "artifact_sha256": sha256_bytes(out.read_bytes()),
    }


def compare_core(source: dict[str, Any], observation: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    core = observation["core_observation"]
    checks = [
        ("candidate_identity", "IDENTITY_DRIFT"),
        ("symbol", "SYMBOL_DRIFT"),
        ("epistemic_class", "EPISTEMIC_DRIFT"),
        ("authority_ceiling", "AUTHORITY_DRIFT"),
    ]
    for key, code in checks:
        if str(core.get(key)) != str(source.get(key)):
            issues.append(code)
    if not observation.get("declared_projection_loss"):
        issues.append("LOSS_UNDECLARED")
    return issues


def parent(canary_path: Path, out_root: Path) -> int:
    canary = load_json(canary_path)
    source = canary.get("source_object")
    projections = canary.get("projections")
    if not isinstance(source, dict):
        raise SystemExit("FAIL_CLOSED__SOURCE_OBJECT_REQUIRED")
    if not isinstance(projections, list) or len(projections) != 5:
        raise SystemExit("FAIL_CLOSED__EXACTLY_FIVE_PROJECTIONS_REQUIRED")
    if out_root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out_root}")
    out_root.mkdir(parents=True, exist_ok=False)

    script_path = Path(__file__).resolve()
    runs: list[dict[str, Any]] = []
    for index, projection in enumerate(projections, start=1):
        if not isinstance(projection, dict):
            raise SystemExit("FAIL_CLOSED__PROJECTION_OBJECT_REQUIRED")
        runs.append(run_worker(script_path, projection, out_root, f"receiver-{index}"))

    pids = [int(r["artifact"]["process_id"]) for r in runs]
    if len(set(pids)) != 5:
        raise SystemExit("FAIL_CLOSED__RECEIVER_PROCESS_IDS_NOT_DISTINCT")

    families = {str(r["artifact"]["projection_family"]) for r in runs}
    if families != EXPECTED_FAMILIES:
        raise SystemExit("FAIL_CLOSED__PROJECTION_FAMILY_SET_MISMATCH")

    receiver_results = []
    all_issues: list[str] = []
    loss_signatures = set()
    for r in runs:
        obs = r["artifact"]
        issues = compare_core(source, obs)
        all_issues.extend(f"{obs['projection_id']}:{issue}" for issue in issues)
        loss_signatures.add(tuple(sorted(obs["declared_projection_loss"])))
        receiver_results.append({
            "projection_id": obs["projection_id"],
            "projection_family": obs["projection_family"],
            "process_id": obs["process_id"],
            "artifact_sha256": r["artifact_sha256"],
            "core_issues": issues,
            "declared_projection_loss_count": len(obs["declared_projection_loss"]),
        })

    if all_issues:
        raise SystemExit("FAIL_CLOSED__CORE_INVARIANT_DRIFT=" + ";".join(all_issues))
    if len(loss_signatures) < 3:
        raise SystemExit("FAIL_CLOSED__PROJECTION_DIVERGENCE_COLLAPSED")

    tampered_ep = copy.deepcopy(projections[0])
    tampered_ep["epistemic_class"] = "OBSERVED"
    ep_run = run_worker(script_path, tampered_ep, out_root, "tamper-epistemic")
    ep_issues = compare_core(source, ep_run["artifact"])
    if "EPISTEMIC_DRIFT" not in ep_issues:
        raise SystemExit("FAIL_CLOSED__EPISTEMIC_TAMPER_NOT_DETECTED")

    tampered_id = copy.deepcopy(projections[1])
    tampered_id["candidate_identity"] = "coall-element:Fu:TAMPER"
    id_run = run_worker(script_path, tampered_id, out_root, "tamper-identity")
    id_issues = compare_core(source, id_run["artifact"])
    if "IDENTITY_DRIFT" not in id_issues:
        raise SystemExit("FAIL_CLOSED__IDENTITY_TAMPER_NOT_DETECTED")

    result = {
        "schema": "CoAll.FuProjectionReceiverCanary.R0B.v0.1-candidate",
        "state": "PASS_R0B_FIVE_DISTINCT_RECEIVER_PROCESSES__CORE_INVARIANTS_STABLE__DECLARED_DIVERGENCE_PRESERVED__TAMPER_REJECTED__SEMANTIC_EQUIVALENCE_NOT_PROVEN",
        "source_canary_sha256": sha256_bytes(canary_path.read_bytes()),
        "coverage": {
            "receiver_processes": 5,
            "projection_families": sorted(families),
            "distinct_process_ids": len(set(pids)),
            "unique_declared_loss_signatures": len(loss_signatures),
            "tamper_cases": 2,
        },
        "receiver_results": receiver_results,
        "checks": {
            "same_candidate_identity_across_receivers": True,
            "same_symbol_across_receivers": True,
            "mythic_epistemic_class_preserved": True,
            "authority_ceiling_preserved": True,
            "projection_loss_declared_by_every_receiver": True,
            "projection_divergence_preserved": True,
            "epistemic_tamper_rejected": True,
            "identity_tamper_rejected": True,
            "semantic_equivalence": "NOT_PROVEN",
            "independent_model_understanding": "NOT_TESTED",
        },
        "effects": {
            "repo_mutations_by_canary": 0,
            "runtime_promotions": 0,
            "canon_promotions": 0,
            "authority_changes": 0,
            "participant_notifications": 0,
        },
        "next": "R0C_HETEROGENEOUS_MODEL_OR_HUMAN_RECEIVER_MEANING_RECOVERY_CHALLENGE",
        "nonclaims": [
            "STRUCTURAL_STABILITY_NE_SEMANTIC_EQUIVALENCE",
            "DISTINCT_RECEIVER_PROCESS_NE_DISTINCT_MODEL",
            "DISTINCT_PROCESS_NE_DISTINCT_FAILURE_DOMAIN",
            "TAMPER_REJECTION_NE_TRUTH",
            "PROJECTION_CANARY_NE_NATURAL_PERIODIC_LAW",
            "LANDED_CANDIDATE_NE_CANON",
            "NO_RUNTIME_OR_AUTHORITY_PROMOTION",
        ],
    }

    result_path = out_root / "r0b-result.json"
    digest = write_json(result_path, result)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(result_path),
        "OUTPUT_SHA256": digest,
        "RECEIVER_PIDS": pids,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--projection")
    ap.add_argument("--output")
    ap.add_argument("--canary")
    ap.add_argument("--out-root")
    args = ap.parse_args()

    if args.worker:
        if not args.projection or not args.output:
            raise SystemExit("FAIL_CLOSED__WORKER_REQUIRES_PROJECTION_AND_OUTPUT")
        return worker(Path(args.projection), Path(args.output))

    if not args.canary or not args.out_root:
        raise SystemExit("FAIL_CLOSED__PARENT_REQUIRES_CANARY_AND_OUT_ROOT")
    return parent(Path(args.canary), Path(args.out_root))


if __name__ == "__main__":
    raise SystemExit(main())
