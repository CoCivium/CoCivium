#!/usr/bin/env python3
"""Deterministic CoResourceFrontier canary. No workers, network or OS actions."""
from __future__ import annotations

import hashlib
import json
import random
import string
from pathlib import Path

POLICIES = ('first_n', 'random', 'keyword', 'evidence', 'novelty', 'challenge')
UNITS = ('cpu_units', 'energy_estimate_units', 'attention_units')
SAFE_EFFECT = 'SHADOW_READ'


def compact_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def identity(task):
    """Scoped reference only. Never a credential, cryptographic signature, or permission."""
    return 'candidate-ref:' + compact_hash([task['namespace'], task['source_sha256'], task['revision']])


def gate(task, receiver):
    if task['effect'] != SAFE_EFFECT:
        return 'HELD_EFFECT_NOT_SHADOW'
    if task['kind'] == 'PHYSICAL_ENERGY_HARVEST':
        return 'HELD_REQUIRES_INDEPENDENT_PHYSICAL_MEASUREMENT'
    if not task['current'] or not task['material_wake']:
        return 'DORMANT_NO_MATERIAL_WAKE'
    if not task['source_sha256'] or len(task['source_sha256']) != 64 or any(c not in string.hexdigits for c in task['source_sha256']):
        return 'HELD_NO_EXACT_SOURCE_PIN'
    if not task['consent'] or not task['authorized']:
        return 'HELD_CONSENT_OR_AUTHORITY'
    if task['privacy'] != 'PUBLIC' or task['receiver'] != receiver:
        return 'HELD_RECEIVER_OR_PRIVACY'
    if not task['provenance']:
        return 'HELD_NO_PROVENANCE'
    if any(task['cost'][unit] < 0 for unit in UNITS):
        return 'HELD_NEGATIVE_COST'
    return 'ELIGIBLE_SHADOW_ONLY'


def order_tasks(tasks, policy, seed=17):
    if policy not in POLICIES:
        raise ValueError('unknown selection policy')
    result = list(tasks)
    if policy == 'random':
        random.Random(seed).shuffle(result)
    elif policy == 'keyword':
        result.sort(key=lambda x: (-x['keyword'], x['id']))
    elif policy in ('evidence', 'novelty', 'challenge'):
        result.sort(key=lambda x: (-x[policy], x['id']))
    return result


def run_shadow(fixture, policy, offline=(), max_wave=None):
    """Planning only: no resource leases, processes, effects, subscriptions or sends."""
    receiver = fixture['receiver']
    resources = [dict(node, available=(node['available'] and node['id'] not in offline
                  and all(0 <= node['reserve'][u] <= node['capacity'][u] for u in UNITS)))
                 for node in fixture['resources']]
    residual = {node['id']: {unit: node['capacity'][unit] - node['reserve'][unit] for unit in UNITS} for node in resources}
    held = {}
    candidates = []
    seen = {}
    for task in fixture['tasks']:
        verdict = gate(task, receiver)
        if verdict != 'ELIGIBLE_SHADOW_ONLY':
            held[task['id']] = verdict
            continue
        dedupe_key = (task['namespace'], task['semantic_key'], task['source_sha256'], task['revision'], task['receiver'], task['privacy'])
        if dedupe_key in seen:
            held[task['id']] = 'DEDUPED_EXACT_WORK_OF:' + seen[dedupe_key]
            continue
        seen[dedupe_key] = task['id']
        candidates.append(task)
    chosen = []
    wave = fixture['max_wave'] if max_wave is None else min(fixture['max_wave'], int(max_wave))
    if not 0 <= wave <= 32:
        raise ValueError('wave must be bounded between 0 and 32')
    for task in order_tasks(candidates, policy):
        if len(chosen) >= wave:
            held[task['id']] = 'DORMANT_WAVE_CAP'
            continue
        accepted_node = None
        for node in sorted(resources, key=lambda x: x['id']):
            if not node['available'] or task['capability'] not in node['capabilities']:
                continue
            if node['tenant'] != task['tenant'] or task['privacy'] not in node['clearances']:
                continue
            if all(residual[node['id']][unit] >= task['cost'][unit] for unit in UNITS):
                accepted_node = node
                break
        if accepted_node is None:
            held[task['id']] = 'HELD_NO_QUALIFIED_RESOURCE_WITH_RESERVE'
            continue
        for unit in UNITS:
            residual[accepted_node['id']][unit] -= task['cost'][unit]
        chosen.append({'task': task['id'], 'node': accepted_node['id'], 'scope_ref': identity(task),
                       'cost': task['cost'], 'source_sha256': task['source_sha256'],
                       'receiver_value_proxy': task['receiver_value_proxy']})
    result = {'schema': 'CoResourceFrontier.ShadowAllocator.R0', 'policy': policy,
              'source_pin': compact_hash(fixture), 'receiver': receiver,
              'effect_ceiling': 'ZERO_EXTERNAL_EFFECTS', 'selected': chosen,
              'held': dict(sorted(held.items())), 'residual': residual,
              'projected_value_proxy': sum(x['receiver_value_proxy'] for x in chosen),
              'projected_units_consumed': {unit: sum(x['cost'][unit] for x in chosen) for unit in UNITS},
              'nonclaims': ['PROXY_NE_REAL_BENEFIT', 'SHADOW_NE_EXECUTION',
                            'RESOURCE_CANDIDATE_NE_WORKER', 'PHYSICAL_HARVEST_NOT_TESTED',
                            'POINTER_NE_RECEIVER_ACK', 'RESOURCE_ALLOCATION_NE_GLOBAL_OPTIMUM']}
    result['plan_sha256'] = compact_hash(result)
    return result


def route_event(event, subscribers, fanout_limit=2):
    """Simulated opt-in notification. Returns IDs only; no network/message emission."""
    if not 0 < fanout_limit <= 32:
        return []
    routed = []
    for receiver in sorted(subscribers, key=lambda x: x['id']):
        if receiver['opt_in'] and event['topic'] in receiver['topics'] and \
           event['privacy'] in receiver['clearances'] and event['authority'] in receiver['permissions']:
            routed.append(receiver['id'])
        if len(routed) >= fanout_limit:
            break
    return routed


def load_fixture():
    return json.loads(Path(__file__).with_name('fixture.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    f = load_fixture()
    print(json.dumps({'schema': 'CoResourceFrontier.ShadowComparison.R0',
                      'fixture_sha256': compact_hash(f),
                      'results': [run_shadow(f, name) for name in POLICIES]}, indent=2, sort_keys=True))
