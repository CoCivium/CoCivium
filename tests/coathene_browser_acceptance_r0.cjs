"use strict";
/**
 * CoAthene browser acceptance R0: actually operates the current offline HTML
 * in Chromium at desktop and mobile sizes. Uses synthetic content only.
 *
 * Ceiling: screenshot/browser UI proof, NOT accessibility certification,
 * education efficacy, child safety, school operation or hosted deployment.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright-core");

const ROOT = path.resolve(__dirname, "..");
const OUTPUT = path.join(ROOT, "coathene-browser-proof");
const ISSUE = [];
const RECEIPTS = [];

function check(value, message) {
  if (!value) throw new Error(message);
  RECEIPTS.push({ check: message, pass: true });
}
async function text(locator) {
  return (await locator.innerText()).trim();
}
function chooseBrowser() {
  const options = [
    process.env.COATHENE_BROWSER_PATH,
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    chromium.executablePath()
  ].filter(Boolean);
  return options.find(p => fs.existsSync(p)) || null;
}
async function newPage(browser, size, label) {
  const context = await browser.newContext({
    viewport: size,
    deviceScaleFactor: 1,
    acceptDownloads: false,
    serviceWorkers: "block",
    permissions: []
  });
  const page = await context.newPage();
  page.on("pageerror", error => ISSUE.push(label + ":pageerror:" + error.message));
  page.on("console", msg => { if (msg.type() === "error") ISSUE.push(label + ":console:" + msg.text()); });
  page.on("request", request => {
    const url = request.url();
    if (/^https?:/i.test(url)) {
      ISSUE.push(label + ":unexpected-network:" + url.slice(0, 180));
      request.failure();
    }
  });
  return { context, page };
}
async function load(page, source) {
  const target = pathToFileURL(path.join(ROOT, source)).href;
  await page.goto(target, { waitUntil: "load" });
  await page.locator("h1").waitFor();
  check((await page.locator("main").count()) === 1, source + " one primary main");
  check((await page.locator("h1").count()) === 1, source + " one primary heading");
  check((await page.locator("script").count()) === 2, source + " two local scripts only");
}
async function sizeCheck(page, label) {
  const metrics = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
    clientHeight: document.documentElement.clientHeight
  }));
  check(metrics.scrollWidth <= metrics.innerWidth + 2, label + " no horizontal overflow: " + JSON.stringify(metrics));
}
async function noStorage(page, label) {
  const state = await page.evaluate(() => ({
    localStorage: localStorage.length,
    sessionStorage: sessionStorage.length,
    indexedDBAvailable: typeof indexedDB !== "undefined",
    cookie: document.cookie
  }));
  check(state.localStorage === 0 && state.sessionStorage === 0 && state.cookie === "", label + " no persistent browser data");
}
async function screenshot(page, file) {
  await page.screenshot({ path: path.join(OUTPUT, file), fullPage: true });
}
async function copetDesktop(browser) {
  const { context, page } = await newPage(browser, { width: 1280, height: 900 }, "copet-desktop");
  try {
    await load(page, "examples/coathene_copet_r0/index.html");
    check((await text(page.locator("#progress"))).includes("0 of 4"), "guest progress starts empty");
    await screenshot(page, "copet-desktop-first.png");
    await page.locator("#wardrobe summary").click();
    await page.locator("#gear-type").selectOption("hat");
    await page.locator("#gear-item").selectOption("hat_space");
    await page.locator("#gear-claim").click();
    check((await text(page.locator("#gear-look"))).includes("Orbit Cap"), "chosen hat visible as self-claim");
    check((await text(page.locator("#progress"))).includes("0 of 4"), "costume alone does not count learning");
    check(await page.locator("#gear-follow").isEnabled(), "subject hint separately actionable");
    await screenshot(page, "copet-desktop-wardrobe.png");
    await page.locator("#gear-follow").click();
    check((await page.locator("#lesson-select").inputValue()) === "space", "explicit click chooses space question");
    check((await text(page.locator("#progress"))).includes("0 of 4"), "route choice does not grant mastery");
    await page.locator('input[name="claim"][value="0"]').check();
    await page.locator('input[name="evidence"][value="0"]').check();
    await page.locator("#teach").click();
    check(await page.locator("#results").isVisible(), "teach-to-reveal result visible");
    check((await text(page.locator("#lesson-why"))).includes("Gravity"), "real subject explanation revealed");
    check((await text(page.locator("#progress"))).includes("1 of 4"), "single encountered question recorded only for visit");
    check((await text(page.locator("#visit-markers"))).includes("not a grade"), "visit mark not presented as grade");
    await screenshot(page, "copet-desktop-result.png");
    await page.locator("#again").click();
    check(await page.locator("#setup").isVisible(), "return to question choice");
    await page.locator("#clear").click();
    check((await text(page.locator("#progress"))).includes("0 of 4"), "explicit reset erases explored questions");
    check((await text(page.locator("#gear-look"))).includes("Nothing claimed"), "explicit reset erases outfit");
    await noStorage(page, "copet-desktop");
    await page.reload();
    check((await text(page.locator("#progress"))).includes("0 of 4"), "reload has no durable student profile");
  } finally { await context.close(); }
}
async function copetMobile(browser) {
  const { context, page } = await newPage(browser, { width: 390, height: 844 }, "copet-mobile");
  try {
    await load(page, "examples/coathene_copet_r0/index.html");
    await sizeCheck(page, "copet-mobile");
    await page.locator("#wardrobe summary").click();
    await page.locator("#gear-type").selectOption("trail");
    await page.locator("#gear-item").selectOption("trail_animals");
    await page.locator("#gear-claim").click();
    check((await text(page.locator("#gear-look"))).includes("Habitat Path"), "mobile trail cue is visible");
    await page.locator("#gear-follow").click();
    check((await page.locator("#lesson-select").inputValue()) === "animals", "mobile explicit route action works");
    await page.locator('input[name="claim"][value="0"]').check();
    await page.locator('input[name="evidence"][value="0"]').check();
    await page.locator("#teach").click();
    check(await page.locator("#results").isVisible(), "mobile lesson feedback reachable");
    await sizeCheck(page, "copet-mobile-after-feedback");
    await screenshot(page, "copet-mobile-result.png");
    await noStorage(page, "copet-mobile");
  } finally { await context.close(); }
}
async function anywhereDesktop(browser) {
  const { context, page } = await newPage(browser, { width: 1280, height: 900 }, "anywhere-desktop");
  try {
    await load(page, "examples/coathene_anywhere_r0/index.html");
    await page.locator("#mode").selectOption("group");
    check(await page.locator("#participants-box").isVisible(), "group role choices appear only when selected");
    await page.locator("#question").selectOption("mirror");
    await page.locator("#place").selectOption("offline");
    await page.locator("#audience").selectOption("youth");
    await page.locator("#participants").selectOption("4");
    await page.locator("#assemble").click();
    check(await page.locator("#session").isVisible(), "assembled single-front plan visible");
    check((await page.locator("#roles li").count()) === 4, "four anonymous local role seats");
    check((await text(page.locator("#conditions"))).includes("responsible real adult"), "child supervision warning visible");
    check((await text(page.locator("#conditions"))).includes("consent"), "group consent warning visible");
    await screenshot(page, "anywhere-desktop-group-plan.png");
    await page.locator('input[name="local-prediction"][value="0"]').check();
    await page.locator("#check").click();
    check((await text(page.locator("#prediction-feedback"))).includes("does not match"), "misconception corrected in live UI");
    await page.locator("#new-plan").click();
    check(await page.locator("#setup").isVisible(), "session returns to configuration");
    check(await page.locator("#session").isHidden(), "previous version does not stack in foreground");
    await noStorage(page, "anywhere-desktop");
  } finally { await context.close(); }
}
async function anywhereMobile(browser) {
  const { context, page } = await newPage(browser, { width: 390, height: 844 }, "anywhere-mobile");
  try {
    await load(page, "examples/coathene_anywhere_r0/index.html");
    await sizeCheck(page, "anywhere-mobile");
    await page.locator("#mode").selectOption("solo");
    await page.locator("#question").selectOption("runoff");
    await page.locator("#place").selectOption("anywhere");
    await page.locator("#assemble").click();
    check(await page.locator("#session").isVisible(), "mobile solo plan renders");
    check(await page.locator("#roles-box").isHidden(), "solo session has no fake connected team");
    await sizeCheck(page, "anywhere-mobile-plan");
    await screenshot(page, "anywhere-mobile-solo-plan.png");
    await noStorage(page, "anywhere-mobile");
  } finally { await context.close(); }
}
async function main() {
  fs.mkdirSync(OUTPUT, { recursive: true });
  const browserPath = chooseBrowser();
  check(!!browserPath, "Chromium executable available");
  const browser = await chromium.launch({
    executablePath: browserPath,
    headless: true,
    args: ["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu"]
  });
  try {
    await copetDesktop(browser);
    await copetMobile(browser);
    await anywhereDesktop(browser);
    await anywhereMobile(browser);
  } finally { await browser.close(); }
  check(ISSUE.length === 0, "no browser page errors or unexpected network: " + JSON.stringify(ISSUE));
  const receipt = {
    schema: "CoAthene.BrowserAcceptance.R0",
    state: "PASS_BOUNDED_REAL_CHROMIUM_UI_NOT_CHILD_OR_EDUCATOR_REVIEW",
    testSurface: "locally opened repository HTML via file:// in headless Chromium",
    viewportSizes: ["1280x900", "390x844"],
    exactInterfaces: ["CoPet+CoEntour R0", "Anywhere Studio R0"],
    checks: RECEIPTS.length,
    screenshots: fs.readdirSync(OUTPUT).filter(x => x.endsWith(".png")),
    browserNetworkCalls: "NONE_OBSERVED_UNTIL_EXPLICIT_EXTERNAL_LINK_NOT_TESTED",
    realLearners: 0,
    schoolAuthorizations: 0,
    biometricCredentials: 0,
    deployment: "NOT_PERFORMED",
    browserErrors: ISSUE
  };
  fs.writeFileSync(path.join(OUTPUT, "receipt.json"), JSON.stringify(receipt, null, 2) + "\n");
  process.stdout.write("BROWSER_ACCEPTANCE_R0 " + JSON.stringify(receipt) + "\n");
}
main().catch(err => {
  fs.mkdirSync(OUTPUT, {recursive: true});
  fs.writeFileSync(path.join(OUTPUT, "FAILURE.txt"),
    "BROWSER_ACCEPTANCE_HELD " + String(err.stack || err) + "\n" + JSON.stringify(ISSUE) + "\n");
  process.stderr.write("BROWSER_ACCEPTANCE_HELD " + String(err.stack || err) + "\n");
  process.exitCode = 1;
});
