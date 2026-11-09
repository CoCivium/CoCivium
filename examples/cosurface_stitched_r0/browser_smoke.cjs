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
    // Screenshot-derived challenge: the user should not need to decipher a
    // microscopic rail at a 2048x1151 desktop viewport, and the Orb must
    // remain physically distinct from the rail on narrow screens.
    async function railLegibility(width, height, screenshotName) {
      const p = await browser.newPage({ viewport: { width, height } });
      try {
        await p.goto(pathToFileURL(resolve(__dirname, "index.html")).href);
        const values = await p.evaluate(() => {
          const rail = document.getElementById("r5-rail");
          const orb = document.getElementById("orb");
          const button = document.getElementById("rail-workspace");
          const rb = rail.getBoundingClientRect(), ob = orb.getBoundingClientRect();
          return {
            font: parseFloat(getComputedStyle(rail).fontSize),
            buttonFont: parseFloat(getComputedStyle(button).fontSize),
            buttonHeight: button.getBoundingClientRect().height,
            railTop: rb.top, orbBottom: ob.bottom,
            railIsVisible: rb.width > 100 && rb.height >= 44,
            workspaceHidden: document.getElementById("workspace").hidden,
            orbCount: document.querySelectorAll("#orb").length,
            evidence: rail.innerText,
            membrane: orb.dataset.membraneState
          };
        });
        assert.ok(values.font >= 14, "CoAll rail must be legible rather than microtext");
        assert.ok(values.buttonFont >= 14);
        assert.ok(values.buttonHeight >= 38, "Navigation controls should not shrink to tiny targets");
        assert.ok(values.railIsVisible);
        assert.ok(values.orbBottom <= values.railTop - 1,
                  "Orb must sit above the rail, not cover its controls");
        assert.equal(values.workspaceHidden, true, "Default remains quiet");
        assert.equal(values.orbCount, 1);
        assert.match(values.evidence, /NO LIVE EFFECT/);
        assert.equal(values.membrane, "unknown");
        mkdirSync(evidenceDir, { recursive: true });
        await p.screenshot({ path: resolve(evidenceDir, screenshotName), fullPage: true });
      } finally {
        await p.close();
      }
    }
    await railLegibility(2048, 1151, "x2-sized-quiet-candidate.png");
    await railLegibility(390, 844, "narrow-quiet-candidate.png");
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
