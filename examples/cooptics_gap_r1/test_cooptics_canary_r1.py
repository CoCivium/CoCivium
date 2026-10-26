"""Deterministic, negative-case and semantic-boundary tests for CoOptics R1."""
import json
import random
import tempfile
import unittest
from pathlib import Path
import numpy as np
from cooptics_canary_r1 import summarize, surface, shadow_lit, toy_speckle, N

class Canary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = summarize(20261026)
        cls.h = surface(20261026)

    def test_source_deterministic(self):
        self.assertEqual(surface(99).tolist(), surface(99).tolist())
    def test_distinct_seed(self):
        self.assertNotEqual(surface(99).tolist(), surface(100).tolist())
    def test_packet_deterministic(self):
        self.assertEqual(json.dumps(summarize(20261026),sort_keys=True), json.dumps(summarize(20261026),sort_keys=True))
    def test_fixed_size(self):
        self.assertEqual(len(self.d['arrays']['surface_height']),N)
    def test_n_constraints_low(self):
        with self.assertRaises(ValueError): summarize(n=4)
    def test_n_constraints_high(self):
        with self.assertRaises(ValueError): summarize(n=99999)
    def test_shadow_left(self):
        self.assertGreater(self.d['metrics']['shadowed_left'],0)
    def test_shadow_right(self):
        self.assertGreater(self.d['metrics']['shadowed_right'],0)
    def test_direction_changes_shadow(self):
        self.assertGreater(self.d['metrics']['shadow_status_diff_count'],0)
    def test_bad_side(self):
        with self.assertRaises(ValueError): shadow_lit(self.h, 'above')
    def test_bad_angle(self):
        with self.assertRaises(ValueError): shadow_lit(self.h, 'left',alpha_deg=0)
    def test_bad_pitch(self):
        with self.assertRaises(ValueError): shadow_lit(self.h, 'right',pitch=-1)
    def test_no_shadow_at_near_vertical(self):
        self.assertTrue(np.all(shadow_lit(self.h,'left',alpha_deg=89.999)==1))
    def test_detector_not_surface_mapping(self):
        self.assertIn('AXES_NOT_ONE_TO_ONE',self.d['warnings'][0])
    def test_incoherent_control_constant(self):
        self.assertEqual(set(self.d['arrays']['incoherent_detector_control']),{1.0})
    def test_speckle_variance(self):
        self.assertGreater(self.d['metrics']['coherent_speckle_cv'],0.1)
    def test_low_detector_bin(self):
        self.assertGreater(self.d['metrics']['low_detector_bins_fraction_below_point_1_mean'],0)
    def test_analyzer_change(self):
        self.assertGreater(self.d['metrics']['mean_abs_polarization_change'],0.05)
    def test_wavelength_change(self):
        self.assertGreater(self.d['metrics']['mean_abs_wavelength_change'],0.05)
    def test_normalization(self):
        for deg in (0,45,90):
            self.assertAlmostEqual(float(np.mean(toy_speckle(self.h,.532,deg))),1.0,places=9)
    def test_global_surface_height_shift_only_changes_global_phase(self):
        # A global phase factor must not change normalized far-field intensity.
        baseline = toy_speckle(self.h,.532,0)
        shifted = toy_speckle(self.h+0.61,.532,0)
        self.assertTrue(np.allclose(baseline,shifted,rtol=1e-8,atol=1e-8))
    def test_flat_surface_has_no_geometric_shadow(self):
        flat = np.zeros(64)
        self.assertTrue(np.all(shadow_lit(flat, 'left')==1))
        self.assertTrue(np.all(shadow_lit(flat, 'right')==1))
    def test_shadow_not_claimed_optical_intensity(self):
        self.assertIn('RAY_SHADOW', self.d['hypotheses'][0])
        self.assertIn('CALIBRATED_VECTOR_SCATTERING', self.d['warnings'][1])
    def test_negative_bad_wavelength(self):
        with self.assertRaises(ValueError): toy_speckle(self.h,0)
    def test_negative_bad_polarizer(self):
        with self.assertRaises(ValueError): toy_speckle(self.h,.532,999)
    def test_status_honest(self):
        self.assertEqual(self.d['status'],'PASS_SYNTHETIC_ONLY')
    def test_no_effects(self):
        self.assertEqual(self.d['external_effects'],[])
        self.assertEqual(self.d['authority'],'NONE')
    def test_no_optical_real_world_claim(self):
        self.assertIn('NO_PHYSICAL_LIGHT_OR_SENSOR_USED',self.d['warnings'])
    def test_no_et_signal_claim(self):
        self.assertIn('DARK_DETECTOR_BIN_IS_NOT_A_VOID_OR_ET_SIGNAL',self.d['warnings'])
    def test_known_surface_digest(self):
        self.assertRegex(self.d['source_surface_sha256'],r'^[0-9a-f]{64}$')
    def test_surface_invariant_direction(self):
        self.assertEqual(self.d['source_surface_sha256'],summarize(20261026)['source_surface_sha256'])
    def test_surface_changes_seed_hash(self):
        self.assertNotEqual(self.d['source_surface_sha256'],summarize(20261027)['source_surface_sha256'])
    def test_model_uses_separate_axes(self):
        self.assertNotEqual(self.d['arrays']['left_ray_illuminated'],self.d['arrays']['detector_0deg_normalized_intensity'])
    def test_all_arrays_lengths(self):
        self.assertTrue(all(len(v)==N for v in self.d['arrays'].values()))
    def test_safe_rerun_no_fixed_timestamp(self):
        self.assertNotIn('observed_at', self.d)
    def test_no_arbitrary_negative_claim(self):
        self.assertNotIn('UNKNOWN_ET_DETECTED',json.dumps(self.d))
    def test_coherent_different_from_flat(self):
        self.assertFalse(np.allclose(np.array(self.d['arrays']['detector_0deg_normalized_intensity']),1.0))
    def test_left_right_are_binary(self):
        self.assertLessEqual(set(self.d['arrays']['left_ray_illuminated']),{0,1})
    def test_different_n_allowed(self):
        self.assertEqual(len(summarize(n=48)['arrays']['surface_height']),48)
    def test_synthetic_budget(self):
        self.assertLessEqual(self.d['n'],2048)

if __name__=='__main__':
    unittest.main(verbosity=2)
