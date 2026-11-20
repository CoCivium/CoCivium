"use strict";
/**
 * CoMegaThesis three-view source parity canary.
 * Read-only local checks. No runtime/service/receiver qualification.
 * A GitHub CI PASS proves only source-level invariants for this candidate.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const pagePath = path.join(root, "docs/CoTheoryAll/candidates/comegathesis-reader-r0.html");
const graphPath = path.join(root, "ai/cotheoryall/comegathesis-relations-r0.json");
const deltaPath = path.join(root, "ai/cotheoryall/comegathesis-mythos-federation-delta-r0.json");
const workId = "CoTheoryAll::CoForgetToBecome::R0";
const sourceBlob = "d5a8f256183d0f8862d12c10861cac5e84a1bd6b";
const viewIds = ["view-reading", "view-map", "view-orb"];
const evidenceClass = "METAPHYSICAL_HYPOTHESIS";
let passes = 0;
function test(name, fn) { fn(); passes++; process.stdout.write("PASS " + name + "\n"); }
function occurrences(s, needle) { return s.split(needle).length - 1; }
function verifyGraph(graph, baseIds = []) {
  assert(Array.isArray(graph.nodes) && Array.isArray(graph.edges));
  const ids = new Set(baseIds);
  for (const node of graph.nodes) {
    assert(node.id && node.source, "node missing source");
    assert(!ids.has(node.id), "duplicate node " + node.id);
    ids.add(node.id);
  }
  for (const edge of graph.edges) {
    assert(ids.has(edge.from), "unknown from: " + edge.from);
    assert(ids.has(edge.to), "unknown to: " + edge.to);
    assert(edge.type && edge.source && edge.gate, "edge missing relation proof fields");
  }
  return ids;
}
const html = fs.readFileSync(pagePath, "utf8");
const base = JSON.parse(fs.readFileSync(graphPath, "utf8"));
const delta = JSON.parse(fs.readFileSync(deltaPath, "utf8"));

test("Three distinct visible projections are present once each", () => {
  for (const id of viewIds) assert.equal(occurrences(html, 'id="' + id + '"'), 1);
});
test("All views share exactly one WorkID", () => {
  assert.equal(occurrences(html, 'data-work-id="' + workId + '"'), 3);
});
test("All views share pinned source blob", () => {
  assert.equal(occurrences(html, 'data-source-blob="' + sourceBlob + '"'), 3);
});
test("All views preserve the speculative class", () => {
  assert.equal(occurrences(html, 'data-epistemic="' + evidenceClass + '"'), 3);
});
test("All views retain alternative and uncertainty, not only an attractive claim", () => {
  for (const id of viewIds) {
    const part = html.split('id="' + id + '"')[1].split("</article>")[0].toLowerCase();
    assert.match(part, /hypothes|metaphys/);
    assert.match(part, /alternative|emergence|ordinary physical|no chooser/);
  }
  assert.match(html, /independent reader acceptance remains <strong>not verified<\/strong>/i);
});
test("Read-only safe HTML has no executable JavaScript and has accessible fallbacks", () => {
  assert.match(html, /<meta http-equiv="Content-Security-Policy"/);
  assert.match(html, /script-src 'none'/);
  assert.doesNotMatch(html, /<script\b|onload=|onclick=|fetch\(/i);
  assert.match(html, /<a class="skip" href="#main">/);
  assert.match(html, /prefers-reduced-motion/);
  for (const id of ["main", "canary", "map", "orb", "proof"]) {
    assert.match(html, new RegExp('id="' + id + '"'));
  }
});
test("Base selected relation graph is valid", () => {
  const ids = verifyGraph(base);
  assert.equal(ids.size, 32);
  assert.equal(base.edges.length, 48);
});
test("Federation sidecar adds valid distinct, non-promoted nodes and edges", () => {
  assert.match(delta.state, /NOT_APPLIED_TO_BASE_GRAPH/);
  assert.equal(delta.base_graph_blob_sha, "644fb504234dff960e580b2da1bc0cbef9f12c3b");
  const ids = verifyGraph(base);
  verifyGraph(delta, ids);
  assert.equal(delta.nodes.length, 32);
  assert.equal(delta.edges.length, 62);
});
test("ET horizon stays voluntary and afterlife claims remain unverified", () => {
  const myth = fs.readFileSync(path.join(root, "docs/CoTheoryAll/candidates/COMYTHOS_COSEEDUNIFY_COFED_COIGC_R0_20261120.md"), "utf8");
  for (const term of ["CoETSharedHorizon+", "CoShroud+", "DEATH_NE_REQUIRED_JOURNEY", "SHARED_HORIZON_NE_SHARED_BELIEF"]) {
    assert(myth.includes(term), "missing mythos guard: " + term);
  }
  assert(delta.nodes.some(x => x.id === "etshared" && /OPTIONAL/.test(x.epistemic)));
  assert(delta.nodes.some(x => x.id === "shroud" && /METAPHOR/.test(x.epistemic)));
  assert(delta.nodes.some(x => x.id === "beyondhome" && /UNVERIFIED/.test(x.epistemic)));
  assert(delta.edges.some(x => x.from === "etshared" && x.to === "seedunify"));
  assert(delta.edges.some(x => x.from === "shroud" && x.to === "epistemic"));
  assert(delta.edges.some(x => x.from === "contactgate" && x.to === "guardian"));
});
test("No false promotion of CoBF, ET, G_d or Civ3", () => {
  assert.match(html, /CoBF\+<\/strong> remains an unresolved historical shorthand/);
  assert.match(html, /not a scientific finding/i);
  assert.match(html, /not evidence that future events physically pull the present/i);
  assert.match(html, /neither a theory nor a graph certifies a civilization/i);
});
process.stdout.write("SOURCE_ONLY_PASS " + passes + " tests; browser, device, receiver, canon and deployment remain UNVERIFIED\n");
