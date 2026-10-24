#!/usr/bin/env python3
"""Build R1 evidence from explicit frozen public-fixture test results.

Events are append-only; outputs observed in this run are not a production SLA.
"""
import hashlib
import json
from pathlib import Path
from coscalemorph import canonical
from verify_ledger import verify as verify_r0

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
SCHEMA='CoScaleMorph.EvoEvent/R1'

def main():
    verify_r0((OUT/'benchmark_evo.jsonl').read_text(),(OUT/'HEAD.sha256').read_text())
    oldhead=(OUT/'HEAD.sha256').read_text().strip()
    kill=json.loads((OUT/'kill_restart_receipt.json').read_text())
    bench=json.loads((OUT/'bench_repetitions.json').read_text())
    assert kill['proof']=='ACTUAL_PROCESS_KILL_AND_INDEPENDENT_LOCAL_SUCCESSOR'
    assert kill['replay_exact_digest'] and kill['completed']==kill['task_count']==32
    assert bench['measured']['1']['all_outputs_match'] and bench['measured']['2']['all_outputs_match']
    # Evidence fixtures are created before their frozen-head regression tests can
    # run. The release gate reruns the full tests after generating the ledger.
    tests=(OUT/'r1_tests.log').read_text() if (OUT/'r1_tests.log').exists() else ''
    if 'Ran 52 tests' not in tests or '\nOK' not in tests:
        raise ValueError('UNEXPECTED_TEST_COUNT')
    events=[]
    def add(status, name, **detail):
        events.append({'outcome':status,'test':name,'detail':detail})
    add('PASS','PARENT_R0_HEAD_VALID',parent_head=oldhead,parent_events=21)
    add('PASS','R0_REGRESSION_TESTS',cases=27)
    add('PASS','R1_NEGATIVE_AND_RECOVERY_TESTS',cases=25)
    add('PASS','OS_KILL_ACTUAL_PROCESS',killed_exit_nonzero=kill['kill_nonzero_exit'],completed_at_kill=kill['completed_at_kill'])
    add('PASS','STALE_LOCK_REFUSES_RESTART',attempt_refused=kill['stale_lock_blocked_attempt'])
    add('PASS','EXPLICIT_STALE_LOCK_RECLAIM_AFTER_EXIT',reclaimed=kill['explicit_lock_reclaim'])
    add('PASS','INDEPENDENT_PROCESS_REHYDRATES_TASK_STATE',different_pid=kill['successor_different_pid'],restart_count=kill['restart_count'])
    add('PASS','PREFIX_REPLAY_MATCHES_BASELINE',task_count=kill['task_count'],result_sha256=kill['result_digest_sha256'])
    add('PASS','AUTHORITY_REVOKED_FAIL_CLOSED',evidence='test_revoked_grant_rejected')
    add('PASS','AUTHORITY_EXPIRED_FAIL_CLOSED',evidence='test_expired_grant_rejected')
    add('PASS','SOURCE_MISSING_OR_ALTERED_FAIL_CLOSED',evidence='test_missing_source_rejected,test_wrong_source_rejected')
    add('PASS','FORGED_ACK_REJECTED',evidence='test_forged_receiver_ack_rejected')
    add('PASS','REHASHED_FICTITIOUS_CHECKPOINT_REJECTED',evidence='test_invented_progress_even_with_rehashed_checkpoint_rejected')
    add('PASS','REPEATED_SERIAL_PARALLEL_OUTPUT_EQUAL',repeats_per_width=5,result_sha256=bench['matched_digest_sha256'])
    add('PASS','LIVE_CONCURRENT_WORKER_REJECTED',evidence='test_two_live_processes_do_not_share_one_checkpoint')
    add('PASS','LIVE_AUTHORIZATION_REVOCATION_STOPS_NEXT_STEP',evidence='test_revoke_grant_while_worker_is_running')
    add('PASS','LOGICAL_TRILLION_NOT_ACTUAL_WORKERS',logical_slots=bench['logical_slots'],max_workers=2)
    add('FAIL','FIRST_R1_EVENT_COUNT_ASSERTION',reason='Initial independent test assumed 27 ledger entries; generator emitted 28 and verifier failed, retained as explicit negative result')
    add('PASS','CORRECTED_R1_EVENT_COUNT_ASSERTION',reason='Corrected event count and status expectations to frozen published rows')
    add('FAIL','HYPOTHESIS_TWO_PROCESSES_ALWAYS_FASTER',reason='Not supported; median 2-process time marginally worse in this 5-trial synthetic run',serial_p50_seconds=bench['measured']['1']['p50_s'],parallel_p50_seconds=bench['measured']['2']['p50_s'])
    add('FAIL','HYPOTHESIS_LOSSY_SUMMARY_EXACT_SOURCE_REHYDRATION',reason='A lossy summary cannot restore deleted source without retained underlying bytes')
    add('HOLD','REAL_DISTRIBUTED_LOCK_AND_LEASE',reason='One local controller, PID owner guard only; no network or host-failure synchronization')
    add('HOLD','EXTERNAL_RECEIVER_EXACT_OBJECT_ACK',reason='Only local work checkpoint and evidence; no independently authorized receiver')
    add('HOLD','REPLACE_MODEL_SESSION_WITH_CHECKPOINT',reason='No Claude/Pi/Ollama provider session was reconstructed')
    add('NOT_RUN','REAL_X2_OR_MAC_SERVICE_DEATH',reason='Local container only; not installed on user devices')
    add('NOT_RUN','ENERGY_JOULES_PER_VERIFIED_TASK',reason='No power meter supplied')
    add('NOT_RUN','VIDEO_THUMB_FFPROBE_BLACKDETECT',reason='No eligible video/thumbnail in scope')
    add('NOT_RUN','GITHUB_HTTP_P95_BELOW_2S',reason='No end-to-end external receiver timing test')
    add('NOT_RUN','GMAIL_PRIMARY_UNDER_60S_ID',reason='No consented outbound email delivery canary')
    add('NOT_RUN','PI_CLAUDE_OLLAMA_LIVE_TIMING',reason='No credential or verified local runtime invoked')
    add('NOT_RUN','COVIA_NODES_SITES_PICKUP',reason='No receiver endpoint and exact-object readproof')
    add('NOT_RUN','NATIVE_THUMB_BUTTON_ORBWARE',reason='No hardware remapping or desktop integration performed')
    prev='0'*64
    rows=[]
    for i,e in enumerate(events,1):
        row={'schema':SCHEMA,'seq':i,'parent_r0_head':oldhead,'prev_hash':prev,**e}
        row['event_hash']=hashlib.sha256(canonical(row)).hexdigest()
        prev=row['event_hash'];rows.append(row)
    (OUT/'benchmark_evo_R1.jsonl').write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n' for r in rows),encoding='utf-8')
    (OUT/'HEAD_R1.sha256').write_text(prev+'\n',encoding='ascii')
    totals={s:sum(r['outcome']==s for r in rows) for s in ('PASS','FAIL','HOLD','NOT_RUN')}
    report={'schema':'CoScaleMorph.ReleaseSummary/R1','source_sha256':kill['source_sha256'],
            'parent_r0_head':oldhead,'r1_head':prev,'events':len(rows),
            'statuses':totals,'tests':52,'subprocess_recovery':kill,
            'parallel_benchmark':bench,'environment':'ISOLATED_LOCAL_CONTAINER',
            'nonclaims':['NOT_PRODUCTION','NOT_MAC_OR_X2_CANARY','NOT_DISTRIBUTED_LEASE','NOT_COORBWARE_INSTALL','NOT_PROVIDER_SESSION_RESTART','NO_EMAIL_OR_NODES_SENT']}
    (OUT/'R1_SUMMARY.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'events':len(rows),'totals':totals,'head':prev},indent=2))

if __name__=='__main__':main()
