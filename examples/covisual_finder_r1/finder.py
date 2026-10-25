#!/usr/bin/env python3
"""Deterministic no-network, metadata-only CoVisual source qualification demo."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'sources.json'
ALLOWED = {'commons.wikimedia.org', 'science.nasa.gov', 'www.nasa.gov', 'www.w3.org', 'opensource.creativecommons.org'}
ROLES = {'CoMap', 'CoOrb', 'CoTurtle', 'CoTheoryAll', 'CoA11y', 'CoOmni', 'CoProduct'}
POLICY_STATUSES = {'LICENSE_IDENTIFIED_CONDITIONS_REMAIN','MEDIA_GUIDELINES_KNOWN_ITEM_CLEARANCE_UNCONFIRMED','DOCUMENT_SOURCE_FOUND_IMAGE_LICENSE_UNVERIFIED','IMAGE_LICENSE_NOT_VERIFIED'}


def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path=SOURCE):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def check_url(url):
    p = urlparse(url)
    return p.scheme == 'https' and p.hostname in ALLOWED and not p.username and not p.password and not p.fragment


def validate(reg):
    if reg.get('schema') != 'CoCivium.CoVisual.ExternalInspiration.R1':
        raise ValueError('unknown schema')
    pol = reg['policy']; rows = reg['public_donors']
    if len(rows) > 4 or len(rows) > pol['max_candidates'] or pol.get('media_bytes_permitted') or pol.get('license_qualified_for_derivative'):
        raise ValueError('unsafe candidate/bulk/media policy')
    if pol.get('route_mode') != 'INTERNAL_PROPOSED_READONLY_ROLES_NO_SEND' or pol.get('max_routes_per_candidate',100) > 3:
        raise ValueError('unsafe routing policy')
    if any(reg['effects'].values()) or reg.get('privacy') != 'PUBLIC_SAFE_SOURCE_DESCRIPTIONS_ONLY':
        raise ValueError('unexpected effect / privacy')
    ids = set(); urls = set()
    needed = {'id','title','source_page','origin','rights_state','stated_license','rights_evidence_page','credit','motif','accessible_twin','inverse_challenge','next_test','epistemic_class','consumers','selected_reuse','noendorsement'}
    for x in rows:
        if not needed.issubset(x): raise ValueError('missing required source fields')
        if x['id'] in ids or x['source_page'] in urls: raise ValueError('duplicate id / URL')
        ids.add(x['id']); urls.add(x['source_page'])
        if not check_url(x['source_page']) or not check_url(x['rights_evidence_page']): raise ValueError('untrusted URL')
        if x['rights_state'] not in POLICY_STATUSES or x.get('selected_reuse') != 'MOTIF_ONLY_LINK_BACK_TO_SOURCE': raise ValueError('unqualified reuse')
        if len(x['consumers'])==0 or len(x['consumers'])>pol['max_routes_per_candidate'] or len(set(x['consumers']))!=len(x['consumers']): raise ValueError('route fanout exceeds budget')
        if any(c not in ROLES for c in x['consumers']): raise ValueError('unknown route')
        if not x['noendorsement'] or any(not str(x[k]).strip() for k in ['credit','motif','accessible_twin','inverse_challenge','next_test']): raise ValueError('no evidence / unclear rights')
        if set(x).intersection({'image_url','image_data','raw_image','prompt_to_clone','public_send','device_actuation','raw_private_data'}): raise ValueError('unexpected media or effect bytes')
    for x in reg.get('existing_donor_families',[]):
        if x.get('mode')!='LINK_ONLY' or not x.get('path','').startswith(('docs/Architecture/','examples/')) or '..' in x['path']: raise ValueError('bad internal donor')
    return rows


def project(reg):
    rows=validate(reg)
    return {'schema': 'CoCivium.CoVisual.ExternalInspirationProjection.R1', 'policy': 'METADATA_ONLY_PREVIEW_NOT_BROADCAST',
            'sources_digest': sha(canon(reg).encode()), 'sample_size':len(rows), 'routes_proposed': sum(len(x['consumers']) for x in rows),
            'network_calls':0, 'actual_receivers':0, 'actual_effects':0,
            'candidates': [{
                'id':x['id'],'source_page':x['source_page'],'title':x['title'],'motif':x['motif'],
                'inversion':x['inverse_challenge'],'accessibility':x['accessible_twin'],
                'rights':x['rights_state'],'credit':x['credit'],'proposed_roles':x['consumers'],
                'proposed_test':x['next_test'],'status':'INSPIRES_CANDIDATE__NO_DERIVATIVE_OR_SEND'
            } for x in rows], 'nonclaims':reg['nonclaims']}


def card(x, idx):
    def esc(k): return html.escape(str(x[k]),quote=True)
    roles=' '.join(f'<span class="role">{html.escape(role)}</span>' for role in x['consumers'])
    return (f'<article class="source" id="source-{idx}" data-index="{idx}">'
      f'<p class="eyebrow">0{idx+1} / {esc("source_type")}</p>'
      f'<h2>{esc("title")}</h2><p class="lead">{esc("motif")}</p>'
      f'<section class="detail" data-view="motif"><h3>Motif and original source</h3><p>{esc("accessible_twin")}</p></section>'
      f'<section class="detail" data-view="inverse" hidden><h3>CoTurtle inverse / NotElse</h3><p>{esc("inverse_challenge")}</p></section>'
      f'<section class="detail" data-view="test" hidden><h3>Smallest useful test</h3><p>{esc("next_test")}</p></section>'
      f'<section class="detail" data-view="rights" hidden><h3>Rights and provenance</h3><p>{esc("rights_state")}: {esc("stated_license")}</p><p>Attribution: {esc("credit")}</p></section>'
      f'<p class="roles">Qualified internal role proposals: {roles}</p>'
      f'<a href="{esc("source_page")}" target="_blank" rel="noopener noreferrer">Open original source page</a>'
      '</article>')


def render(reg, projection):
    rows=validate(reg)
    digest=sha(canon(reg).encode())
    body='\n'.join(card(x,i) for i,x in enumerate(rows))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; form-action 'none'; object-src 'none'; base-uri 'none'">
<title>CoVisual+ external inspiration | bounded sample</title><style>
:root {{ color-scheme:dark; font-family:system-ui, sans-serif; background:#101522; color:#f3f7ff }}
* {{ box-sizing:border-box }} body {{ margin:0; line-height:1.5 }} .wrap {{ max-width:1050px; margin:auto; padding:28px 20px 72px }}
a {{ color:#9de9ff }} button {{ font:inherit; color:inherit; background:#273149; border:1px solid #597189; border-radius:9px; padding:10px 14px; cursor:pointer }}
button[aria-pressed="true"] {{ background:#23545b; border-color:#9de9ff }} button:focus-visible, a:focus-visible {{ outline:3px solid #f9c86c; outline-offset:3px }}
.eyebrow {{ color:#a7bfd1; text-transform:uppercase; letter-spacing:.06em; font-size:.75rem }} .top {{ border-bottom:1px solid #3e4b5f; margin-bottom:24px; padding-bottom:16px }}
.banner {{ color:#c8d7e6; max-width:70ch }} .toolbar {{ display:flex; flex-wrap:wrap; gap:8px; margin:18px 0 24px }} .cards {{ display:grid; gap:16px; grid-template-columns:repeat(2,minmax(0,1fr)) }}
.source {{ border:1px solid #3e4b5f; border-radius:14px; background:#192134; padding:18px; min-width:0 }} .source h2 {{ margin:0; font-size:1.25rem }} .source h3 {{ margin:12px 0 6px; font-size:1rem }}
.lead {{ font-weight:600 }} .role {{ display:inline-block; border-radius:7px; padding:2px 7px; background:#364860; margin:3px }} .roles {{ font-size:.89rem }}
footer {{ margin-top:28px; padding-top:18px; border-top:1px solid #3e4b5f; color:#bfcdde; font-size:.86rem; overflow-wrap:anywhere }}
@media(max-width:720px) {{ .wrap{{padding:18px 12px 40px}} .cards{{grid-template-columns:1fr}} button{{flex:1 1 42%}} }}
@media(prefers-reduced-motion:reduce) {{ *{{scroll-behavior:auto!important;transition:none!important}} }}
</style></head><body><main class="wrap"><header class="top"><p class="eyebrow">CoOmni+ / CoOrbWare+ / CoTurtle+ · public-source inspiration sample R1</p>
<h1>Find → qualify → propose, without spraying media</h1><p class="banner">Four verified source-page references. All image bytes remain with their owners. These are design inspirations, not a complete web scan, public broadcast, reuse licence clearance or a live receiver. Each concept has an inverse challenge and an accessible text interpretation.</p>
<p><strong>Current mode:</strong> metadata-only, no login, network fetch, model workers, private images or automatic device effects. Proposed routes are <em>labels</em>, not actual deliveries.</p></header>
<nav class="toolbar" aria-label="Choose what to inspect"><button type="button" class="view" data-lens="motif" aria-pressed="true">◎ Motif</button><button type="button" class="view" data-lens="inverse" aria-pressed="false">¬ Inverse</button><button type="button" class="view" data-lens="test" aria-pressed="false">◇ Test</button><button type="button" class="view" data-lens="rights" aria-pressed="false">© Rights</button></nav>
<div class="cards" id="sources">{body}</div><footer>Machine source digest (SHA-256): <code>{digest}</code><p>Inspiration ≠ proof · shared pattern ≠ ownership · relevant source ≠ permission to redistribute · proposed fanout ≠ recipient ACK · logical infinity ≠ unlimited workers. Compatible with the CoLivingHighlight / CoVisualPriors contracts; not installed in CoOrbWare/X2.</p></footer>
</main><script>
(() => {{ const choices=[...document.querySelectorAll('button.view')]; const parts=[...document.querySelectorAll('.detail')];
 for (const b of choices) b.addEventListener('click', () => {{ const lens=b.dataset.lens; for(const c of choices) c.setAttribute('aria-pressed',String(c===b)); for(const d of parts) d.hidden=d.dataset.view!==lens; }});
}})();
</script></body></html>'''


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args=parser.parse_args()
    r=load(); p=project(r); page=render(r,p)
    outputs={'projection.json':json.dumps(p,ensure_ascii=False,indent=2,sort_keys=True)+'\n','index.html':page}
    if args.check:
        for n,t in outputs.items():
            if not (HERE/n).is_file() or (HERE/n).read_text(encoding='utf-8')!=t: raise SystemExit('FAIL: stale generated '+n)
        print('PASS deterministic projected data and HTML; sources:',p['sample_size'],'proposed role labels:',p['routes_proposed'],'actual effects: 0')
    else:
        for n,t in outputs.items(): (HERE/n).write_text(t,encoding='utf-8')
        print('built', ', '.join(outputs))

if __name__=='__main__': main()
