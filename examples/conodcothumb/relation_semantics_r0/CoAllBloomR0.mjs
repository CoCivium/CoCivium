// CoAllBloom+ R0: bounded OPTIONALITY PROPOSALS over CoMiddle R0, not another truth store.
// Inert pure functions. No browser, mouse, network, files, workers, model or effect access.
import {validateSyntheticAssertion, converseView, negationQuestion} from './CoRelationKernelR0.mjs';

export const SCHEMA = 'CoCivium.CoAllBloom.CompositionalProposal.R0';
export const OPERATORS = Object.freeze([
  'REVISIT_SOURCE', 'CONVERSE', 'NEGATE_QUESTION', 'ELSE',
  'ORTHOGONAL', 'NULL_OPEN_WORLD', 'INBETWEEN',
  'COUNTERFACTUAL', 'TURTLE_CHALLENGE', 'COMPOSE_PROPOSAL'
]);
export const FRAMES = Object.freeze([
  'EMPIRICAL_TEST', 'MATHEMATICAL_MODEL', 'PHYSICAL_MODEL',
  'NONPHYSICAL_HYPOTHESIS', 'SPIRITUAL_SYMBOL', 'MYTHIC_CULTURAL',
  'ET_HYPOTHESIS', 'SOCIAL_INSTITUTIONAL', 'UNKNOWN_ONTOLOGY', 'INBETWEEN_MODEL'
]);
export const TIMES = Object.freeze([
  'SOURCE_TIME', 'HISTORICAL_REPLAY', 'PRESENT_ALTERNATIVE',
  'FUTURE_SCENARIO', 'UNSPECIFIED_TIME'
]);
export const PROJECTIONS = Object.freeze([
  'TEXT', 'COMAP', 'COORB', 'DIAGRAM', 'ACCESSIBLE_TWIN', 'SCHEMA'
]);
export const ADDRESSABLE_COUNT =
  OPERATORS.length * FRAMES.length * TIMES.length * PROJECTIONS.length; // 3000, syntactic only
export const MAX_PREVIEW = 8;
const KEYS = new Set(['assertion','registry','operator','frame','time','projection','right','turtle_depth']);
const effectCeiling = () => ({
  active_workers:0, network_requests:0, account_logins:0,
  messages_sent:0, clipboard_reads:0, device_mutations:0,
  authority:'NONE', receiver_ack:null
});

