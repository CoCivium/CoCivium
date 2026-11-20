'use strict';
/**
 * CoCI+ R0: adversarial same-host, filesystem-backed sink-fencing canary.
 * Synthetic WorkID/effect only; sandboxed under os.tmpdir().
 * Deliberately tests concurrent attempts, stale preflight, lock orphan HOLD,
 * replay and source/receipt drift. It is not a production coordinator or
 * distributed-consensus, fsync/power-loss, CoStead/X2, or independent receiver proof.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawn, spawnSync} = require('node:child_process');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const ID = 'CoWorkID::concurrent-fencing-fixture:R0';
const SOURCE = 'INERT_SYNTHETIC_CONCURRENT_SOURCE_R0';
const DIGEST = hash(SOURCE);
const TOKEN = hash(ID + '\0' + DIGEST);
const WAIT = new Int32Array(new SharedArrayBuffer(4));
function sleep(ms){Atomics.wait(WAIT, 0, 0, ms);}
const file = (d,n) => path.join(d,n + '.json');
const parse = (d,n) => JSON.parse(fs.readFileSync(file(d,n),'utf8'));
const exists = (d,n) => fs.existsSync(file(d,n));
function replace(d,n,o){
 const p=file(d,n), t=p+'.'+process.pid+'.tmp';
 fs.writeFileSync(t,JSON.stringify(o)+'\n',{flag:'wx'});fs.renameSync(t,p);
}
function lock(d,fn){
 const lockDir=path.join(d,'fenced-sink.lock');const deadline=Date.now()+Number(process.env.COCI_LOCK_BUDGET_MS||5000);
 while(true){
  try{fs.mkdirSync(lockDir);break;}
  catch(e){if(e.code!=='EEXIST')throw e;if(Date.now()>deadline)throw Error('HOLD_LOCK_BUSY');sleep(5);}
 }
 try{return fn();}finally{fs.rmdirSync(lockDir);}
}
function bootstrap(d){
 assert(!exists(d,'intake'),'HOLD_PREEXISTING_INTAKE');
 replace(d,'intake',{work_id:ID,token:TOKEN,source_sha256:DIGEST,ceiling:'INERT_LOCAL_ONLY'});
}
function lease(d,owner,ttlMs=10000){return lock(d,()=>{
 const prev=exists(d,'lease')?parse(d,'lease'):{epoch:0};
 const rec={owner,epoch:prev.epoch+1,permission:true,expires_at_ms:Date.now()+ttlMs};
 replace(d,'lease',rec);return rec;
});}
function check(d,owner,epoch){
 const intake=parse(d,'intake'),l=parse(d,'lease');
 if(intake.work_id!==ID||intake.token!==TOKEN||intake.source_sha256!==DIGEST)throw Error('HOLD_SOURCE_DRIFT');
 if(!l.permission)throw Error('HOLD_AUTHORITY_REVOKED');
 if(l.expires_at_ms<=Date.now())throw Error('HOLD_LEASE_EXPIRED');
 if(l.owner!==owner||l.epoch!==epoch)throw Error('HOLD_STALE_ACTUATOR');
 return intake;
}
function ensureEffect(d){
 const expected={work_id:ID,source_sha256:DIGEST,token:TOKEN,effect:'INERT_MARKER'};
 if(exists(d,'effect')){assert.deepEqual(parse(d,'effect'),expected,'HOLD_EFFECT_COLLISION');return true;}
 // Exclusive publication while holding the single scoped sink lock.
 fs.writeFileSync(file(d,'effect'),JSON.stringify(expected)+'\n',{flag:'wx'});
 return false;
}
function finish(d){
 if(!exists(d,'effect'))throw Error('HOLD_EFFECT_MISSING');
 const effect=parse(d,'effect');
 assert.deepEqual(effect,{work_id:ID,source_sha256:DIGEST,token:TOKEN,effect:'INERT_MARKER'},'HOLD_EFFECT_COLLISION');
 const expected={work_id:ID,source_sha256:DIGEST,effect_sha256:hash(fs.readFileSync(file(d,'effect'))),outcome:'INERT_ONE_EFFECT'};
 if(exists(d,'receipt'))assert.deepEqual(parse(d,'receipt'),expected,'HOLD_RECEIPT_DRIFT');
 else fs.writeFileSync(file(d,'receipt'),JSON.stringify(expected)+'\n',{flag:'wx'});
}
function commit(d,owner,epoch,mode='run'){
 return lock(d,()=>{
  check(d,owner,epoch);
  const repeated=ensureEffect(d);
  if(mode==='effect-only')return {repeated};
  finish(d);return {repeated};
 });
}
function readback(d){return lock(d,()=>{
 if(!exists(d,'receipt'))throw Error('HOLD_RECEIVER_MISSING');
 const e=fs.readFileSync(file(d,'effect')),r=parse(d,'receipt'),intake=parse(d,'intake');
 if(r.work_id!==ID||r.source_sha256!==DIGEST||r.effect_sha256!==hash(e)||intake.token!==TOKEN)throw Error('HOLD_READBACK_DRIFT');
 return {scope:'SAME_HOST_DIFFERENT_PID',reader_pid:process.pid,independent_provider:false};
});}
function worker(args){const r=spawnSync(process.execPath,[__filename,...args],{encoding:'utf8',timeout:8000,env:{...process.env,COCI_LOCK_BUDGET_MS:'120'}});return r;}
function workerOK(args){const r=worker(args);assert.equal(r.status,0,r.stderr||String(r.error));return JSON.parse(r.stdout);}
function workerHOLD(args,reason){const r=worker(args);assert.notEqual(r.status,0,'Unexpected success '+args.join(' '));assert.match(r.stderr,new RegExp(reason));}
function child(d,owner,epoch,mode='run'){
 return new Promise((resolve,reject)=>{
  const p=spawn(process.execPath,[__filename,'work',d,owner,String(epoch),mode],{stdio:['ignore','pipe','pipe'],env:{...process.env,COCI_LOCK_BUDGET_MS:'5000'}});
  let out='',err='';p.stdout.on('data',x=>out+=x);p.stderr.on('data',x=>err+=x);
  p.on('error',reject);p.on('close',(code,signal)=>resolve({code,signal,out,err,pid:p.pid}));
 });
}
if(process.argv[2]==='work'){
 try{
  const [d,owner,rawEpoch,mode='run']=process.argv.slice(3),epoch=Number(rawEpoch);
  if(mode==='pause-after-preflight'){
   check(d,owner,epoch);
   fs.writeFileSync(path.join(d,'ready-'+owner),String(process.pid),{flag:'wx'});
   const deadline=Date.now()+5000;
   while(!fs.existsSync(path.join(d,'go-'+owner))){if(Date.now()>deadline)throw Error('HOLD_BARRIER_TIMEOUT');sleep(3);}
  }
  if(mode==='die-with-lock')lock(d,()=>{check(d,owner,epoch);process.kill(process.pid,'SIGKILL');});
  const result=commit(d,owner,epoch,mode==='effect-only'?'effect-only':'run');
  process.stdout.write(JSON.stringify(result)+'\n');
 }catch(e){process.stderr.write(e.message+'\n');process.exitCode=49;}
}else if(process.argv[2]==='read'){
 try{process.stdout.write(JSON.stringify(readback(process.argv[3]))+'\n');}
 catch(e){process.stderr.write(e.message+'\n');process.exitCode=50;}
}else if(process.argv.length>2){throw Error('Unknown mode');}
else{
 (async()=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'coci-concurrent-fence-r0-'));
  const d=name=>{const p=path.join(root,name);fs.mkdirSync(p);bootstrap(p);return p;};
  let passed=0;const test=(title,fn)=>{fn();passed++;console.log('PASS '+title);};
  const asyncTest=async(title,fn)=>{await fn();passed++;console.log('PASS '+title);};
  try{
   const a=d('parallel');const l=lease(a,'ELECTED');
   const out=await Promise.all(Array.from({length:12},()=>child(a,'ELECTED',l.epoch)));
   test('twelve overlapping attempts all finish without corruption',()=>{
     assert.equal(out.filter(x=>x.code!==0).length,0,JSON.stringify(out.filter(x=>x.code!==0)));
   });
   test('exactly one effect-creating attempt and eleven replays',()=>{
     const results=out.map(x=>JSON.parse(x.out));
     assert.equal(results.filter(x=>x.repeated===false).length,1);
     assert.equal(results.filter(x=>x.repeated===true).length,11);
   });
   test('one idempotency token yields one effect and one receipt',()=>{
     const files=fs.readdirSync(a);assert.equal(files.filter(x=>x==='effect.json').length,1);
     assert.equal(files.filter(x=>x==='receipt.json').length,1);
     assert.equal(parse(a,'effect').token,TOKEN);
   });
   test('another PID readback is scoped to same host',()=>{
     const r=workerOK(['read',a]);assert.notEqual(r.reader_pid,process.pid);assert.equal(r.independent_provider,false);
   });
   const b=d('stale');const early=lease(b,'A');
   const pa=child(b,'A',early.epoch,'pause-after-preflight');
   const deadline=Date.now()+5000;while(!fs.existsSync(path.join(b,'ready-A'))){if(Date.now()>deadline)throw Error('HOLD_PRELUDE_TIMEOUT');await new Promise(res=>setTimeout(res,4));}
   const current=lease(b,'B');fs.writeFileSync(path.join(b,'go-A'),'go',{flag:'wx'});
   const res=await pa;
   test('stale worker preflight before newer election rejected at sink',()=>{
     assert.notEqual(res.code,0);assert.match(res.err,/HOLD_STALE_ACTUATOR/);assert(!exists(b,'effect'));
   });
   test('new epoch elected worker commits after stale actor rejected',()=>{
     assert.equal(workerOK(['work',b,'B',String(current.epoch)]).repeated,false);
     assert.equal(parse(b,'effect').token,TOKEN);
   });
   const c=d('collision');const el=lease(c,'K');
   const mixed=await Promise.all([
     ...Array.from({length:4},()=>child(c,'K',el.epoch)),
     ...Array.from({length:7},()=>child(c,'UNKNOWN',el.epoch))
   ]);
   test('unelected competing owners all rejected without effect duplication',()=>{
     assert(mixed.slice(0,4).every(x=>x.code===0));
     assert(mixed.slice(4).every(x=>x.code!==0 && /HOLD_STALE_ACTUATOR/.test(x.err)));
     assert.equal(parse(c,'effect').token,TOKEN);
   });
   const exp=d('expiry');const ex=lease(exp,'E',-1);
   test('expired lease denies commit',()=>{workerHOLD(['work',exp,'E',String(ex.epoch)],'HOLD_LEASE_EXPIRED');assert(!exists(exp,'effect'));});
   const rev=d('revoked');const rv=lease(rev,'R');const rec=parse(rev,'lease');rec.permission=false;replace(rev,'lease',rec);
   test('revoked lease denies commit',()=>{workerHOLD(['work',rev,'R',String(rv.epoch)],'HOLD_AUTHORITY_REVOKED');assert(!exists(rev,'effect'));});
   const gap=d('receipt-gap');const pre=lease(gap,'P');
   test('effect can exist without ACK and separate reader must HOLD',()=>{
     workerOK(['work',gap,'P',String(pre.epoch),'effect-only']);workerHOLD(['read',gap],'HOLD_RECEIVER_MISSING');
   });
   const after=lease(gap,'S');
   test('successor reconciles effect without creating another',()=>{
     assert.equal(workerOK(['work',gap,'S',String(after.epoch)]).repeated,true);
     assert.equal(workerOK(['read',gap]).independent_provider,false);
   });
   const corrupt=d('corrupt');const cl=lease(corrupt,'C');workerOK(['work',corrupt,'C',String(cl.epoch)]);
   const receipt=parse(corrupt,'receipt');receipt.effect_sha256='0'.repeat(64);replace(corrupt,'receipt',receipt);
   test('tampered receipt is refused',()=>workerHOLD(['read',corrupt],'HOLD_READBACK_DRIFT'));
   const torn=d('torn');const tl=lease(torn,'T');fs.writeFileSync(file(torn,'intake'),'{torn');
   test('torn intake fails closed',()=>{const r=worker(['work',torn,'T',String(tl.epoch)]);assert.notEqual(r.status,0);assert(!exists(torn,'effect'));});
   const orphan=d('orphan');const ol=lease(orphan,'O');
   test('SIGKILL while holding sink lock creates quarantine',()=>{
     const r=worker(['work',orphan,'O',String(ol.epoch),'die-with-lock']);assert.equal(r.signal,'SIGKILL');assert(fs.existsSync(path.join(orphan,'fenced-sink.lock')));assert(!exists(orphan,'effect'));
   });
   test('orphaned lock blocks new writer and reader rather than guessing owner',()=>{
     workerHOLD(['work',orphan,'O',String(ol.epoch)],'HOLD_LOCK_BUSY');workerHOLD(['read',orphan],'HOLD_LOCK_BUSY');
   });
   test('no auto-lock-break makes power-failure recovery explicitly unproven',()=>{
     assert(fs.existsSync(path.join(orphan,'fenced-sink.lock')));assert(!exists(orphan,'receipt'));
   });
   const summary={schema:'CoCI.SyntheticConcurrentFencing.R0',passed,source_work_id:ID,
     concurrent_attempts:12,one_effect:true,one_receipt:true,stale_actor_after_preflight_rejected:true,
     orphan_lock_result:'HOLD_NO_AUTO_BREAK',external_effects:0,
     nonclaims:['SAME_HOST_NE_INDEPENDENT_RECEIVER','NO_FSYNC_POWER_LOSS_PROOF','NO_DISTRIBUTED_CONSENSUS','SYNTHETIC_NE_PRODUCTION_ACTUATOR','NO_COSTEAD_OR_X2_RECEIVER_ACK']};
   if(process.env.COCI_FENCE_RECEIPT_DIR){fs.mkdirSync(process.env.COCI_FENCE_RECEIPT_DIR,{recursive:true});
     fs.writeFileSync(path.join(process.env.COCI_FENCE_RECEIPT_DIR,'concurrent-fence-receipt.json'),JSON.stringify(summary,null,2)+'\n',{flag:'wx'});}
   console.log('SYNTHETIC_CONCURRENT_FENCE_PASS '+passed+' tests | NO_INDEPENDENT_RECEIVER | NO_POWER_LOSS_PROOF');
  }finally{fs.rmSync(root,{recursive:true,force:true});}
 })().catch(e=>{console.error(e.stack);process.exitCode=1;});
}