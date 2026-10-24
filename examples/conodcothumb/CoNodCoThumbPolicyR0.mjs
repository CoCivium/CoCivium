#!/usr/bin/env node
// CoNod+ / CoThumb+ context selector R0.
// PUBLIC-SAFE, SHADOW-ONLY. NO MOUSE DRIVER, CLIPBOARD, NETWORK, AUTOMATIC INPUT,
// SENDING, CREDENTIALS, BACKGROUND SCHEDULER OR EXTERNAL AUTHORITY.
const FORMAT = "CoNodCoThumb.ShadowPreview.R0";
const DEFAULT_ACTIONS = Object.freeze([
  "Next safe deed", "Copy safe pointer", "Find priors", "Challenge",
  "Map unknown", "Compare residual", "Replay history", "More"
]);
const NULL_STATES = new Set([
  "UNKNOWN", "NOT_OBSERVED", "OBSERVED_ABSENT", "EXPLICIT_DISCONNECTED",
  "INACCESSIBLE", "INTENTIONALLY_PRIVATE", "INCOMPATIBLE", "EXPIRED",
  "REJECTED", "NOT_MATERIALIZED", "PREDICTED_ONLY", "NOT_APPLICABLE"
]);
function result(primary, state="SHADOW_ONLY", extra={}) {
  return {
    format: FORMAT,
    label: "' CoNod+",
    tagline: "Preview one safe next step",
    primary,
    state,
    choices: ["Preview", "More", "Cancel"],
    deeper_options: DEFAULT_ACTIONS,
    effects: {network:0, send:0, execution:0, credential_access:0, persistence:0},
    authority: "NONE",
    gestures: {tap:"OPEN_LOCAL_PREVIEW", hold:"OPTIONAL_EXPAND_WHEN_DEVICE_VERIFIED",
      keyboard:"ACCESSIBLE_CONFIGURABLE_EQUIVALENT", escape:"CANCEL"},
    nonclaims: ["POINTER_NE_ACK","GESTURE_NE_AUTHORITY","COTHUMB_SOURCE_NE_PHYSICAL_BINDING",
      "NULL_NE_ZERO","RESIDUAL_NE_ENTITY","MODEL_OUTPUT_NE_SENTIENCE_PROOF",
      "PREVIEW_NE_EXECUTION","DESIGNED_NE_INTEGRATED"],
    ...extra
  };
}
export function preview(context={}) {
  if (!context || typeof context !== "object" || Array.isArray(context)) {
    return result("No safe context", "HOLD_INVALID_CONTEXT");
  }
  // No sniffing password/payment/editor contents or clipboard by default.
  if (context.sensitive || context.untrusted_surface ||
      ["PASSWORD","PAYMENT","AUTH","SECRET"].includes(context.field)) {
    return result("Unavailable here", "HOLD_PRIVACY",
      {choices:["Cancel"], deeper_options:[], capture_allowed:false});
  }
  if (["DEGRADING","SATURATED"].includes(context.pressure)) {
    return result("Preserve local handoff draft", "SHADOW_ONLY",
      {rationale:"Reduce work pressure; do not send, spawn or claim pickup"});
  }
  if (context.request === "BROADCAST") {
    return result("Prepare a local broadcast draft", "HOLD_EXTERNAL_EFFECT",
      {rationale:"Requires independently authorized, selected receivers and receipts"});
  }
  if (context.edge_state) {
    if (!NULL_STATES.has(context.edge_state)) {
      return result("Unknown edge classification", "HOLD_UNKNOWN_CLASS");
    }
    if (context.edge_state === "INTENTIONALLY_PRIVATE") {
      return result("Private relation withheld", "HOLD_PRIVACY",
        {choices:["Cancel"], deeper_options:[], capture_allowed:false,
          no_public_metadata:true});
    }
    if (context.edge_state === "OBSERVED_ABSENT" &&
        (!context.closed_world_scope || !context.observation_ref)) {
      return result("CoNull: unresolved, not absent", "HOLD_NEGATIVE_EVIDENCE");
    }
    return result("Inspect CoNull: " + context.edge_state, "SHADOW_ONLY",
      {rationale:"Missing, withheld and absent are different evidence states"});
  }
  if (context.measurement) {
    const m = context.measurement;
    const valid = m && typeof m==="object" &&
      typeof m.a==="number" && Number.isFinite(m.a) &&
      typeof m.b==="number" && Number.isFinite(m.b) &&
      typeof m.tolerance==="number" && Number.isFinite(m.tolerance) && m.tolerance>=0 &&
      typeof m.unit_a==="string" && m.unit_a && m.unit_a===m.unit_b &&
      typeof m.valid_time_a==="string" && m.valid_time_a && m.valid_time_a===m.valid_time_b &&
      typeof m.source_a==="string" && m.source_a && m.source_a!==m.source_b &&
      typeof m.source_b==="string" && m.source_b && m.independence_claim===true;
    if (!valid) return result("G_dRes: evidence gap", "HOLD_INCOMPARABLE",
      {rationale:"Require comparable units/times, distinct sources, a declared independence basis and tolerance"});
    return result("Inspect G_dRes candidate", "SHADOW_ONLY",
      {candidate_residual:Math.abs(m.a-m.b),
        exceeds_declared_tolerance:Math.abs(m.a-m.b)>m.tolerance,
        rationale:"A discrepancy, not a calibrated physical effect or proof of independence"});
  }
  if (context.topic === "SENTIENCE" || context.topic === "SANITY") {
    return result("Inspect assumptions and evidence gaps", "SHADOW_ONLY",
      {rationale:"No diagnosis, inference of sentience, or mental-state claim"});
  }
  if (context.selection_available === true) {
    return result("Preview local CoCopy capsule", "SHADOW_ONLY",
      {rationale:"Copying, export or transmission requires separate explicit action"});
  }
  if (context.claim_present === true) {
    return result("Find priors and counterexamples");
  }
  if (context.work_active === true) {
    return result("Continue one bounded safe deed");
  }
  return result("Choose one useful task");
}
function assert(label, ok, tests) {tests.push({label, status:ok?"PASS":"FAIL"});}
export function selftest() {
  const t=[];
  const normal=preview();
  assert("default label is compact CoNod",normal.label==="' CoNod+" && normal.primary==="Choose one useful task",t);
  assert("no automatic effects",Object.values(normal.effects).every(x=>x===0),t);
  assert("no authority on gesture",normal.authority==="NONE",t);
  assert("active work proposes one deed",preview({work_active:true}).primary==="Continue one bounded safe deed",t);
  assert("selection yields local capsule",preview({selection_available:true}).primary==="Preview local CoCopy capsule",t);
  assert("claim prompts priors",preview({claim_present:true}).primary==="Find priors and counterexamples",t);
  assert("saturation invokes local handoff",preview({pressure:"SATURATED"}).primary==="Preserve local handoff draft",t);
  assert("sensitive fields block capture",preview({field:"PASSWORD"}).state==="HOLD_PRIVACY",t);
  assert("unknown external surface blocks capture",preview({untrusted_surface:true}).state==="HOLD_PRIVACY",t);
  assert("broadcast never sends",preview({request:"BROADCAST"}).state==="HOLD_EXTERNAL_EFFECT",t);
  assert("private CoNull reveals no options",preview({edge_state:"INTENTIONALLY_PRIVATE"}).deeper_options.length===0,t);
  assert("unknown is not zero",preview({edge_state:"UNKNOWN"}).primary==="Inspect CoNull: UNKNOWN",t);
  assert("unsupported null is held",preview({edge_state:"INVENTED_NULL"}).state==="HOLD_UNKNOWN_CLASS",t);
  assert("absence needs closed-world ref",preview({edge_state:"OBSERVED_ABSENT"}).state==="HOLD_NEGATIVE_EVIDENCE",t);
  assert("scoped absence can be inspected",preview({edge_state:"OBSERVED_ABSENT",closed_world_scope:"scope:test",observation_ref:"obs:test"}).state==="SHADOW_ONLY",t);
  assert("discrepancy rejects equal sources",preview({measurement:{a:1,b:3,tolerance:1,unit_a:"m",unit_b:"m",valid_time_a:"t",valid_time_b:"t",source_a:"s",source_b:"s",independence_claim:true}}).state==="HOLD_INCOMPARABLE",t);
  assert("discrepancy rejects mismatched units",preview({measurement:{a:1,b:3,tolerance:1,unit_a:"m",unit_b:"s",valid_time_a:"t",valid_time_b:"t",source_a:"s1",source_b:"s2",independence_claim:true}}).state==="HOLD_INCOMPARABLE",t);
  assert("qualified discrepancy yields bounded candidate",preview({measurement:{a:1,b:3,tolerance:1,unit_a:"m",unit_b:"m",valid_time_a:"t",valid_time_b:"t",source_a:"s1",source_b:"s2",independence_claim:true}}).candidate_residual===2,t);
  assert("sentience is evidence question",preview({topic:"SENTIENCE"}).primary==="Inspect assumptions and evidence gaps",t);
  assert("bad context fails closed",preview(null).state==="HOLD_INVALID_CONTEXT",t);
  assert("no hidden input injection",normal.gestures.tap==="OPEN_LOCAL_PREVIEW" && !("type" in normal.gestures),t);
  assert("preview mode includes exit",normal.choices.includes("Cancel") && normal.gestures.escape==="CANCEL",t);
  return {format:FORMAT,test_class:"SYNTHETIC_POLICY_FIXTURE",passed:t.filter(x=>x.status==="PASS").length,
    total:t.length,tests:t,source_scope:"LOCAL_POLICY_ONLY_NO_MOUSE_RUNTIME",nonclaims:normal.nonclaims};
}
if (process.argv[1] && /CoNodCoThumbPolicyR0\.mjs$/.test(process.argv[1])) {
  const mode=process.argv[2]||"--selftest";
  const out=mode==="--preview"?preview():selftest();
  console.log(JSON.stringify(out,null,2));
  if (mode==="--selftest" && out.passed!==out.total) process.exitCode=1;
}
