#!/usr/bin/env node
/* Independent raw-canonical JSONL verifier for Python-origin CoBenchmarkEvoEvent/1.
 * Preserves original numeric spellings (e.g. -117.0) when hashing. Requires a
 * separately retained expected head. No network access or provider calls.
 */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
const [file, headFile] = process.argv.slice(2);
try {
  if (!file || !headFile) throw Error('USAGE node verify_evo_ledger.mjs JSONL HEAD');
  const content = readFileSync(file, 'utf8');
  if (Buffer.byteLength(content) > 1_000_000) throw Error('LEDGER_TOO_LARGE');
  const expected = readFileSync(headFile, 'utf8').trim();
  if (!/^[0-9a-f]{64}$/.test(expected)) throw Error('INVALID_EXPECTED_HEAD');
  const lines = content.trimEnd().split('\n');
  let prior = '0'.repeat(64);
  let count = 0;
  for (const raw of lines) {
    if (raw === '' || raw.endsWith('\r')) throw Error('INVALID_LINE');
    const row = JSON.parse(raw);
    count++;
    if (row.schema !== 'CoBenchmarkEvoEvent/1' || row.seq !== count || row.prev_hash !== prior)
      throw Error('SCHEMA_SEQUENCE_OR_PREV_HASH_MISMATCH');
    const pattern = /,"event_hash":"([0-9a-f]{64})"/g;
    const matches = [...raw.matchAll(pattern)];
    if (matches.length !== 1 || matches[0][1] !== row.event_hash)
      throw Error('EVENT_HASH_FIELD_NOT_CANONICAL');
    const sansHash = raw.replace(pattern, '');
    // Validate the hash of exact canonical source bytes without JS floating-point reserialization.
    const digest = createHash('sha256').update(sansHash, 'utf8').digest('hex');
    if (digest !== row.event_hash) throw Error('BAD_EVENT_HASH');
    prior = digest;
  }
  if (!count || prior !== expected) throw Error('HEAD_MISMATCH');
  process.stdout.write(`PASS node hash-chain events=${count} head=${expected}\n`);
} catch (err) {
  process.stderr.write(`FAIL ${err.message}\n`);
  process.exitCode = 1;
}
