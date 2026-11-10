"""Fail-closed source and projection tests for CoPreGeneric Synth/Bio/G_d R1.

Runs without network access or provider credentials. Verifies the local checkout,
not independent receiver pickup, AGI, sentience, canon, or runtime handoff.
Run: python3 tests/test_copre_synth_bio_gd_r1.py
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACHINE = ROOT / "ai/continuity/copre-synth-bio-gd-coterms-r1-20261109.json"
HUMAN = ROOT / "docs/CoPreGeneric/CoPre_SynthBio_Gd_CoTerms_Candidate_R1_20261109.md"
PREDECESSOR = ROOT / "ai/continuity/conu-existentialism-candidate-field-r0.json"


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate(machine, human, predecessor_bytes):
    errors = []

    def need(condition, code):
        if not condition:
            errors.append(code)

    old = json.loads(predecessor_bytes)
    terms = machine.get("terms", [])
    families = machine.get("families", [])
    relations = machine.get("relations", [])
    ids = [t.get("id") for t in terms]
    labels = [t.get("label") for t in terms]
    family_codes = {f.get("code") for f in families}
    source_path = "ai/continuity/conu-existentialism-candidate-field-r0.json"
    refs = [r for r in machine.get("source_refs", []) if r.get("path") == source_path]
    pin = machine.get("predecessor_field", {})
    later = machine.get("predecessor_currentness_observation", {})

    need(machine.get("schema") == "CoAll.CoPreGeneric.SynthBioGdTerms.R1-candidate", "WRONG_SCHEMA")
    need(machine.get("state") == "PUBLIC_DRAFT_PR_NOT_MERGED_NOT_CANON", "UNEXPECTED_PROMOTION")
    need(machine.get("effect_authority") == "NONE", "UNAUTHORIZED_EFFECT")
    need(len(terms) == 72 and len(families) == 9 and len(relations) == 22, "GRAPH_COUNTS")
    need(len(ids) == len(set(ids)) and len(labels) == len(set(labels)), "DUPLICATE_TERMS")
    need(all(isinstance(x, str) and len(x) > 2 for x in ids + labels), "INVALID_TERM_ID")
    need(all(f.get("term_count") == 8 for f in families), "FAMILY_EXPECTED_COUNT")
    need(all(t.get("group") in family_codes for t in terms), "UNBOUND_FAMILY")
    need(all(sum(t.get("group") == f.get("code") for t in terms) == f.get("term_count")
             for f in families), "FAMILY_COVERAGE")
    need(all(t.get("status") == "UNQUALIFIED_PUBLIC_CANDIDATE" and
             t.get("epistemic_class") == "DESIGN_HYPOTHESIS_NOT_FACT"
             for t in terms), "TERM_PROMOTED_WITHOUT_PROOF")
    need(all(isinstance(t.get("discriminating_probe"), str) and
             len(t["discriminating_probe"]) > 14 for t in terms), "MISSING_FALSIFIER")
    need(all(e.get("from") in ids and e.get("to") in ids and
             e.get("effect_authority") == "NONE" for e in relations), "EDGE_OR_AUTHORITY_ERROR")

    blob_sha = git_blob_sha(predecessor_bytes)
    need(len(old.get("nodes", [])) == 24, "PREDECESSOR_NOT_PINNED_24")
    need(pin.get("known_candidate_count") == 24 and pin.get("pinned_blob_sha") == blob_sha,
         "PREDECESSOR_PIN_MISMATCH")
    need(len(refs) == 1 and refs[0].get("observed_git_blob_sha") == blob_sha,
         "SOURCE_REF_MISMATCH")
    need(later.get("branch_predecessor_count") == 24 and
         later.get("main_predecessor_count") == 28 and
         later.get("branch_blob_sha") == blob_sha and
         len(later.get("new_main_candidates", [])) == 4,
         "LATER_MAIN_OBSERVATION_UNBOUND")

    old_labels = {n.get("label", "").lower() for n in old.get("nodes", [])}
    later_labels = {n.get("label", "").lower() for n in later.get("new_main_candidates", [])}
    need(not old_labels.intersection(x.lower() for x in labels), "R0_NAME_COLLISION")
    need(not later_labels.intersection(x.lower() for x in labels), "LATER_R0_NAME_COLLISION")
    need(all("**" + t["label"] + "**" in human for t in terms if "label" in t),
         "HUMAN_PROJECTION_LOSS")
    by_id = {t.get("id"): t.get("label") for t in terms}
    tick = chr(96)
    need(all((tick + by_id.get(e.get("from"), "") + tick + " **" + e.get("type", "") +
              "** " + tick + by_id.get(e.get("to"), "") + tick) in human for e in relations),
         "HUMAN_RELATION_LOSS")
    need("28 terms" in human and "24" in human, "HUMAN_CURRENTNESS_LOSS")

    nonclaims = set(machine.get("nonclaims", []))
    need({"NO_INDEPENDENT_RECEIVER_PICKUP", "NOT_GLOBAL_COPRE_CANON",
          "NOT_AGI_OR_SENTIENCE_PROOF", "NOT_SPIRITUAL_REVELATION"}.issubset(nonclaims),
         "REQUIRED_NONCLAIMS_LOST")

    if errors:
        raise AssertionError("; ".join(errors))
    return {"terms": len(terms), "families": len(families),
            "relations": len(relations), "predecessor_pinned": 24,
            "later_main_observed": 28, "source_blob": blob_sha,
            "state": "STRUCTURAL_VALIDATION_ONLY_NOT_RECEIVER_READPROOF"}


class CoPreR1Qualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(MACHINE.read_text(encoding="utf-8"))
        cls.human = HUMAN.read_text(encoding="utf-8")
        cls.predecessor = PREDECESSOR.read_bytes()

    def test_exact_checkout_contract(self):
        self.assertEqual(validate(self.payload, self.human, self.predecessor)["terms"], 72)

    def test_duplicate_term_id_fails(self):
        x = copy.deepcopy(self.payload)
        x["terms"][1]["id"] = x["terms"][0]["id"]
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)

    def test_unbound_relation_fails(self):
        x = copy.deepcopy(self.payload)
        x["relations"][0]["to"] = "missing"
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)

    def test_unauthorized_effect_fails(self):
        x = copy.deepcopy(self.payload)
        x["effect_authority"] = "ALL"
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)

    def test_unqualified_term_promoted_fails(self):
        x = copy.deepcopy(self.payload)
        x["terms"][0]["status"] = "CANON"
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)

    def test_missing_discriminator_fails(self):
        x = copy.deepcopy(self.payload)
        x["terms"][0]["discriminating_probe"] = ""
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)

    def test_stale_or_false_predecessor_pin_fails(self):
        x = copy.deepcopy(self.payload)
        x["predecessor_field"]["pinned_blob_sha"] = "0" * 40
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)

    def test_unqualified_currentness_upgrade_fails(self):
        x = copy.deepcopy(self.payload)
        x["predecessor_currentness_observation"]["main_predecessor_count"] = 24
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)

    def test_human_projection_omission_fails(self):
        missing = self.human.replace("**CoClaimAltitude+**", "CoClaimAltitude+")
        with self.assertRaises(AssertionError):
            validate(self.payload, missing, self.predecessor)

    def test_human_relation_omission_fails(self):
        missing = self.human.replace("**DISTINGUISHES_SUPPORT_FROM_CLAIM**",
                                     "DISTINGUISHES_SUPPORT_FROM_CLAIM")
        with self.assertRaises(AssertionError):
            validate(self.payload, missing, self.predecessor)

    def test_missing_nonclaim_fails(self):
        x = copy.deepcopy(self.payload)
        x["nonclaims"].remove("NO_INDEPENDENT_RECEIVER_PICKUP")
        with self.assertRaises(AssertionError):
            validate(x, self.human, self.predecessor)


if __name__ == "__main__":
    unittest.main()
