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
must(/One synthetic work object, shown in every projection/i, "stable synthetic identity across projections");
must(/Redundancy does not duplicate authority/i, "redundancy boundary");
must(/STATIC DEMONSTRATION · NOT LIVE/, "prominent example-only status");
must(/CoGbx\.org hosting, independent peer paths, and X2 native runtime remain unverified/, "unverified external states");
must(/1 synthetic object/, "synthetic durable object");
must(/3 illustrative/, "illustrative embodiments");
must(/1 simulated held state/, "simulated remote unknown");
must(/currentness<\/span><span>synthetic fixture/, "no fake live currentness");
must(/recovery<\/span><span>not live-tested/, "not-yet-restored label");
must(/crown risk<\/span><span>not measured/, "no unverified crown-risk score");
must(/These are proposed alternatives, not verified independent failover paths/, "candidate independence boundary");
must(/source and evidence pointers; not an active receiver/, "unverified receiver boundary");
must(/--forest-bg:#17372c/, "restrained green optionality banner");
must(/role="note"/, "semantic notice");
must(/id="throughput-title"/, "qualified throughput context");
must(/CoSpeedo\+ \| Throughput evidence/, "qualified capacity explainer");
must(/Proven peak<\/span><span>NOT MEASURED/, "no fabricated peak");
must(/Sustained baseline<\/span><span>NOT MEASURED/, "no fabricated sustainable baseline");
must(/Useful outcomes \/ human-time<\/span><span>NOT MEASURED/, "no fabricated human-time throughput");
must(/Available extra capacity<\/span><span>UNQUALIFIED/, "no inferred resource capacity");
must(/New devices and agents are inventory candidates until independently qualified/, "inventory is not capacity");

mustNot(/<span>recovery<\/span><span>available<\/span>/, "false live recovery state");
mustNot(/<span>crown risk<\/span><span>low<\/span>/, "false measured crown risk");
mustNot(/<span>currentness<\/span><span>local current<\/span>/, "false live currentness");


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
