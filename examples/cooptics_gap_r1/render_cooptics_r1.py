#!/usr/bin/env python3
"""Optional static images for CoOptics R1. Illustrative only, no optical input."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    a = argparse.ArgumentParser()
    a.add_argument('source',type=Path)
    a.add_argument('--out',type=Path,default=Path('.'))
    args=a.parse_args()
    v=json.loads(args.source.read_text(encoding='utf8'))
    if v['schema']!='CoCivium.CoOpticsGap.SyntheticShadowSpeckle.R1':
        raise ValueError('wrong data schema')
    x=np.arange(v['n'])
    h=np.array(v['arrays']['surface_height'])
    left=np.array(v['arrays']['left_ray_illuminated'])
    right=np.array(v['arrays']['right_ray_illuminated'])
    l0=np.array(v['arrays']['detector_0deg_normalized_intensity'])
    l45=np.array(v['arrays']['detector_45deg_normalized_intensity'])
    incoh=np.ones(v['n'])

    fig,ax=plt.subplots(2,1,figsize=(12,6),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    ax[0].plot(x,h,label='Synthetic rough-surface height')
    ax[0].set_ylabel('Surface height (arbitrary)')
    ax[0].set_title('Synthetic rough surface: geometric shadows follow illumination direction')
    ax[0].legend(loc='lower left')
    ax[0].grid(alpha=.25)
    ax[1].imshow(np.stack([left,right]),aspect='auto',interpolation='nearest',origin='upper',cmap='viridis',vmin=0,vmax=1,extent=[0,len(x),1.5,-.5])
    ax[1].set_yticks([0,1],['Light from left','Light from right'])
    ax[1].set_xlabel('Synthetic surface position (NOT detector position)')
    ax[1].set_xticks([0,32,64,96,128,160,192])
    ax[1].set_title('Dark = geometrically shadowed; bright = ray-lit',fontsize=10, pad=6)
    fig.text(.5,.005,'SIMULATION ONLY · simplified ray occlusion · no camera, no laser, no ET signal',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1))
    fig.savefig(args.out/'shadow_geometry_r1.png',dpi=160)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(12,4.8))
    floor=1e-4
    ax.semilogy(x,np.maximum(l0,floor),label='Coherent toy detector, analyzer 0°',linewidth=1.5)
    ax.semilogy(x,np.maximum(l45,floor),label='Same surface, analyzer 45°',linewidth=1.3)
    ax.semilogy(x,incoh,label='Idealized incoherent flat detector baseline',linestyle='--')
    ax.set_xlabel('Far-field detector sample (NOT surface position)')
    ax.set_ylabel('Intensity / mean (log scale)')
    ax.set_title('Synthetic optical interference: dark detector bins need not be surface valleys')
    ax.grid(alpha=.3)
    ax.legend(loc='upper right',fontsize=9)
    fig.text(.5,.005,'SIMULATION ONLY · toy scalar phase + illustrative analyzer mixing, NOT calibrated polarimetry',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1))
    fig.savefig(args.out/'speckle_detector_r1.png',dpi=160)
    plt.close(fig)
    print('WROTE shadow_geometry_r1.png speckle_detector_r1.png')

if __name__=='__main__': main()
