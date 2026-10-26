"""Build synthetic data, accessible visual, source-only highlights, and pinned receipt.

No network / credentials / runtime agents; deterministic outputs on a frozen source.
"""
import hashlib
import html
import json
from dataclasses import asdict
from pathlib import Path
from collections import Counter
from cycle import State, Offer, Policy, simulate, qualify_highlight

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
OUT.mkdir(exist_ok=True)


def canon(x):
    return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def write(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    good=Offer('Evidence-gated reusable work (SYNTHETIC)',quality=.95,risk=.04,attention=10)
    hype=Offer('Attention-heavy low evidence (SYNTHETIC)',quality=.10,risk=.15,attention=100000)
    adverse=Offer('High-risk but high-attention (SYNTHETIC)',quality=.95,risk=.8,attention=100000)
    scenarios={
      'regenerative_bounded': simulate(State(),good,external_inflow=4,turns=24),
      'resource_exhausted': simulate(State(useful=18,reserve=0,capacity=25),good,turns=24),
      'hype_evidence_gate': simulate(State(),hype,turns=24),
      'hype_naive_attention': simulate(State(),hype,turns=24,mode='attention'),
      'high_risk_held': simulate(State(),adverse,turns=24),
      'capacity_long_run': simulate(State(),good,external_inflow=4,turns=200),
    }
    write(OUT/'trajectories.json',{'schema':'CoRegenerative.SyntheticTrajectories.R0','scenarios':scenarios,
                                   'note':'Synthetic model only; no physical energy or user behavior measured.'})
    attention=scenarios['hype_naive_attention']
    spent=attention[-1]['after']['cumulative_spend']
    produced=sum(x['decision']['produced'] for x in attention)
    statuses=[]
    def evidence(status,claim,detail):
        statuses.append({'status':status,'claim':claim,'detail':detail})
    evidence('FAIL','ABSOLUTE_TOTAL_MUST_FALL_UNDER_HYPE','Initial test assumed a high-attention/low-quality option must reduce absolute useful stock. Synthetic output contradicted that absolute claim. Correct metric is benefit per resource spent.')
    evidence('PASS','BOUNDED_VERIFIED_GROWTH','Regenerative synthetic case rises initially and never exceeds finite capacity.')
    evidence('PASS','ZERO_INPUT_DECAY','A state with zero reserve and no new input loses useful stock.')
    evidence('PASS','LOW_EVIDENCE_HELD','Very high click attention does not pass quality gate.')
    evidence('PASS','ATTENTION_BASELINE_LOW_YIELD',{'spent':spent,'produced':round(produced,6),'benefit_per_spend':round(produced/spent,6)})
    evidence('PASS','HIGH_RISK_HELD','High risk remains held despite high attention and modeled high quality.')
    evidence('PASS','LONG_RUN_SATURATES','200 synthetic turns cannot exceed configured finite capacity 110.')
    evidence('PASS','SOURCE_ONLY_HIGHLIGHTS','Public source-qualified assets remain candidates, never automatically adopted.')
    evidence('HOLD','INDEPENDENT_RECEIVER_VALUE','No real consenting newcomer/reader/outcome has been measured.')
    evidence('HOLD','EXTERNAL_DOMAIN_AND_COPYRIGHT','Existing source routes require live host, attribution and reuse-rights review before broad promotion.')
    evidence('NOT_RUN','X2_AND_MAC_REPRODUCTION','No native X2 or Mac tests; no mouse or provider connections.')
    evidence('NOT_RUN','ACTUAL_RESOURCE_AND_ENERGY_METERS','No physical energy, CPU fleet, financial or human labor resources measured.')
    evidence('NOT_RUN','G_D_EMPIRICAL_MEASUREMENT','No G_d field, universal metric, divine intervention or novel force tested.')
    hash_inputs={p.name:sha(p) for p in (ROOT/'cycle.py',ROOT/'build.py',ROOT/'README.md')}
    # Source-only sample registry. These SHA-1 IDs were verified against GitHub on Oct 24,
    # but this build does not recheck currentness and does not make a site-live claim.
    catalog=[
      ('default','CoCivia first use','CoCivium/CoCivium','docs/Onramp/COCIVIA_FIRST_USE_R0.md','f18aec48eaa02fc15cdfb66a1b025460d57e02ff'),
      ('words','CoPreCursor+','CoCivium/CoCivium','examples/coprecursor/index.html','773e9de7aa7c6b03bf0bc75eddb7ca0a0c8dd101'),
      ('relationships','CoOrbWare First Look','CoCivium/CoAcademy','docs/coorb/index.html','634adc3ae92e5aba9671427ca56a78a1a72d05f9'),
      ('civic','CoCivicLens+','CoCivium/CoAcademy','docs/civiclens/index.html','98e152b7cd589fd69332cc935af994d68fc18616'),
      ('play','CoPlay+ (fiction)','CoCivium/CoAcademy','docs/coplay/votes-for-sale/index.html','ccbbfdb381144e5f2f6805921da5e33f9389413e'),
      ('build','CoAttractorPull+','CoCivium/CoCivium','examples/coattractorpull/index.html','b0ab26ebc2b2ec7cf6e4ab601798d34c1cb66349'),
    ]
    highlights=[]
    for goal,label,repo,path,blob in catalog:
        a={'goal':goal,'source_state':'GITHUB_BLOB_VERIFIED','privacy':'PUBLIC','requires_registration':False,'independent_first_use':None}
        highlights.append({'goal':goal,'label':label,'source_url':f'https://github.com/{repo}/blob/{"master" if repo.endswith("CoAcademy") else "main"}/{path}',
                           'pinned_blob_sha1_observed_oct24':blob,'review_currentness':'NOT_CHECKED_BY_OFFLINE_BUILD',
                           'first_use_qualified':'NOT_OBSERVED', 'promotion':qualify_highlight(a,goal)})
    write(OUT/'highlight_candidates.json',{'schema':'CoRegenerative.HighlightCandidates.R0','sources':highlights,
               'warning':'Prior source readback, not live first-use or current external site acceptance.'})
    prev='0'*64
    lines=[]
    for i,evt in enumerate(statuses,1):
        row={'schema':'CoRegenerative.Event.R0','seq':i,'prev_hash':prev,'event':evt,'synthetic':True}
        h=hashlib.sha256(canon(row)).hexdigest()
        lines.append(json.dumps({**row,'event_hash':h},ensure_ascii=True,sort_keys=True,separators=(',',':')))
        prev=h
    (OUT/'benchmark_evo.jsonl').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (OUT/'HEAD.sha256').write_text(prev+'\n',encoding='ascii')
    totals=dict(Counter(e['status'] for e in statuses))
    summary={'schema':'CoRegenerative.RunSummary.R0','model':'unitless_synthetic','runs':len(scenarios),
             'events':len(statuses),'status_counts':totals,'ledger_head_sha256':prev,'source_sha256':hash_inputs,
             'examples':{
               'initial_useful':State().useful,
               'regenerative_useful_after_8':scenarios['regenerative_bounded'][7]['after']['useful'],
               'regenerative_useful_after_24':scenarios['regenerative_bounded'][-1]['after']['useful'],
               'resource_exhausted_useful_after_24':scenarios['resource_exhausted'][-1]['after']['useful'],
               'hype_evidence_spend':scenarios['hype_evidence_gate'][-1]['after']['cumulative_spend'],
               'hype_naive_spend':spent,
               'hype_naive_benefit_per_resource':round(produced/spent,6),
               'max_allowed_capacity':Policy().capacity_limit
             },
             'nonclaims':['NO_LIVE_USERS','NO_ETERNAL_AMPLIFICATION','NO_G_D_PHYSICAL_MEASUREMENT','NO_REAL_RESOURCES_MEASURED','NO_PUBLIC_RECEIVER_ACK']}
    write(OUT/'summary.json',summary)
    # Plain static SVG, all labels and values remain synthetic; no JS or tracking.
    W,H=780,280
    def pts(series):
        vals=[State().useful]+[r['after']['useful'] for r in scenarios[series][:24]]
        return ' '.join(f'{40+j*29.0:.1f},{238-v*1.7:.1f}' for j,v in enumerate(vals))
    grid=''.join(f'<line x1="40" y1="{238-x*1.7:.1f}" x2="750" y2="{238-x*1.7:.1f}" stroke="#465464" stroke-dasharray="3 6" opacity=".5"/>' for x in (0,25,50,75,100))
    curves=f'<polyline fill="none" stroke="#45d6a0" stroke-width="3" points="{pts("regenerative_bounded")}"/><polyline fill="none" stroke="#efb95b" stroke-width="3" points="{pts("resource_exhausted")}"/><polyline fill="none" stroke="#9cb0ca" stroke-width="3" points="{pts("hype_evidence_gate")}"/>'
    links=''.join(f'<li><a rel="noreferrer" href="{html.escape(a["source_url"],quote=True)}">{html.escape(a["label"])}</a> <span>(source only; no independent first-use ACK)</span></li>' for a in highlights)
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CoRegenerative+ R0: finite gain and evidence gates</title><style>body{{font:16px/1.55 system-ui,sans-serif;max-width:890px;margin:auto;padding:32px;color:#ebeff4;background:#0d1820}}a{{color:#98d8fa}}h1{{line-height:1.1}}.sub{{color:#b4c7d2}}.box{{background:#172934;padding:18px;border-radius:14px;margin:22px 0}}svg{{width:100%;height:auto}}li{{margin:.45rem 0}}.legend span{{display:inline-block;margin:0 20px 8px 0}}.dot{{display:inline-block;width:14px;height:5px;vertical-align:middle;margin-right:8px}}code{{white-space:pre-wrap}}small{{color:#c7d0d8}}</style><main><h1>CoRegenerative+ R0</h1><p class="sub">How to reinforce verified benefit without amplifying every disturbance. <strong>Offline synthetic demonstration. Not a physical law or evidence of adoption.</strong></p><div class="box"><h2>24 modeled cycles</h2><svg viewBox="0 0 780 280" role="img" aria-label="Synthetic utility stock: permitted evidence feedback rises toward finite capacity; zero-input and held high-attention conditions decay. The values are modeled, not measured.">{grid}<line x1="40" y1="238" x2="750" y2="238" stroke="#b4c7d2"/><line x1="40" y1="10" x2="40" y2="238" stroke="#b4c7d2"/>{curves}<text x="45" y="20" fill="white" font-size="13">Synthetic useful units, 0–110</text><text x="620" y="265" fill="white" font-size="13">cycles 0–24</text></svg><p class="legend"><span><i class="dot" style="background:#45d6a0"></i>Evidence-gated, with fresh input</span><span><i class="dot" style="background:#efb95b"></i>No reserve/input</span><span><i class="dot" style="background:#9cb0ca"></i>Hype held</span></p><small>Regenerative scenario after 24: {summary['examples']['regenerative_useful_after_24']:.2f} synthetic useful units. Resource-exhausted scenario: {summary['examples']['resource_exhausted_useful_after_24']:.2f}. Both are bounded.</small></div><h2>Potential highlighted assets</h2><p>These six source entries were independently matched to GitHub blobs in prior source checks. The offline build does not revalidate their currentness or prove visitor adoption. No tracking or personalization.</p><ul>{links}</ul><h2>The high bar</h2><p>One consenting visitor receives concrete benefit, critiques the result, and can exit. A second builder reproduces it independently; the service survives a relevant failure. No “fireworks” or unbounded gain claims until then.</p><p><small>PASS/FAIL/HOLD are recorded in <code>output/benchmark_evo.jsonl</code>. Initial overclaim that low-quality engagement must reduce absolute usefulness is preserved as a FAIL. Engagement-based growth is not evidence of benefit.</small></p></main></html>'''
    (ROOT/'CoRegenerative_Viewer.html').write_text(page+'\n',encoding='utf-8')
    print(json.dumps(summary['examples'],indent=2));print('evidence:',totals,'head:',prev)

if __name__=='__main__':main()
