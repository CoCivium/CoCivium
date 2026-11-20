#!/usr/bin/env node
/**
 * CoNod -> qualified CoPre source resolver R1. PURE, shadow-only, read-only.
 * A standalone ASCII apostrophe is a request to preview one qualified bounded
 * WorkID; NOT authority, an automatic worker, a universal session binding,
 * a trigger on code/contractions, or permission to send/publish/spawn.
 *
 * Input is already source-observed, scoped JSON supplied by an opt-in caller.
 * This module does no network, disk write, browser injection or scheduling.
 */
import {readFileSync} from "node:fs";

const ALLOWED_EFFECTS = new Set(["NONE","READ_ONLY","SOURCE_TEST"]);
const REQUIRED_RAILS = Object.freeze([
  "SESSION_NE_WORKID","NOD_NE_AUTHORITY","LATEST_NE_NEWEST",
  "ONE_ACTUATOR_PER_SCOPE","NO_PHANTOM_ACK","STOP_OVERRIDES_CONTINUE"
]);
const hex40=/^[a-f0-9]{40}$/i;
const hex64=/^[a-f0-9]{64}$/i;
const isObj = x=>x!==null&&typeof x==="object"&&!Array.isArray(x);
const str = x=>typeof x==="string"&&x.trim().length>0;
const integer = x=>Number.isSafeInteger(x)&&x>=0;
const safeId = x=>typeof x==="string"&&/^[a-zA-Z0-9_.:-]{1,128}$/.test(x);

