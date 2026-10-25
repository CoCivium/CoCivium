#!/usr/bin/env python3
"""CoDoodleNexus R0: finite, shadow-only combinatorial experiment compiler.

Uses only Python stdlib. No spawning, network, accounts, mouse/keyboard hooks,
clipboard, model calls, timers, hidden persistence or external effects.
"""
import argparse
import hashlib
import json
import math
import random
import re
from collections import OrderedDict
from pathlib import Path

DIMENSIONS = OrderedDict([
    ('relation', ('IN', 'BETWEEN', 'INVERT', 'OUT', 'NOT', 'ALTERNATIVE', 'QUESTION', 'REPAIR')),
    ('surface', ('TEXT', 'MAP', 'ORB', 'TRAIL', 'GLYPH', 'ACCESSIBLE_TABLE', 'TIMELINE')),
    ('lens', ('STORY', 'SYSTEMS', 'SCIENCE', 'ETHICS', 'COUNTERFACTUAL', 'ACCESSIBILITY')),
    ('substrate', ('DETERMINISTIC', 'LOCAL_MODEL_OPTION', 'REMOTE_MODEL_OPTION', 'HUMAN_REVIEW', 'SIMULATION', 'UNKNOWN')),
    ('evidence', ('SOURCE', 'NEGATIVE', 'BASELINE', 'RECEIPT', 'REPRO', 'HYPOTHESIS', 'CONSENT')),
    ('process', ('LOGICAL', 'DORMANT', 'PREPARED', 'ACTIVE_PROPOSED', 'REVIEW_PROPOSED', 'RECOVER_PROPOSED')),
    ('benchmark', ('CORRECTNESS', 'LATENCY', 'COST', 'RECOVERY', 'ACCESSIBILITY', 'PRIVACY', 'COUNTEREXAMPLE', 'DUPLICATION', 'ENERGY')),
    ('temporal', ('PAST', 'NOW', 'PREDICTED', 'REVISED', 'SHADOW')),
    ('authority', ('NONE', 'OPT_IN_REQUIRED', 'REVIEW_REQUIRED', 'HOLD', 'REVOKED')),
    ('scope', ('SYNTHETIC', 'PUBLIC_REFERENCE', 'PRIVATE_LOCAL', 'UNKNOWN')),
    ('fault', ('NO_FAULT', 'STALE', 'KILL', 'SOURCE_MISSING', 'CORRUPT', 'LEASE_CONFLICT', 'BYSTANDER')),
    ('observer', ('USER', 'BUILDER', 'REVIEWER', 'DEVICE', 'REMOTE', 'MODEL', 'OBSERVER', 'UNKNOWN', 'THIRD_PARTY')),
    ('counterfactual', ('NONE', 'BASELINE', 'INVERSE', 'MISSING', 'NEGATED', 'HISTORICAL', 'ALTERNATIVE')),
    ('glyph', ('DOT', 'ARROW', 'ORBIT', 'TRAIL', 'INVERSION', 'FORK', 'EMPTY')),
    ('review_seat', ('PROPOSAL', 'FORMAL', 'EMPIRICAL', 'CHALLENGE', 'PROVENANCE', 'SYNTHESIS')),
])

# Strictly finite, bounded, output-sparing defaults. Logical capacity may be large.
MAX_INPUT = 20000
MAX_SAMPLE = 2048
MAX_SELECTION = 16
DEFAULT_TEXT = ('CoIn CoBetween CoInv CoOut CoOrb CoMap CoDoodle CoEvo '
                'CoTurtle CoNexus CoZombie source recovery lens observer Planck '
                'quantum G_d aura access consent replay and challenge')
