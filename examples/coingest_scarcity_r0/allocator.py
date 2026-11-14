#!/usr/bin/env python3
"""CoIngest+ -> CoResourceFrontier+ deterministic, no-actuation synthetic test.

No money movement, model/provider invocation, outreach, or personal data. A
candidate is an investment OPTION in scarce capacity, not investment advice.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path

RESOURCE_KEYS = ('cpu_units', 'energy_units', 'reviewer_minutes', 'human_minutes', 'cash_cents', 'worker_slots')
ALLOWED_AUTHORITY = 'READ_ONLY_SIMULATION'


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def validate_candidate(c: dict) -> list[str]:
    errors = []
    if not isinstance(c, dict):
        return ['NOT_OBJECT']
    if not isinstance(c.get('work_id'), str) or not c['work_id']:
        errors.append('MISSING_WORK_ID')
    if c.get('authority') != ALLOWED_AUTHORITY or c.get('effect') != 'NONE':
        errors.append('EFFECT_OR_AUTHORITY_HELD')
    if c.get('requires_human_gate') is not False or c.get('privacy') != 'PUBLIC_SYNTHETIC':
        errors.append('HUMAN_OR_PRIVACY_GATE')
    if c.get('reversible') is not True or c.get('proof_plan') != 'DETERMINISTIC_FIXTURE':
        errors.append('PROOF_OR_REVERSIBILITY_HELD')
    if c.get('evidence_class') != 'SYNTHETIC_BENCHMARK':
        errors.append('UNQUALIFIED_EVIDENCE_CLASS')
    if not isinstance(c.get('evidence_text'), str) or digest(c.get('evidence_text', '')) != c.get('source_sha256'):
        errors.append('SOURCE_DIGEST_MISMATCH')
    if not isinstance(c.get('collision_domain'), str) or not c.get('collision_domain'):
        errors.append('COLLISION_DOMAIN_MISSING')
    for k in RESOURCE_KEYS:
        v = c.get('resources', {}).get(k) if isinstance(c.get('resources'), dict) else None
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            errors.append('BAD_RESOURCE_' + k)
    for k in ('benefit_points', 'confidence_pct', 'baseline_human_minutes', 'unattended_minutes', 'risk_points'):
        v = c.get(k)
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            errors.append('BAD_ESTIMATE_' + k)
    if isinstance(c.get('confidence_pct'), int) and c['confidence_pct'] > 100:
        errors.append('CONFIDENCE_OVER_100')
    if isinstance(c.get('resources'), dict) and isinstance(c.get('baseline_human_minutes'), int):
        human = c['resources'].get('human_minutes')
        if isinstance(human, int) and human > c['baseline_human_minutes']:
            errors.append('NEGATIVE_HUMAN_RELIEF')
    return sorted(set(errors))


def qualified(candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    seen = set()
    ok, held = [], []
    for c in candidates:
        errors = validate_candidate(c)
        ident = c.get('work_id') if isinstance(c, dict) else None
        if ident in seen:
            errors.append('DUPLICATE_WORK_ID')
        seen.add(ident)
        if errors:
            held.append({'work_id': ident, 'reasons': sorted(set(errors))})
        else:
            ok.append(c)
    return ok, held


def feasible(selected: list[dict], budget: dict) -> bool:
    if any(k not in budget or isinstance(budget[k], bool) or not isinstance(budget[k], int) or budget[k] < 0 for k in RESOURCE_KEYS):
        raise ValueError('Invalid or incomplete budget')
    if len({c['collision_domain'] for c in selected}) != len(selected):
        return False
    return all(sum(c['resources'][k] for c in selected) <= budget[k] for k in RESOURCE_KEYS)


def value(c: dict) -> int:
    return c['benefit_points'] * c['confidence_pct'] - 100 * c['risk_points']


def plan(candidates: list[dict], budget: dict, policy: str = 'frontier') -> dict:
    good, held = qualified(candidates)
    if len(good) > 16:
        raise ValueError('Fixture exceeds bounded exhaustive search (16)')
    feasible([], budget)  # fail closed even when all candidates held
    if policy == 'first_fit':
        chosen = []
        for c in good:
            if feasible(chosen + [c], budget):
                chosen.append(c)
    elif policy == 'frontier':
        possibilities = (list(combo) for n in range(len(good) + 1) for combo in itertools.combinations(good, n))
        chosen = max((p for p in possibilities if feasible(p, budget)),
                     key=lambda p: (sum(value(c) for c in p),
                                    sum(c['baseline_human_minutes'] - c['resources']['human_minutes'] for c in p),
                                    -sum(c['resources']['human_minutes'] for c in p),
                                    -sum(c['resources']['cash_cents'] for c in p),
                                    tuple(sorted(c['work_id'] for c in p))))
    else:
        raise ValueError('Unknown selection policy')
    used = {k: sum(c['resources'][k] for c in chosen) for k in RESOURCE_KEYS}
    selected_ids = {c['work_id'] for c in chosen}
    deferred = sorted(c['work_id'] for c in good if c['work_id'] not in selected_ids)
    result = {
        'schema': 'CoAll.CoIngestScarcityAutonomyFixture.R0',
        'execution': 'SIMULATION_ONLY_NO_EFFECTS',
        'policy': policy,
        'candidate_count': len(candidates),
        'qualified_count': len(good),
        'selected': sorted(selected_ids),
        'deferred_qualified_options': deferred,
        'option_lifecycle': 'QUALIFIED_NOT_SELECTED_IS_DORMANT_NOT_ERASED',
        'materialized_executor_count': 0,
        'held': sorted(held, key=lambda x: str(x['work_id'])),
        'budget': {k: budget[k] for k in RESOURCE_KEYS},
        'used': used,
        'remaining_budget': {k: budget[k] - used[k] for k in RESOURCE_KEYS},
        'projected_utility_score_pctpoints': sum(value(c) for c in chosen),
        'projected_human_minutes_avoided': sum(c['baseline_human_minutes'] - c['resources']['human_minutes'] for c in chosen),
        'projected_unattended_minutes': sum(c['unattended_minutes'] for c in chosen if c['resources']['human_minutes'] == 0),
        'human_free_candidate_count': sum(c['resources']['human_minutes'] == 0 for c in chosen),
        'external_actions': 0,
        'financial_actions': 0,
        'actual_human_minutes_saved': 'NOT_MEASURED',
        'actual_unattended_duration': 'NOT_MEASURED',
        'actual_beneficiary_value': 'NOT_MEASURED',
        'independent_receiver_ack': 'NOT_OBSERVED',
        'nonclaims': ['NO_AUTONOMOUS_SPEND_OR_INVESTMENT', 'SYNTHETIC_SCORE_NE_REAL_VALUE',
                      'ZERO_PLANNED_HUMAN_NE_UNATTENDED_RUNTIME', 'SOURCE_HASH_NE_TRUTH',
                      'POLICY_SELECTION_NE_EXECUTION', 'MANY_TASKS_NE_INDEPENDENT_WORKERS',
                      'DORMANT_OPTION_NE_ACTIVE_PROCESS', 'OPEN_OPTION_SPACE_NE_INFINITE_THROUGHPUT'],
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--fixture', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ns = ap.parse_args()
    payload = json.loads(ns.fixture.read_text('utf-8'))
    obj = {
        'fixture_sha256': hashlib.sha256(ns.fixture.read_bytes()).hexdigest(),
        'comparison': {
            'first_fit': plan(payload['candidates'], payload['budget'], 'first_fit'),
            'frontier': plan(payload['candidates'], payload['budget'], 'frontier'),
        }
    }
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    if ns.output.exists():
        raise SystemExit('HOLD: output exists; no clobber')
    ns.output.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', 'utf-8')
    print(json.dumps(obj, sort_keys=True))

if __name__ == '__main__':
    main()
