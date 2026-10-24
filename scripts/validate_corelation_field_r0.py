#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator


def fail(code):
    raise ValueError(code)


def validate_document(schema, fixture):
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda e: list(e.absolute_path),
    )
    if errors:
        first = errors[0]
        path = ".".join(str(x) for x in first.absolute_path)
        fail(f"FAIL_SCHEMA:{path}:{first.message}")

    relata = fixture["relata"]
    declared_refs = [r["ref"] for r in relata]
    if len(declared_refs) != len(set(declared_refs)):
        fail("FAIL_DUPLICATE_RELATUM_REF")
    declared_kinds = {r["ref"]: r["kind"] for r in relata}

    relations = fixture["relations"]
    relation_ids = [r["relation_id"] for r in relations]
    if len(relation_ids) != len(set(relation_ids)):
        fail("FAIL_DUPLICATE_RELATION_ID")
    relation_by_id = {r["relation_id"]: r for r in relations}
    relation_id_set = set(relation_ids)

    dependencies = {}
    for relation in relations:
        deps = []
        for relatum in relation["relata"]:
            ref = relatum["ref"]
            if ref not in declared_kinds:
                fail(f"FAIL_UNDECLARED_RELATUM:{relation['relation_id']}:{ref}")
            if declared_kinds[ref] != relatum["kind"]:
                fail(f"FAIL_RELATUM_KIND_MISMATCH:{relation['relation_id']}:{ref}")
            if relatum["kind"] == "RELATION":
                rid = ref.removeprefix("relation:")
                if rid not in relation_id_set:
                    fail(f"FAIL_UNKNOWN_RELATION_RELATUM:{relation['relation_id']}:{rid}")
                deps.append(rid)
        dependencies[relation["relation_id"]] = deps

    # Compute real recursion depth from the relation dependency graph.
    visiting = set()
    depth_cache = {}

    def actual_depth(rid):
        if rid in depth_cache:
            return depth_cache[rid]
        if rid in visiting:
            fail(f"FAIL_RELATION_CYCLE:{rid}")
        visiting.add(rid)
        deps = dependencies[rid]
        depth = 0 if not deps else 1 + max(actual_depth(dep) for dep in deps)
        visiting.remove(rid)
        depth_cache[rid] = depth
        return depth

    max_allowed = fixture["max_relation_depth"]
    for relation in relations:
        rid = relation["relation_id"]
        depth = actual_depth(rid)
        if depth > max_allowed:
            fail(f"FAIL_RELATIONAL_RECURSION_DEPTH:{rid}:{depth}>{max_allowed}")
        if relation["meta_depth"] != depth:
            fail(f"FAIL_META_DEPTH_MISMATCH:{rid}:declared={relation['meta_depth']}:actual={depth}")

    if not any(r["causal_status"] == "CAUSAL_SUPPORTED" and r["mechanism"] for r in relations):
        fail("FAIL_NO_SUPPORTED_CAUSAL_WITH_MECHANISM")
    if not any(r["causal_status"] == "COMMON_CAUSE_CANDIDATE" for r in relations):
        fail("FAIL_NO_COMMON_CAUSE_CANDIDATE")
    if not any(
        r["relation_family"] == "LOGICAL_MATHEMATICAL_CONSTRAINT"
        and r["causal_status"] == "CAUSALITY_NOT_APPLICABLE"
        for r in relations
    ):
        fail("FAIL_LOGICAL_CAUSALITY_SEPARATION")
    if not any(
        r["causal_status"] == "CONSTRAINT_RELATION"
        and any(x["kind"] == "ABSENCE" for x in r["relata"])
        for r in relations
    ):
        fail("FAIL_NO_ABSENCE_CONSTRAINT_CASE")
    if not any(
        any(x["kind"] == "BOUNDARY" for x in r["relata"])
        and any(x["kind"] == "UNKNOWN" for x in r["relata"])
        for r in relations
    ):
        fail("FAIL_NO_OUTSIDE_MODEL_UNKNOWN_CASE")
    if not any(
        r["meta_depth"] >= 2 and r["relation_family"] == "META_RELATIONAL"
        for r in relations
    ):
        fail("FAIL_NO_RELATION_OF_RELATIONS")

    quantum = [r for r in relations if r["relation_family"] == "QUANTUM_EVIDENCE_BOUNDED"]
    if not quantum or any("QUANTUM_CORRELATION_NE_SIGNAL" not in r["nonclaims"] for r in quantum):
        fail("FAIL_QUANTUM_NONSIGNAL_RAIL")

    transform_ids = [t["transform_id"] for t in fixture["transforms"]]
    if len(transform_ids) != len(set(transform_ids)):
        fail("FAIL_DUPLICATE_TRANSFORM_ID")
    for transform in fixture["transforms"]:
        source = set(transform["source_relation_ids"])
        output = set(transform["output_relation_ids"])
        if transform["source_mutated"] is not False:
            fail("FAIL_TRANSFORM_SOURCE_MUTATION")
        if not source.issubset(relation_id_set):
            fail("FAIL_TRANSFORM_UNKNOWN_SOURCE")
        if not output.issubset(relation_id_set):
            fail("FAIL_TRANSFORM_UNKNOWN_OUTPUT")
        if source & output:
            fail(f"FAIL_TRANSFORM_SOURCE_OUTPUT_ALIAS:{transform['transform_id']}")
        if not transform["loss_declarations"]:
            fail("FAIL_TRANSFORM_LOSS_UNDECLARED")

    projection_ids = [p["projection_id"] for p in fixture["projections"]]
    if len(projection_ids) != len(set(projection_ids)):
        fail("FAIL_DUPLICATE_PROJECTION_ID")
    for projection in fixture["projections"]:
        selected = set(projection["selected_relation_ids"])
        omitted = set(projection["omitted_relation_ids"])
        if selected & omitted:
            fail(f"FAIL_PROJECTION_OVERLAP:{projection['projection_id']}")
        if selected | omitted != relation_id_set:
            fail(f"FAIL_PROJECTION_COVERAGE:{projection['projection_id']}")
        if projection["source_mutated"] is not False:
            fail(f"FAIL_PROJECTION_MUTATES_SOURCE:{projection['projection_id']}")
        if not projection["loss_declarations"]:
            fail(f"FAIL_PROJECTION_LOSS_UNDECLARED:{projection['projection_id']}")
        if projection["projection_kind"] == "CAUSAL_CHAIN":
            for rid in selected:
                relation = relation_by_id[rid]
                if relation["relation_family"] != "CAUSAL":
                    fail(f"FAIL_CAUSAL_CHAIN_CONTAINS_NONCAUSAL:{rid}")
                if relation["causal_status"] not in {"CAUSAL_SUPPORTED", "CAUSAL_CANDIDATE"}:
                    fail(f"FAIL_CAUSAL_CHAIN_BAD_STATUS:{rid}")

    return {
        "STATE": "PASS_CORELATION_FIELD_R0_SYNTHETIC_VALIDATION",
        "relations": len(relations),
        "max_meta_depth": max(depth_cache.values(), default=0),
        "transforms": len(fixture["transforms"]),
        "projections": len(fixture["projections"]),
        "projection_coverage": "EXACT_SELECTED_PLUS_OMITTED",
        "source_mutations": 0,
        "rails": [
            "RELATION_NE_CAUSATION",
            "CHAIN_NE_RELATION_FIELD",
            "ABSENCE_NE_NONEXISTENCE",
            "OUTSIDE_MODEL_NE_OUTSIDE_REALITY",
            "QUANTUM_CORRELATION_NE_SIGNAL",
            "PROJECTION_NE_SOURCE",
            "RELATIONAL_RECURSION_REQUIRES_ACYCLIC_DEPTH_PROOF",
            "SOURCE_ID_NE_OUTPUT_ID_WHEN_SOURCE_UNMUTATED",
            "MARMALIZE_REQUIRES_DELTA_PROVENANCE",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", default="schemas/corelation-field-v0.1.schema.json")
    ap.add_argument("--fixture", default="examples/corelation-field-r0.example.json")
    args = ap.parse_args()

    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    try:
        result = validate_document(schema, fixture)
    except ValueError as exc:
        print(json.dumps({"STATE": "FAIL_CORELATION_FIELD_R0", "reason": str(exc)}, separators=(",", ":")))
        raise SystemExit(1)
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
