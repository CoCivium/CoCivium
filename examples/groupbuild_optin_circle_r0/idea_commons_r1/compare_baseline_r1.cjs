"use strict";
/* GroupBuild idea-commons R1 comparative test, scripted and non-human.
 * Identical tiny task: sample -> keep -> reload -> clear -> sample -> export.
 * Browser geometry is NOT usability, preference, or receiver acceptance.
 * This test never sends a public suggestion, email, or approval.
 */
const fs=require("fs"), path=require("path"), assert=require("assert").strict;
const {pathToFileURL}=require("url");
const puppeteer=require(process.env.PUPPETEER_MODULE||"puppeteer");
const root=path.resolve(process.argv[2]||__dirname);
const reportPath=path.join(root,"COMPARISON_SCRIPTED_R1.json");
const configurations=[
  {id:"simple",file:"simple_baseline.html",caption:"Text-only baseline"},
  {id:"rich",file:"index.html",caption:"Float/Sketch/Circle"}
];
const NOW=new Date().toISOString();
(async()=>{
  let browser;
  const report={schema:"GroupBuild.IdeaCommons.ComparisonScriptedR1",at_utc:NOW,
    state:"SAME_HOST_SCRIPTED_BROWSER_COMPARATOR__NOT_HUMAN_FIRST_USE",
    scope:"Two source-linked local-file interfaces, identical synthetic task path, no real participant",
    cases:[],errors:[],screenshots:[],conclusion_ceiling:"LAYOUT_AND_SCRIPT_ONLY",
    next_human_test:"Consent-based first-time participant with randomized order and no real identifying text"};
  try{
    browser=await puppeteer.launch({headless:true,args:["--no-sandbox","--disable-dev-shm-usage","--allow-file-access-from-files"]});
    for(const cfg of configurations){
      const page=await browser.newPage();
      const network=[],errors=[];
      page.on("request",r=>{if(!["file:","data:","blob:"].some(s=>r.url().startsWith(s)))network.push(r.url().slice(0,200));});
      page.on("pageerror",e=>errors.push(e.message));
      const facts={id:cfg.id,caption:cfg.caption,viewports:{},controls:{},scripted:{},nonclaims:[]};
      for(const width of [390,768,1440]){
        await page.setViewport({width,height:800,deviceScaleFactor:1});
        await page.goto(pathToFileURL(path.join(root,cfg.file)).href,{waitUntil:"load"});
        await page.waitForSelector("#idea");
        const m=await page.evaluate(()=>{
          const input=document.querySelector("#idea");
          const rect=input.getBoundingClientRect();
          return {
            body_text_chars:document.body.innerText.length,
            links:document.querySelectorAll("a").length,
            buttons:document.querySelectorAll("button").length,
            heading_count:document.querySelectorAll("h1,h2").length,
            idea_top_px:Math.round(rect.top+window.scrollY),
            idea_visible_on_initial_screen:rect.top>=0&&rect.top<window.innerHeight,
            scroll_width:document.documentElement.scrollWidth,
            viewport_width:document.documentElement.clientWidth,
            horizontal_overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2
          };
        });
        facts.viewports[String(width)]=m;
        const imageName=cfg.id+"_"+width+"_R1.png";
        await page.screenshot({path:path.join(root,imageName),fullPage:true});
        report.screenshots.push(imageName);
      }
      // Same scripted actions on both pages; events are synthetic.
      await page.setViewport({width:390,height:800,deviceScaleFactor:1});
      await page.goto(pathToFileURL(path.join(root,cfg.file)).href,{waitUntil:"load"});
      await page.click("#suggest-sample");
      facts.scripted.sample_text=await page.$eval("#idea",e=>e.value);
      await page.click("#save");
      facts.scripted.save_message=await page.$eval("#status",e=>e.textContent);
      facts.scripted.save_claims_local_only=/browser only|browser did not permit local storage/.test(facts.scripted.save_message);
      await page.reload({waitUntil:"load"});
      facts.scripted.after_reload_text=await page.$eval("#idea",e=>e.value);
      await page.click("#clear");
      facts.scripted.cleared=await page.$eval("#idea",e=>e.value==="");
      facts.scripted.clear_message=await page.$eval("#status",e=>e.textContent);
      await page.click("#suggest-sample");
      await page.click("#export");
      facts.scripted.export_message=await page.$eval("#status",e=>e.textContent);
      facts.scripted.export_explicitly_unsent=/download requested/.test(facts.scripted.export_message);
      facts.scripted.synthetic_clicks=5;
      facts.controls.network_requests=network;
      facts.controls.page_errors=errors;
      facts.pass=Object.values(facts.viewports).every(v=>!v.horizontal_overflow)
        && facts.scripted.sample_text.length>0
        && facts.scripted.save_claims_local_only
        && facts.scripted.cleared
        && facts.scripted.export_explicitly_unsent
        && network.length===0 && errors.length===0;
      report.cases.push(facts);
      await page.close();
    }
    const simple=report.cases.find(c=>c.id==="simple");
    const rich=report.cases.find(c=>c.id==="rich");
    report.comparisons={
      mobile_idea_top_delta_px:rich.viewports["390"].idea_top_px-simple.viewports["390"].idea_top_px,
      baseline_has_fewer_initial_buttons:simple.viewports["390"].buttons<rich.viewports["390"].buttons,
      same_synthetic_task_clicks:simple.scripted.synthetic_clicks===rich.scripted.synthetic_clicks,
      responsive_no_overflow:report.cases.every(c=>Object.values(c.viewports).every(v=>!v.horizontal_overflow)),
      no_network_requests:report.cases.every(c=>c.controls.network_requests.length===0),
      no_js_errors:report.cases.every(c=>c.controls.page_errors.length===0),
      human_preference:"UNKNOWN",
      first_time_comprehension:"UNTESTED",
      actual_idea_receiver_ack:"NONE",
      comparative_task_time:"UNMEASURED"
    };
  }catch(e){report.errors.push(String(e.stack||e));}
  finally{
    if(browser)await browser.close();
    report.ok=report.errors.length===0&&report.cases.length===2&&report.cases.every(c=>c.pass);
    fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+"\n");
    process.stdout.write(JSON.stringify({ok:report.ok,cases:report.cases.map(c=>({id:c.id,pass:c.pass,at_390:c.viewports["390"]?.idea_top_px,buttons:c.viewports["390"]?.buttons,saved:c.scripted?.save_message,exported:c.scripted?.export_message})),compare:report.comparisons,errors:report.errors,report:reportPath})+"\n");
    process.exitCode=report.ok?0:1;
  }
})().catch(e=>{console.error(String(e.stack||e));process.exitCode=1;});
