"use strict";
/** CoNav nested atlas: deterministic source/currentness, rights and omission controls. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const os=require("node:os");
const {
  generateAtlas,generateMegaScroller,gitBlobSHA,securePath,checkedSource,run
}=require("./CoNavNestedAtlasR0.cjs");

const root=path.resolve(__dirname,"..");
const graph=JSON.parse(fs.readFileSync(path.join(root,"ai/comap-source-projection-r0.json"),"utf8"));
const overlay=JSON.parse(fs.readFileSync(path.join(root,"examples/comap/prior-media-backfill-overlay-r0.json"),"utf8"));
const copy=x=>JSON.parse(JSON.stringify(x));
let passed=0;
function test(name,fn){fn();passed++;process.stdout.write("PASS "+name+"\n");}

test("Git blob SHA1 matches known independent fixture",()=>{
  assert.equal(gitBlobSHA(Buffer.from("hi")),"32f95c0d1244a78b2be1bab8de17906fabb2c4a8");
});
test("existing 56/61 CoMap graph is preserved and 5/5 public media overlaid",()=>{
  const out=generateAtlas(graph,overlay);
  assert.deepEqual(out.coverage,{base_nodes:56,base_edges:61,backfill_candidates:5,total_nodes:61,total_edges:66,pages:8});
  assert.match(out.markdown,/Prior media inspirations \(5\)/);
});
test("all eight nested pages exist and include accessible text relations",()=>{
  const out=generateAtlas(graph,overlay);
  assert.equal((out.markdown.match(/#### .* \| page \d+ of \d+/g)||[]).length,8);
  assert.match(out.markdown,/\| Source object \| Type \| Outgoing relations \|/);
});
test("saved diagram exactly matches current verified source",()=>{
  const out=generateAtlas(graph,overlay);
  assert.equal(out.markdown,fs.readFileSync(path.join(root,"examples/comap/diagram-of-diagrams-r0.md"),"utf8"));
});
test("repeated render is deterministic",()=>{
  assert.equal(generateAtlas(graph,overlay).markdown,generateAtlas(graph,overlay).markdown);
});
test("existing public Git blob readback remains pinned",()=>{
  assert.deepEqual(run(root,path.join(root,"examples/comap/diagram-of-diagrams-r0.md"),true),
                   generateAtlas(graph,overlay).coverage);
});
test("private candidate cannot enter public atlas",()=>{
  const bad=copy(overlay);bad.candidates[0].privacy="PRIVATE";
  assert.throws(()=>generateAtlas(graph,bad),/HOLD_MEDIA_CANDIDATE_BOUNDARY/);
});
test("media bytes publication flag fails closed",()=>{
  const bad=copy(overlay);bad.media_bytes_uploaded=true;
  assert.throws(()=>generateAtlas(graph,bad),/HOLD_OVERLAY_POLICY/);
});
test("derivative rights silently promoted fails closed",()=>{
  const bad=copy(overlay);bad.rights_release=true;
  assert.throws(()=>generateAtlas(graph,bad),/HOLD_OVERLAY_POLICY/);
});
test("source Git blob drift is detected from exact bytes",()=>{
  const file=overlay.candidates[0].source.path;
  assert.throws(()=>checkedSource(root,file,"0".repeat(40)),/HOLD_GIT_BLOB_DRIFT/);
});
test("source traversal and absolute paths denied",()=>{
  assert.throws(()=>securePath(root,"../../etc/passwd"),/HOLD_UNSAFE_SOURCE_PATH/);
  assert.throws(()=>securePath(root,"/etc/passwd"),/HOLD_UNSAFE_SOURCE_PATH/);
});
test("duplicated source ID is rejected",()=>{
  const bad=copy(overlay);bad.candidates[0].id=graph.nodes[0].id;
  assert.throws(()=>generateAtlas(graph,bad),/HOLD_MEDIA_CANDIDATE_BOUNDARY/);
});
test("unresolved media relation is rejected",()=>{
  const bad=copy(overlay);bad.candidates[0].relation_to="missing:neighbor";
  assert.throws(()=>generateAtlas(graph,bad),/HOLD_MEDIA_EDGE_ENDPOINT/);
});
test("broken source graph edge is rejected",()=>{
  const bad=copy(graph);bad.edges[0].to="missing:id";
  assert.throws(()=>generateAtlas(bad,overlay),/HOLD_BASE_EDGE_ENDPOINT/);
});
test("a caller cannot fake currentness via a new source type",()=>{
  const bad=copy(graph);bad.nodes[0].kind="live_verified_worker";
  assert.throws(()=>generateAtlas(bad,overlay),/HOLD_UNKNOWN_NODE_KIND/);
});
test("stale diagram is detected without clobbering",()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),"conav-"));
  try{
    const target=path.join(dir,"atlas.md");fs.writeFileSync(target,"older render");
    assert.throws(()=>run(root,target,true),/HOLD_ATLAS_OUT_OF_SYNC/);
    assert.equal(fs.readFileSync(target,"utf8"),"older render");
  }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test("public output contains no private library handles",()=>{
  const text=generateAtlas(graph,overlay).markdown;
  assert.doesNotMatch(text,/file_00000000|libfile_|\/CoEvoAll\/CoInput|@inseed\.com/i);
});
test("no effect, runtime or recipient ACK is claimed",()=>{
  const text=generateAtlas(graph,overlay).markdown;
  assert.match(text,/Not the X2 CoOrb/);
  assert.match(text,/Diagram boxes do not imply running agents/);
  assert.match(text,/INSPIRATION_NE_LICENSE/);
});

const retro=JSON.parse(fs.readFileSync(path.join(root,"examples/colensmedia/conav_retro_manifest_r0.json"),"utf8"));
const megaPins={
  graph:gitBlobSHA(fs.readFileSync(path.join(root,"ai/comap-source-projection-r0.json"))),
  overlay:gitBlobSHA(fs.readFileSync(path.join(root,"examples/comap/prior-media-backfill-overlay-r0.json"))),
  retro:gitBlobSHA(fs.readFileSync(path.join(root,"examples/colensmedia/conav_retro_manifest_r0.json")))
};

test("CoMegaScroller reader parity: saved HTML exactly matches three pinned input manifests",()=>{
  const rendered=generateMegaScroller(graph,overlay,retro,megaPins);
  assert.equal(rendered,fs.readFileSync(path.join(root,"examples/comap/megascroller-r0.html"),"utf8"));
  assert.match(rendered,/One source spine/);
});
test("CoMegaScroller includes 63 cards and seven deduplicated retro sources",()=>{
  const html=generateMegaScroller(graph,overlay,retro,megaPins);
  assert.equal((html.match(/<article id="node-/g)||[]).length,63);
  assert.equal((html.match(/CoSeed\/CoPath: PROPOSED/g)||[]).length,7);
  assert.match(html,/68 total displayed relations/);
});
test("CoMegaScroller is offline and accessible without a running JavaScript client",()=>{
  const html=generateMegaScroller(graph,overlay,retro,megaPins);
  assert.match(html,/script-src 'none'/);
  assert.match(html,/role="img" aria-label=/);
  assert.match(html,/class="tree-alt"/);
  assert.match(html,/<main>/);
  assert.doesNotMatch(html,/<script[ >]/i);
  assert.doesNotMatch(html,/<img[ >]/i);
});
test("CoMegaScroller cannot leak private library or email account identifiers",()=>{
  const html=generateMegaScroller(graph,overlay,retro,megaPins);
  assert.doesNotMatch(html,/libfile_|file_000000|\/CoEvoAll\/CoInput|@inseed\.com/i);
  assert.match(html,/Earlier private Library visuals, screenshots, private Gmail drafts/);
});
test("CoMegaScroller repeated materialization produces the same exact bytes",()=>{
  assert.equal(generateMegaScroller(graph,overlay,retro,megaPins),
               generateMegaScroller(graph,overlay,retro,megaPins));
});
test("CoMegaScroller changes when its exact source graph changes",()=>{
  const changed=copy(graph);changed.nodes[1].label="Changed source label";
  assert.notEqual(generateMegaScroller(changed,overlay,retro,megaPins),
                  generateMegaScroller(graph,overlay,retro,megaPins));
});
test("CoMegaScroller rejects private retro media, without automatic publication",()=>{
  const changed=copy(retro);changed.candidates[0].visibility="PRIVATE_LIBRARY_SOURCE";
  assert.throws(()=>generateMegaScroller(graph,overlay,changed,megaPins),/HOLD_RETRO_MEDIA_POLICY/);
});
test("CoMegaScroller rejects conflicting source pins across overlapping prior indexes",()=>{
  const changed=copy(retro);changed.candidates[0].git_blob="0".repeat(40);
  assert.throws(()=>generateMegaScroller(graph,overlay,changed,megaPins),/HOLD_SOURCE_PIN_COLLISION/);
});
test("CoMegaScroller rejects media-byte promotion and source traversal",()=>{
  const bad=copy(overlay);bad.media_bytes_uploaded=true;
  assert.throws(()=>generateMegaScroller(graph,bad,retro,megaPins),/HOLD_OVERLAY_POLICY/);
  const moved=copy(retro);moved.candidates[0].source_path="../../private/source";
  assert.throws(()=>generateMegaScroller(graph,overlay,moved,megaPins),/HOLD_RETRO_MEDIA_POLICY/);
});
test("CoMegaScroller keeps independent site backup and X2 acceptance unverified",()=>{
  const html=generateMegaScroller(graph,overlay,retro,megaPins);
  assert.match(html,/Independent backup \/ CoStead/);
  assert.match(html,/NOT VERIFIED/);
  assert.match(html,/No Gmail draft was read, edited or sent/);
});

process.stdout.write(JSON.stringify({suite:"CoNav.NestedAtlas.R0",passed,source_only:true})+"\n");
