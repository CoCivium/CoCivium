"use strict";
/**
 * Optional CoMegaThesis Chrome smoke. A screenshot and DOM check are only
 * source/browser evidence, not WCAG certification, human UX acceptance,
 * deployed CoOrb/CoBar, or independent receiver pickup.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { pathToFileURL } = require("node:url");
const root = path.resolve(__dirname, "..");
const file = path.join(root, "docs/CoTheoryAll/candidates/comegathesis-reader-r0.html");
const folder = path.join(root, "artifacts/comegathesis-r0");
const html = fs.readFileSync(file, "utf8");
const workId = "CoTheoryAll::CoForgetToBecome::R0";
const blob = "d5a8f256183d0f8862d12c10861cac5e84a1bd6b";
const count = (s, item) => s.split(item).length - 1;
assert.equal(count(html, 'data-work-id="' + workId + '"'), 3);
assert.equal(count(html, 'data-source-blob="' + blob + '"'), 3);
assert.match(html, /script-src 'none'/);
assert.doesNotMatch(html, /<script\b|onload=|onclick=/i);
fs.mkdirSync(folder, { recursive: true });
let browser;
for (const bin of [process.env.CHROME_BIN, "google-chrome", "chromium", "chromium-browser"].filter(Boolean)) {
  const p = spawnSync(bin, ["--version"], { encoding: "utf8", timeout: 4000 });
  if (!p.error && p.status === 0) { browser = bin; break; }
}
assert(browser, "HOLD_NO_CHROME_BROWSER_BINARY");
const profiles = [
  { name: "desktop", width: 1366, height: 900 },
  { name: "narrow", width: 390, height: 844 }
];
const results = [];
for (const profile of profiles) {
  const png = path.join(folder, profile.name + ".png");
  const args = [
    "--headless", "--disable-gpu", "--disable-dev-shm-usage",
    "--disable-extensions", "--disable-background-networking",
    "--no-first-run", "--no-default-browser-check", "--hide-scrollbars",
    "--window-size=" + profile.width + "," + profile.height,
    "--screenshot=" + png, pathToFileURL(file).href
  ];
  if (process.getuid && process.getuid() === 0) args.unshift("--no-sandbox");
  const p = spawnSync(browser, args, { encoding: "utf8", timeout: 20000, maxBuffer: 1_000_000 });
  if (p.error || p.status !== 0) {
    throw new Error("HOLD_CHROME_SMOKE_" + profile.name + ": status=" + p.status + "; " +
      String(p.error || p.stderr || "").slice(-600));
  }
  const data = fs.readFileSync(png);
  assert(data.length > 512, "Screenshot empty: " + profile.name);
  assert.equal(data.subarray(0,8).toString("hex"), "89504e470d0a1a0a");
  const width = data.readUInt32BE(16), height = data.readUInt32BE(20);
  assert(width >= 300 && height >= 400, "Invalid raster dimensions");
  results.push({ name: profile.name, width, height, bytes: data.length, screenshot: path.basename(png) });
  process.stdout.write("BROWSER_SMOKE_SOURCE_ONLY " + profile.name + " " + width + "x" + height + "\n");
}
const receipt = {
  schema: "CoMegaThesis.BrowserSmoke.SourceOnly.R0",
  observed_at_utc: new Date().toISOString(),
  source_commit: process.env.GITHUB_SHA || null,
  source_work_id: workId, source_blob: blob,
  browser_binary: browser, results,
  effect_boundary: "BROWSER_RASTER_ONLY",
  nonclaims: ["human_UX_acceptance","WCAG_certification","live_CoOrb_or_CoBar","independent_receiver_ACK","deployment","CoEx","canon"]
};
fs.writeFileSync(path.join(folder, "browser-smoke-receipt.json"), JSON.stringify(receipt, null, 2) + "\n");
process.stdout.write("BROWSER_RASTER_COMPLETE_NOT_INDEPENDENT_ACCEPTANCE\n");
