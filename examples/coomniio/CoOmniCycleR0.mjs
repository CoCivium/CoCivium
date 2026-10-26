#!/usr/bin/env node
// CoOmniCycle+ R0: bounded, local, file-backed worker queue.
// Never spawns subprocesses or contacts network services. No model or device privileges.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

export const SCHEMA = 'CoCivium.CoOmniCycle.R0';
export const DEFAULT_LIMITS = Object.freeze({maxTasksPerCycle:4,maxActive:2,maxBytesPerCycle:32*1024**3,maxObjectBytes:16*1024**3,maxManifestFiles:24,maxJsonBytes:5*1024**2});
export const NONCLAIMS = Object.freeze(['LOCAL_IS_NOT_LANDED','VALIDATION_IS_NOT_ACCEPTANCE','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF','NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE','HASHING_IS_NOT_SEMANTIC_INGESTION','DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY','QUEUE_NE_INFINITE_COMPUTE','LOGICAL_TASK_NE_PROVIDER_SESSION','COPY_PLAN_NE_PASTE_NE_SEND','SOURCE_HASH_NE_AUTHORIZED_EFFECT']);
function sha256(bytes){return crypto.createHash('sha256').update(bytes).digest('hex');}
function assert(condition, message){if(!condition)throw Error(message);}
export function validateLimits(input={}){
 const limits={...DEFAULT_LIMITS,...input};
 for(const [key,min,max] of [['maxTasksPerCycle',1,64],['maxActive',1,8],['maxBytesPerCycle',1024,128*1024**3],['maxObjectBytes',1024,64*1024**3],['maxManifestFiles',1,24],['maxJsonBytes',512,16*1024**2]]){
  assert(Number.isSafeInteger(limits[key])&&limits[key]>=min&&limits[key]<=max,`INVALID_LIMIT_${key}`);
 }
 assert(limits.maxObjectBytes<=limits.maxBytesPerCycle,'OBJECT_EXCEEDS_CYCLE_BUDGET');
 return limits;
}
export function validateTask(task){
 assert(task&&typeof task==='object'&&!Array.isArray(task),'TASK_OBJECT_REQUIRED');
 assert(task.schema==='CoCivium.CoOmniCycle.Task.R0','INVALID_TASK_SCHEMA');
 assert(typeof task.id==='string'&&/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$/.test(task.id),'INVALID_TASK_ID');
 assert(['HASH_OBJECT','INSPECT_JSON','COPY_PLAN'].includes(task.kind),'TASK_KIND_NOT_ALLOWED');
 assert(task.authority==='LOCAL_READ_ONLY','NO_EXECUTION_AUTHORITY');
 assert(task.confidentiality==='LOCAL_ONLY','NO_PUBLIC_PAYLOAD');
 assert(task.external_effects===false,'EXTERNAL_EFFECTS_NOT_ALLOWED');
 const files=task.kind==='COPY_PLAN'?task.files:[task.relative_path];
 assert(Array.isArray(files)&&files.length>=1&&files.length<=24,'INVALID_FILE_COUNT');
 assert(files.every(x=>typeof x==='string'&&x.length>0&&x.length<=1024),'INVALID_FILE_REFERENCE');
 for(const p of files){
  assert(!path.isAbsolute(p)&&!path.win32.isAbsolute(p),'ABSOLUTE_PATH_FORBIDDEN');
  assert(!p.includes('\\')&&!p.includes('\0')&&!p.includes(':'),'UNSAFE_PATH_CHAR');
  assert(p.split('/').every(c=>c.length>0&&c!=='.'&&c!=='..'),'PATH_ESCAPE_FORBIDDEN');
 }
 if(task.kind==='COPY_PLAN')assert(files.length<=24,'COPY_PLAN_COUNT_EXCEEDED');
 return {...task,files};
}
export function safeResolve(objectsRoot,relative){
 const root=fs.realpathSync(objectsRoot),guess=path.resolve(root,relative);
 assert(guess.startsWith(root+path.sep),'PATH_ESCAPE_FORBIDDEN');
 const real=fs.realpathSync(guess);
 assert(real.startsWith(root+path.sep),'SYMLINK_ESCAPE_FORBIDDEN');
 const st=fs.statSync(real);
 assert(!fs.lstatSync(guess).isSymbolicLink(),'SYMLINK_FILE_FORBIDDEN');
 assert(st.isFile(),'NOT_A_REGULAR_FILE');
 return {full:real,stat:st};
}
export async function hashStream(file){
 const hasher=crypto.createHash('sha256');let n=0;
 for await(const buf of fs.createReadStream(file,{highWaterMark:1024*1024})){
  n+=buf.length;hasher.update(buf);
 }
 return {sha256:hasher.digest('hex'),bytes:n};
}
function atomicWrite(dest,data){
 const temp=dest+'.tmp.'+process.pid+'.'+crypto.randomBytes(4).toString('hex');
 try {fs.writeFileSync(temp,data,{flag:'wx',mode:0o600});fs.renameSync(temp,dest);}finally{try{fs.unlinkSync(temp);}catch{}}
}
function createOnce(file,data){
 try{fs.writeFileSync(file,data,{flag:'wx',mode:0o600});return true;}
 catch(e){if(e.code==='EEXIST')return false;throw e;}
}
export function init(root){
 const target=path.resolve(root);
 for(const folder of ['objects','inbox','receipts','status'])fs.mkdirSync(path.join(target,folder),{recursive:true,mode:0o700});
 return {root:target,existing_or_created:true};
}
export function submit(root,task){
 init(root);const normalized=validateTask(task);
 const payload=JSON.stringify(task,null,2)+'\n';
 const dest=path.join(root,'inbox',task.id+'.json');
 if(!createOnce(dest,payload)){
  assert(fs.readFileSync(dest,'utf8')===payload,'TASK_ID_COLLISION_HOLD');
  return {status:'ALREADY_PRESENT',task_id:task.id};
 }
 return {status:'TASK_QUEUED',task_id:task.id,kind:normalized.kind};
}
export function readStatus(root){
 const result={schema:SCHEMA,status:'NOT_INITIALIZED',receipt_count:0,pending_count:0,paused:false,active_workers:0,real_provider_sessions_started:0,external_effects:0,nonclaims:NONCLAIMS};
 if(!fs.existsSync(path.join(root,'inbox')))return result;
 const receipts=new Set(fs.readdirSync(path.join(root,'receipts')).filter(x=>x.endsWith('.json')));
 const jobs=fs.readdirSync(path.join(root,'inbox')).filter(x=>x.endsWith('.json'));
 return {...result,status:'LOCAL_QUEUE_ONLY',paused:fs.existsSync(path.join(root,'PAUSE')),receipt_count:receipts.size,pending_count:jobs.filter(x=>!receipts.has(x)).length};
}
export function pause(root){init(root);if(!fs.existsSync(path.join(root,'PAUSE')))fs.writeFileSync(path.join(root,'PAUSE'),'paused by local operator\n',{flag:'wx'});return readStatus(root);}
export function resume(root){init(root);try{fs.unlinkSync(path.join(root,'PAUSE'));}catch(e){if(e.code!=='ENOENT')throw e;}return readStatus(root);}
export async function processTask(root,task,limits,bytesLeft){
 const t=validateTask(task);
 const objectsRoot=path.join(root,'objects');
 assert(t.files.length<=limits.maxManifestFiles,'FILE_SET_CEILING');
 const targets=t.files.map(f=>({rel:f,...safeResolve(objectsRoot,f)}));
 const total=targets.reduce((a,b)=>a+b.stat.size,0);
 assert(Number.isSafeInteger(total)&&total<=bytesLeft,'CYCLE_BYTES_BUDGET');
 assert(targets.every(t=>t.stat.size<=limits.maxObjectBytes),'OBJECT_BYTES_BUDGET');
 if(t.kind==='INSPECT_JSON')assert(total<=limits.maxJsonBytes,'JSON_SIZE_BUDGET');
 const outputs=[];
 for(const file of targets){
  const hashed=await hashStream(file.full);
  const after=fs.statSync(file.full);
  assert(hashed.bytes===file.stat.size&&after.size===file.stat.size&&after.mtimeMs===file.stat.mtimeMs,'SOURCE_CHANGED_DURING_READ');
  const obj={relative_path:file.rel,basename:path.basename(file.rel),...hashed};
  if(t.kind==='INSPECT_JSON'){
   const content=fs.readFileSync(file.full,'utf8');const parsed=JSON.parse(content);
   obj.json_type=Array.isArray(parsed)?'array':typeof parsed;
   obj.json_top_level_keys=parsed&&typeof parsed==='object'&&!Array.isArray(parsed)?Object.keys(parsed).length:null;
  }
  outputs.push(obj);
 }
 return {task_id:t.id,kind:t.kind,source_objects:outputs,source_count:outputs.length,total_bytes:total,
  effect_state:t.kind==='COPY_PLAN'?'PREVIEW_ONLY_NO_CLIPBOARD_OR_PASTE':'LOCAL_READ_ONLY',
  authority:'NONE',external_effects:0,real_workers_spawned:0,receiver:'NONE',lifecycle:'VERIFIED_LOCAL_CANDIDATE'};
}
export async function cycle(root,overrides={}){
 const limits=validateLimits(overrides);init(root);
 const start=new Date().toISOString();const lock=path.join(root,'cycle.lock');
 let lockFD;
 try{lockFD=fs.openSync(lock,'wx',0o600);}catch(e){if(e.code==='EEXIST')return {schema:SCHEMA,status:'HELD_ALREADY_LEASED',processed:0,passed:0,failed:0,nonclaims:NONCLAIMS};throw e;}
 let result;
 try{
  fs.writeSync(lockFD,JSON.stringify({pid:process.pid,hostname:os.hostname(),started_at:start})+'\n');
  if(fs.existsSync(path.join(root,'PAUSE')))result={schema:SCHEMA,status:'PAUSED',processed:0,passed:0,failed:0,nonclaims:NONCLAIMS};
  else{
   const names=fs.readdirSync(path.join(root,'inbox')).filter(x=>x.endsWith('.json')).sort();
   const pending=names.filter(n=>!fs.existsSync(path.join(root,'receipts',n))).slice(0,limits.maxTasksPerCycle);
   let bytesReserved=0,passed=0,failed=0;
   const queue=[];
   for(const fileName of pending){
    const full=path.join(root,'inbox',fileName);const bytes=fs.readFileSync(full);
    let task=null,error=null,reservation=0;
    try{
     assert(bytes.length<=128*1024,'TASK_MANIFEST_TOO_LARGE');
     task=JSON.parse(bytes.toString('utf8'));
     validateTask(task);
     assert(fileName===task.id+'.json','TASK_FILENAME_MISMATCH');
     const files=task.kind==='COPY_PLAN'?task.files:[task.relative_path];
     reservation=files.reduce((n,p)=>n+safeResolve(path.join(root,'objects'),p).stat.size,0);
     assert(reservation<=limits.maxBytesPerCycle-bytesReserved,'CYCLE_BYTES_BUDGET');
     bytesReserved+=reservation;
    }catch(e){error=e.message;}
    queue.push({fileName,task,error,reservation,task_manifest_sha256:sha256(bytes)});
   }
   const doOne=async item=>{
    let state='PASS_BOUNDED',detail=null;
    try{if(item.error)throw Error(item.error);detail=await processTask(root,item.task,limits,item.reservation);}
    catch(e){state='FAIL_SCOPED';detail={failure_code:String(e.message).slice(0,128)};}
    const receipt={schema:'CoCivium.CoOmniCycle.TaskReceipt.R0',observed_at:new Date().toISOString(),task_manifest_sha256:item.task_manifest_sha256,
     task_id:item.task?.id||item.fileName.slice(0,-5),state,detail,authority:'NONE',external_effects:0,receiver_readproof:null,
     nonclaims:['LOCAL_IS_NOT_LANDED','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF','HASHING_IS_NOT_SEMANTIC_INGESTION']};
    const dst=path.join(root,'receipts',item.fileName);
    // Race safety: two cycles cannot commit conflicting receipts, and lock guards processing.
    if(!createOnce(dst,JSON.stringify(receipt,null,2)+'\n'))return 'HELD_DUPLICATE_RECEIPT';
    return state;
   };
   for(let i=0;i<queue.length;i+=limits.maxActive){
    const slice=queue.slice(i,i+limits.maxActive);
    const outcomes=await Promise.all(slice.map(x=>doOne(x)));
    for(const state of outcomes){if(state==='PASS_BOUNDED')passed++;else failed++;}
   }
   result={schema:SCHEMA,status:'COMPLETE_BOUNDED_LOCAL_CYCLE',started_at:start,completed_at:new Date().toISOString(),processed:queue.length,passed,failed,
    active_ceiling:limits.maxActive,actual_workers_spawned:0,provider_sessions_started:0,external_effects:0,
    bytes_reserved:bytesReserved,pending_after:readStatus(root).pending_count,nonclaims:NONCLAIMS};
  }
  atomicWrite(path.join(root,'status','last-cycle.json'),JSON.stringify(result,null,2)+'\n');
  return result;
 }finally{
  try{fs.closeSync(lockFD);}catch{}
  try{fs.unlinkSync(lock);}catch{}
 }
}
function help(){return `CoOmniCycle R0 (local, no network)\n  node CoOmniCycleR0.mjs --selftest\n  node CoOmniCycleR0.mjs --init <stateDir>\n  node CoOmniCycleR0.mjs --submit <stateDir> <task.json>\n  node CoOmniCycleR0.mjs --cycle <stateDir>\n  node CoOmniCycleR0.mjs --status <stateDir>\n  node CoOmniCycleR0.mjs --pause <stateDir>\n  node CoOmniCycleR0.mjs --resume <stateDir>\nTask kinds: HASH_OBJECT, INSPECT_JSON, COPY_PLAN. Objects must be in stateDir/objects.\n`;}
const ownPath=process.argv[1]?path.resolve(process.argv[1]):'';
if(ownPath===fileURLToPath(import.meta.url)){
 const [mode,root,extra]=process.argv.slice(2);
 try{
  if(mode==='--selftest'){const x=validateLimits();const t=validateTask({schema:'CoCivium.CoOmniCycle.Task.R0',id:'example',kind:'HASH_OBJECT',authority:'LOCAL_READ_ONLY',confidentiality:'LOCAL_ONLY',external_effects:false,relative_path:'sample.txt'});console.log(JSON.stringify({schema:SCHEMA,status:'PASS_NON_EFFECT_PREFLIGHT',defaults:x,sample:t.id,nonclaims:NONCLAIMS},null,2));}
  else if(mode==='--init')console.log(JSON.stringify(init(root),null,2));
  else if(mode==='--submit')console.log(JSON.stringify(submit(root,JSON.parse(fs.readFileSync(extra,'utf8'))),null,2));
  else if(mode==='--cycle')console.log(JSON.stringify(await cycle(root),null,2));
  else if(mode==='--status')console.log(JSON.stringify(readStatus(root),null,2));
  else if(mode==='--pause')console.log(JSON.stringify(pause(root),null,2));
  else if(mode==='--resume')console.log(JSON.stringify(resume(root),null,2));
  else {console.log(help());if(mode)process.exitCode=2;}
 }catch(e){console.error('HOLD_OR_FAIL: '+e.message);process.exitCode=3;}
}
