import test from 'node:test';
import assert from 'node:assert/strict';
import {compileContext,rehydrate,scoreSource,makeSyntheticSource,sha256,byteLength,SCHEMA}
  from './compiler.mjs';
import {sampleSources,sampleWork} from './fixture.mjs';

const clone=value=>JSON.parse(JSON.stringify(value));
const build=(work=sampleWork,sources=sampleSources)=>compileContext({work,sources});
const expectErr=(fn,code)=>assert.throws(fn,new RegExp(code));
const has=(result,id)=>result.packet.source_items.some(x=>x.id===id);
const restricted=makeSyntheticSource('source:restricted','POLICY','SENSITIVE',['alpha','plan'],
  'Fictional restricted research source');

test('01 pinned schema',()=>assert.equal(SCHEMA,'CoCivium.CoOmniContextPacket.R0'));
test('02 deterministic source fingerprints',()=>assert.equal(sha256('same'),sha256('same')));
test('03 source digest is proper SHA256',()=>assert.match(sampleSources[0].sha256,/^[a-f0-9]{64}$/));
test('04 context compiles with no side effects',()=>{
  const r=build();assert.equal(r.model_calls,0);assert.equal(r.network_calls,0);
  assert.equal(r.materialized_workers,0);assert.equal(r.receiver_ack,null);
  assert.ok(Object.values(r.packet.effects).every(x=>x===0));
});
test('05 exact byte budget includes JSON envelope',()=>{const r=build();assert.equal(byteLength(r.packet),r.packet_bytes);assert.ok(r.packet_bytes<=sampleWork.byte_budget)});
test('06 explicit no-effect authority retained',()=>assert.equal(build().packet.authority,'NONE'));
test('07 relevant challenge is always retained',()=>{const r=build();assert.ok(has(r,'source:beta'));assert.equal(r.packet.challenge_state,'CHALLENGE_INCLUDED')});
test('08 relevance prevents irrelevant content from displacing evidence',()=>{const r=build();assert.ok(!has(r,'source:delta'))});
test('09 input order preserves deterministic rank',()=>{
 const a=build(),b=build(sampleWork,[...sampleSources].reverse());
 assert.deepEqual(a.packet,b.packet);assert.equal(a.packet_sha256,b.packet_sha256);
});
test('10 source excerpts retain real source prefix',()=>{
 for(const x of build().packet.source_items)assert.ok(sampleSources.find(y=>y.id===x.id).text.startsWith(x.excerpt));
});
test('11 exact rehydration of elected source',()=>{
 const r=build(),out=rehydrate(r,sampleSources,'PUBLIC');
 assert.equal(out.exact_reconstruction,true);assert.equal(out.restored.length,r.packet.selected_count);
 for(const x of out.restored)assert.equal(x.exact_text,sampleSources.find(y=>y.id===x.id).text);
});
test('12 rehydration never grants new action authority',()=>{
 const out=rehydrate(build(),sampleSources,'PUBLIC');
 assert.equal(out.authority,'NONE');assert.ok(Object.values(out.effects).every(x=>x===0));
});
test('13 PUBLIC packet cannot leak LOCAL source',()=>{
 const work={...sampleWork,query:'alpha local'};const r=build(work);
 assert.ok(!has(r,'source:epsilon'));assert.equal(JSON.stringify(r).includes('source:epsilon'),false);
});
test('14 LOCAL receiver can retrieve properly-scoped local source',()=>{
 const r=build({...sampleWork,receiver:'LOCAL',query:'alpha local',max_items:5});
 assert.ok(has(r,'source:epsilon'));
});
test('15 sensitive scope never appears even with perfect lexical overlap',()=>{
 const r=build(sampleWork,[...sampleSources,restricted]);assert.equal(JSON.stringify(r).includes('source:restricted'),false);
});
test('16 unknown scope cannot be silently treated as public',()=>{
 const unknown=makeSyntheticSource('source:unknown','TEST','UNKNOWN',['alpha','test'],'Fictional unknown scope');
 assert.equal(JSON.stringify(build(sampleWork,[...sampleSources,unknown])).includes('source:unknown'),false);
});
test('17 wrong receiver cannot rehydrate',()=>expectErr(()=>rehydrate(build(),sampleSources,'LOCAL'),'RECEIVER_SCOPE_MISMATCH'));
test('18 missing source cannot be rehydrated',()=>{
 const r=build();const absent=sampleSources.filter(x=>x.id!==r.packet.source_items[0].id);
 expectErr(()=>rehydrate(r,absent,'PUBLIC'),'SOURCE_MISSING');
});
test('19 source text drift rejects before selection',()=>{
 const sources=clone(sampleSources);sources[0].text+=' mutation';
 expectErr(()=>build(sampleWork,sources),'SOURCE_HASH_MISMATCH');
});
test('20 source content drift rejects rehydration',()=>{
 const r=build(),sources=clone(sampleSources),id=r.packet.source_items[0].id;
 const row=sources.find(x=>x.id===id);row.text+=' changed';row.sha256=sha256(row.text);
 expectErr(()=>rehydrate(r,sources,'PUBLIC'),'REHYDRATION_SOURCE_CHANGED');
});
test('21 semantic metadata drift rejects rehydration',()=>{
 const r=build(),sources=clone(sampleSources),id=r.packet.source_items[0].id;
 sources.find(x=>x.id===id).tags.push('altered');
 expectErr(()=>rehydrate(r,sources,'PUBLIC'),'REHYDRATION_METADATA_CHANGED');
});
test('22 packet mutation rejected by digest',()=>{
 const r=clone(build());r.packet.work_id='work:modified';
 expectErr(()=>rehydrate(r,sampleSources,'PUBLIC'),'PACKET_DIGEST_MISMATCH');
});
test('23 duplicate source identities rejected',()=>expectErr(()=>build(sampleWork,[...sampleSources,sampleSources[0]]),'DUPLICATE_SOURCE_ID'));
test('24 undeclared source attributes rejected',()=>{
 const s=clone(sampleSources);s[0].untrusted_text='unqualified value';
 expectErr(()=>build(sampleWork,s),'UNDECLARED_SOURCE_FIELD');
});
test('25 unknown role not promoted',()=>{
 const s=clone(sampleSources);s[0].role='VERIFIED_BY_MAGIC';
 expectErr(()=>build(sampleWork,s),'BAD_SOURCE_ROLE');
});
test('26 unknown work metadata rejected',()=>expectErr(()=>build({...sampleWork,provider_cookie:'not-used'}),'UNDECLARED_WORK_FIELD'));
test('27 unapproved authority rejected',()=>expectErr(()=>build({...sampleWork,authority:'SEND'}),'NO_EFFECT_AUTHORITY'));
test('28 too-small budget cannot be advertised as success',()=>expectErr(()=>build({...sampleWork,byte_budget:100}),'BAD_BYTE_BUDGET'));
test('29 no eligible relevant data is held',()=>expectErr(()=>build({...sampleWork,query:'xyzabsenttoken'}),'HELD_NO_RELEVANT'));
test('30 source corpus may be large without extra workers',()=>{
 const filler=Array.from({length:200},(_,i)=>makeSyntheticSource(
  'source:generic-'+i,'PRIOR','PUBLIC',['different','history'],
  'Generic synthetic historical record number '+i+' with explanation repeated for context scale.'
 ));
 const r=build(sampleWork,[...sampleSources,...filler]);
 assert.equal(r.materialized_workers,0);assert.ok(r.available_source_bytes>r.packet_bytes*2);
 assert.equal(r.packet.selected_count,3);assert.ok(r.packet_bytes<=sampleWork.byte_budget);
});
test('31 source count bound is enforced',()=>{
 const filler=Array.from({length:1001},(_,i)=>makeSyntheticSource('source:large-'+i,'PRIOR','PUBLIC',['other'], 'Synthetic'));
 expectErr(()=>build(sampleWork,filler),'BAD_SOURCE_LIBRARY');
});
test('32 tiny-query synonym guessing is not falsely claimed',()=>{
 assert.equal(scoreSource(sampleSources[0],'unrelated unknownterm'),0);
});
test('33 two-source catalog without challenger remains explicit',()=>{
 const s=sampleSources.filter(x=>x.id!=='source:beta');
 const r=build(sampleWork,s);assert.equal(r.packet.challenge_state,'NONE_RELEVANT_FOUND');
});
test('34 replay is deterministic after fresh parse and reconstruction',()=>{
 const r=build();const reconstructed=rehydrate(clone(r),clone(sampleSources),'PUBLIC');
 assert.deepEqual(reconstructed,rehydrate(r,sampleSources,'PUBLIC'));
});
