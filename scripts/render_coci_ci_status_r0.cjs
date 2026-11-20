"use strict";
/* CoCI+ receipt to quiet GitHub run front door. Read-only, source-scoped.
   No network, runtime effect, receiver claim or external publication. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
const digest=b=>crypto.createHash("sha256").update(b).digest("hex");
const rails=[
 "CI_ARTIFACT_PICKUP_NE_COSTEAD_OR_X2_RECEIVER_PICKUP",
 "SEPARATE_GITHUB_JOB_NE_INDEPENDENT_PROVIDER",
 "PROCESS_REPLAY_NE_DURABLE_POWER_FAILURE_RECOVERY",
 "CI_PASS_NE_HUMAN_UX_ACCEPTANCE",
 "CI_SOURCE_NE_CANON_OR_COEX_OR_DEPLOYMENT",
 "NO_EXTERNAL_EFFECT_OR_AUTHORITY_EXPANSION"
];
function validate(r,env){
 assert.equal(r.schema,"CoCI.CrossJobArtifactReadback.R0","HOLD_SCHEMA");
 assert.equal(r.status,"GITHUB_CI_JOB_SCOPED_SOURCE_READBACK_PASS","HOLD_NOT_PASS");
 assert.match(r.source_commit,/^[0-9a-f]{40}$/,"HOLD_REVISION");
 if(env.GITHUB_SHA)assert.equal(r.source_commit,env.GITHUB_SHA,"HOLD_STALE_SHA");
 if(env.GITHUB_RUN_ID)assert.equal(String(r.github_run_id),String(env.GITHUB_RUN_ID),"HOLD_WRONG_RUN");
 assert.equal(r.source_job,"source-parity","HOLD_SOURCE_JOB");
 assert.equal(r.receiving_job,"artifact-readback","HOLD_READER_JOB");
 for(const [key,count] of [["source",11],["process_recovery",17],["concurrent_fencing",16],["negative_controls",10]])
   assert.equal(r.tests?.[key],count,"HOLD_"+key);
 const b=r.receiver_boundary;
 assert.equal(b?.distinct_github_actions_job,true,"HOLD_NOT_SEPARATE_JOB");
 assert.equal(b?.github_control_plane_shared,true,"HOLD_SHARED_PROVIDER_UNDECLARED");
 assert.equal(b?.different_power_domain,"NOT_INDEPENDENTLY_VERIFIED","HOLD_POWER_CLAIM");
 assert.equal(b?.receiver_is_cocivium_runtime,false,"HOLD_RUNTIME_CLAIM");
 assert.equal(b?.effect,"READ_ONLY_VERIFICATION_OF_GITHUB_CI_ARTIFACT","HOLD_EFFECT_SCOPE");
 for(const item of rails)assert(r.nonclaims?.includes(item),"HOLD_NONCLAIM_"+item);
 const hashes=r.received_artifact_file_hashes;
 assert(hashes&&Object.keys(hashes).length>=8,"HOLD_HASH_SET");
 for(const hash of Object.values(hashes))assert.match(hash,/^[0-9a-f]{64}$/,"HOLD_BAD_HASH");
 return r;
}
function construct(r,bytes,env){
 validate(r,env);
 return {
  schema:"CoCI.CoHereNow.ProofFrontDoor.R0",
  observed_at_utc:new Date().toISOString(),
  source_commit:r.source_commit,
  github_run_id:String(r.github_run_id),
  readback_receipt_sha256:digest(bytes),
  headline:"CI source and same-host recovery passed; independent receiver is unverified.",
  verified:{source:11,process_replay:17,same_host_concurrency:16,same_provider_tamper:10,
    cross_job_readback:"PASS_WITHIN_GITHUB"},
  holds:{separate_powered_receiver:"NOT_VERIFIED",physical_cold_recovery:"NOT_VERIFIED",
    X2_CoStead:"NOT_VERIFIED",human_UX:"NOT_VERIFIED",browser:"NOT_PROVED_BY_RECEIPT",
    production_runtime:"NOT_VERIFIED",CoEx_canon_publication:"NOT_VERIFIED"},
  next_safe_action:"Authorized separate receiver cold-start/readback for one inert WorkID.",
  authority:"READ_ONLY_CI",
  no_new_scheduler:true,
  Rick_routine_actions:0,
  source_url:env.GITHUB_REPOSITORY?
    "https://github.com/"+env.GITHUB_REPOSITORY+"/tree/"+r.source_commit:null,
  proof_url:env.GITHUB_REPOSITORY?
    "https://github.com/"+env.GITHUB_REPOSITORY+"/actions/runs/"+r.github_run_id:null,
  nonclaims:rails,
  UX_ACCEPTANCE:"UNPROVEN"
 };
}
function render(p){
 const link=p.proof_url?"[GitHub run]("+p.proof_url+")":"GitHub run receipt";
 return [
  "## CoCI+ | CoHereNow",
  "",
  "**Source and synthetic recovery PASS. Independent receiver HOLD.**",
  "",
  "11 source, 17 replay, 16 same-host concurrency and 10 artifact tamper checks passed.",
  "The two CI jobs share GitHub. No separate powered CoStead/X2 receiver is evidenced.",
  "",
  "**Next safe action:** "+p.next_safe_action,
  "",
  "Evidence: "+link+" | source SHA "+p.source_commit+".",
  "",
  "<details><summary>Currentness, limitations and optionality</summary>",
  "",
  "- Separate powered receiver, physical cold recovery and X2/CoStead: UNVERIFIED.",
  "- Browser accessibility and independent reader acceptance: UNVERIFIED.",
  "- No CoEx, canon, production runtime or public domain effect.",
  "- One existing event-triggered CI workflow; no new watcher or Rick handoff.",
  "",
  "</details>",
  "",
  "Rail: CHANGE / CI / RECEIPT / SAME-PROVIDER READBACK / INDEPENDENT RECEIVER HOLD",
  ""
 ].join("\n");
}
function selfTest(r,env){
 const clone=x=>JSON.parse(JSON.stringify(x));
 const variants=[
 ["stale_commit",x=>x.source_commit="0".repeat(40)],
 ["wrong_run",x=>x.github_run_id="0"],
 ["false_power",x=>x.receiver_boundary.different_power_domain="VERIFIED"],
 ["false_runtime",x=>x.receiver_boundary.receiver_is_cocivium_runtime=true],
 ["missing_rail",x=>x.nonclaims=[]],
 ["missing_concurrency",x=>x.tests.concurrent_fencing=0],
 ["wrong_effect",x=>x.receiver_boundary.effect="LIVE_PUBLIC_EFFECT"],
 ["missing_hashes",x=>x.received_artifact_file_hashes={}]
 ];
 for(const [label,mutate] of variants){const d=clone(r);mutate(d);assert.throws(()=>validate(d,env),"NEGATIVE_NOT_HELD_"+label);
   process.stdout.write("PASS FRONTDOOR_NEGATIVE "+label+"\n");}
 process.stdout.write("FRONTDOOR_NEGATIVE_PASS 8\n");
}
const input=path.resolve(process.argv[2]||"artifacts/comegathesis-readback-r0/coci-artifact-readback-receipt.json");
const bytes=fs.readFileSync(input),r=JSON.parse(bytes.toString("utf8")),env=process.env;
validate(r,env);
if(process.argv.includes("--self-test"))selfTest(r,env);
else {
 const out=path.resolve(process.argv[3]||"artifacts/comegathesis-readback-r0/cohere-ci-status.json");
 const md=path.resolve(process.argv[4]||"artifacts/comegathesis-readback-r0/cohere-ci-status.md");
 const p=construct(r,bytes,env),message=render(p);
 fs.mkdirSync(path.dirname(out),{recursive:true});
 fs.mkdirSync(path.dirname(md),{recursive:true});
 fs.writeFileSync(out,JSON.stringify(p,null,2)+"\n",{flag:"wx"});
 fs.writeFileSync(md,message,{flag:"wx"});
 if(env.GITHUB_STEP_SUMMARY)fs.appendFileSync(env.GITHUB_STEP_SUMMARY,"\n"+message+"\n");
 process.stdout.write("CI_FRONTDOOR_PASS source_only=true independent_receiver=false\n");
}