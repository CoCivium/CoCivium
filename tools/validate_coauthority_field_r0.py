#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path

P=Path('fixtures/governance/coauthority_field_r0.json')

def fail(code): raise SystemExit(code)
def blob(path): return subprocess.check_output(['git','rev-parse',f'HEAD:{path}'], text=True).strip()
def csha(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()

def main():
    d=json.loads(P.read_text(encoding='utf-8'))
    s=d['source_bindings']
    if blob(s['service_principal_policy_path']) != s['service_principal_policy_blob_sha']: fail('FAIL_SERVICE_PRINCIPAL_SOURCE_BIND')
    if blob(s['coterms_path']) != s['coterms_blob_sha']: fail('FAIL_COTERMS_SOURCE_BIND')
    m=d['operational_model']
    if m['universal_operational_boss'] is not None: fail('FAIL_UNIVERSAL_OPERATIONAL_BOSS')
    if m['effective_authority_operator'] != 'INTERSECTION_OF_REQUIRED_CEILINGS': fail('FAIL_AUTHORITY_OPERATOR')
    if m['conflict_default'] != 'HOLD_UNLESS_PREDECLARED_RESOLUTION_EXISTS': fail('FAIL_CONFLICT_DEFAULT')
    refs=d['transcendent_references']
    if any(r['executable_principal'] is not False for r in refs): fail('FAIL_TRANSCENDENT_EXECUTABLE_PRINCIPAL')
    labels=[r['label'] for r in refs]
    if len(labels) != len(set(labels)): fail('FAIL_REFERENCE_LABEL_DUPLICATE')
    cases={c['id']:c for c in d['cases']}
    expected={
      'A01_SCOPED_READ_ALLOWED':'ALLOW_SCOPED_EFFECT',
      'A02_SCOPE_DOES_NOT_WIDEN':'HOLD_EFFECT_OUTSIDE_SCOPE',
      'A03_REPRESENTATION_NO_AMPLIFICATION':'HOLD_REPRESENTATION_NE_AUTHORITY',
      'A04_DELEGATION_CHAIN_INTERSECTION':'ALLOW_INTERSECTION_READ',
      'A05_DELEGATION_CHAIN_NO_UNION':'HOLD_NOT_IN_CHAIN_INTERSECTION',
      'A06_CYCLE_NO_AMPLIFICATION':'HOLD_CYCLE_CANNOT_CREATE_WRITE',
      'A07_FUTURE_AUTHORITY_NOT_CURRENT':'HOLD_FUTURE_NE_CURRENT_AUTHORITY',
      'A08_TRANSCENDENT_REFERENCE_NO_CREDENTIAL':'HOLD_TRANSCENDENT_REFERENCE_NE_EXECUTABLE_AUTHORITY',
      'A09_CMA_UNBOUND_NO_CREDENTIAL':'HOLD_UNBOUND_REFERENCE_NE_AUTHORITY',
      'A10_CONFLICT_WITHOUT_RESOLUTION_HOLDS':'HOLD_UNRESOLVED_AUTHORITY_CONFLICT',
      'A11_SIMULATION_COMMANDER_ONLY_SIMULATION':'HOLD_SIMULATION_NE_REAL_AUTHORITY',
      'A12_RESOURCE_SIZE_NO_GOVERNANCE':'NO_GOVERNANCE_POWER_FROM_RESOURCE_SIZE'
    }
    if set(cases)!=set(expected): fail('FAIL_CASE_SET')
    for k,v in expected.items():
        if cases[k]['expected'] != v: fail('FAIL_CASE_EXPECTATION:'+k)
    c4=cases['A04_DELEGATION_CHAIN_INTERSECTION']
    inter=set(c4['effects_a_to_b']) & set(c4['effects_b_to_c'])
    if c4['request_effect'] not in inter: fail('FAIL_INTERSECTION_READ')
    c5=cases['A05_DELEGATION_CHAIN_NO_UNION']
    inter2=set(c5['effects_a_to_b']) & set(c5['effects_b_to_c'])
    if c5['request_effect'] in inter2: fail('FAIL_DELEGATION_UNION_LEAK')
    c6=cases['A06_CYCLE_NO_AMPLIFICATION']
    if c6['cycle_claimed_effect'] in set(c6['original_effects']): fail('FAIL_CYCLE_FIXTURE')
    if cases['A12_RESOURCE_SIZE_NO_GOVERNANCE']['derived_governance_weight'] != 0: fail('FAIL_RESOURCE_GOVERNANCE')
    head=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    print(json.dumps({
      'STATE':'PASS_COAUTHORITY_FIELD_R0',
      'checked_out_head_sha':head,
      'case_count':len(cases),
      'universal_operational_boss':None,
      'transcendent_reference_count':len(refs),
      'executable_transcendent_principal_count':0,
      'future_projection_grants_current_authority':False,
      'authority_cycle_amplifies_authority':False,
      'runtime_authority_changed':False,
      'fixture_semantic_sha256':csha(d)
    },separators=(',',':')))

if __name__=='__main__': main()
