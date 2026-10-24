// CoNull+ / G_dRes+ R1 candidate. Pure, local, provider-neutral, no effects.
// G_dRes here means evidence-qualified discovery discrepancy, NOT a physical/spiritual field.
export const NULL_STATES = Object.freeze([
  'UNKNOWN','NOT_OBSERVED','OBSERVED_ABSENT','EXPLICIT_DISCONNECTED',
  'INACCESSIBLE','INTENTIONALLY_PRIVATE','INCOMPATIBLE','EXPIRED',
  'REJECTED','NOT_MATERIALIZED','PREDICTED_ONLY','NOT_APPLICABLE'
]);
export const PROOF_BOUND_STATES = Object.freeze([
  'OBSERVED_ABSENT','EXPLICIT_DISCONNECTED','INCOMPATIBLE','EXPIRED','REJECTED'
]);
const isPlain = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const finite = x => typeof x === 'number' && Number.isFinite(x);
const setOf = a => new Set(a);
const exactArray = (a, key) => {
  if (!Array.isArray(a) || a.some(x => !isPlain(x) || typeof x[key] !== 'string' || !x[key])) throw Error('BAD_'+key.toUpperCase()+'_LIST');
  if (new Set(a.map(x => x[key])).size !== a.length) throw Error('DUPLICATE_'+key.toUpperCase());
};
const goodTime = t => typeof t === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(t) && Number.isFinite(Date.parse(t));

export function qualifyNull(r) {
  if (!isPlain(r) || typeof r.id !== 'string' || !r.id || !NULL_STATES.includes(r.null_state)) throw Error('INVALID_NULL_RECORD');
  if (!['PUBLIC','PRIVATE','RESTRICTED','UNKNOWN'].includes(r.privacy)) throw Error('PRIVACY_UNQUALIFIED');
  if (r.authority !== 'NONE') throw Error('NULL_NE_AUTHORITY');
  if (!['COMPLETE','PARTIAL','UNKNOWN'].includes(r.coverage)) throw Error('INVALID_COVERAGE');
  if (!Array.isArray(r.evidence_refs) || r.evidence_refs.some(x => typeof x !== 'string' || !x)) throw Error('INVALID_EVIDENCE');
  if (PROOF_BOUND_STATES.includes(r.null_state) && !r.evidence_refs.length) throw Error('NEGATIVE_CLAIM_UNSOURCED');
  if (r.null_state === 'OBSERVED_ABSENT' && (r.coverage !== 'COMPLETE' || !goodTime(r.observed_at) || typeof r.closed_world_scope_ref !== 'string' || !r.closed_world_scope_ref)) throw Error('CLOSED_WORLD_EVIDENCE_REQUIRED');
  if (r.null_state === 'PREDICTED_ONLY' && (typeof r.forecast_ref !== 'string' || !r.forecast_ref || !goodTime(r.horizon_end))) throw Error('FORECAST_PROVENANCE_REQUIRED');
  if (r.null_state === 'INTENTIONALLY_PRIVATE' && r.privacy === 'PUBLIC') throw Error('PRIVATE_CLASS_MISMATCH');
  return Object.freeze({...r, epistemic: r.null_state === 'PREDICTED_ONLY' ? 'PREDICTED' : 'NON_RELATION', effect_authority:'NONE'});
}

export function publicNullProjection(records, mode = 'MAP') {
  if (!['MAP','ORB','TEXT','AMBIENT'].includes(mode)) throw Error('BAD_VIEW');
  if (!Array.isArray(records)) throw Error('BAD_RECORDS');
  const safe=[];
  for (const raw of records) {
    const n=qualifyNull(raw);
    // Even a private count or opaque identity could leak existence. Drop entirely.
    if (n.privacy !== 'PUBLIC' || n.null_state === 'INTENTIONALLY_PRIVATE') continue;
    // Default public projections are metadata-minimal, even for misclassified PUBLIC objects.
    // Exact source refs must go through a separate authenticated evidence resolver.
    safe.push(Object.freeze({id:'null-'+(safe.length+1),null_state:n.null_state,epistemic:n.epistemic,
      evidence_declared:n.evidence_refs.length>0,
      authority:'NONE',render_as_live_edge:false}));
  }
  return Object.freeze({schema:'CoNull.PublicProjection.R1',mode,
    non_edges:mode === 'AMBIENT' ? [] : safe,
    ambient_message:mode === 'AMBIENT' ? 'Known gaps remain; open evidence view' : null,
    rendered_live_edges:0,receiver_ack:'UNPROVEN',external_effects:0});
}

