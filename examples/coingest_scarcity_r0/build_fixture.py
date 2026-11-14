"""Synthetic, reproducible fixture generator: not part of external runtime."""
import hashlib
import json
from pathlib import Path

base = {'authority': 'READ_ONLY_SIMULATION', 'effect': 'NONE', 'requires_human_gate': False,
        'privacy': 'PUBLIC_SYNTHETIC', 'reversible': True, 'proof_plan': 'DETERMINISTIC_FIXTURE',
        'evidence_class': 'SYNTHETIC_BENCHMARK'}

def case(name, benefit, confidence, human, baseline, unattended, cpu, review, energy, money, slots, risk, collision=None, **overrides):
    evidence = f'Public-synthetic planning option: {name}; no external source or outcome'
    item = dict(base, work_id=name, collision_domain=collision or name,
                evidence_text=evidence, source_sha256=hashlib.sha256(evidence.encode()).hexdigest(),
                benefit_points=benefit, confidence_pct=confidence, baseline_human_minutes=baseline,
                unattended_minutes=unattended, risk_points=risk,
                resources={'cpu_units':cpu, 'energy_units':energy, 'reviewer_minutes':review,
                           'human_minutes':human, 'cash_cents':money, 'worker_slots':slots})
    item.update(overrides)
    return item

cases = [
    case('duplicated_summaries', 3, 90, 0, 3, 20, 4, 3, 2, 0, 1, 1),
    case('fresh_source_retrieval', 18, 85, 0, 28, 45, 4, 4, 2, 0, 1, 2),
    case('independent_receipt_recovery', 22, 92, 0, 35, 50, 5, 5, 2, 0, 1, 2),
    case('synthetic_counterexample_search', 15, 90, 0, 20, 40, 4, 3, 1, 0, 1, 1),
    case('baseline_comprehension_projection', 12, 75, 0, 18, 35, 3, 4, 2, 0, 1, 1),
    case('alternate_same_graph_replay', 14, 88, 0, 22, 38, 4, 4, 1, 0, 1, 1,
         collision='independent_receipt_recovery'),
    case('external_outreach_send', 48, 95, 0, 60, 50, 1, 1, 1, 0, 1, 1,
         effect='PUBLIC_MESSAGE', requires_human_gate=True),
    case('real_money_investment', 200, 99, 0, 100, 5, 1, 1, 1, 300000, 1, 1,
         effect='FINANCIAL_TRANSFER', requires_human_gate=True),
    case('private_document_intake', 26, 90, 0, 25, 40, 2, 2, 1, 0, 1, 2,
         privacy='PRIVATE_UNCONSENTED'),
    case('unknown_provenance_claim', 80, 95, 0, 20, 25, 1, 1, 1, 0, 1, 1,
         source_sha256='invalid'),
]
payload={'schema':'CoAll.CoIngestSyntheticFixture.R0',
         'budget': {'cpu_units':14,'energy_units':8,'reviewer_minutes':13,
                    'human_minutes':0,'cash_cents':0,'worker_slots':3},
         'candidates':cases}
Path(__file__).with_name('fixture.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n',encoding='utf-8')
