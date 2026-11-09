#!/usr/bin/env node
'use strict';
/* Public CoMap megascroller release identity, manifest and no-fake-mirror rail.
   This is NOT a site deployer, external receiver, mailbox worker or backup. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const BASE='examples/comap/megascroller-r0.html';
const MANIFEST='examples/comap/megascroller-r0.release.json';
const SOURCES=[
  'ai/comap-source-projection-r0.json',
  'examples/comap/prior-media-backfill-overlay-r0.json',
  'examples/colensmedia/conav_retro_manifest_r0.json',
  'scripts/CoNavNestedAtlasR0.cjs',
  'docs/Evolution/COPUBLIC_CONSTELLATION_MEGASCROLLER_R0.json'
];
const SHA=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const BLOB=bytes=>crypto.createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const HOLD=(x)=>{throw Error('HOLD_'+x)};
const file=(root,rel)=>{
  if(!/^[A-Za-z0-9_./+-]+$/.test(rel)||rel.startsWith('/')||rel.split('/').some(x=>x==='..'||x===''||x==='.'))HOLD('UNSAFE_PATH');
  let p=root;
  for(const chunk of rel.split('/')){
    p=path.join(p,chunk);
    if(fs.lstatSync(p).isSymbolicLink())HOLD('SYMLINK_SOURCE');
  }
  const bytes=fs.readFileSync(p);
  if(!bytes.length||bytes.length>2_000_000)HOLD('BAD_SOURCE_SIZE');
  return bytes;
};
function prepare(root){
  const html=file(root,BASE),text=html.toString('utf8');
  const graph=JSON.parse(file(root,SOURCES[0]));
  const overlay=JSON.parse(file(root,SOURCES[1]));
  const retro=JSON.parse(file(root,SOURCES[2]));
  const contract=JSON.parse(file(root,SOURCES[4]));
  if(graph.schema!=='CoAll.CoMapProjection.R0'||
     overlay.schema!=='CoAll.CoNav.PriorMediaBackfillOverlay.R0'||
     retro.schema!=='CoAll.CoNavRetroMedia.R0'||
     contract.schema!=='cocivium.public-constellation.r0')HOLD('SOURCE_SCHEMA');
  if(overlay.media_bytes_uploaded!==false||overlay.rights_release!==false||
     (overlay.candidates||[]).some(c=>c.privacy!=='PUBLIC_METADATA_ONLY'||
      c.rights!=='PUBLIC_SOURCE_READABLE_DERIVATIVE_RIGHTS_NOT_VERIFIED'))HOLD('MEDIA_PRIVACY_RIGHTS');
  if(!overlay.source_graph||overlay.source_graph.git_blob_sha1!==BLOB(file(root,SOURCES[0])))HOLD('SOURCE_PIN');
  const core=require('./CoNavNestedAtlasR0.cjs');
  core.run(root,path.join(root,'examples/comap/diagram-of-diagrams-r0.md'),true);
  if(!text.startsWith('<!doctype html>')||!text.includes('script-src &#39;none&#39;')&&
     !text.includes("script-src 'none'"))HOLD('OFFLINE_CSP');
  if(/<script[^>]*src=|https?:\/\/(?:mail\.google\.com|chatgpt\.com\/c\/)/i.test(text))HOLD('PRIVATE_OR_REMOTE_EXEC');
  const anchors=[...text.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
  const unique=new Set(anchors);
  if(anchors.length<60||anchors.length>300||unique.size!==anchors.length||
     anchors.some(x=>!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(x)))HOLD('FRAGMENT_IDS');
  const required=['here','overview','maps','graph','retro','evolution','time','resilience','evidence'];
  if(required.some(x=>!unique.has(x)))HOLD('MISSING_SECTION');
  const hash=SHA(html),sources={};
  for(const source of SOURCES)sources[source]={sha256:SHA(file(root,source)),source_scope:'PUBLIC_REPO'};
  const editionId='R0-'+SHA(Buffer.from(hash+JSON.stringify(sources))).slice(0,20);
  const fallback='https://github.com/CoCivium/CoCivium/blob/main/'+BASE;
  const fragments=anchors.map((id)=>({
    stable_id:id,publication_id:'CoCivium.CoMapCoNav.Megascroller',
    edition_id:editionId,media_type:'text/html',
    content_file:BASE,content_sha256:hash,content_granularity:'WHOLE_HTML_EDITION',
    anchor_binding_sha256:SHA(Buffer.from(editionId+'#'+id)),
    source_refs:SOURCES,relation_refs:[],
    relation_coverage:'EDITION_LEVEL_ONLY_NO_INFERRED_PER_FRAGMENT_PROVENANCE',
    custody_scope:'PUBLIC_REPOSITORY_SOURCE',
    license:null,supersedes:null,fallback_uri:fallback,
  }));
  const manifest={
    schema:'CoCivium.PublicMegascrollerRelease.R0',
    publication_id:'CoCivium.CoMapCoNav.Megascroller',
    edition_id:editionId,edition_time_utc:null,source_commit:null,
    content_sha256:hash,source_git_blob_sha1:BLOB(html),
    root_digest_sha256:SHA(Buffer.from(editionId+hash+JSON.stringify(sources))),
    source_objects:sources,renderer:'CoNavNestedAtlasR0.cjs',
    fragment_count:fragments.length,fragments,
    formats:[{path:BASE,media_type:'text/html',accessible_fallback:'STATIC_SEMANTIC_HTML_NO_SCRIPT'},
             {path:MANIFEST,media_type:'application/json',accessible_fallback:'MACHINE_READABLE_SOURCE_ONLY'}],
    surfaces:[
      {kind:'git_repository',state:'PUBLIC_SOURCE_AFTER_MERGE_NOT_EXTERNAL_ACK',failure_domain:'GITHUB',verified_replica:false},
      {kind:'public_website',state:'NOT_DEPLOYED',failure_domain:null,verified_replica:false},
      {kind:'independent_static_mirror',state:'NOT_CONFIGURED',failure_domain:null,verified_replica:false},
      {kind:'local_archive',state:'COLD_COPY_TEST_NOT_HOST_FAILOVER',failure_domain:null,verified_replica:false}
    ],
    next_real_proofs:[
      'Fetch exact HTML and this manifest from two independently administered hosts',
      'Verify SHA-256 and fragment availability from each receiver',
      'Disable primary and recover identical edition from independent mirror',
      'Restore earlier edition and compare predecessor without losing anchors',
      'Keyboard-only and low-bandwidth first-use with independent comprehension receipt'
    ],
    nonclaims:['SOURCE_NE_SITE_DEPLOYMENT','MANY_URLS_NE_INDEPENDENT_FAILURE_DOMAINS',
               'FRAGMENT_NE_COMPLETE_HOLOGRAM','COPY_NE_TESTED_BACKUP',
               'RENDER_NE_SEMANTIC_TRUTH','PUBLIC_NE_LICENSE_RELEASE',
               'HASH_NE_EXTERNAL_RECEIVER_ACK','NO_X2_RUNTIME_OR_24H_SEED_PROOF']
  };
  return {manifest,text:JSON.stringify(manifest,null,2)+'\n'};
}
function check(root){
  const r=prepare(root);
  if(fs.readFileSync(path.join(root,MANIFEST),'utf8')!==r.text)HOLD('STALE_RELEASE_MANIFEST');
  return r;
}
function write(root){
  const result=prepare(root);
  fs.writeFileSync(path.join(root,MANIFEST),result.text,{flag:'wx'});
  return result;
}
module.exports={prepare,check,write,SHA,BLOB,BASE,MANIFEST,SOURCES};
if(require.main===module){
  if(process.argv.length>3)HOLD('ARGS');
  const root=path.resolve(__dirname,'..'),r=process.argv.includes('--check')?check(root):write(root);
  console.log(JSON.stringify({status:process.argv.includes('--check')?'EXACT_RELEASE_MATCH':'RELEASE_METADATA_CREATED',
     edition_id:r.manifest.edition_id,fragment_count:r.manifest.fragment_count,
     content_sha256:r.manifest.content_sha256,independent_mirrors_verified:0}));
}
