import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from CoOomphFanInSaturationR0 import (
    MODES, NONCLAIMS, build_fixture, check_source, run, sample
)


class TestFanInScaling(unittest.TestCase):
    def test_original_compiler_blob_is_exact(self):
        self.assertEqual(check_source(), "690cba4811eb8f4cf8cb6f4b1d4b52d8b6776002")

    def test_echo_18_has_one_unique_candidate(self):
        row = sample(18, "echo")
        self.assertEqual(row["accepted_schema_records"], 18)
        self.assertEqual(row["unique_operation_candidates"], 1)
        self.assertEqual(row["duplicate_groups"], 1)
        self.assertEqual(row["eligible_unique_review_candidates"], 1)
        self.assertEqual(row["hypothetical_next_wave_backlog"], 0)

    def test_diverse_18_produces_review_backlog(self):
        row = sample(18, "diverse")
        self.assertEqual(row["unique_operation_candidates"], 18)
        self.assertEqual(row["eligible_unique_review_candidates"], 18)
        self.assertEqual(row["hypothetical_next_wave_backlog"], 10)

    def test_saturated_pool_plateaus_at_32(self):
        row = sample(256, "pool32")
        self.assertEqual(row["unique_operation_candidates"], 32)
        self.assertEqual(row["eligible_unique_review_candidates"], 32)
        self.assertEqual(row["hypothetical_next_wave_backlog"], 24)

    def test_unique_256_overflows_hypothetical_review(self):
        row = sample(256, "diverse")
        self.assertEqual(row["unique_operation_candidates"], 256)
        self.assertEqual(row["hypothetical_next_wave_backlog"], 248)
        self.assertEqual(row["real_worker_sessions_started"], 0)

    def test_collision_is_quarantined_not_promoted(self):
        row = sample(64, "collision4")
        self.assertEqual(row["unique_operation_candidates"], 4)
        self.assertEqual(row["collision_review_groups"], 1)
        self.assertEqual(row["eligible_unique_review_candidates"], 0)

    def test_private_inputs_are_not_fanned_out(self):
        row = sample(64, "private")
        self.assertEqual(row["public_holds"], 64)
        self.assertEqual(row["eligible_unique_review_candidates"], 0)

    def test_single_item_no_false_duplicate(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                row = sample(1, mode)
                self.assertEqual(row["duplicate_groups"], 0)

    def test_all_scales_zero_effects(self):
        out = run(sizes=(1, 18))
        self.assertEqual(out["real_workers_started"], 0)
        self.assertEqual(out["real_effects"], 0)
        self.assertFalse(out["external_receiver_ack"])
        self.assertEqual(len(out["rows"]), 10)
        self.assertIn("UNIQUE_OPERATION_HASH_NE_VERIFIED_USEFUL_RESULT", NONCLAIMS)

    def test_disallowed_budgets_and_sizes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "BOUNDED_COUNT_REQUIRED"):
            build_fixture(257, "echo")
        with self.assertRaisesRegex(ValueError, "BOUNDED_COUNT_REQUIRED"):
            build_fixture(0, "echo")
        with self.assertRaisesRegex(ValueError, "REVIEW_BUDGET_BOUND_REQUIRED"):
            sample(1, "echo", 0)
        with self.assertRaisesRegex(ValueError, "UNKNOWN_MODE"):
            build_fixture(1, "not_a_mode")


if __name__ == "__main__":
    unittest.main()
