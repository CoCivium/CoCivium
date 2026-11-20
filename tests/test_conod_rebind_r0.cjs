'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const owned=require('../examples/conodcothumb/context_rail_r1/CoOwnedWorkR0.js');
const {preview}=require('../scripts/CoNodRebindPreviewR0.cjs');
const fixed=owned.fixture();
function storage(){
 const state=new Map();let writes=0;
 return {getItem:k=>state.has(k)?state.get(k):null,
  setItem:(k,v)=>{writes++;state.set(k,v)},
  writes:()=>writes,setRaw:(k,v)=>state.set(k,v),
  getRaw:k=>state.get(k)};
}
function req(over={}){return {token:"'",origin:'EXPLICIT_KEYBOARD',
 presence:'PRESENT',scope:'PUBLIC_SYNTHETIC',effect:'PREVIEW_ONLY',
 pressure:'HEALTHY',work_id:fixed.work_id,...over};}
function prepared(){
 const s=storage();
 const r=owned.preserve(s,{privacy:'PUBLIC',context:'RESEARCH',
  question:'WHAT_ELSE',gesture:'EXPLICIT_RING',preview_state:'PROPOSED_ONLY'});
 assert.equal(r.state,'COMMITTED_BROWSER_LOCAL');
 return s;
}
test('one explicit nod reads an existing WorkID without writes',()=>{
 const s=prepared(),before=s.writes(),out=preview(req(),s);
 assert.equal(out.state,'PREVIEW_ONLY_BROWSER_LOCAL');
 assert.equal(out.work_id,fixed.work_id);
 assert.equal(s.writes(),before);
 assert.equal(out.authority,'NONE');
 assert.ok(Object.values(out.effects).every(x=>x===0));
 assert.equal(out.source_verified,false);
 assert.equal(out.receiver_ack,false);
});
test('repeated nod previews are identical and do not enqueue work',()=>{
 const s=prepared(),a=preview(req(),s),b=preview(req(),s);
 assert.deepEqual(a,b);assert.equal(s.writes(),1);
});
test('unrecognized token cannot trigger',()=>assert.equal(preview(req({token:'go'}),prepared()).state,'HOLD_NOT_NOD'));
test('missing WorkID held',()=>assert.equal(preview(req({work_id:''}),prepared()).state,'HOLD_UNBOUND_WORKID'));
test('foreign WorkID held',()=>assert.equal(preview(req({work_id:'other'}),prepared()).state,'HOLD_UNBOUND_WORKID'));
test('no durable record held',()=>assert.equal(preview(req(),storage()).state,'HOLD_NO_VERIFIED_LOCAL_WORK'));
test('revoked record held',()=>{const s=prepared();owned.revoke(s);assert.equal(preview(req(),s).state,'HOLD_REVOKED');});
test('forged ACK in stored record held',()=>{
 const s=prepared(),row=JSON.parse(s.getRaw(owned.STORAGE_KEY));
 row.receiver_ack=true;s.setRaw(owned.STORAGE_KEY,JSON.stringify(row));
 assert.equal(preview(req(),s).state,'HOLD_NO_VERIFIED_LOCAL_WORK');
});
test('fake latest source label held',()=>assert.equal(preview(req({source_hint:'latest'}),prepared()).state,'HOLD_SOURCE_CONFLICT'));
test('matching hint cannot assert independent source verification',()=>{
 const out=preview(req({source_hint:fixed.source_ref}),prepared());
 assert.equal(out.state,'PREVIEW_ONLY_BROWSER_LOCAL');
 assert.equal(out.source_verified,false);
});
test('saturated pressure proposes handoff without starting worker',()=>{
 const s=prepared(),out=preview(req({pressure:'SATURATED'}),s);
 assert.equal(out.proposed_action,'PREVIEW_LOCAL_CHECKPOINT_AND_STOP');
 assert.equal(out.effects.jobs_enqueued,0);assert.equal(s.writes(),1);
});
test('unknown pressure yields only safe preview',()=>{
 const out=preview(req({pressure:'UNKNOWN'}),prepared());
 assert.equal(out.proposed_action,'PREVIEW_ONE_SAFE_NEXT_DEED');
 assert.equal(out.real_session_recovery,false);
});
test('absent user cannot imply apostrophe',()=>assert.equal(preview(req({presence:'ABSENT'}),prepared()).state,'HOLD_NOT_EXPLICIT'));
test('unverified wear sensor cannot trigger',()=>assert.equal(preview(req({origin:'IN_EAR_SENSOR'}),prepared()).state,'HOLD_NOT_EXPLICIT'));
test('private scope is not delegated',()=>assert.equal(preview(req({scope:'PRIVATE'}),prepared()).state,'HOLD_AUTHORITY'));
test('execution intent is not preview authority',()=>assert.equal(preview(req({effect:'RUN_ALL'}),prepared()).state,'HOLD_AUTHORITY'));
test('unknown admin field is rejected',()=>assert.equal(preview(req({admin:true}),prepared()).state,'HOLD_INVALID_REQUEST'));
test('null request held',()=>assert.equal(preview(null,prepared()).state,'HOLD_INVALID_REQUEST'));
test('missing receiver held without writing',()=>assert.equal(preview(req(),null).state,'HOLD_NO_VERIFIED_LOCAL_WORK'));
test('unknown pressure is not silently defaulted',()=>assert.equal(preview(req({pressure:'FOREVER'}),prepared()).state,'HOLD_PRESSURE_UNKNOWN'));
