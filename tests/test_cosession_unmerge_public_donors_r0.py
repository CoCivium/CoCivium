"""CoUnmerge public-donor roundtrip against actual versioned repository bytes."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoSessionUnmergePublicDonorsR0 import (Hold, compile_projection, unmerge_rehydrate,
                                           git_blob_sha)

MANIFEST = ROOT / "ai/convergence/cosession-unmerge-public-donors-r0.json"


class UnmergePublicDonorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.projection = compile_projection(ROOT, cls.manifest)

    def test_exact_three_real_donor_roundtrip(self):
        p = self.projection
        self.assertEqual(p["coverage"]["source_records"], 3)
        self.assertEqual(p["coverage"]["distinct_source_defined_session_ids"], 3)
        self.assertEqual(len({r["delta_id"] for r in p["records"]}), 3)
        self.assertTrue(all(r["source_disposition"] == "PRESERVED_NOT_SUPERSEDED" for r in p["records"]))
        r = unmerge_rehydrate(ROOT, p)
        self.assertEqual(r["state"], "PASS_THREE_PUBLIC_GIT_DONOR_ROUNDTRIP__NO_SESSION_CLOSE")
        self.assertEqual(len(r["recovered"]), 3)
        self.assertFalse(r["external_receiver_ack"])
        self.assertFalse(r["private_provider_history_recovered"])
        self.assertFalse(p["close_safe"])
        self.assertFalse(p["delete_safe"])
        self.assertTrue(all(v == 0 for v in r["effects"].values()))

    def test_all_challenger_source_contradictions_retained(self):
        actual = []
        for row in self.manifest["records"]:
            source = json.loads((ROOT / row["path"]).read_text(encoding="utf-8"))
            actual.extend(source["contradictions"])
        self.assertEqual(self.projection["dissent"], actual)

    def test_compilation_is_idempotent(self):
        self.assertEqual(compile_projection(ROOT, self.manifest),
                         compile_projection(ROOT, copy.deepcopy(self.manifest)))

    def test_bad_identity_rejected(self):
        fixture = copy.deepcopy(self.manifest)
        fixture["records"][1]["session_id"] = "NotThisSession"
        with self.assertRaisesRegex(Hold, "HOLD_DONOR_IDENTITY"):
            compile_projection(ROOT, fixture)

    def test_bad_manifest_hash_rejected(self):
        fixture = copy.deepcopy(self.manifest)
        fixture["records"][0]["git_blob_sha"] = "f" * 40
        with self.assertRaisesRegex(Hold, "HOLD_SOURCE_BLOB_CHANGED"):
            compile_projection(ROOT, fixture)

    def test_duplicate_source_rejected(self):
        fixture = copy.deepcopy(self.manifest)
        fixture["records"][2] = copy.deepcopy(fixture["records"][0])
        with self.assertRaisesRegex(Hold, "HOLD_DUPLICATE_IDENTITY"):
            compile_projection(ROOT, fixture)

    def test_private_source_escape_rejected(self):
        fixture = copy.deepcopy(self.manifest)
        fixture["records"][0]["path"] = "../../private-chats.json"
        with self.assertRaisesRegex(Hold, "HOLD_SOURCE_SCOPE"):
            compile_projection(ROOT, fixture)

    def test_source_changed_after_compaction_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["records"][0]["source_git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(Hold, "HOLD_SOURCE_BLOB_CHANGED"):
            unmerge_rehydrate(ROOT, fixture)

    def test_selected_field_tamper_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["records"][0]["selected_fields"]["subject"] = "unearned fact"
        with self.assertRaisesRegex(Hold, "HOLD_SELECTED_FIELDS_CHANGED"):
            unmerge_rehydrate(ROOT, fixture)

    def test_sha256_projection_tamper_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["records"][0]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(Hold, "HOLD_REHYDRATION_DIGEST"):
            unmerge_rehydrate(ROOT, fixture)

    def test_forged_close_safe_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["close_safe"] = True
        with self.assertRaisesRegex(Hold, "HOLD_PROJECTION_EFFECT_GATE"):
            unmerge_rehydrate(ROOT, fixture)

    def test_forged_effect_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["effects"]["provider_sessions_deleted"] = 1
        with self.assertRaisesRegex(Hold, "HOLD_PROJECTION_EFFECT_GATE"):
            unmerge_rehydrate(ROOT, fixture)

    def test_dissent_erasure_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["dissent"] = []
        with self.assertRaisesRegex(Hold, "HOLD_DISSENT_LEDGER_CHANGED"):
            unmerge_rehydrate(ROOT, fixture)

    def test_duplicate_source_in_projection_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["records"][2] = copy.deepcopy(fixture["records"][0])
        with self.assertRaisesRegex(Hold, "HOLD_PROJECTION_DUPLICATE_DONOR"):
            unmerge_rehydrate(ROOT, fixture)

    def test_forged_success_state_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["state"] = "PROVIDER_SESSIONS_RECOVERED"
        with self.assertRaisesRegex(Hold, "HOLD_PROJECTION_STATE"):
            unmerge_rehydrate(ROOT, fixture)

    def test_evidence_class_tamper_rejected(self):
        fixture = copy.deepcopy(self.projection)
        fixture["records"][0]["epistemic_class"] = "PROVEN"
        with self.assertRaisesRegex(Hold, "HOLD_EVIDENCE_CLASS_CHANGED"):
            unmerge_rehydrate(ROOT, fixture)

    def test_missing_source_rejected(self):
        fixture = copy.deepcopy(self.manifest)
        fixture["records"][0]["path"] = "ai/evolution-deltas/MISSING_SOURCE.json"
        with self.assertRaisesRegex(Hold, "HOLD_MISSING_SOURCE"):
            compile_projection(ROOT, fixture)

    def test_in_root_symlink_donor_is_rejected_even_when_hash_matches(self):
        # Content hashes do not turn a symlink alias into a direct donor path.
        # Checking is_symlink() only after resolve() silently loses link identity.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for item in self.manifest["records"]:
                target = root / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / item["path"], target)
            original = Path(self.manifest["records"][0]["path"])
            alias = root / original.parent / "SYMLINK_DONOR.json"
            try:
                alias.symlink_to(original.name)
            except (OSError, NotImplementedError):
                self.skipTest("symlink unavailable")
            fixture = copy.deepcopy(self.manifest)
            fixture["records"][0]["path"] = (original.parent / alias.name).as_posix()
            with self.assertRaisesRegex(Hold, "HOLD_SYMLINK_SOURCE"):
                compile_projection(root, fixture)

    def test_out_of_scope_source_rejected(self):
        fixture = copy.deepcopy(self.manifest)
        fixture["records"][0]["path"] = "docs/Architecture/COSESSION_AUTOCYCLE_R0.md"
        with self.assertRaisesRegex(Hold, "HOLD_SOURCE_SCOPE"):
            compile_projection(ROOT, fixture)


if __name__ == "__main__":
    unittest.main(verbosity=2)