function oneOf(value, list, field) {
  if(typeof value!=='string'||!list.includes(value))throw new TypeError('HELD_INVALID_'+field);
  return value;
}
export function addressAt(index) {
  if(!Number.isSafeInteger(index)||index<0||index>=ADDRESSABLE_COUNT)
    throw new RangeError('HELD_INDEX_OUTSIDE_DECLARED_NAMESPACE');
  let i=index;
  const projection=PROJECTIONS[i%PROJECTIONS.length];i=Math.floor(i/PROJECTIONS.length);
  const time=TIMES[i%TIMES.length];i=Math.floor(i/TIMES.length);
  const frame=FRAMES[i%FRAMES.length];i=Math.floor(i/FRAMES.length);
  const operator=OPERATORS[i];
  return {address:index,operator,frame,time,projection,active_workers:0,materialized:false};
}
export function propose(input) {
  if(!input||typeof input!=='object'||Array.isArray(input))
    throw new TypeError('HELD_INVALID_REQUEST');
  if(Object.keys(input).some(k=>!KEYS.has(k))) throw new Error('HELD_UNDECLARED_FIELD');
  const {registry,operator,frame,time,projection}=input;
  oneOf(operator,OPERATORS,'OPERATOR');
  oneOf(frame,FRAMES,'FRAME');
  oneOf(time,TIMES,'TIME');
  oneOf(projection,PROJECTIONS,'PROJECTION');
  const assertion=validateSyntheticAssertion(input.assertion,registry);
  if(input.right!==undefined&&operator!=='COMPOSE_PROPOSAL')
    throw new Error('HELD_SECOND_SOURCE_WITHOUT_COMPOSITION');
  if(input.turtle_depth!==undefined&&
      (!Number.isInteger(input.turtle_depth)||input.turtle_depth<0||
       input.turtle_depth>Math.min(2,registry.limits?.max_turtle_depth??0)))
    throw new Error('HELD_TURTLE_BUDGET');
  const sources=[{...assertion}];
  let proposal='Inspect this source-bound relationship without asserting a new fact.';
  let candidate_kind='SOURCE_VIEW_ONLY';
  if(operator==='CONVERSE') {
    const view=converseView(assertion,registry);
    proposal='Inspect the declared converse '+view.relation_id+' of the same source assertion.';
    candidate_kind='CONVERSE_VIEW_NOT_NEW_EVIDENCE';
  } else if(operator==='NEGATE_QUESTION') {
    proposal=negationQuestion(assertion,registry).prompt;
    candidate_kind='QUESTION_NOT_NEGATIVE_FACT';
  } else if(operator==='ELSE') {
    proposal='What materially different explanation fits this scoped source?';
    candidate_kind='ALTERNATIVE_HYPOTHESIS';
  } else if(operator==='ORTHOGONAL') {
    proposal='What independent axis did the present model omit?';
    candidate_kind='OUTSIDE_CURRENT_AXIS';
  } else if(operator==='NULL_OPEN_WORLD') {
    proposal='Which regions were not observed, and how would their absence be tested?';
    candidate_kind='UNKNOWN_NOT_ABSENT';
  } else if(operator==='INBETWEEN') {
    proposal='Does a continuum or transitional state fit better than the named binary?';
    candidate_kind='TRANSITIONAL_MODEL';
  } else if(operator==='COUNTERFACTUAL') {
    proposal='What changes if a named assumption is replaced?';
    candidate_kind='COUNTERFACTUAL_NOT_OBSERVATION';
  } else if(operator==='TURTLE_CHALLENGE') {
    proposal='Which least-cost observation could falsify this branch?';
    candidate_kind='BOUNDED_REVIEW_QUESTION';
  } else if(operator==='COMPOSE_PROPOSAL') {
    if(input.right===undefined)throw new Error('HELD_MISSING_SECOND_SOURCE');
    const right=validateSyntheticAssertion(input.right,registry);
    if(right.scope!==assertion.scope||right.valid_time!==assertion.valid_time||
       right.privacy_class!==assertion.privacy_class)
      throw new Error('HELD_INCOMPATIBLE_SOURCE_SCOPES');
    if(right.source_ref===assertion.source_ref &&
       right.source_version===assertion.source_version)
      throw new Error('HELD_NONINDEPENDENT_DUPLICATE_SOURCE');
    sources.push({...right});
    proposal='Could these two scoped source assertions be meaningfully related? Test rather than assert.';
    candidate_kind='COMPOSITION_QUESTION_NOT_JOINED_FACT';
  }
  const epistemic=frame==='SPIRITUAL_SYMBOL'||frame==='MYTHIC_CULTURAL'?'SYMBOLIC_OR_CULTURAL':
    frame==='ET_HYPOTHESIS'?'ET_HYPOTHESIS_ONLY':
    frame==='NONPHYSICAL_HYPOTHESIS'||frame==='UNKNOWN_ONTOLOGY'?'SPECULATIVE_UNMEASURED':
    'DESIGN_OR_TEST_HYPOTHESIS';
  return {
    schema:SCHEMA,status:'PROPOSAL_ONLY__NOT_A_FACT',operator,frame,time,projection,
    candidate_kind,epistemic,proposal,sources,
    turtle_depth:operator==='TURTLE_CHALLENGE'?(input.turtle_depth??0):0,
    generated_evidence:false,independent_replication:false,truth_promotion:false,
    source_identity_preserved:true,source_verification:'NOT_PERFORMED_BY_BLOOM',
    effect_ceiling:effectCeiling(),
    negative_controls:[
      'CONVERSE_NE_NEGATION','UNKNOWN_NE_ABSENT','INVERSE_NE_PROOF',
      'NULL_NE_NOTHING_EXISTS','SYMBOLIC_GD_NE_MEASUREMENT',
      'ET_STORY_NE_ET_DETECTION','FUTURE_NE_OBSERVED',
      'COMPOSE_NE_CAUSALITY','ADDRESSABLE_NE_MATERIALIZED',
      'SOURCE_VIEW_NE_RECEIVER_ACK'
    ]
  };
}
export function previewAddresses(indices, assertion, registry, right) {
  if(!Array.isArray(indices)||indices.length>MAX_PREVIEW||
     new Set(indices).size!==indices.length)
    throw new Error('HELD_PREVIEW_BUDGET_OR_DUPLICATE');
  return indices.map(index=>{
    const axes=addressAt(index);
    const candidate=propose({...axes,assertion,registry,...(axes.operator==='COMPOSE_PROPOSAL'?{right}:{})});
    return {address:index,...candidate};
  });
}
