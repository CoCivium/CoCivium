#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/covirtual_substrate_prefix_inventory_r0.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))

    pp = d["prefix_policy"]
    if pp["canonical_glyph"] != "⊊":
        fail("FAIL_CANONICAL_GLYPH")
    if pp["glyph_required_for_semantics"] is not False:
        fail("FAIL_GLYPH_BECAME_SEMANTIC_DEPENDENCY")
    if pp["glyph_grants_authority"] is not False:
        fail("FAIL_GLYPH_AUTHORITY")
    if pp["hidden_prefix_must_remain_inspectable"] is not True:
        fail("FAIL_HIDDEN_PREFIX_AUDITABILITY")

    examples = d["prompt_relation"]["synthetic_examples"]
    if len(examples) != 4:
        fail("FAIL_PROMPT_EXAMPLE_COUNT")
    for e in examples:
        if e["authority_before"] != e["authority_after"]:
            fail("FAIL_PREFIX_AUTHORITY_DRIFT:" + e["id"])

    exp = {e["id"]: e["expected"] for e in examples}
    if exp["P01_STRICT_SUBSET_PREFIX"] != "CANONICAL_PREFIX_VALID":
        fail("FAIL_P01")
    if exp["P02_NO_GLYPH_STILL_RELATIONAL"] != "RELATION_SEMANTICS_VALID_WITHOUT_GLYPH":
        fail("FAIL_P02")
    if exp["P03_GLYPH_CANNOT_WIDEN_AUTHORITY"] != "PREFIX_NE_AUTHORITY":
        fail("FAIL_P03")
    if exp["P04_AMBIGUOUS_ALIAS"] != "ALIAS_DISPLAY_ONLY__STRICTNESS_UNPROVEN":
        fail("FAIL_P04")

    inv = d["inventory"]
    if inv["shape"] != "RELATIONAL_INDEX_OF_BOUNDED_INVENTORY_SHARDS":
        fail("FAIL_INVENTORY_SHAPE")
    if inv["coverage_state"] != "PARTIAL_EXPLICIT_BOUNDARY":
        fail("FAIL_COVERAGE_STATE")
    if inv["inventory_inclusion_promotes_lifecycle"] is not False:
        fail("FAIL_INVENTORY_PROMOTION")
    if inv["inventory_claims_complete_history"] is not False:
        fail("FAIL_COMPLETE_HISTORY_CLAIM")
    if inv["hidden_from_default_ux_means_unavailable_to_audit"] is not False:
        fail("FAIL_AUDIT_VISIBILITY")

    classes = {s["class"] for s in inv["shards"]}
    required_classes = {
        "RELATIONS", "QUESTIONS", "RECEIPTS", "BUDGETS",
        "NEGATIVE_KNOWLEDGE", "WAKE_CONDITIONS",
        "STALE_OR_RETIRED", "UNKNOWN_OR_UNSCANNED"
    }
    if not required_classes.issubset(classes):
        fail("FAIL_INVENTORY_CLASSES")

    records = inv["object_records"]
    if len(records) != 2:
        fail("FAIL_OBJECT_RECORD_COUNT")
    by_id = {r["Identity"]: r for r in records}
    a = by_id["obj:verified-only"]
    b = by_id["obj:duplicate-candidate"]
    if a["LifecycleState"] != "VERIFIED_LOCAL" or b["LifecycleState"] != "VERIFIED_LOCAL":
        fail("FAIL_LIFECYCLE_DRIFT")
    if a["ContentHash"] != b["ContentHash"]:
        fail("FAIL_DUPLICATE_FIXTURE_HASH")
    if b["DuplicateOf"] != "obj:verified-only":
        fail("FAIL_DUPLICATE_RELATION")
    if b["Supersedes"] is not None:
        fail("FAIL_DUPLICATE_BECAME_SUPERSESSION")

    rails = set(d["rails"])
    required_rails = {
        "VISIBLE_TEXT_NE_TOTAL_RELATIONAL_CONTEXT",
        "PREFIX_NE_AUTHORITY",
        "HIDDEN_CONTEXT_NE_HIDDEN_AUTHORITY",
        "INVENTORY_NE_REALITY",
        "INVENTORY_INCLUSION_NE_LIFECYCLE_PROMOTION",
        "UNKNOWN_NE_EMPTY",
        "LOCAL_IS_NOT_LANDED",
        "VALIDATION_IS_NOT_ACCEPTANCE",
        "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF"
    }
    if not required_rails.issubset(rails):
        fail("FAIL_REQUIRED_RAILS")

    if d["runtime_effect"] or d["public_effect"]:
        fail("FAIL_EFFECT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COVIRTUAL_SUBSTRATE_PREFIX_INVENTORY_R0",
        "checked_out_head_sha": head,
        "canonical_glyph": pp["canonical_glyph"],
        "prompt_example_count": len(examples),
        "inventory_shard_count": len(inv["shards"]),
        "inventory_class_count": len(classes),
        "fixture_semantic_sha256": canonical_sha(d),
        "runtime_effect": False,
        "public_effect": False
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
