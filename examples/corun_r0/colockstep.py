#!/usr/bin/env python3
"""CoMVP+/CoLockStep+ R0 source-island gate.

Read-only local source guard, NOT an actual release actuator, deployment
qualification, signed provenance check or proof of independent user benefit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "CoCivium.CoLockStep.SourceIsland.R0"
REPORT_SCHEMA = "CoCivium.CoLockStep.SourceAssessment.R0"
MAX_COMPONENTS = 24
MAX_SOURCE_BYTES = 2_000_000
ID = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
EFFECT = "READ_ONLY_LOCAL"
SCOPE = "SOURCE_ONLY_NOT_SERVING"


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n").encode("utf-8")


def blob_hash(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def insist(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError(explanation)


def source_components(snapshot: dict, root: Path) -> tuple[dict, list, list]:
    """Validate exact source identities, but never assert runtime quality."""
    errors: list[str] = []
    evidence: list[dict] = []
    mapping = {}
    items = snapshot.get("components")
    insist(isinstance(items, list) and 1 <= len(items) <= MAX_COMPONENTS,
           "missing or unbounded components")
    root = root.resolve()
    for item in items:
        insist(isinstance(item, dict), "malformed component")
        identifier = item.get("id")
        insist(isinstance(identifier, str) and ID.fullmatch(identifier),
               "invalid component identifier")
        insist(identifier not in mapping, "duplicate component identifier")
        mapping[identifier] = item
        insist(item.get("effect_scope") == EFFECT,
               "effect scope must be read-only")
        interfaces = item.get("provides")
        insist(isinstance(interfaces, dict) and bool(interfaces),
               "source component must expose typed interface")
        for interface, major in interfaces.items():
            insist(isinstance(interface, str) and ID.fullmatch(interface)
                   and type(major) is int and 1 <= major <= 99,
                   "invalid interface or major")
        rel = item.get("path")
        pin = item.get("git_blob_sha1")
        insist(isinstance(rel, str) and rel.startswith("examples/corun_r0/")
               and ".." not in Path(rel).parts, "unsafe source path")
        insist(isinstance(pin, str) and HEX40.fullmatch(pin), "invalid source pin")
        source = (root / rel).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            errors.append("MISSING_SOURCE:" + identifier)
            continue
        if source.stat().st_size > MAX_SOURCE_BYTES:
            errors.append("OVERSIZE_SOURCE:" + identifier)
            continue
        raw = source.read_bytes()
        actual = blob_hash(raw)
        if actual != pin:
            errors.append("SOURCE_DRIFT:" + identifier)
            continue
        evidence.append({"component_id": identifier, "path": rel,
                         "git_blob_sha1": actual,
                         "sha256": hashlib.sha256(raw).hexdigest()})
    return mapping, sorted(errors), sorted(evidence, key=lambda e: e["component_id"])


def compatible_edges(snapshot: dict, mapping: dict) -> list[str]:
    errors: list[str] = []
    edges = snapshot.get("dependencies")
    insist(isinstance(edges, list) and len(edges) <= MAX_COMPONENTS * 3,
           "invalid dependency list")
    walk: dict[str, set[str]] = {key: set() for key in mapping}
    for dep in edges:
        insist(isinstance(dep, dict), "malformed dependency")
        consumer, provider = dep.get("consumer"), dep.get("provider")
        interface, major = dep.get("interface"), dep.get("major")
        insist(isinstance(consumer, str) and isinstance(provider, str),
               "dependency actors missing")
        if consumer not in mapping or provider not in mapping or consumer == provider:
            errors.append("UNRESOLVED_DEPENDENCY:" + str(consumer) + ":" + str(provider))
            continue
        if not isinstance(interface, str) or type(major) is not int:
            errors.append("INVALID_INTERFACE_REQUIREMENT:" + consumer)
            continue
        if mapping[provider]["provides"].get(interface) != major:
            errors.append("INCOMPATIBLE_INTERFACE:" + consumer + ":" + provider)
        walk[consumer].add(provider)

    state: dict[str, int] = {}
    def visit(node: str) -> None:
        if state.get(node) == 1:
            raise ValueError("dependency cycle")
        if state.get(node) == 2:
            return
        state[node] = 1
        for provider in walk[node]:
            visit(provider)
        state[node] = 2

    try:
        for key in sorted(walk):
            visit(key)
    except ValueError:
        errors.append("DEPENDENCY_CYCLE")
    return sorted(set(errors))


def assess(manifest: dict, repo_root: Path) -> dict:
    """Advisory only: cannot promote a source snapshot to MVP or runtime."""
    insist(isinstance(manifest, dict) and manifest.get("schema") == SCHEMA,
           "wrong source-island schema")
    insist(isinstance(manifest.get("work_id"), str)
           and bool(manifest["work_id"].strip()), "missing WorkID")
    baseline, candidate = manifest.get("baseline"), manifest.get("candidate")
    insist(isinstance(baseline, dict) and isinstance(candidate, dict),
           "baseline and candidate snapshots required")
    insist(baseline.get("scope") == SCOPE, "baseline cannot self-claim serving")
    insist(isinstance(baseline.get("release_id"), str), "baseline identity missing")
    insist(isinstance(candidate.get("release_id"), str), "candidate identity missing")
    insist(candidate["release_id"] != baseline["release_id"],
           "candidate must have distinct release identity")
    old, old_errors, old_evidence = source_components(baseline, repo_root)
    insist(not old_errors, "BASELINE_SOURCE_NOT_RECOVERABLE:" + ",".join(old_errors))
    insist(not compatible_edges(baseline, old), "BASELINE_DEPENDENCIES_INVALID")
    old_fail = baseline.get("historical_fail_ids")
    insist(isinstance(old_fail, list) and all(isinstance(i, str) and i
           for i in old_fail) and len(set(old_fail)) == len(old_fail),
           "invalid baseline failure lineage")
    # A candidate can fail, and its failure must never mutate the baseline.
    candidate_errors: list[str] = []
    if candidate.get("scope") != SCOPE:
        candidate_errors.append("CLAIMED_SERVING_WITHOUT_RECEIVER_PROOF")
    try:
        new, errors, new_evidence = source_components(candidate, repo_root)
        candidate_errors.extend(errors)
        candidate_errors.extend(compatible_edges(candidate, new))
    except (ValueError, OSError) as exc:
        new, new_evidence = {}, []
        candidate_errors.append("INVALID_CANDIDATE:" + str(exc))
    for key, original in old.items():
        upgraded = new.get(key)
        if upgraded is None:
            candidate_errors.append("REMOVED_BASELINE_COMPONENT:" + key)
        elif (original["provides"] != upgraded["provides"]
              or original["effect_scope"] != upgraded["effect_scope"]):
            candidate_errors.append("BROKE_BASELINE_PUBLIC_CONTRACT:" + key)
    new_fail = candidate.get("historical_fail_ids")
    if (not isinstance(new_fail, list)
            or not all(isinstance(i, str) and i for i in new_fail)
            or not set(old_fail).issubset(set(new_fail))):
        candidate_errors.append("DROPPED_HISTORICAL_FAILURE_LINEAGE")

    if candidate_errors:
        state = "CANDIDATE_HELD_BASELINE_PRESERVED"
    else:
        state = "SOURCE_COHERENT__NOT_MVP"
    return {
        "schema": REPORT_SCHEMA,
        "work_id": manifest["work_id"],
        "baseline_id": baseline["release_id"],
        "candidate_id": candidate["release_id"],
        "baseline_source_verified": True,
        "baseline_source_evidence": old_evidence,
        "candidate_source_evidence": new_evidence,
        "candidate_source_compatible": not candidate_errors,
        "candidate_holds": sorted(set(candidate_errors)),
        "result": state,
        "previous_baseline_preserved": True,
        "claimed_receiver_readproof_accepted": False,
        "qualified_mvp": False,
        "runtime_activation": "NOT_ATTEMPTED",
        "release_actuator": "NONE",
        "next_gate": "INDEPENDENT_RECEIVER_TASK_AND_RECOVERY_PLUS_AUTHORIZED_RELEASE",
        "nonclaims": [
            "GLOBAL_LOCKSTEP_NE_REQUIRED",
            "SOURCE_COHERENCE_NE_MVP",
            "SELF_REPORTED_RECEIVER_NE_INDEPENDENT_ACK",
            "BRANCH_GIT_BLOB_NE_HOST_RUNTIME",
            "CANDIDATE_NE_REPLACEMENT_OF_BASELINE",
            "LOCAL_IS_NOT_LANDED",
        ],
    }


def write_report(directory: Path, result: dict) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=False)
    report = directory / "colockstep.json"
    proof = directory / "receipt.json"
    body = canonical(result)
    report.write_bytes(body)
    receipt = {"schema": "CoCivium.CoLockStep.SourceReceipt.R0",
               "report_sha256": hashlib.sha256(body).hexdigest(),
               "bytes": len(body),
               "status": result["result"],
               "qualified_mvp": False,
               "real_receiver_ack": False}
    proof.write_bytes(canonical(receipt))
    return report, proof


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--repo-root", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        outcome = assess(manifest, args.repo_root)
        report, receipt = write_report(args.out, outcome)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("FAIL_CLOSED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({"state": outcome["result"], "qualified_mvp": False,
                      "report": str(report), "receipt": str(receipt)},
                     sort_keys=True))
    return 0 if outcome["candidate_source_compatible"] else 2


if __name__ == "__main__":
    sys.exit(main())
