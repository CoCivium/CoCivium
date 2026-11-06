'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {createHarness}=require('./CoEventInvocationR0.cjs');
const event=(changes={})=>({event_id:'e1',work_id:'w1',operation:'REFRESH_LOCAL_STATUS',
  privacy:'PUBLIC_SYNTHETIC',observed_ms:950,expires_ms:1100,...changes});
test('button and CoB event use one operation contract',()=>{
  const manual=createHarness(),automatic=createHarness();
  assert.equal(manual.fromButton(event()).state,'LOCAL_ONLY_EXECUTED');
  assert.equal(automatic.fromCoBEvent(event()).state,'LOCAL_ONLY_EXECUTED');
  assert.deepEqual(manual.snapshot(),automatic.snapshot());
});
test('cross-route duplicate is not executed twice',()=>{
  const h=createHarness({budget:2});
  assert.equal(h.fromButton(event()).state,'LOCAL_ONLY_EXECUTED');
  const other=h.fromCoBEvent(event({event_id:'e2'}));
  assert.equal(other.state,'DEDUPED');
  assert.equal(other.first_event_id,'e1');
  assert.equal(h.snapshot().local_refresh_count,1);
});
test('only harmless allowlisted operation can execute',()=>{
  for(const operation of ['SEND_MAIL','DELETE_FILE','TRADE','PUBLISH','']){
    const h=createHarness();assert.equal(h.fromCoBEvent(event({operation})).state,'HELD');
    assert.equal(h.snapshot().unique_operations,0);
  }
});
test('untrusted packet and privacy fail closed without leaking payload',()=>{
  for(const fields of [{privacy:'PRIVATE_LOCAL'},{privacy:'UNKNOWN'},{privacy:'SENSITIVE'},
    {source:'verified'},{credential:'secret'},{event_id:'bad id'},{work_id:''},
    {authority:'ADMIN'},{token:'abc'}]){
    const h=createHarness();const r=h.fromCoBEvent(event(fields));
    assert.equal(r.state,'HELD');assert.equal(h.snapshot().local_refresh_count,0);
    assert.equal(JSON.stringify(r).includes('secret'),false);
  }
});
test('expiry and future timestamps are rejected',()=>{
  for(const fields of [{observed_ms:1001},{expires_ms:999},
    {observed_ms:0,expires_ms:99999},{observed_ms:'950'},{expires_ms:null}]){
    assert.equal(createHarness().fromCoBEvent(event(fields)).reason,'STALE_FUTURE_OR_UNBOUNDED');
  }
});
test('receiver refusal never reports execution',()=>{
  const h=createHarness({receiver_ready:false});
  assert.equal(h.fromCoBEvent(event()).reason,'RECEIVER_NOT_READY');
  assert.equal(h.snapshot().local_refresh_count,0);
});
test('bounded budget cannot be bypassed with a fresh work id',()=>{
  const h=createHarness({budget:1});
  assert.equal(h.fromButton(event()).state,'LOCAL_ONLY_EXECUTED');
  assert.equal(h.fromCoBEvent(event({event_id:'e2',work_id:'w2'})).reason,'BUDGET_EXHAUSTED');
  assert.equal(h.snapshot().local_refresh_count,1);
});
test('every receipt has zero external effects and no receiver proof',()=>{
  const h=createHarness();
  for(const r of [h.fromCoBEvent(event()),h.fromButton(event())]){
    assert.deepEqual(Object.values(r.external_effects),[0,0,0,0,0,0]);
    assert.equal(r.receiver_readproof,'NOT_TESTED');
    assert.equal(r.authority,'SYNTHETIC_POLICY_ONLY');
  }
});
