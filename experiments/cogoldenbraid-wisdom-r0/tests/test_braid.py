"""Tests are shape/guard/replay tests, not truth or outside-user success."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from braid import STAGES, braid_packet, canonical, digest, load, phrase_match, propose, validate

class BraidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = load()

    def test_valid_source(self):
        self.assertEqual(validate(self.seed)["candidate_count"], 14)

    def test_stage_order(self):
        self.assertEqual(len(STAGES), 10)

    def test_all_ten_stages(self):
        for p in self.seed["principles"]:
            self.assertEqual(tuple(braid_packet(p["id"], self.seed)["stages"]), STAGES)

    def test_no_independent_receivers_claimed(self):
        for p in self.seed["principles"]:
            packet = braid_packet(p["id"], self.seed)
            self.assertEqual(packet["stages"]["RECEIPT"], "NOT_RUN")
            self.assertEqual(packet["stages"]["RECEIVER"], "NONE_VERIFIED")
            self.assertEqual(packet["authority"], "NONE")

    def test_duplicate_id_fails(self):
        s = copy.deepcopy(self.seed); s["principles"][1]["id"] = s["principles"][0]["id"]
        with self.assertRaises(ValueError): validate(s)

    def test_unqualified_canon_fails(self):
        s = copy.deepcopy(self.seed); s["principles"][1]["status"] = "CANON"
        with self.assertRaisesRegex(ValueError,"PROMOTED"): validate(s)

    def test_authority_leak_fails(self):
        s = copy.deepcopy(self.seed); s["principles"][1]["authority"] = "SEND"
        with self.assertRaisesRegex(ValueError,"AUTHORITY"): validate(s)

    def test_private_data_fails(self):
        s = copy.deepcopy(self.seed); s["principles"][1]["privacy"] = "PRIVATE"
        with self.assertRaisesRegex(ValueError,"PRIVACY"): validate(s)

    def test_missing_exception_fails(self):
        s = copy.deepcopy(self.seed); s["principles"][1]["limitation"] = ""
        with self.assertRaisesRegex(ValueError,"MISSING"): validate(s)

    def test_missing_test_fails(self):
        s = copy.deepcopy(self.seed); s["principles"][1]["next_test"] = ""
        with self.assertRaisesRegex(ValueError,"MISSING"): validate(s)

    def test_dangling_edge_fails(self):
        s = copy.deepcopy(self.seed); s["typed_relations"][0]["to"] = "W999"
        with self.assertRaisesRegex(ValueError,"RELATION"): validate(s)

    def test_tension_kept(self):
        kinds = {x["kind"] for x in self.seed["typed_relations"]}
        self.assertIn("TENSION",kinds)
        self.assertIn("GUARD",kinds)

    def test_original_source_pinned(self):
        for x in self.seed["design_sources"].values():
            self.assertEqual(len(x["git_blob"]),40)

    def test_keyword_boundaries(self):
        self.assertTrue(phrase_match("orb", "An orb view"))
        self.assertFalse(phrase_match("orb", "This is absorbent"))

    def test_abstention_unknown(self):
        result=propose("zebra hammock marmalade quasar",self.seed)
        self.assertEqual(result["status"],"ABSTAIN_NO_EVIDENCE")
        self.assertEqual(result["candidates"],[])

    def test_ambiguous_not_authorized(self):
        result=propose("I need permission and a reviewer",self.seed)
        self.assertEqual(result["status"],"AMBIGUOUS_REQUIRES_CHOICE")
        self.assertEqual(result["effect"],"NONE")

    def test_invalid_budget_rejected(self):
        for v in (0,4,True):
            with self.subTest(value=v),self.assertRaises(ValueError): propose("a permission question",self.seed,limit=v)

    def test_large_text_refused(self):
        with self.assertRaises(ValueError): propose("a"*601,self.seed)

    def test_unknown_packet_fails(self):
        with self.assertRaises(ValueError): braid_packet("W999",self.seed)

    def test_no_external_run_in_packets(self):
        for x in self.seed["principles"]:
            self.assertEqual(braid_packet(x["id"],self.seed)["execution"],"NONE")

    def test_canonical_stable(self):
        self.assertEqual(digest({"b":2,"a":1}),digest({"a":1,"b":2}))

if __name__=="__main__":unittest.main()
