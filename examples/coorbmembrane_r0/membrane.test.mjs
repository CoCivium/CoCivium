import test from "node:test";
import assert from "node:assert/strict";
import {validate,project,toText,toSVG} from "./membrane.mjs";
const sha="a".repeat(64);
const fixture=()=>({
  work_id:"Co261108e",work_version:"R0",seed_sha:sha,policy_version:"P0",proof_scope:"SYNTHETIC_FIXTURE_ONLY",observed_at:"2026-11-08T22:30:00Z",
  edges:[
    {edge_id:"receipt",target:"receiver-A",status:"VERIFIED",source_sha:sha,privacy_class:"PUBLIC",observed_at:"2026-11-08T22:29:00Z",valid_to:"2026-11-08T22:31:00Z",receiver_readproof:"readback:abc",authorized:true},
    {edge_id:"future",target:"scenario-B",status:"FORECAST",source_sha:sha,privacy_class:"PUBLIC",observed_at:"2026-11-08T22:30:00Z",horizon:"P1D",confidence:0.42,falsifier:"no observed effect",baseline_ref:"synthetic:baseline"},
    {edge_id:"conflict",target:"contradiction",status:"CONTRADICTED",source_sha:sha,privacy_class:"PUBLIC",observed_at:"2026-11-08T22:30:00Z"},
    {edge_id:"crossing",target:"blocked-gateway",status:"HELD",source_sha:sha,privacy_class:"PUBLIC",observed_at:"2026-11-08T22:30:00Z"},
    {edge_id:"unknown",target:"offline-X2",status:"UNKNOWN",source_sha:sha,privacy_class:"PUBLIC",observed_at:"2026-11-08T22:30:00Z"}
  ]});
test("headless and SVG share exact status/identity/time tokens",()=>{
 const p=project(fixture());
 const txt=toText(p), svg=toSVG(p);
 assert.match(svg,/role="img"/);assert.match(svg,/<desc id="orbdesc">/);
 for(const v of [p.work_id,p.work_version,p.as_of,"VERIFIED","FORECAST","CONTRADICTED","HELD","UNKNOWN"]){
   assert.ok(txt.includes(v));assert.ok(svg.includes(v));
 }
 assert.equal(p.edges[0].receiver_readproof,"readback:abc");
 assert.equal(p.proof_scope,"SYNTHETIC_FIXTURE_ONLY");
 assert.equal(p.receiver_ack,"NOT_OBSERVED");
 assert.match(txt,/NO LIVE RECEIVER ACK/);
 assert.match(svg,/SYNTHETIC ONLY - NO LIVE ACK/);
});
test("expiry propagates across both views",()=>{
 const p=project(fixture(),"2026-11-08T22:33:00Z");
 assert.equal(p.edges[0].status,"STALE");
 assert.equal(p.edges[0].receiver_readproof,null);
 assert.match(toText(p),/receipt: receiver-A \| STALE/);
 assert.match(toSVG(p),/receipt: STALE/);
});
test("unsupported proof does not qualify as verified",()=>{
 const f=fixture();delete f.edges[0].receiver_readproof;
 assert.throws(()=>validate(f),/false verified/);
});
test("forecast cannot pass as measured effect",()=>{
 const f=fixture();delete f.edges[1].horizon;
 assert.throws(()=>validate(f),/forecast missing/);
});
test("duplicate and malicious label fail closed",()=>{
 const f=fixture();f.edges[1].edge_id="receipt";
 assert.throws(()=>validate(f),/duplicate/);
 const h=fixture();h.edges[2].target='<script>alert("x")</script>';
 assert.ok(!toSVG(project(h)).includes("<script>"));
});
test("replay deterministic",()=>{
 assert.equal(toSVG(project(fixture())),toSVG(project(fixture())));
});

test("private or missing privacy class never reaches public view",()=>{
 const f=fixture();f.edges[1].privacy_class="PRIVATE";
 assert.throws(()=>project(f),/private or unqualified edge/);
 const g=fixture();delete g.edges[1].privacy_class;
 assert.throws(()=>project(g),/private or unqualified edge/);
});
test("live scope cannot counterfeit source-only membrane proof",()=>{
 const f=fixture();f.proof_scope="LIVE_OBSERVED";
 assert.throws(()=>project(f),/synthetic proof scope required/);
});
test("unsupported edge source identity cannot be rendered",()=>{
 const f=fixture();f.edges[0].source_sha="self-attested";
 assert.throws(()=>project(f),/edge source SHA256 invalid/);
});
test("forecasts require falsifier, baseline and finite confidence",()=>{
 const f=fixture();delete f.edges[1].falsifier;
 assert.throws(()=>project(f),/forecast missing/);
 const g=fixture();g.edges[1].confidence=Infinity;
 assert.throws(()=>project(g),/forecast missing/);
});
test("bounded edge budget prevents unbounded visual fanout",()=>{
 const f=fixture();
 f.edges=Array.from({length:25},(_,i)=>({...f.edges[2],edge_id:"conflict"+i}));
 assert.throws(()=>project(f),/capped at 24/);
});
