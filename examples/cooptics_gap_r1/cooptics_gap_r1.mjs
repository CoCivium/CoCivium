// CoOpticsGap R1: dependency-free, deterministic synthetic geometry/phase controls.
// NOT a Maxwell solver, measured photons, near-field model, ET/G_d detector or laser driver.
import { createHash } from 'node:crypto';

const PI2 = Math.PI * 2;
export const SCHEMA = 'CoCivium.CoOpticsGap.SyntheticControls.R1';
export const CLAIM_CEILING = 'SYNTHETIC_DEMONSTRATION_ONLY';

function assertInt(value, lower, upper, name) {
  if (!Number.isSafeInteger(value) || value < lower || value > upper) {
    throw new RangeError(name+'_OUT_OF_RANGE');
  }
}

export function rng32(seed) {
  assertInt(seed, 0, 4294967295, 'SEED');
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Heights measured in arbitrary units; sample and illumination geometry are synthetic.
export function syntheticSurface(seed=20261026, n=64) {
  assertInt(n, 16, 256, 'SAMPLE_COUNT');
  const rnd = rng32(seed);
  return Array.from({length:n}, (_, i) =>
    0.75*Math.sin(PI2*i/17) + 0.35*Math.sin(PI2*i/5 + 0.7) + 0.8*(rnd()-0.5));
}

// Simple 2D geometric ray-shadow check on a 1D height profile (NOT wave optics).
export function shadowMask(heights, side, risePerCell) {
  if (!Array.isArray(heights) || heights.length < 2 ||
      heights.some(v => !Number.isFinite(v))) throw new TypeError('INVALID_HEIGHT_PROFILE');
  if (side !== 'LEFT' && side !== 'RIGHT') throw new TypeError('UNQUALIFIED_LIGHT_DIRECTION');
  if (!Number.isFinite(risePerCell) || risePerCell <= 0) throw new RangeError('INVALID_LIGHT_ANGLE');
  return heights.map((height, i) => {
    const first = side === 'LEFT' ? 0 : i + 1;
    const end = side === 'LEFT' ? i : heights.length;
    for (let j = first; j < end; j++) {
      const distance = Math.abs(i-j);
      if (heights[j] > height + distance*risePerCell + 1e-10) return false;
    }
    return true;
  });
}

// Fraunhofer-style 1D scalar phasor toy. The index k denotes a DETECTOR
// angular bin, not a physical valley on the sample. No vector polarization
// scattering, evanescent fields, or near-field nanogaps are simulated.
export function scalarFarField(phases) {
  if (!Array.isArray(phases) || phases.length < 16 || phases.length > 256 ||
      phases.some(v => !Number.isFinite(v))) throw new TypeError('INVALID_PHASE_SCREEN');
  const n=phases.length;
  const intensity=[];
  for (let k=0;k<n;k++) {
    let real=0,imag=0;
    for (let j=0;j<n;j++) {
      const phase=phases[j]-PI2*k*j/n;
      real+=Math.cos(phase);
      imag+=Math.sin(phase);
    }
    intensity.push((real*real+imag*imag)/n);
  }
  return intensity;
}

export function contrast(values) {
  if (!Array.isArray(values) || values.length < 2 ||
      values.some(v => !Number.isFinite(v) || v < 0)) throw new TypeError('INVALID_INTENSITY');
  const mean=values.reduce((a,b)=>a+b,0)/values.length;
  if (mean <= 0) throw new RangeError('NO_DETECTED_POWER');
  const variance=values.reduce((a,v)=>a+(v-mean)**2,0)/values.length;
  return Math.sqrt(variance)/mean;
}

// Ideal POLARIZER REFERENCE (Malus' law), NOT a rough-scattering solver.
export function idealAnalyzerFraction(degrees) {
  if (!Number.isFinite(degrees) || Math.abs(degrees)>360) throw new RangeError('INVALID_ANALYZER_ANGLE');
  return Math.cos(degrees*Math.PI/180)**2;
}

const sum = values => values.reduce((a,b)=>a+b,0);
const round = value => Math.round(value*1e6)/1e6;
const hash = value => createHash('sha256').update(value).digest('hex');
export function simulate({seed=20261026,n=64,frames=16,risePerCell=0.18,wavelengthInHeightUnits=1}={}) {
  assertInt(n,16,128,'SAMPLE_COUNT');
  assertInt(frames,2,32,'FRAME_COUNT');
  if (!Number.isFinite(wavelengthInHeightUnits) || wavelengthInHeightUnits<=0)
    throw new RangeError('INVALID_WAVELENGTH');
  if (!Number.isFinite(risePerCell) || risePerCell<=0) throw new RangeError('INVALID_LIGHT_ANGLE');
  const h=syntheticSurface(seed,n);
  const left=shadowMask(h,'LEFT',risePerCell);
  const right=shadowMask(h,'RIGHT',risePerCell);
  const smooth=scalarFarField(Array(n).fill(0));
  const phases=h.map(x => 4*Math.PI*x/wavelengthInHeightUnits);
  const rough=scalarFarField(phases);
  // Randomly decorrelated added phases, with unchanged synthetic surface heights.
  // This is a PHENOMENOLOGICAL independent-path surrogate, not a full
  // partial-coherence propagation calculation for a real fixed surface.
  const rnd=rng32((seed ^ 0xC0FEBABE) >>> 0);
  const avg=Array(n).fill(0);
  const decorrelatedFrames=[];
  for(let frame=0;frame<frames;frame++) {
    const phi=phases.map(p => p+PI2*rnd());
    const im=scalarFarField(phi);
    decorrelatedFrames.push(im);
    for(let k=0;k<n;k++) avg[k]+=im[k]/frames;
  }
  const surfaceId='synthetic:CoOpticsGap:R1:'+seed+':'+n;
  const output={
    schema:SCHEMA,claim_ceiling:CLAIM_CEILING,source_id:surfaceId,
    source_sha256:hash(h.map(v=>v.toFixed(10)).join(',')),
    source_type:'GENERATED_HEIGHT_PROFILE_AND_IDEALIZED_SCALAR_PHASE',
    seed,n,frames,rise_per_cell:risePerCell,wavelength_in_synthetic_height_units:wavelengthInHeightUnits,
    geometry:{
      domain:'SURFACE_SAMPLE_POSITIONS',
      dark_left:left.filter(v=>!v).length,dark_right:right.filter(v=>!v).length,
      changed_visibility:left.filter((v,i)=>v!==right[i]).length,
      mechanism:'1D_RAY_OCCLUSION_TOY'
    },
    far_field:{
      domain:'DETECTOR_ANGULAR_BINS_NOT_SURFACE_GAPS',
      smooth_diffuse_fraction:round(sum(smooth.slice(1))/sum(smooth)),
      rough_diffuse_fraction:round(sum(rough.slice(1))/sum(rough)),
      rough_single_frame_contrast:round(contrast(rough)),
      decorrelated_mean_contrast:round(contrast(avg)),
      dark_bins_single:rough.filter(v=>v<0.1).length,
      dark_bins_avg:avg.filter(v=>v<0.1).length,
      power_ratio_rough_to_smooth:round(sum(rough)/sum(smooth)),
      mechanism:'ONE_DIMENSIONAL_SCALAR_COHERENT_PHASE_SUM'
    },
    ideal_analyzer:{
      domain:'IDEAL_VECTOR_PROJECTION_ONLY_NOT_ROUGH_SCATTERING',
      parallel_0deg:round(idealAnalyzerFraction(0)),
      oblique_45deg:round(idealAnalyzerFraction(45)),
      crossed_90deg:round(idealAnalyzerFraction(90))
    },
    controls:{
      flat_surface:'SYNTHETIC_DIFFRACTION_REFERENCE',
      reversed_light_direction:'SYNTHETIC_GEOMETRY_INVERSION',
      decorrelated_phase_average:'PHENOMENOLOGICAL_SURROGATE_NOT_REAL_PARTIAL_COHERENCE',
      rotated_analyzer:'MALUS_LAW_IDEAL_REFERENCE_ONLY'
    },
    interpretations:{
      low_pixel:'LOW_SIMULATED_DETECTOR_INTENSITY_WITH_DEFINED_THRESHOLD',
      physical_void:'NOT_INFERABLE',
      surface_nanogap_field:'NOT_MODELED',
      vector_polarimetric_roughness:'NOT_MODELED',
      observed_ET_or_Gd:'NOT_EVIDENCED',
      drug_assisted_measurement:'NOT_A_SENSOR'
    },
    effects:{network:0,laser:0,camera:0,clipboard:0,models:0,workers_spawned:0,public_messages:0},
    receiver_ack:null,
    nonclaims:['DARK_DETECTOR_BIN_NE_SURFACE_VOID','SPECKLE_NE_ET_SIGNAL',
      'POLARIZER_REFERENCE_NE_MATERIAL_CHARACTERIZATION','SIMULATION_NE_CALIBRATED_OPTICS',
      'DMT_REPORT_NE_EXTERNAL_SENSOR','G_D_SYMBOL_NE_OBSERVED_AGENT']
  };
  if (output.geometry.changed_visibility===0) throw new Error('CONTROL_HAS_NO_GEOMETRY_DISCRIMINATION');
  return output;
}

if (process.argv[1] && import.meta.url === new URL('file://'+process.argv[1]).href) {
  if (process.argv.length > 3) throw new Error('NO_ARBITRARY_IO_OR_EFFECT_FLAGS');
  let options={};
  if (process.argv[2]) {
    if (!/^--seed=\d{1,10}$/.test(process.argv[2])) throw new Error('ONLY_SEED_FLAG_SUPPORTED');
    options.seed=Number(process.argv[2].slice(7));
  }
  console.log(JSON.stringify(simulate(options),null,2));
}
