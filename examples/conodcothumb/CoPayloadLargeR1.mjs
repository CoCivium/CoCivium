#!/usr/bin/env node
/*
 CoPayloadLarge R1: deliberately bounded, offline, content-addressed, chunked
 rich-file capsule with resumption after interruption. No clipboard, mouse
 hooks, login, network, third-party sends, device controls, or auto-sharing.
 A private buffer is NOT independent custody, receiver ACK, or canonical truth.
*/
import { constants } from 'node:fs';
import { lstat, mkdir, open, link, readFile, rm } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { basename, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const SCHEMA = 'CoPayload.LocalChunkedCapsule.R1';
export const DEFAULT_MAX_BYTES = 16 * 1024 ** 3;
export const ABSOLUTE_MAX_BYTES = 64 * 1024 ** 3;
export const DEFAULT_CHUNK_BYTES = 8 * 1024 ** 2;
export const MAX_CHUNKS = 8192;
const NOFOLLOW = constants.O_NOFOLLOW || 0;
const SHA = /^[0-9a-f]{64}$/;
const MIME = {'.mp4':'video/mp4','.mkv':'video/x-matroska','.mov':'video/quicktime',
  '.webm':'video/webm','.png':'image/png','.jpeg':'image/jpeg','.jpg':'image/jpeg',
  '.wav':'audio/wav','.flac':'audio/flac','.pdf':'application/pdf','.zip':'application/zip',
  '.json':'application/json','.bin':'application/octet-stream'};

function fail(code) { throw new Error(code); }
function validOptions(opts={}) {
  const maxBytes = opts.maxBytes ?? DEFAULT_MAX_BYTES;
  const chunkBytes = opts.chunkBytes ?? DEFAULT_CHUNK_BYTES;
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 0 || maxBytes > ABSOLUTE_MAX_BYTES)
    fail('INVALID_DECLARED_BYTE_BUDGET');
  if (![1, 2, 4, 8, 16].includes(chunkBytes / 1024 ** 2))
    fail('INVALID_CHUNK_SIZE');
  return { maxBytes, chunkBytes };
}
async function statPlain(path) {
  const s = await lstat(path);
  if (!s.isFile() || s.isSymbolicLink()) fail('NOT_A_REGULAR_DIRECT_FILE');
  return s;
}
function sameStat(a,b) {
  return a.size === b.size && a.dev === b.dev && a.ino === b.ino &&
         a.mtimeMs === b.mtimeMs && a.ctimeMs === b.ctimeMs;
}
async function openPlain(filePath, maxBytes) {
  if (!filePath || typeof filePath !== 'string') fail('EXPLICIT_SOURCE_PATH_REQUIRED');
  const named = await statPlain(filePath);
  if (named.size > maxBytes) fail('FILE_EXCEEDS_DECLARED_BUDGET');
  const f = await open(filePath, constants.O_RDONLY | NOFOLLOW);
  try {
    const actual = await f.stat();
    if (!actual.isFile() || !sameStat(named,actual)) fail('SOURCE_CHANGED_BEFORE_OPEN');
    return { f, before: actual };
  } catch (e) { await f.close(); throw e; }
}
async function readExactly(f, buf, n, position) {
  let taken=0;
  while(taken < n) {
    const r = await f.read(buf, taken, n-taken, position+taken);
    if (r.bytesRead === 0) fail('UNEXPECTED_SOURCE_EOF');
    taken += r.bytesRead;
  }
}
function chunkPath(objectDir,hash) {
  if (!SHA.test(hash)) fail('INVALID_CHUNK_DIGEST');
  return join(objectDir, 'sha256-' + hash + '.chunk');
}
function capsule({wholeHash,bytes,chunks,chunkBytes,mode,mimeHint}) {
  return {
    schema:SCHEMA,
    state: mode==='stage'?'STAGED_LOCAL_ONLY':'SOURCE_PREVIEW_ONLY',
    payload_id:'sha256:'+wholeHash,
    sha256:wholeHash,
    byte_count:bytes,
    chunk_bytes:chunkBytes,
    chunk_count:chunks.length,
    chunks,
    payload_type_hint:mimeHint,
    payload_type_evidence:'UNTRUSTED_FILE_EXTENSION_ONLY',
    provenance:{selection:'EXPLICIT_FILE_PATH',bytes:'READ_FROM_OPEN_FILE_DESCRIPTOR'},
    privacy:'PRIVATE_LOCAL', authority:'NONE', receiver_ack:false,
    external_effects:{network:0,clipboard_read:0,device_input:0,send:0,provider_calls:0},
    resource_rails:{max_active_effect_workers:1, streaming_buffer_bytes:chunkBytes,
                    max_addressable_bytes:ABSOLUTE_MAX_BYTES},
    nonclaims:['NOT_MOUSE_BINDING','NOT_PUBLIC_UPLOAD','NOT_RECEIVER_READPROOF',
      'NOT_CUSTODY_ROOT','NOT_TAMPER_PROOF_AUTHENTICITY','NOT_SEMANTIC_REVIEW']
  };
}
async function privateDirectory(dir,create) {
  if (typeof dir!=='string' || !dir) fail('EXPLICIT_BUFFER_DIRECTORY_REQUIRED');
  if (create) await mkdir(dir,{recursive:true,mode:0o700});
  const s=await lstat(dir);
  if (!s.isDirectory() || s.isSymbolicLink()) fail('BUFFER_DIRECTORY_INVALID');
  return resolve(dir);
}
async function writeChunkOnce(objectDir,digest,view) {
  const target=chunkPath(objectDir,digest);
  const tmp=join(objectDir,'.temporary-'+randomUUID());
  let created=false;
  try {
    const handle=await open(tmp,'wx',0o600);
    created=true;
    try { await handle.writeFile(view); await handle.sync(); }
    finally { await handle.close(); }
    let reused=false;
    try { await link(tmp,target); }
    catch(e) { if(e.code!=='EEXIST') throw e; reused=true; }
    // Validate complete bytes, including pre-existing content for retry safety.
    await verifyChunk(target,digest,view.length);
    return { reused };
  } finally {
    if(created) await rm(tmp,{force:true}).catch(()=>{});
  }
}
async function verifyChunk(path,expected,expectedBytes) {
  const {f,before}=await openPlain(path,expectedBytes);
  try {
    if(before.size!==expectedBytes) fail('CHUNK_BYTE_COUNT_MISMATCH');
    const h=createHash('sha256');
    const buf=Buffer.allocUnsafe(Math.min(1024*1024,Math.max(1,expectedBytes)));
    let pos=0;
    while(pos<expectedBytes) {
      const take=Math.min(buf.length,expectedBytes-pos);
      await readExactly(f,buf,take,pos);
      h.update(buf.subarray(0,take)); pos+=take;
    }
    if(h.digest('hex')!==expected) fail('CHUNK_TAMPER_OR_COLLISION');
    const after=await f.stat();
    if(!sameStat(before,after)) fail('CHUNK_CHANGED_WHILE_VERIFYING');
  } finally { await f.close(); }
}
async function installManifest(root,manifest) {
  const dir=join(root,'manifests');
  await privateDirectory(dir,true);
  const final=join(dir,'sha256-'+manifest.sha256+'-chunks-'+manifest.chunk_bytes+'.json');
  const tmp=join(dir,'.temporary-'+randomUUID());
  let created=false;
  try {
    const f=await open(tmp,'wx',0o600); created=true;
    try { await f.writeFile(JSON.stringify(manifest,null,2)+'\n'); await f.sync(); }
    finally { await f.close(); }
    try { await link(tmp,final); }
    catch(e) {
      if(e.code!=='EEXIST') throw e;
      const ebytes=await readFile(final);
      if(ebytes.length>1024*1024) fail('MANIFEST_TOO_LARGE');
      const existing=JSON.parse(ebytes.toString('utf8'));
      if(JSON.stringify(existing)!==JSON.stringify(manifest)) fail('MANIFEST_CONFLICT');
    }
  } finally { if(created) await rm(tmp,{force:true}).catch(()=>{}); }
  return basename(final);
}

