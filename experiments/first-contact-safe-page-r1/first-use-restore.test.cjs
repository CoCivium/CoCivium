'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const {formatCard, parseCard} = require('./first-use.js');

test('R1 local card round-trips two fields without machine authority', () => {
  const card = formatCard('Improve a local meeting', 'A newcomer understands the options');
  assert.match(card, /LOCAL_DRAFT__NOT_SUBMITTED__NOT_VERIFIED/);
  assert.match(card, /Source: CoCivium CoSpiff first-contact R1/);
  assert.deepEqual(parseCard(card), {
    goal: 'Improve a local meeting',
    proof: 'A newcomer understands the options',
    provenance: 'R1'
  });
});

test('legacy R0 card restores without silently changing provenance', () => {
  const previous = formatCard('A past task', 'A past measure')
    .replace('Source: CoCivium CoSpiff first-contact R1',
             'Source: CoCivium CoSpiff first-contact R0');
  assert.deepEqual(parseCard(previous), {
    goal: 'A past task', proof: 'A past measure', provenance: 'R0'
  });
});

test('UTF-8 content, CRLF and UTF-8 BOM restore into plain text fields', () => {
  const content = '\ufeff' + formatCard('A café meeting and ☀', 'Evidence: 変化')
    .replace(/\n/g, '\r\n');
  assert.equal(parseCard(content).goal, 'A café meeting and ☀');
  assert.equal(parseCard(content).proof, 'Evidence: 変化');
});

test('empty or oversized fields hold rather than truncating', () => {
  assert.throws(() => formatCard(' ', 'evidence'), /HOLD_CARD_FIELD_BOUNDS/);
  assert.throws(() => formatCard('a'.repeat(1001), 'evidence'), /HOLD_CARD_FIELD_BOUNDS/);
  assert.throws(() => formatCard('goal', 'x'.repeat(1001)), /HOLD_CARD_FIELD_BOUNDS/);
});

test('embedded Markdown section headings fail closed', () => {
  assert.throws(() => formatCard('goal\n## Evidence I would look for\nspoof', 'proof'),
                /HOLD_CARD_RESERVED_HEADING/);
  const altered = formatCard('goal', 'proof')
    .replace('goal\n', 'goal\n## Unexpected section\n');
  assert.throws(() => parseCard(altered), /HOLD_CARD_RESERVED_HEADING/);
});

test('draft-status token inside goal cannot replace machine-status header', () => {
  const card = formatCard(
    'goal\nStatus: LOCAL_DRAFT__NOT_SUBMITTED__NOT_VERIFIED',
    'proof'
  );
  const tampered = card.replace(
    '\nStatus: LOCAL_DRAFT__NOT_SUBMITTED__NOT_VERIFIED\n',
    '\nStatus: PUBLICLY_VERIFIED__RECEIVER_ACKED\n'
  );
  assert.match(tampered, /Status: PUBLICLY_VERIFIED__RECEIVER_ACKED/);
  assert.match(tampered, /goal\nStatus: LOCAL_DRAFT__NOT_SUBMITTED__NOT_VERIFIED/);
  assert.throws(() => parseCard(tampered), /HOLD_CARD_PROVENANCE/);
});

test('tampered provenance and wrong section ordering hold', () => {
  const card = formatCard('goal', 'proof');
  assert.throws(() => parseCard(card.replace('# My first useful CoCivium card', '# Stranger card')),
                /HOLD_CARD_PROVENANCE/);
  assert.throws(() => parseCard(card.replace('LOCAL_DRAFT__NOT_SUBMITTED__NOT_VERIFIED',
                                            'SUBMITTED__VERIFIED')),
                /HOLD_CARD_PROVENANCE/);
  assert.throws(() => parseCard(card.replace('## Goal', '## Modified')),
                /HOLD_CARD_STRUCTURE/);
  assert.throws(() => parseCard(card.replace('## One safe next step', '## Evidence I would look for')),
                /HOLD_CARD_STRUCTURE/);
  assert.throws(() => parseCard(card.replace('Source: CoCivium CoSpiff first-contact R1',
                                            'Source: stranger')),
                /HOLD_CARD_PROVENANCE/);
});

