"use strict";
// Three existing public-source candidates. CI checkout is NOT production deployment.
// One Chromium invocation, no external browser requests, no credentials, no site writes.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { pathToFileURL } = require("node:url");
const { execFileSync } = require("node:child_process");
const { chromium } = require("playwright-core");

const OUT = path.resolve("out/cosites261119-three-flagship-first-use-r0");
const SPECS = [
  { id: "cocivium", name: "CoCivium R1", repo: "CoCivium/CoCivium",
    commit: "421e79529da712e15edf78060d889c027f3ad991",
    file: "cosites261118-preview/cocivium-home-r1/index.html",
    blob: "ce97f53e7c28791319f7bca369c26fcac3ba7f36" },
  { id: "inseed", name: "InSeed PR1", repo: "CoCivium/InSeed",
    commit: "dc03e8865a90de6d26bf03bc64061319b1cf7fbd",
    file: "site_sources/inseed/index.html",
    blob: "0effb59c4a4e830f2ce5297998df496786d49f32" },
  { id: "copolitic", name: "CoPolitic PR1", repo: "CoCivium/CoPolitic-site",
    commit: "218b43f773b5f02e63739a0438d88ff6890f6166",
    file: "site_sources/copolitic/index.html",
    blob: "1ae823ad0072cb310c2f30f7cb464c05b375a43f" }
];
const VIEWPORTS = [
  { id: "compact320", width: 320, height: 720, screenshot: false },
  { id: "mobile390", width: 390, height: 844, screenshot: true },
  { id: "desktop1365", width: 1365, height: 900, screenshot: true }
];

