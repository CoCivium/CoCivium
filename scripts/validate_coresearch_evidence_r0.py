#!/usr/bin/env python3
"""Validate declared research evidence, not source truth or runtime adoption."""
import argparse
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def refs(value):
    return isinstance(value, list) and bool(value) and all(text(x) for x in value)


def validate_recovery(r):
    need(isinstance(r, dict), 'RECOVERY_OBJECT')
    required = {'sources_read', 'finding', 'basis', 'scope', 'resource_options', 'continuation'}
    need(required <= r.keys(), 'RECOVERY_FIELDS')
    sources = r['sources_read']
    need(isinstance(sources, list) and bool(sources), 'RECOVERY_NO_READ_SOURCES')
    for s in sources:
        need(isinstance(s, dict) and all(text(s.get(k)) for k in ('ref', 'version', 'observed_at')), 'RECOVERY_SOURCE_BINDING')
    need(r['finding'] in ('PRESENT', 'UNRESOLVED', 'SCOPED_ABSENCE'), 'RECOVERY_FINDING')
    need(r['basis'] in ('SOURCE_READ', 'SEARCH_ONLY', 'OBSERVER_UNAVAILABLE', 'AUTHORITATIVE_BOUNDED_INVENTORY'), 'RECOVERY_BASIS')
    need(text(r['scope']), 'RECOVERY_SCOPE')
    if r['finding'] == 'SCOPED_ABSENCE':
        need(r['basis'] == 'AUTHORITATIVE_BOUNDED_INVENTORY', 'ABSENCE_REQUIRES_INVENTORY')
        inventory = r.get('inventory', {})
        need(isinstance(inventory, dict) and all(text(inventory.get(k)) for k in ('ref', 'version', 'observed_at', 'coverage')), 'ABSENCE_INVENTORY_BINDING')
        need(any(all(inventory[k] == source[k] for k in ('ref', 'version', 'observed_at')) for source in sources), 'ABSENCE_INVENTORY_NOT_READ')
    options = r['resource_options']
    need(isinstance(options, list) and bool(options), 'RESOURCE_OPTIONS')
    for option in options:
        need(isinstance(option, dict) and all(text(option.get(k)) for k in ('id', 'reason', 'cost_or_unknown')), 'RESOURCE_REASON_AND_COST')
        need(option.get('inspection') in ('INSPECTED', 'LISTED', 'UNAVAILABLE'), 'RESOURCE_INSPECTION')
        need(option.get('disposition') in ('SELECTED', 'DEFERRED', 'UNAVAILABLE'), 'RESOURCE_DISPOSITION')
        if option['disposition'] == 'SELECTED':
            need(option['inspection'] == 'INSPECTED', 'SELECTED_RESOURCE_NOT_INSPECTED')
    need(any(o['id'] == 'REUSE_EXISTING' for o in options), 'RESOURCE_REUSE_OPTION')
    need(any(o['disposition'] == 'SELECTED' for o in options), 'RESOURCE_NO_SELECTION')
    c = r['continuation']
    need(isinstance(c, dict) and all(text(c.get(k)) for k in ('next_deed', 'wake_condition')), 'CONTINUATION_FIELDS')
    need(c.get('state') in ('RECORDED', 'WRITEBACK_UNAVAILABLE'), 'CONTINUATION_STATE')
    if c['state'] == 'RECORDED':
        need(all(text(c.get(k)) for k in ('result_ref', 'version')), 'CONTINUATION_EXACT_POINTER')
    else:
        need(text(c.get('reason')), 'CONTINUATION_UNAVAILABLE_REASON')


