#!/usr/bin/env python3
"""Recompute hashes and independent local receiver readback from a saved run."""
import argparse
import json
from pathlib import Path
from coall_braid import reconcile
from run_demo import verify_benchmark


def verify(out):
    out=Path(out)
    report=json.loads((out/'acceptance_report.json').read_text())
    benchmark_head=(out/'HEAD.sha256').read_text().strip()
    run_head=(out/'DEMO_HEAD.sha256').read_text().strip()
    assert benchmark_head==report['benchmark_head']
    assert run_head==report['journal_head']
    records=verify_benchmark(out/'benchmark_evo.jsonl',benchmark_head)
    assert len(records)==11
    result=reconcile(out/'demo_work',report['task_sha256'],run_head)
    assert result==report['recovered']
    assert result['all_local_acked']
    print(json.dumps({'status':'PASS_LOCAL_CROSS_PROCESS_READBACK','receiver_count':2,
                      'benchmark_events':len(records),'journal_head':run_head,
                      'task_sha256':report['task_sha256']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True)
    args=p.parse_args()
    verify(args.out)
