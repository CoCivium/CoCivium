'use strict';
/**
 * CoContextRail+ / CoContextWare+: explicit-source bounded context-packet canary.
 * No filesystem scanning, network, model, mouse, clipboard or receiver effects.
 * Source digests are caller-declared identities, never claims of verification.
 * Bytes are measured on the FULL serialized packet; tokens are NOT measured.
 */
const crypto = require('node:crypto');
const SCHEMA='CoAll.CoContextWare.BoundedPacket.R0';
const STATUSES=new Set(['PASS','FAIL','FAIL_SCOPED','HELD','UNKNOWN','PASS_PUBLICATION_ONLY','HYPOTHESIS']);
const PRIVACY=new Set(['PUBLIC','PRIVATE_LOCAL','SENSITIVE','UNKNOWN']);
const NONCLAIMS=[
  'BYTE_BUDGET_NE_TOKEN_BUDGET',
  'DECLARED_HASH_NE_SOURCE_READPROOF',
  'COMPRESSED_PACKET_NE_COMPLETE_SOURCE',
  'RANKING_NE_TRUTH',
  'FILE_OR_POINTER_NE_RECEIVER_ACK',
  'VIRTUAL_SESSION_NE_LIVE_PROVIDER_SESSION',
  'LOGICAL_CAPACITY_NE_UNBOUNDED_COMPUTE'
];
const EFFECTS=Object.freeze({network:0,model:0,file:0,clipboard:0,device:0,send:0,workers:0});
const byteLength=s=>Buffer.byteLength(s,'utf8');
const sha256=s=>crypto.createHash('sha256').update(s,'utf8').digest('hex');
const tokens=s=>new Set((s.toLowerCase().match(/[\p{L}\p{N}]{2,}/gu)||[]).filter(x=>!new Set(['and','the','with','that','into','from','this','when','what','how','why','you','for']).has(x)));
function invalid(m){throw new Error(m);}
function nonblank(s,maxB,label){if(typeof s!=='string'||!s.trim()||byteLength(s)>maxB)invalid('INVALID_'+label);return s;}
function validRow(row){
  if(!row||typeof row!=='object'||Array.isArray(row))invalid('INVALID_ROW');
  nonblank(row.id,96,'ROW_ID');
  nonblank(row.source_ref,512,'SOURCE_REF');
  if(!/^sha256:[a-f0-9]{64}$/.test(row.source_sha256||''))invalid('INVALID_SOURCE_HASH');
  if(!STATUSES.has(row.status))invalid('INVALID_EVIDENCE_STATUS');
  if(!PRIVACY.has(row.privacy))invalid('INVALID_PRIVACY');
  nonblank(row.text,4096,'EXCERPT_TEXT');
  if(!/^\d{4}-\d{2}-\d{2}$/.test(row.observed_date||'')||Number.isNaN(Date.parse(row.observed_date))||new Date(row.observed_date).toISOString().slice(0,10)!==row.observed_date)invalid('INVALID_OBSERVED_DATE');
  if(!['OBSERVED','SOURCE_REPORT','HYPOTHESIS','SIMULATION'].includes(row.epistemic))invalid('INVALID_EPISTEMIC_CLASS');
  return {
    id:row.id,
    source_ref:row.source_ref,
    source_sha256:row.source_sha256,
    excerpt_sha256:'sha256:'+sha256(row.text),
    status:row.status,
    privacy:row.privacy,
    observed_date:row.observed_date,
    epistemic:row.epistemic,
    text:row.text,
    untrusted_source_text:true,
    evidence_readproof:'NOT_CHECKED_IN_THIS_COMPILER'
  };
}
function compile(input){
  if(!input||typeof input!=='object'||Array.isArray(input))invalid('INVALID_INPUT');
  nonblank(input.work_id,96,'WORK_ID');
  const query=nonblank(input.query,1024,'QUERY');
  if(!PRIVACY.has(input.query_privacy))invalid('INVALID_QUERY_PRIVACY');
  if(!['PUBLIC','PRIVATE_LOCAL'].includes(input.output_privacy))invalid('INVALID_OUTPUT_PRIVACY');
  if(input.output_privacy==='PUBLIC'&&input.query_privacy!=='PUBLIC')invalid('HELD_PRIVATE_QUERY_CANNOT_EXPORT_PUBLIC');
  const budget=input.budget_bytes;
  if(!Number.isInteger(budget)||budget<1536||budget>32768)invalid('INVALID_BYTE_BUDGET_1536_32768');
  const max=input.max_items;
  if(!Number.isInteger(max)||max<1||max>16)invalid('INVALID_ITEM_COUNT_1_16');
  if(!Array.isArray(input.candidates)||input.candidates.length>128)invalid('INVALID_CANDIDATE_COUNT');
  const candidates=input.candidates.map(validRow);
  const allowed=[];let excluded=0;
  for(const r of candidates){
    if(r.privacy==='SENSITIVE'||r.privacy==='UNKNOWN'||(input.output_privacy==='PUBLIC'&&r.privacy!=='PUBLIC')){excluded++;continue;}
    allowed.push(r);
  }
  const keys=new Set();const distinct=[];let duplicates=0;
  for(const r of allowed){
    const key=r.source_sha256+'|'+r.excerpt_sha256+'|'+r.status+'|'+r.epistemic;
    if(keys.has(key)){duplicates++;continue;}
    keys.add(key);distinct.push(r);
  }
  const negatives=distinct.filter(r=>r.status==='FAIL'||r.status==='FAIL_SCOPED'||r.status==='HELD');
  const other=distinct.filter(r=>!negatives.includes(r));
  const q=tokens(query);
  const score=r=>{
    const t=tokens(r.text);let hits=0;for(const w of q)if(t.has(w))hits++;
    return hits*20+(r.status==='UNKNOWN'?2:0)+(r.status==='HYPOTHESIS'?1:0);
  };
  other.sort((a,b)=>score(b)-score(a)||a.id.localeCompare(b.id));
  negatives.sort((a,b)=>a.id.localeCompare(b.id));
  const counts={};for(const s of STATUSES)counts[s]=distinct.filter(r=>r.status===s).length;
  const base={schema:SCHEMA,work_id:input.work_id,state:'SHADOW_CONTEXT_ONLY',
    scope:'EXPLICIT_DECLARED_SOURCES_ONLY',output_privacy:input.output_privacy,
    query:'NOT_COPIED_TO_PACKET',budget_bytes:budget,max_items:max,
    total_declared:candidates.length,eligible_unique:distinct.length,
    duplicate_suppressed:duplicates,privacy_exclusions_present:excluded>0,
    status_counts:counts,required_negative_count:negatives.length,
    selected:[],omitted_eligible:0,
    authority:'NONE',receiver_ack:false,effects:{...EFFECTS},
    nonclaims:NONCLAIMS
  };
  const size=obj=>byteLength(JSON.stringify(obj));
  const output=(state,selected)=>({...base,state,selected,omitted_eligible:distinct.length-selected.length});
  let chosen=[];
  if(size(output('SHADOW_CONTEXT_ONLY',chosen))>budget)invalid('HELD_PACKET_METADATA_EXCEEDS_BUDGET');
  for(const r of negatives){
    const next=[...chosen,r];
    if(next.length>max||size(output('SHADOW_CONTEXT_ONLY',next))>budget)
      return output('HELD_REQUIRED_NEGATIVE_EVIDENCE_EXCEEDS_BUDGET',[]);
    chosen=next;
  }
  for(const r of other){
    if(chosen.length>=max)break;
    const next=[...chosen,r];
    if(size(output('SHADOW_CONTEXT_ONLY',next))<=budget)chosen=next;
  }
  const state=excluded>0?'SHADOW_CONTEXT_PARTIAL_PRIVACY':(distinct.length===0?'HELD_NO_ELIGIBLE_SOURCE':'SHADOW_CONTEXT_ONLY');
  const result=output(state,chosen);
  if(size(result)>budget)invalid('INTERNAL_BUDGET_ERROR');
  return result;
}
module.exports=Object.freeze({SCHEMA,compile,byteLength,sha256});

// Explicit JSON stdin handoff. No file/clipboard/network/device access.
if(require.main===module){
  const chunks=[];let bytes=0;let overflow=false;
  process.stdin.on('data',chunk=>{
    bytes+=chunk.length;
    if(bytes>1048576){overflow=true;process.stdin.pause();process.stderr.write('BLOCKED_STDIN_OVER_1MIB\n');process.exitCode=2;return;}
    chunks.push(chunk);
  });
  process.stdin.on('end',()=>{
    if(overflow)return;
    try{
      const input=JSON.parse(Buffer.concat(chunks).toString('utf8'));
      const packet=compile(input);
      process.stdout.write(JSON.stringify(packet)+'\n');
    }catch(e){
      process.stderr.write('BLOCKED_CONTEXT_PACKET: '+String(e.message||'INVALID_INPUT')+'\n');
      process.exitCode=2;
    }
  });
}
