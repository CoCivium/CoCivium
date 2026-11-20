// End-to-end real headless Chrome test against the actual staged CoCopy/CoBar
// owned input surface. No provider targets, OS clipboard, Send, or X2 focus.
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const cp=require('node:child_process');
const page=path.join(__dirname,'copaste_owned_field_r0.html');
if(!fs.existsSync(page))throw Error('HOLD_MISSING_OWNED_FIELD_PAGE');
const html=fs.readFileSync(page,'utf8');
for(const token of ['id="owned-editor"','data-copaste-owned="true"','id="preview"','id="test-consent"','data-proof="NOT_RUN"']){
  if(!html.includes(token))throw Error('HOLD_PAGE_CONTRACT_MISSING '+token);
}
if(/<form\b|<iframe\b|navigator\.clipboard|fetch\(|XMLHttpRequest|<input[^>]+type="password"/i.test(html)){
  throw Error('HOLD_FORBIDDEN_OUTBOUND_OR_CLIPBOARD_SURFACE');
}
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'copaste-ui-r0-'));
try{
  let chrome=process.env.CHROME_BIN||'';
  for(const candidate of ['google-chrome','google-chrome-stable','chromium','chromium-browser']){
    if(chrome)break;
    const r=cp.spawnSync('which',[candidate],{encoding:'utf8'});
    if(r.status===0) chrome=r.stdout.trim();
  }
  if(!chrome)throw Error('HOLD_NO_CHROME_BINARY_ON_RUNNER');
  const run=cp.spawnSync(chrome,[
    '--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',
    '--disable-background-networking','--disable-extensions','--disable-sync',
    '--no-first-run','--no-default-browser-check','--window-size=390,720',
    '--user-data-dir='+path.join(tmp,'profile'),'--dump-dom','file://'+page+'?canary=1'
  ],{encoding:'utf8',timeout:20000,maxBuffer:8*1024*1024});
  if(run.error)throw run.error;
  if(run.status!==0)throw Error('HOLD_CHROME_EXIT_'+run.status+' '+String(run.stderr).slice(-550));
  const proofAttribute=run.stdout.match(/id="proof" data-proof="([^"]+)"/);
  if(!proofAttribute)throw Error('HOLD_NO_REAL_PAGE_DOM_PROOF '+run.stdout.slice(-500));
  const proof=JSON.parse(Buffer.from(proofAttribute[1],'base64').toString('utf8'));
  for(const item of proof.checks||[])console.log((item.pass?'PASS':'FAIL')+'_COCOPY_OWNED_PAGE '+item.name);
  if(proof.checks?.length!==10||proof.checks.some(c=>!c.pass))throw Error('HOLD_OWNED_PAGE_CHECKS');
  if(proof.stats?.events!==1||proof.stats?.send_count!==0||proof.stats?.clipboard_mutations!==0){
    throw Error('HOLD_EVENT_OR_SEND_BOUNDARY');
  }
  const label=run.stdout.match(/id="readback-length">([^<]+)</);
  if(!label || !label[1].includes('Characters:'))throw Error('HOLD_UI_MISSING_VISIBLE_LENGTH');
  if(!run.stdout.includes('id="state-text"')||!run.stdout.includes('id="preview"')){
    throw Error('HOLD_PAGE_NO_ACCESSIBLE_RESULT');
  }
  console.log('COCOPY_OWNED_PAGE_OBSERVATION '+JSON.stringify(proof.stats));
  console.log('PASS_COCOPY_OWNED_PAGE_REAL_CHROME checks='+proof.checks.length+
    ' focus_negative=PASS undo_collision=HELD no_submit=TRUE');
}finally{
  fs.rmSync(tmp,{force:true,recursive:true});
}