def validate_extraordinary(g):
    need(isinstance(g, dict) and g.get('disposition') in ('CANDIDATE', 'PROMOTION_REQUESTED'), 'EXTRAORDINARY_DISPOSITION')
    need(text(g.get('domain')), 'EXTRAORDINARY_DOMAIN')
    if g['disposition'] == 'CANDIDATE':
        need(refs(g.get('missing_verification')), 'EXTRAORDINARY_CANDIDATE_GAPS')
        return
    checks = ('primary_observations', 'independent_corroboration', 'prior_art_review', 'adversarial_review', 'replication', 'prospective_falsifiers', 'domain_verification')
    for name in checks:
        item = g.get(name, {})
        need(isinstance(item, dict) and item.get('state') == 'PASS' and refs(item.get('source_refs')) and text(item.get('observed_at')), 'EXTRAORDINARY_CHECK_' + name.upper())
    need(text(g['domain_verification'].get('verifier')), 'EXTRAORDINARY_VERIFIER')
    need(refs(g.get('receipts')) and text(g.get('uncertainty')), 'EXTRAORDINARY_RECEIPTS_AND_UNCERTAINTY')


def validate(d, require_recovery=False, require_extraordinary=False):
    need(isinstance(d, dict), 'RECORD_OBJECT')
    required = ['schema', 'record_id', 'observed_at', 'epistemic_class', 'claim', 'source_refs', 'tests', 'confidence', 'authority_ceiling', 'confidentiality', 'nonclaims']
    for k in required:
        need(k in d, 'MISSING_' + k.upper())
    need(d['schema'] == 'CoAll.ResearchEvidence.v0.1-candidate', 'SCHEMA_ID')
    need(not isinstance(d['confidence'], bool) and isinstance(d['confidence'], (int, float)) and 0 <= d['confidence'] <= 1, 'CONFIDENCE_RANGE')
    need(refs(d['source_refs']), 'NO_SOURCE_REFS')
    need(refs(d['nonclaims']), 'NO_NONCLAIMS')
    need(isinstance(d['tests'], list) and all(isinstance(t, dict) for t in d['tests']), 'TESTS_ARRAY')
    if d['epistemic_class'] in {'HYPOTHESIS', 'PREDICTED', 'COUNTERFACTUAL'}:
        need('HYPOTHESIS_NE_FACT' in d['nonclaims'] or 'PREDICTION_NE_FUTURE_FACT' in d['nonclaims'], 'MISSING_EPISTEMIC_BOUNDARY')
    if any(t.get('state') == 'PASS' for t in d['tests']):
        need('CI_PASS_NE_REAL_WORLD_PROOF' in d['nonclaims'], 'MISSING_CI_NONCLAIM')
    need(not require_recovery or 'research_recovery' in d, 'RECOVERY_REQUIRED')
    if 'research_recovery' in d:
        validate_recovery(d['research_recovery'])
    need(not require_extraordinary or 'extraordinary_gate' in d, 'EXTRAORDINARY_GATE_REQUIRED')
    if 'extraordinary_gate' in d:
        validate_extraordinary(d['extraordinary_gate'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', nargs='?', default='examples/coresearch-evidence-v0.1.example.json')
    parser.add_argument('--require-recovery', action='store_true', help='Reject legacy records without a research readback.')
    parser.add_argument('--require-extraordinary-gate', action='store_true', help='Require explicit extraordinary-claim disposition and evidence.')
    args = parser.parse_args()
    try:
        d = json.loads(Path(args.record).read_text(encoding='utf-8'))
        validate(d, args.require_recovery, args.require_extraordinary_gate)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        raise SystemExit('FAIL_CLOSED__' + str(exc))
    print('PASS_BOUNDED_RESEARCH_EVIDENCE_CONTRACT')
    print('record_id=' + str(d['record_id']))
    print('epistemic_class=' + str(d['epistemic_class']))
    print('tests=' + str(len(d['tests'])))
    print('source_refs=' + str(len(d['source_refs'])))
    print('boundary=DECLARED_EVIDENCE_ONLY__NOT_INDEPENDENT_VERIFICATION_OR_ADOPTION')


if __name__ == '__main__':
    main()
