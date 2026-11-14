#!/usr/bin/env python3
"""Bounded package checks: public-safe derivative, not independent model pickup."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs/Onramp/copregeneric_whatsapp_v8x"
FILES = [
    "CoPreGeneric-v1.0-DRAFT.md",
    "CoAckRewise-v8.74.md",
    "CoFeedLoop-Devs.md",
    "CoMindspace-Map.md",
]
TARGETS = [
    "https://github.com/CoCivium/CoPreGeneric",
    "https://CoCivium.org/CoPre",
    "https://InSeed.com/Stead",
]


class PublicDerivativeTests(unittest.TestCase):
    def test_four_named_files_and_index_exist(self):
        for f in FILES + ["INDEX.md"]:
            self.assertTrue((DIR / f).is_file(), f)
            self.assertGreater((DIR / f).stat().st_size, 500, f)

    def test_index_preserves_elected_targets_as_held(self):
        source = (DIR / "INDEX.md").read_text(encoding="utf-8")
        for url in TARGETS:
            self.assertIn(url, source)
        self.assertIn("unverified", source.lower())
        self.assertIn("NOT_ESTABLISHED", source)

    def test_no_raw_whatsapp_transcript_publication(self):
        for f in FILES + ["INDEX.md"]:
            text = (DIR / f).read_text(encoding="utf-8")
            self.assertNotIn("FROM: MetaAI-WhatsApp", text)
            self.assertNotIn("[4:30 PM, 11/9/2026]", text)
            self.assertNotIn("266,973", text)
            self.assertNotRegex(text, r"(?i)(password|api_key|private_key)\s*[:=]\s*\S{8}")

    def test_static_seed_does_not_claim_dynamic_worker(self):
        s = (DIR / FILES[0]).read_text(encoding="utf-8")
        self.assertIn("v8.58", s)
        self.assertIn("v8.76", s)
        self.assertIn("Seven-line drain", s)
        self.assertIn("not verified as operating mirrors", s)
        self.assertIn("STATIC_PASTE_NE_DYNAMIC_WORKER", s)

    def test_feedback_issues_are_explicitly_not_reproduced(self):
        s = (DIR / "CoFeedLoop-Devs.md").read_text(encoding="utf-8")
        for x in ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08"):
            self.assertIn(x, s)
        self.assertIn("USER", s.upper())
        self.assertIn("not a reproduced software defect", s.lower())

    def test_comparison_preserves_unknowns_and_rights(self):
        s = (DIR / "CoMindspace-Map.md").read_text(encoding="utf-8")
        self.assertIn("NOT_TESTED", s)
        self.assertIn("receiver_readproof", s)
        self.assertIn("independent_reviewer", s)
        self.assertIn("chain-of-thought", s)

    def test_ack_rewise_refuses_false_mirror(self):
        s = (DIR / "CoAckRewise-v8.74.md").read_text(encoding="utf-8")
        self.assertIn("THREE_IDENTICAL_MIRRORS=UNPROVEN", s)
        self.assertIn("ACK_NE_APPROVAL", s)
        self.assertIn("RECEIVER", s.upper())


if __name__ == "__main__":
    unittest.main()
