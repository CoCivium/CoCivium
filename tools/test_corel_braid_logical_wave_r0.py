#!/usr/bin/env python3
"""CoRel / CoBraid logical-wave inversion tests. No workers or sockets."""
from __future__ import annotations
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"tools/corel_braid_logical_wave_r0.py"
spec=importlib.util.spec_from_file_location("corel_braid",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SOURCE=ROOT/"fixtures/relations/corel_braid_logical_wave_r0.json"
def fixture(): return json.loads(SOURCE.read_text(encoding="utf-8"))
def rel(id,a,p,b,causal="unknown"):
    return {"rel_id":id,"subject":a,"predicate":p,"object":b,
            "causal_status":causal,"provenance":["fixture:independent-challenge"]}

class CoRelBraidTests(unittest.TestCase):
    def snapshot(self): return fixture()
    def assertHold(self,data,code):
        with self.assertRaisesRegex(m.Hold,code): m.plan(data)
    def test_three_distinct_parallel_read_only_candidates(self):
        out=m.plan(self.snapshot())
        self.assertEqual([a["work_id"] for a in out["parallel_review_candidates"]],
                         ["braid-challenge","speedo-review","x2-launcher-triage"])
    def test_no_effect_or_worker_launched(self):
        out=m.plan(self.snapshot())
        self.assertEqual(out["executed_worker_count"],0)
        self.assertEqual(out["external_effect_count"],0)
        self.assertEqual(out["mutations"],0)
        self.assertFalse(out["physical_scheduler_used"])
        self.assertFalse(out["receiver_ack"])
    def test_causal_claim_is_narrative_not_automatic_dependency(self):
        x=self.snapshot()
        x["relations"]=[e for e in x["relations"] if e["rel_id"]=="narrative-1"]
        out=m.plan(x)
        self.assertIn("narrative-1",out["nonordering_relation_ids"])
        self.assertIn("quiet-boot-effect",[v["work_id"] for v in out["parallel_review_candidates"]]
                      +out["ready_but_deferred"])
    def test_other_noncause_relations_are_nonordering(self):
        r=m.plan(self.snapshot())
        self.assertEqual(r["nonordering_relation_ids"],
                         ["narrative-1","narrative-2","narrative-3"])
    def test_fanin_waits_for_each_explicit_prerequisite_receipt(self):
        r=m.plan(self.snapshot())
        self.assertIn("braid-fanin-review",r["waiting_for_declared_source_receipts"])
        self.assertNotIn("braid-fanin-review",[a["work_id"] for a in r["parallel_review_candidates"]])
    def test_held_legacy_blocks_only_its_descendant(self):
        r=m.plan(self.snapshot())
        self.assertEqual(r["held"]["historical-unknown"],"HELD_SOURCE_OR_AUTHORITY")
        self.assertEqual(r["held"]["blocked-descendant"],"HELD_PREREQUISITE")
        self.assertEqual(len(r["parallel_review_candidates"]),3)
    def test_verified_source_claim_not_rerun(self):
        r=m.plan(self.snapshot())
        self.assertEqual(r["already_source_verified_claims"],["source-orientation"])
        self.assertNotIn("source-orientation",[w["work_id"] for w in r["parallel_review_candidates"]])
        self.assertFalse(r["source_bytes_refetched"])
    def test_same_collision_domain_cannot_run_in_same_tranche(self):
        x=self.snapshot()
        x["relations"]=[e for e in x["relations"] if e["rel_id"] not in ("dep-4","dep-5","dep-6","dep-7")]
        r=m.plan(x)
        selected=r["parallel_review_candidates"]
        self.assertEqual(len(set(v["collision_domain"] for v in selected)),len(selected))
        ids={v["work_id"] for v in selected}
        self.assertFalse({"quiet-boot-effect","x2-launcher-triage"}.issubset(ids))
    def test_budget_defers_without_discarding_other_ready(self):
        x=self.snapshot();x["max_parallel"]=1
        r=m.plan(x)
        self.assertEqual(len(r["parallel_review_candidates"]),1)
        self.assertEqual(len(r["ready_but_deferred"]),2)
    def test_logical_shadow_effect_gated_is_not_effect_authority(self):
        x=self.snapshot()
        x["work"]=[w for w in x["work"] if w["work_id"]!="x2-launcher-triage"
                   and w["work_id"]!="braid-fanin-review"]
        x["relations"]=[e for e in x["relations"] if e["subject"]!="x2-launcher-triage"
                        and e["object"]!="x2-launcher-triage" and e["subject"]!="braid-fanin-review"]
        r=m.plan(x)
        found=[*r["parallel_review_candidates"],*[{"work_id":i} for i in r["ready_but_deferred"]]]
        self.assertIn("quiet-boot-effect",[z["work_id"] for z in found])
        for z in r["parallel_review_candidates"]:
            if z["work_id"]=="quiet-boot-effect":
                self.assertEqual(z["review_lane"],"SHADOW_ONLY_NO_EFFECT_LEASE")
        self.assertEqual(r["external_effect_count"],0)
    def test_two_node_cycle_is_held_without_global_wait(self):
        x=self.snapshot()
        x["relations"].append(rel("loop-1","braid-challenge","REVIEW_DEPENDS_ON","speedo-review"))
        x["relations"].append(rel("loop-2","speedo-review","REVIEW_DEPENDS_ON","braid-challenge"))
        r=m.plan(x)
        self.assertEqual(r["actual_cycle_nodes"],["braid-challenge","speedo-review"])
        self.assertEqual(r["held"]["braid-fanin-review"],"HELD_PREREQUISITE")
        self.assertIn("x2-launcher-triage",[i["work_id"] for i in r["parallel_review_candidates"]])
    def test_cycle_descendant_is_not_part_of_cycle(self):
        x=self.snapshot()
        x["relations"].append(rel("loop-1","braid-challenge","REVIEW_DEPENDS_ON","speedo-review"))
        x["relations"].append(rel("loop-2","speedo-review","REVIEW_DEPENDS_ON","braid-challenge"))
        r=m.plan(x)
        self.assertNotIn("braid-fanin-review",r["actual_cycle_nodes"])
    def test_nonordering_causal_cycle_does_not_hold_work(self):
        x=self.snapshot()
        x["relations"].append(rel("other-cause","quiet-boot-effect","CAUSES","speedo-review","causal"))
        r=m.plan(x)
        self.assertFalse(r["actual_cycle_nodes"])
        self.assertEqual(len(r["parallel_review_candidates"]),3)
    def test_self_dependency_held(self):
        x=self.snapshot()
        x["relations"].append(rel("self","braid-challenge","REVIEW_DEPENDS_ON","braid-challenge"))
        self.assertHold(x,"HELD_SELF_DEPENDENCY")
    def test_dangling_dependency_held(self):
        x=self.snapshot()
        x["relations"].append(rel("dangling","braid-challenge","REVIEW_DEPENDS_ON","not-in-graph"))
        self.assertHold(x,"HELD_DANGLING_OR_RELATION_AS_WORK_ENDPOINT")
    def test_relation_as_endpoint_not_mistaken_for_work_item(self):
        x=self.snapshot()
        x["relations"].append(rel("meta",{"rel_ref":"dep-1"},"REVIEW_DEPENDS_ON","speedo-review"))
        self.assertHold(x,"HELD_DANGLING_OR_RELATION_AS_WORK_ENDPOINT")
    def test_conflict_in_identifiers_not_silent_dedupe(self):
        x=self.snapshot();x["work"].append(copy.deepcopy(x["work"][0]))
        self.assertHold(x,"HELD_DUPLICATE_OR_INVALID_WORK_ID")
    def test_duplicate_relation_id_held(self):
        x=self.snapshot();x["relations"].append(copy.deepcopy(x["relations"][0]))
        self.assertHold(x,"HELD_DUPLICATE_OR_INVALID_RELATION")
    def test_unknown_predicate_held(self):
        x=self.snapshot();x["relations"][0]["predicate"]="CAUSES_WORKER_TO_SPAWN"
        self.assertHold(x,"HELD_UNKNOWN_PREDICATE_OR_CAUSAL_STATUS")
    def test_unknown_causal_status_held(self):
        x=self.snapshot();x["relations"][0]["causal_status"]="CERTIFIED_CAUSAL"
        self.assertHold(x,"HELD_UNKNOWN_PREDICATE_OR_CAUSAL_STATUS")
    def test_provenance_required_not_just_nice_story(self):
        x=self.snapshot();x["relations"][0]["provenance"]=[]
        self.assertHold(x,"HELD_RELATION_PROVENANCE_REQUIRED")
    def test_complete_source_requires_both_hash_claims(self):
        x=self.snapshot();x["work"][0]["receipt_sha256"]=None
        self.assertHold(x,"HELD_MISSING_COMPLETION_RECEIPT_CLAIM")
    def test_open_source_requires_identity_hash(self):
        x=self.snapshot();x["work"][1]["source_sha256"]=None
        self.assertHold(x,"HELD_MISSING_SOURCE_PROOF_CLAIM")
    def test_unfinished_work_cannot_assert_receipt(self):
        x=self.snapshot();x["work"][1]["receipt_sha256"]="f"*64
        self.assertHold(x,"HELD_RECEIPT_WITHOUT_VERIFIED_STATE")
    def test_unknown_authority_class_held(self):
        x=self.snapshot();x["work"][1]["work_class"]="OWNER_GRANTED_ADMIN"
        self.assertHold(x,"HELD_INVALID_WORK_STATE")
    def test_raw_private_prompt_cannot_be_appended(self):
        x=self.snapshot();x["work"][1]["raw_user_message"]="private"
        self.assertHold(x,"HELD_UNKNOWN_WORK_FIELDS")
    def test_unknown_root_authority_field_held(self):
        x=self.snapshot();x["authority_granted"]=True
        self.assertHold(x,"HELD_CONTRACT_SCHEMA")
    def test_fanout_limit_enforced(self):
        x=self.snapshot();x["max_parallel"]=99
        self.assertHold(x,"HELD_UNBOUNDED_FANOUT")
    def test_budget_bool_not_an_integer(self):
        x=self.snapshot();x["max_parallel"]=True
        self.assertHold(x,"HELD_UNBOUNDED_FANOUT")
    def test_snapshot_digest_stable_under_key_order_and_unordered_input(self):
        x=self.snapshot()
        a=m.plan(x);b=m.plan(json.loads(json.dumps(x,sort_keys=True)))
        self.assertEqual(a["input_sha256"],b["input_sha256"])
        self.assertEqual(a["parallel_review_candidates"],b["parallel_review_candidates"])
    def test_unknown_scope_cannot_be_assumed_public(self):
        x=self.snapshot();x["scope"]="PRIVATE_CHAT_AUTODEPLOY"
        self.assertHold(x,"HELD_UNQUALIFIED_SCOPE")
    def test_causal_claim_is_not_supported_by_word_alone(self):
        out=m.plan(self.snapshot())
        self.assertIn("CAUSES_RELATION_NE_EXECUTION_DEPENDENCY",out["nonclaims"])
        self.assertIn("SOURCE_RECEIPT_CLAIM_NE_INDEPENDENT_READBACK",out["nonclaims"])
        self.assertFalse(out["receiver_ack"])
    def test_no_live_worker_calls_in_planner(self):
        source=MODULE.read_text(encoding="utf-8")
        for forbidden in ("subprocess.", "os.system(", "requests.get(", "urllib.request.",
                          "Start-Process", "Restart-Computer", "Disable-ScheduledTask",
                          "time.sleep(", "multiprocessing."):
            self.assertNotIn(forbidden,source)
        self.assertEqual(m.plan(self.snapshot())["state"],"LOGICAL_REVIEW_PLAN_NOT_EXECUTED")
    def test_future_dependency_can_unblock_after_declared_source_receipt(self):
        x=self.snapshot()
        triage=next(w for w in x["work"] if w["work_id"]=="x2-launcher-triage")
        triage["state"]="VERIFIED_SOURCE";triage["receipt_sha256"]="f"*64
        r=m.plan(x)
        self.assertIn("quiet-boot-effect",[w["work_id"] for w in r["parallel_review_candidates"]]
                      +r["ready_but_deferred"])
        self.assertNotIn("braid-fanin-review",[w["work_id"] for w in r["parallel_review_candidates"]])
    def test_noncausal_inverse_does_not_imply_symmetric_permission(self):
        x=self.snapshot()
        x["relations"].append(rel("other-inverse","speedo-review","INVERTS","braid-challenge","mixed"))
        r=m.plan(x)
        self.assertIn("other-inverse",r["nonordering_relation_ids"])
        self.assertEqual(r["external_effect_count"],0)

if __name__=="__main__":
    unittest.main()
