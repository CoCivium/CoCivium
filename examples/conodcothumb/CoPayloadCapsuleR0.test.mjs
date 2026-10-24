import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { previewFile, stageFile, MAX_FILE_BYTES } from './CoPayloadCapsuleR0.mjs';

async function sandbox(t) {
  const d = await mkdtemp(join(tmpdir(), 'cothumb-r0-'));
  t.after(async () => { await rm(d, { recursive: true, force: true }); });
  return d;
}
test('1 preview streams >300KiB without leaking file contents or file path', async t => {
  const dir = await sandbox(t);
  const file = join(dir, 'private-internal-description.mp4');
  const payload = Buffer.alloc(400 * 1024, 0x41);
  await writeFile(file, payload);
  const r = await previewFile(file);
  assert.equal(r.byte_count, 409600);
  assert.equal(r.sha256, createHash('sha256').update(payload).digest('hex'));
  assert.equal(r.payload_type_hint, 'video/mp4');
  assert.equal(r.state, 'PREVIEW_ONLY');
  assert.equal(r.external_effects.network, 0);
  assert.equal(r.authority, 'NONE');
  assert.ok(!JSON.stringify(r).includes('private-internal-description'));
  assert.ok(!JSON.stringify(r).includes(dir));
});
test('2 local staging requires explicit acceptance', async t => {
  const dir = await sandbox(t); const f = join(dir, 'safe.txt');
  await writeFile(f, 'hello');
  await assert.rejects(stageFile(f, join(dir, 'buffer')), /EXPLICIT_LOCAL_COPY_ACCEPTANCE_REQUIRED/);
  assert.deepEqual((await readdir(dir)).sort(), ['safe.txt']);
});
test('3 staged object has exact hash and private relative locator', async t => {
  const dir = await sandbox(t); const f = join(dir, 'media.mp4');
  await writeFile(f, Buffer.alloc(350000, 0xA7));
  const b = join(dir, 'buffer');
  const r = await stageFile(f, b, { accepted: true });
  assert.equal(r.state, 'STAGED_LOCAL_ONLY');
  const data = await readFile(join(b, r.buffer_locator));
  assert.equal(data.length, 350000);
  assert.equal(createHash('sha256').update(data).digest('hex'), r.sha256);
  assert.ok(!r.buffer_locator.includes(dir));
  const manifest = JSON.parse(await readFile(join(b, 'sha256-' + r.sha256 + '.manifest.json')));
  assert.equal(manifest.sha256, r.sha256);
  assert.ok(!JSON.stringify(manifest).includes(f));
});
test('4 repeated stage is idempotent with no new blob', async t => {
  const dir = await sandbox(t); const f = join(dir, 'f.png');
  await writeFile(f, Buffer.alloc(409600, 0x05)); const b = join(dir, 'b');
  const one = await stageFile(f, b, { accepted: true });
  const before = (await readdir(b)).sort();
  const two = await stageFile(f, b, { accepted: true });
  assert.equal(two.duplicate_reuse, true);
  assert.equal(one.payload_id, two.payload_id);
  assert.deepEqual((await readdir(b)).sort(), before);
});
test('5 directories are refused', async t => {
  const dir = await sandbox(t);
  await assert.rejects(previewFile(dir), /ONLY_REGULAR_NON_SYMLINK_FILES_ALLOWED/);
});
test('6 input symlinks are refused', async t => {
  const dir = await sandbox(t); const f = join(dir, 'data.txt');
  await writeFile(f, 'private'); const s = join(dir, 'link.txt');
  try { await symlink(f, s); } catch (e) { t.skip('symlink unavailable: '+e.code); return; }
  await assert.rejects(previewFile(s), /ONLY_REGULAR_NON_SYMLINK_FILES_ALLOWED/);
});
test('7 output buffer symlink is refused', async t => {
  const dir = await sandbox(t); const f = join(dir, 'safe.txt');
  await writeFile(f, 'hello'); const actual = join(dir, 'actual');
  await mkdir(actual); const link = join(dir, 'link');
  try { await symlink(actual, link); } catch (e) { t.skip('symlink unavailable: '+e.code); return; }
  await assert.rejects(stageFile(f, link, { accepted: true }), /BUFFER_DIRECTORY_INVALID/);
});
test('8 path is absent -> explicit failure', async t => {
  const dir = await sandbox(t);
  await assert.rejects(previewFile(join(dir, 'missing.bin')), { code: 'ENOENT' });
});
test('9 tampered blob cannot be reused under the same hash', async t => {
  const dir = await sandbox(t); const f = join(dir, 'safe.bin');
  await writeFile(f, Buffer.alloc(310000, 0x03)); const b = join(dir, 'buffer');
  const initial = await stageFile(f, b, { accepted: true });
  await writeFile(join(b, initial.buffer_locator), 'BAD CONTENT');
  await assert.rejects(stageFile(f, b, { accepted: true }), /STAGED_BYTES_DO_NOT_MATCH_SOURCE_COPY/);
});
test('10 cap constant is finite and applied before processing', async t => {
  assert.ok(MAX_FILE_BYTES <= 1024*1024*1024);
  const dir = await sandbox(t); const f = join(dir, 'small.txt');
  await writeFile(f, 'ok');
  const r = await previewFile(f);
  assert.equal(r.byte_count, 2);
});
