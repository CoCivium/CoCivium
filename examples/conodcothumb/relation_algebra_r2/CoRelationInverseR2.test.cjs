'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const M=require('./CoRelationInverseR2.cjs');
const packet=(v={})=>({privacy:'PUBLIC',gesture:'EXPLICIT_RING',context:'MAP',source_ref:'sha256:'+'a'.repeat(64),authority:'NONE',relation_id:'DEPENDS_ON',transform:'CONVERSE',...v});
const NONE={device:0,network:0,send:0,clipboard:0,worker:0};
test('typed public candidate schema is R2',()=>assert.equal(M.SCHEMA,'CoCivium.CoMiddle.RelationInverse.R2'));
test('one and only 36 unique relation definitions',()=>assert.equal(M.relationMap.size,36));
test('16 directed pairs and four symmetric atoms',()=>{assert.equal(M.PAIRS.length,16);assert.equal(M.SYMMETRIC.length,4)});
test('logical candidate count exact and no workers',()=>{assert.equal(M.addressCount(),'445536');assert.deepEqual(M.ZERO_EFFECTS,NONE)});
test('every family has an explicit uncertainty gate',()=>{for(const v of M.relationMap.values())assert(M.EVIDENCE_GATES[v.family]);});
test('validity inverts relation label, not a verified claim',()=>{const z=M.preview(packet());assert.equal(z.status,'SHADOW_PROPOSAL');assert.equal(z.relation_id,'DEPENDS_ON');assert.equal(z.proposed_relation_id,'IS_DEPENDENCY_OF');assert.equal(z.source_ref_state,'DECLARED_POINTER_ONLY_NOT_BYTE_VERIFIED');assert.equal(z.receiver_ack,false)});
test('direct converse is not substitutability',()=>assert.match(M.preview(packet()).review_gate,/not substitutability/i));
test('outreach inverse never marks delivery',()=>{const z=M.preview(packet({relation_id:'ROUTES_TO',context:'OUTREACH'}));assert.equal(z.proposed_relation_id,'IS_ROUTE_TARGET_OF');assert.match(z.review_gate,/not delivery/i)});
test('causal converse carries scientific warning',()=>assert.match(M.preview(packet({relation_id:'CAUSES',context:'RESEARCH'})).review_gate,/external evidence/));
test('measurement converse requires units',()=>assert.match(M.preview(packet({relation_id:'GREATER_THAN'})).review_gate,/shared units/));
test('sensitive unknown does not expose source',()=>{const z=M.preview(packet({privacy:'UNKNOWN'}));assert.equal(z.status,'HELD_PRIVACY_UNCLASSIFIED');assert.equal(z.source_ref,null);assert.equal(z.context,'REDACTED')});
test('missing privacy held',()=>{const p=packet();delete p.privacy;assert.equal(M.preview(p).status,'HELD_PRIVACY_UNCLASSIFIED')});
test('missing context held',()=>{const p=packet();delete p.context;assert.equal(M.preview(p).status,'HELD_CONTEXT_UNKNOWN')});
test('unknown context held',()=>assert.equal(M.preview(packet({context:'PASSWORD'})).status,'HELD_CONTEXT_UNKNOWN'));
test('garbage gesture held',()=>assert.equal(M.preview(packet({gesture:'AUTO_MIDDLE_SEND'})).status,'HELD_UNBOUND_GESTURE'));
test('missing source held',()=>assert.equal(M.preview(packet({source_ref:null})).status,'HELD_UNVERIFIED_SOURCE_POINTER'));
test('unvalidated digest syntax held',()=>assert.equal(M.preview(packet({source_ref:'sha256:xxx'})).status,'HELD_UNVERIFIED_SOURCE_POINTER'));
test('authority escalation blocked',()=>assert.equal(M.preview(packet({authority:'ADMIN'})).status,'HELD_UNAUTHORIZED_EFFECT'));
test('native middle always passes, even without classifying private app',()=>{const z=M.preview({gesture:'NATIVE_MIDDLE'});assert.equal(z.status,'PASS_THROUGH_NATIVE');assert.deepEqual(z.effects,NONE);assert.equal(z.source_ref,null)});
test('missing gesture held',()=>assert.equal(M.preview(packet({gesture:undefined})).status,'HELD_UNBOUND_GESTURE'));
test('keyboard fallback may preview, not execute',()=>{const z=M.preview(packet({gesture:'KEYBOARD_FALLBACK'}));assert.equal(z.status,'SHADOW_PROPOSAL');assert.deepEqual(z.effects,NONE)});
test('non-object packets held without exception',()=>{for(const x of [null,[],3,'hello'])assert.equal(M.preview(x).status,'HELD_INVALID_REQUEST')});
test('unknown relation never replaced by guess',()=>{const z=M.preview(packet({relation_id:'INVENTED_CAUSE'}));assert.equal(z.status,'HELD_UNTYPED_RELATION');assert.equal(z.proposed_relation_id,null)});
test('unknown transform does not guess',()=>{const z=M.preview(packet({transform:'AUTO_SEND'}));assert.equal(z.status,'HELD_UNSUPPORTED_TRANSFORM')});
for(const [a,b] of M.PAIRS){
  test(`${a} -> ${b} converse`,()=>{const z=M.preview(packet({relation_id:a}));assert.equal(z.status,'SHADOW_PROPOSAL');assert.equal(z.proposed_relation_id,b);assert.deepEqual(z.effects,NONE);});
  test(`${b} -> ${a} converse`,()=>{const z=M.preview(packet({relation_id:b}));assert.equal(z.status,'SHADOW_PROPOSAL');assert.equal(z.proposed_relation_id,a);});
}
for(const [a] of M.SYMMETRIC){
  test(`${a} symmetric converse does not prove anything`,()=>{const z=M.preview(packet({relation_id:a}));assert.equal(z.status,'SHADOW_PROPOSAL');assert.equal(z.relation_kind,'SYMMETRIC');assert.equal(z.proposed_relation_id,a);assert.deepEqual(z.effects,NONE);});
}
for(const t of M.TRANSFORMS.filter(x=>x!=='CONVERSE')){
  test(`${t} is not masquerading as inverse`,()=>{const z=M.preview(packet({transform:t}));assert.equal(z.status,'SHADOW_PROPOSAL');assert.equal(z.proposed_relation_id,null);assert.notEqual(z.message,'formal relational converse (direction swap), not logical negation');});
}
test('first / last mixed-radix addresses valid',()=>{for(const i of [0n,BigInt(M.addressCount())-1n]){const x=M.decodeAddress(i);assert(M.relationMap.has(x.relation_id));assert(M.TRANSFORMS.includes(x.transform));assert(M.CONTEXTS.includes(x.context));assert(M.QUESTIONS.includes(x.question));assert(M.SURFACES.includes(x.surface));assert.equal(x.logical_address,i.toString())}});
test('bad logical addresses rejected',()=>{for(const x of [-1n,BigInt(M.addressCount()),42,'7'])assert.throws(()=>M.decodeAddress(x),/ADDRESS_OUT_OF_RANGE/)});
test('sample is deterministic from seed',()=>assert.deepEqual(M.sampleAddresses('hello',7),M.sampleAddresses('hello',7)));
test('different seed changes selected sample',()=>assert.notDeepEqual(M.sampleAddresses('hello',7),M.sampleAddresses('other',7)));
test('first seven unchanged when sample expanded to 32',()=>assert.deepEqual(M.sampleAddresses('hello',7),M.sampleAddresses('hello',32).slice(0,7)));
test('32 is absolute sample cap',()=>assert.throws(()=>M.sampleAddresses('x',33),/BAD_SAMPLE_REQUEST/));
test('invalid seed rejected',()=>{for(const s of [2,null,'x'.repeat(513)])assert.throws(()=>M.sampleAddresses(s,2),/BAD_SAMPLE_REQUEST/)});
test('sample addresses all within declared field and distinct',()=>{const s=M.sampleAddresses('seed',32);assert.equal(new Set(s.map(x=>x.logical_address)).size,32);for(const x of s)assert(BigInt(x.logical_address)<BigInt(M.addressCount()))});
test('preview does not mutate input',()=>{const p=packet();const saved=JSON.stringify(p);M.preview(p);assert.equal(JSON.stringify(p),saved)});
test('preview result is deep zero-effect and no ACK for every transform',()=>{for(const t of M.TRANSFORMS){const z=M.preview(packet({transform:t}));assert.deepEqual(z.effects,NONE);assert.equal(z.receiver_ack,false);assert.equal(z.authority,'NONE')}});
test('plain-text glyps have semantic names in source',()=>{assert.equal(Object.keys(M.GLYPHS).length,M.TRANSFORMS.length);assert(M.EVIDENCE_GATES.COMPARISON)});
test('source contains no global keyboard/clipboard hooks or fetch',()=>{const s=fs.readFileSync(path.join(__dirname,'CoRelationInverseR2.cjs'),'utf8');for(const signature of ['Add-Type','RegisterHotKey','Set-Clipboard','GetAsyncKeyState','keylogger','fetch(','https.request(','execSync(','spawn('])assert(!s.includes(signature),signature)});

test('private local digest never projected',()=>{const z=M.preview(packet({privacy:'PRIVATE_LOCAL'}));assert.equal(z.status,'SHADOW_PROPOSAL');assert.equal(z.source_ref,null);assert.equal(z.source_ref_state,'PRIVATE_POINTER_REDACTED')});
