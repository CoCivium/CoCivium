#!/usr/bin/env python3
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SCHEMA_PATH = Path("schemas/relations/co_rel_kernel_r0.schema.json")
FIXTURE_PATH = Path("fixtures/relations/co_rel_kernel_r0.fixtures.json")
ADVERSARIAL_PATH = Path("fixtures/relations/co_rel_kernel_r0.adversarial.json")

ALLOWED_CAUSAL = {"causal", "non_causal", "possibly_causal", "mixed", "unknown"}
ALLOWED_BOUNDARY = {"internal", "external", "boundary", "unknown_domain"}
ALLOWED_CONFLICT = {"unresolved", "resolved", "superseded", "not_applicable"}
ALLOWED_CONTRADICTION = {"observer_relative", "temporal_overlap", "scope_relative", "evidence_conflict", "logical_conflict"}
NULL_PREDICATES = {
    "EXPECTED_BUT_MISSING", "IMPOSSIBLE", "FORBIDDEN", "UNKNOWN_RELATION",
    "NOT_YET_OBSERVED", "ONCE_EXISTED", "COUNTERFACTUALLY_PRESENT",
}
REQUIRED = {"rel_id", "subject", "predicate", "object", "causal_status", "provenance"}

class ContractError(ValueError):
    pass

def rel_ref(endpoint):
    return endpoint.get("rel_ref") if isinstance(endpoint, dict) else None

def parse_time(value, rid, field):
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ContractError(f"{rid}: time.{field} must be a non-empty date-time string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{rid}: invalid time.{field} date-time") from exc

def validate_time(r):
    t = r.get("time")
    if t is None:
        return
    if not isinstance(t, dict):
        raise ContractError(f"{r['rel_id']}: time must be an object or null")
    start = parse_time(t.get("valid_from"), r["rel_id"], "valid_from")
    end = parse_time(t.get("valid_to"), r["rel_id"], "valid_to")
    parse_time(t.get("observed_at"), r["rel_id"], "observed_at")
    if start is not None and end is not None and start > end:
        raise ContractError(f"{r['rel_id']}: time.valid_from must be <= time.valid_to")

def validity_interval(r):
    t = r.get("time") or {}
    start = parse_time(t.get("valid_from"), r["rel_id"], "valid_from")
    end = parse_time(t.get("valid_to"), r["rel_id"], "valid_to")
    return start, end

def intervals_overlap(a, b):
    a0, a1 = validity_interval(a)
    b0, b1 = validity_interval(b)
    if None in (a0, a1, b0, b1):
        return False
    return max(a0, b0) <= min(a1, b1)

def reject_supersession_cycles(relations):
    parent = {r["rel_id"]: r.get("supersedes_rel_id") for r in relations if r.get("supersedes_rel_id")}
    for start in parent:
        seen = set()
        cur = start
        while cur in parent:
            if cur in seen:
                raise ContractError(f"{start}: supersession cycle detected")
            seen.add(cur)
            cur = parent[cur]

def conflict_members(relations):
    members = defaultdict(set)
    for r in relations:
        cid = r.get("conflict_set_id")
        if cid:
            members[cid].add(r["rel_id"])
    return members

def validate_sibling_conflicts(relations):
    siblings = defaultdict(list)
    for r in relations:
        prior = r.get("supersedes_rel_id")
        if prior:
            siblings[prior].append(r)
    for prior, children in siblings.items():
        if len(children) < 2:
            continue
        if any(not r.get("conflict_set_id") or not r.get("conflict_status") for r in children):
            raise ContractError(f"{prior}: concurrent sibling revisions require conflict metadata")
        set_ids = {r["conflict_set_id"] for r in children}
        if len(set_ids) != 1:
            raise ContractError(f"{prior}: sibling revisions must share one conflict_set_id")

def validate_resolutions(relations):
    members = conflict_members(relations)
    for r in relations:
        resolves = r.get("resolves_conflict_set_id")
        if not resolves:
            continue
        if r.get("predicate") != "RESOLVES_CONFLICT":
            raise ContractError(f"{r['rel_id']}: resolves_conflict_set_id requires predicate RESOLVES_CONFLICT")
        if resolves not in members:
            raise ContractError(f"{r['rel_id']}: resolves unknown conflict_set_id {resolves!r}")
        target = rel_ref(r.get("object"))
        if not target or target not in members[resolves]:
            raise ContractError(f"{r['rel_id']}: resolution target must belong to conflict set {resolves!r}")
        if not r.get("resolution_note"):
            raise ContractError(f"{r['rel_id']}: conflict resolution requires resolution_note")

def validate_contradictions(relations):
    by_id = {r["rel_id"]: r for r in relations}
    for r in relations:
        if r.get("predicate") != "CONTRADICTS":
            continue
        basis = r.get("contradiction_basis")
        if not basis:
            raise ContractError(f"{r['rel_id']}: CONTRADICTS requires contradiction_basis")
        if basis not in ALLOWED_CONTRADICTION:
            raise ContractError(f"{r['rel_id']}: invalid contradiction_basis {basis!r}")

        left_id = rel_ref(r.get("subject"))
        right_id = rel_ref(r.get("object"))

        if basis in {"observer_relative", "temporal_overlap"}:
            if not left_id or not right_id:
                raise ContractError(f"{r['rel_id']}: {basis} contradiction requires two relation references")
            left = by_id[left_id]
            right = by_id[right_id]

            if basis == "observer_relative":
                if not left.get("observer") or not right.get("observer") or left["observer"] == right["observer"]:
                    raise ContractError(f"{r['rel_id']}: observer_relative contradiction requires distinct observers")

            if basis == "temporal_overlap" and not intervals_overlap(left, right):
                raise ContractError(f"{r['rel_id']}: temporal_overlap contradiction requires overlapping validity intervals")

