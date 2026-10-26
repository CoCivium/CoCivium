import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { basename } from 'node:path';
import {
  SCHEMA, CLAIM_CEILING, rng32, syntheticSurface, shadowMask,
  scalarFarField, contrast, idealAnalyzerFraction, simulate
} from './cooptics_gap_r1.mjs';

const approx=(a,b,tol=1e-5)=>assert.ok(Math.abs(a-b)<=tol, String(a)+' versus '+String(b));
const sum=x=>x.reduce((a,b)=>a+b,0);
const stable=()=>simulate({seed:20261026,n:64,frames:16});
const row=stable();

test('01 schema pinned',()=>assert.equal(SCHEMA,'CoCivium.CoOpticsGap.SyntheticControls.R1'));
test('02 synthetic ceiling pinned',()=>assert.equal(CLAIM_CEILING,'SYNTHETIC_DEMONSTRATION_ONLY'));
test('03 reproducible source hash',()=>assert.equal(stable().source_sha256,row.source_sha256));
test('04 seed mutation changes surface',()=>assert.notEqual(simulate({seed:22}).source_sha256,row.source_sha256));
test('05 source identity includes n and seed',()=>assert.equal(row.source_id,'synthetic:CoOpticsGap:R1:20261026:64'));
test('06 no physical device or model effects',()=>assert.ok(Object.values(row.effects).every(v=>v===0)));
test('07 receiver never asserted',()=>assert.equal(row.receiver_ack,null));
test('08 no unqualified ET and Gd inference',()=>assert.equal(row.interpretations.observed_ET_or_Gd,'NOT_EVIDENCED'));
test('09 missing physical void not inferred',()=>assert.equal(row.interpretations.physical_void,'NOT_INFERABLE'));
test('10 rough phase toy uses detector angular coordinates',()=>assert.equal(row.far_field.domain,'DETECTOR_ANGULAR_BINS_NOT_SURFACE_GAPS'));
test('11 ray geometry uses sample positions',()=>assert.equal(row.geometry.domain,'SURFACE_SAMPLE_POSITIONS'));
test('12 geometry direction actually changes in fixture',()=>assert.ok(row.geometry.changed_visibility>0));
test('13 shadow fixture known occluded valley',()=>assert.equal(shadowMask([0,3,0,0],'LEFT',0.1)[2],false));
test('14 reverse side reveals known valley',()=>assert.equal(shadowMask([0,3,0,0],'RIGHT',0.1)[2],true));
test('15 flat height produces no occluded positions',()=>assert.ok(shadowMask(Array(32).fill(0),'LEFT',0.1).every(Boolean)));
test('16 flat phase screen has only zero-frequency peak',()=>{
  const v=scalarFarField(Array(32).fill(0));
  approx(v[0],32);assert.ok(v.slice(1).every(x=>x<1e-20));
});
test('17 scalar energy accounting via DFT for rough screen',()=>{
  const phases=syntheticSurface(12,64).map(h=>4*Math.PI*h);
  approx(sum(scalarFarField(phases)),64,1e-6);
});
test('18 smooth reference diffuse fraction zero',()=>approx(row.far_field.smooth_diffuse_fraction,0));
test('19 rough phase produces diffuse energy',()=>assert.ok(row.far_field.rough_diffuse_fraction>0.8));
test('20 coherent single frame granular contrast',()=>assert.ok(row.far_field.rough_single_frame_contrast>0.5));
test('21 synthetic phase-decorrelated average lowers contrast',()=>assert.ok(row.far_field.decorrelated_mean_contrast<row.far_field.rough_single_frame_contrast));
test('22 synthetic mean contrast remains above zero',()=>assert.ok(row.far_field.decorrelated_mean_contrast>0));
test('23 16 independent phase screens produce bounded contrast',()=>assert.ok(row.far_field.decorrelated_mean_contrast<0.45));
test('24 total scalar power preserved across smooth and rough',()=>approx(row.far_field.power_ratio_rough_to_smooth,1));
test('25 dark detector bins are not surface valleys',()=>assert.ok(row.far_field.dark_bins_single>0));
test('26 parallel ideal analyzer',()=>approx(idealAnalyzerFraction(0),1));
test('27 45-degree ideal analyzer',()=>approx(idealAnalyzerFraction(45),0.5));
test('28 crossed ideal analyzer',()=>approx(idealAnalyzerFraction(90),0,1e-15));
test('29 polarization model explicitly excludes rough scattering',()=>assert.ok(row.ideal_analyzer.domain.includes('NOT_ROUGH_SCATTERING')));
test('30 no nearfield simulation claim',()=>assert.equal(row.interpretations.surface_nanogap_field,'NOT_MODELED'));
test('31 phase-surrogate flagged as nonphysical coherence solver',()=>assert.ok(row.controls.decorrelated_phase_average.includes('NOT_REAL_PARTIAL_COHERENCE')));
test('32 deterministic across repeated exact replay',()=>assert.deepEqual(stable(),row));
test('33 rng repeat for same seed',()=>assert.deepEqual([rng32(3)(),rng32(3)()],[rng32(3)(),rng32(3)()]));
test('34 invalid sample count blocked',()=>assert.throws(()=>syntheticSurface(1,1),RangeError));
test('35 invalid RNG seed blocked',()=>assert.throws(()=>rng32(-1),RangeError));
test('36 invalid or unknown direction blocked',()=>assert.throws(()=>shadowMask([0,1,0],'UP',0.1),TypeError));
test('37 zero-angle slope blocked',()=>assert.throws(()=>shadowMask([0,1,0],'LEFT',0),RangeError));
test('38 NaN height profile blocked',()=>assert.throws(()=>shadowMask([0,NaN,0],'RIGHT',0.1),TypeError));
test('39 invalid scalar phase blocked',()=>assert.throws(()=>scalarFarField(Array(20).fill(NaN)),TypeError));
test('40 unphysical intensity blocked',()=>assert.throws(()=>contrast([1,-1]),TypeError));
test('41 zero detected intensity held',()=>assert.throws(()=>contrast([0,0]),RangeError));
test('42 unbounded analyzer angle blocked',()=>assert.throws(()=>idealAnalyzerFraction(1000),RangeError));
test('43 invalid wavelength blocked',()=>assert.throws(()=>simulate({wavelengthInHeightUnits:0}),RangeError));
test('44 invalid frame budget blocked',()=>assert.throws(()=>simulate({frames:0}),RangeError));
test('45 too many sample bins blocked',()=>assert.throws(()=>simulate({n:9999}),RangeError));
test('46 static no-network CLI emits same typed result',()=>{
  const s=execFileSync(process.execPath,[new URL('./cooptics_gap_r1.mjs',import.meta.url).pathname],{encoding:'utf8',timeout:8000});
  const j=JSON.parse(s);assert.equal(j.source_sha256,row.source_sha256);
  assert.equal(j.receiver_ack,null);assert.equal(j.effects.network,0);
});
test('47 unknown CLI argument fails closed',()=>{
  assert.throws(()=>execFileSync(process.execPath,[new URL('./cooptics_gap_r1.mjs',import.meta.url).pathname,'--fetch=https://example.com'],{stdio:'pipe',timeout:8000}));
});
test('48 no ET or drug testing claims',()=>{
  assert.ok(row.nonclaims.includes('SPECKLE_NE_ET_SIGNAL'));
  assert.ok(row.nonclaims.includes('DMT_REPORT_NE_EXTERNAL_SENSOR'));
});
test('49 90 degree analyzer not an indicator of a real dark valley',()=>{
  assert.equal(row.ideal_analyzer.crossed_90deg,0);
  assert.equal(row.interpretations.physical_void,'NOT_INFERABLE');
});
test('50 seed flag parsing bounded and reproducible',()=>{
  const p=new URL('./cooptics_gap_r1.mjs',import.meta.url).pathname;
  const s=execFileSync(process.execPath,[p,'--seed=73'],{encoding:'utf8',timeout:8000});
  assert.equal(JSON.parse(s).source_sha256,simulate({seed:73}).source_sha256);
});
