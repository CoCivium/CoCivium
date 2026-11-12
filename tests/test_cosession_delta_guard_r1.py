"""Adversarial source-turn replay dedupe, no live providers or OS effects."""
import copy
import json
from pathlib import Path
import sys
import unittest

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/"scripts"))
from CoSessionAutoTurnR1 import compile_turn
from CoSessionDeltaGuardR1 import compare, SCHEMA
NOW="2026-11-12T20:45:00Z"

def inputs():
    prior=compile_turn(REPO,NOW,"51","1","a"*40)
    current=compile_turn(REPO,NOW,"52","1","b"*40)
    meta={
        "repository":"CoCivium/CoCivium",
        "workflow_path":".github/workflows/cogoall-unattended-proof-pulse.yml",
        "retrieval_state":"VERIFIED_SUCCESSFUL_GITHUB_RUN_ARTIFACT",
        "conclusion":"success",
        "run_id":"51","attempt":"1","head_sha":"a"*40,
        "artifact_name":"cogoall-proof-51-1",
    }
    return current,prior,meta

class TestDeltaGuard(unittest.TestCase):
    def test_identical_source_quiet(self):
        c,p,m=inputs()
        r=compare(c,p,m)
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["state"],"QUIESCENT_NO_MATERIAL_SOURCE_CHANGE")
        self.assertEqual(r["source_delta_count"],0)
        self.assertIsNone(r["next_source_workid"])
        self.assertEqual(r["unchanged_workids_suppressed"],3)

    def test_elected_work_not_reannounced(self):
        c,p,m=inputs()
        r=compare(c,p,m)
        self.assertNotIn("elected",r)
        self.assertEqual(r["co_speedo"]["new_source_changes"],0)
        self.assertTrue(r["co_speedo"]["no_change_quiescence"])

    def test_change_lower_priority_elected_instead_of_stale_top(self):
        c,p,m=inputs()
        target=next(x for x in c["sources"] if x["role"]=="COMAP_PUBLIC_SOURCE_UX")
        target["source_sha256"]="e"*64
        r=compare(c,p,m)
        self.assertEqual(r["state"],"MATERIAL_PUBLIC_SOURCE_DELTA_SHADOW_ONLY")
        self.assertEqual(r["next_source_workid"],target["work_id"])
        self.assertEqual(r["source_delta_count"],1)
        self.assertEqual(r["unchanged_workids_suppressed"],2)

    def test_changed_workset_without_source_delta_is_new_configuration(self):
        c,p,m=inputs()
        c["input"]["sha256"]="f"*64
        r=compare(c,p,m)
        self.assertEqual(r["state"],"MATERIAL_PUBLIC_SOURCE_DELTA_SHADOW_ONLY")
        self.assertEqual(r["source_delta_count"],3)

    def test_priority_change_counts_as_delta(self):
        c,p,m=inputs()
        c["sources"][1]["priority"] += 1
        self.assertEqual(compare(c,p,m)["source_delta_count"],1)

    def test_no_prior_is_held_not_first_run(self):
        c,p,m=inputs()
        r=compare(c,None,m)
        self.assertEqual(r["state"],"HOLD_PRIOR_OR_SOURCE_UNQUALIFIED")
        self.assertIsNone(r["next_source_workid"])

    def test_no_verified_prior_metadata_holds(self):
        c,p,m=inputs()
        m["retrieval_state"]="LOCAL_UNVERIFIED"
        self.assertEqual(compare(c,p,m)["reason"],"NO_VERIFIED_PRIOR_GITHUB_RUN")

    def test_failed_prior_run_does_not_anchor(self):
        c,p,m=inputs()
        m["conclusion"]="failure"
        self.assertEqual(compare(c,p,m)["reason"],"PRIOR_PROVENANCE_OR_ORDER")

    def test_synthetic_prior_run_id_collision_held(self):
        c,p,m=inputs()
        c["run"]["run_id"]=p["run"]["run_id"]
        self.assertEqual(compare(c,p,m)["reason"],"PRIOR_PROVENANCE_OR_ORDER")

    def test_future_prior_run_rejected(self):
        c,p,m=inputs()
        p["run"]["run_id"]="53"
        m["run_id"]="53";m["artifact_name"]="cogoall-proof-53-1"
        self.assertEqual(compare(c,p,m)["reason"],"PRIOR_PROVENANCE_OR_ORDER")

    def test_prior_head_sha_drift_held(self):
        c,p,m=inputs()
        m["head_sha"]="c"*40
        self.assertEqual(compare(c,p,m)["reason"],"PRIOR_PROVENANCE_OR_ORDER")

    def test_prior_attempt_drift_held(self):
        c,p,m=inputs()
        m["attempt"]="2";m["artifact_name"]="cogoall-proof-51-2"
        self.assertEqual(compare(c,p,m)["reason"],"PRIOR_PROVENANCE_OR_ORDER")

    def test_untrusted_repository_held(self):
        c,p,m=inputs()
        m["repository"]="Someone/Other"
        self.assertEqual(compare(c,p,m)["reason"],"PRIOR_PROVENANCE_OR_ORDER")

    def test_bad_source_digest_held(self):
        c,p,m=inputs()
        c["sources"][0]["source_sha256"]="NOT_A_DIGEST"
        self.assertEqual(compare(c,p,m)["reason"],"CURRENT_SOURCE_DIGEST")

    def test_forged_live_approval_fails(self):
        c,p,m=inputs()
        c["sources"][0]["native_effect_authorized"]=True
        self.assertEqual(compare(c,p,m)["reason"],"CURRENT_SOURCE_AUTHORITY")

    def test_fake_external_ack_fails(self):
        c,p,m=inputs()
        c["receiver_ack"]=True
        self.assertEqual(compare(c,p,m)["reason"],"CURRENT_UNSUPPORTED_RUNTIME_EFFECT")

    def test_forged_provider_tabs_started_fails(self):
        c,p,m=inputs()
        c["co_speedo"]["provider_tabs_cycled"]=30
        self.assertEqual(compare(c,p,m)["reason"],"CURRENT_FORBIDDEN_PROCESS_OR_PROVIDER_EFFECT")

    def test_no_secret_reflection(self):
        c,p,m=inputs()
        c["secret_ignored"]="a_fake_access_token_NEVER_ECHO"
        out=json.dumps(compare(c,p,m))
        self.assertNotIn("NEVER_ECHO",out)

    def test_idempotent_without_mutation(self):
        c,p,m=inputs()
        b=copy.deepcopy((c,p,m))
        self.assertEqual(compare(c,p,m),compare(c,p,m))
        self.assertEqual((c,p,m),b)

    def test_one_removed_workid_reports_tombstone_no_action(self):
        c,p,m=inputs()
        c["sources"].pop()
        c["input"]["work_item_count"]=2
        r=compare(c,p,m)
        self.assertEqual(r["source_delta_count"],1)
        self.assertEqual(len(r["removed_workids"]),1)
        self.assertIsNone(r["next_source_workid"])
        self.assertFalse(r["new_machine_effect_authorized"])

    def test_bounded_no_effect_in_all_branches(self):
        c,p,m=inputs()
        for prior,meta in [(p,m),(None,m),(p,{})]:
            r=compare(c,prior,meta)
            self.assertFalse(r["new_machine_effect_authorized"])
            self.assertFalse(r["external_receiver_ack"])
            self.assertEqual(r["provider_sessions_cycled"],0)

if __name__=="__main__":
    unittest.main()
