"""R1E public-safe CoRel-of-CoRel / CoInterstice source fixture.

Typed, finite, evidence-bound addressability is not meaning, causation,
authorization, canon or deployed runtime. Standard-library-only tests.
"""
from dataclasses import dataclass, replace
import unittest

EPISTEMIC = frozenset({"OBSERVED", "PREDICTED", "PROPOSED", "UNKNOWN"})
KINDS = frozenset({"obj", "rel", "gap", "term"})
TYPES = frozenset({"depends_on", "constrains", "challenges", "qualifies",
                   "has_gap", "projects_as", "version_of", "candidate_inverse_of"})

@dataclass(frozen=True)
class Relation:
    id: str
    source: str
    predicate: str
    target: str
    provenance: str
    epistemic: str = "PROPOSED"
    effect_authority: str = "NONE"

@dataclass(frozen=True)
class Interstice:
    id: str
    between: tuple[str, ...]
    kind: str
    provenance: str
    epistemic: str = "UNKNOWN"
    observation_window: str = ""
    closed_scope_evidence: str = ""

@dataclass(frozen=True)
class Term:
    id: str
    label: str
    version: str
    provenance: str
    state: str = "CANDIDATE"

def ref_kind(ref):
    if not isinstance(ref, str) or ":" not in ref:
        return None
    kind, tail = ref.split(":", 1)
    return kind if kind in KINDS and tail else None

def validate(objects, relations, gaps, terms):
    """Pure, source-only structural validation. No external-effect permission."""
    all_ids = list(objects) + [r.id for r in relations] + [g.id for g in gaps] + [t.id for t in terms]
    errors = []
    if len(set(all_ids)) != len(all_ids):
        errors.append("DUPLICATE_ID")
    for ref in all_ids:
        if ref_kind(ref) is None:
            errors.append("INVALID_REFERENCE")
    known = set(all_ids)
    for r in relations:
        if ref_kind(r.id) != "rel" or r.source not in known or r.target not in known:
            errors.append("UNRESOLVED_RELATION_ENDPOINT")
        if r.predicate not in TYPES:
            errors.append("UNKNOWN_PREDICATE")
        if r.epistemic not in EPISTEMIC or not r.provenance:
            errors.append("UNQUALIFIED_RELATION")
        if r.effect_authority != "NONE":
            errors.append("UNAUTHORIZED_AUTHORITY_INHERITANCE")
    for g in gaps:
        if ref_kind(g.id) != "gap" or len(g.between) < 2 or any(ref not in known for ref in g.between):
            errors.append("INVALID_INTERSTICE")
        if not g.provenance or g.epistemic not in {"UNKNOWN", "PROPOSED", "OBSERVED"}:
            errors.append("UNQUALIFIED_INTERSTICE")
        # Even with metadata, this tiny source fixture cannot authenticate an absence claim.
        if g.kind == "OBSERVED_ABSENT" and not (g.observation_window and g.closed_scope_evidence):
            errors.append("ABSENCE_WITHOUT_CLOSED_SCOPE")
    for t in terms:
        if ref_kind(t.id) != "term" or not (t.label and t.version and t.provenance):
            errors.append("UNQUALIFIED_COTERM")
        if t.state not in {"CANDIDATE", "HOLD"}:
            errors.append("UNREVIEWED_TERM_PROMOTION")
    return tuple(sorted(set(errors)))

def traverse(start, relations, budget=12):
    """BFS on relation references, bounded and cycle safe."""
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 0:
        raise ValueError("INVALID_BUDGET")
    seen = {start}
    frontier = [start]
    edges_seen = 0
    while frontier and edges_seen < budget:
        source = frontier.pop(0)
        for r in relations:
            if r.source == source and edges_seen < budget:
                edges_seen += 1
                if r.target not in seen:
                    seen.add(r.target)
                    frontier.append(r.target)
    return frozenset(seen), edges_seen

