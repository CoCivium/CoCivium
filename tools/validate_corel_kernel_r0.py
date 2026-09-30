#!/usr/bin/env python3
import json
import sys
from pathlib import Path

SCHEMA_PATH = Path("schemas/relations/co_rel_kernel_r0.schema.json")
FIXTURE_PATH = Path("fixtures/relations/co_rel_kernel_r0.fixtures.json")

ALLOWED_CAUSAL = {"causal", "non_causal", "possibly_causal", "mixed", "unknown"}
ALLOWED_BOUNDARY = {"internal", "external", "boundary", "unknown_domain"}
NULL_PREDICATES = {
    "EXPECTED_BUT_MISSING",
    "IMPOSSIBLE",
    "FORBIDDEN",
    "UNKNOWN_RELATION",
    "NOT_YET_OBSERVED",
    "ONCE_EXISTED",
    "COUNTERFACTUALLY_PRESENT",
}

def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)

def rel_ref(endpoint):
    if isinstance(endpoint, dict):
        return endpoint.get("rel_ref")
    return None

def main() -> int:
    if not SCHEMA_PATH.exists():
        fail(f"missing schema: {SCHEMA_PATH}")
    if not FIXTURE_PATH.exists():
        fail(f"missing fixtures: {FIXTURE_PATH}")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    required = set(schema.get("required", []))
    expected_required = {"rel_id", "subject", "predicate", "object", "causal_status", "provenance"}
    if not expected_required.issubset(required):
        fail("schema does not require the R0 invariant fields")

    relations = data.get("relations")
    if not isinstance(relations, list) or not relations:
        fail("fixtures.relations must be a non-empty list")

    ids = [r.get("rel_id") for r in relations]
    if any(not x for x in ids):
        fail("every relation must have a non-empty rel_id")
    if len(set(ids)) != len(ids):
        fail("rel_id values must be unique")
    idset = set(ids)

    saw_null = False
    saw_meta = False
    saw_revision = False
    saw_boundary = False

    for r in relations:
        rid = r["rel_id"]
        missing = expected_required - set(r)
        if missing:
            fail(f"{rid}: missing required fields {sorted(missing)}")

        if r["causal_status"] not in ALLOWED_CAUSAL:
            fail(f"{rid}: invalid causal_status {r['causal_status']!r}")

        provenance = r["provenance"]
        if not isinstance(provenance, list) or not provenance or not all(isinstance(x, str) and x for x in provenance):
            fail(f"{rid}: provenance must be a non-empty string list")

        if "confidence" in r and r["confidence"] is not None:
            c = r["confidence"]
            if not isinstance(c, (int, float)) or isinstance(c, bool) or not (0 <= c <= 1):
                fail(f"{rid}: confidence must be in [0, 1]")

        boundary = r.get("boundary")
        if boundary is not None:
            if boundary not in ALLOWED_BOUNDARY:
                fail(f"{rid}: invalid boundary {boundary!r}")
            if boundary == "boundary":
                saw_boundary = True

        for endpoint_name in ("subject", "object"):
            ref = rel_ref(r[endpoint_name])
            if ref is not None:
                saw_meta = True
                if ref not in idset:
                    fail(f"{rid}: {endpoint_name} references unknown relation {ref!r}")

        if r["predicate"] in NULL_PREDICATES:
            saw_null = True
            if r["causal_status"] != "unknown":
                fail(f"{rid}: typed absence relation should use causal_status='unknown' in R0 fixtures")

        prior = r.get("supersedes_rel_id")
        if prior:
            saw_revision = True
            if prior not in idset:
                fail(f"{rid}: supersedes unknown relation {prior!r}")
            for field in ("change_reason", "changed_by", "changed_at"):
                if not r.get(field):
                    fail(f"{rid}: revision missing lineage field {field}")

    if not saw_null:
        fail("fixtures do not exercise typed absence/null relations")
    if not saw_meta:
        fail("fixtures do not exercise relation-on-relation references")
    if not saw_revision:
        fail("fixtures do not exercise lineage-preserving revision")
    if not saw_boundary:
        fail("fixtures do not exercise a boundary-crossing relation")

    print(f"PASS: CoRelKernel R0 contract fixtures validated ({len(relations)} relations)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
