#!/usr/bin/env python3
"""Offline source-bound conformance tests for one CoAllBloom candidate witness.

No model, user, filesystem mutation, service, or device action is performed.
Run: python3 -m unittest discover -s examples/coallbloom -p 'test_*.py' -v
"""
import copy
import json
import re
import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PIN = re.compile(r"^[0-9a-f]{40}$")
EPISTEMIC = {
    "DESIGN_HYPOTHESIS", "COUNTERFACTUAL", "BASELINE", "OBSERVATION_GAP",
    "SYMBOLIC", "SCIENTIFIC_TEST_PLAN", "SPECULATIVE_HYPOTHESIS",
    "METAPHYSICAL_QUESTION", "TESTABLE_HYPOTHESIS", "CONCEPTUAL_DISTINCTION",
}
REQUIRED_OPS = {
    "ALT", "INVERT", "NEGATE", "NULL", "ELSE", "INTERSTICE",
    "CROSS_SUBSTRATE", "SYMBOLIC_LENS", "PHYSICAL_LENS", "ET_LENS",
    "GD_LENS", "CHALLENGE", "COMPARE_DYNAMICS",
}
REQUIRED_NONCLAIMS = {
    "INVERSE_NE_INVERSE_CAUSATION", "NEGATION_NE_TRUTH",
    "NULL_NE_NONEXISTENCE", "SPIRITUAL_SYMBOL_NE_PHYSICAL_EVIDENCE",
    "ET_HYPOTHESIS_NE_ET_CONTACT", "G_D_QUESTION_NE_DIVINE_AUTHORITY",
    "IA_LABEL_NE_QUALIFIED_IDENTITY", "SELECTED_NE_EXECUTED",
    "PUBLISHED_NE_RECEIVER_ACK",
}

def load():
    return json.loads((HERE / "first-seed-witness-r0.json").read_text(encoding="utf-8"))

def check(doc, check_actual_hashes=False):
    """Return scoped, nonempty errors; never mutate the original witness."""
    errors = []
    if doc.get("schema") != "CoCivium.CoAllBloom.FirstSeedWitness.R0":
        errors.append("schema")
    if doc.get("status") != "PUBLIC_REVIEW_CANDIDATE__STATIC_SEMANTIC_WITNESS__NOT_RUNTIME":
        errors.append("scope")
    seed = doc.get("seed") or {}
    if not seed.get("id") or seed.get("authority") != "NONE" or seed.get("privacy") != "PUBLIC_SYNTHETIC":
        errors.append("seed_identity_privacy_authority")
    pins = doc.get("source_pins") or []
    if len(pins) != 6 or len({x.get("path") for x in pins}) != len(pins):
        errors.append("donor_count_uniqueness")
    for row in pins:
        path = row.get("path", "")
        sha = row.get("git_blob", "")
        if not PIN.fullmatch(sha) or not path.startswith(("docs/", "ai/", "examples/")) or ".." in Path(path).parts:
            errors.append("donor_path_or_sha")
            continue
        if check_actual_hashes:
            full = ROOT / path
            if not full.is_file():
                errors.append("donor_file_missing:" + path)
                continue
            actual = subprocess.run(["git", "hash-object", str(full)], capture_output=True, text=True, check=True).stdout.strip()
            if actual != sha:
                errors.append("donor_source_drift:" + path)
    cards = doc.get("candidates") or []
    ids = [c.get("id") for c in cards]
    if not 1 <= len(cards) <= 16 or len(set(ids)) != len(ids):
        errors.append("bounded_unique_cards")
    ops = {c.get("operator") for c in cards}
    if not REQUIRED_OPS.issubset(ops):
        errors.append("mandatory_negative_and_diversity_lanes")
    for card in cards:
        if card.get("source_seed") != seed.get("id") or card.get("state") != "CANDIDATE":
            errors.append("unbound_or_promoted:" + str(card.get("id")))
        if card.get("authority") != "NONE" or card.get("external_effects") is not False:
            errors.append("unauthorized_effect:" + str(card.get("id")))
        if card.get("receiver_ack") is not None or card.get("independent_human_review") is not None:
            errors.append("forged_receiver_or_reviewer:" + str(card.get("id")))
        if card.get("epistemic_class") not in EPISTEMIC:
            errors.append("epistemic_type:" + str(card.get("id")))
        if not card.get("proposal") or not card.get("next_proof"):
            errors.append("missing_proposal_or_test:" + str(card.get("id")))
    named = {c.get("id"): c for c in cards}
    if named.get("SPIRITUAL_SYMBOLIC", {}).get("epistemic_class") != "SYMBOLIC":
        errors.append("spiritual_is_not_measured")
    if named.get("GD_PHILOSOPHICAL", {}).get("epistemic_class") != "METAPHYSICAL_QUESTION":
        errors.append("gd_is_not_a_detector")
    if named.get("ET_SPECULATIVE", {}).get("epistemic_class") != "SPECULATIVE_HYPOTHESIS":
        errors.append("et_hypothesis_is_not_contact")
    if named.get("PHYSICAL_MEASUREMENT", {}).get("epistemic_class") != "SCIENTIFIC_TEST_PLAN":
        errors.append("physical_requires_future_measurements")
    if named.get("NULL_BASELINE", {}).get("epistemic_class") != "BASELINE":
        errors.append("null_is_not_global_absence")
    frontier = doc.get("frontier") or {}
    elected = frontier.get("selected_candidate_ids") or []
    if not 1 <= len(elected) <= 1 or any(x not in ids for x in elected):
        errors.append("elected_frontier")
    if any(frontier.get(k) != 0 for k in ("active_workers", "actual_experiments", "source_receiver_acks", "independent_users")):
        errors.append("runtime_claim_not_supported")
    if frontier.get("generated") != len(cards) or frontier.get("maximum_elected") != 1:
        errors.append("frontier_bounds")
    if (doc.get("onramp") or {}).get("term_ia") != "UNRESOLVED_NO_ACCEPTED_EXPANSION":
        errors.append("ia_must_remain_unresolved")
    if set((doc.get("dynamics") or {}).keys()) != {"CHAOS", "DRIFT", "EVOLUTION", "NOISE"}:
        errors.append("distinct_dynamics")
    if not {"⊂", "↔", "¬", "∅", "?", "Δ", "↺", "∞"}.issubset(set((doc.get("readable_glossary") or {}).keys())):
        errors.append("accessible_glyphs")
    if not REQUIRED_NONCLAIMS.issubset(set(doc.get("nonclaims") or [])):
        errors.append("nonclaims")
    if "NO_INDEPENDENT_REVIEW" not in doc.get("review_state", ""):
        errors.append("review_promotion")
    return errors

