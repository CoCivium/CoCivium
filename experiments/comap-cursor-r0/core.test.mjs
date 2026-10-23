import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {seed,validate,projection,ghost,acceptSuggestion,checkpoint,restore} from "./core.mjs";

test("synthetic source validates",()=>assert.deepEqual(validate(seed),[]));
test("four views bind the same identity and unchanged source",()=>{
 const before=JSON.stringify(seed);
 for(const mode of ["map","orb","trails","ambient"]){
  const p=projection(seed,mode,6);
  assert.equal(p.identity,seed.identity);
  assert.equal(p.version,seed.version);
  assert.equal(p.edges.length,6);
  assert.equal(p.receiver_ack,"UNPROVEN");
 }
 assert.equal(JSON.stringify(seed),before);
});
test("time projection never invents new links",()=>{
 const p=projection(seed,"map",2);
 assert.deepEqual(p.edges.map(e=>e.id),["e1","e2"]);
 assert.equal(p.censored_edges,4);
 assert.equal(projection(seed,"orb",0).edges.length,0);
});
test("forecast remains marked predicted",()=>{
 const f=projection(seed,"map",6).edges.find(e=>e.id==="e6");
 assert.equal(f.epistemic,"PREDICTED");
 assert.equal(seed.nodes.find(n=>n.id==="future").epistemic,"PREDICTED");
});
test("unrecognized epistemic class fails closed",()=>{
 const g=structuredClone(seed);g.nodes[0].epistemic="ACKNOWLEDGED";assert.ok(validate(g).includes("NODE_EPISTEMIC"));
});
test("orphan edge fails closed",()=>{
 const g=structuredClone(seed);g.edges[0].to="missing";assert.ok(validate(g).includes("ORPHAN_EDGE"));
});
test("duplicate node fails closed",()=>{
 const g=structuredClone(seed);g.nodes.push({...g.nodes[0]});assert.ok(validate(g).includes("DUPLICATE_NODE"));
});
test("false ACK in source fails closed",()=>{
 const g=structuredClone(seed);g.metadata.receiver_ack="PROVEN";assert.ok(validate(g).includes("FALSE_ACK"));
});
test("no suggestion for unrelated text",()=>assert.equal(ghost("hello world",11),""));
test("suggestion is deterministic and only beyond caret",()=>{
 const a=ghost("Compare",7);assert.ok(a.includes("readproof"));
 assert.equal(ghost("Compare other",7),a);
 assert.equal(ghost("Compare other",13),"");
});
test("no auto acceptance",()=>assert.throws(()=>acceptSuggestion("Compare",7,ghost("Compare",7),false),/NO_EXPLICIT_ACCEPTANCE/));
test("explicit acceptance preserves trailing authored text",()=>{
 const g=ghost("Compare other",7);
 const v=acceptSuggestion("Compare other",7,g,true);
 assert.ok(v.text.endsWith(" other"));
 assert.ok(v.text.startsWith("Compare the source"));
 assert.equal(v.effect,"LOCAL_TEXT_EDIT_ONLY");
 assert.equal(v.receiver_ack,"UNPROVEN");
});
test("stale ghost rejected",()=>assert.throws(()=>acceptSuggestion("Review",6,"fake",true),/STALE_OR_INVALID/));
test("invalid input cursor rejected",()=>assert.throws(()=>ghost("x",5),/BAD_INPUT_CURSOR/));
test("source-bound checkpoint survives exact restore",()=>{
 const c=checkpoint("Compare the source","trails",3,[{type:"LOCAL_EDIT"}]);
 assert.deepEqual(restore(JSON.parse(JSON.stringify(c))),c);
 assert.equal(c.submission,"NONE");
 assert.equal(c.provider_session,"NONE");
 assert.equal(c.receiver_ack,"UNPROVEN");
});
test("forged checkpoint receiver ACK rejected",()=>{
 const c=checkpoint("x","map",1);c.receiver_ack="ACKED";
 assert.throws(()=>restore(c),/INCOMPATIBLE_CHECKPOINT/);
});
test("stale seed version checkpoint rejected",()=>{
 const c=checkpoint("x","map",1);c.source_version="future-version";
 assert.throws(()=>restore(c),/INCOMPATIBLE_CHECKPOINT/);
});
test("invalid view or time rejected",()=>{
 assert.throws(()=>projection(seed,"wallpaper",6),/BAD_MODE/);
 assert.throws(()=>projection(seed,"map",7),/BAD_CURSOR/);
});
test("no network API or remote SDK dependency",()=>{
 const html=readFileSync(new URL("./index.html",import.meta.url),"utf8");
 const app=readFileSync(new URL("./app.mjs",import.meta.url),"utf8");
 assert.ok(!html.includes("https://"));
 for(const forbidden of ["fetch(","XMLHttpRequest","WebSocket(","mediaDevices","localStorage","sessionStorage","sendBeacon","eval("]){
  assert.ok(!app.includes(forbidden),"unexpected app primitive "+forbidden);
 }
 assert.ok(html.includes('id="scene"'));
 assert.ok(html.includes('id="accept"'));
});
test("exhaustive 7-step projection preserves source and ACK",()=>{
 for(let cursor=0;cursor<=6;cursor++){
  for(const mode of ["map","orb","trails","ambient"]){
   const p=projection(seed,mode,cursor);
   assert.ok(p.edges.every(e=>e.at<=cursor));
   assert.equal(p.receiver_ack,"UNPROVEN");
  }
 }
});
