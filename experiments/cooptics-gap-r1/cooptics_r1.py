#!/usr/bin/env python3
"""CoOpticsGap R1 synthetic discriminator, NOT Maxwell or measurement.

This runnable standard NumPy/Matplotlib toy is an educational inverse/null canary.
Keep far-field detector indices distinct from actual surface coordinates.
No network, device, sensors, drug protocol, ET input, credentials, external effects.
"""
import json
import hashlib
from pathlib import Path
import numpy as np

SEED = 2601026
POINTS = 384
WAVENUMBER_TOY = 8.0
ELEV_DEG = 13.0
ENSEMBLE = 16


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def make_height(n=POINTS, seed=SEED):
    """1D synthetic profile; units are arbitrary (not nm, not fabricated)."""
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=n)
    kernel_x = np.arange(-15, 16)
    kernel = np.exp(-0.5*(kernel_x/5.5)**2)
    kernel /= kernel.sum()
    smoothed = np.convolve(raw, kernel, mode='same')
    profile = smoothed + .23*np.sin(np.linspace(0, 15*np.pi, n))
    profile = .75 * (profile-profile.mean())/profile.std()
    return profile


def illumination_mask(h, from_left=True, elevation_deg=ELEV_DEG):
    """Ray-occlusion toy. Horizontal step=.14; height shares arbitrary units.

    Ray from left to right climbs up right-to-left by tan(elevation).
    An earlier higher point intercepts the source path when h[j] >
    h[i] + (i-j)*dx*tan(elevation). Not a wave-optics solution.
    """
    values = np.asarray(h)
    if not from_left:
        return illumination_mask(values[::-1], True, elevation_deg)[::-1]
    dx=.14
    slope=np.tan(np.deg2rad(elevation_deg))
    allowed=np.ones(len(values), dtype=bool)
    for i in range(1,len(values)):
        j=np.arange(i)
        upstream_clearance=values[i]+(i-j)*dx*slope
        if np.any(values[j] > upstream_clearance+1e-10):
            allowed[i] = False
    return allowed


def speckle_scenarios(h, seed=SEED+1, ensemble=ENSEMBLE):
    """Fraunhofer-style phase-screen toy, detector-coordinate intensities.

    Independent phase screens are changes to *illumination realization*,
    NOT changing the pinned rough surface itself. Averaged intensities may
    suppress speckle under decorrelation; neither is a real measured field.
    """
    rng=np.random.default_rng(seed)
    win=np.hanning(len(h))
    height_phase=WAVENUMBER_TOY*h
    patterns=[]
    for _ in range(ensemble):
        # independent randomized incident phases for this synthetic control
        phi=rng.uniform(-np.pi,np.pi,size=len(h))
        amp=win*np.exp(1j*(height_phase+phi))
        out=np.fft.fftshift(np.fft.fft(amp))
        patterns.append((np.abs(out)**2).astype(float))
    stack=np.array(patterns)
    reference=stack[0]/np.mean(stack[0])
    avg=np.mean(stack,axis=0)
    avg/=np.mean(avg)
    return reference,avg,stack


def polar_response(angles_deg, axis_deg=0, leak=.04):
    """cos² toy for a hypothetical gap axis. Not a plasmonics solver.

    The nonzero 'leak' is an explicit heuristic; field enhancement requires
    material permittivity, exact morphology, wavelength, and Maxwell solver.
    """
    ang=np.deg2rad(np.asarray(angles_deg)-axis_deg)
    return leak+(1-leak)*np.cos(ang)**2


