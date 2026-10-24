#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

MATRIX = Path("fixtures/relations/co_rel_kernel_field_collision_r0.json")
ADJ = Path("fixtures/relations/co_rel_kernel_field_adjudication_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git","hash-object",str(path)], text=True).strip()

def canonical_sha(obj):
    data=json.dumps(obj,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest().upper()

matrix=json.loads(MATRIX.read_text(encoding="utf-8"))
adj=json.loads(ADJ.read_text(encoding="utf-8"))
src=adj["source_collision_matrix"]

if git_blob(MATRIX) != src["git_blob_sha"]:
    fail("FAIL_SOURCE_MATRIX_BLOB")
if canonical_sha(matrix) != src["semantic_sha256"]:
    fail("FAIL_SOURCE_MATRIX_SEMANTIC_SHA")

cases={c["case_id"]:c for c in matrix["cases"]}
decisions={d["decision_id"]:d for d in adj["decisions"]}
if set(decisions) != {"D01_CAUSAL_STATUS_LAYERING","D02_ABSENCE_DUAL_LAYERING"}:
    fail("FAIL_DECISION_SET")

d1=decisions["D01_CAUSAL_STATUS_LAYERING"]
d2=decisions["D02_ABSENCE_DUAL_LAYERING"]
if d1["collision_case_id"] not in cases or d2["collision_case_id"] not in cases:
    fail("FAIL_DECISION_CASE_BINDING")
if d1["status"] != "LAYERED_POLICY_RESOLVED" or d2["status"] != "LAYERED_POLICY_RESOLVED":
    fail("FAIL_DECISION_STATUS")

rules={r["kernel_status"]:r for r in d1["rules"]}
if rules["causal"]["field_default"] != "CAUSAL_CANDIDATE":
    fail("FAIL_CAUSAL_DEFAULT_UPGRADE")
if rules["possibly_causal"]["field_default"] != "CAUSAL_CANDIDATE":
    fail("FAIL_POSSIBLE_CAUSAL_MAPPING")
if rules["non_causal"]["field_default"] != "NONCAUSAL":
    fail("FAIL_NONCAUSAL_MAPPING")
if rules["unknown"]["field_default"] != "UNKNOWN_CAUSAL_STATUS":
    fail("FAIL_UNKNOWN_MAPPING")
if rules["mixed"]["field_default"] is not None:
    fail("FAIL_MIXED_MUST_NOT_COERCE")
if "MUST_NOT_BE_INFERRED_FROM_KERNEL_STATUS_ALONE" not in rules["causal"]["upgrade_rule"]:
    fail("FAIL_CAUSAL_SUPPORTED_GUARD")
if "CAUSALITY_NOT_APPLICABLE_MUST_BE_DECIDED_BY_FIELD_RELATION_FAMILY" not in rules["unknown"]["upgrade_rule"]:
    fail("FAIL_NOT_APPLICABLE_GUARD")

absence_rules=set(d2["rules"])
required_absence={
    "DO_NOT_REIFY_EVERY_ABSENCE_PREDICATE_INTO_A_STANDALONE_FIELD_RELATUM",
    "WHEN_AN_ABSENCE_MUST_PARTICIPATE_IN_OTHER_FIELD_RELATIONS_CREATE_A_PROJECTION_SCOPED_ABSENCE_RELATUM_WITH_EXACT_SOURCE_PROVENANCE",
    "PROJECTION_SCOPED_ABSENCE_IDENTITY_MUST_NOT_BE_TREATED_AS_PROOF_OF_AN_INDEPENDENT_ENTITY"
}
if not required_absence.issubset(absence_rules):
    fail("FAIL_ABSENCE_LAYERING_GUARD")

result=adj["result"]
if result["ownership_unresolved_before"] != 2 or result["ownership_unresolved_after"] != 0:
    fail("FAIL_UNRESOLVED_COUNT")
if result["semantic_non_equivalence_remaining"] is not True:
    fail("FAIL_FALSE_EQUIVALENCE")
if result["schema_mutation_required_now"] is not False:
    fail("FAIL_PREMATURE_SCHEMA_MUTATION")

print(json.dumps({
    "STATE":"PASS_COREL_KERNEL_FIELD_ADJUDICATION_R0",
    "source_matrix_semantic_sha256":canonical_sha(matrix),
    "decisions":2,
    "ownership_unresolved_before":2,
    "ownership_unresolved_after":0,
    "semantic_non_equivalence_remaining":True,
    "schema_mutation_required_now":False,
    "rails":[
        "CAUSAL_NE_CAUSAL_SUPPORTED_BY_TRANSLATION",
        "UNKNOWN_NE_CAUSALITY_NOT_APPLICABLE",
        "MIXED_NE_FORCED_SINGLE_FIELD_VALUE",
        "ABSENCE_PREDICATE_NE_ABSENCE_RELATUM",
        "ADJUDICATION_NE_CANON"
    ]
},separators=(",",":")))
