#!/usr/bin/env python3
"""Create a deterministic, explicitly scoped observation ledger for the offline pilot."""
import json
import subprocess
import sys
from pathlib import Path
from braid import ROOT, canonical, digest, load, propose, validate

seed=load();source=validate(seed)
fixture=json.loads((ROOT/'fixture.json').read_text(encoding='utf-8'))
rows=[]
for item in fixture['examples']:
    out=propose(item['intent'],seed)
    predicted=out['candidates'][0]['id'] if out['candidates'] else None
    rows.append({'intent':item['intent'],'expected':item['expected'],'selected':predicted,'status':'PASS' if predicted==item['expected'] else 'FAIL','selector_status':out['status']})
fixture_report={'schema':'CoGoldenBraidFixtureResult/0.1','scope':'HAND_AUTHORED_SAME_AUTHOR_AS_MATCH_PHRASES','rows':rows,'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows),'total':len(rows)}
(ROOT/'fixture_report.json').write_text(json.dumps(fixture_report,indent=2)+'\n',encoding='utf-8')
unit=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_braid.py','-v'],cwd=ROOT,capture_output=True,text=True)
(ROOT/'test_report.txt').write_text(unit.stdout+unit.stderr,encoding='utf-8')
if unit.returncode!=0:
    raise SystemExit('UNITS_FAILED; see test_report.txt')
line=next((x for x in (unit.stdout+unit.stderr).splitlines() if x.startswith('Ran ') and ' tests ' in x),None)
n=int(line.split()[1]) if line else 0
if not n: raise SystemExit('MISSING_UNIT_COUNT')
browser=json.loads((ROOT/'browser_receipt.json').read_text(encoding='utf-8'))
if browser['passed']!=browser['total'] or browser['requests'] or browser['errors']: raise SystemExit('BROWSER_FAILED')

records=[]
def record(kind,status,detail):
    previous=records[-1]['event_hash'] if records else '0'*64
    body={'schema':'CoGoldenBraidEvidenceEvent/0.1','seq':len(records)+1,'kind':kind,'status':status,'detail':detail,'prev_hash':previous}
    body['event_hash']=digest(body)
    records.append(body)
record('SOURCE_IDENTITY','PASS',{'source_sha256':source['seed_sha256'],'candidate_count':source['candidate_count'],'typed_relations':source['relation_count'],'design_sources':source['source_count'],'note':'Public source IDs pinned, upstream documents verified through GitHub connector before this experiment.'})
record('SCHEMA_AND_NEGATIVE_TESTS','PASS',{'unit_tests_passed':n,'runner':'python unittest, local container, no external endpoints'})
record('LOCAL_BROWSER_CANARY','PASS',{'passed':browser['passed'],'total':browser['total'],'mode':browser['mode'],'external_requests':len(browser['requests']),'note':'Not a native X2 or independent user result.'})
record('BROWSER_TEST_HARNESS_INITIAL','FAIL',{'reason':'The test used inner_text() on content inside a closed HTML details element and misclassified hidden-but-present source text as absent. The test was corrected to text_content().','scope':'TEST_HARNESS_NOT_PRODUCT_DEFECT'})
for x in rows:
    record('HAND_AUTHORED_ROUTING_FIXTURE',x['status'],{'expected':x['expected'],'selected':x['selected'],'intent':x['intent'],'outcome':x['selector_status']})
record('HUMAN_USEFULNESS','HOLD',{'reason':'No independent consenting newcomer has attempted the task. 13/14 is hand-authored keyword fixture matching, not semantic understanding.'})
record('CANON_PROMOTION','HOLD',{'reason':'All 14 sayings are normative/heuristic candidates. No receiver effect or repeatable benefit has been measured.'})
record('CONTINUOUS_EXECUTION','NOT_RUN',{'reason':'No new scheduler, model calls, autonomous loop or external effects. Existing CoEvoAll Pulse and CoTidy review are upstream observer candidates only.'})
record('X2_COORBWARE','NOT_RUN',{'reason':'The portable browser lens does not install CoOrbWare, read native devices or control UX.'})
record('EXTERNAL_DISTRIBUTION','NOT_RUN',{'reason':'At this stage no GitHub publication, external outreach or recipient pickup was performed by the offline harness.'})
p=ROOT/'benchmark_evo.jsonl'
p.write_text(''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in records),encoding='utf-8')
(ROOT/'HEAD.sha256').write_text(records[-1]['event_hash']+'\n',encoding='utf-8')
counts={k:sum(x['status']==k for x in records) for k in ('PASS','FAIL','HOLD','NOT_RUN')}
summary={'schema':'CoGoldenBraidR0Summary/0.1','candidate_count':len(seed['principles']),'typed_relations':len(seed['typed_relations']), 'local_unit_tests_passed':n,'local_browser_tests_passed':browser['passed'],'fixture_passed':fixture_report['pass'],'fixture_failed':fixture_report['fail'],'fixture_total':fixture_report['total'],'benchmark_evo_records':len(records),'counts':counts,'head_sha256':records[-1]['event_hash'],'state':'LOCAL_OFFLINE_CANDIDATE_NOT_CANON_NOT_SCHEDULED'}
(ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
