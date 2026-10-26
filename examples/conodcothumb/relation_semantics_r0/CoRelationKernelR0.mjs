// CoMiddle+ R0, pure, zero-effect, synthetic-source typed relation views.
// This is NOT a mouse hook, provider adapter, execution authority, or inference engine.
const FIELDS = [
  "relation_id", "subject_id", "object_id", "source_ref", "source_version",
  "scope", "valid_time", "privacy_class", "claim_status"
];
function boundedString(v, name, max = 512) {
  if (typeof v !== "string" || !v.trim() || v.length > max) {
    throw new TypeError("HELD_INVALID_" + name.toUpperCase());
  }
  return v;
}
export function validateSyntheticAssertion(input, registry) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new TypeError("HELD_INVALID_ASSERTION");
  }
  if (!registry || registry.schema !== "CoCivium.CoMiddle.TypedRelations.R0") {
    throw new TypeError("HELD_UNKNOWN_REGISTRY");
  }
  const safe = {};
  for (const field of FIELDS) safe[field] = boundedString(input[field], field);
  if (safe.privacy_class !== "PUBLIC_SYNTHETIC") {
    throw new Error("HELD_PRIVATE_OR_UNCLASSIFIED_SOURCE");
  }
  if (!safe.source_ref.startsWith("synthetic://")) {
    throw new Error("HELD_SOURCE_MUST_BE_SYNTHETIC_FOR_R0");
  }
  if (!registry.assertion_contract.allowed_status.includes(safe.claim_status)) {
    throw new Error("HELD_UNKNOWN_EPISTEMIC_CLASS");
  }
  if (!registry.relation_types.some(r => r.id === safe.relation_id)) {
    throw new Error("HELD_UNKNOWN_RELATION");
  }
  return safe; // Whitelist. Extra input fields, including possible secrets, are discarded.
}
export function converseView(input, registry) {
  const a = validateSyntheticAssertion(input, registry);
  const r = registry.relation_types.find(t => t.id === a.relation_id);
  return {
    relation_id: r.counterpart,
    subject_id: a.object_id,
    object_id: a.subject_id,
    source_ref: a.source_ref,
    source_version: a.source_version,
    scope: a.scope,
    valid_time: a.valid_time,
    privacy_class: a.privacy_class,
    claim_status: a.claim_status,
    derived_view: "CONVERSE_OF_SAME_SOURCE_ASSERTION",
    original_relation_id: a.relation_id,
    new_evidence: false,
    authority_ceiling: "NONE",
    external_effects: false
  };
}
export function negationQuestion(input, registry) {
  const a = validateSyntheticAssertion(input, registry);
  return {
    kind: "NEGATION_QUESTION_NOT_A_FACT",
    subject_id: a.subject_id,
    relation_id: a.relation_id,
    object_id: a.object_id,
    source_ref: a.source_ref,
    source_version: a.source_version,
    scope: a.scope,
    valid_time: a.valid_time,
    privacy_class: a.privacy_class,
    claim_status: "HYPOTHESIS",
    prompt: "What would falsify the scoped relation between these two IDs?",
    new_evidence: false,
    authority_ceiling: "NONE",
    external_effects: false
  };
}
export function effectGate() {
  return {
    status: "HELD",
    reason: "NO_NATIVE_RUNTIME_OR_EXECUTION_AUTHORITY",
    external_effects: false,
    active_workers: 0
  };
}