def run(out_dir):
    p=Path(out_dir)
    p.mkdir(parents=True,exist_ok=True)
    h=make_height()
    l=illumination_mask(h,True)
    r=illumination_mask(h,False)
    s,avg,stack=speckle_scenarios(h)
    ang=np.linspace(0,180,181)
    px=polar_response(ang,0)
    py=polar_response(ang,90)
    flat_mask=illumination_mask(np.zeros_like(h))
    stats={
      'schema':'CoCivium.CoOpticsGap.SyntheticDiscrimination.R1',
      'date':'2026-10-26','state':'SYNTHETIC_ONLY_NO_MEASUREMENT_OR_ET_SIGNAL',
      'seed_surface':SEED,'seed_phase':SEED+1,'surface_samples':POINTS,
      'shadow_incidence_elevation_degrees':ELEV_DEG,
      'shadow_fraction_from_left':round(float(1-np.mean(l)),6),
      'shadow_fraction_from_right':round(float(1-np.mean(r)),6),
      'shadow_orientation_changed_fraction':round(float(np.mean(l != r)),6),
      'flat_surface_shadows':int(np.count_nonzero(~flat_mask)),
      'speckle_ensemble_count':ENSEMBLE,
      'single_speckle_contrast_std_div_mean':round(float(np.std(s)/np.mean(s)),6),
      'averaged_speckle_contrast_std_div_mean':round(float(np.std(avg)/np.mean(avg)),6),
      'single_detector_bins_below_0p1mean_fraction':round(float(np.mean(s<.1)),6),
      'illumination_scrambling_changes_phase_not_surface':True,
      'polarization_0deg_for_axis0':round(float(polar_response([0],0)[0]),6),
      'polarization_90deg_for_axis0':round(float(polar_response([90],0)[0]),6),
      'figure':'cooptics_r1_control_figure.png',
      'nonclaims':['RAY_TOY_NE_CALIBRATED_ROUGH_SURFACE','PHASE_SCREEN_NE_FULL_MAXWELL','DETECTOR_DARK_NE_EMPTY_SURFACE_GAP','COS2_TOY_NE_NANOGAP_SOLVER','SIMULATION_NE_ET_SIGNAL','ENERGY_ENHANCEMENT_NE_ENERGY_CREATION','NO_DMT_OR_DEVICE_TEST','NO_ACTUAL_CCC_COEBE_ADOPTION']
    }
    # Legitimate test assertions, with a conscious zero-data baseline.
    assert stats['flat_surface_shadows']==0
    assert stats['shadow_fraction_from_left']>.04
    assert stats['shadow_fraction_from_right']>.04
    assert stats['shadow_orientation_changed_fraction']>.10
    assert stats['single_speckle_contrast_std_div_mean']>.6
    assert stats['averaged_speckle_contrast_std_div_mean'] < .55
    assert stats['averaged_speckle_contrast_std_div_mean'] < .6*stats['single_speckle_contrast_std_div_mean']
    assert polar_response([0],0)[0]>polar_response([90],0)[0]
    assert polar_response([0],90)[0]<polar_response([90],90)[0]
    assert 0<stats['single_detector_bins_below_0p1mean_fraction']<.35
    assert np.array_equal(make_height(),h)
    assert np.array_equal(speckle_scenarios(h)[0],s)
    assert not np.array_equal(s,avg)
    # Record exact generated data without crowding outputs with massive arrays.
    stats['height_array_sha256']=sha256(h.astype('<f8').tobytes())
    stats['speckle_single_sha256']=sha256(s.astype('<f8').tobytes())
    stats['speckle_average_sha256']=sha256(avg.astype('<f8').tobytes())
    (p/'metrics.json').write_text(json.dumps(stats,indent=2,sort_keys=True)+'\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    xx=np.arange(len(h))
    ax=axs[0,0]
    ax.plot(xx,h,'k-',lw=.7,label='Pinned synthetic height (arbitrary units)')
    ax.scatter(xx[l],h[l],s=8,marker='.',label='Lit by LEFT oblique ray')
    ax.scatter(xx[r],h[r]+.12,s=8,marker='.',label='Lit by RIGHT ray (+.12 offset)')
    ax.set(xlabel='Surface coordinate (index, NOT detector pixel)',ylabel='Toy height (arbitrary)',title='A. Geometric shadow masks: reversal changes valleys')
    ax.legend(fontsize=7,loc='lower right')

    ax=axs[0,1]
    det_axis=np.arange(len(s))
    ax.plot(det_axis,s,lw=.8,label='One coherent phase-screen realization')
    ax.plot(det_axis,avg,lw=1.5,label='Mean of 16 scrambled illumination phases')
    ax.axhline(.1,color='gray',ls=':',label='Detector 10% of mean; not zero field')
    ax.set(xlabel='Angular detector bin (NOT mapped to a surface valley)',ylabel='Normalized far-field intensity',title='B. Speckle vs phase-scrambled ensemble')
    ax.set_ylim(0,min(8,max(6,np.quantile(s,.995))))
    ax.legend(fontsize=7)

    ax=axs[1,0]
    ax.plot(ang,px,label='Toy axis 0 degrees')
    ax.plot(ang,py,label='Toy axis 90 degrees')
    ax.set(xlabel='Incident linear polarization angle (degrees)',ylabel='Illustrative normalized response',title='C. cos² selection toy; NOT Maxwell/nanogap measurement')
    ax.legend(fontsize=8)

    ax=axs[1,1];ax.axis('off')
    lines=[
     'D. CoNull / CoTurtle discrimination',
     '',
     'DARK detector bin  !=  EMPTY nanogap',
     'LIT geometric valley != near-field hot spot',
     'cos² toy            != Maxwell solution',
     'single pattern     != independent cause',
     'unresolved residual!= ET or G_d evidence',
     '',
     'Counters and control checks:',
     f'Left shadowed: {stats["shadow_fraction_from_left"]:.1%}',
     f'Right shadowed: {stats["shadow_fraction_from_right"]:.1%}',
     f'Changed by inversion: {stats["shadow_orientation_changed_fraction"]:.1%}',
     f'Flat-profile shadow: {stats["flat_surface_shadows"]}',
     f'Speckle contrast: {stats["single_speckle_contrast_std_div_mean"]:.3f}',
     f'16-realization contrast: {stats["averaged_speckle_contrast_std_div_mean"]:.3f}',
    ]
    ax.text(.03,.98,'\n'.join(lines),fontsize=10,va='top',ha='left',family='monospace',transform=ax.transAxes)
    fig.suptitle('CoOpticsGap+ R1 | Three distinct, controlled synthetic phenomena (NOT an instrument)',fontsize=14)
    fig.savefig(p/stats['figure'],dpi=155)
    plt.close(fig)
    return stats


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='.')
    args=parser.parse_args()
    d=run(args.out)
    print('PASS_SYNTHETIC_COOPTICS_R1',json.dumps({k:v for k,v in d.items() if k in ['shadow_fraction_from_left','shadow_fraction_from_right','shadow_orientation_changed_fraction','single_speckle_contrast_std_div_mean','averaged_speckle_contrast_std_div_mean','flat_surface_shadows']},sort_keys=True))
