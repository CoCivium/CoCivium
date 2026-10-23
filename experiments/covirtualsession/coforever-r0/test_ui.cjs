'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'CoOrbWare_offline.html'),'utf8');
const source=html.match(/<script type="application\/json" id="source">([\s\S]*?)<\/script>/);
assert(source,'embedded source absent');
const data=JSON.parse(source[1]);
const js=html.match(/<script>\s*([\s\S]*?)<\/script>/);
assert(js,'presentation script absent');
new vm.Script(js[1]);
const buttons=['glance','work','time','proof'].map(name=>({name,attributes:{'data-view':name,'aria-pressed':name==='glance'?'true':'false'},
 handlers:{},addEventListener(event,cb){this.handlers[event]=cb},getAttribute(key){return this.attributes[key]},setAttribute(key,v){this.attributes[key]=v},click(){this.handlers.click()}}));
const els=new Map();for(const id of ['source','option-count','budget-count','child-count','spec','task-list','glance','work','time','proof']){
 els.set(id,{textContent:id==='source'?source[1]:'',classList:{hidden:id!=='glance',toggle(name,val){if(name==='hidden')this.hidden=val}},
 children:[],appendChild(child){this.children.push(child)}});
}
const doc={getElementById:(id)=>els.get(id),createElement:(tag)=>({tag,textContent:''}),querySelectorAll:(query)=>query==='[data-view]'?buttons:[]};
const checks=[];function test(label,fn){fn();checks.push(label)}
vm.runInNewContext(js[1],{document:doc,console},{timeout:500});
test('exact logical space embedded',()=>assert.equal(data.logical_space,'1208925819614629174706176'));
test('visible runtime bound is two',()=>assert.equal(els.get('budget-count').textContent,'2'));
test('completed local subprocess result is four',()=>assert.equal(els.get('child-count').textContent,'4'));
test('source spec bound',()=>assert(els.get('spec').textContent.includes(data.spec_sha256)));
test('public-only list nine entries',()=>assert.equal(els.get('task-list').children.length,9));
test('private source absent even from embedded data',()=>{assert(!html.includes('PRIVATE_NOT_FOR_DISPLAY'));assert(!source[1].includes('UNKNOWN'));});
test('view selector actually toggles',()=>{buttons[1].click();assert.equal(els.get('work').classList.hidden,false);assert.equal(els.get('glance').classList.hidden,true);assert.equal(buttons[1].getAttribute('aria-pressed'),'true');buttons[3].click();assert.equal(els.get('proof').classList.hidden,false)});
test('zero-network strict static view',()=>{assert(html.includes("connect-src 'none'"));for(const forbidden of ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'WebSocket(', 'localStorage', 'sessionStorage'])assert(!js[1].includes(forbidden))});
console.log(JSON.stringify({status:'PASS',tests:checks.length,checks,scope:'NODE_FAKE_DOM_NOT_REAL_BROWSER'}));
