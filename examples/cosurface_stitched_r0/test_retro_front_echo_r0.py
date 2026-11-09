"""Temporal replay does not invent lost sessions, chronology, or receiver ACK."""
import hashlib
import unittest
from dataclasses import replace
from retro_front_echo_r0 import Echo, replay, chronological_view, public_rollup


HASH = hashlib.sha256(b"synthetic historical item").hexdigest()


class RetroFrontEchoTests(unittest.TestCase):
    def item(self, **changes):
        baseline = dict(source_ref="private:old-item", work_id="work-1",
                        revision="r1", content_sha256=HASH, front_id="CoMap",
                        historical_at="2024-01-01T00:00:00Z")
        return Echo(**{**baseline, **changes})

    def test_one_candidate_never_implies_complete_history(self):
        result = replay((self.item(),))
        self.assertEqual(len(result["accepted_candidates"]), 1)
        self.assertFalse(result["coverage"]["complete_history"])

    def test_duplicate_exact_work_revision_and_bytes_not_new_front(self):
        result = replay((self.item(), self.item(source_ref="private:other-copy")))
        self.assertEqual(len(result["accepted_candidates"]), 1)
        self.assertEqual(len(result["duplicate_identities"]), 1)

    def test_new_revision_retained_even_with_same_workid(self):
        result = replay((self.item(), self.item(revision="r2")))
        self.assertEqual(len(result["accepted_candidates"]), 2)

    def test_changed_bytes_retained_as_distinct_collision_candidate(self):
        different = hashlib.sha256(b"revision collision").hexdigest()
        result = replay((self.item(), self.item(content_sha256=different)))
        self.assertEqual(len(result["accepted_candidates"]), 2)
        self.assertTrue(all(x["coex"] is False for x in result["accepted_candidates"]))

    def test_missing_source_is_held(self):
        result = replay((self.item(source_ref=""),))
        self.assertEqual(result["held"][0][1], "INCOMPLETE_PROVENANCE")

    def test_invalid_sha_is_held(self):
        result = replay((self.item(content_sha256="pretend-sha"),))
        self.assertEqual(result["held"][0][1], "INVALID_HASH_FORMAT")

    def test_unseen_front_is_debt_not_fabricated_object(self):
        r = replay((self.item(),), known_fronts=("CoMap", "CoLUE", "CoSeed"))
        self.assertEqual(r["fronts_without_evidence"], ["CoLUE", "CoSeed"])

    def test_unknown_time_never_sorted_into_fabricated_history(self):
        r = replay((self.item(), self.item(work_id="work-2", historical_at="")),)
        view = chronological_view(r)
        self.assertEqual(len(view["known_historical_order"]), 1)
        self.assertEqual(len(view["unknown_historical_order"]), 1)
        self.assertFalse(view["timestamps_independently_verified"])

    def test_out_of_order_discovery_replay_uses_explicit_old_time(self):
        older = self.item(work_id="old", historical_at="2020-01-01T00:00:00Z")
        newer = self.item(work_id="new", historical_at="2025-01-01T00:00:00Z")
        view = chronological_view(replay((newer, older)))
        self.assertEqual([x["work_id"] for x in view["known_historical_order"]], ["old", "new"])

    def test_private_source_not_exposed_in_public_rollup(self):
        report = replay((self.item(source_ref="secret:local/path"),))
        text = str(public_rollup(report))
        for secret in ("secret:local/path", "work-1", HASH):
            self.assertNotIn(secret, text)

    def test_semantic_not_promoted_from_hash(self):
        row = replay((self.item(),))["accepted_candidates"][0]
        self.assertEqual(row["semantic_status"], "NOT_SEMANTICALLY_REVIEWED")
        self.assertEqual(row["lifecycle"], "VERIFIED_POINTER_NOT_ACCEPTED")

    def test_replay_is_bounded_and_exposes_remainder(self):
        entries = tuple(self.item(work_id=str(i)) for i in range(5))
        r = replay(entries, max_records=2)
        self.assertEqual(len(r["accepted_candidates"]), 2)
        self.assertIn(("UNINSPECTED_REMAINDER", "SCAN_BOUND_REACHED"), r["held"])

    def test_invalid_privacy_scope_cannot_enter_graph(self):
        r = replay((self.item(privacy_scope="UNDECIDED"),))
        self.assertEqual(r["held"][0][1], "UNKNOWN_PRIVACY_SCOPE")

    def test_retro_predictions_do_not_become_real_predictions(self):
        r = replay((self.item(),))
        self.assertFalse(r["coverage"]["retro_predictive_accuracy_proven"])

    def test_required_custody_nonclaims_retained(self):
        r = replay((self.item(),))
        self.assertIn("DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY", r["nonclaims"])
        self.assertIn("NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF", r["nonclaims"])


if __name__ == "__main__":
    unittest.main()
