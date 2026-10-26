'use strict';
/* CoContextRail / CoOmni R0: pure, fail-closed FULL-REQUEST token-count gate.
 * No provider/API invocation. No source or token count is independently verified.
 * A caller-owned authenticated adapter must count the EXACT proposed model request,
 * bind the full request digest, and authorize any actual call separately.
 */
const crypto = require('node:crypto');
const SCHEMA = 'CoAll.CoContextWare.RequestTokenAdmission.R0';
const NONCLAIMS = Object.freeze([
  'DECLARED_TOKEN_COUNT_NE_INDEPENDENT_PROVIDER_PROOF',
  'COUNT_FOR_FULL_REQUEST_NE_TEXT_ONLY_COUNT',
  'TOKEN_WINDOW_METADATA_NE_CURRENT_MODEL_LIMIT_VERIFIED',
  'FITS_MATH_NE_PERMISSION_TO_CALL_MODEL',
  'VALID_INPUT_COUNT_NE_OUTPUT_RESERVATION_PROOF',
  'BYTE_BUDGET_NE_TOKEN_BUDGET',
  'CONTEXT_PACKET_NE_COMPLETE_SOURCE',
  'TOKEN_SAVINGS_NE_INFINITE_CONTEXT',
  'TOKEN_COUNT_RECEIPT_NE_RECEIVER_ACK'
]);
const EFFECTS = Object.freeze({network:0,model:0,file:0,clipboard:0,device:0,send:0,workers:0});
const digest = text => 'sha256:'+crypto.createHash('sha256').update(text,'utf8').digest('hex');
const bytes = text => Buffer.byteLength(text,'utf8');
function deny(code){throw new Error(code)}
function integer(value,min,max,code){if(!Number.isSafeInteger(value)||value<min||value>max)deny(code);return value}
function isoUtc(value,code){
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/.test(value))deny(code);
  const ms=Date.parse(value);if(!Number.isFinite(ms)||new Date(ms).toISOString().slice(0,19)!==value.slice(0,19))deny(code);
  return ms;
}
function modelId(value){if(typeof value!=='string'||!/^[A-Za-z0-9][A-Za-z0-9._:/-]{0,95}$/.test(value))deny('INVALID_MODEL_ID');return value;}
function gate(input){
  if(!input||typeof input!=='object'||Array.isArray(input))deny('INVALID_INPUT');
  const s=input.request_json;
  if(typeof s!=='string'||!s.trim()||bytes(s)>262144)deny('INVALID_OR_OVERSIZED_REQUEST_JSON');
  let payload;
  try{payload=JSON.parse(s)}catch(_){deny('INVALID_REQUEST_JSON')}
  if(!payload||typeof payload!=='object'||Array.isArray(payload)||!Object.hasOwn(payload,'input')||!(typeof payload.input==='string'&&payload.input.trim()||Array.isArray(payload.input)&&payload.input.length>0))deny('INVALID_FULL_REQUEST_SHAPE');
  const target=input.target;
  if(!target||typeof target!=='object'||Array.isArray(target))deny('INVALID_TARGET');
  const model=modelId(target.model_id);
  if(payload.model!==model)deny('MISMATCH_REQUEST_MODEL');
  const window=integer(target.context_window_tokens,1024,4000000,'INVALID_CONTEXT_WINDOW');
  const outputReserve=integer(target.reserved_output_tokens,1,window,'INVALID_OUTPUT_RESERVE');
  const requestedOutput=integer(payload.max_output_tokens,1,window,'INVALID_REQUEST_MAX_OUTPUT_TOKENS');
  if(requestedOutput!==outputReserve)deny('MISMATCH_REQUEST_OUTPUT_RESERVE');
  const guardReserve=integer(target.reserved_guard_tokens,128,window,'INVALID_GUARD_RESERVE');
  if(outputReserve+guardReserve>=window)deny('RESERVES_EXHAUST_CONTEXT_WINDOW');
  const now=isoUtc(input.observed_at_utc,'INVALID_OBSERVATION_TIME');
  const ttl=integer(input.maximum_count_age_seconds,1,3600,'INVALID_COUNT_TTL');
  const rawDigest=digest(s);
  const size=bytes(s);
  const evidence=input.count_receipt;
  const summary={
    schema:SCHEMA, state:'HELD_COUNT_UNAVAILABLE',model_id:model,
    request_sha256:rawDigest, request_bytes:size,
    count_source:'NONE', measurement_scope:'UNKNOWN',
    input_tokens:null, context_window_tokens:window,
    reserved_output_tokens:outputReserve,reserved_guard_tokens:guardReserve,
    input_ceiling_tokens:window-outputReserve-guardReserve,
    available_headroom_tokens:null,
    count_evidence_origin:'UNVERIFIED_BY_THIS_GUARD',
    target_window_origin:'CALLER_DECLARED_UNVERIFIED',
    receiver_ack:false, model_call_authorized:false,
    authority:'NONE',effects:{...EFFECTS},nonclaims:[...NONCLAIMS]
  };
  if(evidence===null||evidence===undefined)return summary;
  if(!evidence||typeof evidence!=='object'||Array.isArray(evidence))deny('INVALID_COUNT_RECEIPT');
  const method=evidence.method;
  if(!['PROVIDER_FULL_REQUEST_COUNT','LOCAL_TEXT_TOKENIZER','SYNTHETIC_FIXTURE'].includes(method))deny('INVALID_COUNT_METHOD');
  const scope=evidence.scope;
  if(!['FULL_REQUEST','TEXT_ONLY'].includes(scope))deny('INVALID_COUNT_SCOPE');
  const count=integer(evidence.input_tokens,1,4000000,'INVALID_INPUT_TOKEN_COUNT');
  summary.count_source=method;
  summary.measurement_scope=scope;
  summary.input_tokens=count;
  if(evidence.request_sha256!==rawDigest){summary.state='HELD_COUNT_REQUEST_DIGEST_MISMATCH';return summary}
  if(evidence.model_id!==model){summary.state='HELD_COUNT_MODEL_MISMATCH';return summary}
  if(evidence.request_bytes!==size){summary.state='HELD_COUNT_BYTES_MISMATCH';return summary}
  const when=isoUtc(evidence.observed_at_utc,'INVALID_COUNT_OBSERVATION_TIME');
  if(when>now+1000||now-when>ttl*1000){summary.state='HELD_STALE_OR_FUTURE_COUNT';return summary}
  if(scope!=='FULL_REQUEST'||method==='LOCAL_TEXT_TOKENIZER'){
    summary.state='HELD_TEXT_ONLY_COUNT_CANNOT_ADMIT_FULL_REQUEST';
    return summary;
  }
  summary.available_headroom_tokens=summary.input_ceiling_tokens-count;
  if(count>summary.input_ceiling_tokens){summary.state='HELD_INPUT_PLUS_OUTPUT_RESERVE_EXCEEDS_CONTEXT';return summary}
  if(method==='SYNTHETIC_FIXTURE'){
    summary.state='SHADOW_FIXTURE_FITS_MATH_ONLY';
    return summary;
  }
  summary.state='SHADOW_FITS_DECLARED_PROVIDER_COUNT__AUTH_UNVERIFIED';
  return summary;
}
module.exports=Object.freeze({SCHEMA,gate,digest,bytes});
if(require.main===module){
  const chunks=[];let seen=0;
  process.stdin.on('data',chunk=>{
    seen+=chunk.length;
    if(seen>524288){process.stderr.write('BLOCKED_INPUT_TOO_LARGE\n');process.exit(2)}
    chunks.push(chunk);
  });
  process.stdin.on('end',()=>{
    try{
      const input=JSON.parse(Buffer.concat(chunks).toString('utf8'));
      const result=gate(input);
      process.stdout.write(JSON.stringify(result)+'\n');
    }catch(err){
      // Error codes are static; never echo a request, source, prompt or token data.
      process.stderr.write('HELD_TOKEN_ADMISSION: '+(/^[A-Z0-9_]+$/.test(err.message)?err.message:'INVALID_INPUT')+'\n');
      process.exitCode=2;
    }
  });
}