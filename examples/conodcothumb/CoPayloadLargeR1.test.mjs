import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, open, readFile, readdir, rm, symlink, truncate, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { inspectLarge,verifyStaged,DEFAULT_MAX_BYTES,ABSOLUTE_MAX_BYTES } from './CoPayloadLargeR1.mjs';

const MiB=1024*1024;
async function box(t) {
 const dir=await mkdtemp(join(tmpdir(),'cothumb-r1-'));
 t.after(()=>rm(dir,{force:true,recursive:true})); return dir;
}
async function fixture(path,megabytes) {
 const handle=await open(path,'wx',0o600);
 try {
  const buf=Buffer.allocUnsafe(MiB);
  for(let i=0;i<megabytes;i++) {
   for(let j=0;j<buf.length;j++) buf[j]=(i*83+j*17+(j>>>11))&255;
   await handle.writeFile(buf);
  }
 } finally {await handle.close();}
}
async function dirFiles(root) {return (await readdir(root)).sort()}

test('R1 preview hashes multiple deterministic chunks without exposing source path',async t=>{
 const dir=await box(t),file=join(dir,'internal-client-name.mp4'); await fixture(file,3);
 const r=await inspectLarge(file,{chunkBytes:MiB,maxBytes:10*MiB});
 assert.equal(r.byte_count,3*MiB); assert.equal(r.chunk_count,3);assert.equal(r.state,'SOURCE_PREVIEW_ONLY');
 assert.equal(r.authority,'NONE'); assert.equal(r.receiver_ack,false);assert.equal(r.external_effects.send,0);
 assert.ok(r.chunks.every((c,i)=>c.index===i&&c.byte_count===MiB));
 assert.equal(r.sha256,createHash('sha256').update(await readFile(file)).digest('hex'));
 assert.equal(JSON.stringify(r).includes('internal-client-name'),false);
 assert.equal(JSON.stringify(r).includes(dir),false);
});
test('R1 explicit local stage + hash-bound manifest reassembly verified',async t=>{
 const dir=await box(t),file=join(dir,'sample.mov');await fixture(file,3);
 const b=join(dir,'private');
 const r=await inspectLarge(file,{stage:true,acceptLocalCopy:true,bufferDir:b,chunkBytes:MiB,maxBytes:10*MiB});
 assert.equal(r.state,'STAGED_LOCAL_ONLY');assert.equal(r.staging_receipt.created_chunks,3);
 assert.equal((await readdir(join(b,'objects'))).length,3);
 const v=await verifyStaged(b,r.manifest_locator.split('/')[1]);
 assert.equal(v.sha256,r.sha256);assert.equal(v.byte_count,3*MiB);
 assert.equal(v.independent_custody,false);
});
test('R1 refuses stage without exact opt-in before buffer is created',async t=>{
 const dir=await box(t),f=join(dir,'x.txt');await writeFile(f,'hello');
 await assert.rejects(inspectLarge(f,{stage:true,bufferDir:join(dir,'buffer')}),/EXPLICIT_LOCAL_COPY_CONSENT_REQUIRED/);
 assert.deepEqual(await dirFiles(dir),['x.txt']);
});
test('R1 interruptions preserve verified chunks and restart resumes exactly',async t=>{
 const dir=await box(t),f=join(dir,'asset.bin'),b=join(dir,'buffer');await fixture(f,4);
 const opts={stage:true,acceptLocalCopy:true,bufferDir:b,chunkBytes:MiB,maxBytes:10*MiB};
 await assert.rejects(inspectLarge(f,{...opts,interruptAfterChunks:2}),/INJECTED_RECOVERY_TEST_INTERRUPTION/);
 assert.equal((await readdir(join(b,'objects'))).length,2);
 const resumed=await inspectLarge(f,opts);
 assert.equal(resumed.staging_receipt.created_chunks,2);
 assert.equal(resumed.staging_receipt.reused_chunks,2);
 assert.equal((await readdir(join(b,'objects'))).length,4);
 assert.equal((await verifyStaged(b,resumed.manifest_locator.split('/')[1])).sha256,resumed.sha256);
 const replay=await inspectLarge(f,opts);
 assert.equal(replay.staging_receipt.created_chunks,0);
 assert.equal(replay.staging_receipt.reused_chunks,4);
 assert.equal((await readdir(join(b,'objects'))).length,4);
});
test('R1 tampered chunk fails closed both readback and repeat staging',async t=>{
 const dir=await box(t),f=join(dir,'asset.bin'),b=join(dir,'buffer');await fixture(f,2);
 const opt={stage:true,acceptLocalCopy:true,bufferDir:b,chunkBytes:MiB,maxBytes:10*MiB};
 const receipt=await inspectLarge(f,opt);
 const c=receipt.chunks[0];
 await writeFile(join(b,'objects','sha256-'+c.sha256+'.chunk'),'tamper');
 await assert.rejects(verifyStaged(b,receipt.manifest_locator.split('/')[1]),/CHUNK_BYTE_COUNT_MISMATCH|CHUNK_TAMPER_OR_COLLISION/);
 await assert.rejects(inspectLarge(f,opt),/CHUNK_BYTE_COUNT_MISMATCH|CHUNK_TAMPER_OR_COLLISION/);
});
test('R1 direct file only and no symlink traversal on input',async t=>{
 const dir=await box(t),f=join(dir,'file.bin');await writeFile(f,'hello');
 await assert.rejects(inspectLarge(dir),/NOT_A_REGULAR_DIRECT_FILE/);
 const sym=join(dir,'link.bin');
 try{await symlink(f,sym)}catch(e){t.skip('symlink unsupported '+e.code);return}
 await assert.rejects(inspectLarge(sym),/NOT_A_REGULAR_DIRECT_FILE/);
});
test('R1 symbolic buffer path rejected',async t=>{
 const dir=await box(t),f=join(dir,'file.bin');await writeFile(f,'hello');
 const target=join(dir,'target');await mkdir(target);const link=join(dir,'link');
 try{await symlink(target,link)}catch(e){t.skip('symlink unsupported '+e.code);return}
 await assert.rejects(inspectLarge(f,{stage:true,bufferDir:link,acceptLocalCopy:true}),/BUFFER_DIRECTORY_INVALID/);
});
test('R1 rejects malicious manifest names without opening arbitrary paths',async t=>{
 const dir=await box(t);await assert.rejects(verifyStaged(dir,'../../secret.json'),/INVALID_HASH_BOUND_MANIFEST_NAME/);
});
test('R1 empty file capsule roundtrip is valid with zero chunks',async t=>{
 const dir=await box(t),f=join(dir,'empty.bin'),b=join(dir,'buf');await writeFile(f,'');
 const r=await inspectLarge(f,{stage:true,bufferDir:b,acceptLocalCopy:true,chunkBytes:MiB});
 assert.equal(r.byte_count,0);assert.equal(r.chunk_count,0);
 assert.equal((await verifyStaged(b,r.manifest_locator.split('/')[1])).byte_count,0);
});
test('R1 invalid resource budgets fail before performing I/O',async t=>{
 const dir=await box(t),f=join(dir,'tiny');await writeFile(f,'x');
 await assert.rejects(inspectLarge(f,{maxBytes:ABSOLUTE_MAX_BYTES+1}),/INVALID_DECLARED_BYTE_BUDGET/);
 await assert.rejects(inspectLarge(f,{chunkBytes:13}),/INVALID_CHUNK_SIZE/);
 await assert.rejects(inspectLarge(f,{maxBytes:0}),/FILE_EXCEEDS_DECLARED_BUDGET/);
 assert.equal(DEFAULT_MAX_BYTES,16*1024**3);
});
test('R1 refuses over-large sparse file cheaply before hashing',async t=>{
 const dir=await box(t),f=join(dir,'large.placeholder');await writeFile(f,'');
 await truncate(f,DEFAULT_MAX_BYTES+1);
 await assert.rejects(inspectLarge(f),/FILE_EXCEEDS_DECLARED_BUDGET/);
});
test('R1 >512 MiB sparse file is fully streamed in preview mode without materializing bytes',async t=>{
 if(process.env.CO_THUMB_LARGE_TEST!=='1'){t.skip('large-path regression opted in via CO_THUMB_LARGE_TEST=1');return}
 const dir=await box(t),f=join(dir,'sparse-600MiB.bin');await writeFile(f,'');
 await truncate(f,600*MiB); // sparse, avoids disk allocation; scan still touches exact 600 MiB.
 const before=process.memoryUsage().rss;
 const r=await inspectLarge(f,{chunkBytes:16*MiB,maxBytes:1024*MiB});
 const after=process.memoryUsage().rss;
 assert.equal(r.byte_count,600*MiB);assert.equal(r.chunk_count,38);
 assert.ok(after-before<256*MiB,'fixed memory bound, actual measured RSS delta: '+(after-before));
 assert.equal(r.state,'SOURCE_PREVIEW_ONLY');
});
