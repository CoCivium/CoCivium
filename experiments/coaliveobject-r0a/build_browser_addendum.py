#!/usr/bin/env python3
"""Append an evidence successor to the immutable 20-event R0 baseline. Create-only."""
from pathlib import Path
import json, hashlib, subprocess, re, sys
from datetime import datetime,timezone
from engine import digest, reject_duplicate_keys
ROOT=Path(__file__).parent; OUT=ROOT/'output'
rows=[json.loads(line,object_pairs_hook=reject_duplicate_keys) for line in (OUT/'benchmark_evo.jsonl').read_text().splitlines() if line]
expected=(OUT/'HEAD.sha256').read_text().strip()
assert len(rows)==20 and rows[-1]['event_hash']==expected
browser=json.loads((OUT/'browser_check.json').read_text(),object_pairs_hook=reject_duplicate_keys)
assert browser['view_source_sha256']==hashlib.sha256((ROOT/'CoAliveObject_Viewer.html').read_bytes()).hexdigest()
assert browser['passed']==20 and browser['external_requests']==0 and browser['js_errors']==0
run=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],cwd=ROOT,text=True,capture_output=True)
assert run.returncode==0,run.stderr
match=re.search(r'Ran (\d+) tests',run.stderr)
assert match and int(match.group(1))==44
stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
def append(status,test,detail):
 prev=rows[-1]['event_hash']
 r={'schema':'CoAliveBenchEvent/R0','seq':len(rows)+1,'observed_at':stamp,'status':status,'test':test,
    'detail':detail,'prev_hash':prev}
 r['event_hash']=digest(r);rows.append(r)
append('PASS','DESKTOP_AND_MOBILE_BROWSER_CANARY',{'checks_passed':20,'external_requests':0,'js_errors':0,
'viewer_sha256':browser['view_source_sha256'],'mode':'INJECTED_HTML_CHROMIUM_NOT_FILE_OPEN'})
append('NOT_RUN','DIRECT_FILE_URI_IN_CHROMIUM',{'reason':'ERR_BLOCKED_BY_ADMINISTRATOR','real_file_opening':'UNVERIFIED'})
append('PASS','SUCCESSOR_REGRESSION_44',{'python_unit_tests_passed':44,'failure_count':0,'R0_base_head':expected})
stream=''.join(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n' for row in rows)
(OUT/'benchmark_evo_R0a.jsonl').open('x',encoding='utf-8').write(stream)
(OUT/'HEAD_R0a.sha256').open('x',encoding='utf-8').write(rows[-1]['event_hash']+'\n')
(OUT/'summary_R0a.json').open('x',encoding='utf-8').write(json.dumps({'schema':'CoAliveObjectSummary/R0a',
 'parent_head':expected,'head':rows[-1]['event_hash'],'events':len(rows),
 'pass_count':sum(x['status']=='PASS' for x in rows),
 'fail_count':sum(x['status']=='FAIL' for x in rows),
 'hold_count':sum(x['status']=='HOLD' for x in rows),
 'not_run_count':sum(x['status']=='NOT_RUN' for x in rows),
 'python_tests_current':44,'browser_checks':20,'actual_workers':0,'external_effects':0},indent=2,sort_keys=True)+'\n')
print('PASS R0a events',len(rows),'head',rows[-1]['event_hash'])
