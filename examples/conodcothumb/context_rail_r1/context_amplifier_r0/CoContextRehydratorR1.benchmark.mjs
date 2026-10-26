import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {planContext} from './CoContextAmplifierR0.mjs';
import {rehydrateLocalPlan} from './CoContextRehydratorR1.mjs';

const sha=(x)=>createHash('sha256').update(x).digest('hex');
const root=await fs.mkdtemp(path.join(tmpdir(),'co-context-r1-benchmark-'));
try {
  const sources=[];
  let corpusBytes=0;
  for(let i=0;i<24;i++){
    const id='source'+String(i).padStart(2,'0');
    const data='Fixture '+id+', synthetic public evidence for a purely local benchmark.\n'+
      'Lineage '+(i%4)+', factual status: not real evidence.\n' + ('x'.repeat(320)) + '\n';
    const b=Buffer.from(data,'utf8');
    await fs.writeFile(path.join(root,id+'.txt'),b);
    corpusBytes+=b.length;
    sources.push({id,source_ref:'local:'+id+'.txt',sha256:sha(b),
      cost_units:9,utility: i===0||i===1?100:(i===18?1:60-(i%10)),
      required:i===0||i===1,kind:i===18?'COUNTER':'SUPPORT',
      freshness:'CURRENT',privacy:'PUBLIC'});
  }
  const plan=planContext({work_id:'CoContextAmplifier.R1.Benchmark',budget_units:55,headroom_units:10,sources});
  const before=process.hrtime.bigint();
  const ver=await rehydrateLocalPlan(plan,{root,explicitLocalRead:true,maxPerFileBytes:1024,
    maxTotalBytes:6144,includeText:false});
  const wallMs=Number(process.hrtime.bigint()-before)/1e6;
  const selectedIds=ver.sources.map(x=>x.id);
  const checks={
    source_bytes_hash_qualified:ver.state==='SOURCE_BYTES_VERIFIED_LOCAL_ONLY',
    both_required_preserved:selectedIds.includes('source00')&&selectedIds.includes('source01'),
    counterevidence_preserved:selectedIds.includes('source18'),
    only_selected_files_read:ver.effects.local_reads===ver.source_count,
    fewer_bytes_than_full_corpus:ver.bytes_verified<corpusBytes,
    within_materialized_byte_budget:ver.bytes_verified<=6144,
    model_token_count_not_claimed:ver.model_context_tokens===null,
    no_external_effects:ver.effects.network===0&&ver.effects.sends===0&&ver.effects.writes===0,
    receiver_ack_not_claimed:ver.receiver_ack===false,
    headroom_reserved:plan.headroom_units===10
  };
  const result={
    schema:'CoAll.CoContextAmplifier.SourceRehydrationBenchmark.R1',
    environment:'LOCAL_SYNTHETIC_NODE_FIXTURE',
    status:Object.values(checks).every(Boolean)?'PASS_LOCAL_SOURCE_BYTE_REHYDRATION':'FAIL',
    checks, checked:Object.keys(checks).length,
    passed:Object.values(checks).filter(Boolean).length,
    corpus_descriptor_count:sources.length,
    selected_count:ver.source_count,
    full_corpus_bytes:corpusBytes,selected_verified_bytes:ver.bytes_verified,
    fraction_corpus_bytes_not_materialized:Number((1-ver.bytes_verified/corpusBytes).toFixed(4)),
    included_counterevidence:selectedIds.includes('source18'),
    manifest_sha256:ver.manifest_sha256,read_wall_milliseconds:Number(wallMs.toFixed(3)),
    token_measurement:'HELD_MODEL_SPECIFIC_TOKENIZER_NOT_RUN',
    source_data:'DISPOSABLE_SYNTHETIC_PUBLIC_NOT_REAL_WORLD',
    receiver_ack:false,authority:'EXPLICIT_SYNTHETIC_LOCAL_READ',
    nonclaims:['BYTE_FRACTION_NE_TOKEN_SAVINGS','RETRIEVAL_NE_ANSWER_QUALITY',
      'SYNTHETIC_TIMING_NE_X2_PERFORMANCE','SOURCE_VERIFIED_NE_PROVIDER_READ']
  };
  console.log(JSON.stringify(result,null,2));
  if(result.status!=='PASS_LOCAL_SOURCE_BYTE_REHYDRATION')process.exitCode=2;
} finally {await fs.rm(root,{recursive:true,force:true});}
