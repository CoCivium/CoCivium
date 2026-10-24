#!/usr/bin/env node
// CoPriMath / CoGibberTru GlyphRail R1: typed, zero-effect semantic preview.
// No OS hooks, network, clipboard, raw keys, provider sessions, persistence or send.
export const SCHEMA = 'CoCivium.CoPriMathGlyphRail.R1';
export const GLYPHS = Object.freeze([
  {id:'focus',mark:'◎',ascii:'FOCUS',label:'Focus or inspect the selected observer'},
  {id:'unknown',mark:'?',ascii:'UNKNOWN',label:'Question or unknown evidence'},
  {id:'next',mark:'>',ascii:'NEXT',label:'Possible next step; numeric comparison only in a defined mathematical context'},
  {id:'prior',mark:'<',ascii:'PRIOR',label:'Previous version or source; numeric comparison only in a defined mathematical context'},
  {id:'relations',mark:'↔',ascii:'RELATIONS',label:'Inspect relation directions; reverse is not automatically causation'},
  {id:'inside',mark:'⊂',ascii:'IN_SCOPE',label:'Inside a declared scope, not authority'},
  {id:'outside',mark:'⊃',ascii:'OUTSIDE',label:'Containing or outside perspective'},
  {id:'not',mark:'¬',ascii:'NOT_HYPOTHESIS',label:'Negation or inverse candidate, not established truth'},
  {id:'alternatives',mark:'±',ascii:'ALTERNATIVES',label:'Alternatives, trade-offs and else branches'},
  {id:'change',mark:'Δ',ascii:'DELTA',label:'Change between pinned source versions'},
  {id:'frontier',mark:'∞',ascii:'FRONTIER',label:'Open-ended logical possibilities, not infinite compute'},
  {id:'pass',mark:'✓',ascii:'SCOPED_PASS',label:'Scoped test passed, not universal adoption'},
  {id:'fail',mark:'✕',ascii:'SCOPED_FAIL',label:'Scoped test failed; preserve the negative result'},
  {id:'held',mark:'⏸',ascii:'HELD',label:'Held, blocked or unqualified evidence'},
  {id:'cycle',mark:'⟳',ascii:'REPLAY',label:'Re-evaluate under bounded budget and a stop rule'},
  {id:'flag',mark:'⚑',ascii:'FLAG',label:'Highlight, bookmark or nominate an issue'},
  {id:'route',mark:'⇢',ascii:'ROUTE_CANDIDATE',label:'Candidate receiver, not a delivered message'},
  {id:'action',mark:'⌘',ascii:'ACTION_MENU',label:'Open explicit action choices, without executing them'},
  {id:'payload',mark:'⧉',ascii:'PAYLOAD',label:'Prepare a copy, buffer or file-backed capsule; not paste or send'},
  {id:'trail',mark:'⌁',ascii:'TRAIL',label:'Inspect history, source lineage and receipt chain'}
]);
export const CONTEXTS = Object.freeze({
  BROWSER_TEXT: ['focus','unknown','prior','relations','not','change','payload','trail'],
  SELECTED_FILE: ['focus','prior','relations','inside','held','action','payload','trail'],
  IMAGE: ['focus','unknown','relations','alternatives','change','payload','trail','flag'],
  CODE: ['focus','prior','relations','not','change','pass','fail','trail'],
  EMAIL_DRAFT: ['focus','prior','relations','not','held','route','payload','trail'],
  COMAP_NODE: ['focus','unknown','relations','outside','not','change','cycle','trail'],
  BLANK_DESKTOP: ['focus','unknown','next','inside','frontier','cycle','action','trail'],
  TASKBAR: ['focus','unknown','next','change','held','cycle','flag','trail'],
  DIAGRAM: ['focus','prior','relations','not','alternatives','change','payload','trail'],
  TERMINAL: ['focus','prior','relations','held','change','pass','fail','trail'],
  XR: ['focus','unknown','relations','inside','outside','alternatives','flag','trail']
});
export const OPERATORS = Object.freeze([
  'ASK','CHALLENGE','INVERT','FALSIFY','COMPARE','PROJECT','REPLAY','HOLD'
]);
export const ADDRESSABLE_COUNT = GLYPHS.length * Object.keys(CONTEXTS).length * OPERATORS.length;
const G = new Map(GLYPHS.map(g=>[g.id,g]));
const ALLOWED_META = new Set(['surface','privacy','gesture','explicit_preview','source_id','relation_type','external_effect_requested','closed_world_verified','evidence_ref']);
const EFFECTS = Object.freeze({
  network:0, send:0, paste:0, clipboard_read:0, key_capture:0,
  os_hooks:0, workers_started:0, persistence:0, device_changes:0
});
function held(state) {
  return {schema:SCHEMA,state,choices:['Cancel'],rail:[],effects:{...EFFECTS},
    authority:'NONE',source_authenticity:'NOT_CHECKED',receiver_ack:null};
}
export function inverseCandidate(type, closedWorld=false, evidenceRef='') {
  if(type==='CAUSES') return {status:'HYPOTHESIS_ONLY',proposal:'Could the causal arrow reverse?',proven:false};
  if(type==='DEPENDS_ON') return {status:'HYPOTHESIS_ONLY',proposal:'Could something substitute for the dependency?',proven:false};
  if(type==='SUPPORTED_BY') return {status:'CHALLENGE_CANDIDATE',proposal:'What would challenge this support?',proven:false};
  if(type==='IN_SCOPE') return {status:'COMPLEMENT_CANDIDATE',proposal:'What is outside the declared scope?',proven:false};
  if(type==='OBSERVED') return {status:'OPEN_WORLD_UNKNOWN',proposal:'Unobserved alternatives could exist',proven:false};
  if(type==='OBSERVED_ABSENT') {
    if(closedWorld===true && typeof evidenceRef==='string' && /^[a-zA-Z0-9_.:/#-]{8,128}$/.test(evidenceRef))
      return {status:'SCOPED_NEGATIVE_CANDIDATE',proposal:'Absent only in the tested domain and time',proven:false};
    return {status:'HOLD_NEGATIVE_EVIDENCE',proposal:'Absence needs qualified closed-world evidence',proven:false};
  }
  if(type==='SYMBOLIC_GD' || type==='ET_STORY')
    return {status:'METAPHOR_OR_HYPOTHESIS',proposal:'Separate story from measurable evidence and null models',proven:false};
  return {status:'UNKNOWN_RELATION',proposal:'Specify a typed relation first',proven:false};
}
export function addressAt(index) {
  if(!Number.isSafeInteger(index)||index<0||index>=ADDRESSABLE_COUNT) throw new RangeError('INDEX_OUTSIDE_LOGICAL_FRONTIER');
  const operator=OPERATORS[index%OPERATORS.length];
  const rem=Math.floor(index/OPERATORS.length);
  const contexts=Object.keys(CONTEXTS);
  const surface=contexts[rem%contexts.length];
  const glyph=GLYPHS[Math.floor(rem/contexts.length)];
  return {address:index,semantic_id:glyph.id,surface,operator,materialized_workers:0,authority:'NONE'};
}
export function rail(meta={}) {
  if(!meta || typeof meta!=='object' || Array.isArray(meta)) return held('HOLD_INVALID_CONTEXT');
  if(Object.keys(meta).some(k=>!ALLOWED_META.has(k))) return held('HOLD_UNDECLARED_OR_SENSITIVE_FIELDS');
  if(meta.privacy!=='PUBLIC' && meta.privacy!=='LOCAL') return held('HOLD_UNKNOWN_OR_PRIVATE_CONTEXT');
  if(!Object.prototype.hasOwnProperty.call(CONTEXTS,meta.surface)) return held('HOLD_UNKNOWN_SURFACE');
  if(meta.external_effect_requested===true) return held('HOLD_EXTERNAL_EFFECT');
  if(meta.gesture!=='EXPLICIT_UI' && meta.gesture!=='SYNTHETIC_TEST')
    return held('HOLD_NATIVE_GESTURE_NOT_VERIFIED');
  if(meta.explicit_preview!==true) return held('HOLD_NO_PREVIEW_REQUEST');
  if(meta.source_id!==undefined &&
     (typeof meta.source_id!=='string' || !/^[a-zA-Z0-9_.:/#-]{3,128}$/.test(meta.source_id)))
    return held('HOLD_INVALID_SOURCE_POINTER');
  const ids=CONTEXTS[meta.surface];
  const projected=ids.map(id=>{
    const g=G.get(id);
    return {semantic_id:g.id,mark:g.mark,label:g.label,text_fallback:g.ascii,spoken_fallback:g.label};
  });
  const relation=inverseCandidate(meta.relation_type,meta.closed_world_verified,meta.evidence_ref);
  return {schema:SCHEMA,state:'PASS_DECLARED_SHADOW_PREVIEW_ONLY',primary:'Preview one useful relation',
    rail:projected,rail_size:projected.length,choices:['Preview','More','Cancel'],dismiss:'ESC',
    source_id:meta.source_id||null,source_authenticity:'NOT_CHECKED',
    relation,logical_address_space:ADDRESSABLE_COUNT,materialized_workers:0,
    effects:{...EFFECTS},authority:'NONE',receiver_ack:null,
    nonclaims:['GLYPH_NE_TRUTH','POSITION_NE_INTENT','MIDDLE_NE_EFFECT',
      'INVERSE_NE_CAUSALITY','SYMBOL_NE_MEASURED_PHYSICS',
      'SOURCE_POINTER_NE_VERIFIED_SOURCE','SHADOW_NE_NATIVE_X2',
      'ADDRESSABLE_NE_ACTIVE_SESSIONS']};
}
