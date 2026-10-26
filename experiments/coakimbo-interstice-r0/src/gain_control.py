#!/usr/bin/env python3
"""Finite synthetic gain-control baseline vs sensor shift. NOT operational benefit.

Illustrates that positive feedback filtered by fallible estimates can improve
or worsen returns. Equal aggregate action budget; no physical units, models,
provider sessions, energy claims or human observations.
"""
import json
from pathlib import Path
import numpy as np

STEPS = 120
BUDGET = 38.0
POLICIES = ('conservative', 'amplify_all', 'evidence_proxy')
SCENARIOS = ('calibrated_proxy', 'reversed_proxy')


def run(seed=20261026, scenario='calibrated_proxy', policy='evidence_proxy'):
    if scenario not in SCENARIOS or policy not in POLICIES:
        raise ValueError('INVALID_SCENARIO_OR_POLICY')
    rng = np.random.default_rng(seed)
    real_effect = .3 + rng.normal(0, .95, STEPS)
    sensor_noise = rng.normal(0, .15, STEPS)
    proxy = real_effect + sensor_noise if scenario == 'calibrated_proxy' else -real_effect + sensor_noise
    remaining = BUDGET
    score = 0.0
    actions=[]
    for t in range(STEPS):
        if policy == 'conservative': wanted = .25
        elif policy == 'amplify_all': wanted = 1.0
        else: wanted = .95 if proxy[t] > .25 else .05
        a = min(wanted,remaining)
        remaining-=a
        score += a*real_effect[t] - .10*a*a
        actions.append(a)
    return {'seed':seed, 'scenario':scenario, 'policy':policy,
            'net_utility_toy':round(float(score),6),
            'action_budget_spent':round(float(sum(actions)),6),
            'action_budget_cap':BUDGET,
            'actions_started':int(sum(x>0 for x in actions))}


def study(seeds=12):
    matrix={}
    for s in SCENARIOS:
        rows=[[run(20261026+i,s,p) for p in POLICIES] for i in range(seeds)]
        med={p:round(float(np.median([r[j]['net_utility_toy'] for r in rows])),6)
             for j,p in enumerate(POLICIES)}
        # A selector is tested against the BEST baseline per seed, not mean baseline.
        wins=ties=losses=0
        for r in rows:
            candidate=r[2]['net_utility_toy']
            base=max(r[0]['net_utility_toy'],r[1]['net_utility_toy'])
            if candidate>base+1e-6:wins+=1
            elif candidate<base-1e-6:losses+=1
            else:ties+=1
        matrix[s]={'seeds':seeds,'median_net_toy_utility':med,'wins':wins,'ties':ties,'losses':losses,
                   'note':'Synthetic outcomes, no measured real task benefit or generalized policy superiority'}
    return matrix

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'output'/'gain_control.json'
    p.write_text(json.dumps(study(),indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(p.read_text())
