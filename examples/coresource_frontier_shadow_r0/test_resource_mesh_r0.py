#!/usr/bin/env python3
"""Shadow-only tests; all fixtures are synthetic. No device or provider queried."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

import resource_mesh_r0 as m

BASE = Path(__file__).resolve().parent
FIXTURE = json.loads((BASE / "fixture.json").read_text(encoding="utf8"))

def fixture():
    return copy.deepcopy(FIXTURE)


def resource(d, rid):
    return next(r for r in d["resources"] if r["id"] == rid)


def task(d, tid):
    return next(t for t in d["tasks"] if t["id"] == tid)


class ShadowAllocationTests(unittest.TestCase):
    def out(self, d=None):
        return m.plan(fixture() if d is None else d)

    def test_01_schema(self):
        self.assertEqual(m.SCHEMA,"CoAll.CoResourceFrontier.ShadowAllocation.R0")

    def test_02_fixture_selects_two_only(self):
        x=self.out();self.assertEqual(len(x["selected"]),2)

    def test_03_fixture_does_not_select_offline_workstation(self):
        self.assertNotIn("busy_workstation",[x["resource_id"] for x in self.out()["selected"]])

    def test_04_fixture_preserves_recovery_first(self):
        self.assertEqual(self.out()["selected"][0]["task_id"],"preserve_failure_receipt")

    def test_05_held_unverified_power(self):
        self.assertEqual(dict((x["task_id"],x["reason"]) for x in self.out()["held"])["hypothetical_ambient_harvest"],"SPECULATIVE_OR_SYMBOLIC_NOT_EXECUTABLE_RESOURCE")

    def test_06_held_device_mutation(self):
        self.assertEqual(dict((x["task_id"],x["reason"]) for x in self.out()["held"])["physical_device_repair"],"CONSEQUENTIAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY")

    def test_07_held_unknown_energy(self):
        self.assertEqual(dict((x["task_id"],x["reason"]) for x in self.out()["held"])["unknown_power_gpu"],"UNKNOWN_ESTIMATED_COST")

    def test_08_held_heavy_work(self):
        self.assertEqual(dict((x["task_id"],x["reason"]) for x in self.out()["held"])["pressure_heavy_research"],"NO_CURRENT_ELIGIBLE_RESOURCE")

    def test_09_zero_effect_totals(self):
        x=self.out();self.assertTrue(all(v==0 for v in x["effect_totals"].values()))

    def test_10_never_runtime_authority(self):
        x=self.out();self.assertEqual(x["authority"],"NONE");self.assertFalse(x["receiver_ack"])
        self.assertTrue(all(z["status"]=="SHADOW_PROPOSAL_ONLY" and z["authority"]=="NONE" for z in x["selected"]))

    def test_11_pinned_synthetic_asof(self):
        self.assertEqual(self.out()["as_of"],"2026-10-27T06:00:00+00:00")

    def test_12_input_not_mutated(self):
        d=fixture();b=json.dumps(d,sort_keys=True);self.out(d);self.assertEqual(json.dumps(d,sort_keys=True),b)

    def test_13_deterministic_repetition(self):
        self.assertEqual(self.out(),self.out())

    def test_14_deterministic_input_permutation(self):
        d=fixture();d["tasks"].reverse();d["resources"].reverse()
        self.assertEqual(self.out()["selected"],self.out(d)["selected"])

    def test_15_missing_schema_fails(self):
        d=fixture();d["schema"]="unapproved";self.assertRaisesRegex(ValueError,"INVALID_SCHEMA",self.out,d)

    def test_16_duplicate_resource_fails(self):
        d=fixture();d["resources"].append(copy.deepcopy(d["resources"][0]));self.assertRaisesRegex(ValueError,"DUPLICATE_RESOURCE_ID",self.out,d)

    def test_17_duplicate_task_fails(self):
        d=fixture();d["tasks"].append(copy.deepcopy(d["tasks"][0]));self.assertRaisesRegex(ValueError,"DUPLICATE_TASK_ID",self.out,d)

    def test_18_duplicate_capability_fails(self):
        d=fixture();r=resource(d,"remote_mock");r["capabilities"].append("TEXT_REVIEW");self.assertRaisesRegex(ValueError,"DUPLICATE_CAPABILITY",self.out,d)

    def test_19_bad_output_privacy_fails(self):
        d=fixture();d["output_privacy"]="PUBLISHED";self.assertRaisesRegex(ValueError,"INVALID_OUTPUT_PRIVACY",self.out,d)

    def test_20_private_tasks_in_public_output_fails(self):
        d=fixture();d["output_privacy"]="PUBLIC";self.assertRaisesRegex(ValueError,"HELD_PRIVATE_TASK_IN_PUBLIC_OUTPUT",self.out,d)

    def test_21_private_resources_in_public_output_fails(self):
        d=fixture();d["tasks"]=[t for t in d["tasks"] if t["privacy"]=="PUBLIC"];d["output_privacy"]="PUBLIC"
        self.assertRaisesRegex(ValueError,"HELD_PRIVATE_RESOURCE_IN_PUBLIC_OUTPUT",self.out,d)

    def test_22_public_only_fixture_works(self):
        d=fixture();d["tasks"]=[t for t in d["tasks"] if t["privacy"]=="PUBLIC"]
        d["resources"]=[r for r in d["resources"] if r["privacy"]=="PUBLIC"]
        d["output_privacy"]="PUBLIC";self.assertEqual(self.out(d)["output_privacy"],"PUBLIC")

    def test_23_remote_cannot_serve_private_task(self):
        d=fixture();d["resources"]=[resource(d,"remote_mock")]
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_24_unknown_resource_blocked(self):
        d=fixture();resource(d,"isolated_local_cpu")["state"]="UNKNOWN"
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_25_offline_resource_blocked(self):
        d=fixture();resource(d,"isolated_local_cpu")["state"]="OFFLINE_DECLARED"
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_26_degraded_resource_blocked(self):
        d=fixture();resource(d,"isolated_local_cpu")["health"]="DEGRADED_DECLARED"
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_27_unverified_capacity_blocked(self):
        d=fixture();resource(d,"isolated_local_cpu")["basis"]="DECLARED_UNVERIFIED"
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_28_stale_resource_blocked(self):
        d=fixture();resource(d,"isolated_local_cpu")["observed_at"]="2026-10-27T04:00:00Z"
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_29_future_observation_rejected(self):
        d=fixture();resource(d,"isolated_local_cpu")["observed_at"]="2026-10-27T06:00:01Z"
        self.assertRaisesRegex(ValueError,"OBSERVATION_IN_FUTURE",self.out,d)

    def test_30_malformed_observation_rejected(self):
        d=fixture();resource(d,"isolated_local_cpu")["observed_at"]="nowish"
        self.assertRaisesRegex(ValueError,"INVALID_TIMESTAMP",self.out,d)

    def test_31_protected_resource_blocked_even_if_online(self):
        d=fixture();r=resource(d,"busy_workstation");r["state"]="ONLINE_DECLARED";r["health"]="HEALTHY_DECLARED"
        self.assertNotIn("busy_workstation",[x["resource_id"] for x in self.out(d)["selected"]])

    def test_32_remove_protect_allows_only_shadow(self):
        d=fixture();r=resource(d,"busy_workstation");r["state"]="ONLINE_DECLARED";r["health"]="HEALTHY_DECLARED"
        r["observed_at"]="2026-10-27T05:59:00Z";d["policy"]["protected_ids"]=[]
        self.assertTrue(all(x["authority"]=="NONE" for x in self.out(d)["selected"]))

    def test_33_max_selected_one(self):
        d=fixture();d["policy"]["max_selected"]=1;self.assertEqual(len(self.out(d)["selected"]),1)

    def test_34_no_resources_holds_everything(self):
        d=fixture();d["resources"]=[];x=self.out(d)
        self.assertEqual(x["state"],"HELD_NO_ELIGIBLE_WORK");self.assertEqual(len(x["selected"]),0)

    def test_35_no_tasks_is_held(self):
        d=fixture();d["tasks"]=[];self.assertEqual(self.out(d)["state"],"HELD_NO_ELIGIBLE_WORK")

    def test_36_global_budget_zero_blocks_work(self):
        d=fixture();d["policy"]["total_budget"]["cpu_ms"]=0
        self.assertEqual(len(self.out(d)["selected"]),0)

    def test_37_energy_budget_enforced(self):
        d=fixture();d["policy"]["total_budget"]["energy_mwh"]=9
        self.assertEqual(len(self.out(d)["selected"]),0)

    def test_38_unknown_cpu_estimate_held(self):
        d=fixture();task(d,"preserve_failure_receipt")["estimated"]["cpu_ms"]=None
        self.assertEqual(dict((x["task_id"],x["reason"]) for x in self.out(d)["held"])["preserve_failure_receipt"],"UNKNOWN_ESTIMATED_COST")

    def test_39_unknown_memory_estimate_held(self):
        d=fixture();task(d,"preserve_failure_receipt")["memory_mib"]=None
        self.assertEqual(dict((x["task_id"],x["reason"]) for x in self.out(d)["held"])["preserve_failure_receipt"],"UNKNOWN_ESTIMATED_COST")

    def test_40_unknown_ram_capacity_held(self):
        d=fixture();resource(d,"isolated_local_cpu")["memory_mib"]=None
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_41_unknown_energy_capacity_held(self):
        d=fixture();resource(d,"isolated_local_cpu")["available"]["energy_mwh"]=None
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_42_over_ram_held(self):
        d=fixture();task(d,"preserve_failure_receipt")["memory_mib"]=1000
        self.assertNotIn("preserve_failure_receipt",[x["task_id"] for x in self.out(d)["selected"]])

    def test_43_aggregate_memory_headroom(self):
        d=fixture();d["tasks"]=[task(d,"preserve_failure_receipt")]
        t=copy.deepcopy(d["tasks"][0]);t["id"]="second_recovery";d["tasks"].append(t)
        resource(d,"isolated_local_cpu")["memory_mib"]=200
        d["policy"]["max_selected"]=2;d["policy"]["per_domain_max"]=2;d["policy"]["per_resource_max"]=2
        # 60% of 200 = 120MB; two tasks each 64MB cannot both fit.
        self.assertEqual(len(self.out(d)["selected"]),1)

    def test_44_per_domain_restricts_one_across_two_resources(self):
        d=fixture();d["tasks"]=[task(d,"preserve_failure_receipt")]
        t=copy.deepcopy(d["tasks"][0]);t["id"]="another_recovery";d["tasks"].append(t)
        res=copy.deepcopy(resource(d,"isolated_local_cpu"));res["id"]="same_domain_cpu_2";d["resources"].append(res)
        d["policy"]["per_resource_max"]=2
        self.assertEqual(len(self.out(d)["selected"]),1)

    def test_45_per_domain_two_allows_both(self):
        d=fixture();d["tasks"]=[task(d,"preserve_failure_receipt")]
        t=copy.deepcopy(d["tasks"][0]);t["id"]="another_recovery";d["tasks"].append(t)
        res=copy.deepcopy(resource(d,"isolated_local_cpu"));res["id"]="same_domain_cpu_2";d["resources"].append(res)
        d["policy"]["per_domain_max"]=2
        self.assertEqual(len(self.out(d)["selected"]),2)

    def test_46_no_infinite_slots(self):
        d=fixture();d["policy"]["max_selected"]=10000000
        self.assertRaisesRegex(ValueError,"INVALID_MAX_SELECTED",self.out,d)

    def test_47_reject_boolean_as_cost(self):
        d=fixture();d["policy"]["total_budget"]["cost_cents"]=True
        self.assertRaisesRegex(ValueError,"INVALID_COST_CENTS",self.out,d)

    def test_48_reject_negative_energy(self):
        d=fixture();task(d,"preserve_failure_receipt")["estimated"]["energy_mwh"]=-1
        self.assertRaisesRegex(ValueError,"INVALID_ENERGY_MWH",self.out,d)

    def test_49_reject_extra_metric_fields(self):
        d=fixture();task(d,"preserve_failure_receipt")["estimated"]["magic_perpetual_power"]=999
        self.assertRaisesRegex(ValueError,"INVALID_METRIC_FIELDS",self.out,d)

    def test_50_reject_secret_character_ids(self):
        d=fixture();task(d,"preserve_failure_receipt")["id"]="Private Subject Alice/SSN"
        self.assertRaisesRegex(ValueError,"INVALID_TASK_ID",self.out,d)

    def test_51_cli_sample_exact(self):
        source=(BASE/"fixture.json").read_bytes()
        p=subprocess.run([sys.executable,str(BASE/"resource_mesh_r0.py")],input=source,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),self.out())

    def test_52_cli_failure_no_secret_echo(self):
        d=fixture();d["schema"]="SECRET_NO_ECHO_12345"
        p=subprocess.run([sys.executable,str(BASE/"resource_mesh_r0.py")],input=json.dumps(d).encode(),capture_output=True)
        self.assertEqual(p.returncode,2);self.assertEqual(p.stdout,b"")
        self.assertNotIn(b"SECRET_NO_ECHO",p.stderr)

    def test_53_public_scope_fail_no_private_echo(self):
        d=fixture();d["output_privacy"]="PUBLIC";d["work_id"]="private_work_93450"
        p=subprocess.run([sys.executable,str(BASE/"resource_mesh_r0.py")],input=json.dumps(d).encode(),capture_output=True)
        self.assertEqual(p.returncode,2);self.assertNotIn(b"private_work_93450",p.stderr)

    def test_54_cli_input_cap(self):
        p=subprocess.run([sys.executable,str(BASE/"resource_mesh_r0.py")],input=b"x"*(m.MAX_BODY+1),capture_output=True)
        self.assertEqual(p.returncode,2);self.assertIn(b"INPUT_TOO_LARGE",p.stderr)

    def test_55_source_status_caller_declared(self):
        self.assertEqual(self.out()["source_evidence"],"CALLER_DECLARED_NOT_INDEPENDENTLY_VERIFIED")

    def test_56_unsupported_effect_never_selected(self):
        for effect in ["EXTERNAL_SEND","FINANCIAL","SECURITY_SENSITIVE","DEVICE_MUTATION"]:
            with self.subTest(effect=effect):
                d=fixture();task(d,"preserve_failure_receipt")["effect_class"]=effect
                self.assertNotIn("preserve_failure_receipt",[z["task_id"] for z in self.out(d)["selected"]])

    def test_57_symbolic_and_unknown_hold(self):
        for kind in ["SYMBOLIC","UNKNOWN","UNVERIFIED_ENERGY"]:
            with self.subTest(kind=kind):
                d=fixture();task(d,"preserve_failure_receipt")["kind"]=kind
                self.assertNotIn("preserve_failure_receipt",[z["task_id"] for z in self.out(d)["selected"]])

    def test_58_per_resource_max(self):
        d=fixture();d["tasks"]=[task(d,"preserve_failure_receipt")]
        t=copy.deepcopy(d["tasks"][0]);t["id"]="other";d["tasks"].append(t)
        d["policy"]["per_domain_max"]=2
        self.assertEqual(len(self.out(d)["selected"]),1)

    def test_59_policy_headroom_protected(self):
        d=fixture();d["policy"]["reserve_percent"]=95
        self.assertEqual(len(self.out(d)["selected"]),0)

    def test_60_pure_worker_no_clock_or_network(self):
        x=self.out();self.assertIn("PLANNED_NE_EXECUTED",x["nonclaims"])
        self.assertEqual(x["effect_totals"]["energy_harvested_mwh"],0)

if __name__=="__main__":
    unittest.main(verbosity=2)
