import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {
  SCHEMA, OPERATORS, FRAMES, TIMES, PROJECTIONS,
  ADDRESSABLE_COUNT, MAX_PREVIEW, addressAt, propose, previewAddresses
} from './CoAllBloomR0.mjs';

const registry = JSON.parse(readFileSync(new URL('./registry.json', import.meta.url), 'utf8'));
const sample = registry.sample_assertion;
const base = {assertion:sample, registry, operator:'ELSE',
  frame:'PHYSICAL_MODEL', time:'PRESENT_ALTERNATIVE', projection:'COMAP'};
const go = (extra={}) => propose({...base,...extra});
const other = {...sample,source_ref:'synthetic://codemo/002',object_id:'OtherSyntheticObject'};
const zero = (p) => {
  assert.equal(p.status,'PROPOSAL_ONLY__NOT_A_FACT');
  assert.equal(p.generated_evidence,false);
  assert.equal(p.independent_replication,false);
  assert.equal(p.truth_promotion,false);
  assert.equal(p.source_verification,'NOT_PERFORMED_BY_BLOOM');
  assert.equal(p.effect_ceiling.active_workers,0);
  assert.equal(p.effect_ceiling.network_requests,0);
  assert.equal(p.effect_ceiling.account_logins,0);
  assert.equal(p.effect_ceiling.messages_sent,0);
  assert.equal(p.effect_ceiling.clipboard_reads,0);
  assert.equal(p.effect_ceiling.device_mutations,0);
  assert.equal(p.effect_ceiling.authority,'NONE');
  assert.equal(p.effect_ceiling.receiver_ack,null);
};
test('01 declared schema and bounded syntactic namespace',()=>{
  assert.equal(SCHEMA,'CoCivium.CoAllBloom.CompositionalProposal.R0');
  assert.equal(ADDRESSABLE_COUNT,3000);assert.equal(MAX_PREVIEW,8);
});
test('02 ten explicitly named operators',()=>assert.equal(OPERATORS.length,10));
test('03 ten distinct typed frames',()=>assert.equal(new Set(FRAMES).size,10));
test('04 five distinct time frames',()=>assert.equal(new Set(TIMES).size,5));
test('05 six accessible projection types',()=>assert.equal(new Set(PROJECTIONS).size,6));
test('06 no synthetic address materializes a worker',()=>{
  for(const i of [0,1,7,77,1098,2999]){
    const x=addressAt(i);assert.equal(x.active_workers,0);assert.equal(x.materialized,false);
  }
});
test('07 address stable on replay',()=>assert.deepEqual(addressAt(1173),addressAt(1173)));
test('08 address outside namespace fails closed',()=>{
  for(const i of [-1,3000,3001,NaN,1.4,Number.MAX_SAFE_INTEGER+1])
    assert.throws(()=>addressAt(i),/HELD_INDEX/);
});
test('09 every decoded axis is declared',()=>{
  for(const i of [0,5,100,419,2900,2999]){
    const x=addressAt(i);
    assert.ok(OPERATORS.includes(x.operator));assert.ok(FRAMES.includes(x.frame));
    assert.ok(TIMES.includes(x.time));assert.ok(PROJECTIONS.includes(x.projection));
  }
});
test('10 empty or missing requests held',()=>{
  for(const a of [null,undefined,[],{},'bad'])assert.throws(()=>propose(a));
});
test('11 unknown fields fail before projection',()=>{
  assert.throws(()=>go({raw_key:'TEST_VALUE_NOT_A_REAL_KEY'}),/HELD_UNDECLARED_FIELD/);
  assert.throws(()=>go({clipboard_data:'TEST_VALUE_NOT_A_REAL_SECRET'}),/HELD_UNDECLARED_FIELD/);
  assert.throws(()=>go({remote_effect:true}),/HELD_UNDECLARED_FIELD/);
});
test('12 operator typo fails closed',()=>assert.throws(()=>go({operator:'EXECUTE_ALL'}),/HELD_INVALID_OPERATOR/));
test('13 unknown frame fails closed',()=>assert.throws(()=>go({frame:'CONFIRMED_DIVINITY'}),/HELD_INVALID_FRAME/));
test('14 unknown time or projection held',()=>{
  assert.throws(()=>go({time:'TIME_TRAVEL_PROVEN'}),/HELD_INVALID_TIME/);
  assert.throws(()=>go({projection:'OS_MOUSE_HOOK'}),/HELD_INVALID_PROJECTION/);
});
test('15 no private or unknown source data admitted',()=>{
  for(const privacy_class of ['PRIVATE','UNKNOWN','SECRET']){
    assert.throws(()=>go({assertion:{...sample,privacy_class}}));
  }
});
test('16 no unsourced or arbitrary URLs',()=>{
  assert.throws(()=>go({assertion:{...sample,source_ref:'https://private.example/abc'}}));
});
test('17 no unchecked scientific promotion',()=>{
  assert.throws(()=>go({assertion:{...sample,claim_status:'PROVEN'}}));
});
test('18 truth status may remain unknown',()=>{
  const p=go({assertion:{...sample,claim_status:'UNKNOWN'}});
  assert.equal(p.sources[0].claim_status,'UNKNOWN');zero(p);
});
test('19 finite source and valid time remain unchanged',()=>{
  const p=go();assert.equal(p.sources[0].source_ref,sample.source_ref);
  assert.equal(p.sources[0].valid_time,sample.valid_time);
  assert.equal(p.sources[0].scope,sample.scope);zero(p);
});
test('20 converse is not negation',()=>{
  const c=go({operator:'CONVERSE'}),n=go({operator:'NEGATE_QUESTION'});
  assert.equal(c.candidate_kind,'CONVERSE_VIEW_NOT_NEW_EVIDENCE');
  assert.equal(n.candidate_kind,'QUESTION_NOT_NEGATIVE_FACT');
  assert.notEqual(c.candidate_kind,n.candidate_kind);zero(c);zero(n);
});
test('21 null open world does not imply absence',()=>{
  const p=go({operator:'NULL_OPEN_WORLD'});
  assert.equal(p.candidate_kind,'UNKNOWN_NOT_ABSENT');
  assert.ok(p.negative_controls.includes('UNKNOWN_NE_ABSENT'));zero(p);
});
test('22 orthogonal goes beyond inversion',()=>{
  const p=go({operator:'ORTHOGONAL'});
  assert.equal(p.candidate_kind,'OUTSIDE_CURRENT_AXIS');zero(p);
});
test('23 in-between permits transitional model',()=>{
  const p=go({operator:'INBETWEEN'});
  assert.equal(p.candidate_kind,'TRANSITIONAL_MODEL');zero(p);
});
test('24 counterfactual not observation',()=>{
  const p=go({operator:'COUNTERFACTUAL',time:'HISTORICAL_REPLAY'});
  assert.equal(p.candidate_kind,'COUNTERFACTUAL_NOT_OBSERVATION');zero(p);
});
test('25 future remains proposed rather than observed',()=>{
  const p=go({time:'FUTURE_SCENARIO'});
  assert.equal(p.status,'PROPOSAL_ONLY__NOT_A_FACT');zero(p);
});
test('26 G_d and mythic classes not empirical measurement',()=>{
  for(const frame of ['SPIRITUAL_SYMBOL','MYTHIC_CULTURAL']){
    const p=go({frame});assert.equal(p.epistemic,'SYMBOLIC_OR_CULTURAL');zero(p);
  }
});
test('27 nonphysical hypothesis is not supernatural fact',()=>{
  const p=go({frame:'NONPHYSICAL_HYPOTHESIS'});
  assert.equal(p.epistemic,'SPECULATIVE_UNMEASURED');zero(p);
});
test('28 ET hypothesis never contact or detection',()=>{
  const p=go({frame:'ET_HYPOTHESIS'});
  assert.equal(p.epistemic,'ET_HYPOTHESIS_ONLY');
  assert.ok(p.negative_controls.includes('ET_STORY_NE_ET_DETECTION'));zero(p);
});
test('29 unknown ontology remains proposed',()=>{
  const p=go({frame:'UNKNOWN_ONTOLOGY'});
  assert.equal(p.epistemic,'SPECULATIVE_UNMEASURED');zero(p);
});
test('30 cannot smuggle second source into unary operator',()=>{
  assert.throws(()=>go({right:other}),/HELD_SECOND_SOURCE_WITHOUT_COMPOSITION/);
});
test('31 composition requires two sourced assertions',()=>{
  assert.throws(()=>go({operator:'COMPOSE_PROPOSAL'}),/HELD_MISSING_SECOND_SOURCE/);
});
test('32 two compatible distinct sources combine only as a question',()=>{
  const p=go({operator:'COMPOSE_PROPOSAL',right:other});
  assert.equal(p.candidate_kind,'COMPOSITION_QUESTION_NOT_JOINED_FACT');
  assert.equal(p.sources.length,2);zero(p);
});
test('33 same exact source cannot pretend to be an independent input',()=>{
  assert.throws(()=>go({operator:'COMPOSE_PROPOSAL',right:sample}),/HELD_NONINDEPENDENT_DUPLICATE_SOURCE/);
});
test('34 incompatible scope cannot be joined',()=>{
  assert.throws(()=>go({operator:'COMPOSE_PROPOSAL',right:{...other,scope:'elsewhere'}}),/HELD_INCOMPATIBLE_SOURCE_SCOPES/);
});
test('35 incompatible time cannot be joined',()=>{
  assert.throws(()=>go({operator:'COMPOSE_PROPOSAL',right:{...other,valid_time:'2030-01-01'}}),/HELD_INCOMPATIBLE_SOURCE_SCOPES/);
});
test('36 second private source held',()=>{
  assert.throws(()=>go({operator:'COMPOSE_PROPOSAL',right:{...other,privacy_class:'PRIVATE'}}));
});
test('37 Turtle depth zero and two remain passive',()=>{
  for(const depth of [0,2]){const p=go({operator:'TURTLE_CHALLENGE',turtle_depth:depth});
    assert.equal(p.turtle_depth,depth);zero(p);}
});
test('38 Turtle depth escalation is held',()=>{
  for(const turtle_depth of [-1,3,'2',1.5]){
    assert.throws(()=>go({operator:'TURTLE_CHALLENGE',turtle_depth}),/HELD_TURTLE_BUDGET/);
  }
});
test('39 preview is exactly bounded and effect-free',()=>{
  const list=previewAddresses([0,1,2,3,4,5,6,7],sample,registry);
  assert.equal(list.length,8);for(const x of list){zero(x);assert.equal(x.sources.length,1);}
});
test('40 ninth preview disallowed',()=>assert.throws(()=>
  previewAddresses([0,1,2,3,4,5,6,7,8],sample,registry),/HELD_PREVIEW_BUDGET/));
test('41 duplicate preview addresses held',()=>assert.throws(()=>
  previewAddresses([0,0],sample,registry),/HELD_PREVIEW_BUDGET/));
test('42 address outside declared field held in preview',()=>assert.throws(()=>
  previewAddresses([3000],sample,registry),/HELD_INDEX/));
test('43 composition address requires second when selected',()=>{
  assert.equal(addressAt(2999).operator,'COMPOSE_PROPOSAL');
  assert.throws(()=>previewAddresses([2999],sample,registry),/HELD_MISSING_SECOND_SOURCE/);
  const p=previewAddresses([2999],sample,registry,other)[0];zero(p);
  assert.equal(p.sources.length,2);
});
test('44 no private extra fields echo from input assertion',()=>{
  const p=go({assertion:{...sample,synthetic_secret:'DUMMY_DATA_NOT_REAL_SECRET'}});
  assert.equal(JSON.stringify(p).includes('DUMMY_DATA_NOT_REAL_SECRET'),false);zero(p);
});
for(const operator of OPERATORS){
  if(operator==='COMPOSE_PROPOSAL')continue;
  test('operator '+operator+' cannot cause effects',()=>{
    const p=go({operator});zero(p);
  });
}
