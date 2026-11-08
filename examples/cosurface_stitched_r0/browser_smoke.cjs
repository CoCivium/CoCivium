/* Real Chromium interaction probe for CoSurface R0. No deployment or X2 control. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const { pathToFileURL } = require("node:url");
const { resolve } = require("node:path");
const { mkdirSync } = require("node:fs");
const evidenceDir = resolve(__dirname, "evidence");

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    page.on("pageerror", err => errors.push(err.message));
    await page.goto(pathToFileURL(resolve(__dirname, "index.html")).href);
    mkdirSync(evidenceDir, { recursive: true });
    assert.equal(await page.locator("#workspace").isVisible(), false, "Default should be quiet");
    assert.equal(await page.locator("#r5-rail").isVisible(), true);
    assert.equal(await page.locator("#orb").count(), 1);
    await page.screenshot({ path: resolve(evidenceDir, "quiet-default.png"), fullPage: true });

    assert.equal(await page.locator("#rail-map").isDisabled(), true);
    await page.locator("#rail-evidence").click();
    assert.equal(await page.locator("#workspace").isVisible(), true, "Rail should open workspace");
    assert.equal(await page.locator("#evidence").isVisible(), true);

    await page.locator("#rail-stop").click();
    assert.equal(await page.locator("#workspace").isVisible(), false, "Hide must reverse open");

    await page.locator("#orb").click();
    assert.equal(await page.locator("#orb-panel").isVisible(), true, "Orb opens nav");
    assert.equal(await page.locator("#orb").getAttribute("data-membrane-state"), "unknown", "No unverified green membrane");
    assert.equal(await page.locator("#orb-contract-version").innerText(), "CoOrb.Membrane.R0");
    assert.equal(await page.locator("#orb-evidence-source").innerText(), "UNBOUND");
    assert.equal(await page.locator("#orb-receiver-version").innerText(), "UNBOUND");
    assert.equal(await page.locator("#orb-present-state").innerText(), "UNKNOWN");
    assert.equal(await page.locator("#orb-future-state").innerText(), "UNQUALIFIED");
    assert.equal(await page.locator("#orb-past-state").innerText(), "NO READBACK");
    assert.match(await page.locator("#membrane-truth").innerText(), /No live feed is attached/);
    await page.locator("#orbnav button", { hasText: "Future" }).click();
    assert.equal(await page.locator("#future").isVisible(), true);
    await page.screenshot({ path: resolve(evidenceDir, "future-workspace.png"), fullPage: true });
    assert.equal(await page.locator("#orb-panel").isVisible(), false);
    assert.match(await page.locator("#future").innerText(), /not a divine instruction/);

    await page.locator("#orb").click();
    await page.keyboard.press("Escape");
    assert.equal(await page.locator("#orb-panel").isVisible(), false, "Escape closes panel");

    await page.locator("#orb").click({ button: "right" });
    assert.equal(await page.locator("#legacy").isVisible(), true, "Right click opens legacy menu");
    await page.screenshot({ path: resolve(evidenceDir, "legacy-menu.png"), fullPage: true });
    await page.locator("#legacy button", { hasText: "Evidence" }).click();
    assert.equal(await page.locator("#evidence").isVisible(), true);

    assert.deepEqual(errors, [], "No browser execution errors");
    console.log("BROWSER_PROBE_PASS: rail, orb, legacy, Future, Stop, Escape; synthetic only");
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
