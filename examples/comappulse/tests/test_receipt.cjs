'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const ledger=fs.readFileSync(path.join(root,'benchmark_evo.jsonl'),'utf8').trim().split('\n');
const sha=o=>crypto.createHash('sha256').update(JSON.stringify(o,Object.keys(o).sort())).digest('hex');
// Only top-level document keys are used; nested detail may vary in key order.
function canonical(v){if(Array.isArray(v))return v.map(canonical);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])]));return v;}
const digest=o=>crypto.createHash('sha256').update(JSON.stringify(canonical(o))).digest('hex');
let previous='0'.repeat(64);
ledger.forEach((line,i)=>{const event=JSON.parse(line);assert.equal(event.schema,'CoBenchmarkEvoEvent/1');assert.equal(event.seq,i+1);assert.equal(event.prev_hash,previous);const {event_hash,...body}=event;assert.equal(event_hash,digest(body));previous=event_hash;});
assert.equal(previous,fs.readFileSync(path.join(root,'HEAD.sha256'),'utf8').trim());
console.log('PASS independent Node ledger verifier',ledger.length,'events',previous);
