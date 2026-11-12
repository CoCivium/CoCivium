"""Adversarial CoLocal role re-entry tests, source-only, no device/process calls."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/CoLocalRoleRebindR0.py"
spec = importlib.util.spec_from_file_location("colocal_rebind", SCRIPT)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class TestCoLocalRoleRebind(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel in (core.BOOT, "ai/currentness/colocal-x2-postcontainment-focus-20261112-r1.json"):
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / rel, p)

    def change_boot(self, mutate):
        path = self.root / core.BOOT
        o = json.loads(path.read_text("utf-8"))
        mutate(o)
        path.write_text(json.dumps(o, indent=2) + "\n", encoding="utf-8")

    def test_matching_x2_role_has_one_bounded_rebind(self):
        r = core.rebind(self.root, "X2_DESKTOP_RECOVERY")
        self.assertEqual(r["state"], "SOURCE_BOUND_REBIND_OWNER_REFRESH_REQUIRED")
        self.assertEqual(r["work_id"], core.EXPECTED_WORK)
        self.assertTrue(r["owner_refresh_required"])
        self.assertEqual(r["read_scope"], "PUBLIC_SOURCE_ONLY_NOT_LIVE_DEVICE")
        self.assertFalse(r["operation_performed"])
        self.assertFalse(r["x2_shell_started"])
        self.assertFalse(r["receiver_pickup"])
        self.assertFalse(r["runtime_accepted"])

    def test_unrelated_role_no_incident_content(self):
        r = core.rebind(self.root, "BOOK_EDITOR")
        self.assertEqual(r["state"], "NO_RELEVANT_INCIDENT_CONTENT")
        self.assertNotIn("incident_owner", r)
        self.assertNotIn("work_id", r)

    def test_two_identical_reads_deterministic_no_mutation(self):
        files = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        r1 = core.rebind(self.root, "X2_DESKTOP_RECOVERY")
        r2 = core.rebind(self.root, "X2_DESKTOP_RECOVERY")
        self.assertEqual(r1, r2)
        self.assertEqual(files, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_another_relevant_role_recovers_same_workid(self):
        r = core.rebind(self.root, "COLOCAL_SESSION_RECOVERY")
        self.assertEqual(r["work_id"], core.EXPECTED_WORK)

    def test_bootstrap_missing_fails_closed(self):
        (self.root / core.BOOT).unlink()
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["state"], "HOLD_SOURCE_REBIND")

    def test_source_missing_fails_closed(self):
        (self.root / "ai/currentness/colocal-x2-postcontainment-focus-20261112-r1.json").unlink()
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["state"], "HOLD_SOURCE_REBIND")

    def test_drifted_exact_source_never_promotes(self):
        p = self.root / "ai/currentness/colocal-x2-postcontainment-focus-20261112-r1.json"
        p.write_bytes(p.read_bytes() + b" ")
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_SOURCE_BLOB_DRIFT")

    def test_attempted_path_escape_rejected(self):
        self.change_boot(lambda o: o["role_scoped_rebind"]["source"].update(path="../secret.json"))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["state"], "HOLD_SOURCE_REBIND")

    def test_forged_task_mutation_authority_rejected(self):
        self.change_boot(lambda o: o["role_scoped_rebind"].update(task_mutation_authorized=True))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_UNSAFE_AUTHORITY")

    def test_missing_no_watch_flag_rejected(self):
        self.change_boot(lambda o: o["role_scoped_rebind"].update(no_new_x2_terminal_or_scheduled_watcher=False))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_UNSAFE_AUTHORITY")

    def test_automatic_receiver_ack_claim_fails(self):
        self.change_boot(lambda o: o["role_scoped_rebind"].update(receiver_pickup="PASS"))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_FALSE_PICKUP_OR_RUNTIME")

    def test_automatic_runtime_adoption_claim_fails(self):
        self.change_boot(lambda o: o["role_scoped_rebind"].update(runtime_integration="PASS"))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_FALSE_PICKUP_OR_RUNTIME")

    def test_owner_redirect_rejected(self):
        self.change_boot(lambda o: o["role_scoped_rebind"].update(incumbent_owner="https://attacker.example/"))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_INCUMBENT_OWNER_DRIFT")

    def test_source_state_conflict_holds_without_rehash(self):
        p = self.root / "ai/currentness/colocal-x2-postcontainment-focus-20261112-r1.json"
        o = json.loads(p.read_text("utf-8"))
        o["state"] = "FOCUS_CURED"
        p.write_text(json.dumps(o), encoding="utf-8")
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["state"], "HOLD_SOURCE_REBIND")

    def test_role_set_collision_rejected(self):
        self.change_boot(lambda o: o["role_scoped_rebind"]["role_topics"].append("X2_DESKTOP_RECOVERY"))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_ROLE_SET")

    def test_missing_currentness_rule_rejected(self):
        self.change_boot(lambda o: o["role_scoped_rebind"].update(currentness_rule="RUN_NOW"))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_MISSING_CURRENTNESS_BOUNDARY")

    def test_rebind_does_not_reproduce_private_unrelated_input(self):
        self.change_boot(lambda o: o.update(private_details="a private email example@example.invalid"))
        r = core.rebind(self.root, "X2_DESKTOP_RECOVERY")
        self.assertEqual(r["state"], "SOURCE_BOUND_REBIND_OWNER_REFRESH_REQUIRED")
        self.assertNotIn("example@example.invalid", json.dumps(r))

    def test_explicit_unknown_all_session_ack_holds(self):
        self.change_boot(lambda o: o["role_scoped_rebind"].update(all_session_ack="ALL_ACK"))
        self.assertEqual(core.rebind(self.root, "X2_DESKTOP_RECOVERY")["reason"], "HOLD_FALSE_PICKUP_OR_RUNTIME")


if __name__ == "__main__":
    unittest.main()
