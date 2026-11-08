/* Real Chromium interaction probe for CoSurface R0. No deployment or X2 control. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const { pathToFileURL } = require("node:url");
const { resolve } = require("node:path");

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    page.on("pageerror", err => errors.push(err.message));
    await page.goto(pathToFileURL(resolve(__dirname, "index.html")).href);
    assert.equal(await page.locator("#workspace").isVisible(), false, "Default should be quiet");
    assert.equal(await page.locator("#r5-rail").isVisible(), true);
    assert.equal(await page.locator("#orb").count(), 1);

    await page.locator("#rail-map").click();
    assert.equal(await page.locator("#workspace").isVisible(), true, "Rail should open workspace");
    assert.equal(await page.locator("#map").isVisible(), true);

    await page.locator("#rail-stop").click();
    assert.equal(await page.locator("#workspace").isVisible(), false, "Hide must reverse open");

    await page.locator("#orb").click();
    assert.equal(await page.locator("#orb-panel").isVisible(), true, "Orb opens nav");
    await page.locator("#orbnav button", { hasText: "Future" }).click();
    assert.equal(await page.locator("#future").isVisible(), true);
    assert.equal(await page.locator("#orb-panel").isVisible(), false);
    assert.match(await page.locator("#future").innerText(), /not a divine instruction/);

    await page.locator("#orb").click();
    await page.keyboard.press("Escape");
    assert.equal(await page.locator("#orb-panel").isVisible(), false, "Escape closes panel");

    await page.locator("#orb").click({ button: "right" });
    assert.equal(await page.locator("#legacy").isVisible(), true, "Right click opens legacy menu");
    await page.locator("#legacy button", { hasText: "Evidence" }).click();
    assert.equal(await page.locator("#evidence").isVisible(), true);

    assert.deepEqual(errors, [], "No browser execution errors");
    console.log("BROWSER_PROBE_PASS: rail, orb, legacy, Future, Stop, Escape; synthetic only");
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
