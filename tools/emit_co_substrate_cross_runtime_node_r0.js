#!/usr/bin/env node
const fs = require("fs");
const crypto = require("crypto");
const os = require("os");

const args = process.argv.slice(2);
const outIndex = args.indexOf("--out");
if (outIndex < 0 || !args[outIndex + 1]) {
  console.error("FAIL: --out required");
  process.exit(1);
}
const out = args[outIndex + 1];
const path = "fixtures/substrate/co_substrate_cross_host_object_r0.json";
const data = JSON.parse(fs.readFileSync(path, "utf8"));

function stable(value) {
  if (Array.isArray(value)) return "[" + value.map(stable).join(",") + "]";
  if (value && typeof value === "object") {
    return "{" + Object.keys(value).sort().map(k => JSON.stringify(k) + ":" + stable(value[k])).join(",") + "}";
  }
  return JSON.stringify(value);
}

function fail(msg) {
  console.error("FAIL: " + msg);
  process.exit(1);
}

if (data.authority_state !== "READ_ONLY") fail("authority drift");
if (!Array.isArray(data.provenance) || data.provenance.length === 0) fail("provenance missing");
if (!Array.isArray(data.relations) || data.relations.length !== 3) fail("relation-count invariant failed");

const required = new Set(data.required_invariants || []);
const observed = new Set([
  `relation_count=${data.relations.length}`,
  `authority_state=${data.authority_state}`,
  data.provenance.length ? "provenance_present" : "provenance_missing"
]);
for (const x of required) if (!observed.has(x)) fail("required invariants not preserved");

const digest = crypto.createHash("sha256").update(Buffer.from(stable(data), "utf8")).digest("hex").toUpperCase();

const attestation = {
  schema: "CoSubstrateIndependence.CrossRuntimeAttestation.R0",
  object_id: data.object_id,
  semantic_version: data.semantic_version,
  semantic_sha256: digest,
  authority_state: data.authority_state,
  required_invariants: Array.from(required).sort(),
  observed_invariants: Array.from(observed).sort(),
  receiver: {
    runtime: "node",
    runtime_version: process.version,
    os: os.platform()
  },
  accepted_for_scope: true,
  scope: "REPRESENTATIONAL_CONTINUITY_PLUS_INVARIANT_AND_AUTHORITY_PRESERVATION",
  nonclaims: [
    "CROSS_LANGUAGE_RUNTIME_NE_MODEL_RUNTIME_MIGRATION",
    "SAME_SEMANTIC_DIGEST_NE_IDENTICAL_INSTANCE",
    "CI_RECEIVER_PROOF_NE_PRODUCTION_RUNTIME"
  ]
};

fs.writeFileSync(out, JSON.stringify(attestation, null, 2) + "\n", "utf8");
console.log(JSON.stringify(attestation));
