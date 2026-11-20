"use strict";
// W07-C3-J1 visitor-readiness QA for static site candidates. Read-only: renders local source copies with all
// http(s) requests blocked, runs axe-core, checks links/structure/overflow, saves screenshots. No publication.
// usage: node w07_site_qa.cjs <out_dir> <label>=<html_path> [...]
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright-core");
const AXE = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const AXE_VER = require("axe-core/package.json").version;
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];       // same set as the release-rail audit
const EXTRA = ["wcag22aa", "best-practice"];                       // reported separately, not gating
const VIEWPORTS = [{ id: "mobile390", width: 390, height: 844 }, { id: "desktop1365", width: 1365, height: 900 }];
const sha256 = b => crypto.createHash("sha256").update(b).digest("hex");

async function scanPage(browser, label, file, outDir) {
  const bytes = fs.readFileSync(file);
  const rep = { label, file: path.basename(file), sha256: sha256(bytes), bytes: bytes.length, viewports: [] };
  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, reducedMotion: "reduce" });
    const blocked = {}; const errors = []; const consoleErr = [];
    await ctx.route(/^https?:/i, r => { const h = new URL(r.request().url()).host; blocked[h] = (blocked[h] || 0) + 1; return r.abort("blockedbyclient"); });
    const page = await ctx.newPage();
    page.on("pageerror", e => errors.push(String(e.message || e).slice(0, 160)));
    page.on("console", m => { if (m.type() === "error") consoleErr.push(m.text().slice(0, 160)); });
    await page.goto(pathToFileURL(file).href, { waitUntil: "load", timeout: 20000 });
    await page.waitForTimeout(400);
    // Page CSP stays enforced for errors/DOM/screenshot. If CSP blocks the injected axe script, axe runs in a
    // second, CSP-bypassed context used for nothing else (recorded as axe_csp_bypass).
    let axePage = page, axeCtx = null, cspBypass = false;
    try { await page.addScriptTag({ content: AXE }); }
    catch (e) {
      if (!/Content Security Policy/.test(String(e))) throw e;
      cspBypass = true;
      axeCtx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, reducedMotion: "reduce", bypassCSP: true });
      await axeCtx.route(/^https?:/i, r => r.abort("blockedbyclient"));
      axePage = await axeCtx.newPage();
      await axePage.goto(pathToFileURL(file).href, { waitUntil: "load", timeout: 20000 }); await axePage.waitForTimeout(400);
      await axePage.addScriptTag({ content: AXE });
    }
    const run = tags => axePage.evaluate(async t => {
      const r = await window.axe.run(document, { runOnly: { type: "tag", values: t }, resultTypes: ["violations"] });
      return r.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help,
        samples: v.nodes.slice(0, 3).map(n => n.target.join(" ").slice(0, 120)) }));
    }, tags);
    const gating = await run(TAGS), extra = (await run(EXTRA)).filter(x => !gating.some(g => g.id === x.id));
    const dom = await page.evaluate(() => {
      const q = s => Array.from(document.querySelectorAll(s));
      const links = q("a[href]").map(a => a.getAttribute("href"));
      const ids = new Set(q("[id]").map(e => e.id));
      const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"; };
      const small = q("a[href],button,input,select,textarea,[role=button]").filter(vis).filter(e => {
        const r = e.getBoundingClientRect(); return (r.width < 24 || r.height < 24) && !(e.tagName === "A" && getComputedStyle(e).display === "inline"); }).length;
      return {
        lang: document.documentElement.getAttribute("lang"), title: document.title,
        meta_viewport: !!document.querySelector('meta[name=viewport]'), meta_description: !!document.querySelector('meta[name=description]'),
        h1: q("h1").length, headings: q("h1,h2,h3,h4,h5,h6").map(h => +h.tagName[1]),
        landmarks: { main: q("main,[role=main]").length, nav: q("nav,[role=navigation]").length, header: q("header,[role=banner]").length, footer: q("footer,[role=contentinfo]").length },
        skip_link: links.some((h, i) => i < 3 && h && h.startsWith("#")),
        images: q("img").length, img_no_alt: q("img:not([alt])").length,
        links_total: links.length,
        broken_anchors: links.filter(h => h && h.startsWith("#") && h.length > 1 && !ids.has(decodeURIComponent(h.slice(1)))),
        relative_links: links.filter(h => h && !/^(https?:|mailto:|tel:|#|javascript:|data:)/i.test(h)),
        external_hosts: Array.from(new Set(links.filter(h => /^https?:/i.test(h)).map(h => { try { return new URL(h).host; } catch { return "BAD_URL"; } }))).sort(),
        scroll_w: document.documentElement.scrollWidth, inner_w: window.innerWidth,
        small_targets: small, scripts: q("script[src]").map(s => s.getAttribute("src")),
        text_chars: (document.body ? document.body.innerText : "").length,
      };
    });
    const skipped = new Set(); dom.heading_skips = dom.headings.reduce((a, l, i, arr) => a + (i && l > arr[i - 1] + 1 ? 1 : 0), 0);
    // relative links must resolve on disk next to the page
    dom.broken_relative = dom.relative_links.filter(h => { const p = h.split(/[?#]/)[0]; if (!p) return false;
      const t = path.resolve(path.dirname(file), decodeURIComponent(p)); return !(fs.existsSync(t) || fs.existsSync(path.join(t, "index.html"))); });
    dom.horizontal_overflow_px = Math.max(0, dom.scroll_w - dom.inner_w);
    const shot = path.join(outDir, `${label}-${vp.id}.png`);
    await page.screenshot({ path: shot, fullPage: true });
    if (axeCtx) await axeCtx.close();
    rep.viewports.push({ viewport: vp.id, axe_csp_bypass: cspBypass, axe_gating: gating, axe_extra: extra, dom, blocked_external_requests: blocked,
      page_errors: errors, console_errors: consoleErr, screenshot: path.basename(shot), screenshot_sha256: sha256(fs.readFileSync(shot)) });
    await ctx.close();
  }
  const g = rep.viewports.flatMap(v => v.axe_gating);
  const d = rep.viewports[0].dom;
  rep.summary = {
    axe_gating_violation_ids: Array.from(new Set(g.map(x => x.id))).sort(),
    axe_critical_serious: Array.from(new Set(g.filter(x => ["critical", "serious"].includes(x.impact)).map(x => x.id))).sort(),
    mobile_overflow_px: rep.viewports[0].dom.horizontal_overflow_px,
    broken_relative: Array.from(new Set(rep.viewports.flatMap(v => v.dom.broken_relative))),
    broken_anchors: Array.from(new Set(rep.viewports.flatMap(v => v.dom.broken_anchors))),
    page_errors: rep.viewports.reduce((a, v) => a + v.page_errors.length, 0),
    blocked_hosts: Array.from(new Set(rep.viewports.flatMap(v => Object.keys(v.blocked_external_requests)))).sort(),
    h1: d.h1, heading_skips: d.heading_skips, has_main: d.landmarks.main > 0, skip_link: d.skip_link, lang: d.lang,
  };
  rep.summary.visitor_ready_automated = rep.summary.axe_gating_violation_ids.length === 0 && rep.summary.mobile_overflow_px === 0 &&
    rep.summary.broken_relative.length === 0 && rep.summary.broken_anchors.length === 0 && rep.summary.page_errors === 0 &&
    d.h1 === 1 && rep.summary.has_main && !!d.lang;
  return rep;
}

(async () => {
  const [outDir, ...targets] = process.argv.slice(2); fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ executablePath: "/usr/bin/google-chrome", headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
  const out = { schema: "W07.SiteQA.R0", axe_core: AXE_VER, chrome: browser.version(), gating_tags: TAGS, extra_tags: EXTRA,
    started_utc: new Date().toISOString(), network: "all http(s) blocked; file:// only", pages: [] };
  for (const t of targets) {
    const [label, file] = t.split("=");
    try { out.pages.push(await scanPage(browser, label, path.resolve(file), outDir)); }
    catch (e) { out.pages.push({ label, error: String(e).slice(0, 300) }); }
    const p = out.pages[out.pages.length - 1];
    console.log(label, JSON.stringify(p.summary || p.error));
  }
  await browser.close(); out.finished_utc = new Date().toISOString();
  fs.writeFileSync(path.join(outDir, "qa.json"), JSON.stringify(out, null, 2) + "\n");
})();
