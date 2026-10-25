import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdtempSync, mkdirSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { compile, replaySlice, sha256, exactParagraphs, SCHEMA } from '../CoContextAmpR0.mjs';

const root = new URL('../fixture/', import.meta.url).pathname;
const manifest = JSON.parse(readFileSync(join(root,'manifest.json'),'utf8'));
const params = {root,manifest,question:'How does CoContextWare assemble context and verify source evidence?',max_excerpt_bytes:900};
function changed(mutator){const m=structuredClone(manifest);mutator(m);return {...params,manifest:m};}

test('01 basic deterministic source-bound context plan',()=>{
  const a=compile(params), b=compile(params);
  assert.deepEqual(a,b);
  assert.equal(a.schema,SCHEMA);
  assert.equal(a.state,'PASS_SHADOW_PLAN');
  assert.equal(a.selected[0].source_id,'fabric');
  assert.match(a.selected[0].excerpt,/CoContextWare/);
});
test('02 exact source slice replay and hashes',()=>{
  const p=compile(params);
  for(const s of p.selected){
    const source=manifest.sources.find(row=>row.id===s.source_id);
    assert.equal(replaySlice({root,source,fragment:s}),s.excerpt);
    assert.equal(sha256(Buffer.from(s.excerpt)),s.segment_sha256);
  }
});
test('03 context excerpt budget is strict',()=>{
  const p=compile({...params,max_excerpt_bytes:128});
  assert.ok(p.excerpt_budget.used_excerpt_bytes<=128);
  assert.ok(p.selected.every(x=>x.byte_count<=128));
});
test('04 no truncation or fake compression of a larger paragraph',()=>{
  const p=compile({...params,max_excerpt_bytes:128,max_slices:1});
  assert.ok(p.selected.every(x=>x.byte_count===Buffer.byteLength(x.excerpt)));
  assert.ok(p.omitted_candidate_count>=1);
});
test('05 source hash mismatch yields HOLD and excludes source',()=>{
  const p=compile(changed(m=>m.sources[0].sha256='0'.repeat(64)));
  assert.equal(p.source_qualification.holds[0].status,'HOLD_HASH_MISMATCH');
  assert.ok(p.selected.every(x=>x.source_id!=='fabric'));
});
test('06 source privacy blocks reads and does not reveal data',()=>{
  const p=compile(changed(m=>{m.sources[0].privacy='PRIVATE';m.sources[0].path='../../secrets';}));
  assert.equal(p.source_qualification.holds[0].status,'HOLD_PRIVACY_OR_AUTHORITY');
  assert.ok(!JSON.stringify(p).includes('secrets'));
});
test('07 authority not inherited from a pointer',()=>{
  const p=compile(changed(m=>m.sources[0].authority='EXECUTE'));
  assert.equal(p.source_qualification.holds[0].status,'HOLD_PRIVACY_OR_AUTHORITY');
  assert.equal(p.authority,'NONE');
});
test('08 stale source is HELD and cannot be used',()=>{
  const p=compile(changed(m=>m.sources[0].currentness='STALE'));
  assert.equal(p.source_qualification.holds[0].status,'HOLD_UNQUALIFIED_CURRENTNESS');
});
test('09 missing source not invented',()=>{
  const p=compile(changed(m=>m.sources[0].path='absent.txt'));
  assert.equal(p.source_qualification.holds[0].status,'HOLD_SOURCE_UNAVAILABLE_OR_UNSAFE');
});
test('10 parent-path traversal is blocked',()=>{
  const p=compile(changed(m=>m.sources[0].path='../fixture/fabric.txt'));
  assert.equal(p.source_qualification.holds[0].status,'HOLD_SOURCE_UNAVAILABLE_OR_UNSAFE');
});
test('11 source symlink outside root is blocked',()=>{
  const d=mkdtempSync(join(tmpdir(),'cocontextamp-r0-'));
  mkdirSync(join(d,'public'));
  writeFileSync(join(d,'outside.txt'),'Protected test value');
  symlinkSync(join(d,'outside.txt'),join(d,'public','link.txt'));
  const m={format:manifest.format,sources:[{id:'trap',path:'link.txt',privacy:'PUBLIC',authority:'READ_ONLY_PUBLIC',currentness:'DECLARED_CURRENT',sha256:sha256('Protected test value')}]};
  const p=compile({root:join(d,'public'),manifest:m,question:'Protected value'});
  assert.equal(p.state,'HELD_NO_ADMISSIBLE_RELEVANT_SOURCE');
  assert.equal(p.source_qualification.holds[0].status,'HOLD_SOURCE_UNAVAILABLE_OR_UNSAFE');
  assert.ok(!JSON.stringify(p).includes('Protected test value'));
});
test('12 same source id cannot be silently duplicated',()=>{
  assert.throws(()=>compile(changed(m=>m.sources[1].id=m.sources[0].id)),/BAD_SOURCE_ID/);
});
test('13 unsupported budget bounds fail closed',()=>{
  assert.throws(()=>compile({...params,max_excerpt_bytes:8193}),/BAD_EXCERPT_BUDGET/);
  assert.throws(()=>compile({...params,max_slices:100}),/BAD_SLICE_LIMIT/);
});
test('14 malformed source manifest fails closed',()=>{
  assert.throws(()=>compile({...params,manifest:{sources:[]}}),/BAD_SOURCE_MANIFEST/);
});
test('15 open-world unknown remains held without a claim',()=>{
  const p=compile({...params,question:'Unmeasured omnipotent accelerator'});
  assert.equal(p.state,'HELD_NO_ADMISSIBLE_RELEVANT_SOURCE');
  assert.equal(p.selected.length,0);
});
test('16 no external effects or worker spawning',()=>{
  const p=compile(params);
  assert.deepEqual(Object.values(p.effects),[0,0,0,0,0,0,0]);
  assert.equal(p.authority,'NONE');
});
test('17 fake or altered source cannot replay selected slice',()=>{
  const p=compile(params),source={...manifest.sources[0],sha256:'1'.repeat(64)};
  assert.throws(()=>replaySlice({root,source,fragment:p.selected[0]}),/HOLD_REPLAY_MISMATCH/);
});
test('18 utf8 byte offsets preserved',()=>{
  const src=Buffer.from('Test first.\n\nCaf\u00e9 and orbital evidence.');
  const pieces=exactParagraphs(src);
  assert.equal(pieces[1].start_byte,13);
  assert.equal(src.subarray(pieces[1].start_byte,pieces[1].end_byte).toString('utf8'),'Caf\u00e9 and orbital evidence.');
});
test('19 scores track relevant source, not first paragraph',()=>{
  const p=compile({...params,question:'CoTurtle contrary evidence'});
  assert.match(p.selected[0].excerpt,/CoTurtle/);
  assert.doesNotMatch(readFileSync(join(root,'fabric.txt'),'utf8').split('\n\n')[0],/CoTurtle/);
});
test('20 all selections preserve independently retrievable exact IDs',()=>{
  const p=compile(params);
  assert.ok(p.selected.every(x=>x.source_id&&x.source_sha256&&x.segment_sha256&&Number.isInteger(x.start_byte)&&Number.isInteger(x.end_byte)));
});
test('21 provenance and loss boundaries are explicit',()=>{
  const p=compile(params);
  assert.match(p.loss_notice,/omitted, not disproved/);
  assert.ok(p.nonclaims.includes('CHAR_BUDGET_NE_MODEL_TOKEN_COUNT'));
  assert.ok(p.nonclaims.includes('SOURCE_PLAN_NE_PROVIDER_CONTEXT_MUTATION'));
});