KEYWORDS = OrderedDict([
    ('INPUT', (r'\bco(?:in|input)\b', r'\bkeyboard\b', r'\bkeypress')), 
    ('BETWEEN', (r'\bbetween\b', r'\binterstice\b', r'\bgap\b')), 
    ('INVERT', (r'\bco(?:inv|inver|inversion)\b', r'\binvers')), 
    ('OUTPUT', (r'\bco(?:out|output)\b', r'\bprojection\b')), 
    ('MOUSE', (r'\bmouse\b', r'\bthumb\b', r'\bpointer\b')), 
    ('MAP_ORB', (r'\bco(?:map|orb|orbware)\b', r'\blens\b')), 
    ('RECOVERY', (r'\bcozombie\b', r'\bstuck\b', r'\brecover')), 
    ('SCIENCE_TERM', (r'\bplanck\b', r'\bquantum\b')), 
    ('SYMBOLIC', (r'\bg_d\b', r'\bspirit\b', r'\baura\b', r'\bmyth')), 
    ('SYNTHKIND_THEME', (r'\bsynthkind\b',)), 
    ('PRIVACY', (r'\bconsent\b', r'\bprivacy\b', r'\bauthorit')), 
])

def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')).hexdigest()

def capacity():
    return math.prod(map(len, DIMENSIONS.values()))

def unrank(index):
    if isinstance(index, bool) or not isinstance(index, int) or index < 0 or index >= capacity():
        raise ValueError('INDEX_OUT_OF_BOUNDS')
    result = {}
    for name, options in reversed(DIMENSIONS.items()):
        index, digit = divmod(index, len(options))
        result[name] = options[digit]
    return {name: result[name] for name in DIMENSIONS}

def rank(choices):
    if set(choices) != set(DIMENSIONS):
        raise ValueError('DIMENSIONS_MISMATCH')
    index = 0
    for name, options in DIMENSIONS.items():
        value = choices[name]
        if value not in options:
            raise ValueError('INVALID_OPTION:' + name)
        index = index * len(options) + options.index(value)
    return index

def tags_from(text):
    if not isinstance(text, str) or len(text) > MAX_INPUT:
        raise ValueError('INPUT_TOO_LONG')
    return [key for key, patterns in KEYWORDS.items()
            if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)]

def classify(c):
    """All outputs are descriptions, never executable plans or authorization."""
    if c['scope'] == 'PRIVATE_LOCAL':
        return 'HELD_PRIVATE_CONTEXT'
    if c['scope'] == 'UNKNOWN':
        return 'HELD_UNKNOWN_SOURCE'
    if c['authority'] == 'REVOKED':
        return 'HELD_REVOKED'
    if c['substrate'] == 'UNKNOWN':
        return 'HELD_UNKNOWN_SUBSTRATE'
    if c['authority'] in ('OPT_IN_REQUIRED', 'REVIEW_REQUIRED', 'HOLD'):
        return 'SHADOW_ONLY_REQUIRES_PERMISSION'
    return 'SHADOW_ONLY_PUBLIC_OR_SYNTHETIC'

def estimate(c):
    """Arbitrary synthetic priority heuristic; not actual value or intelligence."""
    score = 0
    score += 6 if c['substrate'] == 'DETERMINISTIC' else 1
    score += 4 if c['scope'] == 'SYNTHETIC' else 1
    score += 5 if c['authority'] == 'NONE' else -4
    score += 3 if c['evidence'] in ('NEGATIVE', 'REPRO', 'SOURCE') else 0
    score += 2 if c['benchmark'] in ('RECOVERY', 'PRIVACY', 'CORRECTNESS') else 0
    score += 2 if c['fault'] != 'NO_FAULT' else 0
    score -= 2 if c['process'] == 'ACTIVE_PROPOSED' else 0
    return score

def test_plan(c):
    if c['fault'] in ('CORRUPT', 'SOURCE_MISSING', 'LEASE_CONFLICT', 'BYSTANDER'):
        return 'Inject a synthetic ' + c['fault'] + ' case; assert HOLD without effects'
    if c['relation'] in ('NOT', 'INVERT', 'ALTERNATIVE'):
        return 'Compare original synthetic claim with inverted/counterfactual fixture and preserve failure'
    if c['benchmark'] == 'RECOVERY':
        return 'Measure exact-source digest after synthetic checkpoint and replay'
    return 'Run deterministic baseline and challenging negative case on public/synthetic fixture'

