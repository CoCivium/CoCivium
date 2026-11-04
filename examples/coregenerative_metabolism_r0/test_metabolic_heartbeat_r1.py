#!/usr/bin/env python3
"""CoAlive R1 negative and positive tests; no OS/network/system side effects."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from metabolic_heartbeat_r1 import load_inputs, shadow_tick, validate

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


class CoObjectHeartbeatR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture, cls.cohort = load_inputs()

    def test_three_unlike_assets_are_in_the_pinned_cohort(self):
        self.assertTrue(validate(self.fixture, self.cohort))
        self.assertEqual([x["asset_id"] for x in self.fixture["objects"]], ["M05", "M07", "M08"])
        self.assertEqual(len({x["kind"] for x in self.fixture["objects"]}), 3)

    def test_source_git_blob_identity_is_real_but_not_liveness(self):
        assets = {x["id"]: x for x in self.cohort["assets"]}
        for p in self.fixture["objects"]:
            asset = assets[p["asset_id"]]
            self.assertEqual(blob_sha((REPO / asset["source"]["path"]).read_bytes()),
                             asset["source"]["git_blob_sha1"])
            self.assertEqual(asset["lifecycle"], "UNASSESSED")
            self.assertEqual(asset["receiver_use"], "UNVERIFIED")

    def test_only_two_relevant_events_are_selected_under_budget(self):
        r = shadow_tick(self.fixture, self.cohort)
        self.assertEqual([x["pulse_id"] for x in r["shadow_proposals"]], ["S04", "S01"])
        self.assertEqual(r["shadow_proposals"][0]["proposed_action"], "REVIEW_CONTRADICTION")
        self.assertEqual(r["shadow_proposals"][1]["proposed_action"], "REQUALIFY_SOURCE")
        self.assertEqual(r["resource_ledger"]["shadow_proposal_cost_units"], 2)
        self.assertEqual(r["resource_ledger"]["unspent_units"], 1)
        self.assertEqual([x["id"] for x in r["deferred"]], ["S05"])

    def test_unverified_receiver_claim_is_held_not_acceptance(self):
        r = shadow_tick(self.fixture, self.cohort)
        self.assertIn({"id": "S02", "reason": "NO_QUALIFIED_FIXTURE_EVIDENCE"}, r["held"])
        self.assertEqual(r["receiver_readproof_count"], 0)
        self.assertEqual(r["actual_actions"], 0)

    def test_a_no_change_pulse_does_not_wake_an_object(self):
        r = shadow_tick(self.fixture, self.cohort)
        self.assertIn({"id": "S03", "reason": "NO_QUALIFIED_OBJECT_RELATION"}, r["ignored"])
        self.assertFalse(any(p["pulse_id"] == "S03" for p in r["shadow_proposals"]))

    def test_every_object_keeps_unknown_real_liveness(self):
        r = shadow_tick(self.fixture, self.cohort)
        self.assertEqual(len(r["projections"]), 3)
        self.assertTrue(all(p["observed_liveness"] == "UNKNOWN_NOT_POLLED" for p in r["projections"]))
        self.assertTrue(all(p["lifecycle"] == "UNASSESSED" for p in r["projections"]))

    def test_replaying_already_processed_cursor_creates_no_new_candidate(self):
        r = shadow_tick(self.fixture, self.cohort, last_processed_cursor=5)
        self.assertEqual(r["event_count"], 0)
        self.assertEqual(r["shadow_proposals"], [])
        self.assertEqual(r["candidate_processed_cursor_not_ack"], 5)
        self.assertEqual(r["actual_actions"], 0)

    def test_partial_cursor_only_sees_unprocessed_events(self):
        r = shadow_tick(self.fixture, self.cohort, last_processed_cursor=3)
        self.assertEqual(r["event_count"], 2)
        self.assertEqual([x["pulse_id"] for x in r["shadow_proposals"]], ["S04", "S05"])

    def test_tight_action_quota_elects_challenge_first(self):
        cfg = copy.deepcopy(self.fixture)
        cfg["policy"]["max_shadow_actions"] = 1
        r = shadow_tick(cfg, self.cohort)
        self.assertEqual([x["pulse_id"] for x in r["shadow_proposals"]], ["S04"])
        self.assertEqual(len(r["deferred"]), 2)

    def test_reserve_exhaustion_causes_no_wake(self):
        cfg = copy.deepcopy(self.fixture)
        cfg["policy"]["min_reserve_units"] = 3
        r = shadow_tick(cfg, self.cohort)
        self.assertEqual(r["shadow_proposals"], [])
        self.assertEqual(len(r["deferred"]), 3)
        self.assertEqual(r["resource_ledger"]["unspent_units"], 3)

    def test_private_event_held_even_when_relevant(self):
        cfg = copy.deepcopy(self.fixture)
        cfg["events"][0]["public_safe"] = False
        r = shadow_tick(cfg, self.cohort)
        self.assertIn({"id": "S01", "reason": "CONFIDENTIALITY_GATE"}, r["held"])
        self.assertFalse(any(x["pulse_id"] == "S01" for x in r["shadow_proposals"]))

    def test_error_shock_does_not_increase_activity_or_grant_authority(self):
        r = shadow_tick(self.fixture, self.cohort)
        self.assertEqual(r["shadow_proposals"][0]["proposal_state"], "SHADOW_ONLY_NO_EXECUTION")
        self.assertEqual(r["edge_fanout_count"], 0)
        self.assertEqual(r["actual_workers"], 0)
        self.assertEqual(r["network_calls"], 0)

    def test_no_automatic_relation_cascade(self):
        cfg = copy.deepcopy(self.fixture)
        cfg["relations"][0]["automatic_cascade"] = True
        with self.assertRaisesRegex(ValueError, "RELATION_CANNOT_SELF_AUTHORIZE"):
            validate(cfg, self.cohort)

    def test_expanding_work_or_runtime_authority_fails_closed(self):
        for name, value in (("max_shadow_actions", 100), ("max_cascade_hops", 1),
                            ("external_effects", 1), ("live_workers", 1), ("allow_network", True)):
            cfg = copy.deepcopy(self.fixture)
            cfg["policy"][name] = value
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate(cfg, self.cohort)

    def test_nonmonotonic_cursor_and_duplicate_id_rejected(self):
        for field, value in (("cursor", 1), ("id", "S01")):
            cfg = copy.deepcopy(self.fixture)
            cfg["events"][-1][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "NONMONOTONIC_OR_DUPLICATE_PULSE"
            ):
                validate(cfg, self.cohort)

    def test_fixture_claim_cannot_be_upgraded_to_real_observation(self):
        cfg = copy.deepcopy(self.fixture)
        cfg["events"][0]["evidence_class"] = "OBSERVED"
        with self.assertRaisesRegex(ValueError, "NONFIXTURE_EVIDENCE_NOT_ACCEPTED"):
            validate(cfg, self.cohort)

    def test_source_presence_must_not_turn_into_verified_receiver_outcome(self):
        cfg = copy.deepcopy(self.cohort)
        next(x for x in cfg["assets"] if x["id"] == "M07")["verified_outcome"] = True
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_PROMOTION"):
            shadow_tick(self.fixture, cfg)

    def test_missing_or_mutated_profile_rejected(self):
        cfg = copy.deepcopy(self.fixture)
        cfg["objects"].pop()
        with self.assertRaisesRegex(ValueError, "REQUIRED_THREE_UNLIKE_OBJECTS"):
            validate(cfg, self.cohort)

    def test_currentness_cursor_is_not_receiver_ack(self):
        r = shadow_tick(self.fixture, self.cohort)
        self.assertEqual(r["candidate_processed_cursor_not_ack"], 5)
        self.assertTrue(all(x["receiver_ack"] == "NOT_OBSERVED" for x in r["shadow_proposals"]))
        self.assertTrue(all(x["source_currentness"] == "UNVERIFIED_NOW" for x in r["shadow_proposals"]))

    def test_deterministic_repeated_runs_and_receipt_hash(self):
        a = shadow_tick(self.fixture, self.cohort)
        b = shadow_tick(self.fixture, self.cohort)
        self.assertEqual(a, b)
        copy_without_digest = {k: v for k, v in a.items() if k != "deterministic_receipt_sha256"}
        canonical = json.dumps(copy_without_digest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        self.assertEqual(hashlib.sha256(canonical.encode()).hexdigest(),
                         a["deterministic_receipt_sha256"])

    def test_not_an_unattended_program_or_perpetual_energy_promise(self):
        code = (ROOT / "metabolic_heartbeat_r1.py").read_text()
        for forbidden in ("import requests", "import socket", "import subprocess",
                          "time.sleep(", "while True", "urllib.request", "os.system("):
            self.assertNotIn(forbidden, code)
        r = shadow_tick(self.fixture, self.cohort)
        self.assertIn("REGENERATIVE_NE_INFINITE_COMPUTE_OR_ENERGY", r["nonclaims"])
        self.assertIn("HEARTBEAT_CANDIDATE_NE_PROCESS_LIVENESS", r["nonclaims"])
        self.assertIn("ET_HYPOTHESIS_NE_ET_DETECTION", r["nonclaims"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
