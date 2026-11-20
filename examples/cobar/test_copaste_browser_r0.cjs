// CoPaste isolated real-browser DOM canary, synthetic owned textarea only.
// No clipboard/HID/provider chat/network/Send, no X2 user surface changes.
'use strict';
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const cp=require('node:child_process');

function runInBrowser() {
  const checks=[];
  const check=(name,pass)=>checks.push({name,pass:!!pass});
  const field=document.getElementById('owned-input');
  let inputEvents=0,submitted=0,keydowns=0,nativeCalls=0;
  field.addEventListener('input',()=>inputEvents++);
  field.addEventListener('keydown',()=>keydowns++);
  document.getElementById('testform').addEventListener('submit',e=>{submitted++;e.preventDefault()});
  const original=field.setRangeText.bind(field);
  field.setRangeText=function(){nativeCalls++;return original(...arguments)};
  field.focus();
  const payload='First\r\nSecond\nThird 🌍 𝄞';
  const engine=createCoPasteR0();
  const before=performance.now();
  const result=engine.insert({target:field,expectedTargetId:'owned-input',
    requestId:'native-browser-test-1',payload,expectedValue:'',authorized:true});
  const elapsed=performance.now()-before;
  check('exactly_one_native_dom_insertion',nativeCalls===1);
  check('real_textarea_newline_and_unicode',field.value===payload.replace(/\r\n?/g,'\n'));
  check('reported_verified_after_dom_normalization',result.state==='INSERTED_VERIFIED_TEXT_VALUE');
  check('no_submit_or_simulated_typing',submitted===0&&keydowns===0);
  const retry=engine.insert({target:field,expectedTargetId:'owned-input',requestId:'native-browser-test-1',
    payload,expectedValue:field.value,authorized:true});
  check('retry_does_not_duplicate',retry.state==='DUPLICATE_SUPPRESSED'&&nativeCalls===1);
  check('first_input_event_dispatched_once',inputEvents===1);
  const long=('data\r\n🌍').repeat(10000);
  const longBefore=performance.now();
  const second=engine.insert({target:field,expectedTargetId:'owned-input',
    requestId:'native-browser-test-long',payload:long,expectedValue:field.value,authorized:true});
  const largeElapsed=performance.now()-longBefore;
  check('long_multiline_bulk_native_one_call',second.state==='INSERTED_VERIFIED_TEXT_VALUE'&&nativeCalls===2);
  check('long_multiline_semantics_preserved',field.value.endsWith(long.replace(/\r\n?/g,'\n')));
  check('second_input_event_dispatched_once',inputEvents===2);
  check('focus_remained_on_owned_field',document.activeElement===field);
  const obs={insertion_calls:nativeCalls,input_events:inputEvents,elapsed_ms:elapsed,large_elapsed_ms:largeElapsed,
    payload_characters:payload.length,value_characters:field.value.length,
    insert_state:result.state,retry_state:retry.state,no_send:submitted===0};
  document.getElementById('proof').setAttribute('data-proof',btoa(JSON.stringify({checks,obs})));
}
const source=fs.readFileSync(path.join(__dirname,'copaste_bulk_r0.cjs'),'utf8');
if(source.toLowerCase().includes('</script')) throw Error('HOLD_UNSAFE_EMBEDDED_SOURCE');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'copaste-dom-'));
try {
  const testHTML='<!doctype html><html><head><meta charset="utf-8"></head><body>'+
    '<form id="testform"><textarea id="owned-input" data-copaste-owned="true"></textarea></form>'+
    '<pre id="proof" data-proof="NOT_RUN"></pre>'+
    '<script>'+source+'</script><script>('+runInBrowser.toString()+')();</script></body></html>';
  const fixture=path.join(tmp,'fixture.html');
  fs.writeFileSync(fixture,testHTML,'utf8');
  let chrome=process.env.CHROME_BIN||'';
  for(const candidate of ['google-chrome','google-chrome-stable','chromium','chromium-browser']){
    if(chrome)break;
    const r=cp.spawnSync('which',[candidate],{encoding:'utf8'});
    if(r.status===0)chrome=r.stdout.trim();
  }
  if(!chrome)throw Error('HOLD_NO_CHROME_BINARY_ON_RUNNER');
  const p=cp.spawnSync(chrome,['--headless=new','--no-sandbox','--disable-gpu',
    '--disable-background-networking','--disable-extensions','--disable-sync','--disable-dev-shm-usage',
    '--no-first-run','--no-default-browser-check','--user-data-dir='+path.join(tmp,'profile'),
    '--dump-dom','file://'+fixture],{encoding:'utf8',timeout:20000,maxBuffer:8*1024*1024});
  if(p.error)throw p.error;
  if(p.status!==0)throw Error('HOLD_CHROME_EXIT_'+p.status+' '+String(p.stderr).slice(-600));
  const m=p.stdout.match(/id="proof" data-proof="([^"]+)"/);
  if(!m)throw Error('HOLD_NO_BROWSER_DOM_PROOF '+p.stdout.slice(-600));
  const proof=JSON.parse(Buffer.from(m[1],'base64').toString('utf8'));
  for(const item of proof.checks)console.log((item.pass?'PASS':'FAIL')+'_COPASTE_REAL_BROWSER '+item.name);
  console.log('COPASTE_REAL_BROWSER_OBSERVATION '+JSON.stringify(proof.obs));
  const failed=proof.checks.filter(x=>!x.pass);
  if(failed.length)throw Error('HOLD_REAL_BROWSER '+failed.map(x=>x.name).join(','));
  console.log('PASS_COPASTE_REAL_BROWSER_DOM_CANARY checks='+proof.checks.length+' sends=0 clipboard=0');
} finally {
  fs.rmSync(tmp,{recursive:true,force:true});
}
