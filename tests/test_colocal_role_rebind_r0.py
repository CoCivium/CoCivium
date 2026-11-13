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


    def _needle_candidate(self, name="candidate.json", **changes):
        """Synthetic public-safe sidecar, never an X2 observation or authority."""
        pin = core.rebind(self.root, "X2_DESKTOP_RECOVERY")
        self.assertEqual(pin["state"], "SOURCE_BOUND_REBIND_OWNER_REFRESH_REQUIRED")
        value = {
            "schema": "CoAll.CoNeedle.PendingObservation.R0",
            "work_id": pin["work_id"],
            "incident_owner": pin["incident_owner"],
            "immutable_source_git_blob_sha1": pin["source_git_blob_sha1"],
            "revision": 1,
            "previous_observation_sha256": None,
            "observed_at_utc": "2026-11-13T14:00:00Z",
            "observer_claim": "synthetic-review-only",
            "evidence_ref": "https://github.com/CoCivium/CoCivium/issues/181",
            "observation_kind": "CURRENTNESS_GAP",
            "authorization": "READ_ONLY_PROPOSAL",
            "receiver_ack": False,
            "runtime_accepted": False,
            "external_effect_verified": False,
            "privacy_reviewed": False,
        }
        value.update(changes)
        rel = "ai/observations/colocal/" + name
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        return rel, path

    def test_needle_new_observation_preserves_immutable_policy_bytes(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        originals = {p.relative_to(self.root): p.read_bytes()
                     for p in self.root.rglob("*") if p.is_file()}
        rel, _ = self._needle_candidate()
        r = review_observation(self.root, "X2_DESKTOP_RECOVERY", rel)
        self.assertEqual(r["state"], "SOURCE_PIN_OK__OBSERVATION_CANDIDATE_REQUIRES_REVIEW")
        self.assertTrue(r["source_pin_verified"])
        self.assertTrue(r["observation_chain_syntax_verified"])
        self.assertFalse(r["observation_authority_verified"])
        self.assertFalse(r["observation_receiver_ack"])
        self.assertFalse(r["runtime_accepted"])
        self.assertFalse(r["operation_performed"])
        for p, raw in originals.items():
            self.assertEqual((self.root / p).read_bytes(), raw)

    def test_needle_claimed_receiver_ack_fails_closed(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        rel, _ = self._needle_candidate(receiver_ack=True)
        self.assertEqual(review_observation(self.root, "X2_DESKTOP_RECOVERY", rel)["reason"],
                         "HOLD_AUTHORITY_INFLATION")

    def test_needle_claimed_public_privacy_review_fails_closed(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        rel, _ = self._needle_candidate(privacy_reviewed=True)
        self.assertEqual(review_observation(self.root, "X2_DESKTOP_RECOVERY", rel)["reason"],
                         "HOLD_AUTHORITY_INFLATION")

    def test_needle_chain_predecessor_exact_hash_and_monotonic_timestamp(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        import hashlib
        p1, raw1 = self._needle_candidate("revision1.json")
        p2, _ = self._needle_candidate(
            "revision2.json", revision=2,
            observed_at_utc="2026-11-13T14:01:00Z",
            previous_observation_sha256=hashlib.sha256(raw1.read_bytes()).hexdigest())
        r = review_observation(self.root, "X2_DESKTOP_RECOVERY", p2, p1)
        self.assertTrue(r["observation_chain_syntax_verified"])
        self.assertEqual(r["observation_revision"], 2)
        self.assertFalse(r["receiver_origin_readproof"])
        self.assertFalse(r["external_effect_verified"])

    def test_needle_forged_predecessor_is_held(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        p1, _ = self._needle_candidate("rev1.json")
        p2, _ = self._needle_candidate("rev2.json", revision=2,
                                      previous_observation_sha256="0" * 64,
                                      observed_at_utc="2026-11-13T14:01:00Z")
        self.assertEqual(review_observation(self.root, "X2_DESKTOP_RECOVERY", p2, p1)["reason"],
                         "HOLD_PREDECESSOR_DIGEST_OR_REVISION_MISMATCH")

    def test_needle_untrusted_predecessor_or_missing_prior_is_held(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        p2, _ = self._needle_candidate("rev2.json", revision=2,
                                      previous_observation_sha256="0" * 64)
        self.assertEqual(review_observation(self.root, "X2_DESKTOP_RECOVERY", p2)["reason"],
                         "HOLD_PRIOR_REQUIRED")

    def test_needle_nonmonotonic_time_is_held(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        import hashlib
        p1, raw1 = self._needle_candidate("rev1.json")
        p2, _ = self._needle_candidate(
            "rev2.json", revision=2,
            previous_observation_sha256=hashlib.sha256(raw1.read_bytes()).hexdigest(),
            observed_at_utc="2026-11-13T13:59:00Z")
        self.assertEqual(review_observation(self.root, "X2_DESKTOP_RECOVERY", p2, p1)["reason"],
                         "HOLD_NONMONOTONIC_OBSERVATION_TIME")

    def test_needle_changed_frozen_pin_is_not_rebased_by_sidecar(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        rel, _ = self._needle_candidate()
        pinned = self.root / "ai/currentness/colocal-x2-postcontainment-focus-20261112-r1.json"
        pinned.write_bytes(pinned.read_bytes() + b" ")
        r = review_observation(self.root, "X2_DESKTOP_RECOVERY", rel)
        self.assertEqual(r["reason"], "HOLD_IMMUTABLE_POLICY_PIN_NOT_QUALIFIED")
        self.assertFalse(r["source_pin_verified"])

    def test_needle_private_or_traversal_route_rejected(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        rel, _ = self._needle_candidate()
        self.assertEqual(review_observation(
            self.root, "X2_DESKTOP_RECOVERY",
            "ai/observations/colocal/../colocal/" + rel.split("/")[-1])["reason"],
                         "HOLD_UNSAFE_OBSERVATION_PATH")
        private, _ = self._needle_candidate(
            "badref.json", evidence_ref="https://mail.google.com/private")
        self.assertEqual(review_observation(self.root, "X2_DESKTOP_RECOVERY", private)["reason"],
                         "HOLD_UNQUALIFIED_OBSERVER_OR_EVIDENCE")

    def test_needle_duplicate_keys_held_without_silent_rebind(self):
        from scripts.CoNeedleObservationAdmissionR0 import review_observation
        rel, path = self._needle_candidate()
        text = path.read_text("utf-8").replace('"schema":', '"schema": "spoof", "schema":', 1)
        path.write_text(text, encoding="utf-8")
        self.assertEqual(review_observation(self.root, "X2_DESKTOP_RECOVERY", rel)["reason"],
                         "HOLD_DUPLICATE_JSON_KEY")


if __name__ == "__main__":
    unittest.main()
