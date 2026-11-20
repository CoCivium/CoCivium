'use strict';
/**
 * Source-only CoWorkID crash/replay and fencing fixture.
 * Synthetic bytes, inert effect, one host, sequential elected actuator.
 * NOT distributed consensus, X2/CoStead deployment, human acceptance, or CoEx.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const hash = x => crypto.createHash('sha256').update(x).digest('hex');
const WORK_ID = 'CoWorkID::synthetic-replay-fixture:R0';
const INPUT = 'inert, public-safe, source-only test fixture';
const INPUT_SHA = hash(INPUT);
const TOKEN = hash(WORK_ID + '\0' + INPUT_SHA);
const name = (dir, stem) => path.join(dir, stem + '.json');
const exists = (dir, stem) => fs.existsSync(name(dir, stem));
const load = (dir, stem) => JSON.parse(fs.readFileSync(name(dir, stem), 'utf8'));
const dump = o => JSON.stringify(o) + '\n';
function replace(dir, stem, obj) {
  const tmp = name(dir, stem) + '.' + process.pid + '.tmp';
  fs.writeFileSync(tmp, dump(obj), {flag:'wx'});
  fs.renameSync(tmp, name(dir, stem));
}
function once(dir, stem, obj) { fs.writeFileSync(name(dir, stem), dump(obj), {flag:'wx'}); }
function admit(dir, input=INPUT) {
  const rec={work_id:WORK_ID, source_sha256:hash(input), token:hash(WORK_ID+'\0'+hash(input)), effect_ceiling:'INERT_LOCAL_ONLY'};
  if (!exists(dir, 'intake')) once(dir, 'intake', rec);
  assert.deepEqual(load(dir,'intake'),rec,'HOLD_CHANGED_INTAKE');
  return rec;
}
function elect(dir, who) {
  const previous=exists(dir,'lease')?load(dir,'lease'):{epoch:0};
  const lease={who,epoch:previous.epoch+1,permission:true};
  replace(dir,'lease',lease);
  return lease.epoch;
}
function gate(dir,who,epoch) {
  const intake=load(dir,'intake'),lease=load(dir,'lease');
  if (intake.work_id!==WORK_ID || intake.source_sha256!==INPUT_SHA || intake.token!==TOKEN) throw Error('HOLD_SOURCE_IDENTITY');
  if (!lease.permission) throw Error('HOLD_AUTHORITY_REVOKED');
  if (lease.who!==who || lease.epoch!==epoch) throw Error('HOLD_STALE_LEASE');
  return intake;
}
function effect(dir,who,epoch) {
  const intake=gate(dir,who,epoch);
  const obj={work_id:WORK_ID, token:intake.token, source_sha256:INPUT_SHA, marker:'INERT_LOCAL_EFFECT'};
  if (exists(dir,'effect')) {
    assert.deepEqual(load(dir,'effect'),obj,'HOLD_EFFECT_COLLISION');
    return {replayed:true};
  }
  try {once(dir,'effect',obj);} catch(e) {
    if(e.code!=='EEXIST') throw e;
    assert.deepEqual(load(dir,'effect'),obj,'HOLD_EFFECT_COLLISION');
    return {replayed:true};
  }
  return {replayed:false};
}
function commit(dir,who,epoch) {
  gate(dir,who,epoch);
  if (!exists(dir,'effect')) throw Error('HOLD_EFFECT_UNOBSERVED');
  const obj=load(dir,'effect');
  const expected={work_id:WORK_ID,token:TOKEN,source_sha256:INPUT_SHA,marker:'INERT_LOCAL_EFFECT'};
  assert.deepEqual(obj,expected,'HOLD_EFFECT_COLLISION');
  const r={work_id:WORK_ID, effect_digest:hash(dump(obj)), result:'INERT_LOCAL_RECONCILED'};
  if (exists(dir,'receipt')) assert.deepEqual(load(dir,'receipt'),r,'HOLD_RECEIPT_DRIFT');
  else once(dir,'receipt',r);
}
function reader(dir) {
  if (!exists(dir,'receipt')) throw Error('HOLD_RECEIVER_MISSING');
  const i=load(dir,'intake'),e=load(dir,'effect'),r=load(dir,'receipt');
  if(i.source_sha256!==INPUT_SHA||i.token!==TOKEN||e.token!==i.token||e.source_sha256!==INPUT_SHA||r.effect_digest!==hash(dump(e))) throw Error('HOLD_READBACK_DRIFT');
  return {receiver_pid:process.pid,scope:'SAME_MACHINE_DIFFERENT_PROCESS',independent_power_domain:false};
}
function invoke(args) {return spawnSync(process.execPath,[__filename,...args],{encoding:'utf8',timeout:7000});}
function succeeds(args) {const r=invoke(args);assert.equal(r.status,0,r.stderr||String(r.error));return JSON.parse(r.stdout);}
function fails(args,pattern) {const r=invoke(args);assert.notEqual(r.status,0,'Expected fail-closed: '+args.join(' '));assert.match(r.stderr,new RegExp(pattern));}
if (process.argv[2]==='worker') {
 try {
  const [dir,who,e,mode]=process.argv.slice(3),epoch=Number(e);
  if(mode==='die-before') {gate(dir,who,epoch);process.kill(process.pid,'SIGKILL');}
  const r=effect(dir,who,epoch);
  if(mode==='die-after') process.kill(process.pid,'SIGKILL');
  if(mode==='commit') commit(dir,who,epoch);
  process.stdout.write(JSON.stringify(r)+'\n');
 } catch(e) {process.stderr.write(e.message+'\n');process.exitCode=41;}
} else if(process.argv[2]==='reader') {
 try {process.stdout.write(JSON.stringify(reader(process.argv[3]))+'\n');}
 catch(e){process.stderr.write(e.message+'\n');process.exitCode=42;}
} else if(process.argv.length>2){throw Error('Invalid fixture mode');}
else {
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'coworkid-source-fixture-'));
  let passed=0;
  const test=(label,fn)=>{fn();passed++;console.log('PASS '+label);};
  const directory=stem=>{const d=path.join(root,stem);fs.mkdirSync(d);return d;};
  try {
   const a=directory('before');
   test('no durable intake means no ACK',()=>{assert(!exists(a,'intake'));assert.throws(()=>reader(a),/HOLD_RECEIVER_MISSING/);});
   test('same-source duplicate intake dedupes',()=>{assert.deepEqual(admit(a),admit(a));});
   test('changed-source duplicate intake fails closed',()=>assert.throws(()=>admit(a,INPUT+'changed'),/HOLD_CHANGED_INTAKE/));
   const epoch1=elect(a,'A');
   test('SIGKILL before effect leaves no marker',()=>{const r=invoke(['worker',a,'A',String(epoch1),'die-before']);assert.equal(r.signal,'SIGKILL');assert(!exists(a,'effect'));});
   const epoch2=elect(a,'B');
   test('fenced stale actuator cannot commit',()=>fails(['worker',a,'A',String(epoch1),'commit'],'HOLD_STALE_LEASE'));
   test('elected successor commits inert effect',()=>{assert.equal(succeeds(['worker',a,'B',String(epoch2),'commit']).replayed,false);assert(exists(a,'receipt'));});
   test('five retries replay one exact effect',()=>{const x=fs.readFileSync(name(a,'effect'));for(let i=0;i<5;i++) assert.equal(succeeds(['worker',a,'B',String(epoch2),'commit']).replayed,true);assert.equal(Buffer.compare(x,fs.readFileSync(name(a,'effect'))),0);});
   test('other PID readback is not independent failure domain',()=>{const r=succeeds(['reader',a]);assert.notEqual(r.receiver_pid,process.pid);assert.equal(r.independent_power_domain,false);});
   const b=directory('after');admit(b);const epoch3=elect(b,'C');
   test('SIGKILL after effect before receipt leaves recovery gap',()=>{const r=invoke(['worker',b,'C',String(epoch3),'die-after']);assert.equal(r.signal,'SIGKILL');assert(exists(b,'effect'));assert(!exists(b,'receipt'));fails(['reader',b],'HOLD_RECEIVER_MISSING');});
   const epoch4=elect(b,'D');
   test('successor reconciles effect, not duplicated',()=>{const before=fs.readFileSync(name(b,'effect'));assert.equal(succeeds(['worker',b,'D',String(epoch4),'commit']).replayed,true);assert.equal(Buffer.compare(before,fs.readFileSync(name(b,'effect'))),0);});
   test('new process reads reconciled source',()=>assert.equal(succeeds(['reader',b]).scope,'SAME_MACHINE_DIFFERENT_PROCESS'));
   const c=directory('revoked');admit(c);const ep5=elect(c,'E');const l=load(c,'lease');l.permission=false;replace(c,'lease',l);
   test('revoked lease fails closed',()=>{fails(['worker',c,'E',String(ep5),'commit'],'HOLD_AUTHORITY_REVOKED');assert(!exists(c,'effect'));});
   const d=directory('torn');admit(d);elect(d,'F');fs.writeFileSync(name(d,'lease'),'{bad');
   test('torn checkpoint fails closed',()=>{const r=invoke(['worker',d,'F','1','commit']);assert.notEqual(r.status,0);assert(!exists(d,'effect'));});
   const e=directory('drift');admit(e);elect(e,'G');const o=load(e,'intake');o.source_sha256='0'.repeat(64);replace(e,'intake',o);
   test('source drift fails closed',()=>{fails(['worker',e,'G','1','commit'],'HOLD_SOURCE_IDENTITY');assert(!exists(e,'effect'));});
   const f=directory('collision');admit(f);elect(f,'H');once(f,'effect',{token:'WRONG'});
   test('effect collision is not silently replaced',()=>{fails(['worker',f,'H','1','commit'],'HOLD_EFFECT_COLLISION');assert(!exists(f,'receipt'));});
   const g=directory('tampered');admit(g);elect(g,'I');succeeds(['worker',g,'I','1','commit']);const rec=load(g,'receipt');rec.effect_digest='0'.repeat(64);replace(g,'receipt',rec);
   test('tampered receipt fails readback',()=>fails(['reader',g],'HOLD_READBACK_DRIFT'));
   const h=directory('unobserved');admit(h);elect(h,'J');
   test('no effect before receipt fails closed',()=>assert.throws(()=>commit(h,'J',1),/HOLD_EFFECT_UNOBSERVED/));
   console.log('SYNTHETIC_SOURCE_RECOVERY_PASS '+passed+' tests | no external effects, no independent receiver');
  } finally {fs.rmSync(root,{recursive:true,force:true});}
}