def candidate(index):
    dims = unrank(index)
    return {
        'id': sha({'v': 'CoDoodleNexus/1', 'index': index, 'dimensions': dims})[:20],
        'index': index, 'dimensions': dims, 'state': classify(dims),
        'proposed_test': test_plan(dims), 'priority_score_synthetic': estimate(dims),
        'effect_authority': 'NONE', 'work_done': False, 'worker_spawned': False,
    }

def compile_shadow(text=DEFAULT_TEXT, seed=17, sample_count=512, selected_count=12):
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError('BAD_SEED')
    if not (1 <= sample_count <= MAX_SAMPLE and 1 <= selected_count <= MAX_SELECTION and selected_count <= sample_count):
        raise ValueError('BOUNDS_EXCEEDED')
    detected = tags_from(text)
    rng = random.Random(seed)
    sampled = set()
    while len(sampled) < sample_count:
        sampled.add(rng.randrange(capacity()))
    # The index roundtrip property is stronger than a label-count claim.
    records = [candidate(i) for i in sampled]
    records.sort(key=lambda c: (-c['priority_score_synthetic'], c['index']))
    selection = records[:selected_count]
    return {
        'schema': 'CoDoodleNexus.ShadowCompilation.R0',
        'manifest_hash': sha(DIMENSIONS),
        'input_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
        'recognized_terms_only': detected, 'raw_input_stored': False,
        'logical_capacity': capacity(), 'sample_size': sample_count,
        'selected_size': len(selection), 'seed': seed,
        'no_effects': True, 'actual_experiments_run': 0, 'live_agents_started': 0,
        'provider_calls': 0, 'clipboard_reads': 0, 'global_keyboard_hooks': 0,
        'remote_receiver_acks': 0, 'candidates': selection,
        'notes': [
            'Scores are synthetically assigned, not validated productivity.',
            'A scientific term in a prompt is not proof of a new scientific claim.',
            'Spiritual/symbolic terms are labels for hypothesis or storytelling only.',
            'No candidate is authorized to execute or contact anyone.',
        ],
    }

def verify_compilation(result):
    if result.get('schema') != 'CoDoodleNexus.ShadowCompilation.R0':
        raise ValueError('BAD_SCHEMA')
    if result.get('manifest_hash') != sha(DIMENSIONS):
        raise ValueError('SPEC_NAMESPACE_CHANGED')
    if result.get('logical_capacity') != capacity():
        raise ValueError('CAPACITY_MISMATCH')
    cs = result.get('candidates')
    if not isinstance(cs, list) or len(cs) > MAX_SELECTION:
        raise ValueError('UNBOUNDED_CANDIDATES')
    if result.get('actual_experiments_run') != 0 or result.get('live_agents_started') != 0:
        raise ValueError('FALSE_EXECUTION_CLAIM')
    for c in cs:
        expected = candidate(c['index'])
        if c != expected:
            raise ValueError('CANDIDATE_DRIFT')
    return True

def main():
    p = argparse.ArgumentParser(description='Compile bounded CoDoodles to offline shadow descriptors')
    p.add_argument('--input', type=Path, help='Explicit local text file; no raw text in output')
    p.add_argument('--seed', type=int, default=17)
    p.add_argument('--sample', type=int, default=512)
    p.add_argument('--select', type=int, default=12)
    p.add_argument('--out', type=Path, default=Path('output/shadow_candidates.json'))
    a = p.parse_args()
    text = a.input.read_text(encoding='utf-8') if a.input else DEFAULT_TEXT
    result = compile_shadow(text, a.seed, a.sample, a.select)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS_DESCRIPTOR_ONLY', 'capacity': result['logical_capacity'],
                      'sampled': a.sample, 'selected': a.select,
                      'real_experiments': 0, 'output': str(a.out)}, sort_keys=True))

if __name__ == '__main__':
    main()
