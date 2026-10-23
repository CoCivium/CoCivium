'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=__dirname;
const canonical=v=>Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;
const digest=o=>crypto.createHash('sha256').update(JSON.stringify(canonical(o))).digest('hex');
const lines=fs.readFileSync(path.join(root,'benchmark_evo_R1.jsonl'),'utf8').trim().split('\n');
let prev='0'.repeat(64),counts={PASS:0,FAIL:0,HOLD:0,NOT_RUN:0};
for(let i=0;i<lines.length;i++){
 const row=JSON.parse(lines[i]);assert.equal(row.seq,i+1);assert.equal(row.schema,'CoBenchmarkEvoEvent/1');assert.equal(row.prev_hash,prev);
 const {event_hash,...body}=row;assert.equal(event_hash,digest(body));assert(Object.hasOwn(counts,row.status));counts[row.status]++;prev=event_hash;
}
assert.equal(lines.length,28);assert.equal(prev,fs.readFileSync(path.join(root,'HEAD_R1.sha256'),'utf8').trim());
console.log(JSON.stringify({state:'PASS',source:'Node independent verifier',events:lines.length,head:prev,counts}));
