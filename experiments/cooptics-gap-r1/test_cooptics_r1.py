"""Bounded zero-network source tests: independently inspect every model boundary."""
import unittest
import numpy as np
from cooptics_r1 import SEED, make_height, illumination_mask, speckle_scenarios, polar_response

class CoOpticsR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h=make_height()
        cls.left=illumination_mask(cls.h)
        cls.right=illumination_mask(cls.h,False)
        cls.one,cls.avg,cls.stack=speckle_scenarios(cls.h)

    def test_height_shape(self):self.assertEqual(self.h.shape,(384,))
    def test_deterministic_height(self):self.assertTrue(np.array_equal(self.h,make_height()))
    def test_different_surface_seed(self):self.assertFalse(np.array_equal(self.h,make_height(seed=SEED+47)))
    def test_height_is_non_flat(self):self.assertGreater(self.h.std(),.1)
    def test_left_bool(self):self.assertEqual(self.left.dtype,bool)
    def test_right_bool(self):self.assertEqual(self.right.dtype,bool)
    def test_left_shadowing(self):self.assertGreater(np.count_nonzero(~self.left),20)
    def test_right_shadowing(self):self.assertGreater(np.count_nonzero(~self.right),20)
    def test_reversal_changes_shadow_pixels(self):self.assertGreater(np.mean(self.left!=self.right),.1)
    def test_shadow_mask_is_directionally_symmetric_under_reverse(self):self.assertTrue(np.array_equal(illumination_mask(self.h[::-1])[::-1],self.right))
    def test_flat_non_shadow_left(self):self.assertTrue(np.all(illumination_mask(np.zeros(384))))
    def test_flat_non_shadow_right(self):self.assertTrue(np.all(illumination_mask(np.zeros(384),False)))
    def test_valid_straight_up_illumination(self):self.assertTrue(np.all(illumination_mask(self.h,elevation_deg=89.0)))
    def test_speckle_count(self):self.assertEqual(self.stack.shape,(16,384))
    def test_positive_speckle_intensities(self):self.assertTrue(np.all(self.stack>=0))
    def test_positive_normalized_one(self):self.assertTrue(np.all(self.one>=0))
    def test_normalized_one_mean(self):self.assertAlmostEqual(float(np.mean(self.one)),1,places=10)
    def test_normalized_ensemble_mean(self):self.assertAlmostEqual(float(np.mean(self.avg)),1,places=10)
    def test_deterministic_speckle(self):self.assertTrue(np.array_equal(self.one,speckle_scenarios(self.h)[0]))
    def test_different_illumination_seed(self):self.assertFalse(np.array_equal(self.one,speckle_scenarios(self.h,seed=22)[0]))
    def test_speckle_bright_and_dark(self):self.assertGreater(float(np.max(self.one)/np.mean(self.one)),3.)
    def test_speckle_dark_fraction(self):self.assertGreater(np.mean(self.one<0.1),.01)
    def test_speckle_average_suppression(self):self.assertLess(np.std(self.avg),np.std(self.one)*.6)
    def test_speckle_ensemble_not_flat(self):self.assertGreater(float(np.std(self.avg)),.05)
    def test_single_ensemble_identical(self):
        one,mean,stack=speckle_scenarios(self.h,ensemble=1)
        self.assertTrue(np.allclose(one,mean))
    def test_surface_not_modified_by_speckle(self):
        before=self.h.copy();speckle_scenarios(self.h);self.assertTrue(np.array_equal(before,self.h))
    def test_polar_at_0(self):self.assertAlmostEqual(polar_response([0])[0],1)
    def test_polar_at_90(self):self.assertAlmostEqual(polar_response([90])[0],.04)
    def test_polar_period_180(self):self.assertAlmostEqual(polar_response([0])[0],polar_response([180])[0])
    def test_rotating_axis_swaps_response(self):self.assertAlmostEqual(polar_response([0],0)[0],polar_response([90],90)[0])
    def test_rotating_axis_swaps_minimum(self):self.assertAlmostEqual(polar_response([90],0)[0],polar_response([0],90)[0])
    def test_polar_output_bounds(self):self.assertTrue(np.all((polar_response(np.arange(0,361))>=.04-1e-10)&(polar_response(np.arange(0,361))<=1+1e-10)))
    def test_polar_angle_45(self):self.assertAlmostEqual(polar_response([45],0)[0],.52,places=10)
    def test_speckle_surface_coordinate_distinctness(self):self.assertEqual(len(self.one),len(self.h)) # Index equality is NOT physical-coordinate equality.

if __name__=='__main__':unittest.main(verbosity=2)
