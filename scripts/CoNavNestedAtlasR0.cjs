const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

function generateAtlas(base, overlay) {
  const fail = code => { throw new Error(code); };
  const clean = text => String(text ?? "").replace(/[\[\]{}"<>`\\|\r\n]/g, " ").replace(/\s+/g, " ").trim().slice(0, 66);
  if (!base || base.schema !== "CoAll.CoMapProjection.R0" ||
      !Array.isArray(base.nodes) || !Array.isArray(base.edges) ||
      base.nodes.length > 1500 || base.edges.length > 6000) fail("HOLD_BASE_GRAPH");
  if (!overlay || overlay.schema !== "CoAll.CoNav.PriorMediaBackfillOverlay.R0" ||
      overlay.rights_release !== false || overlay.media_bytes_uploaded !== false ||
      !Array.isArray(overlay.candidates) || overlay.candidates.length > 150) fail("HOLD_OVERLAY_POLICY");
  const nodes = [];
  const ids = new Set();
  for (const n of base.nodes) {
    if (!n || typeof n.id !== "string" || !/^[A-Za-z0-9_:+./-]{1,180}$/.test(n.id) ||
        typeof n.kind !== "string" || typeof n.label !== "string" || ids.has(n.id)) fail("HOLD_BAD_SOURCE_NODE");
    ids.add(n.id);
    nodes.push({id:n.id,kind:n.kind,label:n.label,source:n.source ?? null});
  }
  for (const m of overlay.candidates) {
    if (!m || !/^[A-Za-z0-9_:+./-]{1,180}$/.test(m.id ?? "") ||
        !m.source || m.source.repository !== "CoCivium/CoCivium" ||
        !/^[0-9a-f]{40}$/.test(m.source.git_blob_sha1 ?? "") ||
        m.privacy !== "PUBLIC_METADATA_ONLY" ||
        m.rights !== "PUBLIC_SOURCE_READABLE_DERIVATIVE_RIGHTS_NOT_VERIFIED" ||
        m.bytes_copied_into_overlay !== false || ids.has(m.id) ||
        typeof m.label !== "string" || m.label.length > 90 ||
        m.relation_type !== "INSPIRATION_CANDIDATE_FOR" || m.seed_ref !== overlay.work_id ||
        m.path_status !== "PROPOSED_NOT_EXECUTED" ||
        typeof m.next_test !== "string" || m.next_test.length < 15 || m.next_test.length > 200) fail("HOLD_MEDIA_CANDIDATE_BOUNDARY");
    ids.add(m.id);
    nodes.push({id:m.id,kind:"media_candidate",label:m.label,source:m.source.path});
  }
  const edges = [];
  for (const e of base.edges) {
    if (!e || typeof e.from !== "string" || typeof e.to !== "string" ||
        typeof e.relation !== "string" || !ids.has(e.from) || !ids.has(e.to)) fail("HOLD_BASE_EDGE_ENDPOINT");
    edges.push({from:e.from,to:e.to,relation:e.relation});
  }
  for (const m of overlay.candidates) {
    if (!ids.has(m.relation_to)) fail("HOLD_MEDIA_EDGE_ENDPOINT");
    edges.push({from:m.id,to:m.relation_to,relation:m.relation_type});
  }
  const nodeBy = new Map(nodes.map(n=>[n.id,n]));
  const groups = [
    ["map","CoMap and CoOrb"],
    ["domain","Evolution domains"],
    ["repository","Repositories"],
    ["highlight","Highlights"],
    ["source_document","Documents"],
    ["media_candidate","Prior media inspirations"]
  ];
  for (const n of nodes) if (!groups.some(g=>g[0]===n.kind)) fail("HOLD_UNKNOWN_NODE_KIND");
  const groupVar = new Map(groups.map((g,i)=>[g[0],"G"+i]));
  const countGroups = new Map(groups.map(g=>[g[0],nodes.filter(n=>n.kind===g[0]).length]));
  const lines = [
    "# CoNav+ | Atlas of diagrams R0", "",
    "**SOURCE-ONLY, PUBLIC-SAFE, PINNED PROJECTION. Not the X2 CoOrb, an all-session census, a live media index, or a receiver ACK.**", "",
    "Based on [existing CoMap source graph](../../ai/comap-source-projection-r0.json) and [five-source retro-media overlay](prior-media-backfill-overlay-r0.json). An earlier bounded private inspiration sample and local screenshots are not copied here.", "",
    "**View:** start with a small line-and-box overview, then choose a group below. Every group has paged sub-diagrams and text relations. Old and alternative versions remain in their original sources.", "",
    "## Overview", "",
    "```mermaid", "flowchart LR",
    '  Root["CoNav atlas | one source spine"]'
  ];
  for (const [kind,name] of groups) {
    lines.push(`  ${groupVar.get(kind)}["${clean(name)} (${countGroups.get(kind)})"]`);
    lines.push(`  Root --> ${groupVar.get(kind)}`);
  }
  const cross = new Map();
  for (const e of edges) {
    const a=nodeBy.get(e.from).kind, b=nodeBy.get(e.to).kind;
    if (a===b) continue;
    const k=[a,b,e.relation].join("|"); cross.set(k,(cross.get(k)||0)+1);
  }
  for (const [k,n] of [...cross.entries()].sort()) {
    const [a,b,relation]=k.split("|");
    lines.push(`  ${groupVar.get(a)} -->|${clean(relation)} x${n}| ${groupVar.get(b)}`);
  }
  lines.push("```", "", "## Diagram index", "", "| Open a diagram | Source objects |", "| --- | ---: |");
  for (const [kind,label] of groups) lines.push(`| [${label}](#${kind.replaceAll("_","-")}-views) | ${countGroups.get(kind)} |`);
  lines.push("", "## Views and typed relations", "");
  const pageSize=12, visible = new Set(), edgeShown = new Set();
  for (const [kind,label] of groups) {
    const sourceNodes=nodes.filter(n=>n.kind===kind).sort((a,b)=>a.id.localeCompare(b.id));
    lines.push(`### ${kind.replaceAll("_","-")} views`, "", `**${label}: ${sourceNodes.length} source objects.**`);
    if (!sourceNodes.length) {lines.push("No source objects registered.", "");continue;}
    for(let pos=0;pos<sourceNodes.length;pos+=pageSize) {
      const page=sourceNodes.slice(pos,pos+pageSize), pnum=pos/pageSize+1;
      lines.push("",`#### ${clean(label)} | page ${pnum} of ${Math.ceil(sourceNodes.length/pageSize)}`, "", "```mermaid","flowchart LR",`  P["${clean(label)} / page ${pnum}"]`);
      const nodeVariables=new Map(),targetVariables=new Map();
      page.forEach((n,i)=>{const v="N"+i;nodeVariables.set(n.id,v);visible.add(n.id);lines.push(`  ${v}["${clean(n.label)}"]`);lines.push(`  P --> ${v}`);});
      let ext=0;
      for(const e of edges.filter(e=>nodeVariables.has(e.from))) {
        const a=nodeVariables.get(e.from);
        let b=nodeVariables.get(e.to);
        if(!b) {
          if(!targetVariables.has(e.to)) {
            const v="X"+(ext++);targetVariables.set(e.to,v);
            const target=nodeBy.get(e.to);
            lines.push(`  ${v}["${clean(target.label)} | ${clean(target.kind)}"]`);
          }
          b=targetVariables.get(e.to);
        }
        lines.push(`  ${a} -->|${clean(e.relation)}| ${b}`);
        edgeShown.add(`${e.from}\u0000${e.to}\u0000${e.relation}`);
      }
      lines.push("```", "", "| Source object | Type | Outgoing relations |", "| --- | --- | --- |");
      for(const n of page) {
        const outgoing=edges.filter(e=>e.from===n.id).map(e=>`${e.relation} → ${e.to}`);
        lines.push(`| \`${n.id}\` | ${clean(n.kind)} | ${outgoing.length?outgoing.map(clean).join("; "):"None registered"} |`);
      }
      const media=page.filter(n=>n.kind==="media_candidate");
      if(media.length) {
        lines.push("", "**Exact source pointers (not copied media):**");
        for(const n of media) {
          const item=overlay.candidates.find(x=>x.id===n.id);
          lines.push(`- [${clean(n.label)}](../../${item.source.path}) | Git blob \`${item.source.git_blob_sha1}\` | rights and receiver uptake **unverified**`);
        }
      }
    }
    lines.push("");
  }
  if (visible.size!==nodes.length || edgeShown.size!==edges.length) fail("HOLD_UNRENDERED_RELATIONS");
  lines.push("## CoSeed and CoPath backfill proposals", "");
  for (const m of overlay.candidates) {
    lines.push(`- [${clean(m.label)}](../../${m.source.path}) | Seed pointer \`${clean(m.seed_ref)}\` | proposed test: ${clean(m.next_test)} | status \`${m.path_status}\``);
  }
  lines.push("");
  lines.push("## Evidence and privacy ceiling", "",
    `- Bounded graph: ${base.nodes.length} earlier source nodes / ${base.edges.length} typed source edges.`,
    `- Retroactive sample: ${overlay.candidates.length} public media **candidates** / same number of typed inspiration edges; prior private assets are not represented.`,
    "- The original source graph remains unmodified, as do previous CoMap/CoLens/CoMail versions.",
    "- Links are source references. Motif selection is a hypothesis, not rights clearance, empirical proof, semantic acceptance, or user permission.",
    "- Diagram boxes do not imply running agents, approved messages, live X2 CoOrb, or any provider/recipient ACK.",
    "- To evolve, check source Git blobs, update the overlay with an explicit successor, re-render and compare. No overwrite without versioned review.", "",
    "`RENDER_NE_TRUTH` · `DIAGRAM_NE_RECEIVER` · `INSPIRATION_NE_LICENSE` · `SOURCE_ONLY_NE_RUNTIME` · `PRIVATE_NE_PUBLIC` · `ADDRESSABLE_NE_ALL_LOADED`", "");
  return {markdown:lines.join("\n"),coverage:{base_nodes:base.nodes.length,base_edges:base.edges.length,backfill_candidates:overlay.candidates.length,total_nodes:nodes.length,total_edges:edges.length,pages:groups.reduce((n,[kind])=>n+Math.ceil((countGroups.get(kind)||0)/pageSize),0)}};
}

function generateMegaScroller(base, overlay, retro, pins) {
  const fail=msg=>{throw Error(msg)};
  const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const safePath=p=>typeof p==="string"&&/^[A-Za-z0-9_+./-]{1,245}$/.test(p)&&!p.startsWith("/")&&!p.split("/").includes("..")&&!p.split("/").includes(".")&&!p.includes("//");
  const gh=p=>{if(!safePath(p))fail("HOLD_PUBLIC_PATH");return "https://github.com/CoCivium/CoCivium/blob/main/"+p.split("/").map(encodeURIComponent).join("/")};
  if(base?.schema!=="CoAll.CoMapProjection.R0"||!Array.isArray(base.nodes)||!Array.isArray(base.edges)||base.nodes.length>1500||base.edges.length>6000)fail("HOLD_GRAPH");
  if(overlay?.schema!=="CoAll.CoNav.PriorMediaBackfillOverlay.R0"||overlay.rights_release!==false||overlay.media_bytes_uploaded!==false||!Array.isArray(overlay.candidates)||overlay.candidates.length>150)fail("HOLD_OVERLAY_POLICY");
  if(retro?.schema!=="CoAll.CoNavRetroMedia.R0"||!Array.isArray(retro.candidates)||retro.candidates.length>100)fail("HOLD_RETRO_POLICY");
  if(!pins||[pins.graph,pins.overlay,pins.retro].some(p=>typeof p!=="string"||! /^[0-9a-f]{40}$/.test(p)))fail("HOLD_SOURCE_PINS");
  const byPath=new Map(), candidates=[];
  for(const item of overlay.candidates){
    const p=item?.source?.path,sha=item?.source?.git_blob_sha1;
    if(!safePath(p)||item.source.repository!=="CoCivium/CoCivium"||! /^[0-9a-f]{40}$/.test(sha)||item.privacy!=="PUBLIC_METADATA_ONLY"||item.rights!=="PUBLIC_SOURCE_READABLE_DERIVATIVE_RIGHTS_NOT_VERIFIED"||item.bytes_copied_into_overlay!==false||item.path_status!=="PROPOSED_NOT_EXECUTED")fail("HOLD_MEDIA_POLICY");
    if(byPath.has(p))fail("HOLD_DUPLICATE_MEDIA_PATH");
    const x={id:item.id,label:item.label,path:p,blob:sha,kind:item.media_kind,groups:["CoNav overlay"],motifs:item.motifs||[],challenge:item.challenge||"",next:item.next_test||"",state:"UNREVIEWED_INSPIRATION_CANDIDATE"};
    byPath.set(p,x);candidates.push(x);
  }
  for(const item of retro.candidates){
    if(!safePath(item?.source_path)||! /^[0-9a-f]{40}$/.test(item.git_blob)||item.visibility!=="PUBLIC_REPO_SOURCE"||item.rights_state!=="METADATA_LINK_ONLY"||item.status!=="RETRO_INSPIRATION_CANDIDATE_UNREVIEWED")fail("HOLD_RETRO_MEDIA_POLICY");
    const prior=byPath.get(item.source_path);
    if(prior){if(prior.blob!==item.git_blob)fail("HOLD_SOURCE_PIN_COLLISION");prior.groups.push("CoNav retro");}
    else{
      const x={id:"retro:"+item.id,label:item.label,path:item.source_path,blob:item.git_blob,kind:item.kind,groups:["CoNav retro"],motifs:[],challenge:"Rights and semantic relevance still require review.",next:item.next_gate,state:"UNREVIEWED_INSPIRATION_CANDIDATE"};
      byPath.set(x.path,x);candidates.push(x);
    }
  }
  candidates.sort((a,b)=>a.label.localeCompare(b.label));
  const nodeIndex=new Map(),all=[];
  for(const n of base.nodes){
    if(!n||typeof n.id!=="string"||nodeIndex.has(n.id)||typeof n.label!=="string"||typeof n.kind!=="string")fail("HOLD_NODE");
    nodeIndex.set(n.id,"node-"+all.length);all.push({...n,isMedia:false});
  }
  for(const c of candidates){
    const id="media-atlas:"+c.path;
    if(nodeIndex.has(id))fail("HOLD_ID_COLLISION");
    nodeIndex.set(id,"node-"+all.length);all.push({id,kind:"media_candidate",label:c.label,source:c.path,status:"UNREVIEWED_CANDIDATE",isMedia:true,candidate:c});
  }
  const edges=[];
  for(const e of base.edges){
    if(!nodeIndex.has(e.from)||!nodeIndex.has(e.to)||typeof e.relation!=="string")fail("HOLD_GRAPH_EDGE");
    edges.push({from:e.from,to:e.to,kind:e.relation,class:"REGISTERED_SOURCE"});
  }
  for(const c of candidates){
    if(!nodeIndex.has("view:CoMap+"))fail("HOLD_ATLAS_ROOT");
    edges.push({from:"media-atlas:"+c.path,to:"view:CoMap+",kind:"INSPIRATION_CANDIDATE_FOR",class:"PROPOSED_LINK"});
  }
  const groups=[
    ["map","CoMap / CoOrb","One map, many observer views","atlas-map"],
    ["domain","Evolution lanes","Registered domains, not active agents","atlas-domain"],
    ["repository","Repository constellation","Names and roles, not repository contents","atlas-repository"],
    ["highlight","CoHighlights","Source-linked ideas and work anchors","atlas-highlight"],
    ["source_document","Source documents","Recoverable references and contracts","atlas-source_document"],
    ["media_candidate","Prior media / CoNav","Public source-pointer candidates only","atlas-media_candidate"]
  ];
  if(all.some(n=>!groups.some(g=>g[0]===n.kind)))fail("HOLD_UNSUPPORTED_NODE_KIND");
  const links=base.sources.filter(s=>safePath(s.path||"")).map(s=>`<a href="${esc(gh(s.path))}">${esc(s.path)}</a>`).join(" · ");
  const css=`
:root{color-scheme:dark;--bg:#07131c;--panel:#10242e;--soft:#17313d;--line:#38616b;--ink:#effbff;--muted:#bdd2d8;--teal:#73e7d3;--violet:#c8b4ff;--gold:#f1d494;--coral:#ffb9a8}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);font:16px/1.58 system-ui,-apple-system,Segoe UI,sans-serif;background:radial-gradient(ellipse at 70% -5%,#1b4c53 0,transparent 48%),var(--bg)}
a{color:var(--teal);overflow-wrap:anywhere}a:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.skip{position:absolute;left:-2000px;top:0;background:var(--gold);color:#15222a;padding:.7rem}.skip:focus{left:1rem;z-index:20}
.shell{max-width:1180px;margin:auto;padding:0 20px}.top{padding:72px 0 42px}.eyebrow{color:var(--teal);font-size:.76rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
h1{font-size:clamp(2.6rem,6vw,5.8rem);line-height:1.05;letter-spacing:-.047em;margin:.3rem 0 1.1rem;max-width:850px}h1 em{color:var(--violet);font-style:normal}
h2{font-size:clamp(1.75rem,3vw,2.85rem);line-height:1.12;letter-spacing:-.025em;margin:.1rem 0 1.1rem}h3{font-size:1.2rem;margin:.25rem 0 .65rem}p{max-width:850px}small,.muted{color:var(--muted)}.intro{font-size:clamp(1.08rem,2vw,1.32rem);max-width:790px;color:#d4e7ed}
.ribbon{display:flex;flex-wrap:wrap;gap:.6rem;margin:25px 0}.metric{min-width:135px;border:1px solid var(--line);border-radius:13px;background:#102730;padding:13px 16px}.metric strong{display:block;font-size:1.5rem;color:var(--teal)}.metric span{font-size:.83rem;color:var(--muted)}
nav{position:sticky;top:0;z-index:10;background:rgba(7,19,28,.96);border-top:1px solid #294854;border-bottom:1px solid #365965;overflow:auto}
nav .navinner{max-width:1180px;margin:auto;display:flex;gap:1rem;padding:13px 20px;white-space:nowrap}nav a{font-size:.88rem;text-decoration:none;color:#d8eaf0}nav a:hover{text-decoration:underline;color:var(--teal)}
.chapter{padding:75px 0;border-bottom:1px solid #294854;scroll-margin-top:70px}.chapter:nth-of-type(even){background:linear-gradient(110deg,rgba(92,57,119,.08),transparent 70%)}
.panel{background:linear-gradient(150deg,#15333d,#11242e);border:1px solid #3b636d;border-radius:18px;padding:clamp(16px,2.5vw,28px);margin:1.1rem 0}
.cap{font-size:.78rem;letter-spacing:.1em;font-weight:800;color:var(--gold);text-transform:uppercase}
.diagram{width:100%;height:auto;background:#0c1f29;border-radius:16px;border:1px solid #31515d;padding:8px}.tree-alt{border-left:3px solid var(--teal);padding-left:1.1rem;color:#c9dee6}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}
.tile{display:block;padding:18px;background:#132b35;border:1px solid #365d67;border-radius:12px;text-decoration:none;color:var(--ink)}.tile:hover{border-color:var(--teal)}.tile strong{display:block;color:var(--teal)}.tile small{display:block;margin-top:.4rem}
details{margin:.85rem 0;border-radius:12px;border:1px solid #385b64;background:#10242e}summary{cursor:pointer;padding:1rem 1.2rem;font-size:1.03rem;font-weight:750}details[open]>summary{border-bottom:1px solid #385b64;color:var(--violet)}
.contents{padding:1rem 1.25rem}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px}.card{background:#162d38;border:1px solid #385c66;border-radius:12px;padding:15px;scroll-margin-top:75px}
.card h4{font-size:1.06rem;margin:.25rem 0}.meta{font-size:.76rem;letter-spacing:.06em;color:var(--gold);text-transform:uppercase}.card p{font-size:.91rem;margin:.55rem 0}.card details{background:#0c202a;margin:.6rem 0}.card details summary{font-size:.85rem;padding:.65rem}
code{overflow-wrap:anywhere;font-size:.85em;color:#d4c3ff}.edges{margin:0;padding-left:1.3rem}.edges li{margin:.4rem 0}.pill{display:inline-block;font-size:.73rem;margin:.15rem;padding:.18rem .45rem;border:1px solid #587680;border-radius:99px;color:#d6e5ea}
.truth{border-left:4px solid var(--gold);padding:12px 18px;background:#2a2a27;border-radius:0 9px 9px 0}.danger{border-left-color:var(--coral)}
.timestep{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:14px}.timestep div{padding:16px;border:1px solid var(--line);border-radius:12px;background:#132a34}
footer{padding:46px 0 90px;color:var(--muted)}@media(max-width:600px){.top{padding:44px 0 24px}.chapter{padding:48px 0}.diagram{display:none}h1{letter-spacing:-.03em}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{nav{position:static}.chapter{break-inside:avoid}.diagram{display:none}details:not([open]) .contents{display:block}body{background:white;color:black}.panel,.card,.tile{color:black;background:white}a{color:#13586c}}
`;
  const sourcePins=`<code>${esc(pins.graph)}</code> · <code>${esc(pins.overlay)}</code> · <code>${esc(pins.retro)}</code>`;
  const summary=[
    `<header class="shell top"><div class="eyebrow">CoAll / CoNav / CoMap / CoMegaScroller · public source projection R0</div>`,
    `<h1>One source spine.<br><em>Many ways to see.</em></h1>`,
    `<p class="intro">A scrollable atlas of atlases: lines and boxes at first glance, source-bound relations as you descend, and versioned possibilities without erasing prior work.</p>`,
    `<div class="ribbon"><div class="metric"><strong>${base.nodes.length}</strong><span>registered source objects</span></div><div class="metric"><strong>${base.edges.length}</strong><span>typed source edges</span></div><div class="metric"><strong>${candidates.length}</strong><span>unique retro-media pointers</span></div><div class="metric"><strong>0</strong><span>media copied or sends</span></div></div>`,
    `<p class="truth"><strong>Evidence ceiling:</strong> this is a public, offline-readable source snapshot, not deployed CoOrbWare, X2 acceptance, a universal corpus, recipient ACK or an independently backed-up website.</p></header>`
  ].join("\n");
  const nav=`<nav aria-label="Megascroller chapter navigation"><div class="navinner"><a href="#here">Start</a><a href="#overview">Overview</a><a href="#maps">Six maps</a><a href="#graph">Relation directory</a><a href="#retro">Retro inspirations</a><a href="#evolution">CoEv and CoLUE</a><a href="#time">CoTime</a><a href="#resilience">Resilience</a><a href="#evidence">Proof</a></div></nav>`;
  const points=[["CoMap + CoOrb","atlas-map"],["Domains","atlas-domain"],["Repositories","atlas-repository"],["Highlights","atlas-highlight"],["Documents","atlas-source_document"],["Prior media","atlas-media_candidate"]];
  const colors=["#77e9da","#d3b1ff","#f1d494","#8ddcb6","#f9c0a5","#92ccff"];
  let svg=`<svg class="diagram" role="img" aria-label="CoAll source atlas flows into six maps: CoMap and Orb, domains, repositories, highlights, documents, and prior media" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 315">`;
  svg+=`<rect x="338" y="12" width="224" height="59" rx="12" fill="#173847" stroke="#73e7d3" stroke-width="2"/><text x="450" y="48" text-anchor="middle" font-size="19" fill="#fff" font-family="system-ui">CoAll source spine</text>`;
  points.forEach((p,i)=>{const row=Math.floor(i/3),col=i%3,x=20+col*302,y=132+row*95;svg+=`<line x1="450" y1="71" x2="${x+130}" y2="${y}" stroke="${colors[i]}" stroke-width="1.4" opacity=".65"/><rect x="${x}" y="${y}" rx="11" width="260" height="55" fill="#1b3340" stroke="${colors[i]}"/><text x="${x+130}" y="${y+34}" fill="#f0f9fb" text-anchor="middle" font-size="17" font-family="system-ui">${esc(p[0])}</text>`;});
  svg+="</svg>";
  const tiles=groups.map(([kind,title,desc,id])=>`<a class="tile" href="#${id}"><strong>${esc(title)}</strong><small>${esc(desc)} · ${all.filter(n=>n.kind===kind).length} entries</small></a>`).join("\n");
  const overview=`<section id="overview" class="chapter"><div class="shell"><div class="cap">01 / Navigate</div><h2>Diagram of diagrams</h2><p>Every box opens a progressively more detailed account of registered sources and typed connections. The diagram's readable equivalent is directly below it.</p><figure class="panel">${svg}<figcaption class="muted">Schematic navigation only. Line placement is not evidence of causality, authority or synchronization.</figcaption></figure><div class="tree-alt">Root → CoMap/CoOrb · Evolution lanes · Repositories · Highlights · Documents · Public retro-media candidates. Each branch links to the original public sources.</div><div class="grid" style="margin-top:22px">${tiles}</div></div></section>`;
  function graphCard(n){
    const outgoing=edges.filter(e=>e.from===n.id),incoming=edges.filter(e=>e.to===n.id);
    const c=n.candidate||null,metapath=c?.path||base.sources.find(s=>s.id===n.source)?.path||null;
    const permalink=metapath&&safePath(metapath)?`<a href="${esc(gh(metapath))}">Source file (moving main link)</a>`:"<span class='muted'>See graph source and declared source ID</span>";
    const rels=[...outgoing.map(e=>({kind:e.kind,other:e.to,arrow:"→",c:e.class})),...incoming.map(e=>({kind:e.kind,other:e.from,arrow:"←",c:e.class}))];
    const li=rels.map(r=>`<li>${esc(r.arrow)} <strong>${esc(r.kind)}</strong> <a href="#${esc(nodeIndex.get(r.other))}">${esc(r.other)}</a> <small>${esc(r.c)}</small></li>`).join("");
    return `<article id="${esc(nodeIndex.get(n.id))}" class="card"><div class="meta">${esc(n.kind)} · ${esc(n.status||"REGISTERED_SOURCE")}</div><h4>${esc(n.label)}</h4><p><code>${esc(n.id)}</code></p>${c?`<p>Git blob pin: <code>${esc(c.blob)}</code></p><p>Registry: ${esc(c.groups.join(" + "))}</p>`:`<p class="muted">Source ref: <code>${esc(n.source||"UNSPECIFIED")}</code></p>`}<p>${permalink}</p><details><summary>Relations (${rels.length})</summary><div class="contents"><ul class="edges">${li||"<li>No typed relations in this bounded snapshot</li>"}</ul></div></details></article>`;
  }
  let grouped=`<section id="graph" class="chapter"><div class="shell"><div class="cap">03 / Inspect</div><h2>The source-bound relation directory</h2><p>Source graph: ${base.nodes.length} nodes and ${base.edges.length} typed edges. Seven deduplicated media candidates add ${candidates.length} <em>proposed</em> inspiration links, giving ${all.length} browsable cards and ${edges.length} total displayed relations. Do not confuse proposed relations with verified ones.</p>`;
  for(const [kind,title,desc,id] of groups){
    const subset=all.filter(n=>n.kind===kind);
    grouped+=`<details id="${esc(id)}" class="panel"><summary>${esc(title)} · ${subset.length} objects</summary><div class="contents"><p>${esc(desc)}</p><div class="cards">${subset.map(graphCard).join("\n")}</div></div></details>`;
  }
  grouped+=`</div></section>`;
  const maps=`<section id="maps" class="chapter"><div class="shell"><div class="cap">02 / Zoom</div><h2>Six maps, not six ontologies</h2><p>Choose a lens. Every section below is a smaller diagram of the same public source universe; the <a href="${esc(gh("examples/comap/source-weave-r0.html"))}">existing interactive CoMap SVG</a> remains an independent option.</p><div class="grid">${groups.map(([kind,name,desc,id])=>`<a class="tile" href="#${id}"><strong>${esc(name)}</strong><small>${esc(desc)}</small></a>`).join("")}</div><p class="muted">For the paged Mermaid equivalent, <a href="${esc(gh("examples/comap/diagram-of-diagrams-r0.md"))}">open the earlier CoNav source atlas</a>. This HTML is a reader-friendly successor view, not a replacement of that file.</p></div></section>`;
  const retroCards=candidates.map(c=>`<article class="card"><div class="meta">${esc(c.kind)} · candidate only</div><h3>${esc(c.label)}</h3><p><a href="${esc(gh(c.path))}">Open public original</a></p><p><small>Source Git blob:</small> <code>${esc(c.blob)}</code></p><p>Index: ${esc(c.groups.join(" / "))}</p><p><strong>Motifs:</strong> ${esc(c.motifs.join("; ")||"Requires semantic review")}</p><p><strong>Challenge:</strong> ${esc(c.challenge||"Rights and relevance remain unreviewed.")}</p><p><strong>Next:</strong> ${esc(c.next||"Qualify intended use and rights.")}</p><span class="pill">CoSeed/CoPath: PROPOSED</span><span class="pill">No media bytes copied</span></article>`).join("\n");
  const retroSection=`<section id="retro" class="chapter"><div class="shell"><div class="cap">04 / Discover</div><h2>Retroactive inspiration, without retroactive authority</h2><p>${candidates.length} distinct public media candidates deduplicated from two existing registers. ${retro.candidates.length} CoNav retro items and ${overlay.candidates.length} CoMap overlay items overlap by exact source path/hash. This is an index of <em>possibilities</em>, not an adopted corpus or exhaustive historical scan.</p><div class="grid">${retroCards}</div><p class="truth danger"><strong>Private branch intentionally absent.</strong> Earlier private Library visuals, screenshots, private Gmail drafts, and messages are not reproduced here. Privacy and license review precede any reusable public derivative.</p></div></section>`;
  const evol=`<section id="evolution" class="chapter"><div class="shell"><div class="cap">05 / Evolve</div><h2>CoEv+ and CoLUE+: successors, not silent overwrites</h2><div class="panel"><h3>Source → Candidate → Challenge → Qualified successor</h3><p>One WorkID can fan out into a diagram, article, accessible text, CoOrb view, or staged email proposal. Corrections feed back as new candidates. A predecessor stays recoverable; revisions trigger new exact-content review and permission checks.</p><div class="grid"><a class="tile" href="${esc(gh("examples/comail_r0/outreach_stage_gate_r0.py"))}"><strong>CoLUE stage gate</strong><small>Separate draft, approval, authority, provider effect, receipt, recipient outcome</small></a><a class="tile" href="${esc(gh("examples/colensmedia/relational_media_diagram_r0.md"))}"><strong>CoMedia lineage</strong><small>Typed source-derived diagram and accessible textual twin</small></a><a class="tile" href="${esc(gh("docs/Architecture/CODIAGRAM_INSPIRATION_CORPUS_R0_20261025.md"))}"><strong>CoDiagram inheritance</strong><small>Motif, inverse, falsifier, rights, accessible replacement</small></a></div></div><p class="truth">No Gmail draft was read, edited or sent by this atlas. A public media pointer is not permission to republish an original image.</p></div></section>`;
  const temporal=`<section id="time" class="chapter"><div class="shell"><div class="cap">06 / Version</div><h2>CoTime and the permeable CoOrb border</h2><div class="timestep"><div><h3>Recorded past</h3><p>Historical <a href="${esc(gh("docs/Public/Snapshots/2026-10-19_CoMegaScroller_CC_CoTheoryAll_R0.md"))}">October 19 megascroller</a> and <a href="${esc(gh("docs/CoEvo/CoEvo_Megascroller_v0__2026-03-24.md"))}">March CoEvo predecessor</a> remain separately inspectable.</p></div><div><h3>Observed source</h3><p>The pinned public graph and two candidate manifests exist at the three source IDs below. Their linked target files require their own observation for currentness.</p></div><div><h3>Projected next</h3><p>Actual receiver use, X2 CoOrb integration and site mirroring are proposed acceptance gates, not observed outcomes.</p></div><div><h3>Counterfactual</h3><p>What if an old image suggests a different topology? Preserve the competing branch until a falsifying test decides its value.</p></div></div><p class="muted">No prediction calibration, real-time synchronization or universal historical inventory is claimed.</p></div></section>`;
  const backups=`<section id="resilience" class="chapter"><div class="shell"><div class="cap">07 / Recover</div><h2>Public constellation and real redundancy</h2><div class="grid"><div class="card"><h3>GitHub source</h3><span class="pill">LANDED SOURCE</span><p>This self-contained HTML and three source manifests are durable GitHub objects with exact Git blob identities.</p></div><div class="card"><h3>Offline reader</h3><span class="pill">SINGLE-FILE VIEW</span><p>All diagram labels, cards and accessible text are in this file. External source links need connectivity, but the page itself has no network dependencies.</p></div><div class="card"><h3>Web domain / Pages</h3><span class="pill">NOT VERIFIED</span><p>Site publication requires a separately observed deploy, exact content hash, HTTPS check and fallback URL.</p></div><div class="card"><h3>Independent backup / CoStead</h3><span class="pill">NOT VERIFIED</span><p>One GitHub repo is one failure domain. A second independently controlled byte copy needs its own receipt and restore test.</p></div></div><p class="truth">Fractal navigation is hierarchical presentation; holographic recovery is a metaphor until independently recoverable replicas are demonstrated. Multiple URLs on the same provider are not an independent backup.</p></div></section>`;
  const proof=`<section id="evidence" class="chapter"><div class="shell"><div class="cap">08 / Proof</div><h2>One truthful version, several readable surfaces</h2><div class="panel"><h3>Exact pinned source objects</h3><p><strong>CoMap graph / backfill overlay / CoNav retro manifest:</strong> ${sourcePins}</p><p><strong>Primary graph sources:</strong> ${links}</p><p><strong>Originals:</strong> <a href="${esc(gh("examples/comap/source-weave-r0.html"))}">interactive CoMap</a> · <a href="${esc(gh("examples/colensmedia/conav_navigator_r0.html"))}">CoNav HTML</a> · <a href="${esc(gh("examples/comap/diagram-of-diagrams-r0.md"))}">paged diagrams</a>.</p></div><p><strong>Acceptance still open:</strong> independent GitHub Actions PASS for this new render, a measured first-use UX, public website deployment, independent host backup/restore, source-to-CoSeed semantic adoption, any live X2 receiver, and 24-hour unattended survivorship.</p><p class="muted">Rails: SOURCE_POINTER ≠ MEDIA_CUSTODY · REGISTERED ≠ RUNNING · INSPIRATION ≠ LICENSE · LAYOUT ≠ CAUSALITY · RENDER ≠ RECEIVER_ACK · G_DSIDE ≠ EMPIRICAL_PROOF · LANDED ≠ PICKED_UP.</p><a href="#here">Return to first view</a></div></section>`;
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="CoAll source-bound megascroller: nested CoMap, CoNav and CoMedia relation diagrams with private-safe retro inspiration pointers.">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; script-src 'none'; base-uri 'none'; form-action 'none'">
<title>CoAll | CoMap+ CoNav+ Megascroller R0</title><style>${css}</style></head><body>
<a href="#here" class="skip">Skip to main content</a><div id="here">${summary}</div>${nav}
<main>${overview}${maps}${grouped}${retroSection}${evol}${temporal}${backups}${proof}</main>
<footer class="shell"><strong>CoAll / CoMegaScroller R0</strong><p>Source-only public projection. The original graph and earlier megascrollers remain unmodified. No user action, account access, tracking, remote code, cookies, media downloads, or automatic correspondence occurs here.</p><p>One Seed · Many views · Evidence before effect · Break Glass always.</p></footer></body></html>
`;
}

function gitBlobSHA(bytes) {
  const prefix=Buffer.from("blob " + bytes.length + String.fromCharCode(0));
  return crypto.createHash("sha1").update(prefix).update(bytes).digest("hex");
}
function securePath(root, rel) {
  if(typeof rel!=="string" || !/^[A-Za-z0-9_+./-]+$/.test(rel) ||
     rel.startsWith("/") || rel.split("/").includes("..")) throw Error("HOLD_UNSAFE_SOURCE_PATH");
  const full=path.resolve(root,rel);
  if(!full.startsWith(root+path.sep) || fs.lstatSync(full).isSymbolicLink()) throw Error("HOLD_OUTSIDE_SOURCE");
  return full;
}
function checkedSource(root, rel, expected) {
  const bytes=fs.readFileSync(securePath(root,rel));
  const actual=gitBlobSHA(bytes);
  if(actual!==expected) throw Error("HOLD_GIT_BLOB_DRIFT "+rel);
  return bytes;
}
function run(root, target, check) {
  root=path.resolve(root);
  const overlayPath=path.join(root,"examples/comap/prior-media-backfill-overlay-r0.json");
  const overlay=JSON.parse(fs.readFileSync(overlayPath,"utf8"));
  const baseBytes=checkedSource(root,overlay.source_graph.path,overlay.source_graph.git_blob_sha1);
  for(const item of overlay.candidates) checkedSource(root,item.source.path,item.source.git_blob_sha1);
  const output=generateAtlas(JSON.parse(baseBytes),overlay);
  const retroPath=path.join(root,"examples/colensmedia/conav_retro_manifest_r0.json");
  const retro=JSON.parse(fs.readFileSync(retroPath,"utf8"));
  for(const item of retro.candidates||[]) checkedSource(root,item.source_path,item.git_blob);
  const pins={graph:overlay.source_graph.git_blob_sha1,
              overlay:gitBlobSHA(fs.readFileSync(overlayPath)),
              retro:gitBlobSHA(fs.readFileSync(retroPath))};
  const mega=generateMegaScroller(JSON.parse(baseBytes),overlay,retro,pins);
  const megaTarget=path.join(root,"examples/comap/megascroller-r0.html");
  if(check) {
    if(fs.readFileSync(target,"utf8")!==output.markdown) throw Error("HOLD_ATLAS_OUT_OF_SYNC");
    if(fs.readFileSync(megaTarget,"utf8")!==mega) throw Error("HOLD_MEGASCROLLER_OUT_OF_SYNC");
  } else {
    fs.writeFileSync(target,output.markdown,{flag:"wx"});
    fs.writeFileSync(megaTarget,mega,{flag:"wx"});
  }
  return output.coverage;
}
module.exports={generateAtlas,generateMegaScroller,gitBlobSHA,securePath,checkedSource,run};
if(require.main===module) {
  const argv=process.argv.slice(2),check=argv.includes("--check");
  if(argv.filter(x=>x==="--check").length>1) throw Error("HOLD_ARGS");
  const root=path.resolve(__dirname,"..");
  const target=path.resolve(root,"examples/comap/diagram-of-diagrams-r0.md");
  const status=run(root,target,check);
  process.stdout.write(JSON.stringify({result:check?"EXACT_ATLAS_MATCH":"SOURCE_ONLY_ATLAS_GENERATED",coverage:status})+String.fromCharCode(10));
}
