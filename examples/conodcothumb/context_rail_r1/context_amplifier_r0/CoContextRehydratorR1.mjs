/*
 * CoContextRehydrator R1 - explicit, bounded, read-only, local-public source adapter.
 * Shadow canary. No network, output-token claims, providers, mouse, or send.
 * Scoped to an explicitly supplied local fixture root, selected plan, and opt-in.
 */
import * as fs from 'node:fs/promises';
import { constants as FS } from 'node:fs';
import * as path from 'node:path';
import { createHash } from 'node:crypto';
import { TextDecoder } from 'node:util';

export const SCHEMA = 'CoAll.CoContextRehydrator.LocalShadowR1';
const SHA = /^[a-f0-9]{64}$/i;
const PART = /^[A-Za-z0-9_][A-Za-z0-9_.-]{0,79}$/;
const MAX_FILES = 32;
const MAX_BYTES = 8 * 1024 * 1024;
const HEX = (bytes) => createHash('sha256').update(bytes).digest('hex');
const NONCLAIMS = [
  'BYTES_NE_PROVIDER_TOKENS', 'LOCAL_VERIFICATION_NE_PROVIDER_INGESTION',
  'PATH_VALIDATION_NE_GENERAL_OS_SANDBOX', 'POINTER_NE_RECEIVER_ACK',
  'LOCAL_IS_NOT_LANDED', 'SELECTED_NE_TRUE',
  'CONTEXT_SELECTION_NE_UNLIMITED_CONTEXT', 'MODEL_QUALITY_NOT_MEASURED'
];
function shell(state) {
  return {
    schema: SCHEMA, state,
    sources: [], source_count: 0, bytes_verified: 0,
    content_materialized: false,
    manifest_sha256: null,
    tokenizer_state: 'HELD_NO_MODEL_SPECIFIC_TOKENIZER',
    model_context_tokens: null, receiver_ack: false, coex: false,
    effects: { local_reads: 0, network: 0, sends: 0, executes: 0, writes: 0 },
    nonclaims: NONCLAIMS
  };
}
function stop(reason) { return shell(reason); }
function safeRelative(ref) {
  if (typeof ref !== 'string' || !ref.startsWith('local:')) return null;
  const s = ref.slice('local:'.length);
  if (!s || s.length > 250 || s.includes('\\') || s.startsWith('/') || s.includes(':')) return null;
  const parts = s.split('/');
  if (!parts.every(p => PART.test(p) && p !== '.' && p !== '..')) return null;
  return parts;
}
function validSource(x) {
  return x && typeof x === 'object' && !Array.isArray(x) &&
    typeof x.id === 'string' && x.id.length > 0 && x.id.length <= 128 &&
    typeof x.sha256 === 'string' && SHA.test(x.sha256) &&
    safeRelative(x.source_ref) !== null;
}
const isSafeInteger = (x, max) => Number.isSafeInteger(x) && x >= 1 && x <= max;

export async function rehydrateLocalPlan(plan, options = {}) {
  if (!options || typeof options !== 'object' || options.explicitLocalRead !== true) {
    return stop('HOLD_EXPLICIT_LOCAL_READ_REQUIRED');
  }
  if (!plan || !['PROPOSAL_ONLY','PARTIAL_PROPOSAL_ONLY'].includes(plan.state) ||
      plan.schema !== 'CoAll.CoContextAmplifier.ShadowR0' ||
      !Array.isArray(plan.selected) || plan.selected.length > MAX_FILES ||
      typeof options.root !== 'string' || !options.root ||
      !isSafeInteger(options.maxTotalBytes, MAX_BYTES) ||
      !isSafeInteger(options.maxPerFileBytes, MAX_BYTES) ||
      options.maxPerFileBytes > options.maxTotalBytes ||
      ![true,false,undefined].includes(options.includeText)) {
    return stop('HOLD_INVALID_PLAN_OR_LIMIT');
  }
  if (!plan.selected.every(validSource)) return stop('HOLD_INVALID_PUBLIC_SOURCE_METADATA');
  const ids = plan.selected.map(s => s.id);
  if (new Set(ids).size !== ids.length) return stop('HOLD_DUPLICATE_SELECTED_ID');
  if (plan.selected.length === 0) {
    const empty = shell('VERIFIED_EMPTY');
    empty.manifest_sha256 = HEX(Buffer.from('[]'));
    return empty;
  }
  let rootReal;
  try {
    rootReal = await fs.realpath(options.root);
    if (!(await fs.stat(rootReal)).isDirectory()) return stop('HOLD_ROOT_UNAVAILABLE');
  } catch { return stop('HOLD_ROOT_UNAVAILABLE'); }
  const verified=[];
  let total=0;
  for (const item of plan.selected) {
    const parts = safeRelative(item.source_ref);
    let fd;
    try {
      // Refuse traversals and symlinks, including symlinked intermediate dirs.
      let loc=rootReal;
      for (let i=0;i<parts.length;i++) {
        loc=path.join(loc,parts[i]);
        const st=await fs.lstat(loc);
        if (st.isSymbolicLink()) return stop('HOLD_SYMLINK_OR_PATH_ESCAPE');
        if (i===parts.length-1 ? !st.isFile() : !st.isDirectory()) {
          return stop('HOLD_NONREGULAR_SOURCE');
        }
      }
      // O_NOFOLLOW guards final component where the host supports it.
      fd=await fs.open(loc,FS.O_RDONLY | (FS.O_NOFOLLOW || 0));
      const before=await fd.stat();
      if (!before.isFile()) return stop('HOLD_NONREGULAR_SOURCE');
      if (before.size > options.maxPerFileBytes || before.size + total > options.maxTotalBytes)
        return stop('HOLD_BYTE_BUDGET_EXCEEDED');
      const bytes=await fd.readFile();
      const after=await fd.stat();
      if (bytes.length !== before.size || before.size !== after.size ||
          before.ino !== after.ino || before.dev !== after.dev ||
          before.mtimeMs !== after.mtimeMs || before.ctimeMs !== after.ctimeMs)
        return stop('HOLD_SOURCE_CHANGED_DURING_READ');
      if (bytes.length + total > options.maxTotalBytes || bytes.length > options.maxPerFileBytes)
        return stop('HOLD_BYTE_BUDGET_EXCEEDED');
      const hash=HEX(bytes);
      if (hash !== item.sha256.toLowerCase()) return stop('HOLD_SHA256_MISMATCH');
      let text;
      try {text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);}
      catch {return stop('HOLD_INVALID_UTF8');}
      const entry={id:item.id,sha256:hash,verified_bytes:bytes.length,
        kind:item.kind || null,required:item.required===true};
      if (options.includeText===true) entry.text=text;
      verified.push(entry);
      total+=bytes.length;
    } catch { return stop('HOLD_READ_OR_PATH_FAILURE'); }
    finally { if (fd) await fd.close().catch(()=>{}); }
  }
  // Manifest identity excludes text content but includes real checked source digests.
  const manifest=verified.map(v=>({id:v.id,sha256:v.sha256,verified_bytes:v.verified_bytes}));
  return {
    ...shell(options.includeText ? 'TEXT_MATERIALIZED_LOCAL_ONLY' : 'SOURCE_BYTES_VERIFIED_LOCAL_ONLY'),
    sources:verified,source_count:verified.length,bytes_verified:total,
    content_materialized:options.includeText===true,
    manifest_sha256:HEX(Buffer.from(JSON.stringify(manifest),'utf8')),
    effects: {local_reads:verified.length,network:0,sends:0,executes:0,writes:0}
  };
}
