#!/usr/bin/env python3
"""Construct an immutable synthetic demo and static privacy-redacted CoOrbWare view."""
import hashlib
import json
import re
from pathlib import Path
import coproc as m

root=Path(__file__).resolve().parent
paths=['demo_state.json','benchmark_evo.jsonl','CoOrbWare_offline.html','RECEIPT.json']
for name in paths:
    if (root/name).exists():raise SystemExit('NO_CLOBBER_EXISTING_'+name)
s=m.empty()
for i in range(12):
    kwargs={'priority':i%5,'submitted':0,'wake':0}
    if i==8:kwargs['privacy']='PRIVATE';kwargs['source']='PRIVATE_NOT_FOR_DISPLAY'
    if i==9:kwargs['privacy']='UNKNOWN'
    if i==10:kwargs['effect']='EXTERNAL'
    if i==11:kwargs['depth']=3
    if i==7:kwargs['wake']=100
    assert m.admit(s,m.task(i,**kwargs))=='ADMITTED'
first=m.elect(s,0,'LOW')
assert len(first)==2
m.finish(s,first[0],0)
expired=m.reap(s,3)
assert expired==[first[1]]
assert m.elect(s,3,'HIGH')==[]
second=m.elect(s,4,'MEDIUM')
assert len(second)==1
m.finish(s,second[0],4)
cp=m.checkpoint(s)
assert m.recover(cp)==s
live=m.live_probe(count=4,cap=2)
assert live['completed']==4 and live['remaining_children']==0 and live['peak_parent_observed_processes']<=2
q=m.public_orb(s)
assert q['observed_working_set']==9 and not any('PRIVATE' in json.dumps(x) for x in q['tiles'])
safe={'schema':'CoAll.CoForever.CandidateDemo.v0.1','scope':'ONE_BOUNDED_SYNTHETIC_WAVE',
      'spec_sha256':m.SPEC_SHA256,'logical_space':str(m.LOGICAL_SPACE),
      'max_active':m.MAX_ACTIVE,'touched':len(s['tasks']),
      'public_orb':q,
      'scales':['COHERE_NOW','LOCAL_DEVICE','LAN','FEDERATED_OPTION','LOGICAL_POSSIBILITIES'],
      'lifecycle':['DORMANT','WAKE_ELIGIBLE','LEASED_SIMULATED','COMPLETE_SIMULATED','SLEEP'],
      'dry_process_probe':{k:v for k,v in live.items() if k!='receipts'},
      'note':'Four real, short-lived local Python child processes completed; no model, network, remote service, or receiver pickup.',
      'receiver_ack':'UNPROVEN','external_effects':0}
(root/'demo_state.json').write_text(json.dumps(safe,sort_keys=True,indent=2)+'\n',encoding='utf-8')
rows=[]
def row(name,status,metric,scope='LOCAL_OR_CONTAINER_PROOF'):
    return {'schema':'CoForever.CoStretch.Benchmark.v1','test_id':name,'status':status,
            'evidence_class':scope,'metrics':metric,
            'source_spec_sha256':m.SPEC_SHA256,
            'limitations':['No live CoOrbWare desktop or external receiver','Not a production scheduler or model throughput result'],
            'promotion_eligible':False,'receiver_ack':'UNPROVEN','external_effects':0}
