/*
 * CoContextAmplifier R0 - PUBLIC metadata-only, deterministic context planner.
 * Does not read source bytes, count actual model tokens, call providers,
 * grant authority, make external effects, or expand a model context window.
 */
export const SCHEMA = 'CoAll.CoContextAmplifier.ShadowR0';
const ALLOWED_KINDS = new Set(['SUPPORT','COUNTER','OPERATIVE','PRIOR']);
const ALLOWED_FRESHNESS = new Set(['CURRENT','STALE','UNKNOWN']);
const SHA256 = /^[0-9a-f]{64}$/i;
const ID = /^[A-Za-z0-9_.:-]{1,128}$/;
const MAX_INPUTS = 256;

function base(workId, budget, headroom) {
  return {
    schema: SCHEMA, work_id: workId || null,
    state: 'PROPOSAL_ONLY', budget_units: budget, headroom_units: headroom,
    available_units: budget - headroom,
    selected: [], omitted: [], held_public: [],
    counterevidence_omitted: false,
    cost_units_used: 0, candidate_total: 0,
    effects: {network:0,read_source_bytes:0,send:0,execute:0,write:0},
    authority: 'NONE', receiver_ack: false,
    tokenizer: 'NOT_MEASURED_SUPPLIED_SYNTHETIC_UNITS',
    materialized_source_bytes: 0,
    nonclaims: ['BUDGET_UNITS_NE_MODEL_TOKENS','POINTER_NE_SOURCE_BYTES',
      'PLAN_NE_EXECUTION','SELECTED_NE_TRUE','SOURCE_HASH_NE_SEMANTIC_VERIFICATION',
      'SUMMARY_NE_LOSSLESS_SOURCE','PROPOSAL_NE_RECEIVER_ACK',
      'LOGICAL_CAPACITY_NE_UNLIMITED_COMPUTE']
  };
}
function idSafe(s) {return typeof s==='string' && ID.test(s);}
function better(a,b) {
  return Number(b.required)-Number(a.required) || b.utility-a.utility ||
    a.cost_units-b.cost_units || a.id.localeCompare(b.id);
}
function fail(header,reason) {header.state=reason;return header;}

export function planContext(req) {
  if (!req || typeof req !== 'object' || Array.isArray(req))
    return fail(base(null,0,0),'HOLD_INVALID_REQUEST');
  const {work_id,budget_units,headroom_units,sources} = req;
  if (!idSafe(work_id) || !Number.isSafeInteger(budget_units) ||
      budget_units < 1 || !Number.isSafeInteger(headroom_units) ||
      headroom_units < 0 || headroom_units >= budget_units ||
      !Array.isArray(sources) || sources.length > MAX_INPUTS)
    return fail(base(null,0,0),'HOLD_INVALID_REQUEST');
  const res=base(work_id,budget_units,headroom_units);
  const valid=[], seenIds=new Set();
  let requiredUnavailable=false;
  let collidingIds=false;
  for (const src of sources) {
    if (!src || typeof src !== 'object' || Array.isArray(src)) {
      res.held_public.push({reason:'INVALID_SOURCE'});
      continue;
    }
    // PUBLIC-only canary; do not reveal private item identities or counts.
    if (src.privacy !== 'PUBLIC') {
      if (src.required===true) requiredUnavailable=true;
      continue;
    }
    const id = idSafe(src.id) ? src.id : null;
    if (!id || seenIds.has(id)) {
      res.held_public.push({reason:'INVALID_OR_COLLIDING_ID'});
      if (id && seenIds.has(id)) collidingIds=true;
      if (src.required===true) requiredUnavailable=true;
      continue;
    }
    seenIds.add(id);
    const good = typeof src.source_ref==='string' && src.source_ref.length>0 &&
      src.source_ref.length<=400 && SHA256.test(src.sha256) &&
      Number.isSafeInteger(src.cost_units) && src.cost_units>0 &&
      Number.isSafeInteger(src.utility) && src.utility>=0 && src.utility<=100 &&
      ALLOWED_KINDS.has(src.kind) && ALLOWED_FRESHNESS.has(src.freshness) &&
      (src.required===true || src.required===false || src.required===undefined);
    if (!good) {
      res.held_public.push({id,reason:'INVALID_PUBLIC_METADATA'});
      if (src.required===true) requiredUnavailable=true;
      continue;
    }
    if (src.freshness !== 'CURRENT') {
      res.held_public.push({id,reason:src.freshness==='STALE'?'STALE':'FRESHNESS_UNPROVEN'});
      if (src.required===true) requiredUnavailable=true;
      continue;
    }
    valid.push({id,source_ref:src.source_ref,sha256:src.sha256.toLowerCase(),
      cost_units:src.cost_units,utility:src.utility,kind:src.kind,
      required:src.required===true});
  }
  if (collidingIds) return fail(res,'HOLD_COLLIDING_IDENTITIES');
  if (requiredUnavailable) return fail(res,'HOLD_REQUIRED_SOURCE_UNAVAILABLE');
  // Identical bytes in different argumentative roles remain distinct claims.
  const groups = new Map();
  for (const s of valid) {
    const key=s.sha256+'|'+s.kind;
    if (!groups.has(key)) groups.set(key,[]);
    groups.get(key).push(s);
  }
  const canonical=[];
  for (const [key,items] of groups) {
    items.sort(better);
    canonical.push({...items[0],required:items.some(v=>v.required),
      aliases:items.slice(1).map(v=>v.id).sort()});
  }
  res.candidate_total=canonical.length;
  const required=canonical.filter(x=>x.required).sort(better);
  const requiredCost=required.reduce((sum,x)=>sum+x.cost_units,0);
  if (requiredCost>res.available_units)
    return fail(res,'HOLD_REQUIRED_EXCEEDS_BUDGET');
  const selected=[], selectedIds=new Set();
  let used=0;
  const admit=(x)=>{
    selected.push({id:x.id,source_ref:x.source_ref,sha256:x.sha256,
      kind:x.kind,cost_units:x.cost_units,aliases:x.aliases,required:x.required});
    used+=x.cost_units;selectedIds.add(x.id);
  };
  required.forEach(admit);
  const optional=canonical.filter(x=>!x.required).sort(better);
  // Reserve one eligible opposing-evidence pointer where capacity allows.
  if (!selected.some(x=>x.kind==='COUNTER')) {
    const counter=optional.find(x=>x.kind==='COUNTER' && x.cost_units<=res.available_units-used);
    if (counter) admit(counter);
  }
  for (const x of optional) {
    if (selectedIds.has(x.id)) continue;
    if (used+x.cost_units<=res.available_units) admit(x);
  }
  res.selected=selected;
  res.cost_units_used=used;
  res.omitted=canonical.filter(x=>!selectedIds.has(x.id)).map(x=>({id:x.id,reason:'BUDGET_EXCLUDED'}));
  res.counterevidence_omitted=canonical.some(x=>x.kind==='COUNTER') &&
    !selected.some(x=>x.kind==='COUNTER');
  if (res.counterevidence_omitted || res.omitted.length || res.held_public.length)
    res.state='PARTIAL_PROPOSAL_ONLY';
  return res;
}