export async function inspectLarge(filePath,options={}) {
  const cfg=validOptions(options);
  const mode=options.stage===true?'stage':'preview';
  if(mode==='stage' && options.acceptLocalCopy!==true)
    fail('EXPLICIT_LOCAL_COPY_CONSENT_REQUIRED');
  if(options.interruptAfterChunks!==undefined && mode!=='stage')
    fail('INTERRUPT_TEST_REQUIRES_STAGE');
  const {f,before}=await openPlain(filePath,cfg.maxBytes);
  let root=null;
  let objectDir=null;
  let copied=0,reused=0;
  try {
    if(Math.ceil(before.size/cfg.chunkBytes)>MAX_CHUNKS) fail('CHUNK_COUNT_BUDGET_EXCEEDED');
    if(mode==='stage') {
      root=await privateDirectory(options.bufferDir,true);
      objectDir=join(root,'objects');
      await privateDirectory(objectDir,true);
    }
    const buf=Buffer.allocUnsafe(cfg.chunkBytes);
    const whole=createHash('sha256');
    const chunks=[];
    let position=0;
    while(position<before.size) {
      const n=Math.min(cfg.chunkBytes,before.size-position);
      await readExactly(f,buf,n,position);
      const view=buf.subarray(0,n);
      const digest=createHash('sha256').update(view).digest('hex');
      whole.update(view);
      if(mode==='stage') {
        const c=await writeChunkOnce(objectDir,digest,view);
        if(c.reused) reused++; else copied++;
      }
      chunks.push({index:chunks.length,sha256:digest,byte_count:n});
      position+=n;
      if(chunks.length>MAX_CHUNKS) fail('CHUNK_COUNT_BUDGET_EXCEEDED');
      if(mode==='stage' && options.interruptAfterChunks===chunks.length)
        fail('INJECTED_RECOVERY_TEST_INTERRUPTION');
    }
    const after=await f.stat();
    const current=await statPlain(filePath);
    if(!sameStat(before,after) || !sameStat(before,current))
      fail('SOURCE_CHANGED_DURING_SCAN');
    const wholeHash=whole.digest('hex');
    const hint=MIME[extname(filePath).toLowerCase()]||'application/octet-stream';
    const result=capsule({wholeHash,bytes:position,chunks,chunkBytes:cfg.chunkBytes,mode,mimeHint:hint});
    if(mode==='stage') {
      const name=await installManifest(root,result);
      return {...result, manifest_locator:'manifests/'+name,
              staging_receipt:{created_chunks:copied,reused_chunks:reused,exact_chunk_reads:true}};
    }
    return result;
  } finally { await f.close(); }
}

