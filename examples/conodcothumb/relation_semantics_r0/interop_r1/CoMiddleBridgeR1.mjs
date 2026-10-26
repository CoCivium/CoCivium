// CoMiddle+ R0 -> R2 evidence-preserving cross-schema review canary.
// NO mouse hooks, credentials, external sends, model calls or automatic migration.
import { validateSyntheticAssertion } from '../CoRelationKernelR0.mjs';

export const SCHEMA = 'CoCivium.CoMiddle.CrossSchemaBridge.R1';
export const SOURCE_PINS = Object.freeze({
  r0_registry_blob: '3ad1d048a864df9cb6ed364faebf40614d96edf1',
  r0_kernel_blob: '67b3bd7b0d534e919730e55684dc4efc8290d98a',
  r2_kernel_blob: '15fb5d3065e147c3615d05e449d39de47abd4ef6',
  r1_human_preview_blob: '16544a43f1ce2dc3495555b3fed066988d08f502'
});
export const NAME_MATCH = Object.freeze({
  CITES:'CITED_BY', CITED_BY:'CITES',
  PRECEDES:'FOLLOWS', FOLLOWS:'PRECEDES',
  SUPERSEDES:'SUPERSEDED_BY', SUPERSEDED_BY:'SUPERSEDES'
});
export const ALIAS_CANDIDATES = Object.freeze({
  DEPENDS_ON: Object.freeze({r0_converse:'REQUIRED_BY',r2_id:'DEPENDS_ON',r2_converse:'IS_DEPENDENCY_OF',type_guard:'WorkObject -> WorkObject'}),
  REQUIRED_BY: Object.freeze({r0_converse:'DEPENDS_ON',r2_id:'IS_DEPENDENCY_OF',r2_converse:'DEPENDS_ON',type_guard:'WorkObject -> WorkObject'}),
  CONTAINS: Object.freeze({r0_converse:'PART_OF',r2_id:'CONTAINS',r2_converse:'CONTAINED_BY',type_guard:'Container -> Member'}),
  PART_OF: Object.freeze({r0_converse:'CONTAINS',r2_id:'CONTAINED_BY',r2_converse:'CONTAINS',type_guard:'Member -> Container'})
});
export const UNQUALIFIED_NEAR_MATCHES = Object.freeze({
  DERIVED_FROM:'DERIVES_FROM', SOURCE_FOR:'IS_SOURCE_FOR',
  RELATES_TO:'RELATED_TO', CONFLICT_CANDIDATE_WITH:'CONTRADICTS',
  SUPPORTS:'HAS_EVIDENCE', SUPPORTED_BY:'EVIDENCE_FOR'
});
export const NO_EFFECTS = Object.freeze({device:0,network:0,send:0,clipboard:0,worker:0,mutation:0});
const nonclaims = Object.freeze([
  'SOURCE_VIEW_NE_VERIFIED_FACT','NAME_MATCH_NE_SEMANTIC_EQUIVALENCE',
  'ALIAS_CANDIDATE_NE_APPROVED_MIGRATION','CONVERSE_NE_NEGATION',
  'CONVERSE_NE_UNDO','ROUTING_NE_DELIVERY','GLYPH_NE_AUTHORITY',
  'GITHUB_SOURCE_NE_X2_RUNTIME','POINTER_NE_RECEIVER_ACK'
]);
function withheld(status) {
  return {schema:SCHEMA,status,source:null,relation:null,target_candidate:null,
    authority:'NONE',effects:{...NO_EFFECTS},receiver_ack:false,
    nonclaims:[...nonclaims]};
}
/** A documentary preview only; never returns an R2 executable packet. */
export function reviewSyntheticCrosswalk(input, r0Registry) {
  let a;
  try { a=validateSyntheticAssertion(input,r0Registry); }
  catch { return withheld('HELD_SOURCE_PRIVACY_OR_SCHEMA'); }
  if (r0Registry.version !== '2026-10-26.R0' || !/^synthetic:\/\/[A-Za-z0-9][A-Za-z0-9/_-]{0,100}$/.test(a.source_ref)) return withheld('HELD_UNQUALIFIED_PINNED_SOURCE');
  const r0=r0Registry.relation_types.find(r=>r.id===a.relation_id);
  if (!r0) return withheld('HELD_UNKNOWN_RELATION');
  let status='HELD_NOT_MAPPED';
  let candidate=null;
  if (Object.hasOwn(NAME_MATCH,r0.id)) {
    if (NAME_MATCH[r0.id] !== r0.counterpart) return withheld('HELD_SOURCE_DRIFT');
    status='SHADOW_NAME_MATCH_ONLY';
    candidate={relation_id:r0.id,converse_id:NAME_MATCH[r0.id],kind:'SAME_NAME_NOT_VERIFIED_EQUIVALENCE'};
  } else if (Object.hasOwn(ALIAS_CANDIDATES,r0.id)) {
    const entry=ALIAS_CANDIDATES[r0.id];
    if (entry.r0_converse !== r0.counterpart || (r0.subject_type+' -> '+r0.object_type) !== entry.type_guard) return withheld('HELD_SOURCE_DRIFT');
    status='HELD_EXPLICIT_ALIAS_REVIEW';
    candidate={relation_id:entry.r2_id,converse_id:entry.r2_converse,kind:'QUALIFIED_ALIAS_CANDIDATE_ONLY',type_guard:entry.type_guard};
  } else if (Object.hasOwn(UNQUALIFIED_NEAR_MATCHES,r0.id)) {
    status='HELD_SEMANTIC_NON_EQUIVALENCE_RISK';
    // Potentially misleading target IDs deliberately withheld.
  }
  return {schema:SCHEMA,status,
    source:{schema:r0Registry.schema,version:r0Registry.version,relation_id:r0.id,
      counterpart:r0.counterpart,subject_id:a.subject_id,object_id:a.object_id,
      subject_type:r0.subject_type,object_type:r0.object_type,
      source_ref:a.source_ref,source_version:a.source_version,
      scope:a.scope,valid_time:a.valid_time,privacy_class:a.privacy_class,claim_status:a.claim_status},
    relation:{original:r0.id,r0_converse:r0.counterpart},target_candidate:candidate,
    target_schema:'CoCivium.CoMiddle.RelationInverse.R2',
    target_executable:false,source_bytes_verified_by_this_call:false,
    requires_human_semantic_approval:true,requires_r2_source_binding:true,
    authority:'NONE',effects:{...NO_EFFECTS},receiver_ack:false,
    nonclaims:[...nonclaims]};
}
export function summarizeBridge() {
  return {schema:SCHEMA,source_pins:{...SOURCE_PINS},same_name_ids:Object.keys(NAME_MATCH).length,
    alias_candidate_ids:Object.keys(ALIAS_CANDIDATES).length,
    blocked_near_matches:Object.keys(UNQUALIFIED_NEAR_MATCHES).length,
    target_executable:false,authority:'NONE',effects:{...NO_EFFECTS}};
}
