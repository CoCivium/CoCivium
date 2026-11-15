"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");

const home=path.resolve(__dirname,"..","examples","coathene_anywhere_r0");
const html=fs.readFileSync(path.join(home,"index.html"),"utf8");
const full=JSON.parse(fs.readFileSync(path.join(home,"recipe.json"),"utf8"));
const jsonMatch=html.match(/<script id="coathene-recipe" type="application\/json">([\s\S]*?)<\/script>/);
const jsMatch=html.match(/<script id="coathene-planner">([\s\S]*?)<\/script>/);
assert.ok(jsonMatch,"embedded source twin");
assert.ok(jsMatch,"planner JS");
const publicRecipe=JSON.parse(jsonMatch[1]);
const harness={document:{getElementById(id){
    if(id==="coathene-recipe")return{textContent:jsonMatch[1]};
    throw Error("unexpected DOM input requested in source-only test");
}},module:{exports:{}},console};
vm.runInNewContext(jsMatch[1],harness,{filename:"index.html:inline-planner"});
const {buildPlan,describePlan,recipe}=harness.module.exports;
const fresh=x=>JSON.parse(JSON.stringify(x));
const choose=(mode="solo",question="runoff",place="anywhere",audience="adult",participants="4")=>({mode,question,place,audience,participants});

test("source twin is exactly the selected R0 recipe schema and fields",()=>{
  assert.equal(publicRecipe.schema,full.schema);
  for(const field of ["modes","placeOptions","audiences","groupRoles","scenarios"]){
    assert.deepEqual(publicRecipe[field],full[field],field);
    assert.deepEqual(fresh(recipe[field]),full[field],field+" actual script");
  }
});
test("every mode x question x place x audience creates a bounded plan",()=>{
 let n=0;
 for(const q of full.scenarios)for(const m of full.modes)
 for(const place of full.placeOptions)for(const audience of full.audiences){
   const p=buildPlan(choose(m.id,q.id,place.id,audience.id));
   assert.equal(p.lesson.id,q.id);
   assert.equal(p.mode.id,m.id);
   assert.equal(p.place.id,place.id);
   assert.equal(p.audience.id,audience.id);
   assert.ok(p.lesson.knowledge.length>=60);
   assert.ok(p.lesson.challenge.length>=60);
   assert.ok(p.lesson.activity.length>=60);
   assert.ok(p.lesson.transfer.length>=60);
   assert.ok(p.conditions.length>0);
   assert.ok(p.roles.length===(m.id==="group"?4:0));
   assert.ok(!("student" in p));
   assert.ok(!("storage" in p));
   n++;
 }
 assert.equal(n,120);
});
test("Groupbuild 2 through 6 produces only local anonymous seat labels",()=>{
 for(let n=2;n<=6;n++){
  const plan=buildPlan(choose("group","commons","offline","adult",String(n)));
  assert.equal(plan.roles.length,n);
  assert.equal(plan.roles[0],"Questioner");
  assert.match(describePlan(plan),/Offline source prototype/);
  assert.match(plan.conditions.join(" "),/participants' consent/);
 }
});
test("bad group counts fail, rather than create a fabricated classroom",()=>{
 for(const participants of ["0","1","7","-1","not-a-number","2.5",""]){
   assert.throws(()=>buildPlan(choose("group","runoff","anywhere","adult",participants)),/Invalid local role count/);
 }
});
test("unknown mode, school, venue, audience or question fails closed",()=>{
 const valid=choose();
 for(const key of ["mode","question","place","audience"]){
   assert.throws(()=>buildPlan({...valid,[key]:"does_not_exist"}),/Unknown/);
 }
});
test("youth requires real adult supervision text, not a fake checkbox",()=>{
 const p=buildPlan(choose("solo","runoff","anywhere","youth"));
 assert.match(p.conditions.join(" "),/responsible real adult must supervise/);
 assert.match(p.conditions.join(" "),/does not verify or provide one/);
 assert.equal(p.roles.length,0);
});
test("mentor and school modes do not book or authenticate institutions",()=>{
 const mentor=buildPlan(choose("mentor"));
 const institution=buildPlan(choose("institution"));
 assert.match(mentor.conditions.join(" "),/No mentor is booked/);
 assert.match(institution.conditions.join(" "),/No institution is contacted, approved or accredited/);
 assert.match(institution.conditions.join(" "),/enrolment, credits, attendance/);
});
test("online venue choice does not imply real-time sync or account creation",()=>{
 const p=buildPlan(choose("group","mirror","remote","adult","3"));
 assert.match(p.conditions.join(" "),/no room, messaging, video or collaborative server/);
 assert.equal(full.limits.realTimeSync,"NOT_PRESENT");
 assert.equal(full.limits.learnerAccounts,"NONE");
 assert.equal(full.limits.autoMessaging,"NONE");
});
test("each scenario has exactly one valid proposed prediction and a robust non-equivalence",()=>{
 for(const q of full.scenarios){
    assert.equal(q.prediction.length,3);
    assert.ok(Number.isInteger(q.correct));
    assert.ok(q.correct>=0 && q.correct<q.prediction.length);
    assert.ok(q.challenge.length>=60);
    assert.ok(q.source.startsWith("https://"));
    assert.ok(q.safety.length>=40);
 }
});
test("one primary screen at a time and no auto network or tracking source",()=>{
 assert.equal((html.match(/<main\b/g)||[]).length,1);
 assert.equal((html.match(/<h1\b/g)||[]).length,1);
 assert.match(html,/<section id="session"[^>]* hidden>/);
 assert.match(html,/setup.hidden=true;session.hidden=false/);
 assert.match(html,/session.hidden=true;setup.hidden=false/);
 for(const unwanted of ["localStorage","sessionStorage","indexedDB","fetch(","XMLHttpRequest","WebSocket(","navigator.sendBeacon","document.cookie","<iframe","<img"]){
   assert.ok(!html.includes(unwanted),unwanted+" not expected");
 }
 assert.match(html,/connect-src 'none'/);
 assert.match(html,/frame-src 'none'/);
 assert.match(html,/form-action 'none'/);
});
test("right to stop, no mandatory login and only explicit external reference clicks",()=>{
 assert.match(html,/No account/);
 assert.match(html,/No network needed/);
 assert.match(html,/No tracking or saved answers/);
 assert.match(html,/Closing or refreshing this page discards/);
 assert.match(html,/target="_blank" rel="noopener noreferrer"/);
 assert.match(html,/prefers-reduced-motion/);
 assert.match(html,/:focus-visible/);
});
test("formatting the plan does not assert actual learning or affiliation",()=>{
 const p=buildPlan(choose("institution","mirror","mixed","youth"));
 const output=describePlan(p);
 assert.match(output,/not a school or a completed lesson/i);
 assert.match(output,/No institution is contacted/);
 assert.match(output,/responsible real adult/);
 assert.match(output,/Source: https:\/\//);
});
test("all audience, location, institution combinations are optional projections",()=>{
 assert.equal(full.audiences.length,2);
 assert.equal(full.placeOptions.length,5);
 assert.equal(full.modes.length,4);
 assert.equal(full.placeOptions.filter(x=>!x.physicalRequired).length,4);
 assert.equal(full.modes.filter(x=>!x.requiresHumanInstitution).length,3);
 assert.ok(full.nonclaims.includes("GROUP_PLAN_NE_PARTICIPANT_CONSENT"));
 assert.ok(full.nonclaims.includes("SOURCE_PR_NE_DEPLOYED_SITE"));
});
