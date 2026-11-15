'use strict';
// Automated Chromium user-agent exercise of one PUBLIC_SYNTHETIC G_dSide WorkID.
// This is not a real participant study, provider session, runtime receiver or ACK.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const {chromium}=require('playwright-core');

const root=__dirname;
const htmlPath=path.join(root,'one_workid_lenses_r0.html');
const modelPath=path.join(root,'model.py');
const html=fs.readFileSync(htmlPath);
const model=fs.readFileSync(modelPath);
const sha256=b=>crypto.createHash('sha256').update(b).digest('hex');
const gitBlob=b=>crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const expectedBlob='eb6b2e0e472d94f612999d44c92c5a055e9eabf7';
assert.equal(gitBlob(model),expectedBlob,'HOLD_PINNED_MODEL_CHANGED');
const python=JSON.parse(execFileSync('python3',['-B','model.py'],{cwd:root,encoding:'utf8',timeout:12000}));
assert.equal(python.epistemic_class,'SYNTHETIC');
assert.equal(python.not_runtime,true);
const expected=python.pareto_frontiers;
const required=['future_benefit','backcast_overfit','rights_veto'];
assert.deepEqual(Object.keys(expected).sort(),required.sort());
assert.deepEqual(expected.future_benefit,['gdside']);
assert.deepEqual(expected.backcast_overfit,['supply']);
assert.deepEqual(expected.rights_veto,['supply']);

