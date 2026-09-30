#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

MATRIX_PATH = Path("fixtures/relations/co_rel_kernel_field_collision_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob_sha(ref, path):
    out = subprocess.check_output(["git", "rev-parse", f"{ref}:{path}"], text=True).strip()
    return out

def git_json(ref, path):
    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"])
    return json.loads(raw.decode("utf-8"))

def refs_from_kernel(fixture):
    return {r["rel_id"] for r in fixture["relations"]}

def refs_from_field(fixture):
    refs = {r["relation_id"] for r in fixture["relations"]}
    refs |= {p["projection_id"] for p in fixture["projections"]}
    refs |= {t["transform_id"] for t in fixture["transforms"]}
    return refs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-ref", required=True)
    args = ap.parse_args()

    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    ks = matrix["sources"]["corel_kernel"]
    fs = matrix["sources"]["corelation_field"]

    kernel_schema_blob = git_blob_sha("HEAD", ks["schema_path"])
    kernel_fixture_blob = git_blob_sha("HEAD", ks["fixture_path"])
    if kernel_schema_blob != ks["schema_blob_sha"]:
        fail("FAIL_KERNEL_SCHEMA_BLOB_DRIFT")
    if kernel_fixture_blob != ks["fixture_blob_sha"]:
        fail("FAIL_KERNEL_FIXTURE_BLOB_DRIFT")

    actual_field_head = subprocess.check_output(["git", "rev-parse", args.field_ref], text=True).strip()
    if actual_field_head != fs["frozen_head"]:
        fail("FAIL_FIELD_FROZEN_HEAD_MISMATCH")

    field_schema_blob = git_blob_sha(args.field_ref, fs["schema_path"])
    field_fixture_blob = git_blob_sha(args.field_ref, fs["fixture_path"])
    if field_schema_blob != fs["schema_blob_sha"]:
        fail("FAIL_FIELD_SCHEMA_BLOB_DRIFT")
    if field_fixture_blob != fs["fixture_blob_sha"]:
        fail("FAIL_FIELD_FIXTURE_BLOB_DRIFT")

    kernel_fixture = json.loads(Path(ks["fixture_path"]).read_text(encoding="utf-8"))
    field_fixture = git_json(args.field_ref, fs["fixture_path"])

    kernel_refs = refs_from_kernel(kernel_fixture)
    field_refs = refs_from_field(field_fixture)

    allowed_classes = set(matrix["mapping_classes"])
    allowed_owners = set(matrix["ownership_candidates"])
    seen_ids = set()
    counts = {k: 0 for k in allowed_classes}
    unresolved = 0

    for case in matrix["cases"]:
        cid = case["case_id"]
        if cid in seen_ids:
            fail("FAIL_DUPLICATE_CASE_ID:" + cid)
        seen_ids.add(cid)

        mapping_class = case["mapping_class"]
        owner = case["ownership_candidate"]
        if mapping_class not in allowed_classes:
            fail("FAIL_UNKNOWN_MAPPING_CLASS:" + cid)
        if owner not in allowed_owners:
            fail("FAIL_UNKNOWN_OWNERSHIP:" + cid)

        unknown_kernel = set(case["kernel_refs"]) - kernel_refs
        unknown_field = set(case["field_refs"]) - field_refs
        if unknown_kernel:
            fail("FAIL_UNKNOWN_KERNEL_REF:" + cid + ":" + ",".join(sorted(unknown_kernel)))
        if unknown_field:
            fail("FAIL_UNKNOWN_FIELD_REF:" + cid + ":" + ",".join(sorted(unknown_field)))

        if mapping_class in {"OVERLAP_LOSSY", "VOCABULARY_COLLISION", "NON_EQUIVALENT_ENCODING"}:
            if not case["kernel_refs"] or not case["field_refs"]:
                fail("FAIL_CROSS_CANDIDATE_CASE_MISSING_SIDE:" + cid)
        if mapping_class == "KERNEL_ONLY_R0" and (not case["kernel_refs"] or case["field_refs"]):
            fail("FAIL_KERNEL_ONLY_SHAPE:" + cid)
        if mapping_class == "FIELD_ONLY_R0" and (case["kernel_refs"] or not case["field_refs"]):
            fail("FAIL_FIELD_ONLY_SHAPE:" + cid)

        if not case["losses"]:
            fail("FAIL_UNDECLARED_COLLISION_LOSS:" + cid)
        if owner == "UNRESOLVED":
            unresolved += 1
        counts[mapping_class] += 1

    expected = matrix["summary_expectations"]
    if len(matrix["cases"]) != expected["case_count"]:
        fail("FAIL_CASE_COUNT")
    if expected["lossless_case_count"] != 0:
        fail("FAIL_R0_MUST_NOT_PREDECLARE_LOSSLESS_MAPPING")
    if counts["KERNEL_ONLY_R0"] != expected["kernel_only_case_count"]:
        fail("FAIL_KERNEL_ONLY_COUNT")
    if counts["FIELD_ONLY_R0"] != expected["field_only_case_count"]:
        fail("FAIL_FIELD_ONLY_COUNT")
    if unresolved != expected["unresolved_case_count"]:
        fail("FAIL_UNRESOLVED_COUNT")

    canonical = json.dumps(matrix, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest().upper()
    print(json.dumps({
        "STATE": "PASS_COREL_KERNEL_FIELD_COLLISION_R0",
        "case_count": len(matrix["cases"]),
        "lossless_case_count": 0,
        "counts": counts,
        "unresolved": unresolved,
        "kernel_schema_blob": kernel_schema_blob,
        "kernel_fixture_blob": kernel_fixture_blob,
        "field_head": actual_field_head,
        "field_schema_blob": field_schema_blob,
        "field_fixture_blob": field_fixture_blob,
        "matrix_semantic_sha256": digest,
        "rails": [
            "PARALLEL_SCHEMA_NE_DESIRED_ENDSTATE",
            "MAPPING_NE_EQUIVALENCE",
            "NEWEST_NE_WINNER",
            "GREEN_CI_NE_COLLISION_RESOLUTION"
        ]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
