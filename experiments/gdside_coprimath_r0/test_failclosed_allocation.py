"""Negative controls for G_dSide allocation guards, including python -O."""
import math
import unittest

import simulate


class FailClosedAllocationTests(unittest.TestCase):
    def test_valid_allocation(self):
        self.assertEqual(simulate.checked_extraction([1, 2, 3, 4], 100, 4), 10)

    def test_cap_violation(self):
        with self.assertRaisesRegex(ValueError, "HOLD_EXTRACTION_CAP"):
            simulate.checked_extraction([8, 8, 0, 0], 100, 4)

    def test_negative_allocation(self):
        with self.assertRaisesRegex(ValueError, "HOLD_ALLOCATION_NONFINITE_OR_NEGATIVE"):
            simulate.checked_extraction([-1, 2, 0, 0], 100, 4)

    def test_nonfinite_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "HOLD_ALLOCATION_NONFINITE_OR_NEGATIVE"):
                    simulate.checked_extraction([value, 0, 0, 0], 100, 4)

    def test_bool_disallowed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_ALLOCATION_NONFINITE_OR_NEGATIVE"):
            simulate.checked_extraction([True, 0, 0, 0], 100, 4)

    def test_wrong_shape(self):
        with self.assertRaisesRegex(ValueError, "HOLD_ALLOCATION_SHAPE"):
            simulate.checked_extraction([1, 2], 100, 4)

    def test_unknown_policy(self):
        with self.assertRaisesRegex(ValueError, "HOLD_UNKNOWN_POLICY"):
            simulate.run_one(1, "unverified")

    def test_zero_or_invalid_steps(self):
        for value in (0, -1, 1.5, True):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "HOLD_INVALID_STEPS"):
                    simulate.run_one(1, "hybrid", steps=value)

    def test_determinism_preserved(self):
        first = simulate.run_one(3, "gdside", 6)
        self.assertEqual(first, simulate.run_one(3, "gdside", 6))


if __name__ == "__main__":
    unittest.main()
