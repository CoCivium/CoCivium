#!/usr/bin/env python3
"""Synthetic selector comparison, explicitly not real user benefit."""
import json
import statistics
import time
from pathlib import Path
import nexus

def run(trials=20, sample=512, pick=12):
    if not (1 <= trials <= 100 and 1 <= sample <= 2048 and 1 <= pick <= min(sample, 16)):
        raise ValueError('INVALID_BENCHMARK_BOUNDS')
    cases=[]
    for seed in range(trials):
        ids = sorted(set())
        import random
        rng = random.Random(seed)
        while len(ids) < sample: ids = sorted(set(ids) | {rng.randrange(nexus.capacity())})
        # No live work, no private payload: all results are artificial payoffs.
        fixture = [nexus.candidate(i) for i in ids]
        scored = sorted(fixture, key=lambda c: (-c['priority_score_synthetic'], c['index']))[:pick]
        baseline = fixture[:pick]
        normal = lambda arr: sum(c['priority_score_synthetic'] for c in arr)
        reverse = lambda arr: sum(-c['priority_score_synthetic'] for c in arr)
        delta_normal = normal(scored)-normal(baseline)
        delta_adversarial = reverse(scored)-reverse(baseline)
        cases.append({'seed':seed,'selector_score_synthetic':normal(scored),
                      'baseline_score_synthetic':normal(baseline),
                      'normal_delta':delta_normal,'adversarial_delta':delta_adversarial})
    return {'schema':'CoDoodleNexus.SyntheticChallenge.R0', 'trials':trials,
            'baseline':'lowest-index of same pseudo-random sample',
            'selector':'highest predeclared synthetic priority on same sample',
            'adversarial':'exact negation of the assumed synthetic priority',
            'outcome_normal':{'wins':sum(c['normal_delta']>0 for c in cases),
                              'ties':sum(c['normal_delta']==0 for c in cases),
                              'losses':sum(c['normal_delta']<0 for c in cases)},
            'outcome_adversarial':{'wins':sum(c['adversarial_delta']>0 for c in cases),
                                   'ties':sum(c['adversarial_delta']==0 for c in cases),
                                   'losses':sum(c['adversarial_delta']<0 for c in cases)},
            'cases':cases, 'not_measured':['real utility','AI inference','human comprehension','energy','provider speed']}

def measure(samples=256, repeats=7):
    # Benchmarks are in-process CPU figures, not fleet throughput guarantees.
    series=[]
    for _ in range(repeats):
        start=time.perf_counter_ns()
        out=nexus.compile_shadow(sample_count=samples, selected_count=12)
        end=time.perf_counter_ns()
        assert len(out['candidates'])==12
        series.append((end-start)/1e6)
    return {'host':'isolated container Python', 'sample':samples, 'repeats':repeats,
            'median_compile_ms':round(statistics.median(series),3),
            'min_ms':round(min(series),3),'max_ms':round(max(series),3),
            'warning':'Descriptor planning only; no experiment/model execution'}

if __name__=='__main__':
    outcome=run();outcome['timing']=measure()
    path=Path('output/challenge.json');path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(outcome,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'normal':outcome['outcome_normal'],'adversarial':outcome['outcome_adversarial'],
                      'median_compile_ms':outcome['timing']['median_compile_ms']},sort_keys=True))
