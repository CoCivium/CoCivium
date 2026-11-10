"""Adversarial, offline receiver-native views tests for CoPre R1.

These tests use only temporary local files and preserve all external effect
and authority boundaries. They do not establish independent receiver uptake.
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoPreReceiverViewsR1 import project, save_local_preview, git_blob_sha, build_portable_packet

SOURCE = ROOT / "ai/continuity/copre-synth-bio-gd-coterms-r1-20261109.json"
HUMAN = ROOT / "docs/CoPreGeneric/CoPre_SynthBio_Gd_CoTerms_Candidate_R1_20261109.md"


class ReceiverNativeViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_bytes()
        cls.human = HUMAN.read_text(encoding="utf-8")
        cls.obj = json.loads(cls.source)

    def mutated(self, change):
        x = copy.deepcopy(self.obj)
        change(x)
        return json.dumps(x, sort_keys=True).encode("utf-8")

    def test_two_distinct_roles_one_pinned_work_id(self):
        r = project(self.source, self.human)
        self.assertEqual(r["common"]["source_git_blob_sha"], git_blob_sha(self.source))
        self.assertEqual(r["synth"]["work_id"], r["common"]["work_id"])
        self.assertEqual(r["synth"]["source_git_blob_sha"], r["common"]["source_git_blob_sha"])
        self.assertIn(r["common"]["source_git_blob_sha"], r["bio"])
        self.assertEqual(len(r["synth"]["graph"]["nodes"]), 72)
        self.assertEqual(len(r["synth"]["graph"]["relations"]), 22)
        self.assertNotIn('"graph":', r["bio"])
        self.assertTrue(r["synth"]["translation_loss"]["bio_narrative_not_embedded"])
        self.assertEqual(r["loss_ledger"]["cross_projection_equivalence"], "UNTESTED")
        self.assertIsNone(r["synth"]["receiver_ack"])

    def test_independent_local_views_have_distinct_readback_receipts(self):
        views = project(self.source, self.human)
        with tempfile.TemporaryDirectory(prefix="copre-views-r1-") as tmp:
            root = Path(tmp) / "native"
            receipts = save_local_preview(root, views)
            self.assertEqual(set(receipts), {"synth", "bio"})
            self.assertNotEqual(receipts["synth"]["sha256"], receipts["bio"]["sha256"])
            for role, path in (
                ("synth", root / "synthetic-local-a/copre-r1-synth.json"),
                ("bio", root / "synthetic-local-b/copre-r1-bio.md"),
            ):
                self.assertTrue(path.is_file())
                raw = path.read_bytes()
                self.assertEqual(receipts[role]["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(receipts[role]["source_git_blob_sha"], git_blob_sha(self.source))
                self.assertEqual(receipts[role]["effect_authority"], "NONE")
                self.assertIsNone(receipts[role]["receiver_ack"])

            with self.assertRaises(FileExistsError):
                save_local_preview(root, views)  # never clobber same WorkID output

    def test_portable_packet_manifest_and_no_clobber(self):
        with tempfile.TemporaryDirectory(prefix="copre-portable-") as tmp:
            root = Path(tmp) / "handoff"
            receipt = build_portable_packet(root)
            self.assertEqual(receipt["state"], "LOCAL_PACKET_BUILT_READBACK_NOT_RECEIVER_PICKUP")
            self.assertEqual(receipt["file_count"], 5)
            self.assertEqual(receipt["external_effects"], 0)
            source = json.loads((root / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(source["work_id"], self.obj["work_id"])
            self.assertEqual(source["source"]["git_blob_sha"], git_blob_sha(self.source))
            self.assertIsNone(source["receiver_readproof"])
            self.assertEqual((root / "source/copre-r1-source.json").read_bytes(), self.source)
            self.assertEqual(source["readback"]["source"]["git_blob_sha"], git_blob_sha(self.source))
            self.assertEqual(source["lifecycle"], "TEMPORARY_CI_PREVIEW_NOT_DURABLE_RECEIVER_LANDING")
            self.assertEqual(source["effect_authority"], "NONE")
            self.assertIn("Next:", (root / "README.md").read_text(encoding="utf-8"))
            for role in ("source", "synth", "bio", "front_door"):
                observed = source["readback"][role]
                output_bytes = (root / observed["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(output_bytes).hexdigest(), observed["sha256"])
            self.assertEqual(
                hashlib.sha256((root / "receipt.json").read_bytes()).hexdigest(),
                receipt["receipt_sha256"],
            )
            with self.assertRaises(FileExistsError):
                build_portable_packet(root)

    def test_portable_packet_source_denial_does_not_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="copre-portable-guard-") as tmp:
            root = Path(tmp) / "handoff"
            root.mkdir()
            marker = root / "README.md"
            marker.write_text("existing prior", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                build_portable_packet(root)
            self.assertEqual(marker.read_text(encoding="utf-8"), "existing prior")

    def test_machine_graph_relation_authority_escalation_denied(self):
        changed = self.mutated(lambda d: d["relations"][0].update(effect_authority="ALL"))
        with self.assertRaises(ValueError):
            project(changed, self.human)

    def test_top_level_authority_escalation_denied(self):
        changed = self.mutated(lambda d: d.update(effect_authority="ALL"))
        with self.assertRaises(ValueError):
            project(changed, self.human)

    def test_unknown_relation_target_denied(self):
        changed = self.mutated(lambda d: d["relations"][0].update(to="unknown-target"))
        with self.assertRaises(ValueError):
            project(changed, self.human)

    def test_unqualified_canon_upgrade_denied(self):
        changed = self.mutated(lambda d: d["terms"][0].update(status="CANON"))
        with self.assertRaises(ValueError):
            project(changed, self.human)

    def test_missing_human_term_denied(self):
        changed = self.human.replace("**CoClaimAltitude+**", "CoClaimAltitude+")
        self.assertNotEqual(changed, self.human)
        with self.assertRaises(ValueError):
            project(self.source, changed)

    def test_missing_relation_in_human_view_denied(self):
        changed = self.human.replace("**DISTINGUISHES_SUPPORT_FROM_CLAIM**",
                                     "DISTINGUISHES_SUPPORT_FROM_CLAIM")
        self.assertNotEqual(changed, self.human)
        with self.assertRaises(ValueError):
            project(self.source, changed)

    def test_lost_nonclaim_denied(self):
        changed = self.mutated(
            lambda d: d["nonclaims"].remove("NO_INDEPENDENT_RECEIVER_PICKUP")
        )
        with self.assertRaises(ValueError):
            project(changed, self.human)

    def test_changed_source_keeps_distinct_identity(self):
        changed = self.mutated(
            lambda d: d["terms"][0].update(
                definition=d["terms"][0]["definition"] + " (candidate variant)"
            )
        )
        original = project(self.source, self.human)
        updated = project(changed, self.human)
        self.assertNotEqual(
            original["common"]["source_git_blob_sha"],
            updated["common"]["source_git_blob_sha"],
        )
        self.assertEqual(updated["common"]["work_id"], original["common"]["work_id"])
        # WorkID equality never implies content/revision equality.


if __name__ == "__main__":
    unittest.main()
