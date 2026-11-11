// CoBar R4b: portable, dependency-free synthetic interaction contract.
// A DOM shim is not a browser, a human acceptance test, or receiver proof.
// Run: node examples/cobar/interaction_r4b.cjs
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const crypto=require('node:crypto');
const assert=require('node:assert/strict');

const sourcePath=process.env.COBAR_HTML_PATH||path.join(__dirname,'copre_local_io_r4b.html');
const bytes=fs.readFileSync(sourcePath);
const html=bytes.toString('utf8');
const sha256=crypto.createHash('sha256').update(bytes).digest('hex').toUpperCase();
assert.equal(sha256,'D56DF449DF491EC38F0D9B963B1B3D93DBC04FAEB7E1B3C8679462E3B39A2B72',
  'source bytes differ from X2 first-use browser-tested HTML');
const inline=[...html.matchAll(/<script>([\s\S]*?)<\/script>/gi)];
assert.equal(inline.length,1,'exactly one inline script is expected');
for(const marker of [
  'id="io-command"','id="io-submit"','id="io-stop"','id="io-consent"',
  'aria-live="polite"','aria-atomic="true"','CO-SESSION-RECOVERY',
  'No external delivery or deletion','NAS-native ACK not observed'
]) assert(html.includes(marker),'missing visible control/rail '+marker);
assert(!/<script\s+[^>]*src=|<iframe|XMLHttpRequest|navigator\.sendBeacon/i.test(html),
  'unexpected browser external adapter');

const key='CoCivium.CoBar.CoPreLocalIO.R4.Synthetic.R0';
const work='CO-SESSION-RECOVERY::LOCAL-SYNTHETIC-R0';
const snapshot='BB1483149B30A336617805CDF3AF02483EA3A46A8347C8220602E1DCB7AE0B6A';
function makeBrowser(storage=new Map(),opts={}){
  const elements=new Map();
  const writes=[];
  function el(id){
    if(!elements.has(id)){
      const node={
        id,value:'',checked:false,hidden:id==='evidence',textContent:'',
        attrs:{},listeners:{},
        addEventListener(event,fn){(this.listeners[event]??=[]).push(fn);},
        setAttribute(name,value){this.attrs[name]=value;},
        getAttribute(name){return this.attrs[name]??null;},
        click(){for(const fn of this.listeners.click||[])fn({target:this});},
        keydown(key){for(const fn of this.listeners.keydown||[])fn({
          key,preventDefault(){this.defaultPrevented=true;}
        });},
        scrollIntoView(){},
      };
      if(id==='evidence-toggle')node.attrs['aria-expanded']='false';
      elements.set(id,node);
    }
    return elements.get(id);
  }
  const document={
    getElementById:el,
    listeners:{},
    addEventListener(event,fn){(this.listeners[event]??=[]).push(fn);},
    keydown(key){for(const fn of this.listeners.keydown||[])fn({key});}
  };
  const localStorage={
    getItem(id){
      if(opts.failRead)throw Error('simulated storage read unavailable');
      return storage.has(id)?storage.get(id):null;
    },
    setItem(id,value){
      if(opts.failWrite)throw Error('simulated storage write unavailable');
      writes.push({id,value});
      storage.set(id,String(value));
    }
  };
  vm.runInNewContext(inline[0][1],{document,localStorage,console},{timeout:1500});
  return {
    el,document,storage,writes,
    get state(){return el('io-state').textContent;},
    get response(){return el('io-response').textContent;},
    get raw(){return storage.get(key);},
    get record(){return storage.has(key)?JSON.parse(storage.get(key)):null;},
    consent(){el('io-consent').checked=true;},
    command(value){el('io-command').value=value;},
    submit(){el('io-submit').click();},
    stop(){el('io-stop').click();}
  };
}

