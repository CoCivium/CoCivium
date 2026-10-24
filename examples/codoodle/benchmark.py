#!/usr/bin/env python3
"""Bounded local microbenchmark; no IO in measured functions."""
from __future__ import annotations
import json
import platform
import statistics
import time
from pathlib import Path
from codoodle import compile_doodle, trigger_probe

ROOT=Path(__file__).resolve().parent
base=(ROOT/'sample_synthetic.txt').read_text(encoding='utf-8')
inputs={'sample_923b':base,'repeated_approx_3_7kb':base*4,'no_match_3_7kb':'x'*3692,'no_match_64kb':'x'*65536}

def measure(fn, text, iterations):
    for _ in range(150):fn(text)
    samples=[]
    for _ in range(iterations):
        t0=time.perf_counter_ns()
        fn(text)
        samples.append(time.perf_counter_ns()-t0)
    samples.sort()
    return {'iterations':iterations,'median_us':round(statistics.median(samples)/1000,3),
            'p95_us':round(samples[int(.95*(len(samples)-1))]/1000,3),
            'p99_us':round(samples[int(.99*(len(samples)-1))]/1000,3),
            'min_us':round(samples[0]/1000,3)}
report={'schema':'CoDoodle.LocalMicrobenchmark.R0','test_type':'ISOLATED_LOCAL_SYNTHETIC',
  'environment':{'python':platform.python_version(),'machine':platform.machine(),'platform':platform.system()},
  'results':{},'limits':['Wall-clock per-call timing includes Python invocation overhead',
    'No operating system input hook, model, network, file IO, semantic verification or real experiment inside measured region',
    'Timing on isolated container, not X2, not an SLA or an infinite-rate proof']}
for label,content in inputs.items():
    count = 100 if label=='no_match_64kb' else (1000 if label=='no_match_3_7kb' else 2000)
    report['results'][label]={'bytes':len(content.encode('utf-8')),
       'hot_trigger':measure(trigger_probe,content,20000 if count>100 else 500),
       'full_seed_compiler':measure(compile_doodle,content,count)}
(ROOT/'benchmark_receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
