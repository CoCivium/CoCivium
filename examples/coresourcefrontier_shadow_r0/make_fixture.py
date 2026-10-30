#!/usr/bin/env python3
"""Generate deterministic synthetic research fixture, no real device or energy telemetry."""
import hashlib
import json
from pathlib import Path


def task(id, key, cap='verify', kind='INFORMATIONAL', value=4, evidence=1, novelty=1, challenge=1,
         keyword=1, cpu=2, energy=2, attention=0, **changes):
    rec = {'id': id, 'semantic_key': key, 'namespace': 'cocivium.synthetic.r0',
           'source_sha256': hashlib.sha256((key + ':v1').encode()).hexdigest(), 'revision': 'v1',
           'receiver': 'demo_reader', 'tenant': 'synthetic', 'privacy': 'PUBLIC',
           'provenance': 'SYNTHETIC_FIXTURE', 'consent': True, 'authorized': True, 'current': True,
           'material_wake': True, 'effect': 'SHADOW_READ', 'capability': cap, 'kind': kind,
           'receiver_value_proxy': value, 'evidence': evidence, 'novelty': novelty,
           'challenge': challenge, 'keyword': keyword,
           'cost': {'cpu_units': cpu, 'energy_estimate_units': energy, 'attention_units': attention}}
    rec.update(changes)
    return rec

fixture = {
 'schema': 'CoResourceFrontier.SyntheticFixture.R0', 'receiver': 'demo_reader', 'max_wave': 3,
 'note': 'All nodes, units, recipients, qualities and evidence scores are synthetic. No X1/X2 state is measured.',
 'resources': [
  {'id': 'candidate_A', 'tenant': 'synthetic', 'available': True,
   'capabilities': ['verify', 'challenge', 'compare'], 'clearances': ['PUBLIC'],
   'capacity': {'cpu_units': 12, 'energy_estimate_units': 20, 'attention_units': 3},
   'reserve': {'cpu_units': 4, 'energy_estimate_units': 8, 'attention_units': 1}},
  {'id': 'candidate_B', 'tenant': 'synthetic', 'available': True,
   'capabilities': ['verify', 'challenge', 'compare'], 'clearances': ['PUBLIC'],
   'capacity': {'cpu_units': 9, 'energy_estimate_units': 14, 'attention_units': 1},
   'reserve': {'cpu_units': 3, 'energy_estimate_units': 5, 'attention_units': 0}},
  {'id': 'unavailable_candidate_C', 'tenant': 'synthetic', 'available': False,
   'capabilities': ['verify', 'challenge', 'compare'], 'clearances': ['PUBLIC'],
   'capacity': {'cpu_units': 50, 'energy_estimate_units': 50, 'attention_units': 50},
   'reserve': {'cpu_units': 5, 'energy_estimate_units': 5, 'attention_units': 5}}
 ],
 'tasks': [
  task('A', 'evidence_review', value=10, evidence=5, novelty=1, challenge=1, keyword=3, cpu=4, energy=4, attention=1),
  task('B', 'evidence_review', value=10, evidence=5, novelty=1, challenge=1, keyword=3, cpu=4, energy=4, attention=1),
  task('C', 'counterexample', cap='challenge', value=9, evidence=3, novelty=4, challenge=5, cpu=3, energy=3, attention=1),
  task('D', 'interstice_symbolic', cap='compare', kind='SYMBOLIC', value=6, evidence=1, novelty=5, challenge=2, keyword=5),
  task('E', 'reusable_summary', value=8, evidence=4, novelty=1, challenge=1, keyword=4, cpu=2, energy=2),
  task('F', 'no_permission', consent=False, value=100, evidence=5),
  task('G', 'cold_outreach', effect='EXTERNAL_EMAIL', value=100, evidence=5),
  task('H', 'planck_power_claim', kind='PHYSICAL_ENERGY_HARVEST', value=100, evidence=5),
  task('I', 'no_receiver', receiver='different_receiver', value=100, evidence=5),
  task('J', 'cold_dormant', material_wake=False, value=100, evidence=5),
  task('K', 'costly_experiment', cpu=50, energy=50, attention=5, value=100, evidence=5),
  task('L', 'stale_source', current=False, value=100, evidence=5),
  task('M', 'conceptual_question', cap='compare', kind='SPECULATIVE', value=3, evidence=1, novelty=4, challenge=3),
  task('N', 'cached_proof_reuse', value=8, evidence=5, novelty=1, challenge=1, cpu=1, energy=1),
  task('O', 'wrong_tenant', tenant='another_organization', value=100, evidence=5),
  task('P', 'private_receipt', privacy='PRIVATE', value=100, evidence=5),
  task('Q', 'missing_source', source_sha256='', value=100, evidence=5)
 ],
 'subscribers': [
  {'id': 'a_public', 'opt_in': True, 'topics': ['frontier'], 'clearances': ['PUBLIC'], 'permissions': ['VIEW']},
  {'id': 'b_public', 'opt_in': True, 'topics': ['frontier'], 'clearances': ['PUBLIC'], 'permissions': ['VIEW']},
  {'id': 'c_public', 'opt_in': True, 'topics': ['frontier'], 'clearances': ['PUBLIC'], 'permissions': ['VIEW']},
  {'id': 'd_refusal', 'opt_in': False, 'topics': ['frontier'], 'clearances': ['PUBLIC'], 'permissions': ['VIEW']},
  {'id': 'e_other', 'opt_in': True, 'topics': ['unrelated'], 'clearances': ['PUBLIC'], 'permissions': ['VIEW']}
 ]
}
Path(__file__).with_name('fixture.json').write_text(json.dumps(fixture, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print('synthetic fixture created', len(fixture['tasks']), 'tasks', len(fixture['resources']), 'candidate resources')
