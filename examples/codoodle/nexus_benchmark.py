#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import platform
import statistics
import time
from pathlib import Path
import codoodle
import nexus

here=Path(__file__).resolve().parent
raw=(here/'sample_synthetic.txt').read_text(encoding='utf-8')
parent=codoodle.compile_doodle(raw)
fixture=nexus.expand(parent,20261024,fanout=3,max_total=16)
(here/'nexus_synthetic_example.json').write_text(json.dumps(fixture,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def bench(count, fanout, total):
    for _ in range(250):nexus.expand(parent,20261024,fanout=fanout,max_total=total)
    times=[]
    for _ in range(count):
        t=time.perf_counter_ns()
        nexus.expand(parent,20261024,fanout=fanout,max_total=total)
        times.append(time.perf_counter_ns()-t)
    times.sort()
    return {'iterations':count,'median_us':round(statistics.median(times)/1000,3),
            'p95_us':round(times[int((len(times)-1)*.95)]/1000,3),
            'p99_us':round(times[int((len(times)-1)*.99)]/1000,3)}

receipt={
    'schema':'CoNex.LocalSyntheticBenchmark.R0',
    'scope':'ISOLATED_CONTAINER_NOT_X2_NOT_PROVIDER_NOT_RUNTIME_SERVICE',
    'environment':{'python':platform.python_version(),'os':platform.system(),'arch':platform.machine()},
    'base_fixture_bytes':len(raw.encode('utf-8')),
    'parent_candidates':len(parent['candidates']),
    'sample_seed_u64':20261024,
    'sample_fanout':3,
    'sample_max_total':16,
    'sample_emitted':fixture['emitted'],
    'source_sha256':hashlib.sha256((here/'nexus.py').read_bytes()).hexdigest(),
    'results':{
      'default_fanout2_max12':bench(1000,2,12),
      'fanout3_max24':bench(1000,3,24)
    },
    'nonclaims':['MICROSECOND_BRANCH_SELECTION_NE_MICROSECOND_REASONING',
       'SOURCE_CATALOG_NE_DATA_INGESTION','SELECTOR_DESCRIPTOR_NE_EXECUTED_EXPERIMENT',
       'NO_AUTONOMOUS_KEYBOARD_OR_ACCOUNT_CONTROL','LOCAL_TIMING_NE_X2_TIMING']
}
(here/'nexus_benchmark_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
