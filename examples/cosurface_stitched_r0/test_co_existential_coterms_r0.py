"""Fail-closed static checks for the noncanonical CoTerms existential field.

This suite is not glossary approval and does not verify metaphysical claims.
"""
import json
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent
DOC = json.loads((BASE / "co_existential_coterms_candidates_r0.json").read_text(encoding="utf-8"))
CURATED = json.loads((BASE.parent.parent / "docs" / "coterms" / "coterms-public-r0.json").read_text(encoding="utf-8"))

class CoExistentialTermsTests(unittest.TestCase):
    def test_40_distinct_candidates(self):
        self.assertEqual(DOC["count"], 40)
        self.assertEqual(len(DOC["terms"]), DOC["count"])
        self.assertEqual(len({x["concept_id"] for x in DOC["terms"]}), 40)
        self.assertEqual(len({x["term"] for x in DOC["terms"]}), 40)

    def test_no_unproven_canon(self):
        self.assertIn("NOT_CANON", DOC["status"])
        self.assertTrue(all(x["status"] == "WORKING_NAME_CANDIDATE" for x in DOC["terms"]))
        self.assertTrue(all(x["verified_product"] is False for x in DOC["terms"]))

    def test_term_anti_meaning_present(self):
        for x in DOC["terms"]:
            with self.subTest(x["term"]):
                self.assertGreaterEqual(len(x["definition"]), 30)
                self.assertGreaterEqual(len(x["anti_meaning"]), 24)
                self.assertTrue(x["provenance"])

    def test_epistemic_classes_explicit(self):
        for x in DOC["terms"]:
            self.assertIn(x["epistemic_class"], {
                "PHILOSOPHICAL_OR_NORMATIVE_CANDIDATE",
                "INTERPRETIVE_OR_DESIGN_CANDIDATE",
                "DESIGN_OR_HYPOTHESIS",
            })

    def test_groups_balanced_but_not_homogenized(self):
        groups = {}
        for x in DOC["terms"]:
            groups[x["group"]] = groups.get(x["group"], 0) + 1
        self.assertEqual(sorted(groups.values()), [10, 10, 10, 10])

    def test_foundational_existential_names(self):
        names={x["term"] for x in DOC["terms"]}
        self.assertIn("CoNuExistentialism+", names)
        self.assertIn("CoG_dSide+", names)
        self.assertIn("CoRegrow+", names)
        self.assertIn("CoInverseLens+", names)

    def test_curated_31_not_modified_by_expansion(self):
        self.assertEqual(CURATED["release_scope"]["term_count"], 31)
        self.assertEqual(len(CURATED["terms"]), 31)
        self.assertNotEqual(DOC["schema"], CURATED["schema"])

    def test_no_implicit_authority(self):
        required={"CANDIDATE_NE_CANON","METAPHOR_NE_MECHANISM",
                  "BELIEF_NE_EMPIRICAL_PROOF","NAMING_NE_OPERATIONAL_CAPABILITY"}
        self.assertTrue(required.issubset(DOC["controls"]))

    def test_explicit_lifecycle(self):
        required=("Meaning and anti-meaning","Distinct value over existing CoLex item",
                  "Accept reject merge split archive and supersede with receipt")
        self.assertTrue(all(x in DOC["term_gates"] for x in required))

    def test_no_private_identity_payload(self):
        text=json.dumps(DOC).lower()
        for marker in ("@gmail.com", "c:\\users\\", "private key", "api_token"):
            self.assertNotIn(marker, text)

if __name__=="__main__":
    unittest.main()
