import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { converseView, negationQuestion, effectGate, validateSyntheticAssertion } from "./CoRelationKernelR0.mjs";
const registry = JSON.parse(readFileSync(new URL("./registry.json", import.meta.url), "utf8"));
const sample = registry.sample_assertion;
const byId = new Map(registry.relation_types.map(r => [r.id,r]));
test("schema and finite frontier", () => {
  assert.equal(registry.schema, "CoCivium.CoMiddle.TypedRelations.R0");
  assert.equal(registry.state, "PUBLIC_DRAFT_SOURCE_REVIEW_ONLY_NO_DEVICE_OR_PROVIDER_RUNTIME");
  assert.equal(registry.relation_types.length, 20);
  assert.equal(byId.size,20);
  assert.equal(registry.limits.max_external_effects,0);
  assert.equal(registry.limits.max_worker_materializations,0);
  assert.ok(registry.limits.max_first_ring <= 8);
  assert.ok(registry.limits.max_preview_candidates <= 8);
});
test("source donors carry exact Git blob IDs", () => {
  assert.equal(registry.donors.length,5);
  for(const d of registry.donors) assert.match(d.blob,/^[a-f0-9]{40}$/);
});
for(const relation of registry.relation_types){
  test("typed counterpart round trip: "+relation.id,()=>{
    const c=byId.get(relation.counterpart);
    assert.ok(c);
    assert.equal(c.counterpart,relation.id);
    assert.equal(c.subject_type,relation.object_type);
    assert.equal(c.object_type,relation.subject_type);
    assert.equal(c.counterpart_kind,relation.counterpart_kind);
  });
  test("no effect or authority: "+relation.id,()=>{
    assert.equal(relation.authority_ceiling,"NONE");
    assert.equal(relation.effect,"NONE");
    assert.equal(relation.claim_status,"SOURCE_BOUND_NOT_AUTOVERIFIED");
    assert.ok(["CONVERSE_VIEW","SYMMETRIC_VIEW"].includes(relation.counterpart_kind));
  });
}
test("only two symmetric types",()=>{
  assert.deepEqual(registry.relation_types.filter(x=>x.counterpart_kind==="SYMMETRIC_VIEW").map(x=>x.id).sort(),["CONFLICT_CANDIDATE_WITH","RELATES_TO"]);
});
for(const q of registry.question_forms){
  test("question does not execute: "+q.id,()=>{
    assert.equal(q.action,"PROPOSE_OR_INSPECT_ONLY");
    assert.ok(q.meaning.length>5);
  });
}
for(const op of registry.candidate_operations){
  test("candidate operation has no authority: "+op.id,()=>{
    assert.equal(op.authority_ceiling,"NONE");
    assert.equal(op.execution,"NO_EXTERNAL_EFFECT");
    assert.equal(op.truth_promotion,"FORBIDDEN");
  });
}
test("original source cannot be silently changed in a converse view",()=>{
  const a=converseView(sample,registry);
  assert.equal(a.relation_id,"REQUIRED_BY");
  assert.equal(a.subject_id,sample.object_id);
  assert.equal(a.object_id,sample.subject_id);
  for (const p of ["source_ref","source_version","scope","valid_time","privacy_class","claim_status"]) {
    assert.equal(a[p],sample[p]);
  }
  assert.equal(a.new_evidence,false);
  assert.equal(a.external_effects,false);
});
test("double converse preserves typed original",()=>{
  const a=converseView(converseView(sample,registry),registry);
  assert.equal(a.relation_id,sample.relation_id);
  assert.equal(a.subject_id,sample.subject_id);
  assert.equal(a.object_id,sample.object_id);
  assert.equal(a.claim_status,sample.claim_status);
});
test("negation is a question, not evidence or falsehood",()=>{
  const a=negationQuestion(sample,registry);
  assert.equal(a.kind,"NEGATION_QUESTION_NOT_A_FACT");
  assert.equal(a.claim_status,"HYPOTHESIS");
  assert.equal(a.new_evidence,false);
  assert.equal(a.external_effects,false);
});
test("empty and missing fields fail closed",()=>{
  for(const bad of [{},null,{...sample,scope:""},{...sample,claim_status:undefined},{...sample,relation_id:"FAKE"}]){
    assert.throws(()=>validateSyntheticAssertion(bad,registry));
  }
});
test("private and unqualified sources fail closed",()=>{
  for(const bad of [
    {...sample,privacy_class:"PRIVATE"},
    {...sample,privacy_class:"UNKNOWN"},
    {...sample,source_ref:"file:///C:/secret"},
    {...sample,source_ref:"https://example.com/secret"},
    {...sample,claim_status:"PROVEN"},
    {...sample,valid_time:45}
  ]){
    assert.throws(()=>converseView(bad,registry));
    assert.throws(()=>negationQuestion(bad,registry));
  }
});
test("unrecognized object fields including simulated secrets never leak",()=>{
  const result=converseView({...sample,secret_password:"NOT_REAL_TEST_SECRET",other_user:"someone"},registry);
  assert.equal(JSON.stringify(result).includes("NOT_REAL_TEST_SECRET"),false);
  assert.equal("secret_password" in result,false);
  assert.equal("other_user" in result,false);
});
test("unknown remains unknown instead of false",()=>{
  const unknown={...sample,claim_status:"UNKNOWN"};
  assert.equal(converseView(unknown,registry).claim_status,"UNKNOWN");
  assert.equal(negationQuestion(unknown,registry).claim_status,"HYPOTHESIS");
});
test("synthetic-source only; no automatic account or device grant",()=>{
  const result=effectGate();
  assert.equal(result.status,"HELD");
  assert.equal(result.active_workers,0);
  assert.equal(result.external_effects,false);
});
test("inverse is not negation and undo is not converse",()=>{
  assert.ok(registry.candidate_operations.some(x=>x.id==="NEGATE_AS_QUESTION"));
  assert.ok(registry.candidate_operations.some(x=>x.id==="UNDO_EFFECT"));
  assert.ok(registry.candidate_operations.some(x=>x.id==="COMPENSATE_EFFECT"));
  assert.ok(registry.nonclaims.includes("UNDO_NE_CONVERSE"));
  assert.ok(registry.nonclaims.includes("NEGATION_CANDIDATE_NE_FALSEHOOD_PROOF"));
});
test("same fixture derives deterministic output",()=>{
  assert.deepEqual(converseView(sample,registry),converseView(sample,registry));
  assert.deepEqual(negationQuestion(sample,registry),negationQuestion(sample,registry));
});
test("receiver and potential media projections are not permissions",()=>{
  assert.match(registry.assertion_contract.middle_button,/PASS_THROUGH_DEFAULT/);
  assert.match(registry.assertion_contract.media_projection,/not an independent source/);
  assert.equal(registry.assertion_contract.device_or_provider,"NO_ACCESS_OR_AUTHORITY_GRANTED_BY_THIS_REGISTRY");
});
