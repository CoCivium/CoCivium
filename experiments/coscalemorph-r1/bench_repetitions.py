#!/usr/bin/env python3
"""Matched CPU synthetic benchmark, not sustained capacity or energy proof."""
import json
import statistics
from pathlib import Path
from benchmark import execute
from coscalemorph import planning_frontier


def nearest_rank_p95(values):
    a=sorted(values)
    return a[min(len(a)-1, max(0, (95*len(a)+99)//100-1))]


def main():
    observations={1:[], 2:[]}
    # Interleave to lessen but not remove drift and scheduling artifacts.
    for order in [[1,2],[2,1],[1,2],[2,1],[1,2]]:
        for width in order:
            observations[width].append(execute(width))
    hashes={z['work_digest_sha256'] for vals in observations.values() for z in vals}
    assert len(hashes)==1
    stats={}
    for width, obs in observations.items():
        a=[x['elapsed_seconds'] for x in obs]
        stats[str(width)]={'repetitions':len(a), 'seconds':a,
                           'p50_s':round(statistics.median(a),6),
                           'p95_s':round(nearest_rank_p95(a),6),
                           'all_outputs_match':True}
    plan=planning_frontier(10**12,10**6,max_workers=2,actual_tasks=12)
    return {
      'schema':'CoScaleMorph.RepeatedMultiprocessing/R1',
      'work_type':'SYNTHETIC_CPU_SHA256',
      'task_count_per_trial':12,
      'matched_digest_sha256':next(iter(hashes)),
      'widths':[1,2],
      'measured':stats,
      'logical_slots':plan['logical_slots'],
      'actual_process_workers_per_parallel_trial':2,
      'actual_trillion_workers_spawned':False,
      'energy_joules':None,
      'memory_peak_bytes':None,
      'sustained_scaling_proven':False,
      'statistical_significance_established':False,
      'nonclaims':['FIVE_TRIALS_NE_PRODUCTION_BENCHMARK','NOT_ENERGY_METERED','PARALLELISM_NE_USEFUL_GAIN'],
    }

if __name__=='__main__':
    result=main()
    p=Path(__file__).resolve().parent/'output/bench_repetitions.json'
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
