import importlib.util
import json
import pathlib
import sys
import unittest
import numpy as np

SRC=pathlib.Path(__file__).resolve().parents[1]/'src'/'optical_control.py'
spec=importlib.util.spec_from_file_location('optical_control',SRC)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

class OpticalControlTest(unittest.TestCase):
    def test_seed_determinism(self):
        x,h=mod.surface()
        x2,h2=mod.surface()
        self.assertTrue(np.array_equal(x,x2))
        self.assertTrue(np.array_equal(h,h2))
    def test_seed_variant(self):
        _,a=mod.surface(seed=1)
        _,b=mod.surface(seed=2)
        self.assertFalse(np.array_equal(a,b))
    def test_horizon_shadow_direction(self):
        x,h=mod.surface()
        a,b=mod.horizon_shadows(x,h)
        self.assertGreater(np.mean(a!=b),.03)
    def test_missing_bad_surface(self):
        with self.assertRaises(ValueError):
            mod.horizon_shadows(np.array([0,2,1,3]),np.zeros(4))
    def test_angle_validation(self):
        x,h=mod.surface()
        for k in [-1,0,90,120]:
            with self.assertRaises(ValueError):mod.horizon_shadows(x,h,k)
    def test_single_coherent_is_nonnegative(self):
        _,h=mod.surface()
        z=mod.farfield_speckle(h)
        self.assertEqual(len(z),len(h))
        self.assertTrue(np.all(z>=0))
    def test_averaging_reduces_contrast_in_toy(self):
        _,h=mod.surface()
        a=mod.farfield_speckle(h)
        b=mod.phase_screen_average(h)
        self.assertLess(mod.contrast(b),mod.contrast(a))
    def test_surface_exists_despite_detector_dark_pixels(self):
        *_,metrics=mod.run()
        self.assertGreater(metrics['dark_detector_bins_at_below_quartile'],10)
        self.assertEqual(metrics['surface_material_cells_present'],mod.N)
    def test_no_cross_coordinate_inference(self):
        *_,metrics=mod.run()
        self.assertIn('detector angular bins are not surface gaps',metrics['model_limitations'])
    def test_no_external_instrument_claim(self):
        *_,metrics=mod.run()
        self.assertIn('not a physical measurement or laser procedure',metrics['model_limitations'])
    def test_no_anomalous_source_claim(self):
        *_,metrics=mod.run()
        self.assertIn('no inference about ET, G_d, DMT or invisible entities',metrics['model_limitations'])
    def test_zero_wavelength_rejected(self):
        _,h=mod.surface()
        with self.assertRaises(ValueError):mod.farfield_speckle(h,wavelength_um=0)
    def test_zero_ensemble_rejected(self):
        _,h=mod.surface()
        with self.assertRaises(ValueError):mod.phase_screen_average(h,realizations=0)
    def test_perturbation_changes_phase_pattern(self):
        _,h=mod.surface()
        a=mod.farfield_speckle(h)
        b=mod.farfield_speckle(h,extra_phase=np.linspace(0,7,len(h)))
        self.assertGreater(float(np.mean(np.abs(a-b))),1)

if __name__=='__main__':unittest.main()
