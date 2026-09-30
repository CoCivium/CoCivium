#!/usr/bin/env python3
import json
import sys
from pathlib import Path

SCHEMA_PATH = Path("schemas/relations/co_rel_kernel_r0.schema.json")
FIXTURE_PATH = Path("fixtures/relations/co_rel_kernel_r0.fixtures.json")
ADVERSARIAL_PATH = Path("fixtures/relations/co_rel_kernel_r0.adversarial.json")

ALLOWED_CAUSAL = {"causal", "non_causal", "possibly_causal", "mixed", "unknown"}
ALLOWED_BOUNDARY = {"internal", "external", "boundary", "unknown_domain"}
NULL_PREDICATES = {
    "EXPECTED_BUT_MISSING", "IMPOSSIBLE", "FORBIDDEN", "UNKNOWN_RELATION",
    "NOT_YET_OBSERVED", "ONCE_EXISTED", "COUNTERFACTUALLY_PRESENT",
}
REQUIRED = {"rel_id", "subject", "predicate", "object", "causal_status", "provenance"}

class ContractError(ValueError):
    pass

def rel_ref(endpoint):
    return endpoint.get("rel_ref") if isinstance(endpoint, dict) else None

def reject_supersession_cycles(relations):
    parent = {
        r["rel_id"]: r.get("supersedes_rel_id")
        for r in relations
        if r.get("supersedes_rel_id")
    }
    for start in parent:
        seen = set()
        cur = start
        while cur in parent:
            if cur in seen:
                raise ContractError(f"{start}: supersession cycle detected")
            seen.add(cur)
            cur = parent[cur]

def validate_relations(relations, require_coverage=False):
    if not isinstance(relations, list) or not relations:
        raise ContractError("relations must be a non-empty list")

    ids = [r.get("rel_id") for r in relations]
    if any(not x for x in ids):
        raise ContractError("every relation must have a non-empty rel_id")
    if len(set(ids)) != len(ids):
        raise ContractError("rel_id values must be unique")
    idset = set(ids)

    saw_null = saw_meta = saw_revision = saw_boundary = False

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

    reject_supersession_cycles(relations)

    if require_coverage:
        if not saw_null:
            raise ContractError("fixtures do not exercise typed absence/null relations")
        if not saw_meta:
            raise ContractError("fixtures do not exercise relation-on-relation references")
        if not saw_revision:
            raise ContractError("fixtures do not exercise lineage-preserving revision")
        if not saw_boundary:
            raise ContractError("fixtures do not exercise a boundary-crossing relation")

def main():
    for path in (SCHEMA_PATH, FIXTURE_PATH, ADVERSARIAL_PATH):
        if not path.exists():
            print(f"FAIL: missing required file: {path}")
            return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    if not REQUIRED.issubset(required):
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
