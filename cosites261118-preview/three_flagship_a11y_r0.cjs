"use strict";
// Candidate-source accessibility audit, never public deployment/visitor acceptance.
// One site per ephemeral CI job; no HTTP browser requests and no raw HTML export.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { pathToFileURL } = require("node:url");
const { execFileSync } = require("node:child_process");
const { chromium } = require("playwright-core");

const SPECS = Object.freeze({
  cocivium: {repo: "CoCivium/CoCivium", source: "cosites261118-preview/cocivium-home-r1/index.html", blob: "ce97f53e7c28791319f7bca369c26fcac3ba7f36"},
  inseed: {repo: "CoCivium/InSeed", source: "site_sources/inseed/index.html", blob: "0effb59c4a4e830f2ce5297998df496786d49f32"},
  copolitic: {repo: "CoCivium/CoPolitic-site", source: "site_sources/copolitic/index.html", blob: "1ae823ad0072cb310c2f30f7cb464c05b375a43f"}
});
const VIEWPORTS = Object.freeze([
  {id:"mobile390", width:390, height:844},
  {id:"desktop1365", width:1365, height:900}
]);
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
const sha256 = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const blobSha = bytes => crypto.createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex");
function browserExecutable() {
  for(const name of ["google-chrome", "google-chrome-stable", "chromium"]){
    try { return execFileSync("which", [name], {encoding:"utf8"}).trim(); } catch {}
  }
  throw new Error("HOLD_NO_CHROMIUM_BINARY");
}
async function main() {
  const site = process.argv[2];
  if(!Object.hasOwn(SPECS, site)) throw new Error("HOLD_UNELECTED_SITE");
  const spec = SPECS[site];
  const base = path.resolve(`out/cosites261120-a11y/${site}`);
  fs.mkdirSync(base, {recursive:true});
  const report = {
    schema:"CoSites.ThreeFlagship.PinnedSourceAccessibility.R0",
    state:"HOLD_PENDING_SCAN", site, source_repo:spec.repo, expected_blob:spec.blob,
    run_commit:process.env.GITHUB_SHA || "LOCAL_UNATTESTED",
    observed_utc:new Date().toISOString(),
    scan_tags:TAGS, viewports:[],
    bounds:{chrome_headless:true, browser_http_requests_permitted:0, public_site_mutations:0,
      no_raw_page_html_export:true, no_dom_node_text_or_selector_export:true,
      no_credentials_or_storage_access:true, synthetic_not_user_acceptance:true},
    nonclaims:["AUTOMATED_A11Y_SCAN_IS_NOT_HUMAN_ACCEPTANCE","CANDIDATE_NE_PUBLIC_SITE",
      "SINGLE_CI_PROVIDER_NE_3IND","NO_PUBLIC_DEPLOYMENT","NO_COEX","NO_PHANTOM_ACK"]
  };
  let browser;
  try {
    const html = fs.readFileSync(path.resolve(spec.source));
    const actual=blobSha(html);
    if(actual!==spec.blob) throw new Error("HOLD_SOURCE_DRIFT_"+site);
    report.source_sha256=sha256(html);
    report.source_blob_sha1=actual;
    const axeSource=fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
    browser=await chromium.launch({executablePath:browserExecutable(), headless:true,
      args:["--no-sandbox", "--disable-dev-shm-usage"]});
    let violations=0;
    for(const viewport of VIEWPORTS){
      const ctx=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},
        reducedMotion:"reduce",deviceScaleFactor:1});
      const attempted=[]; const errors=[];
      await ctx.route(/^https?:/i, async route=>{
        attempted.push("BLOCKED_EXTERNAL_REQUEST");
        await route.abort("blockedbyclient");
      });
      const page=await ctx.newPage();
      page.on("pageerror", e=>errors.push(String(e.name||"PAGE_ERROR").slice(0,48)));
      try {
        await page.goto(pathToFileURL(path.resolve(spec.source)).href,
          {waitUntil:"load",timeout:15000});
        await page.addScriptTag({content:axeSource});
        const result=await page.evaluate(async tags => window.axe.run(document,{
          runOnly:{type:"tag",values:tags},
          resultTypes:["violations","incomplete"]
        }), TAGS);
        const summary=result.violations.map(x=>({id:x.id,impact:x.impact||"unknown",
          affected_node_count:x.nodes.length, tags:x.tags.filter(t=>TAGS.includes(t)).sort()}));
        violations += summary.length;
        // Rule IDs only: no HTML, node selectors, messages, markup, or target text.
        const incompleteRules = result.incomplete.map(x => ({
          id: /^[a-z0-9_-]{1,80}$/.test(x.id) ? x.id : "UNRECOGNIZED_RULE_ID",
          impact: ["minor","moderate","serious","critical"].includes(x.impact) ? x.impact : "unknown",
          affected_node_count: x.nodes.length
        })).sort((a,b)=>a.id.localeCompare(b.id));
        report.viewports.push({viewport:viewport.id,width:viewport.width,height:viewport.height,
          violations:summary, rule_violation_count:summary.length,
          incomplete_rule_count:result.incomplete.length,
          incomplete_rules:incompleteRules,
          rules_passed:result.passes.length, blocked_http_requests:attempted.length,
          javascript_page_errors:errors.length});
      } finally {await ctx.close();}
    }
    report.state = violations ? "HOLD_AUTOMATED_A11Y_VIOLATIONS" : "PASS_AUTOMATED_A11Y_NO_DETECTED_VIOLATIONS_NOT_HUMAN_ACCEPTED";
    if(violations) process.exitCode=1;
  } catch(e) {
    report.state="HOLD_AUDIT_ERROR";
    report.failure_class=String(e.message||e).slice(0,160).replace(/https?:\/\/[^ ]+/g,"URL_REDACTED");
    process.exitCode=2;
  } finally {
    if(browser)await browser.close();
    const output=path.join(base,"audit_receipt.json");
    fs.writeFileSync(output,JSON.stringify(report,null,2)+"\n");
    console.log(JSON.stringify({site,state:report.state,
      viewports:report.viewports.map(x=>({id:x.viewport,violations:x.rule_violation_count,incomplete:x.incomplete_rule_count})),
      output}));
  }
}
main().catch(e=>{console.error("HOLD_AUDIT_RUNNER_EXCEPTION",e.name);process.exitCode=3;});