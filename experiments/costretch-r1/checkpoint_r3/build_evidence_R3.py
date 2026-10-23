#!/usr/bin/env python3
"""Offline release reporter for CoStretch R3. Does not invoke any AI or network."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE / 'parent_R2'
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(SOURCE))
import turtle_checkpoint as t
from verify_evo_ledger import verify, digest, no_duplicate_keys


def run(*args):
    return subprocess.run(args, capture_output=True,text=True,cwd=HERE)


def check(outcome, expected):
    if outcome.returncode==0 and not expected:
        raise AssertionError('UNEXPECTED_SUCCESS:'+outcome.stdout)
    if outcome.returncode!=0 and expected:
        raise AssertionError('UNEXPECTED_FAILURE:'+outcome.stderr)


def append(rows, name, outcome, detail):
    new={'schema':'CoBenchmarkEvoEvent/1','seq':len(rows)+1,
         'prev_hash':rows[-1]['event_hash'],'kind':name,'outcome':outcome,'detail':detail}
    new['event_hash']=digest(new)
    rows.append(new)


def elapsed_ms(fn, trials=101):
    times=[]
    for _ in range(trials):
        start=time.perf_counter_ns(); fn(); times.append((time.perf_counter_ns()-start)/1_000_000)
    return round(statistics.median(times),5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', type=Path, default=HERE)
    args = parser.parse_args()
    outdir = args.out_dir
    if not outdir.is_dir():
        raise ValueError('OUTPUT_DIR_MUST_ALREADY_EXIST')
    if any((outdir/f).exists() for f in ('benchmark_evo_R3.jsonl','HEAD_R3.sha256','R3_REPORT.json')):
        raise FileExistsError('R3_EVIDENCE_ALREADY_EXISTS_NO_CLOBBER')
    base_rows=[json.loads(line, object_pairs_hook=no_duplicate_keys)
               for line in (SOURCE/'benchmark_evo.jsonl').read_text('utf-8').splitlines()]
    r2head=(SOURCE/'HEAD.sha256').read_text('ascii').strip()
    assert verify(SOURCE/'benchmark_evo.jsonl',r2head)==28
    old_sha=hashlib.sha256((SOURCE/'benchmark_evo.jsonl').read_bytes()).hexdigest()
    rows=copy.deepcopy(base_rows)
    spec, spec_hash=t.load_space(HERE/'space_manifest.json')
    cp=t.load_checkpoint(HERE/'checkpoint_R3_seed0.json')
    t.validate_checkpoint(spec,spec_hash,cp)
    nextcp=t.load_checkpoint(HERE/'checkpoint_R3_successor.json')
    t.validate_checkpoint(spec,spec_hash,nextcp)
    assert nextcp['parent_checkpoint_sha256']==cp['checkpoint_sha256']
    assert nextcp['next_index']==4

    # Demonstrate the prior arithmetic-index semantic-drift failure as a genuine baseline FAIL.
    old=copy.deepcopy(spec)
    old['dimensions'][0]['options'][:2]=old['dimensions'][0]['options'][1::-1]
    assert t.capacity(old)==t.capacity(spec)
    assert t.unrank(old,0)!=t.unrank(spec,0)
    append(rows,'R3_BARE_INDEX_SEMANTIC_STABILITY','FAIL',
           {'source':'R1 positional address','test':'swap two role labels without changing dimensions/cardinality',
            'capacity_unchanged':True,'index_0_original':t.unrank(spec,0)['role'],
            'index_0_altered':t.unrank(old,0)['role'],
            'interpretation':'Unversioned integer cannot preserve option meaning after reordering.'})

    suite=run(sys.executable,'-m','unittest','-v','test_turtle_checkpoint.py')
    check(suite,True)
    m=re.search(r'Ran (\d+) tests?',suite.stderr)
    test_count=int(m.group(1)) if m else 0
    assert test_count==25,(suite.stderr,test_count)
    append(rows,'R3_PYTHON_REGRESSION','PASS',{'tests':test_count,'environment':'offline Python runtime',
                 'covers':'namespace drift, tampering, policy boundaries, no-clobber, zero-work exhaustion, roundtrip'})

    py=run(sys.executable,'turtle_checkpoint.py','verify','--space','space_manifest.json',
           '--checkpoint','checkpoint_R3_successor.json')
    node=run('node','verify_checkpoint.mjs','space_manifest.json','checkpoint_R3_successor.json')
    check(py,True);check(node,True)
    append(rows,'R3_CROSS_RUNTIME_VALIDATION','PASS',
           {'python_result':json.loads(py.stdout)['result'],'node_result':json.loads(node.stdout)['status'],
            'spec_sha256':spec_hash,'checkpoint_sha256':nextcp['checkpoint_sha256'],
            'independence_limit':'Different runtimes with related verifier contracts, not independent human review.'})

    scenarios={}
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp)
        changedspace=d/'space_swapped.json'
        changedspace.write_text(json.dumps(old),encoding='utf-8')
        corruptcp=d/'cp_corrupt.json'; corrupt=copy.deepcopy(cp); corrupt['next_index']=103
        corruptcp.write_text(json.dumps(corrupt),encoding='utf-8')
        escalate=d/'cp_escalated.json'; altered=copy.deepcopy(cp);altered['effect_ceiling']='EXTERNAL_ACTION'
        altered['checkpoint_sha256']=t.digest(t.canonical({k:v for k,v in altered.items() if k!='checkpoint_sha256'}))
        escalate.write_text(json.dumps(altered),encoding='utf-8')
        double=d/'cp_duplicate.json';raw=(HERE/'checkpoint_R3_seed0.json').read_text('utf-8')
        double.write_text(raw.replace('"schema": "CoTurtleCheckpoint/3",','"schema": "CoTurtleCheckpoint/3", "schema": "CoTurtleCheckpoint/3",'),encoding='utf-8')
        for name,sp,checkpath,expect_reason_node in [
            ('same_size_definition_swap',changedspace,HERE/'checkpoint_R3_seed0.json','SPEC_NAMESPACE_CHANGED'),
            ('altered_cursor',HERE/'space_manifest.json',corruptcp,'TAMPERED_CHECKPOINT'),
            ('rehashed_policy_escalation',HERE/'space_manifest.json',escalate,'EFFECT_POLICY_CHANGED'),
            ('duplicate_checkpoint_key',HERE/'space_manifest.json',double,'DUPLICATE_OR_UNEXPECTED_KEY'),
        ]:
            node_run=run('node','verify_checkpoint.mjs',str(sp),str(checkpath))
            py_run=run(sys.executable,'turtle_checkpoint.py','verify','--space',str(sp),'--checkpoint',str(checkpath))
            check(node_run,False);check(py_run,False)
            assert expect_reason_node in node_run.stderr,(name,node_run.stderr)
            scenarios[name]={'python_rejected':True,'node_rejected':True,'node_reason':expect_reason_node,
                             'python_message':py_run.stderr.strip()[:100]}
    append(rows,'R3_CROSS_RUNTIME_NEGATIVE_CONTROLS','PASS',
           {'negative_cases':len(scenarios),'scenarios':scenarios})
    append(rows,'R3_VERSIONED_RESUME_GUARD','PASS',
           {'namespace_sha256':spec_hash,'capacity':t.capacity(spec),'next_index':nextcp['next_index'],
            'previous_checkpoint':cp['checkpoint_sha256'],'recovery_proved':'scoped logical cursor and policy only'})
    append(rows,'R3_EXECUTION_CEILING','PASS',
           {'actual_model_calls':0,'actual_experiments_executed':0,'actual_sessions_created':0,
            'human_authority_granted':False,'disallowed_effects':t.disclosure({**t.unrank(spec,0),'effect':'EXTERNAL_ACTION'})})
    measurements={
        'manifest_hash_median_ms':elapsed_ms(lambda:t.digest((HERE/'space_manifest.json').read_bytes())),
        'decode_random_index_median_ms':elapsed_ms(lambda:t.unrank(spec,t.capacity(spec)//3)),
        'checkpoint_verify_median_ms':elapsed_ms(lambda:t.validate_checkpoint(spec,spec_hash,cp)),
        'bounded_16_descriptions_median_ms':elapsed_ms(lambda:t.peek(spec,cp,16))
    }
    append(rows,'R3_LOCAL_CPU_BENCHMARK','PASS',
           {'measurements':measurements,'trials_per_measurement':101,
            'limits':'This execution environment only; not Mac, inference latency, power, or trillion-way execution.'})
    for name, reason in [
        ('R3_MAC_REPRODUCTION','No Mac under authorized observation; independent Andrew reproduction not completed.'),
        ('R3_CLAUDE_PI_OLLAMA','Provider integrations/credential availability and per-model latency not tested.'),
        ('R3_MILLION_WORKER_COORDINATION','No distributed lease, idempotency, activation or receiver uptake tested.'),
        ('R3_MEDIA','No video or thumbnail supplied for ffprobe/size/blackdetect checks.'),
    ]:
        append(rows,name,'NOT_RUN',{'reason':reason})
    append(rows,'R3_PROMOTION_GATE','HOLD',
           {'reason':'Only logical-cursor continuity and local sandbox proofs; independent custody/receiver uptake missing.',
            'publication':'draft_PR_only','recommended_next':'Andrew Mac independent reproduction + empirical workload baseline'})

    path=outdir/'benchmark_evo_R3.jsonl'; headpath=outdir/'HEAD_R3.sha256'
    path.write_text(''.join(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n' for x in rows),encoding='utf-8')
    headpath.write_text(rows[-1]['event_hash']+'\n',encoding='ascii')
    assert verify(path,rows[-1]['event_hash'])==len(rows)
    counts={s:sum(r['outcome']==s for r in rows) for s in ('PASS','FAIL','HOLD','NOT_RUN')}
    summary={'schema':'CoStretchCheckpointEvidence/3','spec_sha256':spec_hash,'r2_source_sha256':old_sha,
             'r2_source_head':r2head,'new_head':rows[-1]['event_hash'],'total_events':len(rows),'added_events':len(rows)-28,
             'status_counts':counts,'new_python_tests':test_count,'negative_cross_runtime_cases':len(scenarios),
             'measurements':measurements,'baseline_failure':'SAME_COUNT_SEMANTIC_DRIFT',
             'corrective_behavior':'SPEC_NAMESPACE_CHANGED_FAIL_CLOSED',
             'nonclaims':['No hardware Mac test','No provider/model integration','No million live sessions',
                          'No signed provenance or independently witnessed user adoption',
                          'No real-world gain calibration']}
    (outdir/'R3_REPORT.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (outdir/'test_results.txt').write_text(suite.stderr,encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
