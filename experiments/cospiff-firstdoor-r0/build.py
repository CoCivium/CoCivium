#!/usr/bin/env python3
"""Build a source-only accessible first-door page, zero JS, no tracking."""
import html
from pathlib import Path
from cospiff import load_registry,audit_registry,ROOT

reg=load_registry()
assert not audit_registry(reg)

def card(route, main=False):
    h=html.escape
    noun='Open the public guide' if route['category']=='GUIDE' else 'Inspect the public source'
    label=h(route['label'])
    return f'''<article class="route{' main' if main else ''}" aria-labelledby="route-{h(route['id'])}">
  <div class="top"><h3 id="route-{h(route['id'])}">{label}</h3><span class="type">{'First step' if main else 'Optional'}</span></div>
  <p>{h(route['first_action'])}</p>
  <p class="audience">For: {h(route['audience'])}</p>
  <a class="cta" href="{h(route['source_url'])}" target="_blank" rel="noopener noreferrer">{noun} <span aria-hidden="true">&rarr;</span></a>
  <p class="limit">Source verified in GitHub; not a validated hosted app or independent user outcome.</p>
</article>'''

main=next(r for r in reg['routes'] if r['id']==reg['default_route'])
other=[r for r in reg['routes'] if r['id']!=main['id']]
page='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark light">
<title>CoSpiff+ | Choose a first step</title><style>
:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color-scheme:dark;--bg:#101921;--surface:#1a2935;--line:#3c5866;--text:#f2f8fc;--muted:#c1d0d8;--action:#a6e6d1}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);line-height:1.5}main{max-width:900px;padding:clamp(16px,4vw,40px);margin:auto}a{color:var(--action)}a:focus-visible,summary:focus-visible{outline:3px solid #a6e6d1;outline-offset:4px;border-radius:4px}
.kicker{font-size:.85rem;letter-spacing:.09em;color:var(--action);text-transform:uppercase;font-weight:700}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.15;margin:.4rem 0 1rem}h2{font-size:1.35rem;margin:0 0 1rem}h3{font-size:1.15rem;margin:0}
.lead{max-width:620px;color:var(--muted);font-size:1.1rem}.route{border:1px solid var(--line);border-radius:15px;background:var(--surface);padding:1.2rem;min-height:220px}.route.main{margin:1.5rem 0;box-shadow:0 4px 0 #2a7669}.top{display:flex;gap:.5rem;justify-content:space-between;align-items:center}.type{font-size:.75rem;border:1px solid var(--line);border-radius:30px;padding:.15rem .6rem;color:var(--muted)}.route p{margin:.5rem 0 1.2rem}.audience,.limit{color:var(--muted);font-size:.84rem}.cta{display:inline-block;padding:.7rem 1rem;border:1px solid var(--action);border-radius:8px;text-underline-offset:.2rem;font-weight:700}
details{border:1px solid var(--line);border-radius:12px;padding:1rem;margin:1.8rem 0}summary{cursor:pointer;font-weight:700;font-size:1.06rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:1rem;padding-top:1.2rem}footer{color:var(--muted);border-top:1px solid var(--line);margin-top:2rem;padding-top:1.5rem}small{font-size:.83rem}
@media(prefers-reduced-motion:reduce){*,*::after,*::before{animation:none!important;scroll-behavior:auto!important}}@media(prefers-color-scheme:light){:root{color-scheme:light;--bg:#f6fafb;--surface:white;--line:#94a9b3;--text:#122633;--muted:#385260;--action:#085d4d}}
</style></head><body><main>
<p class="kicker">CoSpiff+ / CoCivium / Public working experiment</p><h1>One thing. One useful next step.</h1>
<p class="lead">You do not need to learn the ecosystem, create an account, or choose an AI model first. Begin with one problem. Explore specialist paths only if they help.</p>
<h2>Your starting point</h2>
'''+card(main,True)+'''
<details><summary>Different goal? Explore five optional specialist paths</summary><div class="grid">
'''+''.join(card(route) for route in other)+'''</div></details>
<section aria-label="Trust and boundaries"><h2>What these links mean</h2>
<p>They lead to <strong>public source files</strong> on GitHub. Some contain downloadable offline browser examples. A linked source does not imply that a custom-domain website, installed app, agent, or separate account exists.</p>
<p>There is <strong>no JavaScript, tracking, profile inference, or automatic redirect</strong> on this page. Opening a GitHub link is a deliberate external navigation, subject to GitHub's own service policies. Your input does not leave this page because this page does not collect it.</p>
<p>For an issue or suggestion, use the <a href="https://github.com/CoCivium/CoCivium/issues" target="_blank" rel="noopener noreferrer">public issue tracker</a> and do not post secrets or someone else's personal data.</p></section>
<footer><small>Six public-source identities were checked against their route manifest on October 24, 2026. No independent newcomer acceptance, broader readership, Pages uptime, or domain routing is claimed. <a href="https://github.com/CoCivium/CoCivium/blob/main/ai/onramp/specialist-entrypoints-r0.json" target="_blank" rel="noopener noreferrer">Source registry</a>. FOSS Forever · Working Together Respectfully · Privacy by design.</small></footer>
</main></body></html>
'''
(ROOT/'CoSpiff_FirstDoor.html').write_text(page,encoding='utf-8')
print('built',len(page),'chars',6,'routes')