const errors=[];
let localRequests=0,externalRequests=0,checks=0;
function check(actual,exp,why){assert.deepEqual(actual,exp,why);checks++;}
const server=http.createServer((req,res)=>{
  if(req.url==='/lens'){
    localRequests++;
    res.writeHead(200,{'content-type':'text/html; charset=utf-8','cache-control':'no-store','referrer-policy':'no-referrer'});
    res.end(html);
  } else if(req.url==='/favicon.ico'){res.writeHead(204);res.end();}
  else {externalRequests++;res.writeHead(404);res.end();}
});
function listen(){
  return new Promise((resolve,reject)=>{
    server.once('error',reject);
    server.listen(0,'127.0.0.1',resolve);
  });
}
async function run(){
  await listen();
  const url='http://127.0.0.1:'+server.address().port+'/lens';
  const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-sandbox']});
  try{
    const context=await browser.newContext({viewport:{width:1120,height:760}});
    await context.route('**/*',route=>{
      if(route.request().url()===url||route.request().url().endsWith('/favicon.ico')){
        route.continue();
      }else{
        externalRequests++;
        errors.push('HOLD_EXTERNAL_REQUEST:'+route.request().url());
        route.abort('blockedbyclient');
      }
    });
    const page=await context.newPage();
    page.on('pageerror',e=>errors.push('JS_ERROR:'+e.message));
    await page.goto(url,{waitUntil:'load'});
    check(await page.locator('#workid').innerText(),'GDSIDE-5LANE-R0','identity');
    check(await page.locator('#source-blob').innerText(),expectedBlob,'exact model source pin');
    check(await page.locator('#truth').innerText(),'SYNTHETIC MODEL ONLY','truth label');
    check(await page.locator('#receiver').innerText(),'NONE / UNVERIFIED','ACK not invented');
    check(await page.locator('#scope').innerText(),'PUBLIC_SYNTHETIC_ONLY / EFFECT_AUTHORITY_NONE / NO_SESSION_SYNC','scope ceiling');
    check(await page.locator('#time').innerText(),'Fixture snapshot: 2026-11-15 UTC. Static source timestamp, not a heartbeat.','time is not live');

    for(const [name,title] of Object.entries({
      object:'Object lens',relation:'Relation lens',
      interstice:'In-between lens',future:'Future lens'
    })){
      await page.getByRole('button',{name:name==='interstice'?'In-between':name==='relation'?'Relations':name==='object'?'Object':'Future'}).click();
      check(await page.locator('#lens-title').innerText(),title,name+' title');
      check(await page.locator('button[data-lens][aria-pressed=true]').count(),1,name+' one lens active');
      check(await page.locator('#workid').innerText(),'GDSIDE-5LANE-R0',name+' unchanged WorkID');
      check(await page.locator('#receiver').innerText(),'NONE / UNVERIFIED',name+' receiver untouched');
    }
    await page.getByRole('button',{name:'In-between'}).click();
    const facts=await page.locator('#lens-facts').innerText();
    for(const marker of ['UNKNOWN','NOT_OBSERVED','WITHHELD','EXPLICITLY_ABSENT']) {
      check(facts.includes(marker),true,marker+' preserved');
    }

    for(const name of ['future_benefit','backcast_overfit','rights_veto']){
      await page.locator('#scenario').selectOption(name);
      check(await page.locator('#frontier').innerText(),expected[name].join(', '),name+' parity with Python model');
      check(await page.locator('#workid').innerText(),'GDSIDE-5LANE-R0',name+' still one object');
    }
    check((await page.locator('#reason').innerText()).includes('rights veto'),true,'rights veto remains visible');

    await page.getByRole('button',{name:'Pause preview'}).click();
    check(await page.locator('#lens-panel').isHidden(),true,'pause locally hides projection');
    check(await page.locator('#pause').getAttribute('aria-pressed'),'true','reversible thumb state');
    check(await page.locator('#receiver').innerText(),'NONE / UNVERIFIED','pause cannot invent ACK');
    await page.getByRole('button',{name:'Resume preview'}).click();
    check(await page.locator('#lens-panel').isVisible(),true,'resume locally restores');
    check(await page.locator('#pause').getAttribute('aria-pressed'),'false','thumb reset');
    await page.locator('#evidence summary').click();
    check(await page.locator('#rights').innerText(),'Toy rights status is declared, not independently authorized.','rights truth');

    await page.reload({waitUntil:'load'});
    check(await page.locator('#workid').innerText(),'GDSIDE-5LANE-R0','reload without browser-persistent WorkID');
    check(await page.locator('#receiver').innerText(),'NONE / UNVERIFIED','reload does not upgrade ACK');
    check(await page.evaluate(()=>localStorage.length),0,'not storage as truth root');
    await context.close();
    const fresh=await browser.newContext({viewport:{width:390,height:780},isMobile:true,hasTouch:true});
    await fresh.route('**/*',route=>{
      if(route.request().url()===url||route.request().url().endsWith('/favicon.ico')) route.continue();
      else {externalRequests++;errors.push('HOLD_EXTERNAL_REQUEST');route.abort('blockedbyclient');}
    });
    const page2=await fresh.newPage();
    page2.on('pageerror',e=>errors.push('JS_ERROR:'+e.message));
    await page2.goto(url,{waitUntil:'load'});
    check(await page2.locator('#workid').innerText(),'GDSIDE-5LANE-R0','new context source reentry');
    check(await page2.locator('#truth').innerText(),'SYNTHETIC MODEL ONLY','new context truth');
    check(await page2.locator('#receiver').innerText(),'NONE / UNVERIFIED','new context no ACK');
    check(await page2.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'mobile viewport no horizontal overflow');
    await page2.getByRole('button',{name:'Relations'}).click();
    check(await page2.locator('#lens-title').innerText(),'Relation lens','mobile lens interaction');
    await fresh.close();
    check(errors,[],'no browser errors or outbound network');
    check(externalRequests,0,'no unexpected network requests');
    assert.ok(localRequests>=3);
    const receipt={
      schema:'G_dSide.OneWorkIDLensBrowserReadproof.R0',
      state:'SYNTHETIC_CHROMIUM_LENS_PARITY_AND_REENTRY_PASS',
      work_id:'GDSIDE-5LANE-R0',
      source_model_git_blob_sha1:gitBlob(model),
      source_model_sha256:sha256(model),
      source_html_sha256:sha256(html),
      checks,
      local_page_loads:localRequests,
      unexpected_external_requests:externalRequests,
      model_pareto_frontiers:expected,
      perspectives:['object','relation','interstice','future'],
      lenses_preserve_workid:true,
      receiver_ack:false,
      human_ux_accepted:false,
      live_provider_ingestion:false,
      persistent_agent:false,
      externally_authorized_action:false,
      real_futures_validated:false,
      nonclaims:['BROWSER_SYNTHETIC_NE_HUMAN_ACCEPTANCE','STATIC_HTML_NE_LIVE_COBAR',
        'LOCAL_RELOAD_NE_INDEPENDENT_RECEIVER_PICKUP','G_DSIDE_NE_THEOLOGICAL_AUTHORITY',
        'PINNED_RESEARCH_MODEL_NE_EMPIRICAL_FUTURE_CAUSATION','NOT_CANON','NOT_COEX']
    };
    const out=path.join(root,'out','gdside-lens-r0');
    fs.mkdirSync(out,{recursive:true});
    fs.writeFileSync(path.join(out,'browser-readproof.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
    process.stdout.write(JSON.stringify(receipt)+'\n');
  }finally{
    await browser.close();
  }
}
run().catch(error=>{process.stderr.write('HOLD_BROWSER_LENS='+error.stack+'\n');process.exitCode=1}).finally(()=>{
  server.close();
});
