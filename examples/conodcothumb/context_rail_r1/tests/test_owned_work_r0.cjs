'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const owned=require('../CoOwnedWorkR0.js');
function fake(){
  const values=new Map(),stats={reads:0,writes:0};
  return {getItem:k=>(stats.reads++,values.has(k)?values.get(k):null),
    setItem:(k,v)=>(stats.writes++,values.set(k,v)),values,stats};
}
const selected={privacy:'PUBLIC',context:'RESEARCH',question:'WHAT_ELSE',
  fixture:false,gesture:'EXPLICIT_RING',preview_state:'PROPOSED_ONLY'};
test('one actual browser-origin write for ten repeated explicit synthetic events',()=>{
  const store=fake();let first=owned.preserve(store,selected);
  assert.equal(first.state,'COMMITTED_BROWSER_LOCAL');assert.equal(first.committed,1);
  for(let i=0;i<9;i++)assert.equal(owned.preserve(store,selected).state,'DUPLICATE_SUPPRESSED');
  assert.equal(store.stats.writes,1);
  assert.equal(owned.recover(store).state,'RECOVERED_BROWSER_LOCAL');
});
test('recover only source-declared fixture narrative with prior decisions and blockers',()=>{
  const store=fake();owned.preserve(store,selected);
  const result=owned.recover(store);
  assert.equal(result.work_id,'CoPre.ReadyCycle.Synthetic.R0');
  assert.equal(result.decisions.length,3);assert.equal(result.blockers.length,3);
  assert.match(result.summary,/Ready Cycle/);assert.match(result.next_safe_deed,/receiver/);
  assert.match(result.source_ref,/@[0-9a-f]{40}$/);
  assert.equal(result.source_verified_by_browser,false);
  assert.equal(result.receiver_ack,false);
  assert.equal(result.live_mouse,false);
});
test('keyboard preview shares the same WorkID and does not create second write',()=>{
  const store=fake();owned.preserve(store,selected);
  assert.equal(owned.preserve(store,{...selected,gesture:'KEYBOARD_FALLBACK'}).state,
    'DUPLICATE_SUPPRESSED');
  assert.equal(store.stats.writes,1);
});
test('native mouse passes through without writing',()=>{
  const store=fake();
  assert.equal(owned.preserve(store,{...selected,gesture:'NATIVE_MIDDLE'}).state,
    'HELD_EXPLICIT_SCOPE');
  assert.equal(store.stats.writes,0);
});
test('privacy, fixture, accidental context and absent preview all fail closed',()=>{
  for(const bad of [
    {privacy:'PRIVATE_LOCAL'},{privacy:'UNKNOWN'},{privacy:'SENSITIVE'},{fixture:true},
    {context:'OUTREACH'},{question:'WHEN'},{preview_state:'HELD_PRIVACY'},
    {gesture:'UNBOUND'}
  ]){
    const store=fake();
    assert.equal(owned.preserve(store,{...selected,...bad}).state,'HELD_EXPLICIT_SCOPE');
    assert.equal(store.stats.writes,0);
  }
});
test('cannot inject private narrative, source, authority or lease into the fixture',()=>{
  const store=fake();owned.preserve(store,selected);
  const result=owned.recover(store);
  assert.equal(result.source_ref.startsWith('CoCivium/CoCivium:'),true);
  assert.equal(owned.fixture().consent,'SYNTHETIC_TEST_ONLY');
  assert.equal(owned.fixture().lease_epoch,1);
  assert.equal(JSON.stringify(owned.fixture()).includes('private@'),false);
});
test('revocation preserves record and blocks replay',()=>{
  const store=fake();owned.preserve(store,selected);
  assert.equal(owned.revoke(store).state,'REVOKED_BROWSER_LOCAL');
  assert.equal(owned.recover(store).state,'HELD_REVOKED');
  assert.equal(owned.preserve(store,selected).state,'HELD_REVOKED');
  assert.equal(owned.revoke(store).state,'ALREADY_REVOKED');
  assert.equal(store.stats.writes,2);
});
test('tampered work object cannot become recovered evidence or be overwritten',()=>{
  const store=fake();owned.preserve(store,selected);
  const stored=JSON.parse(store.values.get(owned.STORAGE_KEY));
  stored.packet.source_sha256='0'.repeat(64);
  store.values.set(owned.STORAGE_KEY,JSON.stringify(stored));
  assert.equal(owned.recover(store).state,'HELD_CONFLICT');
  assert.equal(owned.preserve(store,selected).state,'HELD_CONFLICT');
  assert.equal(store.stats.writes,1);
});
test('duplicate same WorkID but changed narrative holds instead of clobber',()=>{
  const store=fake();owned.preserve(store,selected);
  const stored=JSON.parse(store.values.get(owned.STORAGE_KEY));
  stored.packet.narrative_summary='Different story';
  store.values.set(owned.STORAGE_KEY,JSON.stringify(stored));
  assert.equal(owned.preserve(store,selected).state,'HELD_CONFLICT');
});
test('storage disabled or quota reached fails closed and makes no success claim',()=>{
  const disabled={getItem(){throw Error('Denied')},setItem(){throw Error('Denied')}};
  assert.equal(owned.preserve(disabled,selected).state,'HELD_STORAGE_UNAVAILABLE');
  assert.equal(owned.recover(disabled).state,'HELD_STORAGE_UNAVAILABLE');
  assert.equal(owned.preserve(null,selected).state,'HELD_STORAGE_UNAVAILABLE');
  const full={getItem(){return null},setItem(){throw Error('Quota')}};
  assert.equal(owned.preserve(full,selected).state,'HELD_STORAGE_UNAVAILABLE');
});
test('lost-write acknowledgment is detected by exact readback',()=>{
  const store={getItem(){return null},setItem(){}};
  assert.equal(owned.preserve(store,selected).state,'HELD_WRITE_READBACK');
});
test('unknown, malformed or oversized local state fails closed',()=>{
  for(const value of ['[]','{"state":"ACTIVE"}','z'.repeat(9000)]){
    const store=fake();store.values.set(owned.STORAGE_KEY,value);
    assert.equal(owned.preserve(store,selected).state==='COMMITTED_BROWSER_LOCAL',false);
  }
});
test('read-only recovery never writes',()=>{
  const store=fake();owned.preserve(store,selected);const before=store.stats.writes;
  for(let i=0;i<5;i++)assert.equal(owned.recover(store).state,'RECOVERED_BROWSER_LOCAL');
  assert.equal(store.stats.writes,before);
});
