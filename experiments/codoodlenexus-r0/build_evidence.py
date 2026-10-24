#!/usr/bin/env python3
"""Freeze evidence from this one local wave; do not infer independent uptake."""
import json
from collections import Counter
from pathlib import Path
from verify_evidence import digest, verify

ROOT=Path(__file__).resolve().parent
bench=json.loads((ROOT/'output/challenge.json').read_text())
shadow=json.loads((ROOT/'output/shadow_candidates.json').read_text())
zombie=json.loads((ROOT/'output/cozombie_triage.json').read_text())
browser=json.loads((ROOT/'output/browser_canary.json').read_text())
assert bench['outcome_normal']['wins']==20 and bench['outcome_adversarial']['losses']==20
assert shadow['sample_size']==512 and shadow['actual_experiments_run']==0
assert len(zombie['assessments'])==5
assert browser['external_http_requests']==0

entries=[
 ('SOURCE','PASS','CoLens public living-media R0 retrieved from GitHub; original declaration text not verified'),
 ('SOURCE','PASS','CoMousePalette Windows CI #40110826879 completed success; physical thumb not tested'),
 ('TEST','PASS','45 offline deterministic and negative tests passed after corrections'),
 ('SPACE','PASS',str(shadow['logical_capacity'])+' logical descriptions indexable; none executed'),
 ('INDEX','PASS','1200 seeded rank/unrank cases plus boundary indices passed'),
 ('SHADOW','PASS','512 sample descriptions generated; no model calls'),
 ('SELECT','PASS','12 shadow proposal cards; no execution/effect permissions'),
 ('PRIVACY','PASS','raw prompt never placed in candidate output; only keyword tags and SHA'),
 ('PRIVACY','PASS','private / unknown / revoked option states held'),
 ('ZOMBIE','PASS','5 synthetic heartbeat/grant/quota fixtures classified'),
 ('ZOMBIE','PASS','no killed process, automatic wake, or lease overwrite in fixture audit'),
 ('PROVIDER','PASS','zero live model calls in this offline experiment'),
 ('HARNESS','FAIL','first static HTML test expected a details element created dynamically at runtime'),
 ('HARNESS','PASS','test corrected to inspect dynamic DOM construction; all 45 tests now pass'),
 ('BROWSER_HARNESS','FAIL','Playwright bundled headless-shell path absent; used system Chromium after correction'),
 ('BROWSER_FILE','HOLD','file:// navigation blocked by browser administrator; only injected page tested'),
 ('BROWSER','PASS','desktop injected-page Chromium canary: 12 specified checks'),
 ('BROWSER','PASS','mobile injected-page Chromium canary and narrow viewport test'),
 ('NETWORK','PASS','zero HTTP requests observed during injected Chromium tests'),
 ('BASELINE','PASS','on synthetic favorable scoring assumptions selector wins 20/20 seeds'),
 ('CHALLENGE','FAIL','on deliberately inverted synthetic payoffs selector loses 20/20 seeds'),
 ('PROMOTION','HOLD','no empirical evidence to promote selector beyond shadow research'),
 ('PERFORMANCE','PASS','isolated Python 256-sample median '+str(bench['timing']['median_compile_ms'])+' ms; descriptor compiler only'),
 ('MICROSECOND','FAIL','256-descriptor end-to-end compile did not meet hypothetical 1 ms target in this environment'),
 ('X2','HOLD','Desktop Commander X2 offline, last seen ~5h in observed query; no live device inspection'),
 ('HARDWARE','NOT_RUN','physical MX Master 4 button, Perixx events and contextual action acceptance not exercised'),
 ('MEDIA','NOT_RUN','original Synthkind declaration or finished video not independently verified'),
 ('ADAPTER','NOT_RUN','Claude, Pi and Ollama adapters or account conditions not invoked'),
 ('DISTRIBUTION','NOT_RUN','CoVIA, .nodes, .sites and Gmail receiver-origin readproof not observed'),
 ('ACCEPTANCE','NOT_RUN','independent user task, cross-device cold recovery and actual energy not measured'),
]
prior='0'*64
lines=[]
for seq,(kind,status,detail) in enumerate(entries,1):
    payload={'schema':'CoDoodleNexus.Receipt.R0','seq':seq,'kind':kind,'status':status,
             'detail':detail,'scope':'BOUNDED_LOCAL_PLUS_DECLARED_GITHUB_READBACK',
             'prev_hash':prior}
    event_hash=digest(payload);payload['event_hash']=event_hash;prior=event_hash
    lines.append(json.dumps(payload,sort_keys=True,separators=(',',':')))
assert verify(lines,prior)['events']==len(entries)
(ROOT/'output/benchmark_evo.jsonl').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(ROOT/'output/HEAD.sha256').write_text(prior+'\n',encoding='utf-8')
summary={'schema':'CoDoodleNexus.EvidenceSummary.R0','outcomes':dict(Counter(status for _,status,_ in entries)),
         'events':len(entries),'head':prior,'tests_passed':45,
         'browser_checks':browser['checks'],'logical_capacity':shadow['logical_capacity'],
         'real_agents':0,'real_experiments':0,'network_requests_browser_observed':0,
         'synthetic_normal':bench['outcome_normal'],'synthetic_adversarial':bench['outcome_adversarial'],
         'compile_256_median_ms':bench['timing']['median_compile_ms']}
(ROOT/'output/SUMMARY.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,sort_keys=True))
