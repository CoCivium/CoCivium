"""No-effect CoRel/CoBraid frontier tests using synthetic WorkIDs only."""
from __future__ import annotations
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / "scripts" / "CoRelBraidFrontierR0.py"
spec = importlib.util.spec_from_file_location("cobraid_frontier", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def task(id, deps=(), state="CANDIDATE", mutation="READ_ONLY", domain=None, priority=3):
    return {
        "id":id, "depends_on":list(deps), "state":state,
        "mutation_class":mutation, "collision_domain":domain or id,
        "source_ref":"fixture:"+id, "source_sha256":"a"*64,
        "receipt_ref":"fixture:unverified:"+id if state=="DECLARED_DONE" else None,
        "priority":priority,
    }


def payload():
    return {"schema":mod.SCHEMA, "work_id":"synthetic:CoPre:1",
            "source_revision":"b"*64, "max_parallel":3, "tasks":[
              task("seed",state="DECLARED_DONE"),
              task("source_check",["seed"],domain="source",priority=0),
              task("challenge",["seed"],domain="challenge",priority=1),
              task("media",["seed"],domain="media",priority=2),
              task("outreach",["source_check"],mutation="EFFECT_GATED",priority=3),
              task("receiver_result",["outreach"],priority=4),
              task("other",["seed"],domain="source",priority=5),
            ]}


class Tests(unittest.TestCase):
    def test_parallel_independent_fronts(self):
        result=mod.compile_frontier(payload())
        self.assertEqual([t["id"] for t in result["logical_parallel_frontier"]],
                         ["source_check","challenge","media"])
    def test_sequential_dependency_held(self):
        result=mod.compile_frontier(payload())
        self.assertIn("DEP_NOT_DECLARED_DONE:source_check",
                      next(t["reasons"] for t in result["deferred"] if t["id"]=="outreach"))
    def test_gate_held_and_unrelated_ready(self):
        x=payload();x["tasks"][4]["depends_on"]=[]
        z=mod.compile_frontier(x)
        self.assertIn("EFFECT_AUTHORITY_UNAVAILABLE",
                      next(t["reasons"] for t in z["deferred"] if t["id"]=="outreach"))
        self.assertEqual(len(z["logical_parallel_frontier"]),3)
    def test_no_actual_workers(self):
        z=mod.compile_frontier(payload())
        self.assertEqual(z["metrics"]["active_workers"],0)
        self.assertEqual(z["metrics"]["external_effects"],0)
        self.assertEqual(z["metrics"]["receiver_acks"],0)
    def test_deterministic_permutation(self):
        a=payload();b=deepcopy(a);b["tasks"].reverse()
        aa=mod.compile_frontier(a);bb=mod.compile_frontier(b)
        for field in ("logical_parallel_frontier","deferred","collision_or_budget_held",
                      "causal_levels_potential_only"):
            self.assertEqual(aa[field],bb[field])
    def test_budget_limits(self):
        x=payload();x["max_parallel"]=1
        z=mod.compile_frontier(x)
        self.assertEqual(len(z["logical_parallel_frontier"]),1)
        self.assertEqual(len(z["collision_or_budget_held"]),3)
    def test_collision_limit(self):
        x=payload();x["max_parallel"]=8
        z=mod.compile_frontier(x)
        self.assertEqual(len(z["logical_parallel_frontier"]),3)
        self.assertEqual(z["collision_or_budget_held"][0]["reason"],
                         "COLLISION_DOMAIN_ALREADY_ELECTED")
    def test_cycle_denied(self):
        x=payload();x["tasks"][0]["depends_on"]=["receiver_result"]
        with self.assertRaisesRegex(mod.Hold,"CAUSAL_CYCLE_REJECTED"):
            mod.compile_frontier(x)
    def test_self_edge_denied(self):
        x=payload();x["tasks"][1]["depends_on"]=["source_check"]
        with self.assertRaisesRegex(mod.Hold,"UNKNOWN_OR_SELF_DEPENDENCY"):
            mod.compile_frontier(x)
    def test_unknown_dependency_denied(self):
        x=payload();x["tasks"][1]["depends_on"]=["lost"]
        with self.assertRaisesRegex(mod.Hold,"UNKNOWN_OR_SELF_DEPENDENCY"):
            mod.compile_frontier(x)
    def test_duplicate_task_id_denied(self):
        x=payload();x["tasks"].append(deepcopy(x["tasks"][1]))
        with self.assertRaisesRegex(mod.Hold,"DUPLICATE_OR_MALFORMED_TASK"):
            mod.compile_frontier(x)
    def test_undeclared_receipt_denied(self):
        x=payload();x["tasks"][1]["receipt_ref"]="fake"
        with self.assertRaisesRegex(mod.Hold,"NON_DONE_MUST_NOT_HAVE_RECEIPT"):
            mod.compile_frontier(x)
    def test_declared_done_receipt_required(self):
        x=payload();x["tasks"][0]["receipt_ref"]=None
        with self.assertRaisesRegex(mod.Hold,"DONE_REQUIRES_DECLARED_RECEIPT"):
            mod.compile_frontier(x)
    def test_effect_cannot_be_marked_done(self):
        x=payload();x["tasks"][0]["mutation_class"]="EFFECT_GATED"
        with self.assertRaisesRegex(mod.Hold,"EFFECT_CANNOT_BE_SELF_CERTIFIED_DONE"):
            mod.compile_frontier(x)
    def test_source_revision_required(self):
        x=payload();x["source_revision"]="unknown"
        with self.assertRaisesRegex(mod.Hold,"INVALID_SOURCE_REVISION"):
            mod.compile_frontier(x)
    def test_source_task_sha_required(self):
        x=payload();x["tasks"][1]["source_sha256"]="unknown"
        with self.assertRaisesRegex(mod.Hold,"SOURCE_SHA_REQUIRED"):
            mod.compile_frontier(x)
    def test_held_task_not_elected(self):
        x=payload();x["tasks"][1]["state"]="HELD"
        z=mod.compile_frontier(x)
        self.assertNotIn("source_check",[t["id"] for t in z["logical_parallel_frontier"]])
        self.assertIn("TASK_HELD",next(t["reasons"] for t in z["deferred"]
                                      if t["id"]=="source_check"))
    def test_zero_budget_rejected(self):
        x=payload();x["max_parallel"]=0
        with self.assertRaisesRegex(mod.Hold,"INVALID_BUDGET"):
            mod.compile_frontier(x)
    def test_true_is_not_int_budget(self):
        x=payload();x["max_parallel"]=True
        with self.assertRaisesRegex(mod.Hold,"INVALID_BUDGET"):
            mod.compile_frontier(x)
    def test_no_claim_of_independent_proof(self):
        z=mod.compile_frontier(payload())
        self.assertEqual(z["declared_complete_unverified"][0]["status"],
                         "DECLARED_ONLY_NOT_INDEPENDENTLY_VERIFIED")
        self.assertEqual(z["logical_parallel_frontier"][0]["actual_source_readproof"],
                         "NOT_OBSERVED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
