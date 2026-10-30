// CoGbx R1 candidate: deterministic DOM-shim interaction checks.
// Not a browser, screen reader, accessibility certification or live X2 UX.
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/i);
assert(script, "one inline script is required");
for (const token of [
  'role="group" aria-label="Projection controls"',
  'role="status" aria-live="polite" aria-atomic="true"',
  'id="undoBtn" disabled',
  'role="status" aria-live="polite"',
  "prefers-reduced-motion",
  "default-src 'none'",
]) assert(html.includes(token), "missing accessible source contract: " + token);

function cl() {
  const s = new Set();
  return {
    toggle(name, on) {
      if (on === undefined ? !s.has(name) : !!on) s.add(name);
      else s.delete(name);
      return s.has(name);
    },
    contains(name) {return s.has(name);},
  };
}
function node(id, options={}) {
  return {
    id, value:options.value||"", textContent:options.text||"",
    dataset:options.dataset||{}, disabled:!!options.disabled,
    classList:cl(), attrs:{}, handlers:{},
    addEventListener(event, fn) { (this.handlers[event]??=[]).push(fn); },
    setAttribute(name, val) { this.attrs[name]=val; },
    click() {for(const fn of this.handlers.click||[]) fn();},
    input() {for(const fn of this.handlers.input||[]) fn();},
  };
}
const ids=["app","field","mapBtn","textBtn","ambientBtn","threeBtn",
  "footerMode","draft","ghost","receipt","focusText","acceptBtn","undoBtn","rejectBtn"];
const nodes=Object.fromEntries(ids.map(id=>[id,node(id)]));
nodes.draft.value="Sample raw input";
nodes.ghost.textContent="Candidate: test a recovery path";
nodes.undoBtn.disabled=true;
const details=["current","source","unknown","next","recover","peer"].map(id=>
  node("node."+id,{dataset:{node:id}}));
const doc={
  getElementById(id) {assert(nodes[id],"missing "+id);return nodes[id];},
  querySelectorAll(q){assert.equal(q,".node");return details;},
};
vm.runInNewContext(script[1],{document:doc,console});
let checks=0;
function test(label, fn){fn();checks++;console.log("PASS "+label);}
test("initial text unchanged",()=>assert.equal(nodes.draft.value,"Sample raw input"));
test("default undo disabled",()=>assert.equal(nodes.undoBtn.disabled,true));
test("select text",()=>{nodes.textBtn.click();assert.equal(nodes.textBtn.attrs["aria-pressed"],"true");assert(nodes.app.classList.contains("textmode"));});
test("return map",()=>{nodes.mapBtn.click();assert(!nodes.app.classList.contains("textmode"));});
test("select ambient",()=>{nodes.ambientBtn.click();assert(nodes.app.classList.contains("ambient"));});
test("map after ambient",()=>{nodes.mapBtn.click();assert(!nodes.app.classList.contains("ambient"));});
test("optional spatial mode",()=>{nodes.threeBtn.click();assert(nodes.field.classList.contains("threed"));nodes.threeBtn.click();assert(!nodes.field.classList.contains("threed"));});
test("focus detail",()=>{details[3].click();assert(nodes.focusText.textContent.includes("Prediction"));});
test("accept exact input once",()=>{nodes.acceptBtn.click();assert.equal(nodes.draft.value,"Sample raw input → compare recovery before materialization");assert.equal(nodes.acceptBtn.disabled,true);});
test("accept opens undo",()=>assert.equal(nodes.undoBtn.disabled,false));
test("undo restores exact RAW",()=>{nodes.undoBtn.click();assert.equal(nodes.draft.value,"Sample raw input");assert.equal(nodes.undoBtn.disabled,true);assert.equal(nodes.acceptBtn.disabled,false);});
test("fresh accept after undo",()=>{nodes.acceptBtn.click();assert(nodes.draft.value.endsWith("materialization"));});
test("new human edit invalidates stale undo",()=>{nodes.draft.value="NEW HUMAN EDIT";nodes.draft.input();assert.equal(nodes.undoBtn.disabled,true);});
test("stale undo cannot clobber",()=>{nodes.undoBtn.click();assert.equal(nodes.draft.value,"NEW HUMAN EDIT");});
test("subsequent accept uses current input",()=>{nodes.acceptBtn.click();assert(nodes.draft.value.startsWith("NEW HUMAN EDIT"));});
test("reject does not erase accepted input",()=>{const before=nodes.draft.value;nodes.rejectBtn.click();assert.equal(nodes.draft.value,before);});
test("no-send receipt",()=>assert(nodes.receipt.textContent.includes("SEND 0")));
test("no-execute receipt",()=>assert(nodes.receipt.textContent.includes("EXECUTE 0")));
console.log("PASS_COGBX_R1_INTERACTION_DOM_SHIM",checks);