function gitBlobSha1(data) {
  return crypto.createHash("sha1").update("blob " + data.length + "\0").update(data).digest("hex");
}
function sha256(data) { return crypto.createHash("sha256").update(data).digest("hex"); }
function chromePath() {
  const names = ["google-chrome", "google-chrome-stable", "chromium"];
  for (const n of names) {
    try { return execFileSync("which", [n], { encoding: "utf8" }).trim(); }
    catch (_) {}
  }
  throw Error("HOLD_NO_CHROMIUM_BINARY");
}
function assert(condition, message) {
  if (!condition) throw Error(message);
}
function atomicallyWriteReceipt(receipt) {
  fs.mkdirSync(OUT, { recursive: true });
  const f = path.join(OUT, "source_browser_receipt.json");
  const temp = f + ".tmp";
  fs.writeFileSync(temp, JSON.stringify(receipt, null, 2) + "\n", { flag: "w" });
  fs.renameSync(temp, f);
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const receipt = {
    schema: "CoSites.ThreeFlagship.FirstUseBrowserCI.R0",
    status: "PENDING",
    proof_scope: "PINNED_SOURCE_ONLY_SAME_GITHUB_PROVIDER_NOT_HOSTED_SITE_OR_HUMAN_ACCEPTANCE",
    generated_utc: new Date().toISOString(),
    browser: "Chromium via playwright-core@1.56.0, reduced-motion",
    active_effects: { startup_mutations: 0, public_deployments: 0, network_requests_permitted_from_browser: 0 },
    candidates: [], errors: [],
    nonclaims: ["NO_PUBLIC_SITE_HOSTING_PROOF", "NO_PUBLIC_PRIVACY_CLEARANCE", "NO_X2_RUNTIME",
      "NO_THREE_INDEPENDENT_ROOTS", "CI_BROWSER_IS_NOT_HUMAN_FIRST_USE", "NO_COEX", "NO_PHANTOM_ACK"]
  };
  let browser;
  try {
    browser = await chromium.launch({ executablePath: chromePath(), headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"] });
    for (const spec of SPECS) {
      const f = path.resolve(spec.file);
      const src = fs.readFileSync(f);
      const blob = gitBlobSha1(src);
      assert(blob === spec.blob, "HOLD_SOURCE_BLOB_DRIFT:" + spec.id + ":" + blob);
      const candidate = { id: spec.id, repo: spec.repo, checked_out_commit: spec.commit,
        path: spec.file, source_git_blob_sha1: blob, source_sha256: sha256(src),
        views: [], status: "PENDING" };
      receipt.candidates.push(candidate);
      for (const view of VIEWPORTS) {
        const ctx = await browser.newContext({
          viewport: { width: view.width, height: view.height }, deviceScaleFactor: 1,
          reducedMotion: "reduce", colorScheme: "dark"
        });
        const outside = [], errors = [];
        await ctx.route(/^https?:/i, async route => {
          outside.push(route.request().url().split("?")[0]);
          await route.abort("blockedbyclient");
        });
        const page = await ctx.newPage();
        page.on("pageerror", e => errors.push(e.message));
        try {
          await page.goto(pathToFileURL(f).href, { waitUntil: "load", timeout: 15000 });
          const m = await page.evaluate(() => {
            const a = [...document.querySelectorAll('a[href^="#"]')];
            const unresolved = a.map(x => x.getAttribute("href")).filter(h => !h ||
              !document.getElementById(decodeURIComponent(h.slice(1))));
            const main = document.querySelector("main");
            return {
              title: document.title, lang: document.documentElement.lang,
              viewport_meta: !!document.querySelector('meta[name="viewport"]'),
              h1_count: document.querySelectorAll("h1").length,
              h1_visible: !!document.querySelector("h1") &&
                document.querySelector("h1").getBoundingClientRect().height > 0,
              main_visible: !!main && main.getBoundingClientRect().height > 0,
              document_scroll_width: document.documentElement.scrollWidth,
              body_scroll_width: document.body.scrollWidth,
              internal_anchor_count: a.length, unresolved,
              form_count: document.forms.length, script_count: document.scripts.length,
              horizontal_overflow_px: Math.max(0,
                document.documentElement.scrollWidth - window.innerWidth,
                document.body.scrollWidth - window.innerWidth)
            };
          });
          assert(m.title.length > 8 && m.lang === "en", "HOLD_TITLE_OR_LANGUAGE:" + spec.id);
          assert(m.viewport_meta && m.h1_count === 1 && m.h1_visible && m.main_visible,
            "HOLD_NO_READABLE_MAIN:" + spec.id + ":" + view.id);
          assert(m.unresolved.length === 0 && m.internal_anchor_count > 0,
            "HOLD_BROKEN_LOCAL_ANCHORS:" + spec.id + ":" + view.id);
          assert(m.horizontal_overflow_px <= 2, "HOLD_HORIZONTAL_OVERFLOW:" +
            spec.id + ":" + view.id + ":" + m.horizontal_overflow_px);
          assert(m.form_count === 0 && m.script_count === 0,
            "HOLD_UNQUALIFIED_SCRIPTS_OR_FORMS:" + spec.id);
          assert(errors.length === 0 && outside.length === 0,
            "HOLD_BROWSER_ERRORS_OR_NETWORK:" + spec.id);
          let image = null;
          if (view.screenshot) {
            const file = spec.id + "-" + view.id + ".png";
            const screenshot = await page.screenshot({ path: path.join(OUT, file), fullPage: true });
            image = { file, sha256: sha256(screenshot), bytes: screenshot.length };
          }
          const nav = page.locator('nav a[href^="#"]');
          assert(await nav.count() > 0, "HOLD_NO_KEYBOARD_NAVIGATION:" + spec.id);
          const target = await nav.first().getAttribute("href");
          await nav.first().click({ timeout: 5000 });
          const actual = await page.evaluate(() => location.hash);
          assert(actual === target, "HOLD_NAVIGATION_NOT_WORKING:" + spec.id + ":" + view.id);
          candidate.views.push({
            viewport: view.id, width: view.width, height: view.height,
            result: "PASS_SOURCE_BROWSER_PROBE", horizontal_overflow_px: m.horizontal_overflow_px,
            internal_anchors: m.internal_anchor_count, broken_anchors: 0,
            tested_navigation: target, blocked_network: outside.length,
            screenshot: image
          });
        } finally { await ctx.close(); }
      }
      candidate.status = "PASS_3_VIEWPORT_SOURCE_BROWSER_PROBES";
    }
    receipt.status = "PASS_PINNED_SOURCE_BROWSER_PROBES_3_SITES";
  } catch (err) {
    receipt.status = "HOLD_SOURCE_BROWSER_PROBES";
    receipt.errors.push(String(err.message || err).slice(0, 1200));
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    atomicallyWriteReceipt(receipt);
    console.log(JSON.stringify({ status: receipt.status,
      candidates: receipt.candidates.map(x => ({ site: x.id, state: x.status, views: x.views.length })),
      errors: receipt.errors, output: OUT }));
  }
}
main().catch(err => { console.error(err); process.exitCode = 2; });
