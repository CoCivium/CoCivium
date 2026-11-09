#!/usr/bin/env python3
"""CoPreGeneric candidate evidence contract smoke test. No network or writes."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "ai/copregeneric/session-contribution-r0-20261109.json"
HUMAN = ROOT / "docs/Onramp/COPREGENERIC_SESSION_HANDOFF_R0_20261109.md"


class CoPreGenericContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = GRAPH.read_bytes()
        cls.data = json.loads(cls.raw)
        cls.doc = HUMAN.read_text(encoding="utf-8")
        cls.sources = {s["id"]: s for s in cls.data["source_manifest"]}
        cls.claims = {c["id"]: c for c in cls.data["contribution_claims"]}

    def test_valid_schema_and_unknown_receiver(self):
        d = self.data
        self.assertEqual(d["schema"], "CoCivium.CoPreGeneric.SessionContribution.R0")
        self.assertIn("CANDIDATE", d["state"])
        self.assertIsNone(d["receiver_status"]["exact_object_readproof"])
        self.assertFalse(d["receiver_status"]["integrated"])
        self.assertFalse(d["receiver_status"]["automatic_delivery"])

    def test_manifest_pins_and_unique_source_ids(self):
        self.assertEqual(len(self.sources), len(self.data["source_manifest"]))
        self.assertGreaterEqual(len(self.sources), 20)
        for s in self.sources.values():
            self.assertEqual(s["repo"], "CoCivium/CoCivium")
            self.assertRegex(s["git_blob_sha1"], r"^[0-9a-f]{40}$")
            self.assertEqual(s["exact_read_state"], "GITHUB_CONNECTOR_CONTENT_READ")
            self.assertNotIn("..", s["path"])
            self.assertIn(s["path"], s["provenance_locator"])

    def test_exact_preseed_alias_not_two_independent_sources(self):
        a, b = self.sources["copre-seed"], self.sources["copre-seed-alias"]
        self.assertEqual(a["git_blob_sha1"], b["git_blob_sha1"])
        self.assertEqual(b["duplicate_of"], "copre-seed")
        self.assertTrue(self.data["prior_reconciliation"]["duplicate_is_not_independent_confirmation"])

    def test_all_claims_source_bound_and_unpromoted(self):
        self.assertEqual(len(self.claims), len(self.data["contribution_claims"]))
        self.assertGreaterEqual(len(self.claims), 10)
        for claim in self.claims.values():
            self.assertTrue(claim["source_ids"])
            self.assertTrue(set(claim["source_ids"]).issubset(self.sources))
            self.assertTrue(claim["discriminator_or_falsifier"])
            self.assertTrue(claim["next_proof_gate"])
            self.assertEqual(claim["promotion_state"], "CANDIDATE_ONLY")

    def test_typed_edges_have_existing_endpoints(self):
        known = set(self.sources) | set(self.claims)
        for edge in self.data["typed_edges"]:
            self.assertIn(edge["from"], known)
            self.assertIn(edge["to"], known)
            self.assertRegex(edge["rel"], r"^[A-Z_]+$")

    def test_retro_is_bounded_and_explicitly_incomplete(self):
        r = self.data["retroactive_echo"]
        self.assertTrue(r["no_claim_of_recovered_history"])
        self.assertIn("NO_GLOBAL_BACKFILL_EXECUTED", r["status"])
        self.assertIn("UNKNOWN_REQUIRES_RECOVERY", r["dispositions"])
        self.assertIn("ORPHAN_RISK", r["dispositions"])
        self.assertIn("private_provider_sessions", r["unverified_coverage"])
        self.assertIn("Meta_AI_receiver", r["unverified_coverage"])

    def test_synth_bio_are_distinct_loss_aware_views(self):
        s = self.data["surfaces"]
        self.assertFalse(s["synth_native"]["humanized_persona_required"])
        self.assertTrue(s["translation"]["same_underlying_claim_ids"])
        self.assertFalse(s["translation"]["shared_authority"])
        self.assertEqual(s["translation"]["roundtrip_test_state"], "NOT_EXECUTED")
        self.assertIn("epistemic_class", s["translation"]["loss_fields"])

    def test_nongrant_noclaims_and_source_not_ack(self):
        nc = set(self.data["nonclaims"])
        for required in ("PUBLIC_POINTER_NE_META_AI_READPROOF",
                         "COHERENCE_NE_SENTIENCE",
                         "GITHUB_PR_NE_CANON",
                         "GITHUB_SOURCE_NE_COEX",
                         "NO_ACCOUNT_OR_DEVICE_EFFECT"):
            self.assertIn(required, nc)
        self.assertEqual(self.data["session_external_effects"],
                         "PUBLIC_DRAFT_REPO_CANDIDATE_ONLY")

    def test_human_companion_cross_references(self):
        self.assertIn("CoHereNow", self.doc)
        self.assertIn("CoSynthVerse", self.doc)
        self.assertIn("CoBioVerse", self.doc)
        self.assertIn("CoFront", self.doc)
        self.assertIn("CoEcho", self.doc)
        self.assertIn("UNKNOWN_REQUIRES_RECOVERY", self.doc)
        self.assertIn("Meta AI", self.doc)
        self.assertIn("PR #402", self.doc)
        self.assertIn("not a deployed", self.doc.lower())


if __name__ == "__main__":
    unittest.main()
