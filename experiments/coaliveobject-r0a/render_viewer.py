#!/usr/bin/env python3
"""Build an offline, illustrative CoOrbWare-style projection from frozen SHADOW evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
trace=json.loads((ROOT/'output/pulse_trace.json').read_text())
summary=json.loads((ROOT/'output/SUMMARY.json').read_text())
manifest=json.loads((ROOT/'manifest.json').read_text())
payload=json.dumps({'trace':trace['trace'],'objects':manifest['objects'],'relations':manifest['relations'],'gaps':manifest['gaps'], 'summary':summary},ensure_ascii=True,separators=(',',':'))
payload=payload.replace('</','<\\/')
html=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CoAliveObject+ R0 | A bounded living-relations pulse</title>
<style>
:root{color-scheme:dark;--ink:#e9f0f2;--muted:#a9bcc2;--line:#334d59;--teal:#65cbbb;--plum:#bcacfb;--warn:#ffcf8e;--surface:#152631;--surface2:#1a303c;--bg:#0a1620}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 85% 6%,#183d49 0%,transparent 50%),var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Arial,sans-serif}main{max-width:1240px;margin:auto;padding:24px 20px 50px}
header{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;padding-bottom:18px;border-bottom:1px solid var(--line)}h1{font-size:clamp(22px,4vw,34px);line-height:1.18;margin:0 0 8px;letter-spacing:-.04em}h2{margin:0 0 12px;font-size:16px;letter-spacing:.01em}p{margin:0 0 10px;color:var(--muted)}.eyebrow{color:var(--teal);font-size:12px;letter-spacing:.15em;text-transform:uppercase;font-weight:700}.badge{color:var(--teal);border:1px solid #568f88;border-radius:99px;padding:5px 10px;font-size:12px;white-space:nowrap}.summary{max-width:790px}.layout{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,1fr);gap:16px;margin-top:18px}.card{background:linear-gradient(135deg,rgba(24,43,56,.98),rgba(15,30,41,.97));border:1px solid var(--line);border-radius:15px;padding:20px;min-width:0}.sub{font-size:13px;color:var(--muted)}.graph-wrap{border:1px solid #2b4854;border-radius:14px;background:#101e28;padding:8px;margin:14px 0}.graph{width:100%;height:auto;display:block}.nodelabel{font-size:13px;fill:#ecf5f7;font-weight:650}.nodesub{font-size:10.5px;fill:#c2d0d6}.edge{stroke:#477480;stroke-width:2;stroke-dasharray:6 5;fill:none}.ring{stroke:#65cbbb;stroke-width:2;fill:#173440}.gapring{stroke:#c09e69;stroke-width:1.5;fill:#32291f;stroke-dasharray:3 4}.rule{border-top:1px solid var(--line);margin:14px 0}.details{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}.measure{border:1px solid #314e59;padding:12px;border-radius:11px}.measure strong{font-size:24px;display:block;color:var(--ink);font-variant-numeric:tabular-nums}.measure span{font-size:11px;color:var(--muted)}.frames{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0 0}.frames button,.objects button{background:var(--surface2);border:1px solid #45606a;color:var(--ink);padding:9px 11px;border-radius:10px;cursor:pointer;font:inherit}.frames button:hover,.objects button:hover{background:#264451}.frames button[aria-pressed="true"],.objects button[aria-pressed="true"]{border-color:var(--teal);box-shadow:0 0 0 1px var(--teal);background:#183e42}.frames button:focus-visible,.objects button:focus-visible{outline:2px solid #fff;outline-offset:2px}.objects{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}.objects button{font-size:13px}.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;overflow-wrap:anywhere}.kv{display:flex;justify-content:space-between;gap:20px;padding:9px 0;border-bottom:1px solid #2d4752}.kv span{color:var(--muted)}.kv strong{font-weight:650;text-align:right}.status{color:var(--teal)}.held{color:var(--warn)}.readout{font-size:13px;line-height:1.55;background:#111e28;border:1px solid #2d4752;padding:12px;border-radius:10px;min-height:89px}.bottom{grid-column:1/-1}.legend{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.legend>div{border-left:2px solid var(--line);padding-left:11px}.legend strong{display:block;margin-bottom:4px}.foot{margin-top:20px;color:var(--muted);font-size:12px}small{font-size:12px}@media(max-width:820px){.layout{grid-template-columns:1fr}.legend{grid-template-columns:1fr}.details{grid-template-columns:repeat(3,minmax(0,1fr))}.card{padding:14px}}@media(max-width:440px){.details{grid-template-columns:1fr 1fr}.graph-wrap{padding:2px}}@media(prefers-reduced-motion:no-preference){button{transition:background .15s}}
</style></head><body><main>
<header><div><div class="eyebrow">CoOmni+ / CoFractal / CoEvergreen</div><h1>CoAliveObject+ <span style="color:var(--teal)">Pulse R0</span></h1><p class="summary">Objects can carry wake conditions, relations, evidence, and recovery paths without staying awake. Inspect one frozen, bounded research run. This is not a live fleet, operating-system service, or actual CoVIA delivery.</p></div><span class="badge">OFFLINE · SHADOW · NO NETWORK</span></header>
<div class="layout">
<section class="card" aria-labelledby="graph-title"><h2 id="graph-title">CoMap / CoOrb: three types, one shared work field</h2><p class="sub">Dashed lines are proposed relations, not verified causal or authorized transfers.</p>
<div class="graph-wrap"><svg class="graph" viewBox="0 0 620 330" role="img" aria-label="Triangle of Mouse software, First Door publication, Recovery work; a separate amber gap denotes missing independent receiver proof">
<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#477480"/></marker></defs>
<path class="edge" d="M174 96L427 96" marker-end="url(#arrow)"/><path class="edge" d="M463 125L338 255" marker-end="url(#arrow)"/><path class="edge" d="M268 255L150 125" marker-end="url(#arrow)"/>
<circle class="ring" cx="132" cy="96" r="58"/><text class="nodelabel" x="132" y="91" text-anchor="middle">CoMouse</text><text class="nodesub" x="132" y="109" text-anchor="middle">software</text>
<circle class="ring" cx="486" cy="96" r="58"/><text class="nodelabel" x="486" y="91" text-anchor="middle">CoSpiff</text><text class="nodesub" x="486" y="109" text-anchor="middle">publication</text>
<circle class="ring" cx="303" cy="263" r="58"/><text class="nodelabel" x="303" y="258" text-anchor="middle">CoScale</text><text class="nodesub" x="303" y="276" text-anchor="middle">dormant work</text>
<circle class="gapring" cx="500" cy="250" r="34"/><text x="500" y="246" fill="#ffcf8e" font-size="11" font-weight="700" text-anchor="middle">ACK?</text><text x="500" y="259" fill="#ffcf8e" font-size="9" text-anchor="middle">gap held</text>
</svg></div>
<div class="details" aria-live="polite"><div class="measure"><strong id="work-count">0</strong><span>Proposals this pulse</span></div><div class="measure"><strong id="pending-count">0</strong><span>Pending, not completed</span></div><div class="measure"><strong id="effects-count">0</strong><span>External effects</span></div></div>
<div class="rule"></div><h2>Inspect a recorded pulse</h2><div class="frames" role="group" aria-label="Recorded synthetic pulse scenarios" id="frames"></div><div class="readout" id="pulse-detail" aria-live="polite"></div>
</section>
<section class="card"><h2>CoObject state and wake contract</h2><p class="sub">Only one selected description is displayed. All four cases preserve their own identity and authority limits.</p><div class="objects" role="group" aria-label="Choose object" id="objects"></div>
<div class="kv"><span>Source</span><strong id="obj-id" class="mono"></strong></div><div class="kv"><span>Currentness</span><strong class="held">Pinned, not continuously fetched</strong></div><div class="kv"><span>Authority</span><strong class="status">NONE</strong></div><div class="kv"><span>Wake rule</span><strong id="obj-wake"></strong></div><div class="kv"><span>Review period</span><strong id="obj-period"></strong></div><div class="kv"><span>Recovery identity</span><strong id="obj-sha" class="mono"></strong></div><div class="rule"></div><h2>Observed vs. proposed</h2><p class="sub">These statuses are not interchangeable.</p><div class="kv"><span>Pulse simulation</span><strong class="status">Passed local tests</strong></div><div class="kv"><span>Physical X2 gesture</span><strong class="held">NOT RUN</strong></div><div class="kv"><span>Receiver independent ACK</span><strong class="held">HOLD</strong></div><div class="kv"><span>Autonomous new workers</span><strong>0</strong></div><div class="kv"><span>Long-running scheduler</span><strong>Not installed</strong></div>
</section>
<section class="card bottom"><h2>Why the engine doesn't amplify everything immediately</h2><div class="legend"><div><strong>CoAmp+ proposes, measures, and retains failures.</strong><p>Object and relationship exploration are bounded by hops, queue capacity, and review budget. A loop must stop.</p></div><div><strong>CoWake+ requires a material condition.</strong><p>An ordinary heartbeat is not evidence that anything changed. Dormancy conserves capacity and attention.</p></div><div><strong>CoAckRAW+ does not invent delivery.</strong><p>A proposed relation, source hash, or GitHub pointer cannot impersonate recipient pickup, permission, or adoption.</p></div></div><div class="foot mono">CoAliveObjectManifest/R0 · 3 pinned public source objects · synthetic fixture · one provenance spine · no actual persistent timer</div></section>
</div></main><script id="data" type="application/json">__JSON_DATA__</script><script>
'use strict';
const data=JSON.parse(document.getElementById('data').textContent);
const frames=document.getElementById('frames');
const objects=document.getElementById('objects');
const format=(n)=>String(n);
function showFrame(index){
 const entry=data.trace[index], result=entry.result;
 for(const button of frames.querySelectorAll('button'))button.setAttribute('aria-pressed',String(Number(button.dataset.index)===index));
 document.getElementById('work-count').textContent=format(result.processed_count);
 document.getElementById('pending-count').textContent=format(result.pending_count);
 document.getElementById('effects-count').textContent=format(result.external_effects);
 let holds=result.admissions.filter(e=>e.outcome.startsWith('HOLD_')).map(e=>e.outcome).join(', ');
 document.getElementById('pulse-detail').textContent='Tick '+entry.observed_tick+' · '+entry.label+'. '+result.processed_count+' candidate proposals; '+result.pending_count+' remain queued. '+(holds?'Explicit hold: '+holds+'. ':'')+'No provider calls or receiver acknowledgments observed.';
}
for(let i=0;i<data.trace.length;i++){let b=document.createElement('button');b.type='button';b.dataset.index=String(i);b.textContent='Tick '+data.trace[i].observed_tick;b.addEventListener('click',()=>showFrame(i));frames.appendChild(b)}
function showObject(index){
 const obj=data.objects[index];
 for(const button of objects.querySelectorAll('button'))button.setAttribute('aria-pressed',String(Number(button.dataset.index)===index));
 document.getElementById('obj-id').textContent=obj.id;
 document.getElementById('obj-wake').textContent=obj.metabolism.WAKE;
 document.getElementById('obj-period').textContent='every '+obj.review_period_ticks+' logical ticks';
 document.getElementById('obj-sha').textContent=obj.source.git_blob_sha1.slice(0,14)+'…';
}
for(let i=0;i<data.objects.length;i++){let b=document.createElement('button');b.type='button';b.dataset.index=String(i);b.textContent=data.objects[i].id;b.addEventListener('click',()=>showObject(i));objects.appendChild(b)}
showFrame(0);showObject(0);
</script></body></html>
'''.replace('__JSON_DATA__',payload)
(ROOT/'CoAliveObject_Viewer.html').write_text(html,encoding='utf-8')
print('Viewer',len(html.encode()),'bytes','frames',len(trace['trace']))
