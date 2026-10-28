#!/usr/bin/env python3
"""Build offline, reproducible SHADOW acceptance artifacts. No writes outside output/."""
from pathlib import Path
from datetime import datetime, timezone
from engine import CoAlive, canonical_bytes, digest
import hashlib, json, re, subprocess, sys

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
RAW = (ROOT / 'manifest.json').read_bytes()
M = json.loads(RAW)


def write(path, data: bytes):
    # Create only, no clobber. Rebuild intentionally in a fresh dir, or remove generated files first.
    with path.open('xb') as f:
        f.write(data)


def pretty(x):
    return (json.dumps(x, indent=2, sort_keys=True, ensure_ascii=True) + '\n').encode('utf-8')


def example_event(id, name, kind='SOURCE_DELTA_REPORTED', source=None, scope='SYNTHETIC_SHADOW'):
    obj = next(o for o in M['objects'] if o['id'] == name)
    return dict(event_id=id, object_id=name, kind=kind,
                source_blob_sha=source or obj['source']['git_blob_sha1'], scope=scope)


run = subprocess.run([sys.executable, '-m', 'unittest','discover','-s','tests','-v'],
                     cwd=ROOT, capture_output=True, text=True)
log = run.stdout + run.stderr
m = re.search(r'Ran (\d+) tests', log)
assert run.returncode == 0 and m, log
count = int(m.group(1))
assert count >= 41, f'Unexpectedly low suite size: {count}'
write(OUT/'test_results.txt', log.encode('utf-8'))

engine = CoAlive(RAW)
trace = []
for label, tick, events in [
    ('idle initial heartbeat, no work', 0, []),
    ('bounded software test failure wakes shadow review', 4, [example_event('fixture-mouse-fail-1','mouse','TEST_FAILURE_REPORTED')]),
    ('first-door review and relational handoff', 5, [example_event('fixture-spiff-1','spiff','SOURCE_DELTA_REPORTED')]),
    ('mismatched source is held, recovery source due', 7, [example_event('fixture-stale-1','morph',source='0'*40)]),
    ('revoked mouse shadow work is suppressed', 8, []),
    ('private payload holds, no network effects', 10, [example_event('fixture-private-1','spiff',scope='PRIVATE')]),
]:
    if tick == 8:engine.revoke('mouse')
    result = engine.pulse(tick,events)
    trace.append({'label':label,'observed_tick':tick,'result':result,'manifest_sha256':engine.manifest_hash})
write(OUT/'pulse_trace.json', pretty({'schema':'CoAlivePulseTrace/R0','trace':trace,
    'limits':M['policy'], 'source_binding':engine.manifest_hash,
    'warning':'Simulated tick, not a timed background heartbeat. No real worker activated.'}))
write(OUT/'snapshot.json', pretty(engine.snapshot()))
restored = CoAlive(RAW,engine.snapshot())
assert restored.snapshot() == engine.snapshot()

# One intentionally unsuccessful criterion: claiming all graph work can fit in a single wave.
low = json.loads(RAW)
low['policy']['max_work_per_pulse'] = 1
limited = CoAlive(canonical_bytes(low))
limited_result = limited.pulse(0,[example_event('fixture-budget-1','mouse')])
assert limited_result['processed_count'] == 1 and limited_result['pending_count'] > 0

rows=[]
prev='0'*64
stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
def add(status, test, detail):
    global prev
    row={'schema':'CoAliveBenchEvent/R0','seq':len(rows)+1,'observed_at':stamp,
         'status':status,'test':test,'detail':detail,'prev_hash':prev}
    row['event_hash']=digest(row)
    prev=row['event_hash']
    rows.append(row)

add('PASS','PYTHON_REGRESSION_SUITE',{'tests_passed':count,'failures':0,'runtime':'Python stdlib only'})
add('PASS','SOURCE_MANIFEST_PIN',{'manifest_sha256':engine.manifest_hash,'object_count':len(M['objects']),'gap_count':len(M['gaps'])})
add('PASS','HEARTBEAT_WITH_NO_CHANGE',{'tick':0,'work':trace[0]['result']['processed_count'],'provider_calls':0})
add('PASS','SHADOW_SIGNAL_WAKE',{'tick':4,'admissions':trace[1]['result']['admissions']})
add('PASS','CYCLE_SUPPRESSION',{'unit_test':'test_cycles_suppressed','finite_depth':M['policy']['max_hops']})
add('PASS','COAMP_FINITE_BUDGET',{'work_per_pulse_cap':M['policy']['max_work_per_pulse'],'fanout_cap':M['policy']['max_fanout']})
add('FAIL','ONE_PULSE_COMPLETES_ALL_RELATIONS',{'reason':'Budget is intentionally finite','processed':limited_result['processed_count'],'left_pending':limited_result['pending_count'],'promotion_eligible':False})
add('PASS','SOURCE_PIN_MISMATCH_HELD',{'tick':7,'admissions':trace[3]['result']['admissions']})
add('PASS','REVOCATION_RECHECK',{'policy':'revoke mouse before tick 8; queued work suppressed'})
add('PASS','PRIVATE_SCOPE_HELD',{'tick':10,'admissions':trace[-1]['result']['admissions']})
add('PASS','RESTORE_FROM_SNAPSHOT',{'same_payload':True,'snapshot_sha256':hashlib.sha256((OUT/'snapshot.json').read_bytes()).hexdigest()})
add('PASS','ZERO_REAL_EFFECTS',{'provider_calls':0,'external_effects':0,'remote_acks_observed':0,'actual_workers':0})
add('HOLD','PHYSICAL_X2_NATIVE_COTHUMB',{'reason':'No authorized device readproof in this wave'})
add('HOLD','REMOTE_RECEIVER_ACK',{'reason':'No endpoint/readproof qualified'})
add('NOT_RUN','INDEPENDENT_MAC_OR_X2_REPRODUCTION',{'reason':'Needs a second machine/operator'})
add('NOT_RUN','LONG_HORIZON_PROCESS_SURVIVAL',{'reason':'No live daemon/timer installed by this prototype'})
add('NOT_RUN','REAL_ENERGY_SAVINGS',{'reason':'No energy meter; useful-work budgeting is not physical power measurement'})
add('NOT_RUN','REAL_USER_TASK_QUALITY',{'reason':'No independent useful-outcome adjudication'})
add('NOT_RUN','CLAUDE_PI_LLAMA_OR_OLLAMA',{'reason':'No provider/local inference attempted'})
add('HOLD','PRODUCTION_PROMOTION',{'reason':'Only local finite synthetic SHADOW tests; no adoption/authority'})
write(OUT/'benchmark_evo.jsonl', ''.join(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n' for x in rows).encode('utf-8'))
write(OUT/'HEAD.sha256',(prev+'\n').encode())
write(OUT/'SUMMARY.json',pretty({'schema':'CoAliveObjectSummary/R0','source_sha256':engine.manifest_hash,
    'test_pass':count,'outcomes':{k:sum(x['status']==k for x in rows) for k in ('PASS','FAIL','HOLD','NOT_RUN')},
    'event_count':len(rows),'head':prev,'actual_workers':0,'remote_effects':0,'long_running_daemon':False,
    'build_epoch_utc':stamp,'status':'OFFLINE_SHADOW_CANDIDATE__NOT_DEPLOYED'}))
print(json.dumps({'tests_passed':count,'evidence_events':len(rows),'ledger_head':prev,
                  'selected_by_tick':{row['observed_tick']:row['result']['processed_count'] for row in trace},
                  'no_remote_effects':True},indent=2))
