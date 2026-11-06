'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const raw=fs.readFileSync(path.join(__dirname,'manifest.json'),'utf8');
const manifest=JSON.parse(raw);
const match=html.match(/<script type="application\/json" id="co-manifest">([\s\S]*?)<\/script>/);
if(!match)throw Error('MISSING_PINNED_MANIFEST');
const embedded=JSON.parse(match[1]);
const begin=html.lastIndexOf('<script>');
const end=html.lastIndexOf('</script>');
if(begin<0||end<=begin)throw Error('MISSING_INLINE_JS');
const code=html.slice(begin+8,end);

function setup({clipboardBlocked=false}={}){
  const elements=new Map(),copied=[],calls=[];
  function el(id){
    if(!elements.has(id)){
      elements.set(id,{id,textContent:'',value:'',href:'',style:{display:'none'},
        listeners:new Map(),focus(){this.focused=true;},
        addEventListener(evt,fn){this.listeners.set(evt,fn);},
        setAttribute(name,value){this[name]=value;}});
    }
    return elements.get(id);
  }
  el('co-manifest').textContent=match[1];
  const sandbox={
    document:{getElementById:el,querySelectorAll:()=>[]},
    navigator:{clipboard:{async writeText(value){
      calls.push('clipboard.writeText');
      if(clipboardBlocked)throw Error('synthetic permission refusal');
      copied.push(value);
    }}}
  };
  const context=vm.createContext(sandbox,{name:'OnrampMesh isolated no-network DOM'});
  new vm.Script(code,{filename:'onramp-inline.js'}).runInContext(context,{timeout:1000});
  const make=(route,outcome)=>vm.runInContext(
    'buildEdgeFeedback('+JSON.stringify(route)+','+JSON.stringify(outcome)+')',context,{timeout:1000});
  return {el,context,copied,calls,make};
}
test('01 pinned manifest matches inline machine twin',()=>assert.deepEqual(embedded,manifest));
test('02 no consentless network/data storage API in HTML',()=>{
  assert.match(html,/connect-src 'none'/);
  assert.match(html,/form-action 'none'/);
  assert.doesNotMatch(html,/\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon|localStorage|sessionStorage|indexedDB|setInterval\s*\(/);
});
test('03 no input or clipboard access occurs upon load',()=>{
  const s=setup();assert.deepEqual(s.copied,[]);assert.deepEqual(s.calls,[]);
});
test('04 builder positive completion self-report is unverified',()=>{
  const r=setup().make('builder','helped');
  assert.equal(r.schema,'CoCivium.CoEdgeInFirstUseFeedback.R0');
  assert.equal(r.status,'VOLUNTARY_SELF_REPORT_UNVERIFIED');
  assert.equal(r.route_id,'builder');assert.equal(r.outcome,'helped');
  assert.equal(r.receiver_ack,null);assert.equal(r.transmitted,false);
});
test('05 explorer route stays tied to actual public source',()=>{
  const r=setup().make('explorer','source_unclear');
  assert.equal(r.source_id,'civiclens');assert.match(r.public_source,/github\.com\/CoCivium\/CoAcademy/);
});
test('06 community route preserves no-cross-brand authority',()=>{
  const r=setup().make('community','confusing');
  assert.equal(r.source_id,'coorb');assert.equal(r.transmitted,false);
});
test('07 all five categorical outcomes are allowed but none sent',()=>{
  const s=setup();
  for(const o of ['helped','confusing','not_finished','source_unclear','privacy_concern']){
    const r=s.make('builder',o);assert.equal(r.outcome,o);assert.equal(r.receiver_ack,null);
  }
});
test('08 unknown or invented outcome fails closed',()=>{
  const s=setup();for(const o of ['sent','acknowledged','endorsed','',null,'HELLO_SECRET'])
    assert.equal(s.make('builder',o),null);
});
test('09 unknown route fails closed',()=>{
  assert.equal(setup().make('private_account','helped'),null);
});
test('10 no identity, location, task text or browser content in output',()=>{
  const r=setup().make('explorer','privacy_concern');const j=JSON.stringify(r);
  assert.equal(r.no_identity_or_user_text,true);
  for(const term of ['password','email_address','ip_address','private_note','clipboard_text','user_agent','location','auth_token'])
    assert.equal(Object.hasOwn(r,term),false);
  assert.equal(j.includes('HELLO_SECRET'),false);
});
test('11 ordinary user selection alone does not copy anything',()=>{
  const s=setup();s.el('feedback-outcome').value='helped';assert.equal(s.copied.length,0);
});
test('12 explicit action copies only categorical packet',async()=>{
  const s=setup();s.el('feedback-outcome').value='helped';
  await s.el('feedback-copy').listeners.get('click')();
  const r=JSON.parse(s.copied[0]);assert.equal(r.outcome,'helped');
  assert.equal(r.status,'VOLUNTARY_SELF_REPORT_UNVERIFIED');
  assert.equal(s.el('feedback-status').textContent,'Feedback note copied locally. Nothing was sent.');
});
test('13 missing outcome cannot prepare or copy',async()=>{
  const s=setup();s.el('feedback-outcome').value='';
  await s.el('feedback-copy').listeners.get('click')();
  assert.equal(s.copied.length,0);assert.match(s.el('feedback-status').textContent,/Choose one outcome/);
});
test('14 clipboard refusal creates manual fallback without external effect',async()=>{
  const s=setup({clipboardBlocked:true});s.el('feedback-outcome').value='privacy_concern';
  await s.el('feedback-copy').listeners.get('click')();
  assert.equal(s.copied.length,0);
  assert.equal(s.el('feedback-preview').style.display,'block');
  assert.equal(JSON.parse(s.el('feedback-preview').textContent).receiver_ack,null);
});
test('15 source navigation and GitHub issue remain explicit links',()=>{
  assert.match(html,/Optional issue or challenge/);assert.match(html,/target="_blank" rel="noopener noreferrer"/);
});
test('16 report does not contain visitor answers or invented receiver identity',()=>{
  const s=setup();const r=s.make('builder','helped');const keys=Object.keys(r);
  assert.deepEqual(keys.sort(),[
    'no_identity_or_user_text','note','outcome','public_source','receiver_ack','route_id',
    'schema','source_claim','source_id','status','transmitted'
  ].sort());
});
test('17 private or election-personalized modes do not exist',()=>{
  const s=setup();for(const q of ['targeted_voter','fundraising','surveillance','forced_signup']){
    assert.equal(s.make(q,'helped'),null);
  }
});
