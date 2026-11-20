"use strict";
/* CoCI+ R0 non-cycling session-residue gates, source-only.
 * Bounded to one public-safe checkpoint and explicit adopters.
 * Does NOT archive/close provider chats, clean user files, stop processes,
 * elect live receivers, or enforce policy over future sessions globally.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const checkpoint=JSON.parse(fs.readFileSync(path.join(root,"ai/currentness/coci-session-noncycling-checkpoint-r0-20261120.json"),"utf8"));
const policy=JSON.parse(fs.readFileSync(path.join(root,"ai/currentness/coci-session-residue-gates-r0-20261120.json"),"utf8"));
const clone=x=>JSON.parse(JSON.stringify(x));
let passed=0;
function check(name,fn){fn();passed++;process.stdout.write("PASS "+name+"\n");}
function validCheckpoint(c){
  assert.equal(c.schema,"CoAll.CoSessionLifecycle.NonCyclingHandoff.R0","HOLD_CHECKPOINT_SCHEMA");
  assert.equal(c.status,"CANDIDATE_NONCYCLING_HANDOFF__NOT_PROVIDER_ARCHIVE__NOT_RUNTIME_ADOPTION","HOLD_STATUS_PROMOTION");
  assert.match(c.work_id,/^CoTheoryAll::CoMegaThesis::PR500::CI$/,"HOLD_WORKID_DRIFT");
  assert.equal(c.session_projection.provider_chat_archive_effect,"NOT_EXECUTED","HOLD_FALSE_ARCHIVE");
  assert.equal(c.session_projection.auto_restart_chat,false,"HOLD_AUTO_CHAT_RESTART");
  assert.equal(c.session_projection.chat_ping_or_heartbeat_required,false,"HOLD_CHAT_PING");
  assert.equal(c.session_projection.chat_as_actuator,false,"HOLD_CHAT_ACTUATOR");
  assert.equal(c.session_projection.provider_window_as_source_of_truth,false,"HOLD_PROVIDER_WINDOW_AS_SOURCE");
  assert.equal(c.session_projection.closed_or_archived_in_chatgpt_ui,"UNKNOWN_NOT_CLAIMED","HOLD_FALSE_PROVIDER_CLOSURE");
  assert.equal(c.lifecycle.other_session_pickup,"NO_RECEIPT","HOLD_PHANTOM_OTHER_SESSION_ACK");
  assert.equal(c.lifecycle.CoStead_receiver_pickup,"NO_RECEIPT","HOLD_PHANTOM_COSTEAD_ACK");
  assert.equal(c.lifecycle.CoAll_canon,"NOT_PROMOTED","HOLD_FALSE_CANON");
  assert.equal(c.privacy.chat_transcript_included,false,"HOLD_CHAT_TRANSCRIPT_EXPORT");
  assert.equal(c.privacy.private_manuscript_material_included,false,"HOLD_PRIVATE_MANUSCRIPT_EXPORT");
  assert.equal(c.privacy.secrets_included,false,"HOLD_SECRET_EXPORT");
  assert(c.source_pointers.some(x=>x.reference==="https://github.com/CoCivium/CoCivium/pull/500"),"HOLD_MISSING_WORK_FRONT");
  assert(c.wake_policy.some(x=>x.event==="PROVIDER_CHAT_CLOSED_OR_RATE_LIMITED"&&x.executor==="NONE"&&!x.chat_reopen),"HOLD_CHAT_OUTAGE_RESTART");
  assert(c.wake_policy.some(x=>x.event==="ELIGIBLE_GIT_SOURCE_DELTA"&&x.executor==="EXISTING_GITHUB_ACTIONS_CI"&&x.authority==="SOURCE_ONLY"&&!x.chat_reopen),"HOLD_CI_AUTHORITY_DRIFT");
  assert(c.nonclaims.includes("NO_PROVIDER_UI_ARCHIVE_EFFECT"),"HOLD_NONCLAIMS");
  return c;
}
function validPolicy(p){
  assert.equal(p.schema,"CoCI.SessionResidueBudget.R0","HOLD_POLICY_SCHEMA");
  assert.equal(p.state,"CANDIDATE_POLICY_NOT_GLOBALLY_ENFORCED","HOLD_FALSE_GLOBAL_POLICY");
  assert.equal(p.applies_to,"ONLY_EXPLICITLY_BOUND_WORKIDS_AND_ADOPTERS","HOLD_FALSE_ALL_SESSIONS");
  assert.equal(p.mode,"ARCHIVE_LOGICAL_CONTEXT_NOT_PROVIDER_CONVERSATION","HOLD_FALSE_UI_ARCHIVE");
  assert.equal(p.on_outage.automatic_provider_chat_restart,false,"HOLD_AUTO_PROVIDER_RESTART");
  assert.equal(p.on_outage.periodic_chat_heartbeat,false,"HOLD_HEARTBEAT");
  assert.equal(p.on_outage.auto_claim_successor,false,"HOLD_AUTO_SUCCESSOR");
  assert.equal(p.on_outage.auto_delete_provider_data,false,"HOLD_AUTO_DELETE");
  assert.equal(p.on_outage.automatic_public_release,false,"HOLD_AUTO_PUBLIC");
  assert.equal(p.on_outage.automatic_canon_promotion,false,"HOLD_AUTO_CANON");
  assert.equal(p.on_outage.unauthorized_network_effects,false,"HOLD_NETWORK_EFFECT");
  assert.equal(p.on_outage.unknown_receivers,"HOLD","HOLD_RECEIVER_UNCERTAINTY");
  assert.equal(p.on_outage.orphaned_leases,"QUARANTINE","HOLD_ORPHAN_LOCK_POLICY");
  assert.equal(p.on_outage.indeterminate_effects,"RECONCILE_BEFORE_RETRY","HOLD_UNCERTAIN_EFFECT");
  assert.equal(p.on_outage.max_infinite_retry,"FORBIDDEN","HOLD_INFINITE_RETRY");
  assert.equal(p.on_outage.durable_checkpoint_required,true,"HOLD_CHECKPOINT");
  assert(p.durable_keep.some(x=>x.kind==="SOURCE_AND_PROVENANCE"),"HOLD_SOURCE_LOSS");
  assert(p.durable_keep.some(x=>x.kind==="UNCERTAIN_EFFECTS_AND_ORPHAN_LOCKS"),"HOLD_UNCERTAIN_EVIDENCE_LOSS");
  assert(p.scope_exclusions.includes("GLOBAL_SESSION_LIFECYCLE_ENFORCEMENT"),"HOLD_FALSE_RUNTIME");
  assert(p.nonclaims.includes("NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF"),"HOLD_PHANTOM_ACK_RAIL");
  return p;
}
function planOutage(kind,p=policy,c=checkpoint){
  validPolicy(p);validCheckpoint(c);
  const actions={
    PROVIDER_SESSION_ENDED:"PRESERVE_CHECKPOINT_AND_SLEEP",
    PROVIDER_RATE_LIMITED:"PRESERVE_CHECKPOINT_AND_SLEEP",
    PROVIDER_UNKNOWN_FAILURE:"HOLD_UNKNOWN_AND_PRESERVE_CHECKPOINT",
    ORPHANED_ACTUATOR_LOCK:"QUARANTINE_NO_AUTO_BREAK",
    INDETERMINATE_EXTERNAL_EFFECT:"RECONCILE_BEFORE_RETRY",
    RECEIVER_ACK_MISSING:"HOLD_NO_PHANTOM_ACK",
    UNOBSERVED_FUTURE_SESSION:"HOLD_NO_GLOBAL_ENFORCEMENT"
  };
  return {
    status:actions[kind]??"HOLD_UNKNOWN_EVENT",
    effect:"NONE",
    provider_chat_restart:false,
    public_or_financial_effect:false,
    cleanup_delete:false,
    receiver_ack:false,
    ephemeral_session_kept_alive:false
  };
}
function negative(name,edit,which="policy"){
  check("fail-closed "+name,()=>{
    const p=clone(policy),c=clone(checkpoint);
    edit(which==="policy"?p:c);
    assert.throws(()=>which==="policy"?validPolicy(p):validCheckpoint(c),"MUTATION_UNDETECTED_"+name);
  });
}
check("bounded checkpoint and exact WorkID",()=>validCheckpoint(checkpoint));
check("policy candidate and explicit adoption boundary",()=>validPolicy(policy));
check("source pointers and prior receipt retained",()=>{
  assert(checkpoint.source_baseline.last_source_ci_run.includes("actions/runs/"));
  assert(checkpoint.source_pointers.some(x=>x.kind==="SOURCE_CONTRACT"&&x.git_blob_sha));
});
check("provider session not restarted or archived",()=>{
  assert.equal(planOutage("PROVIDER_SESSION_ENDED").provider_chat_restart,false);
  assert.equal(checkpoint.lifecycle.provider_chat_archive,"NOT_EXECUTED");
});
check("provider rate limit yields sleep not spin",()=>assert.equal(planOutage("PROVIDER_RATE_LIMITED").status,"PRESERVE_CHECKPOINT_AND_SLEEP"));
check("orphan lock quarantined without deleting evidence",()=>{
  const r=planOutage("ORPHANED_ACTUATOR_LOCK");
  assert.equal(r.status,"QUARANTINE_NO_AUTO_BREAK");assert.equal(r.cleanup_delete,false);
});
check("uncertain effect must reconcile before retry",()=>assert.equal(planOutage("INDETERMINATE_EXTERNAL_EFFECT").status,"RECONCILE_BEFORE_RETRY"));
check("unverified receiver cannot produce ACK",()=>assert.equal(planOutage("RECEIVER_ACK_MISSING").receiver_ack,false));
check("unknown future session explicitly held",()=>assert.equal(planOutage("UNOBSERVED_FUTURE_SESSION").status,"HOLD_NO_GLOBAL_ENFORCEMENT"));
check("all outage types remain non-effectful",()=>{
  for(const kind of ["PROVIDER_SESSION_ENDED","PROVIDER_RATE_LIMITED","PROVIDER_UNKNOWN_FAILURE","ORPHANED_ACTUATOR_LOCK","INDETERMINATE_EXTERNAL_EFFECT","RECEIVER_ACK_MISSING","UNOBSERVED_FUTURE_SESSION","UNRECOGNIZED"]){
    const r=planOutage(kind);
    assert.equal(r.effect,"NONE");assert.equal(r.public_or_financial_effect,false);
    assert.equal(r.provider_chat_restart,false);assert.equal(r.receiver_ack,false);
  }
});
negative("global-enforcement claim",x=>x.state="GLOBALLY_ENFORCED");
negative("false provider archive",x=>x.session_projection.provider_chat_archive_effect="EXECUTED","checkpoint");
negative("phantom CoStead ACK",x=>x.lifecycle.CoStead_receiver_pickup="PICKED_UP","checkpoint");
negative("provider auto-restart",x=>x.on_outage.automatic_provider_chat_restart=true);
negative("automatic deletion",x=>x.on_outage.auto_delete_provider_data=true);
negative("automatic public release",x=>x.on_outage.automatic_public_release=true);
negative("automatic canon promotion",x=>x.on_outage.automatic_canon_promotion=true);
negative("orphaned lock discarded",x=>x.on_outage.orphaned_leases="DELETE");
negative("private manuscript leak",x=>x.privacy.private_manuscript_material_included=true,"checkpoint");
negative("unqualified CI wake",x=>{x.wake_policy.find(y=>y.event==="ELIGIBLE_GIT_SOURCE_DELTA").authority="UNLIMITED";},"checkpoint");
process.stdout.write("NONCYCLING_RESIDUE_SOURCE_ONLY_PASS "+passed+" tests | all_sessions=false provider_chat_archived=false receiver_ack=false\n");