function hold(reason,extra={}) {
  return {schema:"CoNod.QualifiedRebind.ShadowR1",decision:"HOLD",
    reason,work_id:null,effect:"NONE",executed:false,
    receiver_ack:false,provider_session_mutated:false,
    next:"Verify source, owner approval, scope and stop without a new watcher.",
    nonclaims:[...REQUIRED_RAILS],...extra};
}
export function parseGesture(message) {
  return typeof message==="string"&&message.trim()==="'" ? "CONOD_REBIND" : "NOT_CONOD";
}
function validPolicy(p,scope,now) {
  if(!isObj(p)||!safeId(p.id)||!safeId(p.scope)||p.scope!==scope) return false;
  if(!hex40.test(p.git_commit)||!hex40.test(p.git_blob)||!hex64.test(p.content_sha256)) return false;
  if(!integer(p.epoch)||p.epoch===0||!str(p.approved_by)||!str(p.approval_receipt))return false;
  if(p.approved!==true||p.source_verified!==true||p.revoked!==false||p.compatible!==true)return false;
  if(!integer(p.valid_from)||p.valid_from>now)return false;
  if(!integer(p.valid_until)||p.valid_until<now)return false;
  if(!Array.isArray(p.effect_ceiling)||!p.effect_ceiling.length||p.effect_ceiling.some(x=>!ALLOWED_EFFECTS.has(x)))return false;
  if(p.expands_authority!==false)return false;
  return true;
}
function validWork(w,scope,now) {
  return isObj(w)&&safeId(w.work_id)&&w.scope===scope&&hex64.test(w.source_sha256)&&
    str(w.owner)&&str(w.receiver)&&w.stop_available===true&&w.revoked===false&&
    integer(w.observed_at)&&w.observed_at<=now&&integer(w.valid_until)&&w.valid_until>=now&&
    integer(w.lease_epoch)&&w.lease_epoch>0&&w.lease_state==="CURRENT"&&
    ALLOWED_EFFECTS.has(w.effect_class)&&w.authority_provenance==="SCOPED_APPROVED"&&
    w.receiver_state==="SOURCE_KNOWN"&&w.dependency_state==="READY"&&
    w.collision_state==="NO_CONTEST"&&w.source_verified===true&&
    integer(w.value)&&integer(w.urgency)&&integer(w.risk)&&w.risk<=10&&
    integer(w.dependencies_priority)&&w.dependencies_priority<=10&&
    (w.status==="ELIGIBLE"||w.status==="QUIESCENT");
}
function score(w){return w.value*10+w.urgency*5+w.dependencies_priority*3-w.risk*8}
export function resolveCoNod(input) {
  if(!isObj(input)||parseGesture(input.message)!=="CONOD_REBIND")return hold("HOLD_NOT_STANDALONE_APOSTROPHE");
  if(input.stop===true)return hold("HOLD_STOP_ACTIVE");
  if(!safeId(input.scope)||!safeId(input.caller)||!integer(input.now_utc_s)||input.now_utc_s===0)return hold("HOLD_UNBOUND_CONTEXT");
  if(input.authorized_reader!==true||input.consent_current!==true)return hold("HOLD_NO_READER_OR_CONSENT");
  if(!Array.isArray(input.policies)||!Array.isArray(input.work)||!Array.isArray(input.receipts))return hold("HOLD_MISSING_EVIDENCE_COLLECTION");
  if(input.policy_registry_current!==true||input.owner_registry_current!==true||input.revocation_check_current!==true)return hold("HOLD_STALE_QUALIFICATION");
  const ps=input.policies.filter(p=>validPolicy(p,input.scope,input.now_utc_s));
  if(!ps.length)return hold("HOLD_NO_QUALIFIED_COPRE");
  const epoch=Math.max(...ps.map(p=>p.epoch));
  const sameEpoch=ps.filter(p=>p.epoch===epoch);
  const identities=new Set(sameEpoch.map(p=>p.git_commit+"/"+p.git_blob+"/"+p.content_sha256));
  if(identities.size!==1)return hold("HOLD_COLLIDING_POLICY_EPOCH");
  const selected=sameEpoch[0];
  const eligible=input.work.filter(w=>validWork(w,input.scope,input.now_utc_s)&&
    selected.effect_ceiling.includes(w.effect_class));
  if(!eligible.length)return hold("HOLD_NO_ELIGIBLE_WORK");
  // One work ID may have at most one observed state for a single head.
  const byId=new Map();
  for(const w of input.work){
    if(!safeId(w?.work_id))continue;
    const prior=byId.get(w.work_id);
    if(prior&&JSON.stringify(prior)!==JSON.stringify(w))return hold("HOLD_WORK_IDENTITY_COLLISION");
    byId.set(w.work_id,w);
  }
  eligible.sort((a,b)=>score(b)-score(a)||a.work_id.localeCompare(b.work_id));
  const w=eligible[0];
  if(input.receipts.some(r=>r?.work_id===w.work_id&&r?.source_sha256===w.source_sha256&&
      ["COMMITTED","RECEIVER_ACK"].includes(r?.state))) {
    return { ...hold("NO_MATERIAL_DELTA"),decision:"NO_MATERIAL_DELTA",
      work_id:w.work_id,policy_epoch:selected.epoch,
      next:"Sleep until an eligible source, authority, or work state changes." };
  }
  if(input.receipts.some(r=>r?.work_id===w.work_id&&
      (r?.source_sha256!==w.source_sha256||r?.state==="INDETERMINATE")))
    return hold("HOLD_PRIOR_EFFECT_UNRESOLVED");
  const canPreview = w.effect_class==="NONE"||w.effect_class==="READ_ONLY";
  return {
    schema:"CoNod.QualifiedRebind.ShadowR1",
    decision:canPreview?"PREVIEW_READ_ONLY":"HOLD",
    reason:canPreview?"QUALIFIED_POLICY_AND_WORK":"HOLD_EFFECT_REQUIRES_SEPARATE_ACTUATOR",
    work_id:w.work_id,policy_id:selected.id,policy_epoch:selected.epoch,
    policy_ref:{commit:selected.git_commit,blob:selected.git_blob,sha256:selected.content_sha256},
    source_sha256:w.source_sha256,owner:w.owner,receiver:w.receiver,
    lease_epoch:w.lease_epoch,priority_score:score(w),
    effect:"NONE",executed:false,receiver_ack:false,provider_session_mutated:false,
    next:canPreview?"Review source-backed next deed; execute only through an elected authorized adapter.":"Obtain separate effect authority.",
    nonclaims:[...REQUIRED_RAILS,"SHADOW_PREVIEW_NE_RUNTIME","CI_PASS_NE_RECEIVER_PICKUP"]
  };
}
if(process.argv[1]?.endsWith("conod_qualified_copre_r1.mjs")){
  const arg=process.argv[2];
  if(arg==="--preview"){
    const data=JSON.parse(readFileSync(process.argv[3],"utf8"));
    process.stdout.write(JSON.stringify(resolveCoNod(data),null,2)+"\n");
  }else if(arg==="--help"){
    process.stdout.write("node conod_qualified_copre_r1.mjs --preview <scoped-input.json> (read-only)\n");
  }
}
