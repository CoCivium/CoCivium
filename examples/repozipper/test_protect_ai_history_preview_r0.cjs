"use strict";
/* Exact JS model extracted from the offline HTML, not a reimplementation. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const page = fs.readFileSync(path.join(__dirname,"protect_ai_history_preview_r0.html"),"utf8");
const match = page.match(/<script id="repozipper-preview-logic">([\s\S]*?)<\/script>/);
assert.ok(match,"MISSING_PREVIEW_SCRIPT");
const sandbox = {module:{exports:{}}};
vm.runInNewContext(match[1],sandbox,{timeout:1000,filename:"protect-preview-inline.js"});
const {inspectSynthetic,SYNTHETIC_FIXTURE} = sandbox.module.exports;

const result = inspectSynthetic(SYNTHETIC_FIXTURE);
assert.equal(result.schema,"RepoZipper.FirstUsePreview.R0");
assert.equal(result.evidence_class,"SYNTHETIC_ONLY");
assert.equal(result.conversation_count,3);
assert.equal(result.message_node_count,7);
assert.equal(result.real_files_read,0);
assert.equal(result.uploaded_bytes,0);
assert.equal(result.provider_sessions_modified,0);
assert.equal(result.independent_backup_verified,false);
assert.equal(result.delete_safe,false);
assert.equal(result.records.length,3);
assert.equal(result.records.map(x=>x.nodes).join(","),"3,2,2");
assert.deepEqual(result,inspectSynthetic(SYNTHETIC_FIXTURE),"REPLAY_NOT_DETERMINISTIC");

function rejected(fixture,label) {
  assert.throws(()=>inspectSynthetic(fixture),undefined,label);
}
rejected([],"EMPTY");
rejected([{id:"x",label:"L",messages:[]},{id:"x",label:"L2",messages:[]}],"DUPLICATE_ID");
rejected([{id:"x",label:"L",messages:[{role:"system"}]}],"ROLE_OUT_OF_SCOPE");
rejected([{id:"",label:"L",messages:[]}],"NO_ID");
rejected([{id:"x",label:"L",messages:null}],"BAD_MESSAGE_SHAPE");
rejected([{id:"x",label:12,messages:[]}],"BAD_LABEL_SHAPE");

console.log("PASS: 14 synthetic preview assertions/negative cases; offline source only; no DOM/browser acceptance claimed");
