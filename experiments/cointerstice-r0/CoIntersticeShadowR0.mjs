#!/usr/bin/env node
// CoInterstice Shadow R0: explicit, non-persistent synthetic/input metadata classifier.
// NO OS HOOKS, KEY CONTENT, TIMING PROFILE RETENTION, NETWORK, FILE OR DEVICE EFFECTS.
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const SCHEMA = 'CoCivium.CoIntersticeShadow.R0';
export const GLYPHS = Object.freeze({
  focus: Object.freeze({symbol: '\u25ce', label: 'Focus or selected observer'}),
  candidate: Object.freeze({symbol: '\u25c7', label: 'Proposed action, not executed'}),
  inverse: Object.freeze({symbol: '\u2194', label: 'Explore direction or inverse, not equivalent proof'}),
  change: Object.freeze({symbol: '\u0394', label: 'Source-bound change'}),
  scope: Object.freeze({symbol: '\u2282', label: 'Inside declared scope, without inherited authority'}),
  pass: Object.freeze({symbol: '\u2713', label: 'Scoped test passed'}),
  fail: Object.freeze({symbol: '\u2715', label: 'Scoped test failed'}),
  unknown: Object.freeze({symbol: '?', label: 'Unknown or held, not zero'}),
  cycle: Object.freeze({symbol: '\u27f3', label: 'Re-evaluate within budget, not unlimited processing'})
});
const SAFE_CONTEXTS = new Set(['LOCAL_EDITOR', 'LOCAL_CANARY']);
const ALLOWED_MOTION = new Set(['INPUT_GAP', 'POINTER_DWELL', 'FOCUS_CHANGE', 'BUTTON_PREVIEW']);
const FORBIDDEN_INPUT_NAMES = ['raw_key','key','text','clipboard','password','email','screen_capture', 'scan_code', 'device_fingerprint'];

function decision(status,primary='No action',extra={}) {
  return {
    schema:SCHEMA,status,primary,
    actions:['Preview','Cancel'], authority:'NONE',
    effect_counts:{os_hooks:0,key_capture:0,clipboard_read:0,network:0,send:0,input_injection:0,workers_started:0,persistent_events:0},
    provenance:'EXPLICIT_SYNTHETIC_OR_LOCAL_EDITOR_METADATA_ONLY',
    nonclaims:['INTERSTICE_NE_INTENT','SILENCE_NE_REJECTION','POINTER_NE_AUTHORITY',
      'SYNTHETIC_NE_NATIVE_X2','GLYPH_NE_SOURCE','INVERSE_NE_CAUSALITY','OPEN_WORLD_NE_ABSENT'],
    ...extra
  };
}
export function coarseInterval(milliseconds) {
  if (!Number.isSafeInteger(milliseconds)||milliseconds<0||milliseconds>60_000)
    return 'HELD_INVALID_INTERVAL';
  if (milliseconds<400) return 'BRIEF';
  if (milliseconds<1800) return 'MODERATE';
  if (milliseconds<4500) return 'LONG';
  return 'EXTENDED';
}
export function inverseCandidate(input={}) {
  const kind = input?.relation_type;
  if (kind==='CAUSES') return {state:'HYPOTHESIS_ONLY',label:'Could the direction be reversed?',proven:false};
  if (kind==='INSIDE_SCOPE') return {state:'COMPLEMENT_CANDIDATE',label:'What is outside this declared scope?',proven:false};
  if (kind==='OBSERVED') return {state:'OPEN_WORLD_UNKNOWN',label:'Unobserved alternatives may exist',proven:false};
  if (kind==='OBSERVED_ABSENT') {
    const qualifies=input.closed_world_verified===true &&
      typeof input.evidence_ref==='string' && /^[A-Za-z0-9:_./-]{8,180}$/.test(input.evidence_ref);
    return qualifies?{state:'SCOPED_ABSENCE_CANDIDATE',label:'Absent inside independently bounded domain',proven:false,evidence_ref:input.evidence_ref}
      :{state:'HOLD_NO_CLOSED_WORLD_PROOF',label:'Absence not established',proven:false};
  }
  return {state:'UNKNOWN_RELATION',label:'Declare typed relation first',proven:false};
}
export function preview(meta={}) {
  if (!meta || typeof meta!=='object'||Array.isArray(meta)) return decision('HELD_INVALID_META');
  // Unknown or extra event fields fail closed, so raw keys and text cannot be smuggled into a loggable response.
  const allowed=new Set(['opt_in','scope','event_type','interval_ms','explicit_preview','relation','pointer_zone']);
  if(Object.keys(meta).some(k=>!allowed.has(k)||FORBIDDEN_INPUT_NAMES.includes(k))) return decision('HOLD_UNRECOGNIZED_OR_RAW_FIELDS');
  if(meta.opt_in!==true) return decision('HOLD_NO_OPT_IN');
  if(!SAFE_CONTEXTS.has(meta.scope)) return decision('HOLD_UNKNOWN_OR_SENSITIVE_CONTEXT');
  if(!ALLOWED_MOTION.has(meta.event_type)) return decision('HOLD_UNSUPPORTED_EVENT');
  if(meta.pointer_zone!==undefined && !['LEFT','CENTER','RIGHT','NONE'].includes(meta.pointer_zone))
    return decision('HOLD_UNSCOPED_POSITION');
  if(meta.interval_ms!==undefined && coarseInterval(meta.interval_ms)==='HELD_INVALID_INTERVAL')
    return decision('HOLD_INVALID_INTERVAL');
  const interval=meta.interval_ms===undefined?'NOT_MEASURED':coarseInterval(meta.interval_ms);
  // No raw time, raw coordinates, app title or identity in result; input intervals are immediately coarse-bucketed.
  const relation=meta.relation===undefined ? undefined : inverseCandidate(meta.relation);
  if(meta.explicit_preview!==true) return decision('PASS_NO_ACTION','Context observed; no preview requested',
    {coarse_gap:interval,relation,selected_zone:meta.pointer_zone||'NONE'});
  return decision('PASS_SHADOW_PREVIEW_ONLY','Inspect one safe relation',
    {coarse_gap:interval,relation,selected_zone:meta.pointer_zone||'NONE',glyph:GLYPHS.candidate});
}
if (process.argv[1] && fileURLToPath(import.meta.url)===fileURLToPath(pathToFileURL(path.resolve(process.argv[1])).href)) {
  // No automatic listener or scheduling; CLI provides only synthetic example.
  if (process.argv.includes('--demo')) console.log(JSON.stringify(preview({opt_in:true,scope:'LOCAL_CANARY',event_type:'INPUT_GAP',interval_ms:2300,explicit_preview:true,relation:{relation_type:'OBSERVED'}}),null,2));
}
