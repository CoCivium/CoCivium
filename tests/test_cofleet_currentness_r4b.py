"""CoFleet R4B: bounded currentness is not physical-device health.

No device, process, clipboard, network, or provider calls. Reproduce the
misleading projection with intentionally synthetic runtime facts.
"""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cofleet", ROOT / "scripts" / "CoFleetProjectionCompilerR4A.py")
cofleet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cofleet)


def project(*, runtime=None, ledger=None, spawn=None):
    return cofleet.compile_projection(ledger, spawn, None, runtime, "2026-10-28T17:32:27Z")


class CoFleetCurrentnessR4BTests(unittest.TestCase):
    def test_no_evidence_remains_unknown(self):
        p = project()
        self.assertEqual(p["pressure"]["headline"], "UNKNOWN")
        self.assertIsNone(p["provider_sessions"]["count"])
        self.assertEqual(p["coverage"]["global_fleet_census"], "UNPROVEN")

    def test_stale_observer_is_not_hidden_by_empty_queue(self):
        p = project(runtime={"currentness": {"state": "STALE", "age_seconds": 3600}})
        self.assertEqual(p["pressure"]["headline"], "DEGRADED")
        self.assertEqual(p["currentness"]["state"], "STALE")
        self.assertIn("RUNTIME_CURRENTNESS_NOT_HEALTHY", [e["exception_class"] for e in p["exceptions"]])
        self.assertEqual(p["human_blockers"], [])

    def test_explicit_degraded_runtime_is_visible(self):
        p = project(runtime={"currentness": {"state": "DEGRADED"}})
        self.assertEqual(p["pressure"]["headline"], "DEGRADED")

    def test_aging_runtime_is_caution_not_inferred_health(self):
        p = project(runtime={"currentness": {"state": "AGING", "age_seconds": 120}})
        self.assertEqual(p["pressure"]["headline"], "MODERATE")

    def test_healthy_observer_does_not_imply_global_health(self):
        p = project(runtime={"currentness": {"state": "HEALTHY"}})
        self.assertEqual(p["pressure"]["headline"], "UNKNOWN")
        self.assertEqual(p["coverage"]["global_fleet_census"], "UNPROVEN")

    def test_blocked_contract_without_sessions_remains_visible(self):
        p = project(spawn={"contracts": [{
            "scope": "fixture", "spawn_id": "b", "materialization_state": "BLOCKED",
            "uncertainty": "MISSING_AUTHORITY", "lease": {"effect_lease": "NONE"},
        }]})
        self.assertEqual(p["pressure"]["headline"], "HIGH")
        self.assertEqual(p["human_blockers"], [])

    def test_explicit_human_blocker_without_sessions_is_visible(self):
        p = project(runtime={"human_blockers": [{"gate": "CONSENT_REQUIRED"}]})
        self.assertEqual(p["pressure"]["headline"], "HIGH")
        self.assertEqual(len(p["human_blockers"]), 1)

    def test_boolean_counts_are_not_worker_evidence(self):
        p = project(runtime={"workspaces": True, "materialized_workers": True,
                             "provider_sessions": False, "model_runtimes": True,
                             "effect_leases": False})
        for key in ("workspaces", "materialized_workers", "provider_sessions", "model_runtimes"):
            with self.subTest(key=key):
                self.assertIsNone(p[key]["count"])
                self.assertEqual(p[key]["coverage"], "RUNTIME_FACT_UNPROVEN")
        self.assertEqual(p["effect_leases"]["count"], 0)
        self.assertEqual(p["effect_leases"]["coverage"], "LOGICAL_CONTRACTS_ONLY__LIVE_RUNTIME_UNPROVEN")

    def test_real_integer_zero_preserved(self):
        p = project(runtime={"workspaces": 0, "materialized_workers": 0,
                             "provider_sessions": 0, "model_runtimes": 0,
                             "effect_leases": 0})
        for key in ("workspaces", "materialized_workers", "provider_sessions",
                    "model_runtimes", "effect_leases"):
            self.assertEqual(p[key]["count"], 0)
            self.assertEqual(p[key]["coverage"], "BOUND_RUNTIME_FACT")

    def test_negative_effect_leases_do_not_become_runtime_fact(self):
        p = project(runtime={"effect_leases": -7})
        self.assertEqual(p["effect_leases"]["count"], 0)
        self.assertEqual(p["effect_leases"]["coverage"], "LOGICAL_CONTRACTS_ONLY__LIVE_RUNTIME_UNPROVEN")

    def test_bounded_session_recovery_still_degraded(self):
        p = project(ledger={"sessions": [{"session_id": "fixture", "projection": "RECOVERY"}]})
        self.assertEqual(p["pressure"]["headline"], "DEGRADED")
        self.assertEqual(p["virtual_sessions"]["count"], 1)

    def test_stale_is_not_physical_machine_diagnosis(self):
        p = project(runtime={"currentness": {"state": "STALE"}})
        self.assertNotIn("device_state", p)
        self.assertIn("OBSERVER_PATH_STATE_NE_DEVICE_STATE", p["nonclaims"])
        self.assertIn("STALE_OBSERVER_NE_DEVICE_DEAD", p["nonclaims"])

    def test_observed_runtime_currentness_is_still_bounded(self):
        p = project(runtime={"currentness": {"state": "STALE"},
                             "provider_sessions": 3})
        self.assertEqual(p["provider_sessions"]["count"], 3)
        self.assertEqual(p["coverage"]["global_fleet_census"], "UNPROVEN")
        self.assertEqual(p["observer"], "CoFleetProjectionCompiler.R4B.v0.1")


    def test_distinct_work_same_count_has_distinct_projection_id(self):
        one = project(ledger={"sessions": [{"session_id": "work-A", "projection": "ACTIVE"}]})
        two = project(ledger={"sessions": [{"session_id": "work-B", "projection": "ACTIVE"}]})
        self.assertNotEqual(one["projection_id"], two["projection_id"])
        self.assertEqual(one["virtual_sessions"]["count"], two["virtual_sessions"]["count"])

    def test_runtime_evidence_change_alters_projection_id(self):
        one = project(runtime={"currentness": {"state": "STALE", "age_seconds": 3600}})
        two = project(runtime={"currentness": {"state": "DEGRADED", "age_seconds": 3600}})
        self.assertNotEqual(one["projection_id"], two["projection_id"])

    def test_identical_input_snapshot_replays_same_projection_id(self):
        input_ledger = {"sessions": [{"session_id": "same", "projection": "WORKING"}]}
        self.assertEqual(project(ledger=input_ledger)["projection_id"],
                         project(ledger=input_ledger)["projection_id"])

    def test_unaged_healthy_label_cannot_certify_currentness(self):
        p = project(ledger={"sessions": [{"session_id": "A", "projection": "ACTIVE"}]},
                    runtime={"currentness": {"state": "HEALTHY"}})
        self.assertEqual(p["currentness"]["state"], "UNKNOWN")
        self.assertEqual(p["pressure"]["headline"], "UNKNOWN")

    def test_boolean_negative_string_and_infinite_age_not_healthy(self):
        for invalid in (True, -1, "0", float("inf"), float("nan")):
            with self.subTest(invalid=invalid):
                p = project(runtime={"currentness": {"state": "HEALTHY",
                                                      "age_seconds": invalid}})
                self.assertEqual(p["currentness"]["state"], "UNKNOWN")

    def test_source_only_active_session_is_not_health_evidence(self):
        p = project(ledger={"sessions": [{"session_id": "A", "projection": "ACTIVE"}]})
        self.assertEqual(p["pressure"]["headline"], "UNKNOWN")
        self.assertEqual(p["coverage"]["global_fleet_census"], "UNPROVEN")

if __name__ == "__main__":
    unittest.main()
