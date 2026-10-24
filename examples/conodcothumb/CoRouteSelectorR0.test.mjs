import test from 'node:test';
import assert from 'node:assert/strict';
import { chooseRoute,INLINE_LIMIT,R0_LIMIT,R1_DEFAULT_LIMIT,R1_HARD_LIMIT } from './CoRouteSelectorR0.mjs';
test('small text stays inline',()=>assert.equal(chooseRoute({byte_count:80}).lane,'SMALL_INLINE'));
test('inline limit is stable',()=>assert.equal(chooseRoute({byte_count:INLINE_LIMIT}).lane,'SMALL_INLINE'));
test('first file-backed byte elects R0',()=>assert.equal(chooseRoute({byte_count:INLINE_LIMIT+1}).lane,'EXPLICIT_FILE_BACKED_R0'));
test('R0 boundary honored',()=>assert.equal(chooseRoute({byte_count:R0_LIMIT}).lane,'EXPLICIT_FILE_BACKED_R0'));
test('largest path uses R1 chunking',()=>assert.equal(chooseRoute({byte_count:600*1024**2}).lane,'EXPLICIT_CHUNKED_R1'));
test('R1 standard ceiling honored',()=>assert.equal(chooseRoute({byte_count:R1_DEFAULT_LIMIT}).lane,'EXPLICIT_CHUNKED_R1'));
test('above R1 standard cap held absent extra budget',()=>assert.equal(chooseRoute({byte_count:R1_DEFAULT_LIMIT+1}).status,'HOLD_RESOURCE_BUDGET'));
test('explicit 64GiB band is proposed but not executed',()=>assert.equal(chooseRoute({byte_count:R1_HARD_LIMIT,explicit_extended:true}).lane,'EXTENDED_CHUNKED_R1'));
test('even opt-in cannot exceed hard cap',()=>assert.equal(chooseRoute({byte_count:R1_HARD_LIMIT+1,explicit_extended:true}).status,'HOLD_RESOURCE_BUDGET'));
test('private and invalid objects fail closed',()=>{
 assert.equal(chooseRoute({byte_count:5,sensitive:true}).status,'HOLD_PRIVACY');
 assert.equal(chooseRoute({byte_count:-1}).status,'HOLD_INVALID_SIZE');
 assert.equal(chooseRoute({byte_count:'500'}).status,'HOLD_INVALID_SIZE');
});
test('route election never grants external authority',()=>{
 const a=chooseRoute({byte_count:800000000});
 assert.equal(a.external_actions,0);assert.equal(a.consent_scope,'NONE');assert.equal(a.opt_in_required_for_stage,true);
});
