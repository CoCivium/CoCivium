#!/usr/bin/env node
// CoOmni+ ContextCompiler R0: offline, exact-source, zero-effect shadow canary.
// Token/model capacity is NOT expanded; packet budgets are exact UTF-8 bytes.
import { createHash } from 'node:crypto';

export const SCHEMA = 'CoCivium.CoOmniContextPacket.R0';
export const SOURCE_SCHEMA = 'CoCivium.CoOmniSource.R0';
const ROLES = new Set(['OBSERVATION','PRIOR','POLICY','PROPOSAL','TEST','CHALLENGE']);
const SCOPES = new Set(['PUBLIC','LOCAL','SENSITIVE','UNKNOWN']);
const WORK_FIELDS = new Set(['work_id','query','receiver','byte_budget','max_items','authority']);
const SOURCE_FIELDS = new Set(['schema','id','text','sha256','role','scope','tags']);
const STOP = new Set(['a','an','the','and','or','at','by','to','on','for','with','in','is','of','be','what','how','can','are','about']);

export function sha256(text) {
  return createHash('sha256').update(text,'utf8').digest('hex');
}
export function byteLength(value) {
  return Buffer.byteLength(typeof value === 'string' ? value : JSON.stringify(value),'utf8');
}
function guard(condition,code) {
  if (!condition) throw new Error(code);
}
function words(text) {
  return new Set((text.toLowerCase().match(/[a-z0-9_]+/g) || []).filter(t=>t.length>1 && !STOP.has(t)));
}
export function verifySource(s) {
  guard(s && typeof s==='object' && !Array.isArray(s),'BAD_SOURCE_OBJECT');
  guard(Object.keys(s).every(k=>SOURCE_FIELDS.has(k)),'UNDECLARED_SOURCE_FIELD');
  guard(s.schema===SOURCE_SCHEMA,'BAD_SOURCE_SCHEMA');
  guard(typeof s.id==='string' && /^[a-z][a-z0-9_.:-]{3,79}$/.test(s.id),'BAD_SOURCE_ID');
  guard(ROLES.has(s.role),'BAD_SOURCE_ROLE');
  guard(SCOPES.has(s.scope),'BAD_SOURCE_SCOPE');
  guard(typeof s.text==='string' && byteLength(s.text)>0 && byteLength(s.text)<=8192,'BAD_SOURCE_TEXT');
  guard(typeof s.sha256==='string' && /^[0-9a-f]{64}$/.test(s.sha256),'BAD_SOURCE_DIGEST');
  guard(s.sha256===sha256(s.text),'SOURCE_HASH_MISMATCH');
  guard(Array.isArray(s.tags) && s.tags.length<=20 &&
        s.tags.every(t=>typeof t==='string' && /^[a-z0-9_-]{2,40}$/.test(t)),'BAD_SOURCE_TAGS');
  return true;
}
export function makeSyntheticSource(id,role,scope,tags,text) {
  return {schema:SOURCE_SCHEMA,id,role,scope,tags,text,sha256:sha256(text)};
}
function visibleTo(source,receiver) {
  return source.scope==='PUBLIC' || (receiver==='LOCAL' && source.scope==='LOCAL');
}
export function scoreSource(source,query) {
  const desired=words(query);
  const sourceWords=words(source.text+' '+source.tags.join(' '));
  let score=0;
  for(const word of desired) if(sourceWords.has(word)) score+=1;
  return score;
}
function verifyWork(w) {
  guard(w && typeof w==='object' && !Array.isArray(w),'BAD_WORK');
  guard(Object.keys(w).every(k=>WORK_FIELDS.has(k)),'UNDECLARED_WORK_FIELD');
  guard(typeof w.work_id==='string' && /^[a-z][a-z0-9_.:-]{5,100}$/.test(w.work_id),'BAD_WORK_ID');
  guard(typeof w.query==='string' && w.query.trim().length>3 && byteLength(w.query)<=256,'BAD_QUERY');
  guard(w.receiver==='PUBLIC' || w.receiver==='LOCAL','BAD_RECEIVER');
  guard(w.authority==='NONE','NO_EFFECT_AUTHORITY');
  guard(Number.isSafeInteger(w.byte_budget) && w.byte_budget>=700 && w.byte_budget<=8192,'BAD_BYTE_BUDGET');
  guard(Number.isSafeInteger(w.max_items) && w.max_items>=1 && w.max_items<=8,'BAD_ITEM_BUDGET');
}
export function compileContext({work,sources}) {
  verifyWork(work);
  guard(Array.isArray(sources) && sources.length<=1000,'BAD_SOURCE_LIBRARY');
  const seen=new Set();
  for(const s of sources){
    verifySource(s);
    guard(!seen.has(s.id),'DUPLICATE_SOURCE_ID');
    seen.add(s.id);
  }
  const visible=sources.filter(s=>visibleTo(s,work.receiver));
  const eligible=visible.map(s=>({s,score:scoreSource(s,work.query)}))
    .filter(row=>row.score>0).sort((a,b)=>b.score-a.score || a.s.id.localeCompare(b.s.id));
  guard(eligible.length>0,'HELD_NO_RELEVANT_PUBLIC_OR_LOCAL_SOURCE');
  // Preserve a material contradictory source even when its lexical rank is lower.
  const challenger=eligible.find(row=>row.s.role==='CHALLENGE');
  const order=challenger?[challenger,...eligible.filter(row=>row!==challenger)]:eligible;
  const packet={
    schema:SCHEMA,work_id:work.work_id,query_sha256:sha256(work.query),
    receiver:work.receiver,authority:'NONE',epistemic_state:'SOURCE_BOUND_SYNTHETIC_PROPOSAL',
    byte_budget:work.byte_budget,source_items:[],selected_count:0,
    omitted_eligible:eligible.length,challenge_state:'NONE_RELEVANT_FOUND',
    effects:{network:0,model:0,device:0,send:0,clipboard:0,workers:0},
    nonclaims:['CONTEXT_NE_MODEL_MEMORY','SUMMARY_NE_SOURCE','SOURCE_HASH_NE_RECEIVER_ACK']
  };
  for(const row of order) {
    if(packet.source_items.length>=work.max_items) break;
    const s=row.s;
    const item={id:s.id,sha256:s.sha256,role:s.role,excerpt:s.text.slice(0,180)};
    const trial={...packet,source_items:[...packet.source_items,item],
      selected_count:packet.source_items.length+1,
      omitted_eligible:eligible.length-packet.source_items.length-1,
      challenge_state:s.role==='CHALLENGE' || packet.source_items.some(x=>x.role==='CHALLENGE')?
        'CHALLENGE_INCLUDED':'NONE_RELEVANT_FOUND'};
    if(byteLength(trial)<=work.byte_budget) Object.assign(packet,trial);
  }
  guard(packet.source_items.length>0,'HELD_CONTEXT_BUDGET_INSUFFICIENT');
  if(challenger) guard(packet.challenge_state==='CHALLENGE_INCLUDED','HELD_CHALLENGE_DID_NOT_FIT');
  guard(byteLength(packet)<=work.byte_budget,'PACKET_BYTE_BUDGET_BREACH');
  return {
    packet,
    packet_sha256:sha256(JSON.stringify(packet)),
    packet_bytes:byteLength(packet),
    available_source_bytes:visible.reduce((a,s)=>a+byteLength(s.text),0),
    model_calls:0,network_calls:0,materialized_workers:0,receiver_ack:null
  };
}
export function rehydrate(result,library,requestedReceiver) {
  guard(result && result.packet && typeof result.packet==='object','BAD_PACKET');
  guard(result.packet.schema===SCHEMA,'BAD_PACKET_SCHEMA');
  guard(result.packet.authority==='NONE','BAD_PACKET_AUTHORITY');
  guard(result.packet.receiver===requestedReceiver,'RECEIVER_SCOPE_MISMATCH');
  guard(sha256(JSON.stringify(result.packet))===result.packet_sha256,'PACKET_DIGEST_MISMATCH');
  guard(byteLength(result.packet)<=result.packet.byte_budget,'REHYDRATION_BUDGET_BREACH');
  guard(Array.isArray(library) && library.length<=1000,'BAD_SOURCE_LIBRARY');
  const byId=new Map();
  for(const s of library){
    verifySource(s);
    guard(!byId.has(s.id),'DUPLICATE_SOURCE_ID');
    byId.set(s.id,s);
  }
  const recovered=[];
  for(const ref of result.packet.source_items){
    const s=byId.get(ref.id);
    guard(!!s,'SOURCE_MISSING_AT_RECEIVER');
    guard(visibleTo(s,requestedReceiver),'REHYDRATION_SCOPE_VIOLATION');
    guard(s.sha256===ref.sha256 && s.text.startsWith(ref.excerpt),'REHYDRATION_SOURCE_CHANGED');
    recovered.push({id:s.id,sha256:s.sha256,role:s.role,exact_text:s.text});
  }
  return {work_id:result.packet.work_id,receiver:requestedReceiver,restored:recovered,
    exact_reconstruction:true,effects:{network:0,model:0,send:0},authority:'NONE'};
}
