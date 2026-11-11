#!/usr/bin/env python3
"""Fail-closed, source-only checks for the EXISTING public CoAll frontier index.

No network calls, tasks, model effects, release promotion or receiver ACK.
The seven initial fronts are a regression floor, NOT a complete inventory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re

INDEX = "docs/Evolution/FRONTIER_EVIDENCE_INDEX_R0.json"
SCHEMA = "cocivium.frontier-index.r0"
STATES = (
    "proposed", "source_committed", "tests_executed",
    "independently_observed", "released",
)
INITIAL_FRONTS = frozenset({
    "receiver-evidence", "x2-coorb-ux", "runtime-recovery",
    "conav-coregroup", "comvp-colockstep", "coprimath-gdside",
    "costead-onboarding",
})
ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
CLAIM = re.compile(r"[A-Z][A-Z0-9_]*\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
RUN = re.compile(r"[1-9][0-9]*\Z")


class Hold(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Hold(reason)


def nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def source_exists(root: Path, relative: str) -> bool:
    if not nonempty(relative) or "\\" in relative:
        return False
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in ("..", ".") for part in path.parts):
        return False
    target = root
    for part in path.parts:
        target = target / part
        if target.is_symlink():
            return False
    if not target.exists():
        return False
    if relative.endswith("/"):
        return target.is_dir() and any(p.is_file() for p in target.iterdir())
    return target.is_file()


def validate(index: dict, root: Path) -> dict:
    require(isinstance(index, dict), "HOLD_NOT_OBJECT")
    require(index.get("schema") == SCHEMA, "HOLD_SCHEMA")
    require(index.get("promotion_states") == list(STATES), "HOLD_STATES")
    for key in ("purpose", "authority", "change_policy"):
        require(nonempty(index.get(key)), "HOLD_MISSING_" + key.upper())
    rules = index.get("rules")
    require(isinstance(rules, dict)
            and rules.get("no_inferred_pass") is True
            and rules.get("no_self_certified_effect") is True
            and nonempty(rules.get("no_silent_drop")),
            "HOLD_TRUST_RAILS")
    fronts = index.get("fronts")
    require(isinstance(fronts, list) and 0 < len(fronts) <= 256,
            "HOLD_FRONT_SET")
    seen = set()
    result = {}
    for front in fronts:
        require(isinstance(front, dict), "HOLD_FRONT_OBJECT")
        fid = front.get("id")
        require(isinstance(fid, str) and bool(ID.fullmatch(fid)),
                "HOLD_FRONT_ID")
        require(fid not in seen, "HOLD_DUPLICATE_FRONT")
        seen.add(fid)
        status = front.get("status")
        require(status in STATES, "HOLD_UNKNOWN_PROMOTION_STATE")
        require(nonempty(front.get("next_gate")), "HOLD_MISSING_NEXT_GATE")
        blocked = front.get("blocked_claims")
        require(isinstance(blocked, list) and bool(blocked)
                and len(blocked) == len(set(str(x) for x in blocked))
                and all(isinstance(x, str) and bool(CLAIM.fullmatch(x)) for x in blocked),
                "HOLD_BLOCKED_CLAIMS")
        for field in ("source", "workflow"):
            if field in front:
                require(source_exists(root, front[field]),
                        "HOLD_INVALID_" + field.upper() + "_POINTER")
        if STATES.index(status) >= STATES.index("source_committed"):
            require("source" in front, "HOLD_PROMOTED_WITHOUT_SOURCE")
        if STATES.index(status) >= STATES.index("tests_executed"):
            proof = front.get("test_receipt")
            require(isinstance(proof, dict)
                    and isinstance(proof.get("run_id"), (str, int))
                    and bool(RUN.fullmatch(str(proof["run_id"])))
                    and isinstance(proof.get("source_sha"), str)
                    and bool(SHA.fullmatch(proof["source_sha"]))
                    and proof.get("conclusion") == "success"
                    and nonempty(proof.get("scope")),
                    "HOLD_UNGROUNDED_TEST_STATUS")
        if STATES.index(status) >= STATES.index("independently_observed"):
            receiver = front.get("receiver_readproof")
            require(isinstance(receiver, dict)
                    and nonempty(receiver.get("observer"))
                    and nonempty(receiver.get("source_ref"))
                    and nonempty(receiver.get("readproof_ref")),
                    "HOLD_NO_INDEPENDENT_READPROOF")
        if status == "released":
            receipt = front.get("release_receipt")
            require(isinstance(receipt, dict)
                    and nonempty(receipt.get("release_ref"))
                    and nonempty(receipt.get("receiver_acceptance_ref")),
                    "HOLD_NO_RELEASE_ACCEPTANCE")
        result[fid] = front
    require(INITIAL_FRONTS.issubset(seen), "HOLD_BASELINE_FRONT_DROPPED")
    return {
        "state": "PASS_SOURCE_INDEX_CONTRACT_ONLY",
        "front_count": len(fronts),
        "baseline_count": len(INITIAL_FRONTS),
        "current_source_pointers": sorted(
            fid for fid, f in result.items() if "source" in f
        ),
        "real_receiver_acceptance": "NOT_EVALUATED",
        "cross_session_sync": "NOT_EVALUATED",
        "all_project_coverage": "NOT_ESTABLISHED",
    }


def validate_continuity(previous: dict, current: dict) -> dict:
    """Compare the actual prior Git revision; no removal without retained tombstone.

    A resolved blocked claim requires a separately reviewable evidence pointer,
    but this static checker cannot authenticate that pointer by itself.
    """
    require(isinstance(previous, dict) and isinstance(current, dict),
            "HOLD_BAD_PREDECESSOR")
    old = {f["id"]: f for f in previous["fronts"]}
    new = {f["id"]: f for f in current["fronts"]}
    require(set(old).issubset(new), "HOLD_SILENT_FRONT_REMOVAL")
    for fid, earlier in old.items():
        now = new[fid]
        removed = set(earlier["blocked_claims"]) - set(now["blocked_claims"])
        if not removed:
            continue
        resolutions = now.get("claim_resolutions", [])
        require(isinstance(resolutions, list), "HOLD_MALFORMED_RESOLUTIONS")
        attested = {
            r.get("claim")
            for r in resolutions if isinstance(r, dict)
            and nonempty(r.get("evidence_ref"))
            and nonempty(r.get("verifier_ref"))
            and nonempty(r.get("observed_at"))
        }
        require(removed.issubset(attested), "HOLD_SILENT_BLOCKER_REMOVAL")
    return {
        "state": "PASS_SOURCE_PREDECESSOR_COMPARISON_ONLY",
        "retained_fronts": len(old),
        "new_fronts": len(new) - len(old),
        "verified_external_effects": "NOT_EVALUATED",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--index", default=INDEX)
    p.add_argument("--prior")
    args = p.parse_args()
    root = Path(args.root).resolve()
    current = json.loads((root / args.index).read_text(encoding="utf-8"))
    result = validate(current, root)
    if args.prior:
        previous = json.loads(Path(args.prior).read_text(encoding="utf-8"))
        validate(previous, root)
        result["predecessor"] = validate_continuity(previous, current)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
