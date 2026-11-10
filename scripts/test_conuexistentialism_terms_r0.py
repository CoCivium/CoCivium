"""Quality gates for candidate existential terminology, not philosophical truth."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"ai/ontology/conuexistentialism-gdside-candidates-r0.json"
DOC=ROOT/"docs/coterms/CONUEXISTENTIALISM_GDSIDE_CANDIDATES_R0_20261110.md"

class CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads(MANIFEST.read_text(encoding="utf8"))
        cls.doc=DOC.read_text(encoding="utf8")
    def test_candidate_count_and_unique_ids(self):
        self.assertEqual(len(self.m["terms"]),36)
        self.assertEqual(len(set(x["id"] for x in self.m["terms"])),36)
        self.assertEqual(len(set(x["name"] for x in self.m["terms"])),36)
    def test_six_nonempty_families(self):
        self.assertEqual(len(self.m["families"]),6)
        self.assertEqual(sum(x["term_count"] for x in self.m["families"]),36)
        self.assertEqual({x["id"] for x in self.m["families"]},{t["family"] for t in self.m["terms"]})
    def test_no_automatic_registration(self):
        self.assertIn("NOT_REGISTERED",self.m["status"])
        self.assertTrue(all(t["lifecycle"]=="PROPOSED_UNREGISTERED" and t["authority"]=="NONE" for t in self.m["terms"]))
        self.assertFalse(self.m["canon"])
    def test_meaning_inverse_discriminator_present(self):
        for t in self.m["terms"]:
            for key in ("name","meaning","inverse_candidate","discriminating_question"):
                self.assertGreater(len(t[key]),10 if key!="name" else 4,t["name"])
    def test_gdside_explicit_epistemic_boundary(self):
        self.assertIn("G_D_SIDE_NE_EMPIRICAL_PROOF",self.m["epistemic_boundaries"])
        self.assertIn("FINITUDE_NE_DEATH_PREFERENCE",self.m["epistemic_boundaries"])
        self.assertIn("NOT CANON",self.doc)
    def test_existing_source_files(self):
        for path in self.m["source_refs"]:
            self.assertTrue((ROOT/path).is_file(),path)
    def test_no_receiver_claim(self):
        for k in ("receiver_ack","coex","canon","live_runtime"):
            self.assertIs(self.m[k],False)
    def test_interpretations_are_question_not_claim(self):
        self.assertIn("CoTranscendenceInLife+",self.doc)
        self.assertIn("CoNullAndMystery+",self.doc)
if __name__=="__main__":
    unittest.main()
