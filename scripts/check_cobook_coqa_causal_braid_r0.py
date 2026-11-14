#!/usr/bin/env python3
"""Check CoBook CoQ&A causal braid without reading private answers or executing tasks.

This is deterministic planning over a public candidate graph. Synthetic fixtures
are NOT real consent, a sent publication, or an independent reader/receiver.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/Books/cobook-coqa-causal-braid-r0.json"
SCHEMA = "CoBook.CoQA.CausalBraid.R0-candidate"
NAMES = (
    "voluntary_answer", "source_attribution", "tension_extract",
    "counter_question_review", "source_challenge", "privacy_rights_preflight",
    "scene_draft", "child_agency_audit", "evidence_audit",
    "accessible_reader_audit", "review_fan_in",
    "uncoached_reader_feedback", "publication_gate",
)
EFFECTS = {
    "human_input": "NONE", "serial_write": "PRIVATE_CANDIDATE",
    "parallel_read": "NONE", "human_review": "NONE",
    "external_effect": "PUBLIC_RELEASE",
}
GATES = {
    "true", "voluntary_answer_present", "consent_to_adapt",
    "review_passed", "independent_reader_receipt",
    "release_approved_with_receipts",
}
EXPECTED_EDGES = {
    "voluntary_answer": (),
    "source_attribution": ("voluntary_answer",),
    "tension_extract": ("source_attribution",),
    "counter_question_review": ("tension_extract",),
    "source_challenge": ("tension_extract",),
    "privacy_rights_preflight": ("tension_extract",),
    "scene_draft": ("counter_question_review", "source_challenge", "privacy_rights_preflight"),
    "child_agency_audit": ("scene_draft",),
    "evidence_audit": ("scene_draft",),
    "accessible_reader_audit": ("scene_draft",),
    "review_fan_in": ("child_agency_audit", "evidence_audit", "accessible_reader_audit"),
    "uncoached_reader_feedback": ("review_fan_in",),
    "publication_gate": ("uncoached_reader_feedback",),
}

def read():
    return json.loads(PATH.read_text(encoding="utf-8"))

def validate(g):
    issues = []
    if g.get("schema") != SCHEMA or g.get("state") != "DRAFT_GRAPH_NOT_AUTONOMOUS_EXECUTION":
        issues.append("not a candidate-only CoBook CoQA graph")
    for field, expected in {
        "source_answer_ref": None, "source_answer_state": "AWAITING_VOLUNTARY_ANSWER",
        "consent_to_adapt": "UNKNOWN", "publication_approval": False,
        "independent_reader_receipt": None, "receiver_ack_ref": None,
        "active_writer": "book_editor",
    }.items():
        if g.get(field, object()) != expected:
            issues.append("unsafe or invented current state: " + field)
    rules = g.get("execution_rules", {})
    for key, val in {
        "all_effects": "PLAN_ONLY_NO_AUTOMATIC_EXECUTION",
        "max_parallel_readers": 3,
        "single_elected_writer": True,
        "on_no_material_delta": "NO_MATERIAL_DELTA",
        "fail_closed_on_unknown_permission": True,
        "no_unverified_receiver_ack": True,
        "no_public_release_without_separate_human_gate": True,
        "repeat_regression_tests_allowed": True,
    }.items():
        if rules.get(key) != val:
            issues.append("missing limit: " + key)
    sources = g.get("lineage", [])
    if len(sources) != 3 or len(set(sources)) != len(sources):
        issues.append("unexpected source lineage")
    for source in sources:
        if not isinstance(source, str) or source.startswith("/") or ".." in Path(source).parts:
            issues.append("unsafe lineage pointer")
        elif not (ROOT / source).is_file():
            issues.append("source pointer missing: " + source)
    nodes = g.get("nodes", [])
    ids = [n.get("id") for n in nodes]
    if tuple(ids) != NAMES:
        issues.append("unknown, missing or reordered stage")
    if len(set(ids)) != len(ids):
        issues.append("duplicate stage identity")
    by_id = {n["id"]: n for n in nodes if isinstance(n.get("id"), str)}
    for node in nodes:
        name = node.get("id", "")
        kind = node.get("kind")
        if kind not in EFFECTS or node.get("effect") != EFFECTS.get(kind):
            issues.append("unexpected effect: " + name)
        if node.get("gate") not in GATES:
            issues.append("unknown gate: " + name)
        if node.get("depends_on") != list(EXPECTED_EDGES.get(name, ())):
            issues.append("dependency changed: " + name)
        if kind == "serial_write" and node.get("actor") != "book_editor":
            issues.append("multiple writers: " + name)
        if kind == "parallel_read" and node.get("actor") != "reviewer":
            issues.append("unsafe parallel actor: " + name)
        if kind == "external_effect" and node.get("actor") != "human":
            issues.append("machine authorization of public effects")
    for name, expected_kind, expected_gate in (
        ("voluntary_answer", "human_input", "voluntary_answer_present"),
        ("source_attribution", "serial_write", "consent_to_adapt"),
        ("scene_draft", "serial_write", "consent_to_adapt"),
        ("review_fan_in", "serial_write", "review_passed"),
        ("uncoached_reader_feedback", "human_review", "independent_reader_receipt"),
        ("publication_gate", "external_effect", "release_approved_with_receipts"),
    ):
        n = by_id.get(name, {})
        if n.get("kind") != expected_kind or n.get("gate") != expected_gate:
            issues.append("safety-critical gate changed: " + name)
    # Fixed expected edges imply an acyclic DAG; still detect future invalid edits.
    seen, visiting = set(), set()
    def walk(name):
        if name in visiting:
            issues.append("cycle: " + name)
            return
        if name in seen or name not in by_id:
            return
        visiting.add(name)
        for dep in by_id[name].get("depends_on", []):
            if dep not in by_id:
                issues.append("dangling dependency: " + str(dep))
            else:
                walk(dep)
        visiting.remove(name)
        seen.add(name)
    for name in by_id:
        walk(name)
    return issues

def gate_ok(name, facts):
    if name == "true":
        return True
    if name in ("voluntary_answer_present", "consent_to_adapt", "review_passed"):
        return facts.get(name) is True
    if name == "independent_reader_receipt":
        return bool(facts.get(name))
    if name == "release_approved_with_receipts":
        return (
            all(facts.get(k) is True for k in (
                "publication_approval", "rights_clearance", "exact_source_digest_verified"))
            and bool(facts.get("independent_reader_receipt"))
        )
    return False

def next_batch(g, done, facts):
    """Plan only. Never execute a stage, mutate an object or forge a receipt."""
    if validate(g):
        raise ValueError("invalid graph")
    options = [n for n in g["nodes"] if n["id"] not in done
        and set(n["depends_on"]).issubset(done)
        and gate_ok(n["gate"], facts)]
    if not options:
        return []
    # A concurrent batch is permitted ONLY if all selected nodes are read-only.
    reads = [n["id"] for n in options if n["kind"] == "parallel_read"]
    if reads:
        assert len(reads) <= g["execution_rules"]["max_parallel_readers"]
        assert len(reads) == len(options), "no mixed writer / reviewer batch"
        return reads
    return [options[0]["id"]]

def synthetic_tests(g):
    assert validate(g) == [], validate(g)
    assert next_batch(g, set(), {}) == [], "Never invent an answer"
    assert next_batch(g, set(), {"voluntary_answer_present": True}) == ["voluntary_answer"]
    done = {"voluntary_answer"}
    facts = {"voluntary_answer_present": True}
    assert next_batch(g, done, facts) == [], "Never adapt without consent"
    facts["consent_to_adapt"] = True
    assert next_batch(g, done, facts) == ["source_attribution"]
    done.add("source_attribution")
    assert next_batch(g, done, facts) == ["tension_extract"]
    done.add("tension_extract")
    assert next_batch(g, done, facts) == [
        "counter_question_review", "source_challenge", "privacy_rights_preflight"]
    done.update(("counter_question_review", "source_challenge", "privacy_rights_preflight"))
    assert next_batch(g, done, facts) == ["scene_draft"]
    done.add("scene_draft")
    assert next_batch(g, done, facts) == [
        "child_agency_audit", "evidence_audit", "accessible_reader_audit"]
    done.update(("child_agency_audit", "evidence_audit", "accessible_reader_audit"))
    assert next_batch(g, done, facts) == [], "Never merge without review"
    facts["review_passed"] = True
    assert next_batch(g, done, facts) == ["review_fan_in"]
    done.add("review_fan_in")
    assert next_batch(g, done, facts) == [], "Never fabricate reader uptake"
    facts["independent_reader_receipt"] = "SYNTHETIC_NOT_REAL"
    assert next_batch(g, done, facts) == ["uncoached_reader_feedback"]
    done.add("uncoached_reader_feedback")
    assert next_batch(g, done, facts) == [], "Never promote on reader test alone"
    facts["publication_approval"] = True
    facts["rights_clearance"] = True
    assert next_batch(g, done, facts) == [], "No release without exact source digest"
    facts["exact_source_digest_verified"] = True
    assert next_batch(g, done, facts) == ["publication_gate"], "Fixture route only"
    bad = copy.deepcopy(g)
    bad["nodes"][-1]["gate"] = "true"
    assert validate(bad), "Release gate bypass must fail"
    bad = copy.deepcopy(g)
    bad["nodes"][4]["depends_on"] = ["publication_gate"]
    assert validate(bad), "Cycle / dependency tamper must fail"
    bad = copy.deepcopy(g)
    bad["nodes"][5]["effect"] = "PUBLIC_RELEASE"
    assert validate(bad), "Parallel reviewer effect must fail"
    bad = copy.deepcopy(g)
    bad["source_answer_ref"] = "invented-private-data"
    assert validate(bad), "Private answer mutation must fail"
    assert next_batch(g, set(NAMES), facts) == [], "No material delta -> no repeated work"
    print("PASS_COBOOK_COQA_CAUSAL_BRAID_R0")
    print(json.dumps({
        "result": "PLAN_VALIDATED_SYNTHETIC_ONLY",
        "stages": len(g["nodes"]),
        "maximum_parallel_readonly_stages": 3,
        "real_input_state": g["source_answer_state"],
        "real_publication_approved": g["publication_approval"],
        "real_receiver_ack": g["receiver_ack_ref"],
        "unverified_live_execution": True,
    }, indent=2))

if __name__ == "__main__":
    synthetic_tests(read())
