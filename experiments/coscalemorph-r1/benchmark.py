"""Bounded actual multiprocessing canary: same work one vs two processes.

Only 12 public synthetic SHA workloads; measures wall time, not energy savings.
"""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import time
from pathlib import Path
from coscalemorph import planning_frontier


def work(i: int):
    assert type(i) is int and 0 <= i < 12
    digest = hashlib.sha256(f'CoScaleMorph:R0:{i}'.encode()).digest()
    for _ in range(20000):
        digest = hashlib.sha256(digest).digest()
    return i,digest.hex()


def execute(width: int):
    if width not in (1,2):
        raise ValueError('WIDTH_UNQUALIFIED')
    t = time.perf_counter()
    if width==1:
        result = list(map(work, range(12)))
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
            result=list(pool.map(work,range(12)))
    checksum=hashlib.sha256(json.dumps(result, separators=(',',':')).encode()).hexdigest()
    return {'width':width,'task_count':len(result),'work_digest_sha256':checksum,'elapsed_seconds':round(time.perf_counter()-t,6)}


def main():
    plan=planning_frontier(10**12,10**6,max_workers=2,actual_tasks=12)
    serial=execute(1)
    parallel=execute(2)
    if serial['work_digest_sha256']!=parallel['work_digest_sha256']:
        raise RuntimeError('RESULT_MISMATCH')
    result={
       'schema':'CoScaleMorph.MultiprocessCanary/R0',
       'logical_slots':plan['logical_slots'],
       'planned_max_workers':plan['eligible_worker_ceiling'],
       'actual_widths_tested':[1,2],
       'work_type':'SYNTHETIC_SHA256_CPU_ONLY',
       'serial':serial,'parallel':parallel,
       'equal_output':True,
       'relative_speedup':round(serial['elapsed_seconds']/max(parallel['elapsed_seconds'],0.000001),3),
       'energy_measured':False,
       'sustained_scaling_proven':False,
       'receiver_acks':0,
       'remote_provider_calls':0,
       'nonclaims':['ONE_SHORT_RUN_NE_UNIVERSAL_SPEEDUP','LOGICAL_SPACE_NE_MATERIALIZED_WORKERS','EQUAL_HASH_NE_DOMAIN_QUALITY']
    }
    dest=Path(__file__).parent/'output/multiprocess_canary.json'
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__': main()