rows.extend([
    row('LOGICAL_SPACE_DIRECT_ADDRESS_16_POW_20','PASS',{'options':str(m.LOGICAL_SPACE),'sampled_roundtrips':1024,'enumerated':0}),
    row('SYNTHETIC_LEASE_CAP_2','PASS',{'cap':m.MAX_ACTIVE,'initial_leases':len(first),'after_pressure_high':0}),
    row('LEASE_EXPIRY_RECOVERY_NO_ACK','PASS',{'reaped':len(expired),'receiver_ack':'UNPROVEN'}),
    row('SOURCE_PINNED_CHECKPOINT_ROUNDTRIP','PASS',{'checkpoint_sha256':cp['sha256']}),
    row('PRIVACY_SUPPRESSED_ORBWARE','PASS',{'public_visible':q['observed_working_set'],'hidden_counts':None}),
    row('TWO_REAL_FINITE_LOCAL_PROCESSES','PASS',{k:v for k,v in live.items() if k!='receipts'}),
    row('CI_INDEPENDENT_REPLAY','NOT_RUN',{}),
    row('COSTRETCH_ENERGY_KWH','NOT_RUN',{}),
    row('INDEPENDENT_RECEIVER_READPROOF','NOT_RUN',{}),
    row('WALLPAPER_BYSTANDER_ACCEPTANCE','NOT_RUN',{}),
    row('COORBWARE_RUNTIME_INTEGRATION','NOT_RUN',{}),
    row('PAID_PROVIDER_EXIT','NOT_RUN',{}),
])
(root/'benchmark_evo.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
# Embed only PUBLIC projection. It is the browser's sole source; there is no network or local file fetch.
obj=json.dumps(safe,sort_keys=True,separators=(',',':')).replace('<','\\u003c')
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; connect-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>CoOrbWare+ | Quiet Forever Field R0</title><style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#07131b;color:#e5f3f2}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 60% 0%,#193d49 0,#07131b 48%);min-height:100vh}main{max-width:1040px;margin:auto;padding:28px 22px 48px}.top{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}.eyebrow{letter-spacing:.22em;color:#8dc7c6;font-size:11px;text-transform:uppercase}h1{font-size:clamp(27px,4vw,43px);line-height:1.1;margin:7px 0 10px;letter-spacing:-.04em}p{line-height:1.55}small,.muted{color:#a9c3c7}.tag{border:1px solid #516f73;border-radius:99px;padding:6px 11px;font-size:11px;color:#d6eaeb}.status{font-size:12px;display:flex;align-items:center;gap:6px}.status:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:#e7ba74}.hero{display:grid;grid-template-columns:minmax(270px,1.25fr) minmax(260px,.9fr);gap:16px;margin-top:25px}.panel{background:#0c2029ed;border:1px solid #305660;border-radius:17px;padding:20px;min-width:0}.panel h2{margin:0 0 14px;font-size:17px;font-weight:650}.numbers{display:grid;grid-template-columns:1fr 1fr;gap:12px}.number{padding:14px 12px;background:#132d35;border-radius:12px}.num{font-size:25px;font-weight:700;letter-spacing:-.04em}.label{font-size:12px;color:#acccd0}.note{font-size:12px;line-height:1.5;color:#bed4d8}.orbit{height:340px;border-radius:16px;position:relative;background:radial-gradient(circle,#234e59 0%,#123441 35%,#0c2029 68%);border:1px solid #30525c;overflow:hidden;margin-bottom:14px}.ring{border:1px dashed #446a73;position:absolute;left:50%;top:50%;border-radius:50%;transform:translate(-50%,-50%)}.ring.a{width:165px;height:165px}.ring.b{width:275px;height:275px}.core{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:grid;place-items:center;text-align:center;background:#17424b;border:2px solid #85d2ca;box-shadow:0 0 22px #71bdba30;border-radius:50%;width:98px;height:98px;font-weight:700;font-size:15px}.dot{position:absolute;width:63px;height:63px;border-radius:50%;background:#15353f;border:1px solid #78a3aa;display:grid;place-items:center;text-align:center;font-size:11px;line-height:1.2;color:#dae9ed}.dot.done{border-color:#7dbe9b}.dot.wait{border-color:#b5a177}.dot:nth-of-type(4){left:25%;top:12%}.dot:nth-of-type(5){left:65%;top:10%}.dot:nth-of-type(6){left:13%;top:41%}.dot:nth-of-type(7){left:72%;top:43%}.dot:nth-of-type(8){left:27%;top:70%}.dot:nth-of-type(9){left:60%;top:77%}.bnav{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px;margin-bottom:16px}button{font:inherit;color:#d9edf0;background:#10333c;border:1px solid #52747b;border-radius:10px;padding:9px 14px;cursor:pointer}button[aria-pressed=true]{background:#24535b;border-color:#a6ddd4;color:white}button:focus-visible{outline:3px solid #e4c18a;outline-offset:3px}.facts{display:grid;grid-template-columns:1fr 1fr;gap:16px}.facts ul{margin:0;padding-left:18px}.facts li{padding:5px 0;font-size:13px}.monos{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.foot{border-top:1px solid #305660;margin-top:26px;padding-top:15px;font-size:12px;color:#a9c3c7}.hidden{display:none!important}@media(max-width:730px){.hero,.facts{grid-template-columns:1fr}.orbit{height:300px}.panel{padding:15px}main{padding:18px 12px 30px}}@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body><main><header class="top"><div><div class="eyebrow">EVO ALL BETTERS + / CoOrbWare research</div><h1>Quiet Forever Field</h1><div class="muted">Many addressable possibilities. Few short-lived workers. One honest view.</div></div><div class="tag">SYNTHETIC CANARY · NOT A LIVE DESKTOP</div></header><section class="hero"><div class="panel"><h2>CoHereNow</h2><div class="orbit" role="img" aria-label="Illustrative orbital map, centre shows quiet source; surrounding nodes are synthetic process states, not real running workers."><div class="ring a"></div><div class="ring b"></div><div class="core">00_me<br>QUIET</div><div class="dot done">proof<br>done</div><div class="dot wait">sleep<br>wait</div><div class="dot">time<br>cursor</div><div class="dot done">lease<br>ended</div><div class="dot">source<br>bound</div><div class="dot wait">wake<br>held</div></div><p class="note">The rings are one possible CoMap/CoOrb projection of a synthetic work field. Only a fresh real-process lease receipt may justify a live status signal. This snapshot makes no such claim.</p></div><div class="panel"><h2>At a glance</h2><div class="numbers"><div class="number"><div class="num" id="option-count">…</div><div class="label">Logical addresses</div></div><div class="number"><div class="num" id="budget-count">…</div><div class="label">Maximum simultaneous workers</div></div><div class="number"><div class="num" id="child-count">…</div><div class="label">Transient child processes tested</div></div><div class="number"><div class="num">0</div><div class="label">Processes left running by this canary</div></div></div><p class="note">Published code and simulated leases are evidence of bounded experiments, not a running distributed fleet, verified model throughput, or a receiver ACK.</p><div class="status">LOCAL EVIDENCE · NO REMOTE ACK</div></div></section><nav class="bnav" aria-label="Projection selector"><button type="button" data-view="glance" aria-pressed="true">Glance</button><button type="button" data-view="work" aria-pressed="false">Working set</button><button type="button" data-view="time" aria-pressed="false">Time / wake</button><button type="button" data-view="proof" aria-pressed="false">Proof / limits</button></nav><section id="glance" class="facts"><div class="panel"><h2>What CoOrbWare should show</h2><p class="note">A durable work identity may be asleep. The visual surface should make unknown, forecast, leased, finished and held states distinct. Only changes that matter to this receiver should interrupt.</p></div><div class="panel"><h2>Not inferred</h2><ul><li>Not an infinite running loop</li><li>Not a million spawned sessions</li><li>Not a ChatGPT replacement</li><li>Not a wallpaper or CoBar installation</li><li>Not evidence of a remote receiver reading this result</li></ul></div></section><section id="work" class="panel hidden" aria-label="Synthetic working set"><h2>Public synthetic tasks only</h2><p class="note">Private and unknown tasks are suppressed entirely, including their hidden count.</p><ul id="task-list"></ul></section><section id="time" class="panel hidden" aria-label="Time and wake states"><h2>Wake / lease / sleep</h2><p>One synthetic election chose two leases, one expired without becoming an ACK, HIGH pressure admitted zero new work, and a later MEDIUM-pressure election admitted one.</p><p class="note">No persistent timer, daemon, or background automation was installed. In a real receiver, wake must be driven by a qualified scheduled event, subscription delta or user input, with resource ceilings and checkpoint reconstruction.</p></section><section id="proof" class="panel hidden" aria-label="Evidence and boundaries"><h2>Source and verification</h2><p class="note">One canonical source spec, one checkpoint identity and many projections. The source is not overwritten by its rendering.</p><p class="monos" id="spec"></p><p class="note">A bounded local run launched four short-lived Python processes with at most two observed concurrently. It did not use Ollama, Claude, Pi, ChatGPT, email, contacts, hardware remaps or external network requests.</p></section><footer class="foot">CoForever+ · CoVirtualSession+ · CoStretch+ · CoTurtleStop+ · CoOrbWare+ | FOSS / privacy-first · No crowns, no coercion, no corruption · Render ≠ ACK</footer></main><script type="application/json" id="source">__PAYLOAD__</script><script>
'use strict';const data=JSON.parse(document.getElementById('source').textContent);document.getElementById('option-count').textContent='≈1.21×10²⁴';document.getElementById('budget-count').textContent=String(data.max_active);document.getElementById('child-count').textContent=String(data.dry_process_probe.completed);document.getElementById('spec').textContent='SPEC SHA-256: '+data.spec_sha256;const list=document.getElementById('task-list');for(const t of data.public_orb.tiles){const li=document.createElement('li');li.textContent=t.id+' · '+t.state+' · SYNTHETIC · ACK UNPROVEN';list.appendChild(li)}const views=['glance','work','time','proof'];for(const b of document.querySelectorAll('[data-view]')){b.addEventListener('click',()=>{const v=b.getAttribute('data-view');if(!views.includes(v))return;for(const name of views){document.getElementById(name).classList.toggle('hidden',name!==v)}for(const x of document.querySelectorAll('[data-view]'))x.setAttribute('aria-pressed',String(x===b))})}
</script></body></html>'''.replace('__PAYLOAD__',obj)
assert 'PRIVATE_NOT_FOR_DISPLAY' not in html
assert 'connect-src \'none\'' in html
(root/'CoOrbWare_offline.html').write_text(html,encoding='utf-8')
sha=lambda name: hashlib.sha256((root/name).read_bytes()).hexdigest()
receipt={'schema':'CoAll.CoForeverR0.Receipt.v1','proof_class':'BOUNDED_LOCAL_PROCESS_CANARY',
         'spec_sha256':m.SPEC_SHA256,'demo_sha256':sha('demo_state.json'),
         'ledger_sha256':sha('benchmark_evo.jsonl'),'html_sha256':sha('CoOrbWare_offline.html'),
         'logical_space':str(m.LOGICAL_SPACE),'touch_count':len(s['tasks']),
         'actual_short_lived_children':live['launched'],'completed_children':live['completed'],
         'peak_children':live['peak_parent_observed_processes'],'remaining_children':live['remaining_children'],
         'duration_ms':live['duration_ms'],'currentness':'LOCAL_BOUNDED_AT_RUN',
         'receiver_pickup':'UNPROVEN','external_effects':0,'authority_change':0,
         'nonclaims':['NO_INFINITE_COMPUTE','NO_LIVE_COORBWARE_RUNTIME','NO_DURABLE_RECEIVER_LANDING',
                      'NO_INDEPENDENT_HUMAN_UX_ACCEPTANCE','NO_MODEL_INFERENCE','NO_SPONTANEOUS_SCHEDULER','NO_PROVIDER_EXIT']}
(root/'RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'demo_pass':True,'logical_space':str(m.LOGICAL_SPACE),'rows':len(rows),
                  'states':{'PASS':6,'NOT_RUN':6},'short_lived_processes':live['completed'],
                  'peak':live['peak_parent_observed_processes'],'elapsed_ms':live['duration_ms']},sort_keys=True))