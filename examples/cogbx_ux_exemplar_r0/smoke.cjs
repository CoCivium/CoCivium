const fs = require("node:fs");
const path = require("node:path");

const file = path.join(__dirname, "index.html");
const html = fs.readFileSync(file, "utf8");

function must(re, label) {
  if (!re.test(html)) throw new Error("missing: " + label);
}

function mustNot(re, label) {
  if (re.test(html)) throw new Error("forbidden: " + label);
}

must(/Content-Security-Policy/i, "CSP");
must(/default-src 'none'/i, "network-closed default CSP");
must(/Orb \+ Map/, "Orb + Map mode");
must(/>Text</, "Text mode");
must(/>Ambient</, "Ambient mode");
must(/>3D\+</, "3D+ optional mode");
must(/UNKNOWN/, "explicit unknown state");
must(/no single crown/i, "no-crown front door");
must(/Predictive shadow/i, "predictive shadow");
must(/SEND 0/, "zero-send UI");
must(/EXECUTE 0/, "zero-execute UI");
must(/same core state as the Orb\/Map view/i, "text recovery floor");
must(/prefers-reduced-motion/, "reduced-motion support");
must(/@media \(max-width:600px\)/, "narrow viewport support");
must(/aria-label="Projection controls"/, "projection control label");
must(/aria-pressed/, "toggle semantics");
must(/one durable work object/i, "durable work identity");
must(/Redundancy does not duplicate authority/i, "redundancy boundary");

mustNot(/\bfetch\s*\(/, "fetch");
mustNot(/XMLHttpRequest/, "XHR");
mustNot(/WebSocket/, "WebSocket");
mustNot(/EventSource/, "EventSource");
mustNot(/navigator\.sendBeacon/, "sendBeacon");
mustNot(/localStorage|sessionStorage|indexedDB/, "browser persistence");
mustNot(/document\.cookie/, "cookie mutation");
mustNot(/\.src\s*=\s*["']https?:/i, "remote script/image assignment");
mustNot(/<script[^>]+src=/i, "external script");
mustNot(/<link[^>]+href=/i, "external stylesheet");
mustNot(/<form\b/i, "form submission surface");

const scriptMatches = [...html.matchAll(/<script>([\s\S]*?)<\/script>/gi)];
if (scriptMatches.length !== 1) throw new Error("expected exactly one inline script");
new Function(scriptMatches[0][1]);

console.log("PASS_COGBX_UX_EXEMPLAR_R0");
