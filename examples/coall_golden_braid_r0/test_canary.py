#!/usr/bin/env python3
"""Deterministic negative and recovery tests for the local-only bridge."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from canary import (
    SEED, REPO, DESTINATIONS, NONCLAIMS, demo, dispatch, initialize,
    inbox_path, load, receipt_path, reconcile, receiver_process_readback,
    sha, validate_seed,
)

class GoldenBraidCanaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / "work"
        self.seed = Path(self.temp.name) / "source.json"
        self.seed.write_bytes(SEED.read_bytes())

    def test_seed_is_existing_typed_coevo_delta_and_exact_blob(self):
        raw = SEED.read_bytes()
        seed = validate_seed(raw)
        self.assertEqual(seed["delta_id"], "coevo-shared-draft-bridge-r0-20261026")
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertEqual(git_blob, "e0cc145c692c3615b277b8457d924da5d8a46000")
        self.assertEqual(seed["epistemic_class"], "PLANNED")
        self.assertIn("NO_EMAIL_SEND", seed["authority_ceiling"])

    def test_after_only_first_destination_no_global_success(self):
        initialize(self.work, self.seed)
        self.assertEqual(dispatch(self.work, "alpha")["state"], "LOCAL_SYNTHETIC_COPY_ONLY")
        self.assertEqual(dispatch(self.work, "beta", inject_failure=True)["state"], "HELD_NOT_DELIVERED")
        receiver_process_readback(self.work, "alpha")
        view = reconcile(self.work)
        self.assertFalse(view["all_synthetic_readbacks"])
        self.assertEqual(view["destinations"]["alpha"]["local_process_readback"], "MATCHED")
        self.assertEqual(view["destinations"]["beta"]["inbox"], "ABSENT")
        self.assertEqual(view["destinations"]["beta"]["external_receiver_ack"], "UNPROVEN")
        self.assertEqual(view["cross_surface_integration"], "UNPROVEN")

    def test_two_receiver_process_recovery_and_fresh_process_readback(self):
        out = demo(self.work, self.seed)
        self.assertEqual(out["state"], "PASS_SYNTHETIC_SAME_RUNNER_TWO_DESTINATION_CANARY")
        self.assertEqual(out["injected_beta"]["attempt"], "INJECTED_FAILURE")
        self.assertEqual(out["replay_alpha"]["attempt"], "ALREADY_IDENTICAL")
        self.assertEqual(out["replay_beta"]["attempt"], "CREATED_EXACT")
        self.assertTrue(out["reconstructed_in_fresh_process"]["all_synthetic_readbacks"])
        self.assertEqual(out["actual_external_deliveries"], 0)
        self.assertEqual(out["independent_receiver_acceptances"], 0)
        self.assertTrue((self.work / "synthetic_result.json").is_file())
        for dest in DESTINATIONS:
            self.assertEqual(inbox_path(self.work, dest).read_bytes(), self.seed.read_bytes())
            self.assertEqual(load(receipt_path(self.work, dest))["receiver_kind"],
                             "LOCAL_TEST_PROCESS_NOT_INDEPENDENT")
            self.assertEqual(reconcile(self.work)["destinations"][dest]["external_receiver_ack"],
                             "UNPROVEN")

    def test_no_duplicate_or_clobber_of_completed_first_destination(self):
        initialize(self.work, self.seed)
        dispatch(self.work, "alpha")
        receiver_process_readback(self.work, "alpha")
        before = inbox_path(self.work, "alpha").read_bytes()
        receipt_before = receipt_path(self.work, "alpha").read_bytes()
        self.assertEqual(dispatch(self.work, "alpha")["attempt"], "ALREADY_IDENTICAL")
        self.assertEqual(receiver_process_readback(self.work, "alpha"), "ALREADY_IDENTICAL")
        self.assertEqual(before, inbox_path(self.work, "alpha").read_bytes())
        self.assertEqual(receipt_before, receipt_path(self.work, "alpha").read_bytes())

    def test_bad_destination_does_not_create_any_receiver(self):
        initialize(self.work, self.seed)
        with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_TEST_DESTINATION"):
            dispatch(self.work, "external-real-user")
        self.assertFalse((self.work / "inbox").exists())

    def test_inbox_collision_is_held_never_overwritten(self):
        initialize(self.work, self.seed)
        path = inbox_path(self.work, "beta")
        path.parent.mkdir(parents=True)
        path.write_bytes(b"tampered test data")
        outcome = dispatch(self.work, "beta")
        self.assertEqual(outcome["state"], "HELD_INBOX_CONFLICT")
        self.assertEqual(path.read_bytes(), b"tampered test data")
        with self.assertRaisesRegex(ValueError, "DO_NOT_MATCH"):
            receiver_process_readback(self.work, "beta")
        self.assertFalse(receipt_path(self.work, "beta").exists())
        self.assertEqual(reconcile(self.work)["destinations"]["beta"]["inbox"], "CONFLICT")

    def test_source_drift_fails_closed(self):
        initialize(self.work, self.seed)
        self.seed.write_bytes(self.seed.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "SOURCE_CHANGED_SINCE_MANIFEST"):
            dispatch(self.work, "alpha")
        self.assertFalse((self.work / "inbox").exists())

    def test_private_or_broadened_authority_is_rejected(self):
        source = json.loads(self.seed.read_text())
        for change in (
            {"confidentiality": "PRIVATE"},
            {"authority_ceiling": "GLOBAL_PERMISSION"},
            {"mutation_class": "EFFECT_GATED"},
        ):
            changed = dict(source)
            changed.update(change)
            raw = json.dumps(changed).encode("utf-8")
            with self.subTest(change=change):
                with self.assertRaisesRegex(ValueError, "NOT_AUTHORIZED"):
                    validate_seed(raw)

    def test_receipt_collision_does_not_claim_accepted(self):
        initialize(self.work, self.seed)
        dispatch(self.work, "alpha")
        path = receipt_path(self.work, "alpha")
        path.parent.mkdir(parents=True)
        path.write_text('{"state":"I_AM_A_REAL_HUMAN_ACK"}')
        with self.assertRaisesRegex(ValueError, "CONTENT_COLLISION"):
            receiver_process_readback(self.work, "alpha")
        view = reconcile(self.work)
        self.assertEqual(view["destinations"]["alpha"]["local_process_readback"], "UNPROVEN")
        self.assertEqual(view["destinations"]["alpha"]["external_receiver_ack"], "UNPROVEN")

    def test_no_real_delivery_permission_or_fictional_external_ack(self):
        initialize(self.work, self.seed)
        r = reconcile(self.work)
        self.assertEqual(r["external_effects"], 0)
        self.assertEqual(r["cross_surface_integration"], "UNPROVEN")
        for label in ("LOCAL_COPY_NE_EXTERNAL_DELIVERY",
                      "READBACK_NE_INDEPENDENT_ACCEPTANCE",
                      "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF"):
            self.assertIn(label, NONCLAIMS)

if __name__ == "__main__":
    unittest.main(verbosity=2)
