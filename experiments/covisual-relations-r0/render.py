#!/usr/bin/env python3
"""Build an accessible external-link-only CoOrb visual reference index."""
from pathlib import Path
import html
import json
from scout import ROOT, validate, rank

d=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
entries=validate(d);selected={e['id'] for e in rank(entries)}
colors={'UI_REFERENCE':'#b69cf5','MEDIA_CATALOG':'#78d2bf','COCIVIUM_PRIOR':'#eac183'}
cards=[]
for e in entries:
    label=html.escape(e['label']);url=html.escape(e['url'],quote=True)
    def esc(key):return html.escape(str(e[key]))
    badge='Selected for test' if e['id'] in selected else 'Research reserve'
    cards.append(f'''<article class="card" aria-label="{label}"><div class="ribbon"><span class="type" style="--accent:{colors[e['kind']]}">{esc('kind')}</span><span class="state">{badge}</span></div><h2>{label}</h2><p>{esc('use_case')}</p><div class="group"><strong>Discriminating test</strong><p>{esc('candidate_test')}</p></div><div class="group"><strong>Relation</strong><p>{esc('relation')}</p></div><div class="license"><strong>Rights gate:</strong> {esc('rights')}<br><small>Link-only reference. Exact asset rights not qualified.</small></div><a href="{url}" target="_blank" rel="noopener noreferrer">Inspect source page</a></article>''')
htmltext=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>CoVisual Relations R0 | Research index</title><style>
:root{{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#0a111c;color:#e8edf7}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 13% 0%,#223553aa,transparent 50%),#0a111c}}main{{max-width:1220px;margin:0 auto;padding:clamp(16px,3vw,42px)}}.eyebrow{{color:#91decf;font-weight:650;letter-spacing:.12em;font-size:12px}}h1{{font-size:clamp(28px,4vw,52px);margin:.25em 0}}h2{{font-size:18px;margin:14px 0 10px}}p{{line-height:1.5;color:#bfc9d9}}.intro{{max-width:790px}}.notice{{border:1px solid #567083;border-radius:14px;padding:14px 18px;color:#e5edf5;background:#16263b;margin:24px 0}}.metrics{{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}}.metric{{padding:12px 18px;border:1px solid #385064;border-radius:12px;background:#0e1b2c;min-width:140px}}.metric strong{{font-size:23px;display:block}}.metric span{{font-size:12px;color:#c6d2df}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:16px}}.card{{background:#111f31;border:1px solid #35506a;border-radius:16px;padding:20px;display:flex;flex-direction:column;gap:5px}}.ribbon{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px}}.type{{color:var(--accent);font-size:11px;font-weight:800;letter-spacing:.08em}}.state{{font-size:11px;color:#bacbe0}}.group{{border-top:1px solid #293d52;padding-top:8px}}.group strong,.license strong{{font-size:13px;color:#eaf0f8}}.group p{{margin:5px 0}}.license{{border-radius:9px;background:#27313b;color:#e0e4e9;padding:12px;font-size:12px;margin:8px 0;line-height:1.5}}.license small{{color:#e1cfbd}}a{{color:#7ee8d6;font-weight:650;text-underline-offset:3px;display:inline-block;margin-top:auto}}a:focus-visible{{outline:3px solid #f2bb77;outline-offset:4px}}footer{{margin:36px 0 4px;color:#c0cad6;font-size:13px}}.labels{{font-size:13px;color:#b2bccd}}@media(prefers-reduced-motion:reduce){{*,*:before,*:after{{animation:none!important;transition:none!important}}}}</style></head><body><main>
<div class="eyebrow">COORBWARE+ / COTURTLE∞+ / IMAGE SOURCE RELATIONS</div>
<h1>Visual source scout</h1>
<p class="intro">Every image may inspire a relation. Every relation must still earn qualification. This page indexes public <em>source pages</em>, not individual cleared images. No image bytes, tracker, remote JS, model, or publication effect is embedded.</p>
<div class="metrics"><div class="metric"><strong>{len(entries)}</strong><span>public source families</span></div><div class="metric"><strong>3</strong><span>bounded test candidates</span></div><div class="metric"><strong>0</strong><span>individual assets licensed for reuse</span></div><div class="metric"><strong>0</strong><span>receiver acknowledgments</span></div></div>
<div class="notice">Research source → rights/provenance → design hypothesis → challenge → independent outcome → optional permissioned reuse. The links below are external; nothing is fetched unless you open one.</div>
<section class="cards" aria-label="Research source references">{''.join(cards)}</section>
<footer><p><strong>Limits:</strong> This offline index does not demonstrate real-world discovery quality, compatibility, hosted availability, user comprehension or independent image licensing. All externally consequential actions remain separate opt-in decisions.</p><p class="labels">FOSS Forever · Working Together Respectfully · SOURCE_NE_LICENSE · LINK_NE_ACK · VIRTUAL_CANDIDATES_NE_LIVE_WORKERS</p></footer></main></body></html>'''
(ROOT/'CoVisual_Atlas.html').write_text(htmltext,encoding='utf-8')
print('Atlas bytes:',len(htmltext.encode('utf-8')))
