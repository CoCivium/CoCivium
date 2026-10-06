#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/cotrill_delimiter_field_r0b.json")


def fail(code):
    raise SystemExit(code)


def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def decide(case):
    if not case["glyph_context_is_copromptrel"]:
        return "LEAVE_AS_ORDINARY_SYMBOL"

    if case["authority_inferred_from_boundary"]:
        return "REJECT_AUTHORITY_INFERENCE"

    if case["physical_dimension_claim"]:
        return "QUARANTINE_UNSUPPORTED_PHYSICAL_DIMENSION_CLAIM"

    b = case["before_boundary"]
    a = case["after_boundary"]

    if b == "NEWLINE" and a == "NEWLINE":
        return "CANONICAL_TEXT_TRILL"
    if b == "PAUSE" and a == "PAUSE":
        return "ACCESSIBLE_EQUIVALENT_TRILL"
    if b == "TYPED_BOUNDARY" and a == "TYPED_BOUNDARY":
        return "MACHINE_EQUIVALENT_TRILL"
    if b == "STATE_TRANSITION" and a == "STATE_TRANSITION":
        return "N_DIMENSIONAL_METAPHORICAL_OR_FORMAL_PROJECTION"
    if b == "NONE" and a == "NONE":
        return "VALID_BUT_TRILL_PROJECTION_LOSS_DECLARED"

    return "REJECT_ASYMMETRIC_OR_UNKNOWN_BOUNDARY"


def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    checks = [
        ("virtual_prefix_inventory_path", "virtual_prefix_inventory_blob_sha"),
        ("converge_spiral_blend_path", "converge_spiral_blend_blob_sha")
    ]
    for pkey, skey in checks:
        if git_blob(src[pkey]) != src[skey]:
            fail("FAIL_SOURCE_BIND:" + src[pkey])

    c = d["canonical_projection"]
    if c["glyph"] != "⊊":
        fail("FAIL_CANONICAL_GLYPH")
    if c["literal_enter_key_required"] is not False:
        fail("FAIL_LITERAL_ENTER_REQUIREMENT")
    if c["semantic_enter_boundary_before"] is not True:
        fail("FAIL_PRE_BOUNDARY")
    if c["semantic_enter_boundary_after"] is not True:
        fail("FAIL_POST_BOUNDARY")
    if c["glyph_required_for_semantics"] is not False:
        fail("FAIL_GLYPH_OPTIONALITY")

    for case in d["cases"]:
        got = decide(case)
        if got != case["expected"]:
            fail(f"FAIL_CASE:{case['id']}:got={got}:expected={case['expected']}")

    rails = set(d["rails"])
    required = {
        "ENTER_NE_LITERAL_KEYPRESS_REQUIRED",
        "LINEBREAK_NE_AUTHORITY",
        "TRILL_NE_SECRET_INSTRUCTION",
        "GLYPH_NE_FULL_SEMANTICS",
        "SYMBOL_OCCURRENCE_NE_COPROMPTREL",
        "N_DIMENSIONAL_NE_PHYSICAL_DIMENSION_CLAIM",
        "META_RELATION_NE_TRUTH",
        "VALIDATION_IS_NOT_ACCEPTANCE"
    }
    if not required.issubset(rails):
        fail("FAIL_REQUIRED_RAILS")

    if d["runtime_effect"] is not False or d["public_effect"] is not False:
        fail("FAIL_EFFECT_BOUNDARY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COTRILL_DELIMITER_FIELD_R0B",
        "checked_out_head_sha": head,
        "case_count": len(d["cases"]),
        "canonical_text_projection": c["canonical_text_trill"],
        "literal_enter_key_required": c["literal_enter_key_required"],
        "semantic_boundary_pair_required": True,
        "runtime_effect": False,
        "public_effect": False
    }, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