OBJECTS = ("obj:prepared_action", "obj:approval_gate", "obj:time_context")
RELATIONS = (
    Relation("rel:r1", "obj:prepared_action", "depends_on", "obj:approval_gate", "source:demo"),
    Relation("rel:r2", "rel:r1", "constrains", "term:consent", "source:demo"),
    Relation("rel:r3", "gap:g1", "challenges", "rel:r1", "source:demo"),
    Relation("rel:r4", "obj:time_context", "qualifies", "rel:r1", "source:demo"),
)
GAPS = (Interstice("gap:g1", ("rel:r1", "obj:time_context"), "MISSING_FRESHNESS", "source:demo"),)
TERMS = (Term("term:consent", "Consent", "R0", "source:demo"),
         Term("term:cotim", "CoTim+", "unverified", "source:prior", "HOLD"),
         Term("term:cotume", "CoTume+", "unverified", "source:prior", "HOLD"))

class CoRelMetaCanary(unittest.TestCase):
    def check(self, relations=RELATIONS, gaps=GAPS, terms=TERMS, objects=OBJECTS):
        return validate(objects, relations, gaps, terms)
    def test_baseline_qualified(self):
        self.assertEqual(self.check(), ())
    def test_relation_itself_subject(self):
        self.assertEqual(RELATIONS[1].source, RELATIONS[0].id)
    def test_relation_itself_target(self):
        self.assertEqual(RELATIONS[2].target, RELATIONS[0].id)
    def test_gap_is_addressable(self):
        self.assertEqual(RELATIONS[2].source, GAPS[0].id)
    def test_missing_source_hold(self):
        self.assertIn("UNQUALIFIED_RELATION", self.check(relations=(replace(RELATIONS[0], provenance=""),)+RELATIONS[1:]))
    def test_unknown_relation_endpoint_hold(self):
        self.assertIn("UNRESOLVED_RELATION_ENDPOINT", self.check(relations=(replace(RELATIONS[0], target="rel:missing"),)+RELATIONS[1:]))
    def test_relation_cannot_inherit_effect_authority(self):
        self.assertIn("UNAUTHORIZED_AUTHORITY_INHERITANCE", self.check(relations=(replace(RELATIONS[1], effect_authority="WRITE"),)+RELATIONS[2:]))
    def test_coined_predicate_requires_review(self):
        self.assertIn("UNKNOWN_PREDICATE", self.check(relations=(replace(RELATIONS[1], predicate="is_god"),)+RELATIONS[2:]))
    def test_unknown_is_not_observed_absence(self):
        self.assertEqual(GAPS[0].epistemic, "UNKNOWN")
        self.assertIn("ABSENCE_WITHOUT_CLOSED_SCOPE", self.check(gaps=(replace(GAPS[0], kind="OBSERVED_ABSENT"),)))
    def test_closed_scope_metadata_still_not_truth(self):
        g=replace(GAPS[0], kind="OBSERVED_ABSENT", observation_window="t0..t1", closed_scope_evidence="self_report")
        self.assertEqual(self.check(gaps=(g,)), ())
        self.assertEqual(g.closed_scope_evidence, "self_report")
    def test_unverified_tim_and_tume_remain_hold(self):
        self.assertEqual((TERMS[1].state, TERMS[2].state), ("HOLD", "HOLD"))
    def test_term_promoted_without_review_hold(self):
        self.assertIn("UNREVIEWED_TERM_PROMOTION", self.check(terms=(replace(TERMS[1], state="CANON"),)+TERMS[0:1]+TERMS[2:]))
    def test_prediction_not_observation(self):
        r=replace(RELATIONS[0], epistemic="PREDICTED")
        self.assertEqual(self.check(relations=(r,)+RELATIONS[1:]), ())
        self.assertEqual(r.epistemic, "PREDICTED")
    def test_cycle_bounded(self):
        cycle=(Relation("rel:e1","rel:c1","challenges","rel:c2","source:demo"),
               Relation("rel:e2","rel:c2","constrains","rel:c1","source:demo"))
        reach,steps=traverse("rel:c1", cycle, budget=2)
        self.assertEqual(reach,frozenset(("rel:c1","rel:c2")))
        self.assertLessEqual(steps,2)
    def test_zero_budget_quiet(self):
        self.assertEqual(traverse("rel:r1", RELATIONS, 0),(frozenset(("rel:r1",)),0))
    def test_negative_budget_rejected(self):
        with self.assertRaises(ValueError): traverse("rel:r1",RELATIONS,-1)
    def test_no_automatic_perpetual_ontology(self):
        self.assertTrue(all(t.state!="CANON" for t in TERMS))
        self.assertTrue(all(r.effect_authority=="NONE" for r in RELATIONS))

if __name__ == "__main__":
    unittest.main()
