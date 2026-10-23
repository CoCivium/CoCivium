"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const failures = [];
const checks = [];

function check(name, fn) {
  checks.push(name);
  try { fn(); process.stdout.write("PASS " + name + "\n"); }
  catch (err) {
    failures.push({name, error: err.message});
    process.stdout.write("FAIL " + name + ": " + err.message + "\n");
  }
}

check("CSP forbids network connections", () => {
  assert.match(html, /connect-src 'none'/);
  assert.match(html, /default-src 'none'/);
});

check("no network or background APIs", () => {
  assert(!/\bfetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|serviceWorker|RTCPeerConnection/.test(html));
});

check("no persistent browser storage", () => {
  assert(!/localStorage|sessionStorage|indexedDB/.test(html));
});

check("exact RAW surface exists", () => {
  assert(html.includes('id="raw"'));
  assert(html.includes('id="rawMirror"'));
  assert(html.includes("raw_exact:rawBefore"));
});

check("explicit decisions only", () => {
  assert(html.includes('id="accept"'));
  assert(html.includes('id="reject"'));
  assert(html.includes('addEventListener("click",()=>decide("ACCEPT"))'));
  assert(html.includes('addEventListener("click",()=>decide("REJECT"))'));
});

check("no global keyboard automation", () => {
  assert(!/addEventListener\s*\(\s*["']key(?:down|up|press)/.test(html));
});

check("zero outward effect receipt fields", () => {
  for (const fragment of [
    "network_calls:0",
    "provider_calls:0",
    "external_mutations:0",
    "messages_sent:0",
    "accounts_changed:0"
  ]) assert(html.includes(fragment), fragment);
});

check("required predictive rails present", () => {
  for (const rail of [
    "PREDICTED_NE_TYPED",
    "PREDICTED_NE_AUTHORIZED",
    "PRECOMPUTED_NE_EXECUTED",
    "REWRITE_NE_REPLACEMENT_OF_RAW",
    "PROJECTION_NE_SOURCE"
  ]) assert(html.includes(rail), rail);
});

check("CoMap lineage nodes present", () => {
  for (const id of ["nRaw","nAck","nShadow","nDecision","nReceipt","nEffect"]) {
    assert(html.includes('id="' + id + '"'), id);
  }
});

check("CoQuanta receipt schema present", () => {
  assert(html.includes("CoQuanta.PredictiveInput.R0"));
  assert(html.includes("CoPredictiveInput.LocalReceiptLedger.R0"));
});

check("counterfactual latency is not asserted by default", () => {
  assert(html.includes("estimated_latency_saved_ms:estimated"));
  assert(html.includes("?baseline:null"));
  assert(html.includes("ESTIMATED_LATENCY_NE_MEASURED_COUNTERFACTUAL"));
});

check("deterministic local continuation rules include core lanes", () => {
  const start = html.indexOf("const continuationRules =");
  const end = html.indexOf("];", start);
  assert(start >= 0 && end > start);
  const source = html.slice(start + "const continuationRules =".length, end + 1);
  const rules = vm.runInNewContext("(" + source + ")");
  assert(Array.isArray(rules));
  assert(rules.some(r => r.match.includes("publish")));
  assert(rules.some(r => r.match.includes("virtual session")));
  assert(rules.some(r => r.match.includes("comap")));
  assert(rules.some(r => r.match.includes("privacy")));
});

check("download is explicit local action", () => {
  assert(html.includes('id="download"'));
  assert(html.includes("URL.createObjectURL"));
  assert(html.includes("EXPLICIT_LOCAL_EXPORT"));
});

const report = {
  schema: "CoPredictiveInput.PublicSmoke.R0",
  total: checks.length,
  passed: checks.length - failures.length,
  failed: failures.length,
  failures,
  nonclaims: [
    "STATIC_SMOKE_NE_USER_ACCEPTANCE",
    "LOCAL_RULES_NE_MODEL_PREDICTION",
    "BROWSER_CANARY_NE_DESKTOP_INTEGRATION",
    "ZERO_NETWORK_SOURCE_CHECK_NE_UNIVERSAL_BROWSER_PROOF"
  ]
};
process.stdout.write(JSON.stringify(report) + "\n");
if (failures.length) process.exitCode = 1;
