#!/usr/bin/env node
// Independent byte-bound checkpoint verifier; Node built-ins only.
// Does not execute any described experiment, subprocess, network call, or model.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const NAMES = [
  'schema','spec_sha256','capacity','next_index','revision',
  'parent_checkpoint_sha256','effect_ceiling','actual_executed_experiments',
  'actual_live_sessions','checkpoint_sha256'
];
const sha256 = (b) => createHash('sha256').update(b).digest('hex');
const canon = (o) => JSON.stringify(Object.fromEntries(Object.keys(o).sort().map(k => [k,o[k]])));
function verify(spacePath, cpPath) {
  const manifestBytes = readFileSync(spacePath);
  const cpBytes = readFileSync(cpPath);
  if (manifestBytes.length > 1048576 || cpBytes.length > 16384) throw Error('INPUT_TOO_LARGE');
  const manifest = JSON.parse(manifestBytes.toString('utf8'));
  if (manifest.schema !== 'CoEvoSpace/1' || !Array.isArray(manifest.dimensions)) throw Error('BAD_SPACE');
  const count = manifest.dimensions.reduce((p,d) => {
    if (typeof d.name !== 'string' || !Array.isArray(d.options) || d.options.length < 2 || d.options.length > 64) throw Error('BAD_DIMENSION');
    return p * BigInt(d.options.length);
  }, 1n);
  const cpText = cpBytes.toString('utf8');
  const names = [...cpText.matchAll(/"([A-Za-z_][A-Za-z0-9_]*)"\s*:/g)].map(m => m[1]);
  if (names.length !== NAMES.length || new Set(names).size !== names.length || names.some(k => !NAMES.includes(k))) throw Error('DUPLICATE_OR_UNEXPECTED_KEY');
  const cp = JSON.parse(cpText);
  if (Object.keys(cp).length !== NAMES.length || NAMES.some(k => !Object.hasOwn(cp,k))) throw Error('BAD_CHECKPOINT_SHAPE');
  if (cp.schema !== 'CoTurtleCheckpoint/3') throw Error('BAD_CHECKPOINT_SCHEMA');
  const payload = Object.fromEntries(Object.entries(cp).filter(([key]) => key !== 'checkpoint_sha256'));
  if (cp.checkpoint_sha256 !== sha256(canon(payload))) throw Error('TAMPERED_CHECKPOINT');
  if (cp.spec_sha256 !== sha256(manifestBytes)) throw Error('SPEC_NAMESPACE_CHANGED');
  if (count > BigInt(Number.MAX_SAFE_INTEGER) || typeof cp.capacity !== 'number' || !Number.isSafeInteger(cp.capacity) || BigInt(cp.capacity) !== count) throw Error('CAPACITY_MISMATCH_OR_EXCEEDS_JS_SAFE_INTEGER');
  if (cp.effect_ceiling !== 'LOGICAL_ONLY_NO_EXTERNAL_EFFECTS') throw Error('EFFECT_POLICY_CHANGED');
  if (typeof cp.actual_live_sessions !== 'number' || cp.actual_live_sessions !== 0 || typeof cp.actual_executed_experiments !== 'number' || cp.actual_executed_experiments !== 0) throw Error('FALSE_EXECUTION_STATUS');
  if (!Number.isSafeInteger(cp.next_index) || cp.next_index < 0 || cp.next_index > cp.capacity || !Number.isSafeInteger(cp.revision) || cp.revision < 0) throw Error('BAD_CURSOR_OR_REVISION');
  if (cp.parent_checkpoint_sha256 !== null && !/^[0-9a-f]{64}$/.test(cp.parent_checkpoint_sha256)) throw Error('BAD_PARENT_DIGEST');
  return { status:'PASS_CHECKPOINT_NAMESPACE', capacity:String(count), cursor:cp.next_index,
           spec_sha256:cp.spec_sha256, executions_verified:0 };
}
try {
  if (process.argv.length !== 4) throw Error('USAGE node verify_checkpoint.mjs space_manifest.json checkpoint.json');
  console.log(JSON.stringify(verify(process.argv[2],process.argv[3])));
} catch (error) {
  process.stderr.write('FAIL ' + String(error.message) + '\n');
  process.exitCode = 2;
}