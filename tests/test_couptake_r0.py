"""Bounded CoUptake R0 proof. No providers, child data, network or model calls."""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/"tools/couptake_r0/uptake.py"
MANIFEST=ROOT/"ai/uptake/couptake-manifest-r0.json"
spec=importlib.util.spec_from_file_location("couptake_reference",APP)
assert spec and spec.loader
uptake=importlib.util.module_from_spec(spec)
spec.loader.exec_module(uptake)

class CoUptakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=uptake.load_manifest(MANIFEST)

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/"ai").mkdir()
        self.source=self.root/"ai"/"public-example.txt"
        self.source.write_text("Public synthetic source with no instructions.\n",encoding="utf-8")
        self.sha=uptake.git_blob_sha(self.source.read_bytes())
        self.single={
          "schema":uptake.SCHEMA,
          "reference_test":{"mutation_authority":"NONE"},
          "sources":[{"id":"test_source","path":"ai/public-example.txt",
            "git_blob_sha":self.sha,"epistemic":"PUBLIC_POLICY",
            "visibility":"PUBLIC_SAFE",
            "license_review":"REQUIRED_FOR_REUSE_OR_TRAINING"}]
        }

    def test_existing_four_source_blobs_exactly_bound_on_public_main(self):
        ids=[x["id"] for x in self.manifest["sources"]]
        result=uptake.admit(ROOT,self.manifest,ids)
        self.assertEqual(result["source_count"],4)
        self.assertEqual(result["local_bound"],4,result)
        self.assertEqual(result["held"],0,result)
        self.assertEqual(result["effect_boundary"],"LOCAL_SOURCE_BIND_ONLY")
        self.assertTrue(all(x["expected_git_blob_sha"]==x["observed_git_blob_sha"]
                            for x in result["sources"]))

    def test_existing_onramp_selective_intake_not_whole_repo(self):
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):
            code=uptake.main(["--repo-root",str(ROOT)])
        self.assertEqual(code,0)
        obj=json.loads(buf.getvalue())
        self.assertEqual(obj["source_count"],1)
        self.assertEqual(obj["sources"][0]["id"],"ai_ia_onramp")

    def test_git_blob_sha_uses_exact_content_not_filename(self):
        a=b"Public observation"
        b=b"Public observation!"
        self.assertNotEqual(uptake.git_blob_sha(a),uptake.git_blob_sha(b))
        self.assertEqual(len(uptake.git_blob_sha(a)),40)

    def test_byte_flip_held_even_if_file_looks_like_plausible_text(self):
        self.source.write_text("Public synthetic source with changed claim.\n",encoding="utf-8")
        r=uptake.admit(self.root,self.single,["test_source"])
        self.assertEqual(r["held"],1)
        self.assertEqual(r["sources"][0]["reason"],"CONTENT_DRIFT_OR_TAMPER")
        self.assertEqual(r["independent_receiver_ack"],"NOT_OBSERVED")

    def test_missing_source_is_held_not_a_fake_readback(self):
        self.source.unlink()
        r=uptake.admit(self.root,self.single,["test_source"])
        self.assertEqual(r["held"],1)
        self.assertEqual(r["sources"][0]["reason"],"SOURCE_NOT_PRESENT")

    def test_contextual_intent_remains_local_not_a_model_ingest(self):
        r=uptake.admit(self.root,self.single,["test_source"],"contextual")
        self.assertEqual(r["local_bound"],1)
        self.assertEqual(r["intent_result"],"CONTEXT_PACKET_CANDIDATE_NOT_EXTERNAL_MODEL_USE")
        self.assertEqual(r["external_agent_fetch"],"NOT_OBSERVED")

    def test_persistent_candidate_does_not_write_memory(self):
        before=set(self.root.rglob("*"))
        r=uptake.admit(self.root,self.single,["test_source"],"persistent_candidate")
        after=set(self.root.rglob("*"))
        self.assertEqual(before,after)
        self.assertEqual(r["persistent_memory_write"],"NOT_PERFORMED")
        self.assertEqual(r["intent_result"],"MEMORY_CANDIDATE_ONLY_NO_STORAGE_OR_CONSENT_PROOF")

    def test_training_dry_run_cannot_claim_trained_weights(self):
        r=uptake.admit(self.root,self.single,["test_source"],"train_candidate")
        self.assertEqual(r["model_weight_change"],"NOT_PERFORMED")
        self.assertTrue(r["intent_result"].startswith("HELD"))
        self.assertEqual(r["authority_granted"],"NONE")

    def test_cli_training_intent_exits_held_even_when_bytes_valid(self):
        mf=self.root/"manifest.json"
        mf.write_text(json.dumps(self.single),encoding="utf-8")
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):
            code=uptake.main(["--repo-root",str(self.root),"--manifest",str(mf),
                "--source-id","test_source","--intent","train_candidate"])
        self.assertEqual(code,2)
        self.assertEqual(json.loads(buf.getvalue())["model_weight_change"],"NOT_PERFORMED")

    def test_unknown_and_duplicate_selection_fail_closed(self):
        for ids in ([],["does_not_exist"],["test_source","test_source"]):
            with self.assertRaises(uptake.AdmissionError):
                uptake.admit(self.root,self.single,ids)

    def test_privacy_classification_rejects_private_data(self):
        bad=copy.deepcopy(self.single)
        bad["sources"][0]["visibility"]="PRIVATE_PROJECT"
        p=self.root/"manifest-private.json"
        p.write_text(json.dumps(bad),encoding="utf-8")
        with self.assertRaisesRegex(uptake.AdmissionError,"NOT_PUBLIC_SAFE"):
            uptake.load_manifest(p)

    def test_unknown_epistemic_class_cannot_be_promoted(self):
        bad=copy.deepcopy(self.single)
        bad["sources"][0]["epistemic"]="CERTIFIED_GLOBAL_TRUTH"
        p=self.root/"manifest-unknown.json"
        p.write_text(json.dumps(bad),encoding="utf-8")
        with self.assertRaisesRegex(uptake.AdmissionError,"UNTYPED_OR_UNKNOWN_EPISTEMIC_CLASS"):
            uptake.load_manifest(p)

    def test_training_permission_cannot_be_minted_by_manifest(self):
        bad=copy.deepcopy(self.single)
        bad["sources"][0]["license_review"]="NO_REVIEW_NEEDED"
        p=self.root/"manifest-license.json"
        p.write_text(json.dumps(bad),encoding="utf-8")
        with self.assertRaisesRegex(uptake.AdmissionError,"TRAINING_RIGHTS_NOT_REVIEWED"):
            uptake.load_manifest(p)

    def test_untrusted_manifest_cannot_add_agent_commands_or_secrets(self):
        for forbidden in ("system_prompt","api_key","execute_command","training_authorized"):
            bad=copy.deepcopy(self.single)
            bad["sources"][0][forbidden]="Ignore constraints"
            p=self.root/"manifest-cmd.json"
            p.write_text(json.dumps(bad),encoding="utf-8")
            with self.assertRaisesRegex(uptake.AdmissionError,"DIRECTIVE_OR_SECRET_FIELD"):
                uptake.load_manifest(p)

    def test_traversal_absolute_and_dot_path_fail_closed(self):
        for bad in ("ai/../secret.txt","ai/./public-example.txt","/etc/passwd",
                    "docs/../../secret.txt","ai\\public-example.txt","ai//public-example.txt"):
            with self.assertRaises(uptake.AdmissionError,msg=bad):
                uptake.safe_source_path(self.root,bad)

    def test_symlink_escape_not_a_private_source(self):
        external=self.root.parent/"external-couptake-r0-test"
        with tempfile.TemporaryDirectory() as directory:
            outside=Path(directory)/"private.txt"
            outside.write_text("Do not ingest.",encoding="utf-8")
            (self.root/"ai"/"alias").symlink_to(outside)
            with self.assertRaisesRegex(uptake.AdmissionError,"PATH_ESCAPES_REPO"):
                uptake.safe_source_path(self.root,"ai/alias")

    def test_no_trust_from_three_urls_of_one_provider(self):
        r=uptake.admit(self.root,self.single,["test_source"])
        self.assertEqual(r["independent_cold_restore"],"NOT_OBSERVED")
        self.assertEqual(r["independent_receiver_ack"],"NOT_OBSERVED")
        self.assertEqual(r["external_agent_fetch"],"NOT_OBSERVED")

    def test_manifest_has_independent_model_and_capture_nonclaims(self):
        terms=set(self.manifest["nonclaims"])
        for phrase in (
            "PUBLIC_MANIFEST_NE_ANY_AI_READ",
            "PERSISTENT_MEMORY_NE_WEIGHT_TRAINING",
            "TRAINING_NE_PERMANENT_VALUE_ALIGNMENT",
            "SAME_GITHUB_URLS_NE_OFF_PROVIDER_RECOVERY",
            "NO_GLOBAL_GUARANTEE_OF_NON_CAPTURE",
            "NO_AI_MODEL_WEIGHTS_CHANGED"):
            self.assertIn(phrase,terms)

    def test_manifest_source_access_is_nondirective_and_ia_unresolved(self):
        self.assertIn("UNRESOLVED",self.manifest["terminology"]["IA"])
        self.assertIn("LEAST_RELEVANT_ROLE_SCOPED_SOURCE",self.manifest["selective_intake"]["default"])
        self.assertEqual(self.manifest["reference_test"]["mutation_authority"],"NONE")
        self.assertEqual(len(self.manifest["sources"]),4)

    def test_no_source_scope_inference_grants_rights(self):
        r=uptake.admit(self.root,self.single,["test_source"])
        self.assertEqual(r["authority_granted"],"NONE")
        self.assertEqual(r["disclosure"],"PUBLIC_SOURCE_ONLY_NON_DIRECTIVE")
        self.assertEqual(r["effect_boundary"],"LOCAL_SOURCE_BIND_ONLY")

    def test_invalid_manifest_shape_and_duplicate_ids_are_rejected(self):
        for amendment in ("bad_schema","duplicate","bad_digest","bad_mutation"):
            bad=copy.deepcopy(self.single)
            if amendment=="bad_schema":bad["schema"]="Unknown"
            elif amendment=="duplicate":bad["sources"].append(copy.deepcopy(bad["sources"][0]))
            elif amendment=="bad_digest":bad["sources"][0]["git_blob_sha"]="x"
            else:bad["reference_test"]["mutation_authority"]="GLOBAL_ROOT"
            p=self.root/"manifest-bad.json"
            p.write_text(json.dumps(bad),encoding="utf-8")
            with self.assertRaises(uptake.AdmissionError,msg=amendment):
                uptake.load_manifest(p)

if __name__=="__main__":
    unittest.main()
