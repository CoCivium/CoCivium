"""Bounded CoAllBloom R0 source/negative controls."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("coallbloom_r0",ROOT/"bloom.py")
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class BloomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed=b.load_seed(ROOT/"seed.json")
        cls.result=b.make(cls.seed)

    def test_source_shape(self): self.assertEqual(self.seed["schema"],b.SCHEMA)
    def test_pinned_donors(self): self.assertEqual(len(self.seed["source_donors"]),5)
    def test_seed_digest(self): self.assertEqual(self.result["seed_sha256"],b.digest(self.seed))
    def test_exact_ten(self): self.assertEqual(self.result["generated_count"],10)
    def test_kinds_unique(self): self.assertEqual({x["operator"] for x in self.result["candidates"]},set(b.KINDS))
    def test_id_unique(self): self.assertEqual(len({x["id"] for x in self.result["candidates"]}),10)
    def test_ranking_complete(self): self.assertEqual(len(self.result["ranking"]),10)
    def test_score_order(self): self.assertEqual([z["score"] for z in self.result["ranking"]], sorted([z["score"] for z in self.result["ranking"]],reverse=True))
    def test_factor_only_score(self):
        # No text, operator or epistemic class appears in the scoring API.
        self.assertEqual(b.score(b.DESIGNS[0][4]),self.result["candidates"][0]["shadow_score"])
        self.assertEqual(b.score((3,4,5,1,2)), 3*3+3*4+2*5-3*1-2)
    def test_one_election(self): self.assertEqual(self.result["elected_shadow_candidate"]["operator"],"CONVENTIONAL_SOURCE_CHECK")
    def test_election_not_execution(self): self.assertEqual(self.result["elected_shadow_candidate"]["status"],"ELECTED_FOR_SOURCE_ONLY_CHECK_NOT_EFFECT")
    def test_zero_workers(self): self.assertEqual(self.result["active_model_workers"],0)
    def test_zero_sends(self): self.assertEqual(self.result["external_sends"],0)
    def test_no_authority(self): self.assertTrue(all(x["authority"]=="NONE" for x in self.result["candidates"]))
    def test_no_effect_promotion(self): self.assertTrue(all(x["effect_state"]=="NOT_RUN" for x in self.result["candidates"]))
    def test_no_receiver_ack(self): self.assertTrue(all(x["receiver_ack"]=="UNPROVEN" for x in self.result["candidates"]))
    def test_all_real_world_held(self): self.assertTrue(all(x["real_world_claim"]=="HELD" for x in self.result["candidates"]))
    def test_symbolic_distinct_from_empirical(self):
        kinds={z["operator"]:z["epistemic_class"] for z in self.result["candidates"]}
        self.assertEqual(kinds["SPIRITUAL_SYMBOLIC"],b.NONEMP)
        self.assertEqual(kinds["PHYSICAL_MEASURABLE"],b.EMPR)
        self.assertNotEqual(kinds["ET_GD_INTERPRETATION"],b.EMPR)
    def test_null_distinct_from_negative(self):
        self.assertNotEqual(next(x for x in self.result["candidates"] if x["operator"]=="NULL")["meaning"], next(x for x in self.result["candidates"] if x["operator"]=="INVERSION")["meaning"])
    def test_falsifier_exists(self): self.assertTrue(any(x["operator"]=="FALSIFIER" for x in self.result["candidates"]))
    def test_deterministic_second_run(self): self.assertEqual(b.canon(b.make(self.seed)),b.canon(b.make(self.seed)))
    def test_frozen_json_equal(self): self.assertEqual((ROOT/"first_proof.json").read_bytes(),b.canon(self.result))
    def test_no_et_scope_omits_branch(self):
        s=copy.deepcopy(self.seed);s["contextual_et_gd_lane"]=False
        v=b.make(s)
        self.assertEqual(v["generated_count"],9)
        self.assertFalse(any(x["operator"]=="ET_GD_INTERPRETATION" for x in v["candidates"]))
    def test_scope_change_ids_change(self):
        s=copy.deepcopy(self.seed);s["purpose"] += " and recover safely"
        self.assertNotEqual(b.make(s)["seed_sha256"],self.result["seed_sha256"])
    def test_missing_private_source_refused(self):
        s=copy.deepcopy(self.seed);s["raw_private_keys"]="xyz"
        with self.assertRaisesRegex(ValueError,"HOLD_SEED_FIELDS"):b.make(s)
    def test_wrong_authority_refused(self):
        s=copy.deepcopy(self.seed);s["authority"]="SEND"
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_SCOPE_AUTHORITY"):b.make(s)
    def test_wrong_privacy_refused(self):
        s=copy.deepcopy(self.seed);s["scope"]="PRIVATE"
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_SCOPE_AUTHORITY"):b.make(s)
    def test_fake_recipient_ack_refused(self):
        s=copy.deepcopy(self.seed);s["recipient"]="ACKED"
        with self.assertRaisesRegex(ValueError,"HOLD_RECEIVER_OR_EVIDENCE_STATUS"):b.make(s)
    def test_duplicate_donor_refused(self):
        s=copy.deepcopy(self.seed);s["source_donors"].append(copy.deepcopy(s["source_donors"][0]))
        with self.assertRaisesRegex(ValueError,"HOLD_DONOR_PATH"):b.make(s)
    def test_donor_path_traversal_refused(self):
        s=copy.deepcopy(self.seed);s["source_donors"][0]["path"]="../secret.txt"
        with self.assertRaisesRegex(ValueError,"HOLD_DONOR_PATH"):b.make(s)
    def test_bad_git_sha_refused(self):
        s=copy.deepcopy(self.seed);s["source_donors"][0]["git_blob"]="0"*64
        with self.assertRaisesRegex(ValueError,"HOLD_DONOR_HASH"):b.make(s)
    def test_invalid_factor_refused(self):
        with self.assertRaisesRegex(ValueError,"HOLD_SCORE_AXES"):b.score((6,0,0,0,0))
    def test_boolean_factor_refused(self):
        with self.assertRaisesRegex(ValueError,"HOLD_SCORE_AXES"):b.score((True,0,0,0,0))
    def test_git_blob_standard_vector(self):
        self.assertEqual(b.git_blob(b"test\n"),"9daeafb9864cf43055ae93beb0afd6c7d144bfa4")
    def test_donor_drift_catches(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            s=copy.deepcopy(self.seed)
            s["source_donors"]=[{"path":"example.txt","git_blob":b.git_blob(b"current")},{"path":"other.txt","git_blob":b.git_blob(b"second")},{"path":"third.txt","git_blob":b.git_blob(b"third")}]
            (root/"example.txt").write_bytes(b"current")
            (root/"other.txt").write_bytes(b"second")
            (root/"third.txt").write_bytes(b"third")
            self.assertEqual(len(b.verify_donors(s,root)),3)
            (root/"third.txt").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError,"HOLD_DONOR_DRIFT"):b.verify_donors(s,root)
    def test_missing_donor_catches(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"HOLD_MISSING_OR_UNSAFE_DONOR"):b.verify_donors(self.seed,td)
    def test_exclusive_no_clobber(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"one.json"
            proc=[sys.executable,str(ROOT/"bloom.py"),"--seed",str(ROOT/"seed.json"),"--output",str(path)]
            a=subprocess.run(proc,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.assertEqual(a.returncode,0)
            again=subprocess.run(proc,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.assertNotEqual(again.returncode,0)
            self.assertEqual(path.read_bytes(),b.canon(self.result))
    def test_offline_no_imported_network_libs(self):
        text=(ROOT/"bloom.py").read_text()
        for x in ["requests", "urllib", "socket", "http.client", "selenium", "pyautogui", "smtplib"]:
            self.assertNotIn("import "+x,text)

if __name__=="__main__":unittest.main()