class CoAllBloomWitnessTests(unittest.TestCase):
    def setUp(self):
        self.d = load()

    def mutate(self, callback):
        d = copy.deepcopy(self.d)
        callback(d)
        return check(d)

    def test_original_conforms(self): self.assertEqual(check(self.d), [])
    def test_pinned_sources_exact_in_repo(self): self.assertEqual(check(self.d, check_actual_hashes=True), [])
    def test_repeatable_serialization(self): self.assertEqual(load(), self.d)
    def test_same_one_seed(self): self.assertEqual({c["source_seed"] for c in self.d["candidates"]}, {self.d["seed"]["id"]})
    def test_fourteen_cards(self): self.assertEqual(len(self.d["candidates"]), 14)
    def test_two_conventional_alternatives(self): self.assertEqual(sum(c["operator"] == "ALT" for c in self.d["candidates"]), 2)
    def test_no_active_experiments(self): self.assertEqual(self.d["frontier"]["active_workers"] + self.d["frontier"]["actual_experiments"], 0)
    def test_only_one_elected_falsifier(self): self.assertEqual(self.d["frontier"]["selected_candidate_ids"], ["FALSIFIER"])
    def test_dynamics_not_collapsed(self): self.assertEqual(set(self.d["dynamics"]), {"CHAOS", "DRIFT", "EVOLUTION", "NOISE"})
    def test_seed_authority_fail_closed(self): self.assertIn("seed_identity_privacy_authority", self.mutate(lambda d: d["seed"].update(authority="ADMIN")))
    def test_private_seed_fail_closed(self): self.assertIn("seed_identity_privacy_authority", self.mutate(lambda d: d["seed"].update(privacy="PRIVATE_CONTENT")))
    def test_effect_mutation_rejected(self): self.assertTrue(any(x.startswith("unauthorized_effect") for x in self.mutate(lambda d: d["candidates"][0].update(external_effects=True))))
    def test_authority_mutation_rejected(self): self.assertTrue(any(x.startswith("unauthorized_effect") for x in self.mutate(lambda d: d["candidates"][1].update(authority="UNBOUNDED"))))
    def test_receiver_forgery_rejected(self): self.assertTrue(any(x.startswith("forged_receiver") for x in self.mutate(lambda d: d["candidates"][0].update(receiver_ack="YES"))))
    def test_reviewer_forgery_rejected(self): self.assertTrue(any(x.startswith("forged_receiver") for x in self.mutate(lambda d: d["candidates"][0].update(independent_human_review="DONE"))))
    def test_source_spoof_rejected(self): self.assertIn("donor_path_or_sha", self.mutate(lambda d: d["source_pins"][0].update(git_blob="unverified")))
    def test_duplicate_card_rejected(self): self.assertIn("bounded_unique_cards", self.mutate(lambda d: d["candidates"].append(copy.deepcopy(d["candidates"][0]))))
    def test_unbound_lineage_rejected(self): self.assertTrue(any(x.startswith("unbound_or_promoted") for x in self.mutate(lambda d: d["candidates"][0].update(source_seed="unknown"))))
    def test_active_promotion_rejected(self): self.assertTrue(any(x.startswith("unbound_or_promoted") for x in self.mutate(lambda d: d["candidates"][0].update(state="EFFECTIVE"))))
    def test_et_empirical_claim_rejected(self): self.assertIn("et_hypothesis_is_not_contact", self.mutate(lambda d: next(c for c in d["candidates"] if c["id"]=="ET_SPECULATIVE").update(epistemic_class="SCIENTIFIC_TEST_PLAN")))
    def test_gd_physical_claim_rejected(self): self.assertIn("gd_is_not_a_detector", self.mutate(lambda d: next(c for c in d["candidates"] if c["id"]=="GD_PHILOSOPHICAL").update(epistemic_class="SCIENTIFIC_TEST_PLAN")))
    def test_spiritual_measurement_claim_rejected(self): self.assertIn("spiritual_is_not_measured", self.mutate(lambda d: next(c for c in d["candidates"] if c["id"]=="SPIRITUAL_SYMBOLIC").update(epistemic_class="SCIENTIFIC_TEST_PLAN")))
    def test_null_not_absence(self): self.assertIn("null_is_not_global_absence", self.mutate(lambda d: next(c for c in d["candidates"] if c["id"]=="NULL_BASELINE").update(epistemic_class="DESIGN_HYPOTHESIS")))
    def test_no_missing_null_lane(self): self.assertIn("mandatory_negative_and_diversity_lanes", self.mutate(lambda d: next(c for c in d["candidates"] if c["id"]=="NULL_BASELINE").update(operator="ALT")))
    def test_do_not_invent_workers(self): self.assertIn("runtime_claim_not_supported", self.mutate(lambda d: d["frontier"].update(active_workers=1)))
    def test_do_not_invent_use(self): self.assertIn("runtime_claim_not_supported", self.mutate(lambda d: d["frontier"].update(independent_users=1)))
    def test_do_not_invent_ack(self): self.assertIn("runtime_claim_not_supported", self.mutate(lambda d: d["frontier"].update(source_receiver_acks=1)))
    def test_invalid_selection_rejected(self): self.assertIn("elected_frontier", self.mutate(lambda d: d["frontier"].update(selected_candidate_ids=["ET_SPECULATIVE", "FALSIFIER"])))
    def test_expansion_limit_rejected(self): self.assertIn("bounded_unique_cards", self.mutate(lambda d: d["candidates"].extend([{**d["candidates"][0], "id":f"overflow{i}"} for i in range(4)])))
    def test_ia_inference_rejected(self): self.assertIn("ia_must_remain_unresolved", self.mutate(lambda d: d["onramp"].update(term_ia="INDEPENDENT_AI_PERSON")))
    def test_dynamics_collapse_rejected(self): self.assertIn("distinct_dynamics", self.mutate(lambda d: d["dynamics"].pop("CHAOS")))
    def test_plain_language_glyph_fallback(self): self.assertTrue(all(self.d["readable_glossary"].values()))
    def test_nonclaims_cannot_silently_drop(self): self.assertIn("nonclaims", self.mutate(lambda d: d["nonclaims"].remove("ET_HYPOTHESIS_NE_ET_CONTACT")))
    def test_no_unproven_panel_promotion(self): self.assertIn("review_promotion", self.mutate(lambda d: d.update(review_state="INDEPENDENTLY_REVIEWED")))

if __name__ == "__main__":
    unittest.main()
