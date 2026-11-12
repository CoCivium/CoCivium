"""Provider-exit negative controls, synthetic inputs only. No provider access."""
import copy
import unittest
from datetime import datetime, timedelta, timezone

from provider_exit_readiness_r0 import assess, SCHEMA, RESULT_SCHEMA

NOW = datetime(2026, 11, 12, 13, 0, tzinfo=timezone.utc)


def fixture():
    return {
        "schema": SCHEMA,
        "observed_at_utc": (NOW-timedelta(seconds=30)).isoformat(),
        "work_id": "CoLocalCanary01",
        "confidentiality": "PUBLIC",
        "provider": {"availability":"LIMITED","limit_evidence":"USER_REPORTED"},
        "local": {
            "endpoint":"127.0.0.1",
            "model_version_pinned":True, "license_checked":True,
            "canary_executed":True, "task_quality_verified":True,
            "canary_observed_at_utc":(NOW-timedelta(seconds=20)).isoformat(),
            "privacy_boundary_verified":False,
        },
        "custody": {
            "work_checkpoint_readback":True,
            "checkpoint_sha256":"a"*64,
            "same_workid_restart_verified":True,
            "independent_receiver_readproof":True,
        },
        "surface": {"no_focus_theft_verified":True,"native_fallback_usable":True},
        "export": {
            "state":"NOT_REQUESTED","account_class":"UNKNOWN",
            "archive_received_and_hash_verified":False,
            "coverage_reviewed":False,"permissions_checked":False,
        },
    }


