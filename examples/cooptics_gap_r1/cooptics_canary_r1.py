#!/usr/bin/env python3
"""CoOpticsGap R1: synthetic, pedagogical ray-shadows vs coherent speckle.

Requires: Python 3.9+ and NumPy.  NO laser, camera, device, network, or ET interface.
The toy Jones cross-polarization term is an illustrative ansatz, NOT a
calibrated vector scattering model or physical measurement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
from pathlib import Path

import numpy as np

SCHEMA = "CoCivium.CoOpticsGap.SyntheticShadowSpeckle.R1"
N = 192
PITCH = 0.40  # arbitrary surface coordinate units
WAVELENGTH = 0.532  # same arbitrary units as surface height, illustrative
WAVELENGTH_ALT = 0.633
ALPHA_DEG = 15.0


def surface(seed: int, n: int = N) -> np.ndarray:
    """Deterministic rough relief with several scales and a few taller facets."""
    rng = random.Random(seed)
    noise = [rng.gauss(0, 1) for _ in range(n)]
    smooth = [sum(noise[max(0, i-2):min(n, i+3)]) / len(noise[max(0, i-2):min(n, i+3)]) for i in range(n)]
    phase = rng.uniform(-math.pi, math.pi)
    h = [0.75 * math.sin(2*math.pi*3*i/n + phase)
         + 0.35 * math.sin(2*math.pi*13*i/n + phase/3)
         + 0.70 * smooth[i] for i in range(n)]
    return np.array(h, dtype=float)


def shadow_lit(h: np.ndarray, side: str, alpha_deg: float = ALPHA_DEG, pitch: float = PITCH) -> np.ndarray:
    """Simple 2D ray occlusion at an oblique virtual illumination angle.

    1 = illuminated.  0 = geometrically shadowed from designated side.
    No diffraction, refraction, inter-facet reflection or subsurface return.
    """
    if side not in ("left", "right"):
        raise ValueError("side must be left or right")
    if not (0 < alpha_deg < 90) or pitch <= 0:
        raise ValueError("invalid ray geometry")
    h = np.asarray(h, dtype=float)
    if h.ndim != 1 or not (2 <= h.size <= 2048) or not np.all(np.isfinite(h)):
        raise ValueError('invalid or nonfinite shadow geometry')
    n = len(h)
    lit = np.ones(n, dtype=int)
    slope = math.tan(math.radians(alpha_deg)) * pitch
    for i in range(n):
        indices = range(i-1, -1, -1) if side == "left" else range(i+1, n)
        for j in indices:
            ray_height = float(h[i]) + abs(i-j)*slope
            if float(h[j]) > ray_height + 1e-12:
                lit[i] = 0
                break
    return lit


def toy_speckle(h: np.ndarray, wavelength: float, analyzer_deg: float = 0.0,
                incidence_deg: float = ALPHA_DEG) -> np.ndarray:
    """Toy far-field detector intensity, NOT a direct surface image.

    Scalar phase return from height (no full Maxwell solution). A deliberately
    simplified Jones cross-component depends on local slopes, solely to
    demonstrate how an analyzer can change a computed interference pattern.
    """
    if not all(np.isscalar(v) and np.isfinite(v) for v in (wavelength, analyzer_deg, incidence_deg)):
        raise ValueError('nonfinite or nonscalar optical parameters')
    if wavelength <= 0 or not (0 <= analyzer_deg <= 180) or not (0 <= incidence_deg <= 90):
        raise ValueError('invalid optical parameters')
    h = np.asarray(h, dtype=float)
    if h.ndim != 1 or not (2 <= h.size <= 2048) or not np.all(np.isfinite(h)):
        raise ValueError('invalid or nonfinite surface heights')
    phase = 4 * math.pi * h * math.cos(math.radians(incidence_deg)) / wavelength
    slopes = np.gradient(h, PITCH)
    cross_amplitude = 0.38 * np.tanh(2.5 * slopes)
    field = np.exp(1j*phase)
    a = math.radians(analyzer_deg)
    analyzer_field = (math.cos(a) + math.sin(a)*cross_amplitude) * field
    spectrum = np.fft.fftshift(np.fft.fft(analyzer_field))
    intensity = np.abs(spectrum) ** 2
    # CRITICAL NEGATIVE: a numerically extinguished synthetic polarization channel
    # must not be amplified to unit mean by per-projection normalization.
    # This fixed dimensionless floor is a numerical guard, NOT sensor sensitivity.
    mean_raw = float(np.mean(intensity))
    if not np.isfinite(mean_raw) or mean_raw <= len(h) * 1e-24:
        return np.zeros_like(intensity)
    # Normalize only within viable toy detector projection; no absolute radiometry.
    return intensity / mean_raw


def summarize(seed: int = 20261026, n: int = N) -> dict:
    if not (16 <= n <= 2048):
        raise ValueError("n out of safe bounded range")
    h = surface(seed, n)
    left, right = shadow_lit(h, "left"), shadow_lit(h, "right")
    sp0 = toy_speckle(h, WAVELENGTH, analyzer_deg=0)
    sp45 = toy_speckle(h, WAVELENGTH, analyzer_deg=45)
    sp_alt = toy_speckle(h, WAVELENGTH_ALT, analyzer_deg=0)
    delta_shadow = int(np.sum(left != right))
    delta_pol = float(np.mean(np.abs(sp0 - sp45)))
    delta_wavelength = float(np.mean(np.abs(sp0 - sp_alt)))
    result = {
        "schema": SCHEMA,
        "status": "PASS_SYNTHETIC_ONLY",
        "seed": seed, "n": n,
        "config": {"pitch_arbitrary": PITCH, "wavelength_arbitrary": WAVELENGTH,
                   "wavelength_alt_arbitrary": WAVELENGTH_ALT,
                   "grazing_elevation_degrees": ALPHA_DEG, "analyzer_degrees": [0, 45]},
        "hypotheses": ["H1_RAY_SHADOW", "H2_COHERENT_DETECTOR_SPECKLE", "H3_TOY_ANALYZER_EFFECT"],
        "metrics": {
            "shadowed_left": int(np.sum(left == 0)),
            "shadowed_right": int(np.sum(right == 0)),
            "shadow_status_diff_count": delta_shadow,
            "coherent_speckle_cv": round(float(np.std(sp0)), 6),
            "mean_abs_polarization_change": round(delta_pol, 6),
            "mean_abs_wavelength_change": round(delta_wavelength, 6),
            "low_detector_bins_fraction_below_point_1_mean": round(float(np.mean(sp0 < 0.1)), 6),
        },
        "source_surface_sha256": hashlib.sha256(h.tobytes()).hexdigest(),
        "arrays": {
            "surface_height": [round(float(x), 6) for x in h],
            "left_ray_illuminated": left.astype(int).tolist(),
            "right_ray_illuminated": right.astype(int).tolist(),
            "detector_0deg_normalized_intensity": [round(float(x), 6) for x in sp0],
            "detector_45deg_normalized_intensity": [round(float(x), 6) for x in sp45],
            "detector_alt_wavelength_normalized_intensity": [round(float(x), 6) for x in sp_alt],
            "incoherent_detector_control": [1.0] * n,
        },
        "warnings": [
            "RAY_SHADOWS_ARE_SURFACE_POSITION; SPECKLE_IS_DETECTOR_POSITION; AXES_NOT_ONE_TO_ONE",
            "JONES_MIXING_IS_TOY_NOT_CALIBRATED_VECTOR_SCATTERING",
            "NO_PHYSICAL_LIGHT_OR_SENSOR_USED",
            "DARK_DETECTOR_BIN_IS_NOT_A_VOID_OR_ET_SIGNAL",
            "NEAR_ZERO_SYNTHETIC_CHANNEL_ZEROED_BEFORE_NORMALIZATION_NOT_A_PHYSICAL_DARKNESS_MEASUREMENT",
            "NO_DMT_STUDY_OR_EXTERNAL_CONTACT",
        ],
        "external_effects": [],
        "authority": "NONE",
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=20261026)
    ap.add_argument("--n", type=int, default=N)
    ap.add_argument("--output", type=Path, default=None, help="Explicit new JSON path (no clobber)")
    args = ap.parse_args()
    packet = summarize(args.seed, args.n)
    data = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(data, end="")
    else:
        # Exclusive creation prevents overwriting any receipt/source from a previous wave.
        with args.output.open("x", encoding="utf8") as f:
            f.write(data)
        print(json.dumps({"state": "PASS_SYNTHETIC_ONLY", "file": str(args.output),
                          "sha256": hashlib.sha256(data.encode()).hexdigest(),
                          "metrics": packet["metrics"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
