'use strict';
// CoGlyphRail R0: read-only, zero-network, reproducible source checks.
// Pure policy/HTML tests only. No OS mouse, X2, delivery, account, or runtime claims.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const sourcePath = path.join(root, 'CoGlyphRail_R0.html');
const catalogPath = path.join(root, 'CoRelKernel_R0.json');
const html = fs.readFileSync(sourcePath, 'utf8');
const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
const results = [];
function check(name, fn) {
  try { fn(); results.push({ name, status: 'PASS' }); }
  catch (error) { results.push({ name, status: 'FAIL', error: String(error.message || error) }); }
}
const relations = new Map(catalog.relations.map(r => [r.id, r]));
check('candidate-only schema, 132 predicates', () => {
  assert.equal(catalog.format, 'CoRelKernel.CandidateVocabulary.R0');
  assert.equal(catalog.state, 'OFFLINE_SHADOW_CANDIDATE');
  assert.equal(relations.size, 132);
  assert.equal(catalog.relations.length, 132);
  assert.ok(catalog.relations.every(r => r.claim_status === 'NOT_ASSERTED'));
});
check('converse and typed endpoints', () => {
  for (const r of relations.values()) {
    const inverse = relations.get(r.converse);
    assert.ok(inverse, 'missing ' + r.converse);
    assert.equal(inverse.converse, r.id);
    if (r.converse_kind === 'DIRECTED_CONVERSE') {
      assert.equal(r.domain, inverse.range);
      assert.equal(r.range, inverse.domain);
    } else {
      assert.equal(r.converse_kind, 'SYMMETRIC');
      assert.equal(r.converse, r.id);
    }
  }
  assert.equal(catalog.relations.filter(r => r.converse_kind === 'DIRECTED_CONVERSE').length, 120);
  assert.equal(catalog.relations.filter(r => r.converse_kind === 'SYMMETRIC').length, 12);
});
check('bounded candidate combinatorics', () => {
  assert.equal(catalog.contexts.length, 12);
  assert.equal(catalog.lenses.length, 12);
  assert.equal(catalog.questions.length, 17);
  assert.equal(catalog.combination_ceiling_before_type_filter, 132 * 12 * 12 * 17);
});
check('sensitive and unknown contexts deny preview', () => {
  for (const id of ['sensitive', 'unknown']) {
    assert.equal(catalog.contexts.find(c => c.id === id).guard, 'BLOCK_ALL');
  }
});
check('authority and automatic effects remain zero', () => {
  assert.equal(catalog.output_contract.authority, 'NONE');
  assert.equal(catalog.output_contract.auto_sends, 0);
  assert.equal(catalog.output_contract.auto_spawns, 0);
});
check('relation rails preserve evidence boundaries', () => {
  for (const gate of ['SOURCE_NE_RUNTIME', 'GESTURE_NE_AUTHORITY', 'CONVERSE_NE_NEGATION', 'RANK_NE_PERMISSION']) {
    assert.ok(catalog.rails.includes(gate), gate);
  }
});
check('offline CSP and no browser network/storage APIs', () => {
  assert.ok(html.includes("default-src 'none'"));
  assert.ok(html.includes("connect-src 'none'"));
  for (const forbidden of [/\bfetch\s*\(/i, /\bXMLHttpRequest\b/i, /\bWebSocket\b/i, /\blocalStorage\b/i, /\bsessionStorage\b/i, /\bgetUserMedia\s*\(/i, /\bSendInput\b/i]) {
    assert.ok(!forbidden.test(html), 'forbidden source pattern: ' + forbidden);
  }
});
const script = html.match(/<script>([\s\S]*?)<\/script>/);
check('exactly one inline source script', () => {
  assert.ok(script);
  assert.equal((html.match(/<script>/g) || []).length, 1);
});
let ctx = null;
if (script) {
  ctx = vm.createContext({});
  try { vm.runInContext(script[1].replace(/setup\(\);\s*$/, ''), ctx, { timeout: 1500 }); }
  catch (error) { results.push({ name: 'load pure JS in isolated VM', status: 'FAIL', error: String(error) }); }
}
if (ctx && typeof vm.runInContext('typeof CATALOG', ctx) === 'string') {
  check('embedded catalogue equals standalone exact data', () => {
    const embedded = vm.runInContext('CATALOG', ctx, { timeout: 1500 });
    assert.deepEqual(JSON.parse(JSON.stringify(embedded)), catalog);
  });
  const jsCheck = (name, expr) => check(name, () => assert.ok(vm.runInContext(expr, ctx, { timeout: 1500 })));
  jsCheck('default expression', "expression()==='A is part of B'");
  jsCheck('converse is same qualified edge, not causal reversal', "(state.lens='CONVERSE',expression()==='B has part A')");
  jsCheck('negation stays unasserted', "(state.lens='NEGATION',expression().includes('NOT established'))");
  jsCheck('complement requires a closed universe', "(state.lens='COMPLEMENT',expression().includes('closed universe'))");
  jsCheck('preview has no authority, sends or fabricated claims', "(state.lens='DIRECT',proposal().authority==='NONE' && proposal().effects.send===0 && proposal().relation.status==='NOT_ASSERTED')");
  jsCheck('no imaginary evidence or receiver readproof', "proposal().receiver_readproof===null && proposal().sources.length===0");
  jsCheck('sensitive context fails closed', "(state.context='sensitive',proposal()===null)");
  jsCheck('unknown context fails closed', "(state.context='unknown',proposal()===null)");
  jsCheck('explicitly selected writing context previews', "(state.context='writing',proposal()!==null)");
  jsCheck('bounded relation filter', "(state.filter='authoriz',relationList().length>0 && relationList().length<132)");
  jsCheck('typed causality converse', "REL.get('causes').converse==='caused_by' && REL.get('caused_by').converse==='causes'");
}
const summary = {
  format: 'CoGlyphRail.CISourcePolicy.R0',
  status: results.every(r => r.status === 'PASS') ? 'PASS' : 'FAIL',
  passed: results.filter(r => r.status === 'PASS').length,
  total: results.length,
  source_sha256: Object.fromEntries([['CoGlyphRail_R0.html', sourcePath], ['CoRelKernel_R0.json', catalogPath]].map(([key, file]) => [key, crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')])),
  scope: 'STATIC_AND_ISOLATED_NODE_VM_ONLY',
  nonclaims: ['NO_BROWSER_QA_IN_CI', 'NO_X2_PHYSICAL_INPUT', 'NO_NATIVE_MOUSE_MAPPING', 'NO_REMOTE_DELIVERY', 'NO_COSTEAD_ACK', 'NO_HUMAN_ACCEPTANCE'],
  results
};
console.log(JSON.stringify(summary, null, 2));
if (summary.status !== 'PASS') process.exitCode = 1;
