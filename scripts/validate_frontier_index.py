"""Validate CoAll public frontier index without granting it runtime authority.

Usage: python scripts/validate_frontier_index.py
       python scripts/validate_frontier_index.py path/to/index.json
"""
import json
import pathlib
import sys

DEFAULT = pathlib.Path(__file__).resolve().parents[1] / "docs/Evolution/FRONTIER_EVIDENCE_INDEX_R0.json"
STATES = {"proposed", "source_committed", "tests_executed", "independently_observed", "released"}
REQUIRED = {"receiver-evidence", "x2-coorb-ux", "runtime-recovery",
            "conav-coregroup", "comvp-colockstep", "coprimath-gdside",
            "costead-onboarding"}


def validate(data):
    problems = []
    if data.get("schema") != "cocivium.frontier-index.r0":
        problems.append("unexpected schema")
    fronts = data.get("fronts")
    if not isinstance(fronts, list):
        return ["fronts must be an array"]
    ids = []
    for i, front in enumerate(fronts):
        if not isinstance(front, dict):
            problems.append(f"front[{i}] must be object")
            continue
        ident = front.get("id")
        if not isinstance(ident, str) or not ident.strip():
            problems.append(f"front[{i}] missing id")
            continue
        ids.append(ident)
        if front.get("status") not in STATES:
            problems.append(f"{ident}: invalid status")
        if not isinstance(front.get("next_gate"), str) or not front["next_gate"].strip():
            problems.append(f"{ident}: missing next gate")
        blocked = front.get("blocked_claims")
        if not isinstance(blocked, list) or any(not isinstance(x, str) or not x for x in blocked):
            problems.append(f"{ident}: blocked claims must be string array")
        if front.get("status") == "tests_executed":
            receipt = front.get("test_receipt", {})
            if not isinstance(receipt, dict) or not all(receipt.get(k) for k in ("run_id", "source_sha", "conclusion", "scope", "source_receipt_url")):
                problems.append(f"{ident}: tests_executed requires scoped test receipt")
    if len(ids) != len(set(ids)):
        problems.append("duplicate front IDs")
    for missing in sorted(REQUIRED - set(ids)):
        problems.append(f"missing tracked front: {missing}")
    return problems


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    data = json.loads(path.read_text(encoding="utf-8"))
    problems = validate(data)
    if problems:
        for p in problems:
            print("FAIL:", p)
        return 1
    print(f"PASS: {len(data['fronts'])} fronts retain required evidence gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
