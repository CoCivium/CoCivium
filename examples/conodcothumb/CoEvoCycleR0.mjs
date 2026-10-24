#!/usr/bin/env node
/*
 CoEvoCycle R0: bounded, no-write-to-source scheduled regression and comparative
 advisory. It checks real code, logs PASS/FAIL/HELD and produces a single
 append-only CI artifact. Not self-modifying, perpetual, authority-bearing, or
 a provider/device coordinator.
*/
import { spawnSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { access, mkdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chooseRoute } from './CoRouteSelectorR0.mjs';

const SCHEMA='CoAll.CoEvoCycle.BoundedR0';
const here=dirname(fileURLToPath(import.meta.url));
const argv=process.argv.slice(2);
function arg(name,otherwise=null){let i=argv.indexOf(name);return i<0?otherwise:argv[i+1]??null}
function timestamp(){return new Date().toISOString()}
const root=resolve(arg('--root',resolve(here,'../..')));
const out=arg('--output');
const includeLarge=argv.includes('--include-large');
const sandboxPartial=argv.includes('--allow-partial-sandbox');
const maxMs=120000;
const started=timestamp();
const id=started.replace(/[^0-9TZ]/g,'')+'-'+randomUUID().slice(0,8);
const rows=[];
function logReceipt(test,status,expected,observed,proof='LOCAL_ISOLATED_CANARY') {
 rows.push({schema:SCHEMA,wave_id:id,run_utc:timestamp(),test,status,proof_class:proof,
  expected,observed,environment:{node:process.version,platform:process.platform,arch:process.arch},
  nonclaims:['NOT_X2_DEVICE_PROOF','NOT_RECEIVER_ACK','NO_AUTO_CODE_PROMOTION','NO_EXTERNAL_EFFECTS']});
}
async function check(name,executable,args,{cwd=root,optional=false,env={}}={}) {
 const path=args.find(a=>a.endsWith('.mjs'));
 if(path){try{await access(path.startsWith('/')?path:join(cwd,path));}
  catch(e){logReceipt(name,optional||sandboxPartial?'HELD':'FAIL','Executable fixture exists',{reason:'SOURCE_UNAVAILABLE',code:e.code});return;}}
 const begun=process.hrtime.bigint();
 const p=spawnSync(executable,args,{cwd,encoding:'utf8',timeout:maxMs,maxBuffer:1024*1024,
  env:{...process.env,...env}});
 const elapsed=Number(process.hrtime.bigint()-begun)/1e6;
 const output=String(p.stdout??'')+'\n'+String(p.stderr??'');
 const stdout_sha256=createHash('sha256').update(output).digest('hex');
 const match=output.match(/# tests (\d+)/);
 const passed=output.match(/# pass (\d+)/);
 const skipped=output.match(/# skipped (\d+)/);
 const python=output.match(/Ran (\d+) tests?/);
 const status=p.status===0?'PASS':'FAIL';
 logReceipt(name,status,{exit_code:0,max_runtime_ms:maxMs},
  {exit_code:p.status,elapsed_ms:Math.round(elapsed*1000)/1000,
   tests:match?Number(match[1]):python?Number(python[1]):null,
   passed:passed?Number(passed[1]):null,skipped:skipped?Number(skipped[1]):0,
   stdout_stderr_sha256:stdout_sha256,execution_error:p.error?.code??null},
   'FRESH_BOUNDED_CHILD_PROCESS');
}
async function run(){
 const policy=join(root,'examples/conodcothumb/CoNodCoThumbPolicyR0.mjs');
 const r0=join(root,'examples/conodcothumb/CoPayloadCapsuleR0.test.mjs');
 const r1=join(root,'examples/conodcothumb/CoPayloadLargeR1.test.mjs');
 const selector=join(root,'examples/conodcothumb/CoRouteSelectorR0.test.mjs');
 await check('shadow_policy_22_prior_assertions','node',[policy,'--selftest']);
 await check('explicit_r0_local_payload','node',['--test',r0]);
 await check('r1_chunked_file_recovery_and_tamper','node',['--test',r1],{env:{CO_THUMB_LARGE_TEST:includeLarge?'1':'0'}});
 await check('deterministic_route_election','node',['--test',selector]);
 const pytest=join(root,'benchmarks/costretch_r1/tests/test_costretch.py');
 try {await access(pytest);await check('costretch_prior_benchmark_regression','python3',
   ['-m','unittest','discover','-v','-s','benchmarks/costretch_r1/tests']);}
 catch(e){logReceipt('costretch_prior_benchmark_regression',sandboxPartial?'HELD':'FAIL','Existing Python fixture accessible',
   {code:e.code,reason:'MISSING_IN_THIS_RUNTIME'},'FIXTURE_GAP');}
 const scenarios=[
  ['inline',128],['local_media',1245443],['legacy_r0_max',512*1024**2],
  ['large_stream',600*1024**2],['bounded_16gb',16*1024**3],
  ['extended_without_optin',17*1024**3],['over_any_cap',65*1024**3]
 ];
 const expected=['SMALL_INLINE','EXPLICIT_FILE_BACKED_R0','EXPLICIT_FILE_BACKED_R0',
  'EXPLICIT_CHUNKED_R1','EXPLICIT_CHUNKED_R1',null,null];
 const observed=scenarios.map(([name,byte_count],i)=>{
  const r=chooseRoute({byte_count});return {name,byte_count,lane:r.lane,status:r.status,correct:r.lane===expected[i]};
 });
 logReceipt('bounded_candidate_lane_election',observed.every(x=>x.correct)?'PASS':'FAIL',
  'Seven sizes elect bounded routes, never unlimited automatic agents',observed,
  'DETERMINISTIC_STRATEGY_COMPARISON_NOT_BENCHMARK');
 const failed=rows.filter(x=>x.status==='FAIL');
 const held=rows.filter(x=>x.status==='HELD');
 const status=failed.length?'FAIL':held.length?'INCOMPLETE':'PASS';
 logReceipt('coturtle_adjudication',failed.length?'FAIL':held.length?'HELD':'PASS',
  'No failure is promoted and missing environment is explicit',
  {verification_status:status,observed_tests:rows.length,
   fail:failed.map(x=>x.test),held:held.map(x=>x.test),
   next_deed:failed.length?'INSPECT_FAILURE':held.length?'REQUALIFY_MISSING_FIXTURE':'REVIEW_CANDIDATE_ONLY',
   autopromotion:'DISABLED'},'BOUNDED_META_REVIEW');
 if(!out){console.log(JSON.stringify({status,rows:rows.length,passed:rows.filter(x=>x.status==='PASS').length,
  held:rows.filter(x=>x.status==='HELD').length,failed:rows.filter(x=>x.status==='FAIL').length}));
  process.exitCode=failed.length?1:0;return;}
 await mkdir(dirname(resolve(out)),{recursive:true});
 const body=rows.map(x=>JSON.stringify(x)).join('\n')+'\n';
 await writeFile(resolve(out),body,{flag:'wx',mode:0o600});
 console.log(JSON.stringify({schema:SCHEMA,wave_id:id,status,rows:rows.length,
  pass:rows.filter(x=>x.status==='PASS').length,held:rows.filter(x=>x.status==='HELD').length,
  fail:rows.filter(x=>x.status==='FAIL').length,
  output_sha256:createHash('sha256').update(body).digest('hex'),
  artifact_label:'TEST_HARNESS_LOCAL_OUTPUT_NOT_INDEPENDENT_CUSTODY',
  next_deed:status==='PASS'?'REVIEW_NO_AUTOPROMOTION':'INSPECT_GAPS'}));
 process.exitCode=failed.length?1:0;
}
run().catch(e=>{console.error('CoEvoCycle held: '+(e.code||e.message));process.exitCode=1;});
