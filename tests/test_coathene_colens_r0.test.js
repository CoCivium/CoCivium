"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");

const root=path.resolve(__dirname,"..");
const html=fs.readFileSync(path.join(root,"examples","coathene_copet_r0","index.html"),"utf8");
const canonical=JSON.parse(fs.readFileSync(path.join(root,"examples","coathene_copet_r0","learning_map.json"),"utf8"));
const raw=html.match(/<script id="copet-data" type="application\/json">([\s\S]*?)<\/script>/);
const js=html.match(/<script id="copet-engine">([\s\S]*?)<\/script>/);
assert.ok(raw&&js,"Exact CoLens inline source and working script");
const stub={document:{getElementById(id){
 if(id==="copet-data")return{textContent:raw[1]};throw Error("Unexpected DOM access "+id);
}},module:{exports:{}},console};
vm.runInNewContext(js[1],stub,{filename:"copet/index.html"});
const {lib,lensMode,lensFocus,lensScene,lensPresentation,findLesson,newVisit,viewCoverage}=stub.module.exports;
const copy=x=>JSON.parse(JSON.stringify(x));

test("CoLens source is an exact twin of current typed contract",()=>{
 assert.equal(canonical.lens.schema,"CoAthene.CoLensPresentation.R0-candidate");
 assert.deepEqual(copy(lib.lens),canonical.lens);
});
test("four manual presentation modes and focus intents exist",()=>{
 assert.deepEqual(canonical.lens.modes.map(x=>x.id),
  ["together","play","explore","research"]);
 assert.deepEqual(canonical.lens.focuses.map(x=>x.id),
  ["wonder","make","explain","challenge"]);
 assert.deepEqual(canonical.lens.scenes.map(x=>x.id),
  ["river","space","animals","games"]);
});
test("the 64 explicit scene/lens/focus combinations yield useful safe prompts",()=>{
 let count=0;
 for(const mode of canonical.lens.modes)
 for(const focus of canonical.lens.focuses)
 for(const scene of canonical.lens.scenes){
  const p=lensPresentation(mode.id,focus.id,scene.id);
  assert.equal(p.modeId,mode.id);
  assert.equal(p.focusId,focus.id);
  assert.equal(p.sceneId,scene.id);
  assert.equal(p.visual,scene.art);
  assert.ok(p.activity.length>15);
  assert.ok(p.offscreen.length>20);
  assert.equal(p.inputAgeCollected,false);
  assert.equal(p.ageInferred,false);
  assert.equal(p.masteryAssigned,false);
  assert.equal(p.stored,false);
  count++;
 }
 assert.equal(count,64);
});
test("Together age-one guidance is adult prompt, no screen quiz",()=>{
 const p=lensPresentation("together","wonder","river");
 assert.equal(p.requiresAdult,true);
 assert.equal(p.playOptions.length,0);
 assert.equal(p.correct,null);
 assert.match(p.disclosure,/one-year-old/i);
 assert.match(p.disclosure,/no sedentary screen time/i);
 assert.match(p.childPrompt,/point to water/i);
});
test("Together contains meaningful physical off-screen activity in every topic",()=>{
 for(const scene of canonical.lens.scenes){
  const p=lensPresentation("together","make",scene.id);
  assert.match(p.offscreen,/Screen away:/);
  assert.ok(p.activity.length>15);
  assert.ok(p.disclosure.length>65);
  assert.equal(p.playOptions.length,0);
 }
});
test("Play mode has two brief responses, not a grade",()=>{
 for(const scene of canonical.lens.scenes){
  const p=lensPresentation("play","explain",scene.id);
  assert.equal(p.playOptions.length,2);
  assert.ok(p.playOptions.every(x=>x.length<28));
  assert.ok([0,1].includes(p.correct));
  assert.ok(p.feedback.length>=20);
  assert.equal(p.masteryAssigned,false);
  assert.equal(p.requiresAdult,true);
 }
});
test("Explore and Investigate do not change the underlying science claims",()=>{
 for(const scene of canonical.lens.scenes){
  const original=findLesson(scene.id);
  const explore=lensPresentation("explore","challenge",scene.id);
  const deep=lensPresentation("research","challenge",scene.id);
  assert.equal(explore.sceneId,deep.sceneId);
  assert.equal(explore.visual,deep.visual);
  assert.equal(explore.playOptions.length,0);
  assert.equal(deep.playOptions.length,0);
  assert.ok(original.claims.length===3&&original.evidence.length===3);
  assert.ok(original.why.length>50&&original.boundary.length>45);
  assert.ok(original.source.startsWith("https://"));
 }
});
test("4 focus intentions do not result in permanent interest or ability labels",()=>{
 const intentions=new Set();
 for(const focus of canonical.lens.focuses){
  const p=lensPresentation("play",focus.id,"animals");
  intentions.add(p.activity);
  assert.equal(p.ageInferred,false);
 }
 assert.equal(intentions.size,4);
 assert.equal(canonical.lens.policy.selection,"EXPLICIT_CHOICE_ONLY_NO_DETECTION");
 assert.equal(canonical.lens.policy.childData,"NONE_NO_DATE_OF_BIRTH_NO_PROFILE");
});
test("mode change alone does not mutate any visit or assign mastery",()=>{
 const v=newVisit();
 const old=copy(v);
 for(const mode of canonical.lens.modes)lensPresentation(mode.id,"wonder","river");
 assert.deepEqual(copy(v),old);
 assert.equal(viewCoverage(v).questionsExplored,0);
});
test("wrong or absent scene/mode/focus is rejected, not guessed",()=>{
 assert.throws(()=>lensMode("automatic_age_1"),/Unknown presentation lens/);
 assert.throws(()=>lensFocus("diagnosed_gifted"),/Unknown learning focus/);
 assert.throws(()=>lensScene("real_child_identity"),/Unrecognized lesson illustration/);
 assert.throws(()=>lensPresentation("together","make","does_not_exist"),/Unrecognized/);
});
test("four original inline SVG pictures have textual alternatives",()=>{
 assert.equal((html.match(/id="lens-art-(?:river|space|animals|games)"/g)||[]).length,4);
 assert.equal((html.match(/viewBox="0 0 320 230" role="img" aria-label=/g)||[]).length,4);
 assert.ok(canonical.lens.scenes.every(x=>x.art.startsWith("original_vector_")));
 assert.match(html,/lens-picture svg\[hidden\]/);
});
test("mode buttons are large, semantic and explicitly controllable",()=>{
 assert.equal((html.match(/data-lens-mode="/g)||[]).length,4);
 assert.match(html,/role="group" aria-label="Presentation mode, not an age test"/);
 assert.match(html,/aria-pressed="true"/);
 assert.match(html,/id="lens-switch"/);
 assert.match(html,/id="lens-knob"/);
 assert.match(html,/:focus-visible/);
});
test("stage has a visible offscreen stop and returns to an adult's dial",()=>{
 assert.match(html,/id="lens-finish"/);
 assert.match(html,/id="lens-done"/);
 assert.match(html,/id="lens-reopen"/);
 assert.match(html,/visit=newVisit\(\);outfit=newOutfit\(\);renderProgress\(\);renderOutfit\(\)/);
 assert.match(html,/by\("lens-stage"\).scrollIntoView/);
});
test("Research retains original references, limitations and privacy disclaimers",()=>{
 assert.match(html,/id="lens-research-source"/);
 assert.match(html,/id="lens-research-limit"/);
 assert.match(html,/lesson.boundary/);
 assert.match(html,/No independent educational effect/);
 assert.equal(canonical.lens.effectBoundary.realChildrenObserved,0);
 assert.equal(canonical.lens.effectBoundary.guardianAccessValidated,0);
});
test("no tracking, autoaudio, camera, age inputs, external image or hidden sync",()=>{
 assert.equal(canonical.lens.policy.sharedPlay,"NO_AUTO_AUDIO_NO_CAMERA_NO_MIC_NO_CHAT");
 assert.equal(canonical.lens.policy.persistence,"NONE_RESETS_ON_PAGE_REFRESH");
 for(const bad of ["localStorage","sessionStorage","indexedDB","fetch(","XMLHttpRequest",
   "WebSocket(","speechSynthesis.speak","navigator.mediaDevices",
   "navigator.geolocation","document.cookie",'<img','<iframe','name="birthdate"']){
  assert.equal(html.includes(bad),false,bad+" not expected");
 }
 assert.match(html,/connect-src 'none'/);
});
test("public prior art is present and does not imply endorsement",()=>{
 const src=canonical.lens.externalSources.map(x=>x.url).join(" ");
 assert.match(src,/who.int/);
 assert.match(src,/naeyc.org/);
 assert.match(src,/aap.org/);
 assert.equal(canonical.lens.policy.legalSchool,"PRESENTATION_LENS_NE_LICENSED_SCHOOL_OR_CHILD_CARE");
});
test("single learner question and no duplicated live version stacks",()=>{
 assert.equal((html.match(/<main\b/g)||[]).length,1);
 assert.equal((html.match(/<h1\b/g)||[]).length,1);
 assert.match(html,/body\[data-lens="together"\] \.layout/);
 assert.match(html,/body\[data-lens="play"\] \.layout/);
 assert.match(html,/body\[data-lens="research"\] \.lens-research/);
});
