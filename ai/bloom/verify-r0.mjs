#!/usr/bin/env node
/**
 * CoAllBloom R0 read-only structural and exact Git-blob donor verifier.
 * Node.js 22, no dependencies, no network, no file mutations.
 *
 * This is a machine/source contract check, NOT a semantic truth detector,
 * independent review, AI adapter test or activated CoOrbWare service.
 */
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(dirname, '../..');
const manifest = JSON.parse(fs.readFileSync(path.join(dirname, 'coallbloom-r0.json'), 'utf8'));
const report = [];
const check = (name, ok) => report.push({ test: name, status: ok ? 'PASS' : 'FAIL' });
const hasUnique = arr => new Set(arr).size === arr.length;
const read = p => fs.readFileSync(path.join(root, p));
const gitBlobSha = bytes => crypto.createHash('sha1')
  .update(Buffer.from('blob ' + bytes.length + '\0'))
  .update(bytes)
  .digest('hex');

check('schema recognized', manifest.schema === 'CoCivium.CoAllBloom.TypedSemanticOptionality.R0');
check('review only, zero workers', manifest.state.includes('ZERO_ACTIVE_WORKERS'));
check('no direct effect', manifest.execution_contract.external_effects === false);
check('no semantic authority escalation', manifest.execution_contract.authority_upgrade_by_semantic_operator === false);
check('parent budget shared', manifest.execution_contract.parent_budget_shared === true);
check('selector cap 32', manifest.execution_contract.selector_cap === 32);
check('sample cap 128', manifest.execution_contract.sample_cap === 128);
check('turtle depth 2', manifest.execution_contract.review_depth_cap === 2);
check('turtle rounds 2', manifest.execution_contract.review_round_cap === 2);
check('no real model qualification', manifest.execution_contract.live_model_adapters_verified_by_this_contract === 0);
check('no real device qualification', manifest.execution_contract.live_devices_qualified_by_this_contract === 0);
check('source pin count', manifest.donors.length === 12);
check('donors unique by path', hasUnique(manifest.donors.map(x => x.path)));
check('operators >= 24', manifest.operators.length >= 24);
check('operator identities unique', hasUnique(manifest.operators.map(x => x.id)));
check('every operator has glyph, meaning and gate', manifest.operators.every(x => x.glyph && x.meaning && x.gate));
check('nine nonempty axes', manifest.axes.length === 9 && manifest.axes.every(x => x.values?.length > 0));
check('axes unique', hasUnique(manifest.axes.map(x => x.id)));
check('domain classes >= 12', manifest.domains.length >= 12);
check('domain labels unique', hasUnique(manifest.domains.map(x => x.type)));
check('epistemic classes explicit', ['OBSERVED','HYPOTHESIS','SYMBOLIC','UNKNOWN','COUNTERFACTUAL'].every(x => manifest.epistemic_classes.includes(x)));
check('open-world unknown not false', manifest.semantics.open_world.includes('UNKNOWN'));
check('NOT is not truth promotion', manifest.semantics.negation.includes('never proof'));
check('inverse not symmetric by default', manifest.semantics.inversion.includes('does not simply imply'));
check('composition requires rules', manifest.semantics.composition.includes('licensed composition rule'));
check('no spontaneous ET claim', manifest.invariants.includes('ET_HYPOTHESIS_NE_ET_CONTACT'));
check('no spontaneous G_d proof', manifest.invariants.includes('SPIRITUAL_SYMBOL_NE_DETECTED_ENTITY'));
check('AI role not account ownership', manifest.invariants.includes('AI_ROLE_NE_PERSONHOOD_OR_ACCOUNT_OWNERSHIP'));
check('unknown absence stays unknown', manifest.invariants.includes('ABSENCE_NE_PROVEN_WITHOUT_CLOSED_WORLD_SCOPE'));
check('no receiver inference', manifest.invariants.includes('NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF'));
check('no evergreen daemon assumed', manifest.onramps.ai_ia.evergreen.includes('no permanent background process'));
check('AI/IA revocation stage', manifest.onramps.ai_ia.states.includes('REVOKED_OR_RETIRED'));
check('six human progressive levels', manifest.onramps.human.levels.length === 6);
check('synthetic demonstration examples', manifest.examples.length >= 6 && manifest.examples.every(x => x.nonclaim));
check('ET fixture bounded', manifest.examples.find(x => x.id === 'EX2')?.nonclaim === 'NO_ET_DETECTION');
check('G_d fixture symbolic', manifest.examples.find(x => x.id === 'EX1')?.epistemic === 'SYMBOLIC');
check('source class remains source', manifest.examples.find(x => x.id === 'EX5')?.nonclaim === 'NOT_X2_RUNTIME');
check('logical quantity not runtime', manifest.logical_count_scope.includes('ZERO_MATERIALIZATION'));
const rawCount = manifest.axes.reduce((n, x) => n * BigInt(x.values.length), 1n);
check('raw axes product reproducible', String(rawCount) === manifest.logical_cartesian_address_count);
const humanDoc = read('docs/Architecture/COALLBLOOM_SEMANTIC_OPTIONALITY_R0_20261026.md').toString('utf8');
check('human source and machine twin crosslinked', humanDoc.includes('ai/bloom/coallbloom-r0.json') && humanDoc.includes('123,002,880'));
check('human differentiates source from runtime', humanDoc.includes('0 new workers') && humanDoc.includes('HELD'));
for (const donor of manifest.donors) {
  let ok = false;
  try {
    const normalized = path.posix.normalize(donor.path);
    ok = normalized === donor.path &&
         !normalized.startsWith('../') &&
         /^([a-f0-9]{40})$/.test(donor.blob_sha) &&
         gitBlobSha(read(normalized)) === donor.blob_sha;
  } catch (_) { ok = false; }
  check('pinned donor exact Git blob: ' + donor.id, ok);
}
for(const e of manifest.examples) {
  check('example typed: ' + e.id, manifest.epistemic_classes.includes(e.epistemic) &&
        manifest.domains.some(d => d.type === e.domain) &&
        manifest.operators.some(op => op.id === e.operator));
}
const fails = report.filter(x => x.status === 'FAIL');
process.stdout.write(JSON.stringify({
  schema: 'CoAllBloom.StructuralProof.R0',
  source: 'ai/bloom/coallbloom-r0.json',
  checks: report.length,
  passed: report.length - fails.length,
  failed: fails.length,
  failure_names: fails.map(x => x.test),
  scope: 'STATIC_LOCAL_SOURCE_AND_EXACT_GIT_BLOBS_ONLY',
  workers_started: 0,
  network_calls: 0,
  user_acceptance: 'HELD',
  device_runtime: 'HELD'
}, null, 2) + '\n');
if(fails.length) process.exitCode = 1;