let count=0;
function test(label,fn){fn();count++;console.log('PASS_COBAR '+label);}
let m=new Map(),app=makeBrowser(m);
test('empty untouched first load',()=>{
  assert.equal(app.state,'EMPTY');
  assert.equal(m.size,0);
});
test('unconsented request cannot commit',()=>{
  app.command('recovery status');app.submit();
  assert.equal(app.state,'HELD_CONSENT_REQUIRED');
  assert.equal(app.writes.length,0);
});
test('unsupported command fails closed',()=>{
  app.consent();app.command('delete all');app.submit();
  assert.equal(app.state,'HELD_UNSUPPORTED_COMMAND');
  assert.equal(app.writes.length,0);
});
test('normalization allows one supported command',()=>{
  app.command('  ReCoVeRy    Status ');app.submit();
  assert.equal(app.state,'LOCAL_COMMITTED');
  assert.equal(app.record.command,'recovery status');
  assert.equal(app.record.result_code,'LOCAL_RECOVERY_SNAPSHOT');
  assert.equal(app.writes.length,1);
});
test('record is exact local-only and not external ACK',()=>{
  assert.equal(app.record.work_id,work);
  assert.equal(app.record.source_sha256,snapshot);
  assert.equal(app.record.effect_count,1);
  assert.equal(app.record.receipt_state,'BROWSER_LOCAL_ONLY');
  assert.equal(app.record.receiver_ack,false);
  assert.equal(app.record.consent_epoch,1);
  assert(app.response.includes('Useful-task resumption unproven'));
});
test('duplicate retry creates no second commit',()=>{
  const original=app.raw;app.command('recovery status');app.submit();
  assert.equal(app.state,'DUPLICATE_SUPPRESSED');
  assert.equal(app.raw,original);
  assert.equal(app.writes.length,1);
});
test('conflicting command cannot clobber work id',()=>{
  const original=app.raw;app.command('why held');app.submit();
  assert.equal(app.state,'HELD_WORKID_CONFLICT');
  assert.equal(app.raw,original);
});
test('fresh browser context recovers local record',()=>{
  app=makeBrowser(m);
  assert.equal(app.state,'RECOVERED_LOCAL_ONLY');
  assert.equal(app.el('io-consent').checked,false);
  assert.equal(app.writes.length,0);
});
test('stop revokes one local record',()=>{
  const before=app.record.created_utc;app.stop();
  assert.equal(app.state,'REVOKED_LOCAL');
  assert.equal(app.record.state,'REVOKED');
  assert.equal(app.record.created_utc,before);
  assert.equal(app.record.receiver_ack,false);
});
test('repeated stop is idempotent',()=>{
  const original=app.raw,prior=app.writes.length;app.stop();
  assert.equal(app.state,'HELD_REVOKED');
  assert.equal(app.raw,original);
  assert.equal(app.writes.length,prior);
});
test('revocation persists through reload',()=>{
  app=makeBrowser(m);
  assert.equal(app.state,'HELD_REVOKED');
  assert.equal(app.el('io-consent').checked,false);
});
test('revoked request does not restart work',()=>{
  const original=app.raw;app.consent();app.command('recovery status');app.submit();
  assert.equal(app.state,'HELD_REVOKED');
  assert.equal(app.raw,original);
});
test('corrupted local state is held without overwrite',()=>{
  const store=new Map([[key,'{"unexpected":"data"}']]),testApp=makeBrowser(store);
  assert.equal(testApp.state,'HELD_CONFLICT');
  testApp.consent();testApp.command('recovery status');testApp.submit();
  assert.equal(testApp.state,'HELD_CONFLICT');
  assert.equal(testApp.writes.length,0);
});
test('oversized local state is held',()=>{
  const testApp=makeBrowser(new Map([[key,'x'.repeat(4097)]]));
  assert.equal(testApp.state,'HELD_CONFLICT');
});
test('unavailable storage fails closed',()=>{
  let a=makeBrowser(new Map(),{failRead:true});
  assert.equal(a.state,'HELD_STORAGE_UNAVAILABLE');
  a.consent();a.command('recovery status');a.submit();
  assert.equal(a.state,'HELD_STORAGE_UNAVAILABLE');
  a=makeBrowser(new Map(),{failWrite:true});
  a.consent();a.command('recovery status');a.submit();
  assert.equal(a.state,'HELD_STORAGE_UNAVAILABLE');
});
test('evidence toggles and Escape closes',()=>{
  const a=makeBrowser();
  assert.equal(a.el('evidence').hidden,true);
  a.el('evidence-toggle').click();
  assert.equal(a.el('evidence').hidden,false);
  assert.equal(a.el('evidence-toggle').getAttribute('aria-expanded'),'true');
  a.document.keydown('Escape');
  assert.equal(a.el('evidence').hidden,true);
  assert.equal(a.el('evidence-toggle').getAttribute('aria-expanded'),'false');
});
test('fabricated well-formed local record remains untrusted',()=>{
  // A client-controlled store is not authenticated. The predictable
  // acceptance here is a documented NEGATIVE proof boundary.
  const fixture=JSON.parse(m.get(key));
  fixture.state='ACTIVE';
  fixture.revoked_utc=null;
  const a=makeBrowser(new Map([[key,JSON.stringify(fixture)]]));
  assert.equal(a.state,'RECOVERED_LOCAL_ONLY');
  assert.equal(a.el('io-consent').checked,false);
});
test('Enter cannot bypass explicit consent',()=>{
  const a=makeBrowser();
  a.command('recovery status');
  a.el('io-command').keydown('Enter');
  assert.equal(a.state,'HELD_CONSENT_REQUIRED');
  assert.equal(a.writes.length,0);
});
assert.equal(count,18);
console.log('PASS_COBAR_R4B_PUBLIC_SOURCE_DOM_CONTRACT tests='+count+
  ' source_sha256='+sha256+' effects=browser_local_only receiver_ack=UNPROVEN');
