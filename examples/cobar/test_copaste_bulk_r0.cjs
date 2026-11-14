// Synthetic contract checks. A fake text field is not a browser, OS clipboard, or provider chat.
'use strict';
const assert=require('node:assert/strict');
const {createCoPasteR0}=require('./copaste_bulk_r0.cjs');
let passed=0;
const test=(name,fn)=>{fn();passed++;console.log('PASS_COPASTE_R0 '+name)};
function own(initial='') {
  const doc={activeElement:null};let calls=0;let sends=0;let keys=0;
  const field={id:'copaste-local-test',tagName:'TEXTAREA',type:'text',dataset:{copasteOwned:'true'},
    ownerDocument:doc,value:initial,selectionStart:initial.length,selectionEnd:initial.length,maxLength:300000,
    disabled:false,readOnly:false,
    setRangeText(text,start,end){calls++;this.value=this.value.slice(0,start)+text+this.value.slice(end);this.selectionStart=this.selectionEnd=start+text.length;},
    submit(){sends++;},keydown(){keys++;}
  };doc.activeElement=field;
  return {field,doc,get calls(){return calls},get sends(){return sends},get keys(){return keys}};
}
function perform(engine,obj,payload='abc',requestId='req-1') {
  return engine.insert({target:obj.field,expectedTargetId:'copaste-local-test',requestId,payload,authorized:true,expectedValue:obj.field.value});
}
test('one bulk operation, no send or keystrokes',()=>{
  const a=own(),e=createCoPasteR0();const r=perform(e,a,'abc');
  assert.equal(r.state,'INSERTED_VERIFIED_TEXT_VALUE');assert.equal(a.field.value,'abc');
  assert.equal(a.calls,1);assert.equal(a.sends,0);assert.equal(a.keys,0);
});
test('CRLF and Unicode kept exact',()=>{
  const a=own(),e=createCoPasteR0();const s='first\r\nsecond\nthird\u0301 🌍 𝄞';
  assert.equal(perform(e,a,s).state,'INSERTED_VERIFIED_TEXT_VALUE');assert.equal(a.field.value,s);
});
test('100k code unit multiline inserted in one call',()=>{
  const a=own(),e=createCoPasteR0();const s=('line\r\n🌍').repeat(12000);
  assert.equal(perform(e,a,s).state,'INSERTED_VERIFIED_TEXT_VALUE');assert.equal(a.field.value,s);
  assert.equal(a.calls,1);
});
test('requires granted authority',()=>{
  const a=own(),e=createCoPasteR0();
  assert.equal(e.insert({target:a.field,expectedTargetId:a.field.id,requestId:'x',payload:'a',expectedValue:'',authorized:false}).state,'HELD_NOT_AUTHORIZED');assert.equal(a.calls,0);
});
test('wrong target identity held',()=>{
  const a=own(),e=createCoPasteR0();assert.equal(e.insert({target:a.field,expectedTargetId:'not-this',requestId:'a',payload:'a',expectedValue:'',authorized:true}).state,'HELD_WRONG_TARGET');assert.equal(a.calls,0);
});
test('not owned field held',()=>{
  const a=own(),e=createCoPasteR0();a.field.dataset.copasteOwned='false';
  assert.equal(perform(e,a).state,'HELD_TARGET_NOT_OWNED');assert.equal(a.calls,0);
});
test('focus mismatch held',()=>{
  const a=own(),e=createCoPasteR0();a.doc.activeElement={id:'other'};
  assert.equal(perform(e,a).state,'HELD_FOCUS_CHANGED');assert.equal(a.calls,0);
});
test('prestate compare-and-swap holds',()=>{
  const a=own('human'),e=createCoPasteR0();assert.equal(e.insert({target:a.field,expectedTargetId:a.field.id,requestId:'x',payload:'a',expectedValue:'old',authorized:true}).state,'HELD_PRESTATE_CHANGED');assert.equal(a.calls,0);
});
test('same request does not duplicate insertion',()=>{
  const a=own(),e=createCoPasteR0();perform(e,a);
  assert.equal(perform(e,a).state,'DUPLICATE_SUPPRESSED');assert.equal(a.calls,1);
});
test('same request, different payload held',()=>{
  const a=own(),e=createCoPasteR0();perform(e,a);
  assert.equal(perform(e,a,'other').state,'HELD_REQUEST_CONFLICT');assert.equal(a.calls,1);
});
test('human change after insert prevents unverified replay',()=>{
  const a=own(),e=createCoPasteR0();perform(e,a);a.field.value+='human';
  assert.equal(perform(e,a).state,'HELD_DESTINATION_CHANGED');assert.equal(a.calls,1);
});
test('selection replacement retains surrounding text',()=>{
  const a=own('left___right'),e=createCoPasteR0();a.field.selectionStart=4;a.field.selectionEnd=7;
  assert.equal(perform(e,a,'[middle]').state,'INSERTED_VERIFIED_TEXT_VALUE');assert.equal(a.field.value,'left[middle]right');
});
test('max length held before any insertion',()=>{
  const a=own(),e=createCoPasteR0();a.field.maxLength=2;
  assert.equal(perform(e,a,'three').state,'HELD_LENGTH');assert.equal(a.calls,0);
});
test('oversize payload held',()=>{
  const a=own(),e=createCoPasteR0({maxCodeUnits:10});
  assert.equal(perform(e,a,'x'.repeat(11)).state,'HELD_PAYLOAD');assert.equal(a.calls,0);
});
test('partial write is not retried or declared verified',()=>{
  const a=own(),e=createCoPasteR0();a.field.setRangeText=function(text){this.value=text.slice(0,1);};
  assert.equal(perform(e,a,'many').state,'HELD_READBACK_MISMATCH');assert.equal(a.field.value,'m');
});
test('exception is held without blind retry',()=>{
  const a=own(),e=createCoPasteR0();a.field.setRangeText=()=>{throw Error('fault')};
  assert.equal(perform(e,a).state,'FAILED_INSERT_EXCEPTION');
});
test('undo exact last insertion is one owned operation',()=>{
  const a=own('prefix'),e=createCoPasteR0();perform(e,a,'added');
  const r=e.undo({target:a.field,expectedTargetId:a.field.id,requestId:'req-1',authorized:true});
  assert.equal(r.state,'UNDO_VERIFIED_TEXT_VALUE');assert.equal(a.field.value,'prefix');assert.equal(a.calls,2);
});
test('undo refuses to clobber concurrent human edits',()=>{
  const a=own(),e=createCoPasteR0();perform(e,a,'added');a.field.value+='human';
  assert.equal(e.undo({target:a.field,expectedTargetId:a.field.id,requestId:'req-1',authorized:true}).state,'HELD_DESTINATION_CHANGED');assert.equal(a.calls,1);
});
test('input type password and read-only are forbidden',()=>{
  const a=own(),e=createCoPasteR0();a.field.tagName='INPUT';a.field.type='password';assert.equal(perform(e,a).state,'HELD_UNSUPPORTED_TARGET');
  a.field.tagName='TEXTAREA';a.field.readOnly=true;assert.equal(perform(e,a).state,'HELD_READ_ONLY');
});
test('input and clipboard do not leak to external endpoints',()=>{
  const a=own(),e=createCoPasteR0();const r=perform(e,a,'sensitive synthetic');
  assert.equal(r.sent,false);assert(!('payload' in r));assert.equal(a.sends,0);assert.equal(a.keys,0);
});
assert.equal(passed,20);
console.log('PASS_COPASTE_BULK_R0_CONTRACT tests='+passed+' external_sends=0 clipboard_mutations=0 receiver_ack=UNPROVEN');
