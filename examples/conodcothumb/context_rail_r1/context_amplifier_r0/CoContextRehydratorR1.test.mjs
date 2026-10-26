import test from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import {tmpdir} from 'node:os';
import * as path from 'node:path';
import {createHash} from 'node:crypto';
import {planContext} from './CoContextAmplifierR0.mjs';
import {rehydrateLocalPlan,SCHEMA} from './CoContextRehydratorR1.mjs';

const sha=(s)=>createHash('sha256').update(s).digest('hex');
let root;
const req=(items,budget_units=90)=>planContext({work_id:'check.r1',budget_units,headroom_units:10,sources:items});
const d=(id,content,opts={})=>({id,source_ref:'local:'+id+'.txt',sha256:sha(content),cost_units:10,
  utility:50,kind:'SUPPORT',freshness:'CURRENT',privacy:'PUBLIC',...opts});
const opts=(o={})=>({root,explicitLocalRead:true,maxPerFileBytes:1024,maxTotalBytes:4096,...o});
const run=(p,o={})=>rehydrateLocalPlan(p,opts(o));

test.before(async()=>{
  root=await fs.mkdtemp(path.join(tmpdir(),'co-context-rehydrator-'));
  await fs.writeFile(path.join(root,'alpha.txt'),'Alpha original, evidence A.\n');
  await fs.writeFile(path.join(root,'counter.txt'),'Counterevidence B.\n');
  await fs.mkdir(path.join(root,'nested'));
  await fs.writeFile(path.join(root,'nested','small.txt'),'Nested text.');
  await fs.writeFile(path.join(root,'binary.txt'),Buffer.from([0xff,0xfe,0x01]));
  await fs.writeFile(path.join(root,'large.txt'),'x'.repeat(1500));
});
test.after(async()=>{if(root)await fs.rm(root,{recursive:true,force:true});});

const alpha=()=>d('alpha','Alpha original, evidence A.\n');
const counter=()=>d('counter','Counterevidence B.\n',{kind:'COUNTER'});

