#!/usr/bin/env node
'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {prepare,check,SHA,BLOB,BASE,MANIFEST,SOURCES}=require('./BuildCoPublicConstellationManifestR0.cjs');
const ROOT=path.resolve(__dirname,'..');
test('exact published megascroller release manifest matches generator',()=>{
  const r=check(ROOT);
  assert.equal(r.manifest.schema,'CoCivium.PublicMegascrollerRelease.R0');
});
test('deterministic release ID and byte-identical manifest',()=>{
  const a=prepare(ROOT),b=prepare(ROOT);
  assert.equal(a.text,b.text);
  assert.equal(a.manifest.edition_id,b.manifest.edition_id);
});
test('exact source page is hash-bound in manifest',()=>{
  const r=prepare(ROOT);
  const raw=fs.readFileSync(path.join(ROOT,BASE));
  assert.equal(r.manifest.content_sha256,SHA(raw));
  assert.equal(r.manifest.source_git_blob_sha1,BLOB(raw));
});
test('all public fragment anchors exist uniquely and are edition-scoped',()=>{
  const r=prepare(ROOT),page=fs.readFileSync(path.join(ROOT,BASE),'utf8');
  const ids=new Set();
  for(const f of r.manifest.fragments){
    assert.ok(page.includes('id="'+f.stable_id+'"'));
    assert.equal(f.edition_id,r.manifest.edition_id);
    assert.equal(f.content_granularity,'WHOLE_HTML_EDITION');
    assert.equal(f.content_sha256,r.manifest.content_sha256);
    assert.ok(!ids.has(f.stable_id));
    ids.add(f.stable_id);
    assert.match(f.anchor_binding_sha256,/^[0-9a-f]{64}$/);
    assert.equal(f.license,null);
  }
  assert.equal(ids.size,r.manifest.fragment_count);
  assert.ok(ids.size>=60);
});
test('actual generated public edition has required nested navigation',()=>{
  const page=fs.readFileSync(path.join(ROOT,BASE),'utf8');
  for(const section of ['here','overview','maps','graph','retro','evolution','time','resilience','evidence'])
    assert.ok(page.includes('id="'+section+'"'),section);
  assert.match(page,/<details[\s>]/);
  assert.match(page,/Skip to main content/);
});
test('real CoNav renderer verification is part of manifest build',()=>{
  const r=prepare(ROOT);
  assert.equal(r.manifest.renderer,'CoNavNestedAtlasR0.cjs');
  assert.match(r.manifest.source_objects[SOURCES[3]].sha256,/^[0-9a-f]{64}$/);
});
test('all sources have exact current byte hashes',()=>{
  const r=prepare(ROOT);
  for(const rel of SOURCES){
    assert.equal(r.manifest.source_objects[rel].sha256,SHA(fs.readFileSync(path.join(ROOT,rel))));
  }
});
test('no executable remote assets or user-private conversation URLs',()=>{
  const raw=fs.readFileSync(path.join(ROOT,BASE),'utf8');
  assert.match(raw,/script-src 'none'/);
  assert.doesNotMatch(raw,/<script[^>]+src=|https?:\/\/mail\.google\.com|https?:\/\/chatgpt\.com\/c\//i);
});
test('manifest refuses to call a public URL a verified independent mirror',()=>{
  const r=prepare(ROOT).manifest;
  assert.equal(r.surfaces.filter(x=>x.verified_replica).length,0);
  assert.equal(r.surfaces[1].state,'NOT_DEPLOYED');
  assert.equal(r.surfaces[2].state,'NOT_CONFIGURED');
  assert.equal(r.source_commit,null);
});
test('fragment fallback is public source, not opaque cross-provider magic',()=>{
  const r=prepare(ROOT).manifest;
  for(const f of r.fragments){
    assert.ok(f.fallback_uri.startsWith('https://github.com/CoCivium/CoCivium/blob/main/'));
    assert.equal(f.relation_coverage,'EDITION_LEVEL_ONLY_NO_INFERRED_PER_FRAGMENT_PROVENANCE');
  }
});
test('bounded same-provider cold-copy readback verifies exact bytes only',()=>{
  const raw=fs.readFileSync(path.join(ROOT,BASE));
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'copub-meta-'));
  try{
    fs.writeFileSync(path.join(temp,'index.html'),raw);
    const got=fs.readFileSync(path.join(temp,'index.html'));
    assert.equal(SHA(got),prepare(ROOT).manifest.content_sha256);
    assert.equal(prepare(ROOT).manifest.surfaces[3].state,'COLD_COPY_TEST_NOT_HOST_FAILOVER');
  }finally{fs.rmSync(temp,{recursive:true,force:true})}
});
test('changed or tampered copy is detected, not green',()=>{
  const raw=fs.readFileSync(path.join(ROOT,BASE));
  const evil=Buffer.concat([raw,Buffer.from('tamper')]);
  assert.notEqual(SHA(evil),prepare(ROOT).manifest.content_sha256);
});
test('public site is not equated with a live X2 UI or 24h Seed',()=>{
  const r=prepare(ROOT).manifest;
  assert.ok(r.nonclaims.includes('NO_X2_RUNTIME_OR_24H_SEED_PROOF'));
  assert.ok(r.nonclaims.includes('COPY_NE_TESTED_BACKUP'));
});
test('fragments are related to one edition but not misclaimed independent effects',()=>{
  const r=prepare(ROOT).manifest;
  assert.ok(r.fragments.length>60);
  assert.equal(new Set(r.fragments.map(x=>x.publication_id)).size,1);
  assert.equal(new Set(r.fragments.map(x=>x.content_sha256)).size,1);
});
