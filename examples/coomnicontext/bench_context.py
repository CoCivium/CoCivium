#!/usr/bin/env python3
import json
import statistics
import time
from pathlib import Path
from CoOmniContextCompilerR0 import compile_packet, rehydrate_public, canonical_json
source=json.loads(Path(__file__).with_name('fixture_public_only.json').read_text())
packet=compile_packet(source,1400)
loops=5000
trials=[]
for trial in range(4):
    start=time.perf_counter_ns()
    for _ in range(loops):
        compile_packet(source,1400)
    ms=(time.perf_counter_ns()-start)/1e6
    trials.append(ms/loops)
orig_bytes=len(canonical_json(source))
out_bytes=len(canonical_json(packet))
result={
 'schema':'CoOmni.ContextCompiler.BenchmarkR0',
 'workload':'5 synthetic sources; 1 restricted; 1 challenge; one 1400-byte public packet; local Python-only, no network',
 'host_class':'container Linux; Python 3 stdlib; CPU not calibrated',
 'iterations_per_trial':loops,'trials':len(trials),
 'median_milliseconds_per_compile':round(statistics.median(trials),6),
 'source_compact_bytes':orig_bytes,'packet_compact_bytes':out_bytes,
 'reduction_ratio_bytes':round(orig_bytes/out_bytes,3),
 'actual_selected_sources':len(packet['sources']),
 'withheld_nonpublic':packet['withheld_nonpublic'],
 'omitted_public':packet['omitted_public'],
 'status':packet['status'],
 'qualifications':['Source texts are synthetic, not actual large archives or model-context retrieval', 'Amortized batch timing is not p95 user latency', 'Source digest tests are local, not independent custodian readproof', 'Zero token/provider/runtime integration'],
 }
Path(__file__).with_name('benchmark_R0.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
