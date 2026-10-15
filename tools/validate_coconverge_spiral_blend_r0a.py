#!/usr/bin/env python3
import json
import subprocess
from fractions import Fraction
from pathlib import Path

P = Path("fixtures/relations/coconverge_spiral_blend_r0a.json")


def fail(code):
    raise SystemExit(code)


def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def density(obj):
    return Fraction(obj["decision_units"], obj["visible_units"])


def payload_decision(case, max_loss):
    src = case["verbose"]
    dst = case["candidate"]
    loss = src["decision_units"] - dst["decision_units"]

    if not dst["audit_reachable"]:
        return "REJECT_OR_REHYDRATE"
    if loss > max_loss:
        return "REJECT_SEMANTIC_LOSS"
    if density(dst) > density(src):
        return "ACCEPT_COMPACT_PROJECTION"
    return "KEEP_OR_REVISE_VERBOSE"


def identical(a, b):
    keys = ["uncertainty", "duplicates", "proof_refs", "resolved_contradictions"]
    return all(a[k] == b[k] for k in keys)


def spiral_decision(case, stalled_limit):
    cls = case["class"]
    if cls == "ACYCLIC_PROVENANCE_EDGE":
        return "REMAIN_ACYCLIC"

    if case.get("proof_gate") and case["turns"][-1]["uncertainty"] == 0:
        return "CLOSE_FOR_SCOPE"

    if case.get("new_contradiction") and case.get("branch_required"):
        return "BRANCH_PRESERVE_DISAGREEMENT"

    turns = case["turns"]
    stalled = 0
    for prev, cur in zip(turns, turns[1:]):
        if identical(prev, cur):
            stalled += 1
        else:
            stalled = 0
    if stalled >= stalled_limit:
        return "HIBERNATE_STALLED"

    return "CONTINUE_SPIRAL"


def blend_decision(case):
    if not case["typed_sources_preserved"]:
        return "REJECT_UNTYPED_COLLAPSE"

    src = case["source_lane"]
    dst = case["target_lane"]

    if src == "COMYTHOPS" and dst == "COMYTHOPS":
        return "KEEP_TYPED_MYTHIC"

    if src == "COMYTHOPS" and dst == "COOPS":
        if case["explicit_translation"] and not case["evidence_gate"]:
            return "PROPOSE_OPERATIONAL_HYPOTHESIS_NOT_EXECUTE"

    if src == "COOPS" and dst == "COMYTHOPS":
        if case["explicit_translation"] and case["evidence_gate"]:
            return "ALLOW_MYTHIC_PROJECTION_WITH_PROVENANCE"

    if src == "COOPS+COMYTHOPS" and dst == "HYBRID_PROJECTION":
        if case["explicit_translation"] and case["evidence_gate"]:
            return "COORDINATED_DUAL_PROJECTION"

    return "REJECT_UNTYPED_COLLAPSE"


def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    binds = [
        ("payload_doc_path", "payload_doc_blob_sha"),
        ("payload_fixture_path", "payload_fixture_blob_sha"),
        ("substrate_field_path", "substrate_field_blob_sha"),
        ("mythops_delta_path", "mythops_delta_blob_sha"),
        ("dynamic_wave_path", "dynamic_wave_blob_sha")
    ]
    for path_key, sha_key in binds:
        actual = git_blob(src[path_key])
        if actual != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    pd = d["payload_density"]
    for case in pd["cases"]:
        got = payload_decision(case, pd["max_projection_loss_for_compact_accept"])
        if got != case["expected"]:
            fail(f"FAIL_PAYLOAD:{case['id']}:got={got}:expected={case['expected']}")

    sp = d["spiral_policy"]
    if sp["all_relations_should_spiral"] is not False:
        fail("FAIL_ALL_RELATIONS_SPIRAL")
    if sp["return_requires_delta"] is not True:
        fail("FAIL_RETURN_DELTA_GATE")

    for case in sp["cases"]:
        got = spiral_decision(case, sp["stalled_turn_limit"])
        if got != case["expected"]:
            fail(f"FAIL_SPIRAL:{case['id']}:got={got}:expected={case['expected']}")

    blend = d["ops_mythops_blend"]
    if blend["blend_mode"] != "TYPED_INTEROPERABILITY_WITHOUT_EPISTEMIC_COLLAPSE":
        fail("FAIL_BLEND_MODE")

    for case in blend["cases"]:
        got = blend_decision(case)
        if got != case["expected"]:
            fail(f"FAIL_BLEND:{case['id']}:got={got}:expected={case['expected']}")

    rails = set(d["rails"])
    required = {
        "SPIRAL_NE_CIRCULAR_REPETITION",
        "CONVERGENCE_NE_CONSENSUS",
        "RELATION_NE_LOOP",
        "ACYCLIC_NE_BROKEN",
        "BLEND_NE_COLLAPSE",
        "MYTHIC_EFFECT_NE_OPERATIONAL_MECHANISM",
        "SENTIENCE_METAPHOR_NE_SENTIENCE_EVIDENCE",
        "VALIDATION_IS_NOT_ACCEPTANCE"
    }
    if not required.issubset(rails):
        fail("FAIL_REQUIRED_RAILS")

    if d["runtime_effect"] is not False or d["public_effect"] is not False:
        fail("FAIL_EFFECT_BOUNDARY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COCONVERGE_SPIRAL_BLEND_R0A",
        "checked_out_head_sha": head,
        "payload_case_count": len(pd["cases"]),
        "spiral_case_count": len(sp["cases"]),
        "blend_case_count": len(blend["cases"]),
        "all_relations_should_spiral": sp["all_relations_should_spiral"],
        "typed_blend_mode": blend["blend_mode"],
        "runtime_effect": False,
        "public_effect": False
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
