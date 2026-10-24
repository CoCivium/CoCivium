#!/usr/bin/env node
/**
 * CoThumb+ / CoPayload+ R0: explicit, local, binary-safe capsule canary.
 * No hooks, clipboard inspection, device enumeration, network or provider calls.
 * Requires an explicit file path. Staging additionally requires opt-in flags.
 * Public test source only; not a mouse mapping, custody root or receiver ACK.
 */
import { constants } from 'node:fs';
import { createReadStream, createWriteStream } from 'node:fs';
import { copyFile, lstat, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { basename, extname, join, resolve } from 'node:path';
import { Transform } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { fileURLToPath } from 'node:url';

export const SCHEMA = 'CoPayload.ExplicitLocalCapsule.R0';
export const MAX_FILE_BYTES = 512 * 1024 * 1024;
const O_NOFOLLOW = constants.O_NOFOLLOW ?? 0;
const FILE_HINTS = Object.freeze({
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
  '.webp': 'image/webp', '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
  '.pdf': 'application/pdf', '.json': 'application/json',
  '.md': 'text/markdown', '.txt': 'text/plain', '.zip': 'application/zip'
});

function reject(message) { throw new Error(message); }
async function inspectSource(filePath) {
  if (!filePath || typeof filePath !== 'string') reject('EXPLICIT_FILE_REQUIRED');
  const s = await lstat(filePath);
  if (s.isSymbolicLink() || !s.isFile()) reject('ONLY_REGULAR_NON_SYMLINK_FILES_ALLOWED');
  if (s.size > MAX_FILE_BYTES) reject('SIZE_EXCEEDS_BOUNDED_R0_CAP');
  return s;
}
async function fileHash(filePath) {
  const original = await inspectSource(filePath);
  const hash = createHash('sha256');
  let bytes = 0;
  for await (const chunk of createReadStream(filePath, { flags: constants.O_RDONLY | O_NOFOLLOW })) {
    bytes += chunk.length;
    if (bytes > MAX_FILE_BYTES) reject('SIZE_EXCEEDS_BOUNDED_R0_CAP');
    hash.update(chunk);
  }
  const ending = await inspectSource(filePath);
  if (bytes !== original.size || ending.size !== original.size ||
      ending.mtimeMs !== original.mtimeMs) reject('SOURCE_CHANGED_DURING_READ');
  return { sha256: hash.digest('hex'), byte_count: bytes };
}
function capsule(filePath, observed, mode) {
  // No basename, source path, selected text, secret or media bytes in the result.
  const hint = FILE_HINTS[extname(filePath).toLowerCase()] || 'application/octet-stream';
  return {
    schema: SCHEMA,
    state: mode === 'STAGE' ? 'STAGED_LOCAL_ONLY' : 'PREVIEW_ONLY',
    payload_id: 'sha256:' + observed.sha256,
    payload_type_hint: hint,
    payload_type_evidence: 'UNTRUSTED_FILENAME_EXTENSION_ONLY',
    byte_count: observed.byte_count,
    sha256: observed.sha256,
    provenance: { source_selection: 'EXPLICIT_CLI_PATH', content: 'EXACT_STREAMED_BYTES' },
    privacy: 'PRIVATE_LOCAL',
    authority: 'NONE',
    currentness: 'READ_AT_CALL_TIME',
    receiver_candidates: [],
    preview_ref: null,
    recovery_pointer: null,
    external_effects: { network: 0, provider_calls: 0, messages: 0, device_input: 0 },
    nonclaims: [
      'PREVIEW_NE_SEND', 'STAGED_NE_CUSTODY', 'HASH_NE_SEMANTIC_REVIEW',
      'PAYLOAD_REF_NE_RECEIVER_ACK', 'NOT_PHYSICAL_MOUSE_BINDING'
    ]
  };
}

export async function previewFile(filePath) {
  const r = await fileHash(filePath);
  return capsule(filePath, r, 'PREVIEW');
}

export async function stageFile(filePath, bufferDir, { accepted = false } = {}) {
  if (!accepted) reject('EXPLICIT_LOCAL_COPY_ACCEPTANCE_REQUIRED');
  if (!bufferDir || typeof bufferDir !== 'string') reject('EXPLICIT_PRIVATE_BUFFER_REQUIRED');
  await inspectSource(filePath);
  const destDir = resolve(bufferDir);
  await mkdir(destDir, { recursive: true, mode: 0o700 });
  const d = await lstat(destDir);
  if (!d.isDirectory() || d.isSymbolicLink()) reject('BUFFER_DIRECTORY_INVALID');
  const tmp = join(destDir, '.staging-' + randomUUID() + '.tmp');
  let tmpCreated = false;
  try {
    const initial = await inspectSource(filePath);
    const hash = createHash('sha256');
    let bytes = 0;
    const transform = new Transform({ transform(chunk, encoding, cb) {
      bytes += chunk.length;
      if (bytes > MAX_FILE_BYTES) return cb(new Error('SIZE_EXCEEDS_BOUNDED_R0_CAP'));
      hash.update(chunk);
      cb(null, chunk);
    }});
    tmpCreated = true;
    await pipeline(
      createReadStream(filePath, { flags: constants.O_RDONLY | O_NOFOLLOW }),
      transform,
      createWriteStream(tmp, { flags: 'wx', mode: 0o600 })
    );
    const ending = await inspectSource(filePath);
    if (initial.size !== bytes || ending.size !== initial.size ||
        ending.mtimeMs !== initial.mtimeMs) reject('SOURCE_CHANGED_DURING_COPY');
    const observed = { sha256: hash.digest('hex'), byte_count: bytes };
    const blobName = 'sha256-' + observed.sha256 + '.blob';
    const blob = join(destDir, blobName);
    let reused = false;
    try {
      // Exclusive destination. Never silently overwrite an existing object.
      await copyFile(tmp, blob, constants.COPYFILE_EXCL);
    } catch (err) {
      if (err.code !== 'EEXIST') throw err;
      reused = true;
    }
    const onDisk = await fileHash(blob);
    if (onDisk.sha256 !== observed.sha256 || onDisk.byte_count !== observed.byte_count)
      reject('STAGED_BYTES_DO_NOT_MATCH_SOURCE_COPY');
    const manifest = {
      ...capsule(filePath, observed, 'STAGE'),
      buffer_locator: blobName,
      staged_receipt: 'LOCAL_BLOB_HASH_VERIFIED',
      duplicate_reuse: reused
    };
    // A stable sidecar is the index. No source path or filename is persisted.
    const sidecar = join(destDir, 'sha256-' + observed.sha256 + '.manifest.json');
    const stable = { ...manifest, duplicate_reuse: undefined };
    try {
      await writeFile(sidecar, JSON.stringify(stable, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
    } catch (err) {
      if (err.code !== 'EEXIST') throw err;
      const existing = JSON.parse(await readFile(sidecar, 'utf8'));
      if (existing.sha256 !== observed.sha256 || existing.byte_count !== observed.byte_count)
        reject('MANIFEST_COLLISION_OR_TAMPER');
    }
    return manifest;
  } finally {
    if (tmpCreated) await rm(tmp, { force: true }).catch(() => {});
  }
}

function help() {
  return [
    'CoPayloadCapsuleR0 local-only explicit-file canary',
    '  node CoPayloadCapsuleR0.mjs --preview <selected-file>',
    '  node CoPayloadCapsuleR0.mjs --stage <selected-file> --buffer-dir <private-dir> --accept-local-copy',
    'No mouse mapping, clipboard read, automatic send or file-content stdout.'
  ].join('\n');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  try {
    let output;
    if (args.length === 2 && args[0] === '--preview') {
      output = await previewFile(args[1]);
    } else if (args.length === 5 && args[0] === '--stage' &&
               args[2] === '--buffer-dir' && args[4] === '--accept-local-copy') {
      output = await stageFile(args[1], args[3], { accepted: true });
    } else {
      console.log(help());
      process.exitCode = args.length === 0 || args[0] === '--help' ? 0 : 2;
    }
    if (output) console.log(JSON.stringify(output, null, 2));
  } catch (err) {
    console.error('CoPayload R0 blocked: ' + String(err.message || err));
    process.exitCode = 1;
  }
}
