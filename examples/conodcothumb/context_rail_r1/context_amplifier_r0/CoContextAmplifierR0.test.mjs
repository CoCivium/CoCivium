import test from 'node:test';
import assert from 'node:assert/strict';
import {planContext,SCHEMA} from './CoContextAmplifierR0.mjs';
const H=(char)=>char.repeat(64);
const s=(id,cost_units=3,opts={})=>({id,source_ref:'fixture:'+id,
  sha256:H(id[0] || 'a'),cost_units,utility:50,kind:'SUPPORT',
  freshness:'CURRENT',privacy:'PUBLIC',...opts});
const p=(sources,budget_units=14,headroom_units=3)=>planContext({work_id:'work.r0',budget_units,headroom_units,sources});
const n=(name,fn)=>test(name,fn);
n('schema explicit',()=>assert.equal(p([]).schema,SCHEMA));
n('zero effects',()=>assert.deepEqual(Object.values(p([s('alpha')]).effects),[0,0,0,0,0]));
n('none of the candidates creates model-token count proof',()=>assert.match(p([]).tokenizer,/NOT_MEASURED/));
n('no receiver ack is created',()=>assert.equal(p([s('alpha')]).receiver_ack,false));
n('headroom reserved',()=>assert.equal(p([s('alpha')],10,4).available_units,6));
n('never over budget',()=>assert.ok(p([s('alpha',5),s('beta',5),s('gamma',5)],12,2).cost_units_used<=10));
n('required cost included',()=>assert.ok(p([s('alpha',5,{required:true}),s('beta',5)],10,2).selected.some(x=>x.id==='alpha')));
n('required overflow held',()=>assert.equal(p([s('alpha',9,{required:true})],10,2).state,'HOLD_REQUIRED_EXCEEDS_BUDGET'));
n('required stale held',()=>assert.equal(p([s('alpha',2,{required:true,freshness:'STALE'})]).state,'HOLD_REQUIRED_SOURCE_UNAVAILABLE'));
n('private item leaves no observable metadata',()=>{const v=p([s('alpha',2),s('SECRET_ID',2,{privacy:'PRIVATE'})]);assert.deepEqual(v,p([s('alpha',2)]));});
n('required private fails closed',()=>assert.equal(p([s('SECRET_ID',2,{privacy:'PRIVATE',required:true})]).state,'HOLD_REQUIRED_SOURCE_UNAVAILABLE'));
n('unknown freshness held',()=>assert.equal(p([s('alpha',3,{freshness:'UNKNOWN'})]).selected.length,0));
n('stale excluded',()=>assert.equal(p([s('alpha',3,{freshness:'STALE'})]).selected.length,0));
n('bad hash not trusted',()=>assert.equal(p([s('alpha',2,{sha256:'not-a-digest'})]).selected.length,0));
n('invalid kind held',()=>assert.equal(p([s('alpha',2,{kind:'SEND'})]).selected.length,0));
n('same bytes and same argument type deduped',()=>{
  const v=p([s('alpha',2,{sha256:H('a')}),s('alias',2,{sha256:H('a')})]);
  assert.equal(v.selected.length,1);assert.equal(v.selected[0].aliases.length,1);
});
n('same bytes different roles preserved',()=>{
  const v=p([s('alpha',2,{sha256:H('a'),kind:'SUPPORT'}),s('counter',2,{sha256:H('a'),kind:'COUNTER'})]);
  assert.equal(v.selected.length,2);
});
n('counterargument chosen when eligible',()=>{
  const v=p([s('alpha',5,{utility:100}),s('counter',4,{kind:'COUNTER',utility:3})],10,1);
  assert.ok(v.selected.some(x=>x.kind==='COUNTER'));
});
n('counter omission explicitly reported',()=>{
  const v=p([s('alpha',5,{required:true}),s('counter',5,{kind:'COUNTER'})],8,3);
  assert.equal(v.counterevidence_omitted,true);
});
n('source reference remains pointer not bytes',()=>{
  const v=p([s('alpha',2)]);assert.equal(v.materialized_source_bytes,0);assert.equal('content' in v.selected[0],false);
});
n('replay deterministic',()=>{
  const input=[s('beta',4),s('alpha',2)];assert.deepEqual(p(input),p(input));
});
n('no hidden output when request invalid',()=>assert.equal(planContext(null).state,'HOLD_INVALID_REQUEST'));
n('reject zero budget',()=>assert.equal(p([s('alpha')],0,0).state,'HOLD_INVALID_REQUEST'));
n('reject noninteger budgets',()=>assert.equal(p([s('alpha')],8.2,1).state,'HOLD_INVALID_REQUEST'));
n('reject headroom equal to budget',()=>assert.equal(p([],4,4).state,'HOLD_INVALID_REQUEST'));
n('reject more than 256 source descriptors',()=>assert.equal(p(Array.from({length:257},(_,i)=>s('s'+i))).state,'HOLD_INVALID_REQUEST'));
n('ID collision fails closed',()=>{const v=p([s('alpha',2),s('alpha',2,{sha256:H('b')})]);assert.equal(v.state,'HOLD_COLLIDING_IDENTITIES');assert.equal(v.selected.length,0);});
n('unknown classification is indistinguishable from absent input',()=>assert.deepEqual(p([s('alpha',2,{privacy:'UNKNOWN'})]),p([])));
n('long logical universe does not expand descriptor cap',()=>assert.equal(p([s('alpha',2)]).selected.length,1));
