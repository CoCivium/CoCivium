"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"..","index.html"),"utf8");
const m=html.match(/<script type="application\/json" id="resources-data">([\s\S]*?)<\/script>/);
assert(m,"embedded catalog missing");
const resources=JSON.parse(m[1]);
const a=html.indexOf("const isFrontier="),b=html.indexOf("function el(",a);
assert(a>=0 && b>a,"approved pure helper section missing");
const f=vm.runInNewContext(html.slice(a,b)+";({safeCapsule,filteredRecords,isMiddleCopyGesture})",{records:resources});
const tests=[
["six curated entries",()=>assert.equal(resources.length,6)],
["four public entries by default",()=>assert.equal(f.filteredRecords("",false).length,4)],
["two speculative entries only by opt-in",()=>assert.equal(f.filteredRecords("",true).length,6)],
["intent selects onboarding",()=>assert.equal(f.filteredRecords("CoAndrew",false).length,1)],
["broad stretch intent preserves alternative matches",()=>assert(f.filteredRecords("CoStretch",false).length>=2)],
["precise intent selects benchmark",()=>assert.equal(f.filteredRecords("CoStretch benchmark",false).length,1)],
["no automatic effect authority",()=>resources.forEach(r=>assert.equal(f.safeCapsule(r).effect_authority,"NONE"))],
["unknown sources have no locator",()=>resources.filter(r=>r.scope!=="PUBLIC_REFERENCE").forEach(r=>assert.equal(f.safeCapsule(r).public_locator,null))],
["public locators are bounded",()=>resources.filter(r=>r.scope==="PUBLIC_REFERENCE").forEach(r=>assert.match(r.locator,/^https:\/\/github\.com\/CoCivium\//))],
["no private paths or unpublished media identifiers",()=>assert(!/F30B633008F2|MX Master 4|[A-Z]:\\/.test(html))],
["no network fetch or active input hooks",()=>assert(!/\bfetch\s*\(|XMLHttpRequest|WebSocket|addEventListener\(['\"]keydown/.test(html))],
["centred moustache present",()=>assert(html.includes('aria-label="Gold centre moustache"') && html.includes(".hero{grid-template-columns:1fr;text-align:center}"))],
["safe capsule survives JSON roundtrip",()=>{const capsule=f.safeCapsule(resources[0]);assert.deepEqual(JSON.parse(JSON.stringify(capsule)).resource_id,resources[0].id);}],
["explicit middle gesture only",()=>{assert.equal(f.isMiddleCopyGesture({button:1}),true);assert.equal(f.isMiddleCopyGesture({button:0}),false);assert.equal(f.isMiddleCopyGesture({button:2}),false);assert.equal(f.isMiddleCopyGesture(null),false);}],
["middle-click only on safe copy control",()=>{assert(html.includes("copy.addEventListener('auxclick'"));assert(html.includes("copy.addEventListener('mousedown'"));assert(!html.includes("document.addEventListener('auxclick'"));}],
];
const failures=[];
for(const [name,check] of tests){try{check();process.stdout.write("PASS "+name+"\n");}catch(e){failures.push({name,error:e.message});process.stdout.write("FAIL "+name+": "+e.message+"\n");}}
process.stdout.write(JSON.stringify({schema:"CoAttractorPull.PublicSmoke.v0.1",total:tests.length,passed:tests.length-failures.length,failed:failures.length,nonclaims:["TEST_NE_USER_ACCEPTANCE","NO_REMOTE_DISCOVERY","NO_ACTIVE_MODEL_INTEGRATION"]})+"\n");
if(failures.length)process.exitCode=1;
