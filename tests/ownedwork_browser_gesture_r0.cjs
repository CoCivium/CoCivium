#!/usr/bin/env node
'use strict';
/* Bounded Chromium UI canary for the existing CoContextRail R1 page.
 * Automated click is NOT human consent, receiver authorization or X2 runtime.
 * Zero external service contact: HTTP binds only to 127.0.0.1.
 */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

const htmlFile = path.resolve(__dirname, '../examples/conodcothumb/context_rail_r1/index.html');
const storageKey = 'CoCivium.CoContextRail.SyntheticWorkID.R0';
const output = path.resolve(__dirname, '../out/ownedwork-chromium-r0/browser-record.json');

async function visit(page, address) {
  await page.goto(address, { waitUntil: 'load', timeout: 15000 });
  await page.locator('#context').selectOption('RESEARCH');
  await page.locator('#question').selectOption('WHAT_ELSE');
  await page.locator('#privacy').selectOption('PUBLIC');
  await page.locator('#gesture').selectOption('EXPLICIT_RING');
  const fixture = page.locator('#fixture');
  if (await fixture.isChecked()) await fixture.uncheck();
}

async function prepare(page) {
  await page.locator('#preview').click();
  assert.equal((await page.locator('#state').innerText()).trim(), 'PROPOSED_ONLY');
  assert.equal(await page.locator('#workPreserve').isDisabled(), false);
}

(async () => {
  const contents = fs.readFileSync(htmlFile);
  const server = http.createServer((req, res) => {
    if (req.url !== '/' && req.url !== '/index.html') {
      res.writeHead(404, {'Content-Type':'text/plain'}); return res.end('Not found');
    }
    res.writeHead(200, {'Content-Type':'text/html; charset=utf-8',
                        'Cache-Control':'no-store'});
    res.end(contents);
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  let browser;
  try {
    browser = await chromium.launch({
      channel: 'chrome', headless: true, args: ['--no-sandbox']
    });
    const address = 'http://127.0.0.1:' + server.address().port + '/';
    const context = await browser.newContext();
    const page = await context.newPage();
    await visit(page, address);
    assert.equal(await page.locator('#workPreserve').isDisabled(), true);
    const initial = await page.evaluate(key => window.localStorage.getItem(key), storageKey);
    assert.equal(initial, null, 'no synthetic event before explicit Preview/Preserve');
    await prepare(page);
    await page.locator('#workPreserve').click();
    assert.equal((await page.locator('#workState').innerText()).trim(),
                 'COMMITTED_BROWSER_LOCAL');
    const row = await page.evaluate(key => {
      const value = window.localStorage.getItem(key);
      return value === null ? null : JSON.parse(value);
    }, storageKey);
    assert.ok(row, 'real Chromium localStorage must contain one record');
    assert.equal(row.schema, 'CoAll.CoOwnedWork.BrowserLocal.R0.Record');
    assert.equal(row.packet.work_id, 'CoPre.ReadyCycle.Synthetic.R0');
    assert.equal(row.state, 'ACTIVE');
    assert.equal(row.commit_sequence, 1);
    assert.equal(row.receiver_ack, false);
    assert.equal(row.source_verified_by_browser, false);

    await page.reload({waitUntil:'load'});
    await page.locator('#workRecover').click();
    assert.equal((await page.locator('#workState').innerText()).trim(),
                 'RECOVERED_BROWSER_LOCAL');
    await prepare(page);
    await page.locator('#workPreserve').click();
    assert.equal((await page.locator('#workState').innerText()).trim(),
                 'DUPLICATE_SUPPRESSED');
    const after = await page.evaluate(key => JSON.parse(window.localStorage.getItem(key)), storageKey);
    assert.deepEqual(after, row, 'duplicate must not mutate a preserved work object');

    // A second, disjoint browser context exercises explicit local revocation.
    // Its revoked record is deliberately NOT used as a receiver input.
    const negativeContext = await browser.newContext();
    const negative = await negativeContext.newPage();
    await visit(negative, address);
    await prepare(negative);
    await negative.locator('#workPreserve').click();
    assert.equal((await negative.locator('#workState').innerText()).trim(),
                 'COMMITTED_BROWSER_LOCAL');
    await negative.locator('#workRevoke').click();
    assert.equal((await negative.locator('#workState').innerText()).trim(),
                 'REVOKED_BROWSER_LOCAL');
    await negative.locator('#workRecover').click();
    assert.equal((await negative.locator('#workState').innerText()).trim(),
                 'HELD_REVOKED');
    await prepare(negative);
    await negative.locator('#workPreserve').click();
    assert.equal((await negative.locator('#workState').innerText()).trim(),
                 'HELD_REVOKED');
    await negativeContext.close();

    // The ORIGINAL browser context now revokes the very same WorkID whose
    // ACTIVE bytes are exported for the SQLite commit. This is a synthetic
    // UI event, not authenticated cross-host revocation.
    await page.locator('#workRevoke').click();
    assert.equal((await page.locator('#workState').innerText()).trim(),
                 'REVOKED_BROWSER_LOCAL');
    const revoked = await page.evaluate(key =>
      JSON.parse(window.localStorage.getItem(key)), storageKey);
    assert.equal(revoked.state, 'REVOKED');
    assert.deepEqual({...revoked, state:'ACTIVE'}, row,
                     'revocation must not mutate identity, payload or epoch');
    await page.locator('#workRecover').click();
    assert.equal((await page.locator('#workState').innerText()).trim(),
                 'HELD_REVOKED');
    await prepare(page);
    await page.locator('#workPreserve').click();
    assert.equal((await page.locator('#workState').innerText()).trim(),
                 'HELD_REVOKED');

    fs.mkdirSync(path.dirname(output), {recursive:true});
    fs.writeFileSync(path.join(path.dirname(output), 'browser-revoked-record.json'),
                     JSON.stringify(revoked, null, 2) + '\\n', {flag:'wx'});
    fs.writeFileSync(output, JSON.stringify(row, null, 2) + '\n', {flag:'wx'});
    console.log(JSON.stringify({
      schema:'CoAll.CoOwnedWork.ChromiumUIGestureProof.R0',
      state:'AUTOMATED_BROWSER_PREVIEW_PRESERVE_RECOVER_DUPLICATE_REVOKE_PASS',
      source_page:'examples/conodcothumb/context_rail_r1/index.html',
      stored_work_id:row.packet.work_id,
      exported_state:row.state,
      revoked_context_exported:false,
      same_origin_browser_revocation_exported:true,
      cross_domain_revocation_verified:false,
      real_human_consent:false,
      independently_authorized_receiver:false,
      external_effects:0
    }));
    await context.close();
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
