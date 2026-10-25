#!/usr/bin/env node
// CoContextAmp R0: public, local, read-only source-bound selective retrieval.
// A context compiler, not a tokenizer extension or device/provider controller.
import { createHash } from 'node:crypto';
import { readFileSync, lstatSync, realpathSync } from 'node:fs';
import { dirname, isAbsolute, resolve, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

export const SCHEMA = 'CoContextAmp.ShadowPlan.R0';
const MAX_SOURCE_BYTES = 1024 * 1024;
const MAX_SOURCES = 32;
const MAX_CANDIDATES = 256;
const STOPWORDS = new Set('a an and are as at be by can do does for from how i in is it of on or our should that the their them there these this to we what when where who why will with you your'.split(' '));
export const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const tokens = (s) => [...new Set((s.toLowerCase().match(/[a-z0-9]{2,}/g) || []).filter(t => !STOPWORDS.has(t)))];
const plainObject = (o) => o !== null && typeof o === 'object' && !Array.isArray(o);
function qualifiedPath(root, name) {
  if (typeof name !== 'string' || !name || isAbsolute(name) || name.includes('\\') || name.split('/').some(x => x === '..' || x === '.' || !x)) throw new Error('INVALID_SOURCE_RELATIVE_PATH');
  const top = realpathSync(root);
  const target = resolve(top, name);
  const rel = relative(top, target);
  if (rel.startsWith('..' + sep) || rel === '..' || isAbsolute(rel)) throw new Error('SOURCE_OUTSIDE_ROOT');
  const actual = realpathSync(target);
  const actualRel = relative(top, actual);
  if (actualRel.startsWith('..' + sep) || actualRel === '..' || isAbsolute(actualRel)) throw new Error('SOURCE_SYMLINK_ESCAPE');
  if (!lstatSync(target).isFile()) throw new Error('NOT_REGULAR_FILE');
  return actual;
}
export function exactParagraphs(bytes) {
  const raw = bytes.toString('utf8');
  if (!Buffer.from(raw, 'utf8').equals(bytes)) throw new Error('SOURCE_NOT_UTF8');
  const pieces = [];
  const separator = /(?:\r?\n){2,}/g;
  let pos = 0, m;
  while ((m = separator.exec(raw)) !== null) {
    if (m.index > pos) pieces.push([pos, m.index]);
    pos = m.index + m[0].length;
  }
  if (pos < raw.length) pieces.push([pos, raw.length]);
  return pieces.filter(([a,b]) => raw.slice(a,b).trim()).map(([a,b]) => {
    const start = Buffer.byteLength(raw.slice(0,a), 'utf8');
    const end = Buffer.byteLength(raw.slice(0,b), 'utf8');
    const chunk = bytes.subarray(start,end);
    return { start_byte:start, end_byte:end, byte_count:chunk.length, excerpt:chunk.toString('utf8'), segment_sha256:sha256(chunk) };
  });
}
export function compile({ root, manifest, question, max_excerpt_bytes=900, max_slices=3 }={}) {
  if (!plainObject(manifest) || manifest.format !== 'CoContextAmp.SourceManifest.R0' || !Array.isArray(manifest.sources) || manifest.sources.length > MAX_SOURCES) throw new Error('BAD_SOURCE_MANIFEST');
  if (typeof question !== 'string' || !question.trim() || question.length > 512) throw new Error('BAD_QUESTION');
  if (!Number.isSafeInteger(max_excerpt_bytes) || max_excerpt_bytes < 128 || max_excerpt_bytes > 8192) throw new Error('BAD_EXCERPT_BUDGET');
  if (!Number.isSafeInteger(max_slices) || max_slices < 1 || max_slices > 8) throw new Error('BAD_SLICE_LIMIT');
  const terms = tokens(question);
  if (!terms.length) throw new Error('NO_SEARCH_TERMS');
  const candidates = [], holds=[], qualified=[], seen = new Set();
  for (const s of manifest.sources) {
    if (!plainObject(s) || typeof s.id !== 'string' || !/^[a-zA-Z0-9_.-]{1,80}$/.test(s.id) || seen.has(s.id)) throw new Error('BAD_SOURCE_ID');
    seen.add(s.id);
    if (s.privacy !== 'PUBLIC' || s.authority !== 'READ_ONLY_PUBLIC') { holds.push({source_id:s.id,status:'HOLD_PRIVACY_OR_AUTHORITY'}); continue; }
    if (s.currentness !== 'DECLARED_CURRENT') { holds.push({source_id:s.id,status:'HOLD_UNQUALIFIED_CURRENTNESS'}); continue; }
    if (typeof s.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(s.sha256)) { holds.push({source_id:s.id,status:'HOLD_INVALID_HASH'}); continue; }
    let data;
    try {
      const p = qualifiedPath(root,s.path);
      const size = lstatSync(p).size;
      if (size > MAX_SOURCE_BYTES) {holds.push({source_id:s.id,status:'HOLD_SOURCE_TOO_LARGE'});continue;}
      data = readFileSync(p);
    } catch (e) { holds.push({source_id:s.id,status:'HOLD_SOURCE_UNAVAILABLE_OR_UNSAFE'}); continue; }
    const actualSha = sha256(data);
    if (actualSha !== s.sha256) {holds.push({source_id:s.id,status:'HOLD_HASH_MISMATCH'});continue;}
    qualified.push(s.id);
    for (const piece of exactParagraphs(data)) {
      const lower = piece.excerpt.toLowerCase();
      const hits = terms.filter(t => new RegExp('(?:^|[^a-z0-9])'+t+'(?:$|[^a-z0-9])').test(lower));
      if (!hits.length) continue;
      candidates.push({...piece,source_id:s.id,source_sha256:s.sha256,source_ref:typeof s.source_ref==='string'?s.source_ref:null,
        match_terms:hits,score:hits.length,byte_exact:true});
      if (candidates.length >= MAX_CANDIDATES) break;
    }
    if (candidates.length >= MAX_CANDIDATES) {holds.push({source_id:s.id,status:'HOLD_CANDIDATE_CAP'});break;}
  }
  candidates.sort((a,b)=>b.score-a.score || a.source_id.localeCompare(b.source_id) || a.start_byte-b.start_byte);
  const selected=[], dupes=new Set(); let used = 0;
  for(const c of candidates) {
    if (selected.length >= max_slices) break;
    if (dupes.has(c.segment_sha256)) continue;
    if (used + c.byte_count > max_excerpt_bytes) continue; // whole exact excerpt only
    dupes.add(c.segment_sha256);
    selected.push(c); used += c.byte_count;
  }
  const state = selected.length ? holds.length ? 'PARTIAL_SHADOW_PLAN' : 'PASS_SHADOW_PLAN' : 'HELD_NO_ADMISSIBLE_RELEVANT_SOURCE';
  return {
    schema:SCHEMA,state,question,request_terms:terms,selected,source_qualification:{qualified_ids:qualified,holds},
    excerpt_budget:{max_excerpt_bytes,used_excerpt_bytes:used,max_slices,selected_slices:selected.length},
    omitted_candidate_count:candidates.length-selected.length,
    loss_notice:'Only selected byte-exact paragraphs are shown. All other source content is omitted, not disproved. Exact rehydration requires original source bytes and hash verification.',
    effects:{network:0,send:0,model:0,workers:0,provider_context_mutation:0,source_mutation:0,receiver_ack:0},
    authority:'NONE',
    next:'Use these source-bound excerpts as a local proposal. Test meaning and provenance before any authorized model invocation.',
    nonclaims:['ADDRESSABLE_NE_LOADED','CHAR_BUDGET_NE_MODEL_TOKEN_COUNT','EXCERPTS_NE_COMPLETE_KNOWLEDGE','SUMMARY_NE_SOURCE','POINTER_NE_ACK','LARGE_PAYLOAD_NE_INFINITE_CONTEXT','QUALIFIED_PUBLIC_SOURCE_NE_INDEPENDENT_TRUTH','SOURCE_PLAN_NE_PROVIDER_CONTEXT_MUTATION','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF']
  };
}
export function replaySlice({root,source,fragment}) {
  if (source.privacy!=='PUBLIC' || source.authority!=='READ_ONLY_PUBLIC') throw new Error('HOLD_PRIVACY');
  const data=readFileSync(qualifiedPath(root,source.path));
  if(sha256(data)!==source.sha256 || sha256(data.subarray(fragment.start_byte,fragment.end_byte))!==fragment.segment_sha256)throw new Error('HOLD_REPLAY_MISMATCH');
  return data.subarray(fragment.start_byte,fragment.end_byte).toString('utf8');
}
const invoked = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invoked) {
  const [manifestPath, question, budgetArg] = process.argv.slice(2);
  if(!manifestPath || !question){ console.error('Usage: node CoContextAmpR0.mjs <public-manifest.json> <question> [max-excerpt-bytes]'); process.exitCode=2; }
  else {
    try {
      const plan = compile({root:dirname(resolve(manifestPath)),manifest:JSON.parse(readFileSync(manifestPath,'utf8')),question,
        max_excerpt_bytes:budgetArg ? Number(budgetArg):900});
      console.log(JSON.stringify(plan,null,2));
    } catch(e) {console.error(JSON.stringify({status:'FAIL_CLOSED',reason:String(e.message||e)}));process.exitCode=1;}
  }
}
