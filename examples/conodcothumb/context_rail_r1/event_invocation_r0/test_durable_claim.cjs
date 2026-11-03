'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const os=require('node:os');
const fs=require('node:fs');
const path=require('node:path');
const {spawnSync,spawn}=require('node:child_process');
const {invoke}=require('./CoBDurableClaimR1.cjs');
const SCRIPT=path.join(__dirname,'CoBDurableClaimR1.cjs');
const packet=(x={})=>({event_id:'e1',work_id:'w1',operation:'REFRESH_LOCAL_STATUS',
  privacy:'PUBLIC_SYNTHETIC',observed_ms:950,expires_ms:1100,...x});
function root(){return fs.mkdtempSync(path.join(os.tmpdir(),'cob-durable-r1-'));}
function run(r,route='COB_EVENT',p=packet(),crash=''){
  return spawnSync(process.execPath,[SCRIPT,r,route,JSON.stringify(p),crash],{encoding:'utf8'});
}
function entries(r){return fs.readdirSync(r).filter(s=>/^[a-f0-9]{64}$/.test(s));}
function markers(r){return entries(r).filter(x=>fs.existsSync(path.join(r,x,'synthetic_effect.json'))).length;}
test('fresh process executes one isolated synthetic effect and cross-route cold replay dedupes',t=>{
  const r=root();t.after(()=>fs.rmSync(r,{recursive:true,force:true}));
  const a=run(r,'BUTTON');assert.equal(a.status,0,a.stderr);
  assert.equal(JSON.parse(a.stdout).state,'LOCAL_ONLY_EXECUTED');
  const b=run(r,'COB_EVENT',packet({event_id:'e2'}));assert.equal(b.status,0,b.stderr);
  assert.equal(JSON.parse(b.stdout).state,'DEDUPED');
  assert.equal(markers(r),1);
});
test('crash after durable claim cannot replay effect',t=>{
  const r=root();t.after(()=>fs.rmSync(r,{recursive:true,force:true}));
  assert.equal(run(r,'COB_EVENT',packet(),'AFTER_CLAIM').status,71);
  const b=run(r,'BUTTON',packet({event_id:'e2'}));
  assert.equal(JSON.parse(b.stdout).reason,'CLAIMED_OR_RECOVERY_REQUIRED');
  assert.equal(markers(r),0);
});
test('crash after synthetic effect but before receipt cannot replay effect',t=>{
  const r=root();t.after(()=>fs.rmSync(r,{recursive:true,force:true}));
  assert.equal(run(r,'COB_EVENT',packet(),'AFTER_EFFECT').status,72);
  const b=run(r,'BUTTON',packet({event_id:'e2'}));
  assert.equal(JSON.parse(b.stdout).reason,'CLAIMED_OR_RECOVERY_REQUIRED');
  assert.equal(markers(r),1);
});
test('malformed and private packets cannot write to fixture',t=>{
  const r=root();t.after(()=>fs.rmSync(r,{recursive:true,force:true}));
  for(const fields of [{operation:'SEND_MAIL'},{privacy:'PRIVATE'}, {work_id:'../escape'},
     {source:'verified'}, {observed_ms:1001}, {expires_ms:999}]) {
    assert.equal(invoke({root:r,route:'COB_EVENT',event:packet(fields)}).state,'HELD');
  }
  assert.equal(fs.existsSync(r)&&entries(r).length>0,false);
});
test('distinct work identity creates a distinct effect; no global lockout',t=>{
  const r=root();t.after(()=>fs.rmSync(r,{recursive:true,force:true}));
  assert.equal(run(r).status,0);
  assert.equal(run(r,'COB_EVENT',packet({work_id:'w2',event_id:'e2'})).status,0);
  assert.equal(markers(r),2);
});
test('independent process concurrency elects exactly one local fixture effect',async t=>{
  const r=root();t.after(()=>fs.rmSync(r,{recursive:true,force:true}));
  const workers=await Promise.all(Array.from({length:6},(_,i)=>new Promise((resolve,reject)=>{
    const child=spawn(process.execPath,[SCRIPT,r,i%2?'BUTTON':'COB_EVENT',
       JSON.stringify(packet({event_id:'e'+i}))]);
    let data='';child.stdout.on('data',x=>data+=x);
    child.on('error',reject);child.on('exit',code=>resolve({code,result:JSON.parse(data)}));
  })));
  assert.ok(workers.every(w=>w.code===0));
  assert.equal(workers.filter(w=>w.result.state==='LOCAL_ONLY_EXECUTED').length,1);
  assert.equal(markers(r),1);
});
