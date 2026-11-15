"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");

const base=path.resolve(__dirname,"..","examples","coathene_copet_r0");
const html=fs.readFileSync(path.join(base,"index.html"),"utf8");
const doc=JSON.parse(fs.readFileSync(path.join(base,"learning_map.json"),"utf8"));
const dataTag=html.match(/<script id="copet-data" type="application\/json">([\s\S]*?)<\/script>/);
const engineTag=html.match(/<script id="copet-engine">([\s\S]*?)<\/script>/);
assert.ok(dataTag,"literal source twin");
assert.ok(engineTag,"literal CoPet engine");
const state={
 document:{getElementById(id){
  if(id==="copet-data")return{textContent:dataTag[1]};
  throw Error("Unexpected real UI dependency in pure engine: "+id);
 }},
 module:{exports:{}},console
};
vm.runInNewContext(engineTag[1],state,{filename:"copet/index.html"});
const {lib,findLesson,newVisit,teach,viewCoverage}=state.module.exports;
const clone=x=>JSON.parse(JSON.stringify(x));

test("browser source is exactly the public JSON lesson twin",()=>{
 const embedded=JSON.parse(dataTag[1]);
 for(const key of ["schema","experience","coPathViews","petLessons"]){
  assert.deepEqual(embedded[key],doc[key],key+" on source file");
  assert.deepEqual(clone(lib[key]),doc[key],key+" in actual engine");
 }
});
test("zero-auth guest visit has zero score and zero progress at start",()=>{
 const state=newVisit();
 assert.deepEqual(clone(state),{explored:[],last:null});
 assert.deepEqual(clone(viewCoverage(state)),
 {questionsExplored:0,totalQuestions:4,topicsEncountered:[],masteryClaim:"NONE",persisted:false});
});
test("every interest supports correct learning and sourced counterexample",()=>{
 for(const q of doc.petLessons){
  const receipt=teach(newVisit(),q.id,q.claimCorrect,q.evidenceCorrect);
  assert.equal(receipt.last.claimSupported,true);
  assert.equal(receipt.last.evidenceSupported,true);
  assert.equal(receipt.last.id,q.id);
  assert.ok(receipt.last.explanation.length>50);
  assert.ok(receipt.last.boundary.length>40);
  assert.ok(receipt.last.source.startsWith("https://"));
  assert.equal(receipt.actualMasteryVerified,false);
  assert.equal(receipt.actualGuardianVerified,false);
  assert.equal(receipt.hasLearnerIdentity,false);
 }
});
test("wrong claims still get scientific correction and exploration",()=>{
 for(const q of doc.petLessons){
  const c=(q.claimCorrect+1)%q.claims.length;
  const e=(q.evidenceCorrect+1)%q.evidence.length;
  const r=teach(newVisit(),q.id,c,e);
  assert.equal(r.last.claimSupported,false);
  assert.equal(r.last.evidenceSupported,false);
  assert.deepEqual(clone(r.explored),[q.id]);
  assert.equal(r.actualMasteryVerified,false);
 }
});
test("learning map records topics encountered, never mastery",()=>{
 let s=newVisit();
 for(const q of doc.petLessons)s=teach(s,q.id,q.claimCorrect,q.evidenceCorrect);
 const seen=viewCoverage(s);
 assert.equal(seen.questionsExplored,4);
 assert.equal(seen.totalQuestions,4);
 assert.deepEqual([...seen.topicsEncountered].sort(),
 doc.coPathViews.map(x=>x.id).sort());
 assert.equal(seen.masteryClaim,"NONE");
 assert.equal(seen.persisted,false);
});
test("repetition does not inflate exploration counts or create user profile",()=>{
 const l=doc.petLessons[0];
 const once=teach(newVisit(),l.id,l.claimCorrect,l.evidenceCorrect);
 const twice=teach(once,l.id,0,0);
 assert.equal(viewCoverage(twice).questionsExplored,1);
 assert.equal(twice.hasLearnerIdentity,false);
 assert.equal(twice.storedOnDevice,false);
 assert.equal(twice.sentToServer,false);
});
test("different guest visits do not share progress",()=>{
 const l=doc.petLessons[0];
 const first=teach(newVisit(),l.id,0,0);
 const other=newVisit();
 assert.equal(first.explored.length,1);
 assert.equal(other.explored.length,0);
 assert.equal(viewCoverage(other).questionsExplored,0);
});
test("unknown interest and invalid answer indexes fail closed",()=>{
 assert.throws(()=>findLesson("unlisted_pet_track"),/Unknown interest/);
 const q=doc.petLessons[0];
 for(const x of [-1,3,100,1.5,"1",NaN]){
  assert.throws(()=>teach(newVisit(),q.id,x,0),/Select one idea/);
  assert.throws(()=>teach(newVisit(),q.id,0,x),/Select one idea/);
 }
 assert.throws(()=>teach({explored:"synthetic_bad"},q.id,0,0),/Invalid local visit/);
});
test("no status implies an authenticated or verified child",()=>{
 const q=doc.petLessons[0];
 const state=teach(newVisit(),q.id,0,0);
 assert.equal(state.hasLearnerIdentity,false);
 assert.equal(state.storedOnDevice,false);
 assert.equal(state.sentToServer,false);
 assert.equal(state.actualGuardianVerified,false);
 assert.equal(state.actualMasteryVerified,false);
 assert.equal(doc.proxy_and_identity.active_proxy,"GENERIC_FICTIONAL_PET_NOT_CHILD_PROXY_IDENTITY");
});
test("no hidden storage, tracking, biometrics, network, or private-chat model",()=>{
 for(const bad of ["localStorage","sessionStorage","indexedDB","document.cookie",
                   "fetch(","XMLHttpRequest","WebSocket(","navigator.geolocation",
                   "navigator.mediaDevices","navigator.sendBeacon","<iframe","<img"]){
  assert.ok(!html.includes(bad),"unexpected "+bad);
 }
 assert.match(html,/connect-src 'none'/);
 assert.match(html,/form-action 'none'/);
 assert.match(html,/No child identity collected/);
 assert.match(html,/No stored answers/);
});
test("one primary screen, explicit reset and accessible options",()=>{
 assert.equal((html.match(/<main\b/g)||[]).length,1);
 assert.equal((html.match(/<h1\b/g)||[]).length,1);
 assert.match(html,/id="results" hidden/);
 assert.match(html,/by\("clear"\).addEventListener\("click",resetAll\)/);
 assert.match(html,/by\("clear-result"\).addEventListener\("click",resetAll\)/);
 assert.match(html,/aria-live="polite"/);
 assert.match(html,/prefers-reduced-motion/);
 assert.match(html,/:focus-visible/);
});
test("pet is declared fiction and not a child identity or guardian",()=>{
 assert.equal(doc.experience.teachable_agent_mode,
 "FICTIONAL_CHARACTER_ASKS_CHILD_TO_CORRECT_A_KNOWN_MISCONCEPTION");
 assert.equal(doc.experience.model_training,"NONE");
 assert.equal(doc.experience.actual_AI,"NONE");
 assert.equal(doc.proxy_and_identity.active_proxy,"GENERIC_FICTIONAL_PET_NOT_CHILD_PROXY_IDENTITY");
 assert.equal(doc.synth_review_future.status,"NOT_IMPLEMENTED");
 assert.equal(doc.synth_review_future.human_override,
 "HUMAN_EDUCATOR_OR_GUARDIAN_RETAIN_RELEVANT_SUPERVISION_AND_APPEAL");
 assert.match(html,/not a real person, teacher or guardian/);
});
test("optional CoPassport is explicitly unbuilt, not falsely secured",()=>{
 assert.match(html,/has <strong>not<\/strong> been built/);
 assert.match(html,/progress this visit/i);
 assert.match(html,/CoPassport\+/);
 assert.equal(doc.proxy_and_identity.sync_across_devices,"NOT_PRESENT");
 assert.equal(doc.experience.session_scope,"VOLATILE_BROWSER_MEMORY_ONLY_NEVER_SAVED");
});
