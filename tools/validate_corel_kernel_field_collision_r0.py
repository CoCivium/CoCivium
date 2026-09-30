#!/usr/bin/env python3
import json
import sys
from collections import Counter
from pathlib import Path

PATH = Path("fixtures/relations/co_rel_kernel_field_collision_r0.json")
EXPECTED_IDS = {
    "direct_causal","possible_or_unknown_causal","typed_absence",
    "relation_about_relation","observer_disagreement","time_qualified_contradiction",
    "sibling_revisions","conflict_resolution","projection_loss","transform_lineage"
}
ALLOWED = {"lossless_bounded","lossy","collision_requires_policy","unmappable_without_extension"}

def fail(msg):
    print(f"FAIL: {msg}")
    raise SystemExit(1)

def main():
    if not PATH.exists():
        fail("collision fixture missing")
    data=json.loads(PATH.read_text(encoding="utf-8"))
    cases=data.get("cases")
    if not isinstance(cases,list) or len(cases)!=10:
        fail("expected exactly 10 collision cases")
    ids=[c.get("id") for c in cases]
    if set(ids)!=EXPECTED_IDS or len(ids)!=len(set(ids)):
        fail("collision case identity set mismatch")
    for c in cases:
        if c.get("mapping") not in ALLOWED:
            fail(f"{c.get('id')}: invalid mapping class")
        if not c.get("reason"):
            fail(f"{c.get('id')}: missing reason")
        if "kernel" not in c or "field" not in c:
            fail(f"{c.get('id')}: both candidate projections required")
    counts=Counter(c["mapping"] for c in cases)
    exp=data.get("summary_expectation",{})
    checks={
        "lossless_bounded":exp.get("requires_lossless_or_bounded"),
        "lossy":exp.get("requires_lossy"),
        "collision_requires_policy":exp.get("requires_collision_policy"),
        "unmappable_without_extension":exp.get("requires_unmappable_without_extension")
    }
    for k,v in checks.items():
        if counts[k]!=v:
            fail(f"mapping count mismatch for {k}: {counts[k]} != {v}")
    src=data.get("source_bindings",{})
    if src.get("corel_kernel_pr")!=128 or src.get("corelation_field_pr")!=127:
        fail("source PR bindings drifted")
    if not src.get("corel_kernel_head") or not src.get("corelation_field_head"):
        fail("exact source heads required")
    layers=data.get("candidate_layering",{})
    if not layers.get("kernel_owns") or not layers.get("field_owns"):
        fail("candidate layering must name both ownership sets")
    print("PASS: CoRelKernel x CoRelationField collision fixture validated (10 cases)")
    return 0

if __name__=="__main__":
    sys.exit(main())
