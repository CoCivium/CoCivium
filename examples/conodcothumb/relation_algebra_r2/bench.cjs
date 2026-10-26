'use strict';
const M=require('./CoRelationInverseR2.cjs');
const args={privacy:'PUBLIC',gesture:'EXPLICIT_RING',context:'MAP',source_ref:'sha256:'+'c'.repeat(64),authority:'NONE',relation_id:'DEPENDS_ON',transform:'CONVERSE'};
function batch(fn,n){const st=process.hrtime.bigint();let x;for(let i=0;i<n;i++)x=fn(i);return {per_op_ns:Number(process.hrtime.bigint()-st)/n,check:x};}
function median(a){return [...a].sort((x,y)=>x-y)[Math.floor(a.length/2)];}
for(let i=0;i<3;i++){batch(i=>M.decodeAddress(BigInt(i)%BigInt(M.addressCount())),5000);batch(i=>M.preview(args),5000)}
const decode=[],preview=[];for(let i=0;i<5;i++){decode.push(batch(j=>M.decodeAddress(BigInt(j)%BigInt(M.addressCount())),10000).per_op_ns);preview.push(batch(j=>M.preview(args),10000).per_op_ns)}
const out={schema:'CoCivium.CoMiddle.R2.Benchmark',environment:{node:process.version,platform:process.platform,arch:process.arch,cpu:require('node:os').cpus()[0]?.model},measure:'median per op amortized across five sequential 10k batches after three 5k warmup rounds; in-process only',
  logical_addresses:M.addressCount(),addressable_relations:M.relationMap.size,active_workers:0,
  descriptor_decode:{median_ns:median(decode),runs_ns:decode},
  shadow_preview:{median_ns:median(preview),runs_ns:preview},
  disclaimers:['SYNTHETIC_RUNTIME_NE_GUI','GENERATION_NE_SEMANTIC_VALIDATION','NO_RECIPIENT_OR_OS_IO','IN_PROCESS_TIMING_NE_SLO']};
console.log(JSON.stringify(out,null,2));
