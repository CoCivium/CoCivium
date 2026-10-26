import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { reviewSyntheticCrosswalk as review, summarizeBridge as summary, NAME_MATCH, ALIAS_CANDIDATES,
  UNQUALIFIED_NEAR_MATCHES, SOURCE_PINS, NO_EFFECTS } from './CoMiddleBridgeR1.mjs';
import { converseView, negationQuestion } from '../CoRelationKernelR0.mjs';
const registry=JSON.parse(readFileSync(new URL('../registry.json',import.meta.url),'utf8'));
const fixture=registry.sample_assertion;
const packet=(relation_id='DEPENDS_ON',delta={})=>({...fixture,relation_id,...delta});

// These are typed semantic and safety checks, not X2 runtime, recipient ACK or model tests.
test('bridge has one versioned schema, zero authority and zero workers',()=>{
 const a=summary();assert.equal(a.schema,'CoCivium.CoMiddle.CrossSchemaBridge.R1');assert.equal(a.authority,'NONE');
 assert.equal(a.same_name_ids,6);assert.equal(a.alias_candidate_ids,4);assert.equal(a.blocked_near_matches,6);
 assert.deepEqual(a.effects,NO_EFFECTS);assert.equal(a.target_executable,false);
});
test('source pins are exact 40-char Git blob identities',()=>{
 for(const pin of Object.values(SOURCE_PINS))assert.match(pin,/^[0-9a-f]{40}$/);
 assert.equal(SOURCE_PINS.r0_registry_blob,'3ad1d048a864df9cb6ed364faebf40614d96edf1');
 assert.equal(SOURCE_PINS.r2_kernel_blob,'15fb5d3065e147c3615d05e449d39de47abd4ef6');
});
for(const [relation, converse] of Object.entries(NAME_MATCH)){
 test('same-name pair '+relation+' remains a name-only projection',()=>{
  const v=review(packet(relation),registry);
  assert.equal(v.status,'SHADOW_NAME_MATCH_ONLY');assert.equal(v.target_candidate.relation_id,relation);
  assert.equal(v.target_candidate.converse_id,converse);assert.equal(v.target_executable,false);
  assert.equal(v.source.claim_status,fixture.claim_status);assert.equal(v.receiver_ack,false);
 });
}
for(const [relation,entry] of Object.entries(ALIAS_CANDIDATES)){
 test('converse spelling alias '+relation+' remains HELD',()=>{
  const v=review(packet(relation),registry);
  assert.equal(v.status,'HELD_EXPLICIT_ALIAS_REVIEW');assert.equal(v.target_candidate.relation_id,entry.r2_id);
  assert.equal(v.target_candidate.converse_id,entry.r2_converse);
  assert.equal(v.target_candidate.kind,'QUALIFIED_ALIAS_CANDIDATE_ONLY');assert.equal(v.requires_human_semantic_approval,true);
 });
}
for(const relation of Object.keys(UNQUALIFIED_NEAR_MATCHES)){
 test('unsafe near-match '+relation+' does not emit a target alias',()=>{
  const v=review(packet(relation),registry);
  assert.equal(v.status,'HELD_SEMANTIC_NON_EQUIVALENCE_RISK');assert.equal(v.target_candidate,null);
 });
}
test('changed schema version and unqualified synthetic ID fail closed',()=>{
 const changed=structuredClone(registry);changed.version='2026-11.R0';
 assert.equal(review(packet('DEPENDS_ON'),changed).status,'HELD_UNQUALIFIED_PINNED_SOURCE');
 assert.equal(review(packet('DEPENDS_ON',{source_ref:'synthetic://codemo/001?secret=abc'}),registry).status,'HELD_UNQUALIFIED_PINNED_SOURCE');
});
test('unknown known-to-R0 relation stays unmapped',()=>{
 const z=review(packet('RENDERS'),registry);assert.equal(z.status,'HELD_NOT_MAPPED');assert.equal(z.target_candidate,null);
});
test('missing evidence version does not yield candidate or leak source',()=>{
 const z=review(packet('CONTAINS',{source_version:''}),registry);
 assert.equal(z.status,'HELD_SOURCE_PRIVACY_OR_SCHEMA');assert.equal(z.source,null);
});
test('unknown and private source classification fail closed and redacted',()=>{
 for(const privacy_class of [undefined,'PRIVATE','PASSWORD','UNKNOWN',null]){
  const z=review(packet('DEPENDS_ON',{privacy_class,secret:'private fixture secret'}),registry);
  assert.equal(z.status,'HELD_SOURCE_PRIVACY_OR_SCHEMA');assert.equal(z.source,null);
  assert.equal(JSON.stringify(z).includes('private fixture secret'),false);
 }
});
test('non synthetic protocol fails closed without leaking arbitrary paths',()=>{
 for(const source_ref of ['file:///secret','https://test.example/private','',null]){
  const z=review(packet('DEPENDS_ON',{source_ref}),registry);
  assert.equal(z.status,'HELD_SOURCE_PRIVACY_OR_SCHEMA');assert.equal(z.source,null);
 }
});
test('unknown external effect request is dropped by allowlisted fields',()=>{
 const z=review(packet('DEPENDS_ON',{sends:'send-now',credential:'INVENTED_TEST_SECRET'}),registry);
 assert.equal(z.status,'HELD_EXPLICIT_ALIAS_REVIEW');assert.equal(z.authority,'NONE');
 assert.deepEqual(z.effects,NO_EFFECTS);assert.equal(JSON.stringify(z).includes('INVENTED_TEST_SECRET'),false);
});
test('source scope, version, valid time, claim status and IDs survive unchanged',()=>{
 const z=review(packet('DEPENDS_ON',{claim_status:'UNKNOWN'}),registry);
 assert.equal(z.source.source_version,fixture.source_version);assert.equal(z.source.source_ref,fixture.source_ref);
 assert.equal(z.source.scope,fixture.scope);assert.equal(z.source.valid_time,fixture.valid_time);
 assert.equal(z.source.claim_status,'UNKNOWN');assert.equal(z.source.subject_id,fixture.subject_id);
 assert.equal(z.source.object_id,fixture.object_id);
});
test('type drift halts aliasing rather than assuming WorkObject membership',()=>{
 const changed=structuredClone(registry);changed.relation_types.find(v=>v.id==='CONTAINS').object_type='Actor';
 const z=review(packet('CONTAINS'),changed);assert.equal(z.status,'HELD_SOURCE_DRIFT');assert.equal(z.source,null);
});
test('converse drift halts matching names',()=>{
 const changed=structuredClone(registry);changed.relation_types.find(v=>v.id==='CITES').counterpart='CITED_ELSEWHERE';
 const z=review(packet('CITES'),changed);assert.equal(z.status,'HELD_SOURCE_DRIFT');
});
test('invalid assertion and altered registry fail closed',()=>{
 for(const x of [null,42,[],{},packet('FAKE')]){
  assert.equal(review(x,registry).status,'HELD_SOURCE_PRIVACY_OR_SCHEMA');
 }
 const changed=structuredClone(registry);changed.schema='FAKE';
 assert.equal(review(packet(),changed).status,'HELD_SOURCE_PRIVACY_OR_SCHEMA');
});
test('all 20 R0 types stay inspectable without a rewrite',()=>{
 const a=registry.relation_types.map(r=>review(packet(r.id),registry));
 assert.equal(a.length,20);assert(a.every(z=>z.source?.relation_id && z.target_executable===false));
 assert(a.every(z=>z.authority==='NONE'&&z.effects.network===0 && z.effects.send===0));
});
test('R0 converse is not negation or undo',()=>{
 const c=converseView(packet(),registry),n=negationQuestion(packet(),registry),z=review(packet(),registry);
 assert.equal(c.relation_id,'REQUIRED_BY');assert.equal(n.kind,'NEGATION_QUESTION_NOT_A_FACT');
 assert.equal(z.target_candidate.relation_id,'DEPENDS_ON');
 assert.equal(z.nonclaims.includes('CONVERSE_NE_UNDO'),true);
});
test('bridge never mutates frozen source or registry',()=>{
 const x=Object.freeze(packet('SUPERSEDES'));const before=JSON.stringify(x);
 const z=review(x,registry);assert.equal(JSON.stringify(x),before);
 assert.equal(z.status,'SHADOW_NAME_MATCH_ONLY');
});
test('all output classes deny receiver ACK or effects',()=>{
 for(const id of registry.relation_types.map(x=>x.id)){
  const z=review(packet(id),registry);assert.equal(z.receiver_ack,false);
  assert.equal(z.requires_human_semantic_approval,true);
  assert.equal(z.effects.device+z.effects.network+z.effects.send+z.effects.mutation,0);
 }
});
// CI additionally loads the exact R2 source from its independent open PR branch.
test('actual R2 PR source names match the pinned crosswalk witness', {skip:!process.env.R2_CJS_PATH},()=>{
 const require=createRequire(import.meta.url);
 const r2=require(process.env.R2_CJS_PATH);
 assert.equal(r2.SCHEMA,'CoCivium.CoMiddle.RelationInverse.R2');
 assert.equal(r2.relationMap.size,36);
 for(const [id,converse] of Object.entries(NAME_MATCH))assert.equal(r2.relationMap.get(id)?.converse,converse);
 for(const entry of Object.values(ALIAS_CANDIDATES))assert.equal(r2.relationMap.get(entry.r2_id)?.converse,entry.r2_converse);
 for(const id of Object.keys(UNQUALIFIED_NEAR_MATCHES))assert(registry.relation_types.some(r=>r.id===id));
});
