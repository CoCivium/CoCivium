'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const vm=require('node:vm');
const root=path.resolve(__dirname,'../..');
const read=p=>fs.readFileSync(p,'utf8');
const html=read(path.join(__dirname,'index.html'));
const snap=JSON.parse(read(path.join(__dirname,'snapshot.json')));
const ledgerText=read(path.join(root,'ai/benchmark-evo.jsonl'));
const scoreText=read(path.join(root,'docs/Metrics/COSPEEDO_7DAY_SCORECARD_R0_20261026.json'));
const rows=ledgerText.trim().split('\n').map(JSON.parse);
const score=JSON.parse(scoreText);
const gitBlobSha=data=>crypto.createHash('sha1').update('blob '+Buffer.byteLength(data)+'\0').update(data).digest('hex');
const embeddedMatch=html.match(/<script type="application\/json" id="source-snapshot">([\s\S]*?)<\/script>/);
const embedded=embeddedMatch?JSON.parse(embeddedMatch[1]):null;
const mathMatch=html.match(/\/\* CO_METRIC_MATH_BEGIN \*\/([\s\S]*?)\/\* CO_METRIC_MATH_END \*\//);
const math=mathMatch?vm.runInNewContext(mathMatch[1]+'\n;({temporalExponent,scalingExponent,leastSquares})'):null;

test('01 schema and bounded state, no live claim',()=>{
 assert.equal(snap.schema,'CoSpeedo.CoValGrowthFirstView.R0');
 assert.match(snap.state,/STATIC_PUBLIC_SOURCE_SNAPSHOT/);
 assert.match(snap.state,/OUTCOME_GROWTH_UNQUALIFIED/);
});
test('02 exact source blobs pinned',()=>{
 assert.equal(gitBlobSha(ledgerText),snap.sources.scoped_evidence.blob_sha);
 assert.equal(gitBlobSha(scoreText),snap.sources.metric_policy.blob_sha);
});
test('03 145 strict source rows with unique evidence IDs',()=>{
 assert.equal(rows.length,145);
 assert.equal(new Set(rows.map(x=>x.id)).size,rows.length);
});
test('04 each source row has admissible status and day',()=>{
 for(const r of rows){assert.ok(['PASS','HELD','FAIL'].includes(r.status));
 assert.match(String(r.observed_at),/^\d{4}-\d{2}-\d{2}/);}
});
test('05 exact global counts from raw ledger',()=>{
 const c={PASS:0,HELD:0,FAIL:0};for(const r of rows)c[r.status]++;
 assert.equal(snap.counts.scoped_ledger_events,rows.length);
 assert.equal(snap.counts.PASS,c.PASS);
 assert.equal(snap.counts.HELD,c.HELD);
 assert.equal(snap.counts.FAIL,c.FAIL);
 assert.equal(c.PASS+c.HELD+c.FAIL,rows.length);
});
test('06 no ledger date count beyond observed source',()=>{
 const a=new Map();
 for(const r of rows){
  const day=r.observed_at.slice(0,10);a.set(day,(a.get(day)||0)+1);
 }
 for(const w of snap.windows){
  if(a.has(w.date))assert.equal(w.total,a.get(w.date));
  else assert.equal(w.total,null);
 }
});
test('07 seven windows match original scorecard dates and classes',()=>{
 assert.equal(snap.windows.length,7);
 assert.deepEqual(snap.windows.map(x=>x.date),score.windows.map(x=>x.date));
 assert.deepEqual(snap.windows.map(x=>x.scorecard_state),score.windows.map(x=>x.status));
});
test('08 unknown days are never fabricated zeros',()=>{
 for(const day of ['2026-10-20','2026-10-21','2026-10-22']){
  const w=snap.windows.find(w=>w.date===day);
  assert.equal(w.coverage,'UNKNOWN');
  for(const k of ['pass','held','fail','total','closure','atomic_debt','human_relay'])assert.equal(w[k],null);
 }
});
test('09 verified receiver metrics remain explicitly unknown across windows',()=>{
 for(const w of snap.windows){
  for(const k of ['closure','atomic_debt','human_relay','receiver_returns','recovery','observed_cost'])assert.equal(w[k],null);
 }
 assert.equal(snap.coval.value,null);
 assert.equal(snap.coval.exponential_time_rate_lambda,null);
 assert.equal(snap.coval.historical_scaling_exponent_beta,null);
 assert.equal(snap.coval.tested_exponential_growth,false);
});
test('10 exact embedded source snapshot matches standalone JSON',()=>{
 assert.ok(embedded);
 assert.deepEqual(embedded,snap);
});
test('11 accessible offline dashboard with no third-party fetch or auto-recurrence',()=>{
 assert.match(html,/<html lang="en">/);
 assert.match(html,/aria-label="Historical measurement views"/);
 assert.match(html,/id="coverage"/);
 assert.match(html,/prefers-reduced-motion/);
 for(const forbidden of [/<script[^>]+src=/i,/<link[^>]+rel="stylesheet"/i,/\bfetch\s*\(/i,/\bWebSocket\s*\(/,/\bsetInterval\s*\(/,/\blocalStorage\b/,/\bnavigator\.clipboard\b/])assert.doesNotMatch(html,forbidden);
});
test('12 visible controls have all three functioning modes',()=>{
 for(const mode of ['activity','value','exponent'])assert.match(html,new RegExp('data-mode="'+mode+'"'));
 assert.match(html,/addEventListener\('click',\(\)=>showMode/);
 assert.match(html,/HELD_INSUFFICIENT_COMPARABLE_VALUE_WINDOWS/);
});
test('13 no invalid static live wording',()=>{
 assert.match(html,/STATIC SOURCE SNAPSHOT/);
 assert.match(html,/NOT LIVE X2/);
 assert.match(html,/not receiver closures/i);
 assert.match(html,/UNKNOWN, not zero/);
});
test('14 formula helpers are extractable and deterministic',()=>{
 assert.ok(math);
 assert.equal(typeof math.temporalExponent,'function');
 assert.equal(typeof math.scalingExponent,'function');
});
test('15 no temporal exponential from short or empty data',()=>{
 assert.equal(math.temporalExponent([]).status,'HELD_INSUFFICIENT_COMPARABLE_VALUE_WINDOWS');
 assert.equal(math.temporalExponent([{date:'2026-10-20',value:1}]).lambda,null);
});
test('16 fails closed when receiver or cost evidence is missing',()=>{
 const x=[1,2,4,8].map((value,i)=>({date:'2026-10-'+(20+i),value,independent_receiver:false,cost_qualified:true}));
 const r=math.temporalExponent(x);assert.equal(r.lambda,null);
 assert.equal(r.status,'HELD_RECEIVER_COST_OR_VALUE_GAP');
});
test('17 known synthetic doubling has mathematical rate only',()=>{
 const x=[1,2,4,8].map((value,i)=>({date:'2026-10-'+(20+i),value,independent_receiver:true,cost_qualified:true}));
 const r=math.temporalExponent(x);
 assert.equal(r.status,'EXPONENTIAL_CANDIDATE_ONLY');
 assert.ok(Math.abs(r.lambda-Math.LN2)<1e-9);
 assert.ok(Math.abs(r.doubling_days-1)<1e-9);
});
test('18 temporal chronology is mandatory',()=>{
 const x=[1,2,4,8].map((value,i)=>({date:'2026-10-'+(20+i),value,independent_receiver:true,cost_qualified:true}));
 x[3].date='2026-10-19';
 assert.equal(math.temporalExponent(x).status,'HELD_NON_MONOTONIC_DATES');
});
test('19 scaling exponent beta is mathematically distinct from lambda',()=>{
 const x=[1,2,4,8].map(scale=>({scale,value:scale*scale,independent_receiver:true,cost_qualified:true}));
 const r=math.scalingExponent(x);
 assert.equal(r.status,'POWER_LAW_CANDIDATE_ONLY');
 assert.ok(Math.abs(r.beta-2)<1e-9);
 assert.ok(Math.abs(r.r2-1)<1e-9);
});
test('20 scaling returns unknown with too few independent scales',()=>{
 const x=[1,2,2,2].map(scale=>({scale,value:scale*scale,independent_receiver:true,cost_qualified:true}));
 assert.equal(math.scalingExponent(x).status,'HELD_INSUFFICIENT_DISTINCT_SCALES');
});
test('21 held and failed ledger statuses are not automatically value regressions',()=>{
 assert.equal(snap.coval.valid_receiver_value_windows,0);
 assert.equal(snap.coval.valid_scale_pairs,0);
 assert.match(snap.limitations.join(' '),/not exhaustive daily task attempts/);
});
test('22 proof and unknown statuses remain clearly named',()=>{
 assert.match(html,/CoAtomicDebt trend/);
 assert.match(html,/Human relay per closure/);
 assert.match(html,/Golden Braid/);
 assert.match(html,/Receiver \?/);
 assert.match(html,/Effect \?/);
 assert.match(html,/CoVal is provisional/);
});

function runOfflineDashboardInFakeDOM(){
 class FakeElement{
  constructor(tag){this.tagName=tag;this.children=[];this.attributes={};this.handlers={};this.dataset={};this.textContent='';this.hidden=false;}
  setAttribute(k,v){this.attributes[k]=String(v);}
  appendChild(x){this.children.push(x);return x;}
  replaceChildren(...xs){this.children=[...xs];}
  addEventListener(kind,cb){this.handlers[kind]=cb;}
 }
 const keys=['source-snapshot','ledger-total','passes','held','failed','stamp','ledger-link','scorecard-link','coverage','chart-slot','chart-explainer','chart-scope','legend'];
 const elements=Object.fromEntries(keys.map(k=>[k,new FakeElement('div')]));
 elements['source-snapshot'].textContent=JSON.stringify(snap);
 const buttons=['activity','value','exponent'].map(mode=>{const b=new FakeElement('button');b.dataset={mode};return b;});
 const document={
  getElementById(id){if(!(id in elements))throw Error('Unknown UI id: '+id);return elements[id];},
  querySelectorAll(sel){assert.equal(sel,'[data-mode]');return buttons;},
  createElement(tag){return new FakeElement(tag);},
  createElementNS(ns,tag){assert.equal(ns,'http://www.w3.org/2000/svg');return new FakeElement(tag);}
 };
 const script=html.match(/<script>\s*("use strict";[\s\S]*?)<\/script>/);
 assert.ok(script,'inline dashboard runtime script missing');
 vm.runInNewContext(script[1],{document},{timeout:1500});
 return {elements,buttons};
}
test('23 offline HTML runtime produces seven real source rows and one SVG chart',()=>{
 const {elements,buttons}=runOfflineDashboardInFakeDOM();
 assert.equal(elements.coverage.children.length,7);
 assert.equal(elements['chart-slot'].children[0].tagName,'svg');
 assert.equal(String(elements['ledger-total'].textContent),'145');
 assert.equal(buttons[0].attributes['aria-pressed'],'true');
});
test('24 toggling receiver view refuses to invent CoVal data',()=>{
 const {elements,buttons}=runOfflineDashboardInFakeDOM();
 buttons[1].handlers.click();
 assert.equal(elements['chart-slot'].children[0].tagName,'div');
 assert.match(elements['chart-slot'].children[0].textContent,/CoVal and useful closures are UNKNOWN/);
 assert.equal(elements['chart-scope'].textContent,'Receiver outcome: HELD');
 assert.equal(buttons[1].attributes['aria-pressed'],'true');
});
test('25 exponent view stays held and returning to activity redraws the SVG',()=>{
 const {elements,buttons}=runOfflineDashboardInFakeDOM();
 buttons[2].handlers.click();
 assert.match(elements['chart-slot'].children[0].textContent,/HELD_RECEIVER_COST_OR_VALUE_GAP/);
 assert.match(elements['chart-slot'].children[0].textContent,/HELD_INSUFFICIENT_SCALE_PAIRS/);
 buttons[0].handlers.click();
 assert.equal(elements['chart-slot'].children[0].tagName,'svg');
 assert.equal(elements.legend.hidden,false);
});