export async function verifyStaged(bufferDir,manifestName) {
  const root=await privateDirectory(bufferDir,false);
  if(typeof manifestName!=='string' ||
     !/^sha256-[0-9a-f]{64}-chunks-(1048576|2097152|4194304|8388608|16777216)\.json$/.test(manifestName))
    fail('INVALID_HASH_BOUND_MANIFEST_NAME');
  const name=join(root,'manifests',manifestName);
  const stat=await statPlain(name);
  if(stat.size>1024*1024) fail('MANIFEST_TOO_LARGE');
  const data=JSON.parse(await readFile(name,'utf8'));
  if(data.schema!==SCHEMA || data.state!=='STAGED_LOCAL_ONLY' ||
     !SHA.test(data.sha256) || data.payload_id!=='sha256:'+data.sha256 ||
     !Number.isSafeInteger(data.byte_count)||data.byte_count<0||data.byte_count>ABSOLUTE_MAX_BYTES ||
     !Number.isSafeInteger(data.chunk_bytes)||
     !Array.isArray(data.chunks)||data.chunks.length>MAX_CHUNKS ||
     data.chunks.length!==Math.ceil(data.byte_count/data.chunk_bytes) ||
     manifestName!=='sha256-'+data.sha256+'-chunks-'+data.chunk_bytes+'.json')
     fail('MANIFEST_INVALID');
  const hasher=createHash('sha256');
  let bytes=0;
  const scratch=Buffer.allocUnsafe(1024*1024);
  for(const [i,c] of data.chunks.entries()) {
    if(c.index!==i||!SHA.test(c.sha256)||!Number.isSafeInteger(c.byte_count)||
       c.byte_count<1||c.byte_count>data.chunk_bytes ||
       (i<data.chunks.length-1&&c.byte_count!==data.chunk_bytes))
       fail('INVALID_CHUNK_RECORD');
    const file=chunkPath(join(root,'objects'),c.sha256);
    const {f,before}=await openPlain(file,c.byte_count);
    try {
      if(before.size!==c.byte_count) fail('CHUNK_BYTE_COUNT_MISMATCH');
      let pos=0; const h=createHash('sha256');
      while(pos<c.byte_count) {
        const n=Math.min(scratch.length,c.byte_count-pos);
        await readExactly(f,scratch,n,pos);
        const view=scratch.subarray(0,n);
        h.update(view); hasher.update(view); pos+=n;
      }
      if(h.digest('hex')!==c.sha256) fail('CHUNK_TAMPER_OR_COLLISION');
      if(!sameStat(before,await f.stat())) fail('CHUNK_CHANGED_WHILE_VERIFYING');
      bytes+=c.byte_count;
    } finally { await f.close(); }
  }
  if(bytes!==data.byte_count || hasher.digest('hex')!==data.sha256)
    fail('CAPSULE_CONTENT_DIGEST_MISMATCH');
  return {schema:'CoPayload.Readback.R1',state:'VERIFIED_LOCAL_BYTES',
    sha256:data.sha256,byte_count:bytes,chunk_count:data.chunks.length,
    receiver_ack:false,independent_custody:false,external_effects:{send:0,network:0}};
}

function usage() {
  return [
    'Local, zero-network, exact-byte large payload canary. No physical gesture binding.',
    '  node CoPayloadLargeR1.mjs --preview <file>',
    '  node CoPayloadLargeR1.mjs --stage <file> --buffer-dir <private-dir> --accept-local-copy',
    '  node CoPayloadLargeR1.mjs --verify <hash-bound-manifest-name> --buffer-dir <private-dir>',
    'Default max 16 GiB; chunks 8 MiB; max supported 64 GiB with explicit budgets via module API.'
  ].join('\n');
}

if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const a=process.argv.slice(2);
  try {
    let result;
    if(a.length===2 && a[0]==='--preview') result=await inspectLarge(a[1]);
    else if(a.length===5 && a[0]==='--stage' && a[2]==='--buffer-dir' && a[4]==='--accept-local-copy')
      result=await inspectLarge(a[1],{stage:true,bufferDir:a[3],acceptLocalCopy:true});
    else if(a.length===4 && a[0]==='--verify' && a[2]==='--buffer-dir')
      result=await verifyStaged(a[3],a[1]);
    else { console.log(usage()); process.exitCode=a.length===0||a[0]==='--help'?0:2; }
    if(result) console.log(JSON.stringify(result,null,2));
  } catch(e) { console.error('CoPayloadLarge R1 HOLD: '+(e.code||e.message)); process.exitCode=1; }
}