// Numeric residual: expectation and observation MUST be comparable, with declared units/time.
// The tolerance is a declared decision threshold, not a calibrated standard deviation.
export function numericResidual(x) {
  if (!isPlain(x) || !['PUBLIC','PRIVATE','RESTRICTED'].includes(x.privacy)) throw Error('INVALID_RESIDUAL');
  if (x.privacy !== 'PUBLIC') return Object.freeze({state:'WITHHELD',discovery_eligible:false,external_effects:0});
  if (typeof x.expectation_ref !== 'string' || !x.expectation_ref || !goodTime(x.valid_at)) throw Error('EXPECTATION_LINEAGE_REQUIRED');
  if (!finite(x.expected) || typeof x.unit !== 'string' || !x.unit) throw Error('EXPECTED_VALUE_INVALID');
  if (x.observed === null || x.observed === undefined) return Object.freeze({state:'NOT_OBSERVED',discovery_eligible:false,external_effects:0});
  if (!finite(x.observed) || !finite(x.tolerance) || x.tolerance <= 0) throw Error('INVALID_OBSERVATION_OR_TOLERANCE');
  if (x.observed_unit !== x.unit) return Object.freeze({state:'INCOMPATIBLE_UNITS',discovery_eligible:false,external_effects:0});
  if (!goodTime(x.observed_at) || !goodTime(x.observation_valid_at) || x.observation_valid_at !== x.valid_at || typeof x.observation_ref !== 'string' || !x.observation_ref) return Object.freeze({state:'TIME_OR_SOURCE_UNQUALIFIED',discovery_eligible:false,external_effects:0});
  const delta=x.observed-x.expected;
  const normalized=Math.abs(delta)/x.tolerance;
  const matched=Math.abs(delta)<=x.tolerance;
  const independent=x.expectation_ref!==x.observation_ref && x.independence_evidence===true;
  return Object.freeze({state:matched?'WITHIN_TOLERANCE':'MISMATCH',
    unit:x.unit,delta,normalized_to_tolerance:normalized,
    independently_sourced:independent,
    discovery_eligible:!matched && independent,
    epistemic:'MEASURED_RELATIVE_TO_DECLARED_EXPECTATION',effect_authority:'NONE',external_effects:0});
}

// Expected/observed edge sets. Partial coverage must NOT become evidence of nonexistence.
// Callers must bind a valid observation source; simulated PR215 graphs cannot masquerade as observations.
export function edgeResidual(x) {
  if (!isPlain(x) || x.privacy !== 'PUBLIC') return Object.freeze({state:'WITHHELD_OR_INVALID',discovery_eligible:false});
  exactArray(x.expected, 'id'); exactArray(x.observed, 'id');
  if (!['COMPLETE','PARTIAL'].includes(x.coverage)) throw Error('COVERAGE_REQUIRED');
  if (!x.observation_ref || !x.expectation_ref || typeof x.observation_ref !== 'string' || typeof x.expectation_ref !== 'string') throw Error('EVIDENCE_REFS_REQUIRED');
  if (!goodTime(x.observed_at) || !goodTime(x.expected_at) || !goodTime(x.target_valid_at) || !goodTime(x.observation_valid_at)) throw Error('TIME_REQUIRED');
  if (x.target_valid_at !== x.observation_valid_at) return Object.freeze({state:'TIME_OR_SOURCE_UNQUALIFIED',discovery_eligible:false});
  if (x.coverage==='COMPLETE' && !(typeof x.coverage_evidence_ref==='string' && x.coverage_evidence_ref)) throw Error('COVERAGE_EVIDENCE_REQUIRED');
  if (x.observed.some(e => e.epistemic !== 'OBSERVED')) throw Error('SIMULATED_NE_OBSERVED');
  if (x.expected.some(e => e.epistemic !== 'PREDICTED')) throw Error('EXPECTED_MUST_BE_PREDICTED');
  const exp=setOf(x.expected.map(e=>e.id)),obs=setOf(x.observed.map(e=>e.id));
  const found=[...obs].filter(id=>exp.has(id)).sort();
  const unexpected=[...obs].filter(id=>!exp.has(id)).sort();
  const missing=[...exp].filter(id=>!obs.has(id)).sort();
  return Object.freeze({schema:'G_dRes.EdgeResidual.R1',state:'COMPARISON_ONLY',
    confirmed:found,unexpected,disconfirmed:x.coverage==='COMPLETE'?missing:[],
    unresolved_predictions:x.coverage==='PARTIAL'?missing:[],
    absence_claim_permitted:x.coverage==='COMPLETE',
    independently_sourced:x.expectation_ref!==x.observation_ref&&x.independence_evidence===true,
    discovery_eligible:unexpected.length>0 && x.independence_evidence===true && x.expectation_ref!==x.observation_ref,
    effect_authority:'NONE',external_effects:0});
}

// CoNullSeat is a virtual review option. No worker, provider call, or live session is spawned.
export function electNullSeat(candidates,budget=1) {
  if (!Array.isArray(candidates) || !Number.isInteger(budget) || budget<0 || budget>10) throw Error('INVALID_BUDGET');
  const admissible=[];
  for (const x of candidates) {
    if (!isPlain(x) || typeof x.id!=='string'||!x.id) throw Error('INVALID_CANDIDATE');
    if (x.privacy!=='PUBLIC'||x.authority!=='READ_ONLY'||x.testable!==true||x.recovery!==true) continue;
    if (!finite(x.expected_info_gain)||!finite(x.estimated_cost)||x.expected_info_gain<0||x.expected_info_gain>1||x.estimated_cost<0||x.estimated_cost>1) continue;
    const advantage=x.expected_info_gain-x.estimated_cost;
    if (advantage<=0) continue;
    admissible.push({id:x.id,score:advantage,execution:'LOGICAL_ONLY'});
  }
  admissible.sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));
  return Object.freeze({selected:admissible.slice(0,budget),materialized_workers:0,
    effect_authority:'NONE',external_effects:0,stopping_rule:'BUDGET_OR_NO_MARGINAL_GAIN'});
}