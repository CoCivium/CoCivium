#!/usr/bin/env python3
"""Build local file-friendly read-only HTML from already synthetic outputs."""
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def safe_json(obj):
    return json.dumps(obj,ensure_ascii=True,sort_keys=True,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')

def build():
    d=json.loads((ROOT/'output/shadow_candidates.json').read_text(encoding='utf-8'))
    z=json.loads((ROOT/'output/cozombie_triage.json').read_text(encoding='utf-8'))
    b=json.loads((ROOT/'output/challenge.json').read_text(encoding='utf-8'))
    assert d['no_effects'] and d['actual_experiments_run']==0 and len(d['candidates'])<=16
    assert z['agents_restarted']==0
    title='CoDoodleNexus+ | CoIn / CoInv / CoOut'
    page=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'">
<title>CO_TITLE</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#d7e7ee;background:#0b111b}
*{box-sizing:border-box} body{margin:0;line-height:1.45}main{max-width:1200px;margin:auto;padding:clamp(16px,4vw,40px)}h1{font-size:clamp(1.8rem,4vw,3rem);margin:.3em 0}h2{font-size:1.15rem}
.eyebrow{letter-spacing:.18em;text-transform:uppercase;color:#7dd9ce;font-size:.76rem}.sub{color:#9bb1c0;max-width:72ch}a{color:#96e4da}
.hero{border:1px solid #355164;border-radius:20px;padding:24px;background:radial-gradient(ellipse at 82% 20%,#153e44,#131827 48%,#0c1520)}
.stats{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.stat{flex:1;min-width:145px;border:1px solid #314455;padding:13px;border-radius:13px;background:#13212d}
.stat b{display:block;color:#fff;font-size:1.25rem}.stat small{color:#a6bac7}
.orbit{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:22px 0;padding:16px;border-radius:16px;border:1px solid #355264}
.orbit span{background:#142b38;padding:10px 12px;border-radius:99px}.orbit .arrow{background:none;color:#70cecd;font-size:1.1rem}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}button{background:#1c3546;color:#e6fbff;border:1px solid #496578;border-radius:10px;padding:9px 13px;cursor:pointer;font:inherit}
button:hover,button:focus-visible{outline:2px solid #80dfd3}button[aria-pressed="true"]{background:#155456;border-color:#70cecd}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}.card{border:1px solid #324957;background:#101e2a;border-radius:14px;padding:15px}
.card h3{font-size:1rem;margin:5px 0}.card p,.muted{color:#aac0cc}.card small{color:#7dd9ce}.held{border-left:4px solid #e5ae63}.eligible{border-left:4px solid #66d4b5}
.foot{font-size:.84rem;color:#9cb1be;border-top:1px solid #324657;padding-top:20px;margin-top:28px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem;max-height:340px;overflow:auto;padding:16px;background:#07121a;border:1px solid #324657;border-radius:12px}
.sr{position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body><main>
<div class="hero"><div class="eyebrow">CoEvoAll+ / R0 / shadow experiment compiler</div><h1>CoDoodleNexus<span aria-hidden="true"> &#8634; </span>CoOrb</h1>
<p class="sub">One messy thought can generate many candidate comparisons. These are <strong>descriptions, not executed experiments</strong>. An unknown relation remains unknown. A symbolic G_d/aura lens is not a scientific observation.</p>
<div class="stats"><div class="stat"><b id="capacity">...</b><small>logical combinations</small></div><div class="stat"><b id="sample">...</b><small>sampled descriptions</small></div><div class="stat"><b id="selected">...</b><small>candidate cards</small></div><div class="stat"><b>0</b><small>live agents, network effects</small></div></div>
<div class="orbit" role="img" aria-label="CoIn leads to CoBetween, CoInvert, CoOut, and finally CoProof, with explicit limits"><span>&#8834; CoIn</span><span class="arrow">&#8594;</span><span>&#9675; CoBetween</span><span class="arrow">&#8596;</span><span>&#172; CoInv</span><span class="arrow">&#8594;</span><span>&#8658; CoOut</span><span class="arrow">&#8594;</span><span>&#10003; CoProof</span></div>
<p class="sub"><strong>Labels:</strong> &#9675; unresolved relation; &#172; inversion or counterexample; &#8658; proposed output; &#10003; evidence only after actual verification. No outcome here is a receiver ACK.</p></div>
<section aria-labelledby="candidate-head"><h2 id="candidate-head">Finite candidates from a vast space</h2><p class="muted">Choose a status or inspect each card. No tracking, clipboard access, keystroke capture, or outgoing requests.</p>
<div class="bar" role="group" aria-label="Filter candidates"><button type="button" id="all" aria-pressed="true">All proposals</button><button type="button" id="shadow" aria-pressed="false">Public/synthetic shadow</button><button type="button" id="held" aria-pressed="false">Requires review</button></div>
<div class="grid" id="cards" aria-live="polite"></div></section>
<section aria-labelledby="triage-head"><h2 id="triage-head">CoZombie: observe without guessing</h2><p class="muted">These five status entries are fictional fixtures. A stale heartbeat is not a dead process, and a failed session is not permission to restart it.</p><div class="grid" id="triage"></div></section>
<section aria-labelledby="benchmark-head"><h2 id="benchmark-head">Challenge the selector</h2><div id="benchmark"></div></section>
<section><h2>What must still happen on real X2?</h2><p class="muted">Read-only live state inspection, a deliberate physical thumb-button test, first-use human acceptance, independent process/receiver proof, and cold recovery on a second machine. This file tests none of those.</p></section>
<div class="foot">FOSS candidate. One bounded wave = one checkable artifact. Source is synthetic and public-safe. No original Synthkind declaration, no observed exotic physical mechanism, no infinite compute. <strong>Pointer is not ACK.</strong></div>
</main><script id="nexusData" type="application/json">NEXUS_DATA</script><script id="zombieData" type="application/json">ZOMBIE_DATA</script><script id="benchData" type="application/json">BENCH_DATA</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('nexusData').textContent);
const zombie=JSON.parse(document.getElementById('zombieData').textContent);
const benchmark=JSON.parse(document.getElementById('benchData').textContent);
const cardRoot=document.getElementById('cards');
const fmt=n=>new Intl.NumberFormat('en-US').format(n);
document.getElementById('capacity').textContent=fmt(data.logical_capacity);
document.getElementById('sample').textContent=data.sample_size;
document.getElementById('selected').textContent=data.selected_size;
function tag(name,child,value){const e=document.createElement(name);if(value!==undefined)e.textContent=value;if(child)child.appendChild(e);return e;}
function render(filter){cardRoot.replaceChildren();const items=data.candidates.filter(c=>filter==='all'||(filter==='shadow'?c.state==='SHADOW_ONLY_PUBLIC_OR_SYNTHETIC':c.state!=='SHADOW_ONLY_PUBLIC_OR_SYNTHETIC'));
 for(const c of items){const div=tag('article',cardRoot);div.className='card '+(c.state==='SHADOW_ONLY_PUBLIC_OR_SYNTHETIC'?'eligible':'held');
 tag('small',div,c.state);tag('h3',div,c.dimensions.relation+' / '+c.dimensions.surface+' / '+c.dimensions.benchmark);
 tag('p',div,'Proposed check: '+c.proposed_test);
 const details=tag('details',div);tag('summary',details,'Inspect full candidate and gates');tag('pre',details,JSON.stringify(c,null,2)); }
 if(!items.length)tag('p',cardRoot,'No candidates in this filter.'); }
const filters=['all','shadow','held'];for(const f of filters){document.getElementById(f).addEventListener('click',()=>{for(const x of filters)document.getElementById(x).setAttribute('aria-pressed',String(x===f));render(f);});}
render('all');
const triageRoot=document.getElementById('triage');for(const record of zombie.assessments){const div=tag('article',triageRoot);div.className='card';tag('small',div,record.assessment);tag('h3',div,record.session_id);tag('p',div,record.next_safe_action);}
const benchRoot=document.getElementById('benchmark');tag('p',benchRoot,'20 deterministic synthetic seeds. Favorable assumptions: '+fmt(benchmark.outcome_normal.wins)+' selector wins; inverted payoffs: '+fmt(benchmark.outcome_adversarial.losses)+' losses. Scores are designed fixtures, not observed productivity.');
</script></body></html>'''
    page=page.replace('CO_TITLE',html.escape(title,quote=True)).replace('NEXUS_DATA',safe_json(d)).replace('ZOMBIE_DATA',safe_json(z)).replace('BENCH_DATA',safe_json({k:v for k,v in b.items() if k!='cases'}))
    (ROOT/'CoDoodleNexus_Viewer.html').write_text(page,encoding='utf-8')
    return len(page)
if __name__=='__main__':print('viewer_bytes:',build())
