"use strict";
// R1 read-only browser QA. No user data, no live submission or deployed surface.
const fs=require("fs"),path=require("path"),assert=require("assert").strict;
const {pathToFileURL}=require("url");
const puppeteer=require(process.env.PUPPETEER_MODULE||"puppeteer");
(async()=>{
 const root=path.resolve(process.argv[2]||__dirname);
 const url=pathToFileURL(path.join(root,"index.html")).href;
 const checks=[],errors=[],requests=[];
 const report={schema:"GroupBuild.IdeaCommons.BrowserQAR1",state:"X2_LOCAL_HEADLESS_NO_INDEPENDENT_USER",checked_at_utc:new Date().toISOString(),viewports:[390,768,1440],checks,errors,requests,screenshots:[]};
 const check=(name,condition,detail="")=>checks.push({name,pass:!!condition,detail:String(detail).slice(0,220)});
 let browser=null;
 try{
  browser=await puppeteer.launch({headless:true,args:["--no-sandbox","--disable-dev-shm-usage","--allow-file-access-from-files"]});
  const page=await browser.newPage();
  page.on("pageerror",e=>errors.push(e.message));
  page.on("request",r=>{if(!r.url().startsWith("file:")&&!r.url().startsWith("data:")&&!r.url().startsWith("blob:"))requests.push(r.url().slice(0,180));});
  for(const width of report.viewports){
   await page.setViewport({width,height:820,deviceScaleFactor:1});
   await page.goto(url,{waitUntil:"load"});
   const snap=await page.evaluate(()=>({w:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,buttons:document.querySelectorAll("[data-view]").length,heading:document.querySelector("h1")?.textContent}));
   check("responsive_"+width,snap.scroll<=snap.w+2,snap.scroll+"/"+snap.w);
   check("three_views_"+width,snap.buttons===3,snap.buttons);
   check("clear_promise_"+width,snap.heading?.includes("Not a job"),snap.heading);
   const file="IDEA_COMMONS_"+width+"_R1.png";await page.screenshot({path:path.join(root,file),fullPage:true});report.screenshots.push(file);
  }
  await page.click('[data-view="sketch"]');check("sketch_view",await page.$eval("#preview",e=>e.textContent.includes("alternative")), "view switch");
  await page.click('[data-view="circle"]');check("circle_is_fiction",await page.$eval("#view-disclaimer",e=>e.textContent.includes("FICTIONAL_GROUP_VIEW")),"fictional");
  await page.click('[data-view="float"]');check("float_is_mock",await page.$eval("#view-disclaimer",e=>e.textContent.includes("UX_CONCEPT_ONLY")),"mock");
  await page.click("#save");check("empty_save_refused",await page.$eval("#status",e=>e.textContent.includes("Write a thought")),"no empty save");
  await page.click("#suggest-sample");check("example_inserted",await page.$eval("#idea",e=>e.value.length>20),"example");
  check("example_unsent",await page.$eval("#status",e=>e.textContent.includes("Not saved or sent")),"not sent");
  await page.click("#save");const saveState=await page.$eval("#status",e=>e.textContent);
  check("save_truthful",saveState.includes("Kept on this browser only")||saveState.includes("did not permit local storage"),saveState);
  await page.click("#clear");check("clear_empties_text",await page.$eval("#idea",e=>e.value===""),"clear");
  await page.reload({waitUntil:"load"});check("no_automatic_recovery_of_cleared",await page.$eval("#idea",e=>e.value===""),"no draft");
  await page.click("#export");check("empty_export_refused",await page.$eval("#status",e=>e.textContent.includes("Write a thought")),"no export");
  await page.click("#suggest-sample");check("download_tool_available",await page.$eval("#export",e=>e.textContent.includes("Export")),"download opt in");
  check("no_external_requests",requests.length===0,JSON.stringify(requests));
  check("no_js_errors",errors.length===0,JSON.stringify(errors));
 }catch(e){errors.push(String(e.stack||e));}
 finally{
  if(browser)await browser.close();
  report.passed=checks.filter(x=>x.pass).length;report.total=checks.length;
  report.ok=report.passed===report.total && errors.length===0 && requests.length===0;
  fs.writeFileSync(path.join(root,"BROWSER_QA_R1.json"),JSON.stringify(report,null,2)+"\n");
  console.log(JSON.stringify({ok:report.ok,passed:report.passed,total:report.total,errors,screenshots:report.screenshots}));
  process.exitCode=report.ok?0:1;
 }
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
