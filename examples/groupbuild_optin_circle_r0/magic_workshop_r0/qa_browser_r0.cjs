"use strict";
/** Honest Magic Workshop: bounded headless Chromium QA.
 * Local file only. No site deployment, real participants, real approvals, or independent UX.
 * Optional dependency: puppeteer (or PUPPETEER_MODULE exact installed path).
 */
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const assert = require("assert").strict;
const puppeteer = require(process.env.PUPPETEER_MODULE || "puppeteer");

(async () => {
  const root = path.resolve(process.argv[2] || __dirname);
  const file = path.join(root, "index.html");
  const out = path.join(root, "browser_qa_r0.json");
  assert(fs.existsSync(file), "source file missing");
  const results = [];
  const report = {
    schema: "GroupBuild.MagicWorkshop.BrowserQAR0",
    work_id: "GroupBuild.MagicWorkshop.CoTermables.20261123.R0",
    state: "LOCAL_HEADLESS_QA_NOT_FIRST_USE_ACCEPTANCE",
    observed_at_utc: new Date().toISOString(),
    source: "index.html",
    viewports: [390, 768, 1440],
    cases: results,
    errors: [],
    failed_requests: [],
    screenshots: []
  };
  let browser;
  const test = (name, condition, detail = "") => {
    results.push({ name, pass: !!condition, detail: String(detail || "") });
  };
  try {
    browser = await puppeteer.launch({ headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage", "--allow-file-access-from-files"] });
    const page = await browser.newPage();
    page.on("pageerror", e => report.errors.push(e.message));
    page.on("requestfailed", request => report.failed_requests.push({ url: request.url().slice(0, 120), error: request.failure()?.errorText || "UNKNOWN" }));
    await page.setDefaultNavigationTimeout(10000);
    for (const width of report.viewports) {
      await page.setViewport({ width, height: 850, deviceScaleFactor: 1 });
      await page.goto(pathToFileURL(file).href, { waitUntil: "load" });
      await page.waitForSelector("#steps button");
      const m = await page.evaluate(() => ({
        title: document.title,
        heading: document.querySelector("h1")?.textContent || "",
        stages: document.querySelectorAll("#steps button").length,
        lensButtons: document.querySelectorAll("[data-lens]").length,
        clientWidth: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
        firstState: document.querySelector("#current-stage")?.textContent || ""
      }));
      test("viewport_" + width + "_eight_stages", m.stages === 8, m.stages);
      test("viewport_" + width + "_four_lenses", m.lensButtons === 4, m.lensButtons);
      test("viewport_" + width + "_no_hscroll", m.scrollWidth <= m.clientWidth + 2, m.scrollWidth + "/" + m.clientWidth);
      test("viewport_" + width + "_honest_title", m.heading.includes("Make a world"), m.title);
      const screenshot = path.join(root, "MAGIC_WORKSHOP_" + width + "_R0.png");
      await page.screenshot({ path: screenshot, fullPage: true });
      report.screenshots.push(path.basename(screenshot));
    }
    const before = await page.$eval("#current-stage", e => e.textContent);
    await page.click('#steps button[aria-label="Go stage explanation only"]');
    const after = await page.$eval("#current-stage", e => e.textContent);
    test("explain_only_does_not_move_state", before === after, before + " -> " + after);
    const holdTruth = await page.$eval("#stage-truth", e => e.textContent);
    test("go_truth_no_effects", holdTruth.includes("No effect occurred"), holdTruth.slice(0, 160));
    await page.click('[data-lens="philosopher"]');
    const philosophy = await page.$eval("#stage-example", e => e.textContent);
    test("philosopher_lens_switch", philosophy.length > 20, philosophy.slice(0, 160));
    await page.select("#project", "park");
    const projectState = await page.$eval("#current-stage", e => e.textContent);
    test("park_held_at_gate", projectState.includes("Gate"), projectState);
    await page.select("#toy-world", "2");
    await page.select("#toy-rule", "3");
    await page.click("#poof");
    const poof = await page.$eval("#poof-result", e => e.textContent);
    test("poof_builds_local_scene", poof.includes("Mystery Library") && poof.includes("No single character"), poof.slice(0, 230));
    test("poof_no_effects_claim", poof.includes("No real-world action"), poof.slice(-155));
    const pageUrl = await page.url();
    test("remains_local_file", pageUrl.startsWith("file:///"), pageUrl.split("/").slice(-1)[0]);
    test("no_js_errors", report.errors.length === 0, report.errors.join("; "));
    test("no_failed_network", report.failed_requests.length === 0, JSON.stringify(report.failed_requests));
  } catch (e) {
    report.errors.push("RUNNER:" + String(e.stack || e));
  } finally {
    if (browser) await browser.close();
    report.passed = results.filter(x => x.pass).length;
    report.total = results.length;
    report.ok = report.errors.length === 0 && report.failed_requests.length === 0 && report.passed === report.total;
    fs.writeFileSync(out, JSON.stringify(report, null, 2) + "\n");
    process.stdout.write(JSON.stringify({ ok: report.ok, passed: report.passed, total: report.total, errors: report.errors, screenshots: report.screenshots, report: out }) + "\n");
    process.exitCode = report.ok ? 0 : 1;
  }
})().catch(e => { console.error(e.stack || e); process.exitCode = 1; });