class ExitGateTests(unittest.TestCase):
    def test_positive_canary_does_not_cancel(self):
        r=assess(fixture(),at_utc=NOW)
        self.assertEqual(r["schema"],RESULT_SCHEMA)
        self.assertEqual(r["state"],"LOCAL_PRIMARY_PILOT_ELIGIBLE_EXPORT_HELD")
        self.assertTrue(r["primary_route_eligible"])
        self.assertFalse(r["subscription_retirement_authorized"])
        self.assertFalse(r["automatic_external_transfer_allowed"])
        self.assertFalse(r["recovery_claimed"])

    def test_even_eligible_archive_only_allows_human_review(self):
        f=fixture()
        f["export"].update(state="RECEIVED",account_class="PERSONAL",
                           archive_received_and_hash_verified=True,
                           coverage_reviewed=True, permissions_checked=True)
        r=assess(f,at_utc=NOW)
        self.assertEqual(r["state"],"HUMAN_RETIREMENT_REVIEW_READY_NO_ACTION_AUTHORIZED")
        self.assertTrue(r["subscription_retirement_review_ready"])
        self.assertFalse(r["subscription_retirement_authorized"])

    def test_provider_outage_does_not_trigger_external_private_transfer(self):
        f=fixture()
        f["provider"].update(availability="OUTAGE",limit_evidence="ACCOUNT_UI_OBSERVED")
        f["confidentiality"]="PRIVATE"
        r=assess(f,at_utc=NOW)
        self.assertFalse(r["primary_route_eligible"])
        self.assertFalse(r["automatic_external_transfer_allowed"])
        self.assertEqual(r["state"],"HOLD_LOCAL_OR_CHECKPOINT_UNQUALIFIED")

    def test_private_requires_local_privacy_proof(self):
        f=fixture()
        f["confidentiality"]="PRIVATE"
        f["local"]["privacy_boundary_verified"]=True
        r=assess(f,at_utc=NOW)
        self.assertTrue(r["primary_route_eligible"])

    def test_restricted_requires_local_privacy_proof(self):
        f=fixture()
        f["confidentiality"]="RESTRICTED"
        self.assertFalse(assess(f,at_utc=NOW)["shadow_route_eligible"])

    def test_unknown_confidentiality_fails_closed(self):
        f=fixture()
        f["confidentiality"]="UNKNOWN"
        self.assertFalse(assess(f,at_utc=NOW)["primary_route_eligible"])

    def test_no_local_canary_blocks(self):
        f=fixture()
        f["local"]["canary_executed"]=False
        self.assertEqual(assess(f,at_utc=NOW)["state"],"HOLD_LOCAL_OR_CHECKPOINT_UNQUALIFIED")

    def test_stale_local_canary_blocks(self):
        f=fixture()
        f["local"]["canary_observed_at_utc"]=(NOW-timedelta(hours=1)).isoformat()
        self.assertFalse(assess(f,at_utc=NOW)["shadow_route_eligible"])

    def test_future_local_canary_blocks(self):
        f=fixture()
        f["local"]["canary_observed_at_utc"]=(NOW+timedelta(minutes=1)).isoformat()
        self.assertFalse(assess(f,at_utc=NOW)["shadow_route_eligible"])

    def test_unverified_quality_blocks(self):
        f=fixture()
        f["local"]["task_quality_verified"]=False
        self.assertFalse(assess(f,at_utc=NOW)["shadow_route_eligible"])

    def test_non_loopback_endpoint_blocks(self):
        f=fixture()
        f["local"]["endpoint"]="https://vendor.example"
        self.assertFalse(assess(f,at_utc=NOW)["shadow_route_eligible"])

    def test_missing_checkpoint_hash_blocks(self):
        f=fixture()
        f["custody"]["checkpoint_sha256"]=None
        self.assertFalse(assess(f,at_utc=NOW)["shadow_route_eligible"])

    def test_no_independent_receiver_forces_shadow_only(self):
        f=fixture()
        f["custody"]["independent_receiver_readproof"]=False
        r=assess(f,at_utc=NOW)
        self.assertTrue(r["shadow_route_eligible"])
        self.assertFalse(r["primary_route_eligible"])
        self.assertEqual(r["state"],"SHADOW_ONLY_PRIMARY_UNQUALIFIED")

    def test_no_reboot_proof_forces_shadow_only(self):
        f=fixture()
        f["custody"]["same_workid_restart_verified"]=False
        self.assertFalse(assess(f,at_utc=NOW)["primary_route_eligible"])

    def test_focus_theft_forces_shadow_only(self):
        f=fixture()
        f["surface"]["no_focus_theft_verified"]=False
        r=assess(f,at_utc=NOW)
        self.assertEqual(r["state"],"SHADOW_ONLY_PRIMARY_UNQUALIFIED")

    def test_native_fallback_missing_holds_primary(self):
        f=fixture()
        f["surface"]["native_fallback_usable"]=False
        self.assertFalse(assess(f,at_utc=NOW)["primary_route_eligible"])

    def test_archive_requested_is_not_received(self):
        f=fixture()
        f["export"]["state"]="REQUESTED"
        f["export"]["archive_received_and_hash_verified"]=True
        f["export"]["coverage_reviewed"]=True
        f["export"]["permissions_checked"]=True
        self.assertFalse(assess(f,at_utc=NOW)["subscription_retirement_review_ready"])

    def test_managed_workspace_without_export_stays_held(self):
        f=fixture()
        f["export"]["account_class"]="MANAGED"
        f["export"]["state"]="NOT_SUPPORTED"
        self.assertEqual(assess(f,at_utc=NOW)["state"],"LOCAL_PRIMARY_PILOT_ELIGIBLE_EXPORT_HELD")

    def test_stale_snapshot_fails_closed(self):
        f=fixture()
        f["observed_at_utc"]=(NOW-timedelta(hours=2)).isoformat()
        self.assertEqual(assess(f,at_utc=NOW)["state"],"HOLD_INVALID_OR_STALE_EVIDENCE")

    def test_future_snapshot_fails_closed(self):
        f=fixture()
        f["observed_at_utc"]=(NOW+timedelta(minutes=2)).isoformat()
        self.assertEqual(assess(f,at_utc=NOW)["state"],"HOLD_INVALID_OR_STALE_EVIDENCE")

    def test_bad_schema_fails_closed(self):
        f=fixture()
        f["schema"]="CoAll.Other"
        self.assertFalse(assess(f,at_utc=NOW)["primary_route_eligible"])

    def test_fake_boolean_not_accepted(self):
        f=fixture()
        f["local"]["canary_executed"]=1
        self.assertEqual(assess(f,at_utc=NOW)["state"],"HOLD_INVALID_OR_STALE_EVIDENCE")

    def test_account_secrets_not_returned(self):
        f=fixture()
        f["provider"]["api_key"]="secret_private_key_987"
        f["account_email"]="private@do-not-publish.example"
        f["prompt"]="do not echo this secret"
        r=assess(f,at_utc=NOW)
        self.assertNotIn("secret_private_key_987",str(r))
        self.assertNotIn("private@do-not-publish",str(r))
        self.assertNotIn("do not echo",str(r))

    def test_model_license_required(self):
        f=fixture()
        f["local"]["license_checked"]=False
        self.assertFalse(assess(f,at_utc=NOW)["shadow_route_eligible"])

    def test_no_auto_action_from_requested_billing_approval(self):
        f=fixture()
        f["human_said_cancel"]=True
        f["billing_action"]="CANCEL_ALL"
        r=assess(f,at_utc=NOW)
        self.assertFalse(r["subscription_retirement_authorized"])

    def test_idempotent_and_no_mutation(self):
        f=fixture()
        prior=copy.deepcopy(f)
        self.assertEqual(assess(f,at_utc=NOW),assess(f,at_utc=NOW))
        self.assertEqual(f,prior)


if __name__ == "__main__":
    unittest.main()
