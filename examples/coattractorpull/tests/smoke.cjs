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
const f=vm.runInNewContext(html.slice(a,b)+";({safeCapsule,filteredRecords,previewCandidate})",{records:resources});
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
["accessible moustache preview trigger",()=>assert(html.includes('id="thumbPreview"') && html.includes('aria-label="EVO ALL BETTERS: preview best matching resource, no copy or send"') && html.includes(".hero{grid-template-columns:1fr;text-align:center}"))],
["preview picks an eligible CoAndrew pointer",()=>assert.equal(f.previewCandidate("CoAndrew",false).id,"public:coandrewfirst:r0")],
["preview cannot reveal speculative resources without opt-in",()=>assert.equal(f.previewCandidate("spirit",false),null)],
["explicit opt-in exposes speculative question, not an executable tool",()=>assert.equal(f.previewCandidate("spirit",true).authority,"NONE")],
["moustache invokes inspect only and never clipboard or sending",()=>assert(html.includes("if(r)selectRecord(r);else query.focus();") && html.includes("copy.addEventListener('click',()=>copySelected())"))],
["no global mouse input hook",()=>assert(!/addEventListener\(['"](auxclick|mousedown|mouseup|pointerdown|pointerup|contextmenu)/.test(html))],
["safe capsule survives JSON roundtrip",()=>{const capsule=f.safeCapsule(resources[0]);assert.deepEqual(JSON.parse(JSON.stringify(capsule)).resource_id,resources[0].id);}]
];
const failures=[];
for(const [name,check] of tests){try{check();process.stdout.write("PASS "+name+"\n");}catch(e){failures.push({name,error:e.message});process.stdout.write("FAIL "+name+": "+e.message+"\n");}}
process.stdout.write(JSON.stringify({schema:"CoAttractorPull.PublicSmoke.v0.1",total:tests.length,passed:tests.length-failures.length,failed:failures.length,nonclaims:["TEST_NE_USER_ACCEPTANCE","NO_REMOTE_DISCOVERY","NO_ACTIVE_MODEL_INTEGRATION"]})+"\n");
if(failures.length)process.exitCode=1;
