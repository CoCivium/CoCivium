#!/usr/bin/env python3
"""A limited 1D pedagogical model: geometric shadows vs detector interference.

The geometry model is a 1D horizon mask; the optical model is a scalar
Fraunhofer FFT of a height-dependent phase screen. It omits actual material
BRDFs, multiple scattering, polarization matrices, near fields and real
instruments. It is NOT evidence of any real detection or physical laser test.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np

SEED = 20261026
N = 512
WAVELENGTH_UM = 0.532


def surface(seed: int = SEED, n: int = N):
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 10.0, n, endpoint=False)
    white = rng.normal(size=n)
    freq = np.fft.rfftfreq(n, d=x[1] - x[0])
    smooth = np.fft.irfft(np.fft.rfft(white) * np.exp(-0.5 * (freq / 3.5) ** 2), n=n)
    smooth /= max(np.std(smooth), 1e-9)
    h = 0.19 * smooth + 0.13 * np.sin(2 * np.pi * 0.9 * x) + 0.06 * np.sin(2 * np.pi * 2.1 * x + 0.8)
    return x, h


def horizon_shadows(x, h, grazing_angle_deg=16.0):
    """Parallel rays, 1D height-profile approximation, no multiple bounces."""
    if len(x) != len(h) or len(x) < 4 or not np.all(np.diff(x) > 0):
        raise ValueError('INVALID_SURFACE')
    if not (0 < grazing_angle_deg < 90):
        raise ValueError('INVALID_ANGLE')
    m = np.tan(np.deg2rad(grazing_angle_deg))
    q_left = h + m * x
    past = np.maximum.accumulate(q_left)
    left = np.r_[False, past[:-1] > q_left[1:] + 1e-12]
    q_right = h - m * x
    later = np.maximum.accumulate(q_right[::-1])[::-1]
    right = np.r_[later[1:] > q_right[:-1] + 1e-12, False]
    return left, right


def farfield_speckle(h, *, wavelength_um=WAVELENGTH_UM, extra_phase=None):
    """Scalar far field at DETECTOR angle bins, not at source x positions."""
    if wavelength_um <= 0:
        raise ValueError('INVALID_WAVELENGTH')
    n = len(h)
    phase = 4 * np.pi * np.asarray(h) / wavelength_um
    if extra_phase is not None:
        phase = phase + np.asarray(extra_phase)
    field = np.hanning(n) * np.exp(1j * phase)
    intensity = np.abs(np.fft.fftshift(np.fft.fft(field))) ** 2
    return intensity


def phase_screen_average(h, seed=SEED, realizations=48):
    if realizations < 1:
        raise ValueError('INVALID_REALIZATIONS')
    rng = np.random.default_rng(seed)
    return np.mean([farfield_speckle(h, extra_phase=rng.uniform(-np.pi, np.pi, len(h)))
                    for _ in range(realizations)], axis=0)


def contrast(a):
    a = np.asarray(a)
    return float(np.std(a) / np.mean(a))


def run(seed=SEED):
    x, h = surface(seed)
    left, right = horizon_shadows(x, h)
    one = farfield_speckle(h)
    average = phase_screen_average(h, seed=seed + 1)
    # Independent masks compare along SOURCE x; detector pattern is separate space.
    angular = np.fft.fftshift(np.fft.fftfreq(len(h)))
    central = np.abs(angular) < 0.35
    # Do not compare pixelwise source shadows to angular detector intensity.
    metrics = {
        'seed': seed,
        'n_surface_points': len(h),
        'grazing_angle_degrees': 16.0,
        'wavelength_um': WAVELENGTH_UM,
        'fraction_shadowed_from_left': round(float(np.mean(left)), 6),
        'fraction_shadowed_from_right': round(float(np.mean(right)), 6),
        'fraction_changed_under_illumination_reversal': round(float(np.mean(left != right)), 6),
        'speckle_contrast_single_phase_screen': round(contrast(one[central]), 6),
        'speckle_contrast_averaged_independent_screens': round(contrast(average[central]), 6),
        'dark_detector_bins_at_below_quartile': int(np.sum(one[central] < np.quantile(one[central], .25))),
        'surface_material_cells_present': len(h),
        'source_surface_sha256': hashlib.sha256(h.astype('<f8').tobytes()).hexdigest(),
        'controls': ['illumination_direction_reversal_source_geometry',
                     'independent_phase_screen_average_detector_field'],
        'model_limitations': ['1D geometric horizon and scalar far-field toy',
                              'not an actual polarized Maxwell/scattering solver',
                              'not a physical measurement or laser procedure',
                              'detector angular bins are not surface gaps',
                              'no inference about ET, G_d, DMT or invisible entities'],
    }
    return x, h, left, right, angular, one, average, metrics


def chart(x, h, left, right, angle, single, averaged, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    fig, axes = plt.subplots(3, 1, figsize=(12, 8.5))
    fig.subplots_adjust(left=.10, right=.97, top=.92, bottom=.16, hspace=.80)
    ax = axes[0]
    ax.plot(x, h, color='#466b88', lw=1.5)
    ax.fill_between(x, h.min()-.04, h, color='#8db3c2', alpha=.25)
    ax.set_ylabel('Height (toy units)')
    ax.set_title('SAME PINNED SYNTHETIC SURFACE / DIFFERENT CONTRAST MECHANISMS', loc='left', fontweight='bold', fontsize=12)
    ax.text(.01,.02, 'Source geometry: 512 synthetic height points', transform=ax.transAxes, fontsize=8)
    ax = axes[1]
    ax.step(x, left.astype(int)+.05, where='mid', color='#cc7d32', lw=1.5, label='From left')
    ax.step(x, right.astype(int)-.05, where='mid', color='#5b8e78', lw=1.2, label='From right')
    ax.set_ylim(-.25,1.3)
    ax.set_yticks([0,1], ['lit', 'shadow'])
    ax.set_xlabel('Surface position x (arbitrary units)')
    ax.set_title('H1: geometric shadow mask / left vs right grazing illumination', loc='left', fontsize=10)
    ax.legend(loc='upper right', frameon=False)
    ax = axes[2]
    p = np.abs(angle) < .35
    def scaled(y):
        z = np.asarray(y)[p]
        return 10*np.log10(np.maximum(z/np.max(z), 1e-12))
    ax.plot(angle[p],scaled(single), color='#8b5aa4', lw=1.0,label='One coherent phase screen')
    ax.plot(angle[p],scaled(averaged), color='#236d8b', lw=1.3,label='48 independent phase screens averaged')
    ax.set_ylim(-65,5)
    ax.set_ylabel('Relative intensity (dB)')
    ax.set_xlabel('DETECTOR spatial-frequency bin (not surface coordinate)')
    ax.set_title('H2: scalar interference / phase-screen ensemble control',loc='left',fontsize=10)
    ax.legend(loc='lower center', frameon=False, fontsize=8, ncol=2)
    fig.text(.10,.035,'SYNTHETIC EDUCATIONAL MODEL. Not a polarized-wave solver, lab measurement, or ET detector.',fontsize=9)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    root=Path(__file__).resolve().parents[1]
    x,h,l,r,angle,one,avg,m=run()
    out=root/'output'
    out.mkdir(exist_ok=True)
    chart(x,h,l,r,angle,one,avg,out/'optics_control.png')
    (out/'measurement.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(m,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
