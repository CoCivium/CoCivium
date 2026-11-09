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
  if(check) {
    if(fs.readFileSync(target,"utf8")!==output.markdown) throw Error("HOLD_ATLAS_OUT_OF_SYNC");
  } else {
    fs.writeFileSync(target,output.markdown,{flag:"wx"});
  }
  return output.coverage;
}
module.exports={generateAtlas,gitBlobSHA,securePath,checkedSource,run};
if(require.main===module) {
  const argv=process.argv.slice(2),check=argv.includes("--check");
  if(argv.filter(x=>x==="--check").length>1) throw Error("HOLD_ARGS");
  const root=path.resolve(__dirname,"..");
  const target=path.resolve(root,"examples/comap/diagram-of-diagrams-r0.md");
  const status=run(root,target,check);
  process.stdout.write(JSON.stringify({result:check?"EXACT_ATLAS_MATCH":"SOURCE_ONLY_ATLAS_GENERATED",coverage:status})+String.fromCharCode(10));
}
