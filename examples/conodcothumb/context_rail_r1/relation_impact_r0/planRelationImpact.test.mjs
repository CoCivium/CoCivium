import test from 'node:test';
import assert from 'node:assert/strict';
import {planRelationImpact as plan,SCHEMA} from './planRelationImpact.mjs';

const n=(id,kind='OBJECT',privacy='PUBLIC')=>({id,kind,privacy});
const e=(id,from,to,kind='DEPENDS_ON',status='VERIFIED_DEPENDENCY',
  currentness='CURRENT',privacy='PUBLIC')=>({id,from,to,kind,status,currentness,privacy});
const packet=(nodes=[n('a'),n('b')],edges=[e('ab','a','b')],more={})=>
  ({seed_id:'a',nodes,edges,...more});
const result=(nodes,edges,more={})=>plan(packet(nodes,edges,more));
const chain=()=>packet([n('a'),n('b'),n('c')],[e('ab','a','b'),e('bc','b','c')]);
const isZero=(v)=>Object.values(v.effects).every(x=>x===0);

test('explicit shadow schema',()=>assert.equal(plan(packet()).schema,SCHEMA));
test('no execution on candidate preview',()=>assert.equal(plan(packet()).executed_mutations,0));
test('no receiver acknowledgement inferred',()=>assert.equal(plan(packet()).receiver_ack,false));
test('no source bytes materialized',()=>assert.equal(plan(packet()).materialized_bytes,0));
test('all external effects zero',()=>assert.ok(isZero(plan(packet()))));
test('ordinary dependency becomes a review candidate',()=>assert.deepEqual(plan(packet()).candidates.map(x=>x.id),['b']));
test('every candidate is a review, not a write',()=>assert.ok(plan(packet()).candidates.every(x=>x.disposition==='REVIEW_CANDIDATE_ONLY')));
test('transitive dependency chain reviewed',()=>assert.deepEqual(plan(chain()).candidates.map(x=>[x.id,x.depth]),[['b',1],['c',2]]));
test('graph direction is from upstream to dependent',()=>assert.deepEqual(plan({seed_id:'b',nodes:[n('a'),n('b')],edges:[e('ab','a','b')]}).candidates,[]));
test('relation can itself be a dependent node',()=>{
 const v=result([n('a'),n('r','RELATION'),n('view','VIEW')],[e('ar','a','r'),e('rv','r','view')]);
 assert.deepEqual(v.candidates.map(x=>x.kind),['RELATION','VIEW']);
});
test('relation may itself be the seed',()=>{
 const p=packet([n('r','RELATION'),n('view','VIEW')],[e('rv','r','view')],{seed_id:'r'});
 assert.equal(plan(p).seed_kind,'RELATION'); assert.equal(plan(p).candidates[0].id,'view');
});
test('cycles terminate without duplicates',()=>{
 const v=result([n('a'),n('b')],[e('ab','a','b'),e('ba','b','a')]);
 assert.deepEqual(v.candidates.map(x=>x.id),['b']);
});
test('self dependency never reselects the seed',()=>assert.equal(result([n('a')],[e('aa','a','a')]).candidate_count,0));
test('unrelated nodes do not inherit impact',()=>assert.deepEqual(result([n('a'),n('b'),n('c')],[e('ab','a','b')]).candidates.map(x=>x.id),['b']));
test('private node invisible including counts',()=>{
 const withPrivate=result([n('a'),n('b'),n('hidden','OBJECT','PRIVATE')],[e('ab','a','b'),e('secret','a','hidden')]);
 assert.deepEqual(withPrivate,result([n('a'),n('b')],[e('ab','a','b')]));
});
test('private edge invisible',()=>assert.deepEqual(
 result([n('a'),n('b')],[e('ab','a','b','DEPENDS_ON','VERIFIED_DEPENDENCY','CURRENT','PRIVATE')]),
 result([n('a'),n('b')],[])
));
test('unknown edge classification not assumed public',()=>assert.equal(
 result([n('a'),n('b')],[e('ab','a','b','DEPENDS_ON','VERIFIED_DEPENDENCY','CURRENT','UNKNOWN')]).candidate_count,0
));
test('private seed and unknown seed indistinguishable',()=>{
 const a=plan({seed_id:'hidden',nodes:[n('hidden','OBJECT','PRIVATE')],edges:[]});
 const b=plan({seed_id:'hidden',nodes:[],edges:[]});
 assert.deepEqual(a,b);assert.equal(a.state,'HOLD_PUBLIC_SEED_UNAVAILABLE');
});
test('invalid public node fails closed',()=>assert.equal(result([{id:'!bad',privacy:'PUBLIC',kind:'OBJECT'}],[]).state,'HOLD_INVALID_PUBLIC_METADATA'));
test('invalid public edge fails closed',()=>assert.equal(result([n('a'),n('b')],[e('bad!','a','b')]).state,'HOLD_INVALID_PUBLIC_METADATA'));
test('public node collision fails closed',()=>assert.equal(result([n('a'),n('a')],[]).state,'HOLD_PUBLIC_IDENTITY_COLLISION'));
test('public edge collision fails closed',()=>assert.equal(result([n('a'),n('b')],[e('x','a','b'),e('x','a','b')]).state,'HOLD_PUBLIC_IDENTITY_COLLISION'));
test('stale dependency not propagated',()=>{
 const v=result([n('a'),n('b')],[e('ab','a','b','DEPENDS_ON','VERIFIED_DEPENDENCY','STALE')]);
 assert.equal(v.candidate_count,0);assert.equal(v.optional_explore[0].state,'EXPLORE_NOT_PROPAGATE');
});
test('unknown dependency currentness not propagated',()=>assert.equal(
 result([n('a'),n('b')],[e('ab','a','b','DEPENDS_ON','VERIFIED_DEPENDENCY','UNKNOWN')]).candidate_count,0
));
test('proposed dependency only offers exploration',()=>{
 const v=result([n('a'),n('b')],[e('ab','a','b','DEPENDS_ON','PROPOSED')]);
 assert.equal(v.candidate_count,0);assert.equal(v.optional_explore[0].id,'b');
});
test('analogy offers exploration only',()=>{
 const v=result([n('a'),n('b')],[e('ab','a','b','ANALOGOUS_TO')]);
 assert.equal(v.candidate_count,0);assert.equal(v.optional_explore[0].relation,'ANALOGOUS_TO');
});
test('contrast offers exploration only',()=>assert.equal(
 result([n('a'),n('b')],[e('ab','a','b','CONTRASTS_WITH')]).candidate_count,0
));
test('challenge offers exploration only',()=>assert.equal(
 result([n('a'),n('b')],[e('ab','a','b','CHALLENGES')]).candidate_count,0
));
test('inverted view does not imply causal propagation',()=>assert.equal(
 result([n('a'),n('b')],[e('ab','a','b','INVERTS_VIEW_OF')]).candidate_count,0
));
test('depth zero means nothing downstream materialized',()=>{
 const v=plan({...chain(),max_depth:0});assert.equal(v.candidate_count,0);
 assert.equal(v.depth_truncated,true);assert.equal(v.state,'PARTIAL_REVIEW_CANDIDATES');
});
test('depth one keeps direct only with honest truncation',()=>{
 const v=plan({...chain(),max_depth:1});
 assert.deepEqual(v.candidates.map(x=>x.id),['b']);assert.equal(v.depth_truncated,true);
});
test('count cap keeps selected only and marks incomplete',()=>{
 const v=result([n('a'),n('b'),n('c')],[e('ab','a','b'),e('ac','a','c')],{max_candidates:1});
 assert.equal(v.candidate_count,1);assert.equal(v.count_truncated,true);assert.equal(v.state,'PARTIAL_REVIEW_CANDIDATES');
});
test('candidate selection stable across link input permutations',()=>{
 const nodes=[n('a'),n('b'),n('c')],x=e('ab','a','b'),y=e('ac','a','c');
 assert.deepEqual(result(nodes,[x,y]),result(nodes,[y,x]));
});
test('seed change classified as candidate by default',()=>assert.equal(plan(packet()).change_state,'CANDIDATE_DELTA'));
test('observed delta label is not evidence promotion',()=>{
 const v=plan(packet(undefined,undefined,{change_state:'OBSERVED_DELTA_REF_ONLY'}));
 assert.equal(v.change_state,'OBSERVED_DELTA_REF_ONLY');assert.equal(v.candidates[0].disposition,'REVIEW_CANDIDATE_ONLY');
});
test('null request held without effect',()=>{
 const v=plan(null);assert.equal(v.state,'HOLD_INVALID_INPUT');assert.ok(isZero(v));
});
test('invalid max-depth held',()=>assert.equal(plan(packet(undefined,undefined,{max_depth:9})).state,'HOLD_INVALID_INPUT'));
test('invalid candidate budget held',()=>assert.equal(plan(packet(undefined,undefined,{max_candidates:33})).state,'HOLD_INVALID_INPUT'));
test('128-node public bound enforced',()=>{
 const nodes=Array.from({length:129},(_,i)=>n('n'+i));
 assert.equal(result(nodes,[]).state,'HOLD_PUBLIC_INPUT_BUDGET');
});
test('256-edge public bound enforced',()=>{
 const edges=Array.from({length:257},(_,i)=>e('e'+i,'a','b'));
 assert.equal(result([n('a'),n('b')],edges).state,'HOLD_PUBLIC_INPUT_BUDGET');
});
test('no input mutation while computing preview',()=>{
 const p=chain(),original=JSON.stringify(p);plan(p);assert.equal(JSON.stringify(p),original);
});
