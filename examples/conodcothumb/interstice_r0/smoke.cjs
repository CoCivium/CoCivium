#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const crypto = require("node:crypto");
const assert = require("node:assert/strict");
const html = fs.readFileSync(path.join(__dirname,"index.html"),"utf8");
const rawManifest=fs.readFileSync(path.join(__dirname,"manifest.json"),"utf8");
const manifest=JSON.parse(rawManifest);
const start=html.indexOf("// PURE_BEGIN");
const end=html.indexOf("// PURE_END");
assert(start>=0&&end>start,"pure JS functions must be source extractable");
const funcs=vm.runInNewContext(html.slice(start+"// PURE_BEGIN".length,end)+"\n({GLYPHS,ZONES,classifyGap,relationPreview,emptyBuckets,intersticeHint,safeCapsule})",{});
const checks=[];
function test(name,fn){
  try{fn();checks.push({name,status:"PASS"});}
  catch(e){checks.push({name,status:"FAIL",reason:e.message});}
}
function eq(a,b){assert.equal(a,b);}
const capsule=(zone="writing",glyph="next",stats=null,opt=false)=>funcs.safeCapsule(zone,glyph,stats,opt);
test("manifest identity",()=>eq(manifest.schema,"CoAll.CoInputIntersticeGlyph.R0"));
test("correct source work identity",()=>eq(manifest.work_id,"conod-cothumb:interstice:r0:demo"));
test("no effect authority",()=>eq(manifest.authority,"NONE"));
test("disarmed default",()=>eq(manifest.default,"DISARMED"));
test("finite event budget",()=>eq(manifest.max_keystroke_events_per_arm,32));
test("finite wall-clock window",()=>eq(manifest.max_observation_seconds,15));
test("zero materialized workers",()=>eq(manifest.max_active_workers,0));
test("no network",()=>eq(manifest.network_calls,0));
test("exact four donor references",()=>eq(manifest.source_donors.length,4));
test("unique donor paths",()=>eq(new Set(manifest.source_donors.map(d=>d.path)).size,4));
test("all donor blob values SHA1-shaped",()=>assert(manifest.source_donors.every(x=>/^[0-9a-f]{40}$/.test(x.git_blob))));
test("all contexts mirrored in page",()=>assert(manifest.contexts.every(z=>html.includes('data-zone="'+z+'"'))));
test("all glyphs mirrored in page",()=>assert(Object.keys(manifest.glyphs).every(z=>html.includes('data-glyph="'+z+'"'))));
test("all glyph meanings and IDs match",()=>assert(Object.entries(manifest.glyphs).every(([k,v])=>funcs.GLYPHS[k].glyph===v)));
test("glyphs are distinct",()=>eq(new Set(Object.values(manifest.glyphs)).size,8));
test("valid next glyph",()=>eq(funcs.GLYPHS.next.name,"Next step"));
test("negation is not automatic truth",()=>assert.match(funcs.GLYPHS.negate.boundary,/Not observed does not mean logically false/));
test("open logical infinity does not imply infinite workers",()=>assert.match(funcs.GLYPHS.unbounded.boundary,/not infinite workers or tokens/));
test("comparison needs units",()=>assert.match(funcs.GLYPHS.compare.boundary,/units/));
test("no derived hint without a pause",()=>eq(funcs.intersticeHint("writing",{PAUSE:0}),""));
test("derived pause only for opted-in writing scope",()=>eq(funcs.intersticeHint("media",{PAUSE:3}),""));
test("derived pause can suggest one prior",()=>assert.match(funcs.intersticeHint("writing",{PAUSE:1}),/Optional: inspect a prior/));
test("derived pause cannot assume intent",()=>assert.match(funcs.intersticeHint("writing",{PAUSE:1}),/not a statement of intent/));
test("short interval at 0",()=>eq(funcs.classifyGap(0),"SHORT"));
test("short threshold",()=>eq(funcs.classifyGap(179),"SHORT"));
test("flow threshold",()=>eq(funcs.classifyGap(180),"FLOW"));
test("pause threshold",()=>eq(funcs.classifyGap(850),"PAUSE"));
test("longest bounded pause",()=>eq(funcs.classifyGap(5000),"PAUSE"));
test("out of sample gap ignored",()=>eq(funcs.classifyGap(5001),"OUT_OF_WINDOW"));
test("negative gap rejected",()=>eq(funcs.classifyGap(-1),"UNKNOWN"));
test("non number rejected",()=>eq(funcs.classifyGap("hello"),"UNKNOWN"));
test("NaN rejected",()=>eq(funcs.classifyGap(NaN),"UNKNOWN"));
test("infinite gap rejected",()=>eq(funcs.classifyGap(Infinity),"UNKNOWN"));
test("writing candidate shadow",()=>eq(funcs.relationPreview("writing","next").state,"PROPOSED_ONLY"));
test("media candidate requires selection",()=>assert.match(funcs.relationPreview("media","candidate").detail,/User-selected file/));
test("device candidate requires actual telemetry",()=>assert.match(funcs.relationPreview("device","inverse").detail,/Actual device telemetry/));
test("sensitive app held",()=>eq(funcs.relationPreview("sensitive","next").state,"HELD_SENSITIVE"));
test("unknown app held",()=>eq(funcs.relationPreview("unknown","next").state,"HELD_UNKNOWN_CONTEXT"));
test("invalid app held",()=>eq(funcs.relationPreview("money","next").state,"HELD_UNKNOWN_CONTEXT"));
test("invalid glyph held",()=>eq(funcs.relationPreview("writing","authority").state,"HELD_UNKNOWN_SYMBOL"));
test("capsule has zero effects",()=>eq(capsule().outward_effects,0));
test("capsule has zero executed tasks",()=>eq(capsule().executed_tasks,0));
test("capsule has no receiver ack",()=>eq(capsule().receiver_ack,false));
test("capsule not actual device observation",()=>eq(capsule().exact_device_event,false));
test("capsule includes neither text nor raw keys",()=>assert(capsule().raw_text_included===false&&capsule().raw_keys_included===false));
test("capsule explicit authority NONE",()=>eq(capsule().authority,"NONE"));
test("capsule no exact timing by default",()=>assert(!Object.hasOwn(capsule(),"coarse_intervals")));
test("capsule counters optional",()=>eq(capsule("writing","next",{SHORT:2,FLOW:1,PAUSE:1},true).coarse_intervals.FLOW,1));
test("capsule bounded counter",()=>eq(capsule("writing","next",{SHORT:999,FLOW:0,PAUSE:0},true).coarse_intervals.SHORT,32));
test("capsule negative count clamped",()=>eq(capsule("writing","next",{SHORT:-3,FLOW:0,PAUSE:0},true).coarse_intervals.SHORT,0));
test("blocked context creates no actionable capsule",()=>assert(capsule("sensitive","next").authorized===false));
test("strict no-network CSP",()=>assert(html.includes("connect-src 'none'")));
test("strict no-form CSP",()=>assert(html.includes("form-action 'none'")));
test("no remote API in source",()=>assert(!/\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon|EventSource|\bimport\s*\(/.test(html)));
test("no global key hooks",()=>assert(!/\bwindow\.addEventListener\s*\(\s*['\"]key|\bdocument\.addEventListener\s*\(\s*['\"]key/.test(html)));
test("no key identity inspection",()=>assert(!/\be\.key\b|\bevent\.key\b/.test(html)));
test("no storage APIs",()=>assert(!/localStorage|sessionStorage|indexedDB|serviceWorker|document\.cookie/.test(html)));
test("no clipboard automation",()=>assert(!/navigator\.clipboard|document\.execCommand/.test(html)));
test("no global pointer or window content capture",()=>assert(!/\bscreen\.capture|desktopCapture|window\.getDisplayMedia|navigator\.mediaDevices|\bgetUserMedia\b/.test(html)));
test("local editor only event",()=>assert(html.includes('field.addEventListener("keydown"')));
test("keys are bounded",()=>assert(html.includes('events>=32')&&html.includes('events===32')));
test("timer stops",()=>assert(html.includes('setTimeout(()=>disarm(')));
test("clear erases source sample",()=>assert(html.includes('field.value=""')));
test("download explicit only",()=>assert(html.includes('document.getElementById("download").addEventListener("click"')));
test("download state held gate",()=>assert(html.includes('prepared.state!=="PROPOSED_ONLY"')));
test("reduced motion support",()=>assert(html.includes("prefers-reduced-motion")));
test("keyboard focus visible",()=>assert(html.includes(":focus-visible")));
test("plain text meaning with glyphs",()=>assert(html.includes('id="glyphMeaning"')&&html.includes('aria-label="Glyph meanings"')));
test("no network effect even from 6 contexts",()=>assert(manifest.contexts.every(z=>funcs.relationPreview(z,"next").allowed?capsule(z,"next").outward_effects===0:true)));
const pass=checks.filter(x=>x.status==="PASS").length;
const report={schema:"CoAll.CoInputInterstice.SmokeR0",observed_at:new Date().toISOString(),status:pass===checks.length?"PASS":"FAIL",
  passed:pass,failed:checks.length-pass,total:checks.length,
  html_sha256:crypto.createHash("sha256").update(html).digest("hex"),manifest_sha256:crypto.createHash("sha256").update(rawManifest).digest("hex"),
  checks,scope:"NODE22_PURE_LOGIC_AND_STATIC_SOURCE_ONLY",authority:"NONE",
  nonclaims:["STATIC_CHECK_NE_BROWSER_ACCEPTANCE","NO_X2_GESTURE","NO_NATIVE_INPUT_RUNTIME","NO_HUMAN_FIRST_USE","NO_RECEIVER_ACK","NO_HARDWARE_CAPTURE"]};
const outputAt=process.argv.indexOf("--output");
if(outputAt>=0){const output=process.argv[outputAt+1];if(!output)throw Error("Missing output path");fs.writeFileSync(output,JSON.stringify(report,null,2)+"\n",{flag:"wx"});}
console.log(JSON.stringify({status:report.status,passed:pass,failed:report.failed,total:report.total,html_sha256:report.html_sha256,manifest_sha256:report.manifest_sha256}));
if(report.failed){for(const fail of checks.filter(x=>x.status==="FAIL"))console.error(fail.name+": "+fail.reason);process.exitCode=2;}
