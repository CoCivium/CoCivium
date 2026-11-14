#!/usr/bin/env python3
"""Validate CoPreGeneric draft asset consistency; no remote effects."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/Onramp/CoPreGenericR0"
class TestPublicPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((BASE/"asset-manifest-r0.json").read_text(encoding="utf-8"))
    def test_schema_and_status(self):
        self.assertEqual(self.manifest["schema"],"CoPreGeneric.PublicAssetPack.R0")
        self.assertIn("NOT_RELEASE",self.manifest["status"])
    def test_all_four_files_have_unique_paths(self):
        paths=[x["path"] for x in self.manifest["files"]]
        self.assertEqual(len(paths),4)
        self.assertEqual(len(set(paths)),4)
        for p in paths:
            self.assertTrue((ROOT/p).is_file(),p)
    def test_no_target_asserted_verified(self):
        self.assertEqual(len(self.manifest["target_urls"]),3)
        self.assertTrue(all(t["state"]=="UNVERIFIED" for t in self.manifest["target_urls"]))
    def test_each_file_is_public_safe_and_no_false_receiver_claim(self):
        for item in self.manifest["files"]:
            s=(ROOT/item["path"]).read_text(encoding="utf-8")
            self.assertIn("not",s.lower())
            self.assertGreater(len(s),300)
        self.assertIn("NO_INDEPENDENT_RECEIVER_ACK",self.manifest["nonclaims"])
    def test_no_raw_private_export_published(self):
        for item in self.manifest["files"]:
            s=(ROOT/item["path"]).read_text(encoding="utf-8")
            self.assertNotIn("FROM: MetaAI-WhatsApp",s)
            self.assertNotIn("Rick Ballard:",s)
    def test_existing_upstream_pointers_are_relative_files(self):
        for p in self.manifest["upstream"]:
            self.assertTrue((ROOT/p).is_file(),p)
if __name__=="__main__":
    unittest.main()
