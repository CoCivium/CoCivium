import assert from "node:assert/strict";
import {parseGesture,resolveCoNod} from "./conod_qualified_copre_r1.mjs";
const policy={id:"copre-source-qualified-r0",scope:"colocal",git_commit:"a".repeat(40),
 git_blob:"b".repeat(40),content_sha256:"c".repeat(64),epoch:7,approved_by:"owner",
 approval_receipt:"receipt",approved:true,source_verified:true,revoked:false,compatible:true,
 expands_authority:false,valid_from:100,valid_until:2000,effect_ceiling:["NONE","READ_ONLY"]};
const work={work_id:"CoLocal.WorkA",scope:"colocal",source_sha256:"f".repeat(64),
 owner:"CoLocalOwner",receiver:"local-reader",stop_available:true,revoked:false,
 observed_at:950,valid_until:2000,lease_epoch:2,lease_state:"CURRENT",
 effect_class:"READ_ONLY",authority_provenance:"SCOPED_APPROVED",
 receiver_state:"SOURCE_KNOWN",dependency_state:"READY",collision_state:"NO_CONTEST",
 source_verified:true,value:7,urgency:5,risk:2,dependencies_priority:4,status:"ELIGIBLE"};
const baseline=()=>({message:"'",scope:"colocal",caller:"consenting-reader",now_utc_s:1000,
 stop:false,authorized_reader:true,consent_current:true,policy_registry_current:true,
 owner_registry_current:true,revocation_check_current:true,
 policies:[structuredClone(policy)],work:[structuredClone(work)],receipts:[]});
let passed=0;
const test=(name,fn)=>{fn();passed++;process.stdout.write("PASS "+name+"\n");};
test("only literal standalone apostrophe",()=>{assert.equal(parseGesture("'"),"CONOD_REBIND");for(const s of ["I can't","' plus text","''","quoted apostrophe",null,1])assert.equal(parseGesture(s),"NOT_CONOD");});
test("read-only preview has zero effects",()=>{const r=resolveCoNod(baseline());assert.equal(r.decision,"PREVIEW_READ_ONLY");assert.equal(r.work_id,work.work_id);assert.equal(r.effect,"NONE");assert.equal(r.executed,false);assert.equal(r.receiver_ack,false);});
test("ten repeated nods produce no effects",()=>{const v=Array.from({length:10},()=>resolveCoNod(baseline()));assert.equal(new Set(v.map(x=>JSON.stringify(x))).size,1);assert(v.every(x=>x.executed===false));});
test("committed receipt quiets identical work",()=>{const x=baseline();x.receipts.push({work_id:work.work_id,source_sha256:work.source_sha256,state:"COMMITTED"});assert.equal(resolveCoNod(x).decision,"NO_MATERIAL_DELTA");});
test("source drift with prior effect holds",()=>{const x=baseline();x.receipts.push({work_id:work.work_id,source_sha256:work.source_sha256,state:"COMMITTED"});x.work[0].source_sha256="e".repeat(64);assert.equal(resolveCoNod(x).reason,"HOLD_PRIOR_EFFECT_UNRESOLVED");});
test("STOP overrides",()=>{const x=baseline();x.stop=true;assert.equal(resolveCoNod(x).reason,"HOLD_STOP_ACTIVE");});
test("revoked policy holds",()=>{const x=baseline();x.policies[0].revoked=true;assert.equal(resolveCoNod(x).reason,"HOLD_NO_QUALIFIED_COPRE");});
test("approved epoch beats new timestamp",()=>{const x=baseline();x.policies.push({...policy,id:"old",epoch:3,valid_from:999});assert.equal(resolveCoNod(x).policy_epoch,7);});
test("unapproved newer policy ignored",()=>{const x=baseline();x.policies.push({...policy,epoch:99,approved:false});assert.equal(resolveCoNod(x).policy_epoch,7);});
test("same epoch conflicting source holds",()=>{const x=baseline();x.policies.push({...policy,git_blob:"d".repeat(40)});assert.equal(resolveCoNod(x).reason,"HOLD_COLLIDING_POLICY_EPOCH");});
test("stale registries hold",()=>{for(const k of ["policy_registry_current","owner_registry_current","revocation_check_current"]){const x=baseline();x[k]=false;assert.equal(resolveCoNod(x).reason,"HOLD_STALE_QUALIFICATION");}});
test("unauthorized reader or consent hold",()=>{for(const k of ["authorized_reader","consent_current"]){const x=baseline();x[k]=false;assert.equal(resolveCoNod(x).reason,"HOLD_NO_READER_OR_CONSENT");}});
test("bad source hash or expiry holds",()=>{for(const [k,v] of [["git_commit","bad"],["content_sha256","wrong"],["valid_until",999]]){const x=baseline();x.policies[0][k]=v;assert.equal(resolveCoNod(x).reason,"HOLD_NO_QUALIFIED_COPRE");}});
test("authority ceiling does not expand",()=>{const x=baseline();x.policies[0].effect_ceiling.push("PUBLIC_SEND");assert.equal(resolveCoNod(x).reason,"HOLD_NO_QUALIFIED_COPRE");});
test("missing lease owner or receiver holds",()=>{for(const [k,v] of [["lease_state","EXPIRED"],["stop_available",false],["receiver_state","UNKNOWN"],["source_verified",false],["authority_provenance","UNKNOWN"]]){const x=baseline();x.work[0][k]=v;assert.equal(resolveCoNod(x).reason,"HOLD_NO_ELIGIBLE_WORK");}});
test("duplicate WorkID collision holds",()=>{const x=baseline();x.work.push({...work,value:6});assert.equal(resolveCoNod(x).reason,"HOLD_WORK_IDENTITY_COLLISION");});
test("indeterminate prior effect holds",()=>{const x=baseline();x.receipts.push({work_id:work.work_id,source_sha256:work.source_sha256,state:"INDETERMINATE"});assert.equal(resolveCoNod(x).reason,"HOLD_PRIOR_EFFECT_UNRESOLVED");});
test("source-test effect separately gated",()=>{const x=baseline();x.policies[0].effect_ceiling.push("SOURCE_TEST");x.work[0].effect_class="SOURCE_TEST";const r=resolveCoNod(x);assert.equal(r.decision,"HOLD");assert.equal(r.executed,false);});
test("priority chooses higher value lower risk",()=>{const x=baseline();x.work.push({...work,work_id:"CoLocal.WorkB",value:6,risk:9});assert.equal(resolveCoNod(x).work_id,"CoLocal.WorkA");});
test("unbound or prose input holds",()=>{for(const x of [null,{}, {message:"'",scope:"colocal"},{...baseline(),message:"Agreed '"}])assert.equal(resolveCoNod(x).decision,"HOLD");});
test("private and preview never imply receiver ACK",()=>{const r=resolveCoNod(baseline());assert.equal(r.provider_session_mutated,false);assert.equal(r.receiver_ack,false);assert(r.nonclaims.includes("NOD_NE_AUTHORITY"));});
test("no policy or work holds",()=>{for(const k of ["policies","work"]){const x=baseline();x[k]=[];assert.equal(resolveCoNod(x).decision,"HOLD");}});
process.stdout.write("CONOD_QUALIFIED_SHADOW_PASS "+passed+" tests | execution=0 | receiver_ack=false\n");