def validate_relations(relations, require_coverage=False):
    if not isinstance(relations, list) or not relations:
        raise ContractError("relations must be a non-empty list")
    ids = [r.get("rel_id") for r in relations]
    if any(not x for x in ids):
        raise ContractError("every relation must have a non-empty rel_id")
    if len(set(ids)) != len(ids):
        raise ContractError("rel_id values must be unique")
    idset = set(ids)
    saw_null = saw_meta = saw_revision = saw_boundary = saw_conflict = saw_resolution = saw_qualified_contradiction = False

    for r in relations:
        rid = r["rel_id"]
        missing = REQUIRED - set(r)
        if missing:
            raise ContractError(f"{rid}: missing required fields {sorted(missing)}")
        if r["causal_status"] not in ALLOWED_CAUSAL:
            raise ContractError(f"{rid}: invalid causal_status {r['causal_status']!r}")
        provenance = r["provenance"]
        if not isinstance(provenance, list) or not provenance or not all(isinstance(x, str) and x for x in provenance):
            raise ContractError(f"{rid}: provenance must be a non-empty string list")
        if "confidence" in r and r["confidence"] is not None:
            c = r["confidence"]
            if not isinstance(c, (int, float)) or isinstance(c, bool) or not (0 <= c <= 1):
                raise ContractError(f"{rid}: confidence must be in [0, 1]")
        validate_time(r)
        boundary = r.get("boundary")
        if boundary is not None:
            if boundary not in ALLOWED_BOUNDARY:
                raise ContractError(f"{rid}: invalid boundary {boundary!r}")
            saw_boundary |= boundary == "boundary"
        for endpoint_name in ("subject", "object"):
            ref = rel_ref(r[endpoint_name])
            if ref is not None:
                saw_meta = True
                if ref not in idset:
                    raise ContractError(f"{rid}: {endpoint_name} references unknown relation {ref!r}")
        if r["predicate"] == "CONTRADICTS" and r.get("contradiction_basis"):
            saw_qualified_contradiction = True
        if r["predicate"] in NULL_PREDICATES:
            saw_null = True
            if r["causal_status"] != "unknown":
                raise ContractError(f"{rid}: typed absence relation should use causal_status='unknown' in R0 fixtures")
        prior = r.get("supersedes_rel_id")
        if prior:
            saw_revision = True
            if prior not in idset:
                raise ContractError(f"{rid}: supersedes unknown relation {prior!r}")
            for field in ("change_reason", "changed_by", "changed_at"):
                if not r.get(field):
                    raise ContractError(f"{rid}: revision missing lineage field {field}")
        if r.get("conflict_set_id") or r.get("conflict_status"):
            saw_conflict = True
            if not r.get("conflict_set_id") or not r.get("conflict_status"):
                raise ContractError(f"{rid}: conflict metadata must include conflict_set_id and conflict_status")
            if r["conflict_status"] not in ALLOWED_CONFLICT:
                raise ContractError(f"{rid}: invalid conflict_status {r['conflict_status']!r}")
        if r.get("resolves_conflict_set_id"):
            saw_resolution = True

    reject_supersession_cycles(relations)
    validate_sibling_conflicts(relations)
    validate_resolutions(relations)
    validate_contradictions(relations)

    if require_coverage:
        if not saw_null:
            raise ContractError("fixtures do not exercise typed absence/null relations")
        if not saw_meta:
            raise ContractError("fixtures do not exercise relation-on-relation references")
        if not saw_revision:
            raise ContractError("fixtures do not exercise lineage-preserving revision")
        if not saw_boundary:
            raise ContractError("fixtures do not exercise a boundary-crossing relation")
        if not saw_conflict:
            raise ContractError("fixtures do not exercise explicit concurrent revision conflict")
        if not saw_resolution:
            raise ContractError("fixtures do not exercise explicit conflict resolution")
        if not saw_qualified_contradiction:
            raise ContractError("fixtures do not exercise qualified contradiction semantics")

def main():
    for path in (SCHEMA_PATH, FIXTURE_PATH, ADVERSARIAL_PATH):
        if not path.exists():
            print(f"FAIL: missing required file: {path}")
            return 1
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if not REQUIRED.issubset(set(schema.get("required", []))):
        print("FAIL: schema does not require the R0 invariant fields")
        return 1
    positive = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    try:
        validate_relations(positive.get("relations"), require_coverage=True)
    except ContractError as exc:
        print(f"FAIL: positive fixtures rejected: {exc}")
        return 1
    adversarial = json.loads(ADVERSARIAL_PATH.read_text(encoding="utf-8"))
    cases = adversarial.get("cases")
    if not isinstance(cases, list) or not cases:
        print("FAIL: adversarial cases must be a non-empty list")
        return 1
    for case in cases:
        case_id = case.get("id", "<unnamed>")
        expected = case.get("expected_error", "")
        try:
            validate_relations(case.get("relations"), require_coverage=False)
        except ContractError as exc:
            if expected not in str(exc):
                print(f"FAIL: {case_id}: wrong rejection: {exc}")
                return 1
        else:
            print(f"FAIL: {case_id}: malformed fixture was accepted")
            return 1
    print(f"PASS: CoRelKernel R0 positive fixtures + {len(cases)} adversarial cases validated")
    return 0

if __name__ == "__main__":
    sys.exit(main())
