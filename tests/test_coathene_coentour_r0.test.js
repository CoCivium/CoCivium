"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const base=path.resolve(__dirname,"..","examples","coathene_copet_r0");
const html=fs.readFileSync(path.join(base,"index.html"),"utf8");
const canonical=JSON.parse(fs.readFileSync(path.join(base,"learning_map.json"),"utf8"));
const raw=html.match(/<script id="copet-data" type="application\/json">([\s\S]*?)<\/script>/);
const script=html.match(/<script id="copet-engine">([\s\S]*?)<\/script>/);
assert.ok(raw&&script,"Exact embedded CoEntour source and engine");
const bindings={document:{getElementById(id){if(id==="copet-data")return {textContent:raw[1]};throw Error("Unexpected UI reference "+id);}},module:{exports:{}},console};
vm.runInNewContext(script[1],bindings,{filename:"copet/index.html"});
const {lib,newOutfit,getGearType,selectGear,gearCue,visitTrail,teach,newVisit,viewCoverage}=bindings.module.exports;
const flat=canonical.entourage.item_types.flatMap(t=>t.items);
const copy=x=>JSON.parse(JSON.stringify(x));

test("source twin contains exact 16 CoEntour items and policy",()=>{
 assert.equal(canonical.entourage.displayName,"CoEntour+");
 assert.deepEqual(copy(lib.entourage),canonical.entourage);
 assert.equal(canonical.entourage.item_types.length,4);
 assert.equal(flat.length,16);
 assert.equal(new Set(flat.map(x=>x.id)).size,16);
});
test("each accessory is voluntary and available from first visit",()=>{
 assert.equal(canonical.entourage.choice_mode,"ALL_ITEMS_AVAILABLE_FROM_START_NO_EARNING_GATE_NO_MONEY");
 const first=newOutfit();
 for(const type of canonical.entourage.item_types)for(const item of type.items){
  const v=selectGear(first,type.id,item.id);
  assert.equal(v.claimed.length,1);
  assert.equal(v.lastChoice.routeLessonId,item.routeLessonId);
  assert.equal(v.verifiedCredential,false);
  assert.equal(v.learnerIdentity,false);
  assert.equal(v.stored,false);
  assert.equal(v.broadcast,false);
 }
});
test("claiming an accessory does not automatically complete or teach a lesson",()=>{
 const v=newVisit();const old=copy(v);
 const o=selectGear(newOutfit(),"familiar","familiar_space");
 const c=gearCue(o);
 assert.equal(c.routeLessonId,"space");
 assert.equal(c.automatic,false);
 assert.equal(c.verified,false);
 assert.deepEqual(copy(v),old);
 assert.equal(viewCoverage(v).questionsExplored,0);
});
test("different hats can suggest different questions without assigning fixed ability",()=>{
 const outfit=selectGear(newOutfit(),"hat","hat_river");
 const hint=gearCue(outfit);
 assert.equal(hint.routeLessonId,"river");
 assert.equal(hint.claimedByChoiceOnly,true);
 assert.match(hint.question, /rainwater/i);
 assert.equal(canonical.entourage.current_level,"NONE_NO_SCALAR_LEARNER_RANK");
});
test("16 route hints all point to recognized current lessons",()=>{
 const ids=new Set(canonical.petLessons.map(x=>x.id));
 for(const type of canonical.entourage.item_types)for(const item of type.items){
  assert.ok(ids.has(item.routeLessonId),item.id);
  assert.equal(item.levelClaim,"NONE");
  assert.equal(item.accessRights,"NONE");
  assert.equal(item.immutableIdentity,"NONE");
  const route=gearCue(selectGear(newOutfit(),type.id,item.id));
  assert.equal(route.routeLessonId,item.routeLessonId);
 }
});
test("four cosmetic categories may coexist in a single voluntary entourage",()=>{
 let outfit=newOutfit();
 for(const type of canonical.entourage.item_types){
  outfit=selectGear(outfit,type.id,type.items[1].id);
 }
 assert.equal(outfit.claimed.length,4);
 assert.equal(Object.keys(outfit.equipped).length,4);
 assert.equal(gearCue(outfit).routeLessonId,"space");
 assert.equal(outfit.broadcast,false);
});
test("replacing same accessory category changes look, not earned record",()=>{
 let outfit=selectGear(newOutfit(),"hat","hat_river");
 outfit=selectGear(outfit,"hat","hat_games");
 assert.equal(outfit.equipped.hat,"hat_games");
 assert.equal(gearCue(outfit).routeLessonId,"games");
 assert.equal(outfit.verifiedCredential,false);
 assert.equal(outfit.learnerIdentity,false);
});
test("new visit and outfit are both entirely empty and local",()=>{
 assert.deepEqual(copy(newOutfit()),{equipped:{},claimed:[],lastChoice:null});
 assert.deepEqual(copy(newVisit()),{explored:[],last:null});
 const empty=gearCue(newOutfit());
 assert.equal(empty.routeLessonId,null);
 assert.equal(empty.automatic,false);
});
test("invalid accessory, counterfeit item or malformed outfit fails closed",()=>{
 assert.throws(()=>getGearType("biometric_identifier"),/Unknown accessory type/);
 assert.throws(()=>selectGear(newOutfit(),"hat","badge_games"),/Unknown costume/);
 assert.throws(()=>selectGear(null,"hat","hat_river"),/Invalid local outfit/);
 assert.throws(()=>selectGear({equipped:{},claimed:"not_array"},"hat","hat_river"),/Invalid local outfit/);
});
test("real exploration creates only a nonpersistent visited-topic marker",()=>{
 const q=canonical.petLessons[0];
 const before=visitTrail(newVisit());
 const after=teach(newVisit(),q.id,q.claimCorrect,q.evidenceCorrect);
 const trail=visitTrail(after);
 assert.equal(before.length,0);
 assert.equal(trail.length,1);
 assert.equal(trail[0].lessonId,q.id);
 assert.equal(trail[0].grade,null);
 assert.equal(trail[0].verified,false);
 assert.equal(trail[0].notPersistent,true);
 assert.equal(after.actualMasteryVerified,false);
});
test("wardrobe UI contains explicit claim and separate opt-in route action",()=>{
 assert.match(html,/id="wardrobe"/);
 assert.match(html,/id="gear-claim"/);
 assert.match(html,/id="gear-follow"[^>]*disabled/);
 assert.match(html,/id="gear-clear"/);
 assert.match(html,/by\("gear-claim"\).addEventListener\("click",claimGear\)/);
 assert.match(html,/by\("gear-follow"\).addEventListener\("click",followGear\)/);
 assert.match(html,/sel.value=cue.routeLessonId;renderLesson\(\)/);
 assert.match(html,/No route chosen/);
});
test("reset erases cosmetic state and transient exploration",()=>{
 assert.match(html,/function resetAll\(\)\{visit=newVisit\(\);outfit=newOutfit\(\)/);
 assert.match(html,/by\("gear-clear"\).addEventListener/);
 assert.match(html,/session_scope/);
 assert.equal(canonical.experience.session_scope,"VOLATILE_BROWSER_MEMORY_ONLY_NEVER_SAVED");
});
test("no child ability, ranking, identification or credential is exposed",()=>{
 const flat=canonical.entourage.item_types.flatMap(t=>t.items);
 assert.ok(flat.every(item=>item.claimClass==="COSMETIC_SELF_SELECTED_UNVERIFIED"));
 assert.ok(flat.every(item=>item.levelClaim==="NONE"));
 assert.equal(canonical.entourage.future_credential_candidate.state,"NOT_IMPLEMENTED");
 assert.equal(canonical.entourage.visibility_default,"LOCAL_ONLY_NO_BROADCAST_NO_ONLINE_PROFILE");
 for(const bad of ["localStorage","sessionStorage","indexedDB","fetch(","WebSocket(","XMLHttpRequest","document.cookie","navigator.mediaDevices","navigator.geolocation","<iframe","<img"]){
  assert.equal(html.includes(bad),false,bad);
 }
});
test("one front and no automatic tracking or remote badge issuer",()=>{
 assert.equal((html.match(/<main\b/g)||[]).length,1);
 assert.equal((html.match(/<h1\b/g)||[]).length,1);
 assert.match(html,/connect-src 'none'/);
 assert.match(html,/form-action 'none'/);
 assert.equal(canonical.entourage.future_credential_candidate.state,"NOT_IMPLEMENTED");
 assert.ok(canonical.entourage.nonclaims.includes("COENTOUR_CHOICE_NE_TRUSTED_CHILD_PROFILE"));
});
