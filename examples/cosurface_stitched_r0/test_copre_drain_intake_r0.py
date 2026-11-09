"""CoPre intake tests: received is not drained, duplicate is not new work."""
import unittest
from dataclasses import replace
from copre_drain_intake_r0 import DrainEcho, reconcile, safe_public_rollup


class CoPreDrainIntakeTests(unittest.TestCase):
    def item(self, **changes):
        base = dict(session_ref="synthetic-provider-session", source_ref="private:ref",
                    seed_revision="v8.54", body="synthetic echo",
                    source_scope="RESTRICTED", provider_readback="test-receipt")
        return DrainEcho(**{**base, **changes})

    def reconcile(self, echoes):
        return reconcile(echoes, known_seed_revisions=("v8.54",))

    def test_received_echo_is_not_proof_session_drained(self):
        row = self.reconcile((self.item(),))["accepted_for_review"][0]
        self.assertEqual(row["state"], "RECEIVED_FOR_REVIEW")
        self.assertFalse(row["actual_session_drain_proven"])

    def test_same_echo_dedupes_without_new_front(self):
        r = self.reconcile((self.item(), self.item()))
        self.assertEqual(len(r["accepted_for_review"]), 1)
        self.assertEqual(len(r["identical_echo_duplicates"]), 1)

    def test_changed_content_preserves_distinct_evolution(self):
        a, b = self.item(), self.item(body="better candidate")
        self.assertEqual(len(self.reconcile((a, b))["accepted_for_review"]), 2)

    def test_changed_seed_is_not_silently_same(self):
        r = self.reconcile((self.item(), self.item(seed_revision="v8.55")))
        self.assertEqual(len(r["accepted_for_review"]), 1)
        self.assertEqual(r["held"][0][1], "UNQUALIFIED_SEED_REVISION")

    def test_pasted_claim_without_provider_readback_is_held(self):
        r = self.reconcile((self.item(provider_readback=""),))
        self.assertEqual(r["accepted_for_review"], [])
        self.assertEqual(r["held"][0][1], "NO_INDEPENDENT_SESSION_READBACK")

    def test_unknown_session_not_inventoried(self):
        self.assertFalse(self.reconcile(())["complete_session_history"])

    def test_private_echo_never_public_ready(self):
        item = self.item(reviewer_approved_public=True)
        self.assertFalse(self.reconcile((item,))["accepted_for_review"][0]["public_projection_eligible"])

    def test_public_echo_needs_review_approval(self):
        item = self.item(source_scope="PUBLIC", reviewer_approved_public=False)
        self.assertFalse(self.reconcile((item,))["accepted_for_review"][0]["public_projection_eligible"])

    def test_public_approved_echo_only_eligible_not_published(self):
        item = self.item(source_scope="PUBLIC", reviewer_approved_public=True)
        r = self.reconcile((item,))
        self.assertTrue(r["accepted_for_review"][0]["public_projection_eligible"])
        self.assertEqual(r["public_write_effects"], 0)

    def test_public_rollup_has_no_sensitive_identifiers_or_body(self):
        r = self.reconcile((self.item(),))
        text = str(safe_public_rollup(r))
        for private in ("private:ref", "synthetic-provider-session", "synthetic echo", "test-receipt"):
            self.assertNotIn(private, text)

    def test_bounded_remainder_is_explicit(self):
        r = reconcile((self.item(), replace(self.item(), body="b"), replace(self.item(), body="c")),
                      known_seed_revisions=("v8.54",), max_records=2)
        self.assertIn(("OUTSIDE_BOUND", "REMAINING_UNINSPECTED"), r["held"])

    def test_missing_source_is_held(self):
        r = self.reconcile((self.item(source_ref=""),))
        self.assertEqual(r["held"][0][1], "INCOMPLETE_PROVENANCE")

    def test_no_mail_or_public_side_effects(self):
        r = self.reconcile((self.item(),))
        self.assertEqual((r["external_delivery_effects"], r["public_write_effects"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
