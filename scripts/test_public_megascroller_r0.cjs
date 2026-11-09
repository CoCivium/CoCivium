#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const test=require('node:test');
const builder=require('./build_public_megascroller_r0.cjs');
const ROOT=path.resolve(__dirname,'..');
const {make,verifyEdition,sha256,OUT,SRC,OVERLAY,CONTRACT}=builder;

test('deterministic output for identical public source bytes',()=>{
 const a=make(ROOT),b=make(ROOT);
 assert.equal(a.page,b.page);
 assert.equal(a.manifestText,b.manifestText);
 assert.equal(a.manifest.release_id,b.manifest.release_id);
 assert.equal(sha256(Buffer.from(a.page)),a.manifest.artifact_digests_sha256['index.html']);
});
test('actual checked-in edition exactly reconstructs from source',()=>{
 const a=verifyEdition(ROOT);
 assert.equal(a.manifest.status,'STATIC_SOURCE_ARTIFACT_ONLY_NOT_MIRRORED');
});
test('one exact release identity binds every fragment',()=>{
 const a=make(ROOT),ids=new Set();
 for(const item of a.manifest.fragments){
   assert.equal(item.release_id,a.manifest.release_id);
   assert.equal(item.publication_id,'CoMapCoNav.PublicAtlas');
   assert.match(item.stable_id,/^fragment-[a-f0-9]{16}$/);
   assert.ok(!ids.has(item.stable_id),'duplicate fragment anchor');
   ids.add(item.stable_id);
   assert.ok(a.page.includes('id="'+item.stable_id+'"'));
   assert.equal(item.license,null);
 }
 assert.equal(ids.size,a.manifest.fragment_count);
 assert.ok(ids.size>=50);
});
test('all source-graph relations have accessible fragment links',()=>{
 const a=make(ROOT),g=a.manifest;
 assert.equal(g.fragments.length,make(ROOT).manifest.fragments.length);
 assert.match(a.page,/Typed outgoing relations/);
 assert.match(a.page,/Permalink to this fragment/);
});
test('privacy and source-only effect rails remain visible',()=>{
 const a=make(ROOT);
 for(const value of ['NO LIVE X2 OR MIRROR ACK',
   'not a receiver receipt','no inferred','NOT DEPLOYED',
   'not semantic acceptance']) {
   assert.ok(a.page.toLowerCase().includes(value.toLowerCase()),value);
 }
 assert.equal(a.manifest.surfaces.filter(x=>x.independent_failure_domain).length,0);
 assert.ok(a.manifest.declared_nonclaims.includes('NO_INDEPENDENT_MIRROR'));
});
test('offline page needs no third-party scripts, fonts, images or trackers',()=>{
 const a=make(ROOT);
 assert.match(a.page,/connect-src &#39;none&#39;/);
 assert.doesNotMatch(a.page,/<script[^>]+src=/);
 assert.doesNotMatch(a.page,/<img[^>]+src=["']https?:/);
 assert.doesNotMatch(a.page,/fetch\(|XMLHttpRequest|navigator\.sendBeacon|googletagmanager/i);
});
test('keyboard anchors, reduced motion and plaintext fallback exist',()=>{
 const a=make(ROOT);
 assert.match(a.page,/href="#main"/);
 assert.match(a.page,/prefers-reduced-motion:reduce/);
 assert.match(a.page,/<summary>/);
 assert.match(a.page,/accessible/i);
 assert.match(a.page,/Skip to atlas/);
 assert.match(a.page,/aria-labelledby="map-title map-desc"/);
});
test('release source identity includes real inputs with SHA256',()=>{
 const a=make(ROOT);
 for(const s of [SRC,OVERLAY,CONTRACT]){
  assert.match(a.manifest.source_digests_sha256[s],/^[0-9a-f]{64}$/);
  assert.equal(sha256(fs.readFileSync(path.join(ROOT,s))),a.manifest.source_digests_sha256[s]);
 }
 assert.match(a.manifest.root_digest_sha256,/^[a-f0-9]{64}$/);
});
function copyInputs(temp){
  for(const f of [SRC,OVERLAY,CONTRACT]){
    const dest=path.join(temp,f);fs.mkdirSync(path.dirname(dest),{recursive:true});
    fs.copyFileSync(path.join(ROOT,f),dest);
  }
  const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,OVERLAY)));
  for(const c of overlay.candidates){
    const dest=path.join(temp,c.source.path);
    fs.mkdirSync(path.dirname(dest),{recursive:true});
    fs.copyFileSync(path.join(ROOT,c.source.path),dest);
  }
  const edition=path.join(temp,OUT);fs.mkdirSync(edition,{recursive:true});
  for(const f of ['index.html','release-manifest.json'])
    fs.copyFileSync(path.join(ROOT,OUT,f),path.join(edition,f));
}
test('offline recovery copy validates exact bytes, not independent hosting',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'copub-'));
 try{
  copyInputs(temp);
  assert.doesNotThrow(()=>verifyEdition(temp));
  assert.equal(make(temp).manifest.surfaces[2].state,'NOT_CONFIGURED');
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
});
test('tampered offline page fails before any restore claim',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'copub-'));
 try{
   copyInputs(temp);
   fs.appendFileSync(path.join(temp,OUT,'index.html'),'altered');
   assert.throws(()=>verifyEdition(temp),/HOLD_EDITED_OR_STALE_RENDER/);
   fs.copyFileSync(path.join(ROOT,OUT,'index.html'),path.join(temp,OUT,'index.html'));
   assert.doesNotThrow(()=>verifyEdition(temp));
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
});
test('source graph alteration mismatches pinned Git blob',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'copub-'));
 try{
   copyInputs(temp);fs.appendFileSync(path.join(temp,SRC),' ');
   assert.throws(()=>make(temp),/HOLD_SOURCE_GRAPH_PIN/);
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
});
test('private candidate is not released into the public atlas',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'copub-'));
 try{
   copyInputs(temp);
   const p=path.join(temp,OVERLAY),d=JSON.parse(fs.readFileSync(p));
   d.candidates[0].privacy='PRIVATE';
   fs.writeFileSync(p,JSON.stringify(d));
   assert.throws(()=>make(temp),/HOLD_MEDIA_BOUNDARY/);
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
});
test('swapped media bytes reject false pinned donor',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'copub-'));
 try{
   copyInputs(temp);
   const d=JSON.parse(fs.readFileSync(path.join(temp,OVERLAY)));
   fs.writeFileSync(path.join(temp,d.candidates[0].source.path),'changed public media');
   assert.throws(()=>make(temp),/HOLD_MEDIA_SOURCE_BLOB_DRIFT/);
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
});
test('manifest never self-certifies public deployment or real source commit',()=>{
 const m=make(ROOT).manifest;
 assert.equal(m.source_commit,null);
 assert.equal(m.created_at_utc,null);
 assert.equal(m.surfaces[1].state,'NOT_DEPLOYED');
 assert.equal(m.surfaces[2].state,'NOT_CONFIGURED');
 assert.equal(m.surfaces[3].independent_failure_domain,false);
});
