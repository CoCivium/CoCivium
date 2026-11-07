#!/usr/bin/env python3
"""Executable, synthetic two-receiver acceptance proof for CoCivium issue #317."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import coall_braid as braid

HERE = Path(__file__).resolve().parent


def record_event(events, kind, status, detail):
    prior = events[-1]['hash'] if events else '0'*64
    entry = {'schema':'CoGoldenBenchmark/R0', 'seq':len(events)+1, 'at':braid.now(),
             'kind':kind, 'status':status, 'detail':detail, 'prev_hash':prior}
    entry['hash'] = braid.digest(braid.canonical(entry))
    events.append(entry)


def verify_benchmark(path, expected_head):
    prev='0'*64
    entries=[]
    for idx, line in enumerate(Path(path).read_bytes().splitlines(),1):
        e=json.loads(line)
        if e.get('seq') != idx or e.get('schema')!='CoGoldenBenchmark/R0' or e.get('prev_hash')!=prev:
            raise ValueError('BAD_BENCH_CHAIN')
        if e.get('hash') != braid.digest(braid.canonical({k:v for k,v in e.items() if k!='hash'})):
            raise ValueError('BAD_BENCH_HASH')
        prev=e['hash']; entries.append(e)
    if prev!=expected_head:
        raise ValueError('BAD_BENCH_HEAD')
    return entries


def run(out):
    out=out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('NONEMPTY_OUTPUT_REFUSES_CLOBBER')
    out.mkdir(parents=True,exist_ok=True)
    events=[]
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE/'tests'),'-v'],
                        capture_output=True,text=True,check=False,timeout=160)
    (out/'test_report.txt').write_text(test.stdout+'\n'+test.stderr,encoding='utf-8')
    if test.returncode:
        record_event(events,'TEST_SUITE','FAIL',{'returncode':test.returncode})
        raise ValueError('TEST_SUITE_FAILED')
    tests_count=25
    if 'Ran 25 tests' not in test.stderr:
        raise ValueError('UNEXPECTED_TEST_COUNT')
    record_event(events,'OFFLINE_REGRESSION','PASS',{'tests':tests_count,'runner':'LOCAL_PYTHON_STDLIB'})
    root=out/'demo_work'
    init=braid.init(root,HERE/'fixture'/'task_packet.json')
    record_event(events,'CANONICAL_PACKET','PASS',{'task_sha256':init['task_sha256'], 'authorization':'LOCAL_ONLY'})
    first=braid.dispatch(root,fail_once_beta=True)
    mid=braid.reconcile(root)
    if first != {'alpha':'VERIFIED_LOCAL_RECEIVER','beta':'FAILED_PENDING_RETRY'} or mid['destinations']['beta']!='FAILED_QUEUED':
        raise ValueError('FAULT_NOT_PRESERVED')
    record_event(events,'INJECTED_BETA_FAILURE','FAIL',{'receiver':'beta','effect':'FIRST_ATTEMPT_REFUSED','state':'FAILED_QUEUED','not_a_real_outage':True})
    first_ack=(root/'receivers/alpha/ack.json').read_bytes()
    second=braid.dispatch(root,fail_once_beta=True)
    after=braid.reconcile(root)
    if not after['all_local_acked'] or second['alpha']!='SKIP_COMPLETED' or first_ack!=(root/'receivers/alpha/ack.json').read_bytes():
        raise ValueError('RECOVERY_OR_IDEMPOTENCE_FAILED')
    record_event(events,'RECOVERY_WITHOUT_DUPLICATE','PASS',{'alpha':'SKIP_COMPLETED','beta':'ACK_VERIFIED_LOCAL','alpha_same_receipt':True})
    third=braid.dispatch(root,fail_once_beta=True)
    if third != {'alpha':'SKIP_COMPLETED','beta':'SKIP_COMPLETED'}:
        raise ValueError('THIRD_DISPATCH_NOT_IDEMPOTENT')
    record_event(events,'IDEMPOTENT_SECOND_REPLAY','PASS',{'actual':third})
    final=braid.reconcile(root)
    fresh=subprocess.run([sys.executable,str(HERE/'coall_braid.py'),'reconcile','--root',str(root),
                          '--expect-task-sha',init['task_sha256'],'--expect-head',final['journal_head']],
                          capture_output=True,text=True,check=False,timeout=15)
    if fresh.returncode or json.loads(fresh.stdout)!=final:
        raise ValueError('FRESH_PROCESS_READBACK_FAILED: '+fresh.stderr)
    record_event(events,'FRESH_PROCESS_RECONCILIATION','PASS',{'same_status':True,'journal_head':final['journal_head']})
    record_event(events,'RECEIVER_EVIDENCE','PASS',{'distinct_receiver_pids':
                  json.loads((root/'receivers/alpha/ack.json').read_text())['receiver_pid']!=
                  json.loads((root/'receivers/beta/ack.json').read_text())['receiver_pid'],
                  'two_distinct_local_receipt_files':True})
    record_event(events,'ACTUAL_REMOTE_OR_INDEPENDENT_DOMAIN_PICKUP','HOLD',{'reason':'Both synthetic receivers share one filesystem and host'})
    record_event(events,'EXTERNAL_COMMUNICATION_AND_COORB_RUNTIME','NOT_RUN',{'reason':'No real destinations, running CoOrb, or provider accounts used'})
    record_event(events,'INDEPENDENT_HUMAN_ACCEPTANCE','NOT_RUN',{'reason':'No external consenting test receiver was involved'})
    record_event(events,'PRODUCTION_CONCURRENCY_OR_CRASH_SAFETY','HOLD',{'reason':'Local lock is fail-closed, not a full distributed transaction/fencing system'})
    ledger=out/'benchmark_evo.jsonl'
    ledger.write_bytes(b''.join(braid.canonical(e) for e in events))
    head=events[-1]['hash']
    (out/'HEAD.sha256').write_text(head+'\n',encoding='utf-8')
    verify_benchmark(ledger,head)
    (out/'DEMO_HEAD.sha256').write_text(final['journal_head']+'\n',encoding='utf-8')
    report={'schema':'CoGoldenBraidAcceptance/R0','tracker':'https://github.com/CoCivium/CoCivium/issues/317',
            'task_sha256':init['task_sha256'],'intermediate':mid,'recovered':final,
            'fresh_process_equal':True,'first_dispatch':first,'retry':second,'third_dispatch':third,
            'regression_tests':tests_count,'journal_head':final['journal_head'],
            'benchmark_head':head,'benchmark_counts':{s:sum(e['status']==s for e in events) for s in ('PASS','FAIL','HOLD','NOT_RUN')},
            'publication_or_external_pickup':'NOT_CLAIMED'}
    (out/'acceptance_report.json').write_bytes(braid.canonical(report))
    print(json.dumps(report,indent=2,sort_keys=True))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try: run(args.out)
    except (ValueError, OSError, subprocess.TimeoutExpired) as e:
        print(json.dumps({'status':'FAIL_CLOSED','error':str(e)}),file=sys.stderr)
        sys.exit(3)
