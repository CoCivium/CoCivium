#!/usr/bin/env node
'use strict';
// CoPublic Megascroller R0. Deterministic, public-source only. No network.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const SRC = 'ai/comap-source-projection-r0.json';
const OVERLAY = 'examples/comap/prior-media-backfill-overlay-r0.json';
const CONTRACT = 'docs/Evolution/COPUBLIC_CONSTELLATION_MEGASCROLLER_R0.json';
const OUT = 'examples/comap/public-megascroller-r0';
const VERSION = 'CoPublic.Megascroller.Renderer.R0';
const COUNTS = {nodesMax:1500,edgesMax:6000,mediaMax:150};
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const gitBlob = bytes => crypto.createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const fail = msg => {throw new Error('HOLD_'+msg)};
const html = s => String(s ?? '').replace(/[&<>"']/g, ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const plain = s => html(String(s ?? '').slice(0,400));
const isHex = (s,n) => typeof s==='string' && new RegExp('^[a-f0-9]{'+n+'}$').test(s);
const github = rel => 'https://github.com/CoCivium/CoCivium/blob/main/'+rel.split('/').map(encodeURIComponent).join('/');

function checked(root,rel){
  if(typeof rel!=='string'||!rel||rel.startsWith('/')||rel.includes('\\')||rel.split('/').some(p=>!p||p==='.'||p==='..'))fail('UNSAFE_PATH');
  let target=root;
  for(const part of rel.split('/')){
    target=path.join(target,part);
    if(fs.lstatSync(target).isSymbolicLink())fail('LINKED_SOURCE');
  }
  if(!fs.statSync(target).isFile())fail('SOURCE_NOT_FILE');
  const bytes=fs.readFileSync(target);
  if(!bytes.length||bytes.length>2_000_000)fail('SOURCE_SIZE');
  return bytes;
}
const parse = b=>JSON.parse(b.toString('utf8'));

function input(root){
  const srcBytes=checked(root,SRC),overlayBytes=checked(root,OVERLAY),contractBytes=checked(root,CONTRACT);
  const graph=parse(srcBytes),overlay=parse(overlayBytes),contract=parse(contractBytes);
  if(graph.schema!=='CoAll.CoMapProjection.R0'||!Array.isArray(graph.nodes)||!Array.isArray(graph.edges)||
     graph.nodes.length>COUNTS.nodesMax||graph.edges.length>COUNTS.edgesMax)fail('GRAPH_SCHEMA');
  if(overlay.schema!=='CoAll.CoNav.PriorMediaBackfillOverlay.R0'||overlay.rights_release!==false||
     overlay.media_bytes_uploaded!==false||!Array.isArray(overlay.candidates)||
     overlay.candidates.length>COUNTS.mediaMax)fail('OVERLAY_POLICY');
  if(contract.schema!=='cocivium.public-constellation.r0'||contract.status!=='design_contract_only')fail('CONSTELLATION_CONTRACT');
  if(!overlay.source_graph||overlay.source_graph.path!==SRC||gitBlob(srcBytes)!==overlay.source_graph.git_blob_sha1)fail('SOURCE_GRAPH_PIN');
  const ids=new Set(), nodeBy=new Map();
  for(const node of graph.nodes){
    if(!node||typeof node.id!=='string'||node.id.length>180||ids.has(node.id)||
      typeof node.kind!=='string'||typeof node.label!=='string'||node.label.length>200)fail('NODE_ID_OR_LABEL');
    ids.add(node.id);nodeBy.set(node.id,node);
  }
  for(const edge of graph.edges)if(!edge||!ids.has(edge.from)||!ids.has(edge.to)||
      typeof edge.relation!=='string'||edge.relation.length>80)fail('EDGE_ENDPOINT');
  const candidates=[];
  for(const c of overlay.candidates){
    if(!c||!c.source||c.source.repository!=='CoCivium/CoCivium'||
       c.privacy!=='PUBLIC_METADATA_ONLY'||c.rights!=='PUBLIC_SOURCE_READABLE_DERIVATIVE_RIGHTS_NOT_VERIFIED'||
       c.bytes_copied_into_overlay!==false||c.relation_type!=='INSPIRATION_CANDIDATE_FOR'||
       !ids.has(c.relation_to)||typeof c.id!=='string'||ids.has(c.id))fail('MEDIA_BOUNDARY');
    const rel=c.source.path;
    if(!rel.startsWith('examples/'))fail('MEDIA_ROOT');
    const b=checked(root,rel);
    if(!isHex(c.source.git_blob_sha1,40)||gitBlob(b)!==c.source.git_blob_sha1)fail('MEDIA_SOURCE_BLOB_DRIFT');
    ids.add(c.id);candidates.push(c);
  }
  return {graph,overlay,contract,graphBytes:srcBytes,overlayBytes,contractBytes,nodeBy,candidates};
}
function stableId(id){return 'fragment-'+sha256(Buffer.from(id)).slice(0,16)}
function evidenceUrl(node,graph){
  const record=(graph.sources||[]).find(x=>x.id===node.source);
  if(record&&typeof record.url==='string'&&/^https:\/\/github\.com\/CoCivium\/CoCivium\/(?:blob|issues)\//.test(record.url))return record.url;
  return github(SRC);
}
function make(root){
  const d=input(root),{graph,candidates,overlay}=d;
  const hashes={[SRC]:sha256(d.graphBytes),[OVERLAY]:sha256(d.overlayBytes),[CONTRACT]:sha256(d.contractBytes)};
  const releaseId='r0-'+sha256(Buffer.from(VERSION+JSON.stringify(hashes))).slice(0,16);
  const groupList=[['map','CoMap / first orientation'],['domain','Evolution domains'],['repository','Repositories'],['highlight','Highlighted frontiers'],['source_document','Source documents']];
  const groups=groupList.map(([kind,name])=>({kind,name,nodes:graph.nodes.filter(n=>n.kind===kind)}));
  const others=graph.nodes.filter(n=>!groupList.some(([k])=>k===n.kind));
  if(others.length)fail('UNKNOWN_NODE_KIND');
  const navSources=[SRC,OVERLAY,CONTRACT,'examples/comap/diagram-of-diagrams-r0.md'];
  const edgesById=new Map(graph.nodes.map(n=>[n.id,graph.edges.filter(e=>e.from===n.id)]));
  const fragments=[],parts=[];
  const put=(...s)=>parts.push(...s);
  const C='https://github.com/CoCivium/CoCivium/blob/main/';
  put('<!doctype html>','<html lang="en"><head><meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<meta name="color-scheme" content="dark light">',
    '<meta name="description" content="CoMap and CoNav public atlas: source-backed nested relations, history and recovery without private material.">',
    '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; script-src &#39;unsafe-inline&#39;; style-src &#39;unsafe-inline&#39;; img-src data:; base-uri &#39;none&#39;; form-action &#39;none&#39;; connect-src &#39;none&#39;">',
    '<title>CoMap + CoNav | Public Atlas R0</title>',
    '<style>');
  put(
    ':root{color-scheme:dark;--bg:#081722;--panel:#112838;--ink:#eaf4ff;--sub:#bbcede;--line:#42647a;--aqua:#72eadb;--violet:#cfabff;--amber:#ffd29b;font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}',
    '*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(ellipse 60vw 45vh at 80% 0%,#153c47,transparent),var(--bg);color:var(--ink)}',
    'a{color:var(--aqua);text-underline-offset:.2em}a:hover{text-decoration-thickness:2px}:focus-visible{outline:3px solid var(--amber);outline-offset:3px}',
    '.skip{position:absolute;left:-100vw;top:0;background:#fff;color:#111;padding:1rem;z-index:99}.skip:focus{left:1rem}',
    '.site{max-width:1240px;margin:auto;display:grid;grid-template-columns:230px minmax(0,1fr);gap:2rem;padding:1.5rem}',
    '.rail{position:sticky;top:1rem;align-self:start;border:1px solid var(--line);border-radius:18px;padding:1rem;background:#0b1f2d}',
    '.rail a{display:block;margin:.3rem 0;padding:.34rem;border-radius:6px;text-decoration:none}.rail a:hover{background:var(--panel)}',
    'main{min-width:0}.hero{padding:4rem 1rem 3rem}.eyebrow{text-transform:uppercase;letter-spacing:.16em;color:var(--aqua);font-size:.78rem;font-weight:700}',
    'h1{font-size:clamp(2.8rem,6vw,5.6rem);line-height:1.04;margin:.35em 0}h2{font-size:clamp(1.6rem,3vw,2.6rem);line-height:1.2}h3{margin:0 0 .4rem;font-size:1.14rem}',
    'p{max-width:70ch}section{padding:2rem 0;border-top:1px solid var(--line);scroll-margin-top:2rem}.lead{font-size:1.27rem;color:var(--sub)}',
    '.badge{display:inline-block;border:1px solid var(--line);border-radius:40px;padding:.24rem .65rem;font-size:.78rem;margin-right:.35rem}',
    '.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.8rem}.card,details,.note{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:1rem}',
    '.card{min-width:0}.card p{margin:.3rem 0;color:var(--sub)}.meter{font-size:2rem;font-weight:800;font-variant-numeric:tabular-nums;color:var(--aqua)}',
    'details{margin:.5rem 0}details summary{cursor:pointer;font-weight:700}details[open]{border-color:var(--violet)}',
    '.node-card{margin:.45rem 0;background:#102332}.node-card[hidden]{display:none}small,.muted{color:var(--sub)}',
    'code{overflow-wrap:anywhere;color:#d7bcff;font-size:.88em}.links{display:flex;gap:.5rem;flex-wrap:wrap}.links a{border:1px solid var(--line);border-radius:10px;padding:.35rem .6rem;text-decoration:none}',
    '.map{width:100%;height:auto;border:1px solid var(--line);border-radius:16px;background:#102332}.map text{font-family:system-ui,sans-serif;fill:#eaf4ff;font-size:18px}',
    '.list{padding-left:1.2rem}.list li{margin:.45rem 0}.filter{width:100%;background:#091e2c;color:var(--ink);padding:.8rem;border:1px solid var(--aqua);border-radius:12px}',
    '.status{border-left:4px solid var(--amber);padding:.7rem 1rem;background:#2b2830}.mono{font-family:ui-monospace,monospace;overflow-wrap:anywhere}',
    '.twocol{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}table{border-collapse:collapse;width:100%}th,td{border:1px solid var(--line);padding:.7rem;text-align:left;vertical-align:top}th{background:var(--panel)}',
    'footer{border-top:1px solid var(--line);padding:2rem 0 5rem;color:var(--sub)}',
    '@media(max-width:800px){.site{display:block;padding:1rem}.rail{position:static;margin:0 0 1rem}.rail nav{display:flex;flex-wrap:wrap;gap:.35rem}.hero{padding:2rem 0}.links{gap:.35rem}}',
    '@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{body{background:#fff;color:#111}.rail{display:none}.site{display:block}details{break-inside:avoid}a{color:#065}main{width:100%}}'
  );
  put('</style></head><body><a class="skip" href="#main">Skip to atlas</a><div class="site">',
      '<aside class="rail" aria-label="Atlas navigation"><strong>CoMap / CoNav</strong><br><small>Public evidence atlas R0</small>',
      '<nav aria-label="Chapters"><a href="#orientation">01 / Start here</a><a href="#map">02 / Map of maps</a>',
      '<a href="#fragments">03 / Explore fragments</a><a href="#inspiration">04 / Prior media</a>',
      '<a href="#time">05 / Time and change</a><a href="#resilience">06 / Mirrors and recovery</a>',
      '<a href="#sources">07 / Sources</a></nav><small>Offline page. No tracking or live sync.</small></aside>',
      '<main id="main"><header class="hero" id="orientation"><div class="eyebrow">One evidence graph / many views</div>',
      '<h1>Explore the<br>living map.</h1>',
      '<p class="lead">A long-form public atlas that opens into smaller maps, source objects, and disagreements. Designed for humans and machine readers, with an honest route back to evidence.</p>',
      '<span class="badge">PUBLIC SOURCE CANDIDATE</span><span class="badge">RELEASE '+html(releaseId)+'</span>',
      '<span class="badge">NO LIVE X2 OR MIRROR ACK</span>',
      '<div class="cards" style="margin-top:2rem"><div class="card"><div class="meter">'+graph.nodes.length+'</div><p>source-registered objects</p></div>',
      '<div class="card"><div class="meter">'+graph.edges.length+'</div><p>typed source relations</p></div>',
      '<div class="card"><div class="meter">'+candidates.length+'</div><p>prior-media candidates, unreviewed</p></div></div>',
      '<p class="status"><strong>Currentness:</strong> these are public repository source projections, not a live synchronization channel. Source registries may predate this edition. A link or mirror is not a receiver receipt.</p></header>');

  put('<section id="map"><div class="eyebrow">02 / Navigate</div><h2>A map of maps</h2>',
      '<p>Each box is a view of the same public source. Follow a label into a smaller map, then into the original evidence. Proximity is not causality, adoption or authority.</p>',
      '<svg class="map" viewBox="0 0 760 350" role="img" aria-labelledby="map-title map-desc">',
      '<title id="map-title">Expandable CoMap and CoNav atlas</title>',
      '<desc id="map-desc">One central source object feeds five navigable groups: map, evolution domains, repositories, highlights and documents. All are available as text below.</desc>',
      '<g stroke="#72eadb" stroke-width="2" fill="none"><path d="M380 85V138M380 138H115V188M380 138H247V188M380 138V188M380 138H513V188M380 138H645V188"/></g>',
      '<rect x="224" y="22" width="312" height="63" rx="13" fill="#193a48" stroke="#72eadb"/>',
      '<text x="380" y="60" text-anchor="middle">CoAll source spine</text>');
  const captions=['CoMap','Domains','Repos','Highlights','Documents'];
  captions.forEach((name,i)=>{const x=52+i*132;put('<rect x="'+x+'" y="188" width="124" height="74" rx="12" fill="#183248" stroke="#cfabff"/>',
    '<text x="'+(x+62)+'" y="231" text-anchor="middle">'+html(name)+'</text>')});
  put('</svg><p class="muted">The accessible object list immediately below is authoritative for this projection. Visual geometry is illustrative.</p>',
      '<div class="links"><a href="#fragments">Explore all source fragments</a>',
      '<a href="'+github('examples/comap/diagram-of-diagrams-r0.md')+'">Full nested CoNav diagram source</a>',
      '<a href="'+github('examples/colensmedia/conav_navigator_r0.html')+'">Existing expandable navigator source</a></div></section>');

  put('<section id="fragments"><div class="eyebrow">03 / Fractal drill down</div><h2>Small maps inside the big map</h2>',
    '<p>Expand only the group you need. Each object retains a stable edition anchor and its source evidence. Search is optional; all content remains visible with scripts disabled.</p>',
    '<label for="lookup">Filter public source objects</label><input class="filter" id="lookup" type="search" placeholder="Search label or type; optional" aria-describedby="search-help">',
    '<p id="search-help" class="muted">Client-side only. Search never sends text to a server.</p>');
  for(const group of groups){
    put('<details class="group" id="group-'+html(group.kind)+'"><summary>'+html(group.name)+
      ' ('+group.nodes.length+')</summary><p class="muted">Source-backed, independently navigable fragments.</p>');
    for(const node of group.nodes){
      const id=stableId(node.id),links=edgesById.get(node.id)||[];
      const ev=evidenceUrl(node,graph);
      const label=node.label.slice(0,200);
      const detail=(node.description||node.status||'Public source candidate');
      put('<details class="node-card" id="'+id+'" data-search="'+html((node.id+' '+label+' '+group.kind).toLowerCase())+'">',
        '<summary>'+html(label)+' <small>('+html(group.kind)+')</small></summary>',
        '<p>'+plain(detail)+'</p><p><small>Work fragment: </small><code>'+html(node.id)+'</code></p>',
        '<div class="links"><a href="'+html(ev)+'">Inspect source evidence</a>',
        '<a href="#'+id+'">Permalink to this fragment</a></div>');
      if(links.length){
        put('<p><strong>Typed outgoing relations</strong></p><ul class="list">');
        for(const edge of links)put('<li>'+html(edge.relation)+' → <a href="#'+stableId(edge.to)+'">'+
          html((d.nodeBy.get(edge.to)||{label:edge.to}).label)+'</a></li>');
        put('</ul>');
      }else put('<p class="muted">No typed outgoing edges in this source snapshot.</p>');
      put('</details>');
      fragments.push({
        stable_id:id,publication_id:'CoMapCoNav.PublicAtlas',release_id:releaseId,
        node_id:node.id,media_type:'text/html',content_sha256:sha256(Buffer.from(JSON.stringify(node))),
        source_refs:[ev],relation_refs:links.map(e=>e.to),
        custody_scope:'PUBLIC_SOURCE_GRAPH',license:null,supersedes:null,
        fallback_uri:ev,rights_review:'NOT_PERFORMED',
      });
    }
    put('</details>');
  }
  put('</section>');

  put('<section id="inspiration"><div class="eyebrow">04 / Inspiration, not invention</div>',
      '<h2>Previously published media can seed new paths.</h2>',
      '<p>These five prior media items are pinned public-source pointers. Their possible CoSeed and CoPath contributions are proposals, not semantic acceptance or permission to reproduce media.</p><div class="cards">');
  for(const candidate of candidates){
    const id=stableId(candidate.id),url=github(candidate.source.path);
    put('<article class="card" id="'+id+'"><h3>'+html(candidate.label||candidate.id)+'</h3>',
        '<p>UNREVIEWED / public metadata only</p><p><code>'+html(candidate.source.git_blob_sha1)+'</code></p>',
        '<div class="links"><a href="'+url+'">Open pinned-source path</a><a href="#'+id+'">Fragment link</a></div>',
        '<p class="muted">Candidate relation: '+html(candidate.relation_type)+
        '. Rights, receiver uptake and correctness still require review.</p></article>');
    fragments.push({
       stable_id:id,publication_id:'CoMapCoNav.PublicAtlas',release_id:releaseId,
       node_id:candidate.id,media_type:'text/html',content_sha256:sha256(Buffer.from(JSON.stringify(candidate))),
       source_refs:[url],relation_refs:[candidate.relation_to],
       custody_scope:'PUBLIC_METADATA_ONLY',license:null,supersedes:null,
       fallback_uri:url,rights_review:'NOT_PERFORMED',
    });
  }
  put('</div><p class="status"><strong>Retroactive coverage is bounded.</strong> Unclassified assets are discoverable candidates, not vanished assets and not approved inspiration. Other repositories, old chats, CoFarm and CoStead were not scanned for this release.</p></section>');

  put('<section id="time"><div class="eyebrow">05 / CoTime and provenance</div><h2>Versions do not overwrite their ancestors.</h2>',
      '<div class="twocol"><div class="card"><h3>This source edition</h3><p>Edition identity is derived from exact public-source file hashes and the renderer version, not the clock or the currently open browser tab.</p>',
      '<p class="mono">'+html(releaseId)+'</p></div><div class="card"><h3>Future successor</h3>',
      '<p>A changed source requires a new edition and a comparison receipt. Newer need not mean better, and old anchors should remain recoverable.</p></div></div>',
      '<p>Forecast, correction, dissent, snapshot and measured effect are different relations. A rendered visual cannot certify its own causal explanation.</p></section>');

  put('<section id="resilience"><div class="eyebrow">06 / CoConstellation</div><h2>Replicas are measured, not assumed.</h2>',
      '<p>Portable content is the starting point. Availability requires independent hosts and readbacks; a backup requires an actual restore test.</p>',
      '<table><thead><tr><th scope="col">Surface</th><th scope="col">What this edition proves</th></tr></thead><tbody>',
      '<tr><td>Git source + history</td><td>Public source after merge; GitHub CI can hash this exact file</td></tr>',
      '<tr><td>Independent website mirror</td><td>NOT DEPLOYED / no independently fetched digest</td></tr>',
      '<tr><td>Offline copy</td><td>Static page is portable; CI copy-and-hash test is not independent-host recovery</td></tr>',
      '<tr><td>Headless reader</td><td>Versioned JSON release manifest and stable fragment IDs</td></tr>',
      '<tr><td>Live X2 / CoOrb</td><td>NOT VERIFIED / source publication is not installation</td></tr>',
      '</tbody></table><p><strong>Failure rule:</strong> stale, missing, corrupted or differently versioned copies must display DEGRADED or HOLD, never a fabricated all-green sync.</p>',
      '<div class="links"><a href="release-manifest.json">Machine-readable release manifest</a>',
      '<a href="'+github('docs/Evolution/COPUBLIC_CONSTELLATION_MEGASCROLLER_R0.json')+'">Constellation design contract</a></div></section>');

  put('<section id="sources"><div class="eyebrow">07 / Provenance</div><h2>Check the source, not the wallpaper.</h2>',
      '<ul class="list">');
  navSources.forEach(ref=>put('<li><a href="'+github(ref)+'">'+html(ref)+'</a></li>'));
  put('</ul><p class="muted">No cookies, trackers, CDNs or network requests are needed to read this edition. Off-page source links are deliberately optional and require connectivity.</p>',
      '<p class="status">Nonclaims: SOURCE ≠ RUNTIME · PUBLIC GIT ≠ MIRROR ACK · FRAGMENT ≠ COMPLETE HOLOGRAM · SAME-PROVIDER COPY ≠ INDEPENDENT FAILURE DOMAIN · HASH ≠ SEMANTIC TRUTH · NO INFERRED PUBLICATION RIGHTS.</p></section>',
      '<footer>CoCivium / CoAll / CoMap+ / CoNav+ · Public source-only R0 · ',
      'One WorkID may have many reader views. None of these views has authority to send email, control a device, or certify itself.</footer></main></div>',
      '<script>',
      '(function(){var q=document.getElementById("lookup");if(!q)return;',
      'q.addEventListener("input",function(){var s=q.value.trim().toLowerCase();',
      'document.querySelectorAll(".node-card").forEach(function(el){el.hidden=!!s&&!el.getAttribute("data-search").includes(s)});',
      'if(s)document.querySelectorAll(".group").forEach(function(el){el.open=true});',
      '});',
      'if(location.hash&&location.hash.startsWith("#fragment-")){var el=document.getElementById(location.hash.slice(1));if(el){var p=el.parentElement;while(p){if(p.tagName==="DETAILS")p.open=true;p=p.parentElement;}}}',
      '})();',
      '</script></body></html>');
  const page=parts.join('\n')+'\n';
  const pageHash=sha256(Buffer.from(page,'utf8'));
  const rootDigest=sha256(Buffer.from(releaseId+':'+pageHash+':'+JSON.stringify(hashes)));
  const manifest={
    schema:'CoPublic.ConstellationRelease.R0',publication_id:'CoMapCoNav.PublicAtlas',
    release_id:releaseId,renderer_version:VERSION,created_at_utc:null,source_commit:null,
    status:'STATIC_SOURCE_ARTIFACT_ONLY_NOT_MIRRORED',
    source_digests_sha256:hashes,root_digest_sha256:rootDigest,
    artifact_digests_sha256:{'index.html':pageHash},
    fragment_count:fragments.length,fragments,
    surfaces:[
      {id:'github_source',kind:'git_repository',state:'SOURCE_ONLY_MERGE_AND_CI_READBACK_REQUIRED',digest_proven:false,independent_failure_domain:false},
      {id:'public_website',kind:'public_megascroller',state:'NOT_DEPLOYED',digest_proven:false,independent_failure_domain:false},
      {id:'second_administered_mirror',kind:'independent_static_mirror',state:'NOT_CONFIGURED',digest_proven:false,independent_failure_domain:false},
      {id:'local_archive',kind:'offline_copy',state:'PORTABLE_BYTES_RESTORE_NOT_INDEPENDENTLY_PROVEN',digest_proven:false,independent_failure_domain:false}
    ],
    verification_instructions:[
      'node scripts/build_public_megascroller_r0.cjs --check',
      'node scripts/test_public_megascroller_r0.cjs',
      'Independent host must fetch exact index.html and release-manifest.json and hash-check both; not performed by this build.'
    ],
    declared_nonclaims:[
      'NO_INDEPENDENT_MIRROR','NO_WEBSITE_DEPLOYMENT','NO_EXTERNAL_READER_ACK',
      'NO_LIVE_X2_INSTALL','NO_PRIVATE_SOURCE_COPY','NO_BACKUP_RESTORE_PROOF',
      'NO_SEMANTIC_TRUTH_FROM_HASH','NO_CROSS_SESSION_SYNC'
    ]
  };
  return {page,manifest,manifestText:JSON.stringify(manifest,null,2)+'\n'};
}
function verifyEdition(root){
  const built=make(root), dir=path.join(root,OUT);
  const page=fs.readFileSync(path.join(dir,'index.html'));
  const meta=fs.readFileSync(path.join(dir,'release-manifest.json'),'utf8');
  if(page.toString('utf8')!==built.page||meta!==built.manifestText)fail('EDITED_OR_STALE_RENDER');
  if(sha256(page)!==built.manifest.artifact_digests_sha256['index.html'])fail('PAGE_HASH_MISMATCH');
  return built;
}
function write(root){
  const result=make(root),dir=path.join(root,OUT);
  fs.mkdirSync(dir,{recursive:true});
  for(const [name,text] of [['index.html',result.page],['release-manifest.json',result.manifestText]]){
    const p=path.join(dir,name);
    fs.writeFileSync(p,text,{flag:'wx'});
  }
  return result;
}
module.exports={make,write,verifyEdition,input,sha256,gitBlob,OUT,SRC,OVERLAY,CONTRACT};
if(require.main===module){
  const root=path.resolve(__dirname,'..'),check=process.argv.includes('--check');
  if(process.argv.length>3)fail('ARGS');
  const result=check?verifyEdition(root):write(root);
  process.stdout.write(JSON.stringify({state:check?'EXACT_PUBLIC_EDITION_MATCH':'PUBLIC_EDITION_CREATED',
     release_id:result.manifest.release_id,fragments:result.manifest.fragment_count,
     page_sha256:result.manifest.artifact_digests_sha256['index.html'],
     independent_mirrors_verified:0,live_x2:false})+'\n');
}