test('has a distinct schema',async()=>assert.equal((await run(req([alpha()]))).schema,SCHEMA));
test('explicit opt-in is required',async()=>assert.equal((await rehydrateLocalPlan(req([alpha()]),opts({explicitLocalRead:false}))).state,'HOLD_EXPLICIT_LOCAL_READ_REQUIRED'));
test('selected bytes really read and checked',async()=>assert.equal((await run(req([alpha()]))).state,'SOURCE_BYTES_VERIFIED_LOCAL_ONLY'));
test('byte count exact',async()=>assert.equal((await run(req([alpha()]))).bytes_verified,Buffer.byteLength('Alpha original, evidence A.\n')));
test('actual SHA matches',async()=>assert.equal((await run(req([alpha()]))).sources[0].sha256,sha('Alpha original, evidence A.\n')));
test('text omitted by default',async()=>assert.equal('text' in (await run(req([alpha()]))).sources[0],false));
test('text delivered only when elected',async()=>assert.equal((await run(req([alpha()]),{includeText:true})).sources[0].text,'Alpha original, evidence A.\n'));
test('manifest digest is stable on replay',async()=>assert.equal((await run(req([alpha()]))).manifest_sha256,(await run(req([alpha()]))).manifest_sha256));
test('counterevidence survives the byte path',async()=>assert.deepEqual((await run(req([alpha(),counter()]))).sources.map(x=>x.kind).sort(),['COUNTER','SUPPORT']));
test('no network, send, execution or mutation',async()=>{const x=await run(req([alpha()]));assert.equal(x.effects.network,0);assert.equal(x.effects.sends,0);assert.equal(x.effects.executes,0);assert.equal(x.effects.writes,0);});
test('local read is accounted',async()=>assert.equal((await run(req([alpha(),counter()]))).effects.local_reads,2));
test('tokenizer remains explicitly unverified',async()=>assert.equal((await run(req([alpha()]))).model_context_tokens,null));
test('receiver ack remains false',async()=>assert.equal((await run(req([alpha()]))).receiver_ack,false));
test('missing file fails closed and reveals no prior text',async()=>{const x=await run(req([alpha(),d('missing','I do not exist')]));assert.equal(x.state,'HOLD_READ_OR_PATH_FAILURE');assert.deepEqual(x.sources,[]);});
test('wrong digest fails closed',async()=>assert.equal((await run(req([d('alpha','WRONG')]))).state,'HOLD_SHA256_MISMATCH'));
test('stale source blocked in original proposal',async()=>assert.equal((await run(req([d('alpha','Alpha original, evidence A.\n',{freshness:'STALE',required:true})]))).state,'HOLD_INVALID_PLAN_OR_LIMIT'));
test('private source blocked by planner',async()=>assert.equal((await run(req([d('alpha','Alpha original, evidence A.\n',{privacy:'PRIVATE',required:true})]))).state,'HOLD_INVALID_PLAN_OR_LIMIT'));
test('per source byte limit enforced',async()=>assert.equal((await run(req([d('large','x'.repeat(1500))]),{maxPerFileBytes:1024})).state,'HOLD_BYTE_BUDGET_EXCEEDED'));
test('aggregate byte limit enforced',async()=>assert.equal((await run(req([alpha(),counter()]),{maxTotalBytes:32,maxPerFileBytes:32})).state,'HOLD_BYTE_BUDGET_EXCEEDED'));
test('reject absolute path',async()=>assert.equal((await run(req([d('alpha','Alpha original, evidence A.\n',{source_ref:'local:/etc/passwd'})]))).state,'HOLD_INVALID_PUBLIC_SOURCE_METADATA'));
test('reject path traversal',async()=>assert.equal((await run(req([d('alpha','Alpha original, evidence A.\n',{source_ref:'local:../escape'})]))).state,'HOLD_INVALID_PUBLIC_SOURCE_METADATA'));
test('reject Windows-style path escape',async()=>assert.equal((await run(req([d('alpha','Alpha original, evidence A.\n',{source_ref:'local:..\\escape.txt'})]))).state,'HOLD_INVALID_PUBLIC_SOURCE_METADATA'));
test('reject non-local scheme',async()=>assert.equal((await run(req([d('alpha','Alpha original, evidence A.\n',{source_ref:'https://example.com'})]))).state,'HOLD_INVALID_PUBLIC_SOURCE_METADATA'));
test('valid nested relative path',async()=>assert.equal((await run(req([d('nested','Nested text.',{source_ref:'local:nested/small.txt'})]))).state,'SOURCE_BYTES_VERIFIED_LOCAL_ONLY'));
test('reject final symlink',async()=>{const p=path.join(root,'link.txt');await fs.symlink(path.join(root,'alpha.txt'),p);const x=await run(req([d('link','Alpha original, evidence A.\n')]));assert.equal(x.state,'HOLD_SYMLINK_OR_PATH_ESCAPE');});
test('reject symlinked intermediate folder',async()=>{await fs.symlink(path.join(root,'nested'),path.join(root,'outer'));const x=await run(req([d('other','Nested text.',{source_ref:'local:outer/small.txt'})]));assert.equal(x.state,'HOLD_SYMLINK_OR_PATH_ESCAPE');});
test('reject invalid UTF8',async()=>{const value=await run(req([d('binary',Buffer.from([0xff,0xfe,0x01]))]));assert.equal(value.state,'HOLD_INVALID_UTF8');});
test('invalid plan rejected',async()=>assert.equal((await run({state:'SENT',schema:'Other',selected:[]})).state,'HOLD_INVALID_PLAN_OR_LIMIT'));
test('zero selected is a verifiable empty result',async()=>assert.equal((await run(req([]))).state,'VERIFIED_EMPTY'));
test('missing root fails closed',async()=>assert.equal((await run(req([alpha()]),{root:'/unavailable-fake-nonexistent'})).state,'HOLD_ROOT_UNAVAILABLE'));
test('file changed after descriptor built fails',async()=>{await fs.writeFile(path.join(root,'alpha.txt'),'New contents that changed the source.');const x=await run(req([alpha()]));assert.equal(x.state,'HOLD_SHA256_MISMATCH');await fs.writeFile(path.join(root,'alpha.txt'),'Alpha original, evidence A.\n');});
