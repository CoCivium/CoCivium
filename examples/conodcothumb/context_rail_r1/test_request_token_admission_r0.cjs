'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {SCHEMA,gate,digest,bytes}=require('./CoRequestTokenAdmissionR0.cjs');
const S='DO_NOT_ECHO_PRIVATE_MODEL_PROMPT_592334';
const request=(s='public relevant source')=>JSON.stringify({model:'verified-model-id',max_output_tokens:1024,input:[{role:'user',content:s}]});
function scenario(over={}){
  const raw=request();
  const count_receipt={method:'PROVIDER_FULL_REQUEST_COUNT',scope:'FULL_REQUEST',request_sha256:digest(raw),request_bytes:bytes(raw),model_id:'verified-model-id',input_tokens:1000,observed_at_utc:'2026-10-25T07:00:00Z'};
  const target={model_id:'verified-model-id',context_window_tokens:4096,reserved_output_tokens:1024,reserved_guard_tokens:256};
  return {request_json:raw,target,count_receipt,observed_at_utc:'2026-10-25T07:00:01Z',maximum_count_age_seconds:60,...over};
}
const rejected=(o,pattern)=>assert.throws(()=>gate(o),pattern);
const noEffects=o=>{
  assert.equal(o.model_call_authorized,false);
  assert.equal(o.receiver_ack,false);
  assert.equal(o.authority,'NONE');
  assert.deepEqual(o.effects,{network:0,model:0,file:0,clipboard:0,device:0,send:0,workers:0});
};
test('schema and no effects',()=>{const x=gate(scenario());assert.equal(x.schema,SCHEMA);noEffects(x)});
test('declared full count is not trusted provider verification',()=>{const x=gate(scenario());assert.equal(x.state,'SHADOW_FITS_DECLARED_PROVIDER_COUNT__AUTH_UNVERIFIED');assert.equal(x.count_evidence_origin,'UNVERIFIED_BY_THIS_GUARD')});
test('input ceiling reserves output and guard',()=>{const x=gate(scenario());assert.equal(x.input_ceiling_tokens,2816);assert.equal(x.available_headroom_tokens,1816)});
test('missing receipt is held',()=>{const x=gate(scenario({count_receipt:null}));assert.equal(x.state,'HELD_COUNT_UNAVAILABLE');noEffects(x)});
test('unknown model is denied',()=>rejected(scenario({target:{...scenario().target,model_id:'bad model name'}}),/INVALID_MODEL_ID/));
test('changed request digest held',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,request_sha256:'sha256:'+'f'.repeat(64)}}));assert.equal(x.state,'HELD_COUNT_REQUEST_DIGEST_MISMATCH')});
test('changed count-model ID held',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,model_id:'other-model'}}));assert.equal(x.state,'HELD_COUNT_MODEL_MISMATCH')});
test('changed byte claim held',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,request_bytes:666}}));assert.equal(x.state,'HELD_COUNT_BYTES_MISMATCH')});
test('changed intended request model rejected',()=>{let x=scenario();x.request_json=JSON.stringify({model:'other-model',input:'hi'});rejected(x,/MISMATCH_REQUEST_MODEL/)});
test('stale count held',()=>{const x=gate(scenario({observed_at_utc:'2026-10-25T07:15:00Z'}));assert.equal(x.state,'HELD_STALE_OR_FUTURE_COUNT')});
test('future dated count held',()=>{const x=gate(scenario({observed_at_utc:'2026-10-25T06:59:00Z'}));assert.equal(x.state,'HELD_STALE_OR_FUTURE_COUNT')});
test('same-time count bound accepted as shadow',()=>{const x=gate(scenario({observed_at_utc:'2026-10-25T07:00:00Z'}));assert.match(x.state,/SHADOW_FITS_DECLARED/)});
test('input over available ceiling held',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,input_tokens:2817}}));assert.equal(x.state,'HELD_INPUT_PLUS_OUTPUT_RESERVE_EXCEEDS_CONTEXT')});
test('exact ceiling fit still shadow only',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,input_tokens:2816}}));assert.equal(x.available_headroom_tokens,0);noEffects(x)});
test('local text tokenizer cannot admit full request',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,method:'LOCAL_TEXT_TOKENIZER',scope:'TEXT_ONLY'}}));assert.equal(x.state,'HELD_TEXT_ONLY_COUNT_CANNOT_ADMIT_FULL_REQUEST')});
test('provider text-only count also held',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,scope:'TEXT_ONLY'}}));assert.equal(x.state,'HELD_TEXT_ONLY_COUNT_CANNOT_ADMIT_FULL_REQUEST')});
test('synthetic full count never treated as provider',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,method:'SYNTHETIC_FIXTURE'}}));assert.equal(x.state,'SHADOW_FIXTURE_FITS_MATH_ONLY')});
test('synthetic over limit still held',()=>{const x=gate(scenario({count_receipt:{...scenario().count_receipt,method:'SYNTHETIC_FIXTURE',input_tokens:3000}}));assert.equal(x.state,'HELD_INPUT_PLUS_OUTPUT_RESERVE_EXCEEDS_CONTEXT')});
test('unknown counting method is denied',()=>rejected(scenario({count_receipt:{...scenario().count_receipt,method:'MAGIC_INFINITY'}}),/INVALID_COUNT_METHOD/));
test('unknown scope is denied',()=>rejected(scenario({count_receipt:{...scenario().count_receipt,scope:'UNBOUNDED'}}),/INVALID_COUNT_SCOPE/));
test('fractional count rejected',()=>rejected(scenario({count_receipt:{...scenario().count_receipt,input_tokens:14.5}}),/INVALID_INPUT_TOKEN_COUNT/));
test('negative count rejected',()=>rejected(scenario({count_receipt:{...scenario().count_receipt,input_tokens:-5}}),/INVALID_INPUT_TOKEN_COUNT/));
test('zero output reserve rejected',()=>rejected(scenario({target:{...scenario().target,reserved_output_tokens:0}}),/INVALID_OUTPUT_RESERVE/));
test('zero guard reserve rejected',()=>rejected(scenario({target:{...scenario().target,reserved_guard_tokens:0}}),/INVALID_GUARD_RESERVE/));
test('reserves exhaust window rejected',()=>{const o=scenario();o.target.reserved_output_tokens=4000;o.target.reserved_guard_tokens=128;o.request_json=JSON.stringify({model:'verified-model-id',input:'hi',max_output_tokens:4000});rejected(o,/RESERVES_EXHAUST_CONTEXT_WINDOW/)});
test('missing request output cap rejected',()=>{let x=scenario();x.request_json=JSON.stringify({model:'verified-model-id',input:'hi'});rejected(x,/INVALID_REQUEST_MAX_OUTPUT_TOKENS/)});
test('reserve must match actual model request output cap',()=>{let x=scenario();x.request_json=JSON.stringify({model:'verified-model-id',input:'hi',max_output_tokens:1500});rejected(x,/MISMATCH_REQUEST_OUTPUT_RESERVE/)});
test('empty input rejected',()=>{let x=scenario();x.request_json=JSON.stringify({model:'verified-model-id',input:[],max_output_tokens:1024});rejected(x,/INVALID_FULL_REQUEST_SHAPE/)});
test('zero token count not accepted as provider full input',()=>rejected(scenario({count_receipt:{...scenario().count_receipt,input_tokens:0}}),/INVALID_INPUT_TOKEN_COUNT/));
test('missing request input rejected',()=>{const x=scenario();x.request_json=JSON.stringify({model:'verified-model-id'});rejected(x,/INVALID_FULL_REQUEST_SHAPE/)});
test('malformed JSON rejected without echo',()=>{const x=scenario();x.request_json='{';rejected(x,/INVALID_REQUEST_JSON/)});
test('oversized request rejected',()=>{const x=scenario();x.request_json='a'.repeat(262145);rejected(x,/INVALID_OR_OVERSIZED_REQUEST_JSON/)});
test('wrong now format rejected',()=>rejected(scenario({observed_at_utc:'tomorrow'}),/INVALID_OBSERVATION_TIME/));
test('impossible day rejected',()=>rejected(scenario({observed_at_utc:'2026-02-30T07:00:01Z'}),/INVALID_OBSERVATION_TIME/));
test('count stale boundary inclusive',()=>{const x=gate(scenario({observed_at_utc:'2026-10-25T07:01:00Z'}));assert.match(x.state,/SHADOW_FITS/)});
test('TTL above one hour rejected',()=>rejected(scenario({maximum_count_age_seconds:3601}),/INVALID_COUNT_TTL/));
test('request text is never echoed even under successful shadow',()=>{
  const raw=request(S),t=scenario();t.request_json=raw;t.count_receipt={...t.count_receipt,request_sha256:digest(raw),request_bytes:bytes(raw)};
  const s=JSON.stringify(gate(t));assert(!s.includes(S));assert(!s.includes('role'));noEffects(gate(t));
});
test('UTF8 digest computed over exact serialized request',()=>{
  const raw=request('∞ ↔ CoOmni 关系');const t=scenario();t.request_json=raw;t.count_receipt={...t.count_receipt,request_sha256:digest(raw),request_bytes:bytes(raw)};
  const x=gate(t);assert.equal(x.request_bytes,Buffer.byteLength(raw,'utf8'));assert.match(x.state,/SHADOW_FITS/);
});
test('stdin real child process matches direct adapter',()=>{
  const o=scenario();const p=spawnSync(process.execPath,[require.resolve('./CoRequestTokenAdmissionR0.cjs')],{encoding:'utf8',input:JSON.stringify(o)});
  assert.equal(p.status,0);assert.deepEqual(JSON.parse(p.stdout),gate(o));assert.equal(p.stderr,'');
});
test('stdin malformed private content not echoed',()=>{
  const p=spawnSync(process.execPath,[require.resolve('./CoRequestTokenAdmissionR0.cjs')],{encoding:'utf8',input:'{'+S});
  assert.equal(p.status,2);assert.equal(p.stdout,'');assert(!p.stderr.includes(S));
});
test('stdin non-enrolled method does not emit packet',()=>{
  const o=scenario();o.count_receipt.method='UNLIMITED_AI';const p=spawnSync(process.execPath,[require.resolve('./CoRequestTokenAdmissionR0.cjs')],{encoding:'utf8',input:JSON.stringify(o)});
  assert.equal(p.status,2);assert.equal(p.stdout,'');assert.match(p.stderr,/INVALID_COUNT_METHOD/);
});
test('same raw request produces identical digest and decision',()=>{
  const o=scenario();assert.deepEqual(gate(o),gate(o));assert.equal(digest(o.request_json),digest(o.request_json));
});
test('false infinity vocabulary never authorizes execution',()=>{const o=scenario();o.target.model_id='verified-model-id';const x=gate(o);assert(!x.nonclaims.some(s=>s==='UNLIMITED_TOKENS_PROVEN'));noEffects(x)});