test('duplicate structural marker holds, not last-marker-wins', () => {
  const card = formatCard('goal', 'proof');
  const ambiguous = card.replace('## Evidence I would look for',
                                  '## Goal\nspoof\n\n## Evidence I would look for');
  assert.throws(() => parseCard(ambiguous), /HOLD_CARD_STRUCTURE/);
});

test('raw file and unexpected line ending sizes hold', () => {
  assert.throws(() => parseCard('x'.repeat(12289)), /HOLD_CARD_TOO_LARGE/);
  assert.throws(() => parseCard(formatCard('goal', 'proof').replace(/\n/g, '\r')),
                /HOLD_CARD_LINE_ENDING|HOLD_CARD_PROVENANCE/);
  assert.throws(() => parseCard(null), /HOLD_CARD_TEXT_REQUIRED/);
});

function mountBrowserStub() {
  const listeners = {};
  const goal = {value: '', focused: false, focus() { this.focused = true; }};
  const proof = {value: ''};
  const restore = {files: [], value: '',
    addEventListener(type, fn) { listeners['restore:' + type] = fn; }};
  const status = {textContent: ''};
  const form = {addEventListener(type, fn) { listeners['form:' + type] = fn; }};
  const elements = {'card-form': form, 'goal': goal, 'proof': proof,
                    'restore-file': restore, 'status': status};
  global.window = {document: {getElementById(id) { return elements[id]; }}};
  const file = require.resolve('./first-use.js');
  delete require.cache[file];
  require(file);
  delete global.window;
  return {goal, proof, restore, status, listeners};
}

test('user-selected local R0 file restores into empty fields, never uploads', async () => {
  const b = mountBrowserStub();
  const card = formatCard('saved goal', 'saved proof').replace(
    'Source: CoCivium CoSpiff first-contact R1',
    'Source: CoCivium CoSpiff first-contact R0');
  b.restore.files = [{size: Buffer.byteLength(card, 'utf8'), text: async () => card}];
  await b.listeners['restore:change']();
  assert.equal(b.goal.value, 'saved goal');
  assert.equal(b.proof.value, 'saved proof');
  assert.equal(b.goal.focused, true);
  assert.match(b.status.textContent, /Nothing was uploaded/);
  assert.equal(b.restore.value, '');
});

test('existing local text is never overwritten and file bytes are not read', async () => {
  const b = mountBrowserStub();
  b.goal.value = 'unfinished original';
  let read = false;
  b.restore.files = [{size: 50, text: async () => { read = true; return 'data'; }}];
  await b.listeners['restore:change']();
  assert.equal(read, false);
  assert.equal(b.goal.value, 'unfinished original');
  assert.equal(b.proof.value, '');
  assert.match(b.status.textContent, /Restore held/);
});

test('oversized file is held before bytes are read', async () => {
  const b = mountBrowserStub();
  let read = false;
  b.restore.files = [{size: 12289, text: async () => { read = true; return ''; }}];
  await b.listeners['restore:change']();
  assert.equal(read, false);
  assert.match(b.status.textContent, /Restore held/);
  assert.equal(b.goal.value, '');
});

test('invalid local file never changes either field', async () => {
  const b = mountBrowserStub();
  b.restore.files = [{size: 40, text: async () => '# Some other document'}];
  await b.listeners['restore:change']();
  assert.equal(b.goal.value, '');
  assert.equal(b.proof.value, '');
  assert.match(b.status.textContent, /Restore held/);
});

test('no silent browser storage or network source primitives', () => {
  const js = fs.readFileSync(path.join(__dirname, 'first-use.js'), 'utf8');
  const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
  assert.match(html, /id="restore-file"[^>]*type="file"/);
  assert.match(html, /aria-describedby="restore-hint"/);
  assert.match(html, /connect-src 'none'/);
  for (const term of ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage',
                      'sessionStorage', 'indexedDB', 'WebSocket', 'postMessage(']) {
    assert.equal(js.includes(term), false, 'unexpected effect path: ' + term);
  }
});
