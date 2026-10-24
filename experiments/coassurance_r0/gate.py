#!/usr/bin/env python3
"""CoAssurance R0: declared-evidence stage gate, never an independent auditor."""
import copy
import json
import re
import sys
from pathlib import Path

STAGES = ('DISCOVER', 'DESIGN', 'BUILD', 'REVIEW', 'PUBLIC_PREVIEW', 'OPERATE', 'RECOVER', 'RETIRE')
RISKS = ('LOW', 'MEDIUM', 'HIGH')
REVIEW_ROLES = ('PROPOSER', 'FORMAL_VERIFIER', 'OBSERVER', 'CHALLENGER',
                'PERSPECTIVE', 'PROVENANCE', 'SYNTHESIS', 'HUMAN_DOMAIN')
HASH = re.compile(r'^[0-9a-f]{64}$')


def valid_ref(ref):
    return isinstance(ref, str) and len(ref.strip()) > 8


def evaluate(raw):
    """Fail malformed claims; hold insufficient evidence; never certify a receiver."""
    fail, hold = [], []
    if not isinstance(raw, dict):
        return {'status': 'FAIL', 'fail': ['NOT_OBJECT'], 'hold': [], 'effects': 0}
    x = copy.deepcopy(raw)
    stage = x.get('stage')
    risk = x.get('risk')
    if stage not in STAGES:
        fail.append('INVALID_STAGE')
    if risk not in RISKS:
        fail.append('INVALID_RISK')
    if x.get('authority_ceiling') not in ('NONE', 'READ_ONLY', 'HUMAN_GATE', 'EFFECT_GATED'):
        fail.append('INVALID_AUTHORITY_CEILING')
    if not valid_ref(x.get('work_id')) or not valid_ref(x.get('source_ref')) or not HASH.fullmatch(str(x.get('source_sha256', ''))):
        fail.append('EXACT_SOURCE_IDENTITY_REQUIRED')
    if x.get('receiver_ack') is True and not x.get('receiver_proof'):
        fail.append('ACK_WITHOUT_RECEIVER_PROOF')
    if x.get('real_effects_executed', 0) != 0:
        fail.append('READ_ONLY_CANARY_EFFECT_LIMIT')
    if x.get('review_state') == 'APPROVED' and not x.get('independent_acceptance'):
        fail.append('APPROVED_WITHOUT_ACCEPTANCE')
    limits = x.get('turtle_budget')
    if not isinstance(limits, dict) or any(type(limits.get(k)) is not int for k in ('max_depth', 'max_rounds', 'max_active_workers', 'max_total_evaluations')):
        fail.append('TURTLE_BUDGET_MISSING')
    elif not (0 <= limits['max_depth'] <= 2 and 0 <= limits['max_rounds'] <= 2 and
              0 <= limits['max_active_workers'] <= 8 and 1 <= limits['max_total_evaluations'] <= 128):
        fail.append('TURTLE_BUDGET_UNBOUNDED')
    priors = x.get('priors')
    if not isinstance(priors, list) or not priors:
        hold.append('PRIOR_EVIDENCE_UNBOUND')
    elif any(not isinstance(p, dict) or p.get('kind') not in ('HISTORICAL', 'BASELINE', 'PRIOR_ART', 'REFERENCE_CLASS') or
             not valid_ref(p.get('source_ref')) or not isinstance(p.get('assumption'), str) or not p['assumption'] for p in priors):
        fail.append('MALFORMED_PRIOR')
    if not isinstance(x.get('falsifier'), str) or not x.get('falsifier'):
        hold.append('FALSIFIER_NOT_DECLARED')
    panel = x.get('panel')
    if not isinstance(panel, list) or not panel:
        hold.append('NO_REVIEW_CONTRIBUTIONS')
        panel = []
    ids = set()
    for member in panel:
        if not isinstance(member, dict) or member.get('role') not in REVIEW_ROLES or not valid_ref(member.get('reviewer_id')) or not valid_ref(member.get('evidence_ref')) or member.get('verdict') not in ('SUPPORT', 'DISSENT', 'HOLD'):
            fail.append('MALFORMED_PANEL_CONTRIBUTION')
            continue
        if member['reviewer_id'] in ids:
            fail.append('DUPLICATE_REVIEWER_ID')
        ids.add(member['reviewer_id'])
    roles = {p.get('role') for p in panel if isinstance(p, dict)}
    if 'CHALLENGER' not in roles:
        hold.append('MISSING_CHALLENGER')
    if risk in ('MEDIUM', 'HIGH') and 'PROVENANCE' not in roles:
        hold.append('MISSING_PROVENANCE_REVIEW')
    if risk == 'HIGH':
        human_domain = [p for p in panel if isinstance(p, dict) and p.get('role') == 'HUMAN_DOMAIN']
        if not human_domain:
            hold.append('HIGH_RISK_DOMAIN_REVIEW_REQUIRED')
        # Identity strings are declarations, not independent-party authentication.
        if len({p.get('reviewer_id') for p in panel if isinstance(p, dict)}) < 3:
            hold.append('HIGH_RISK_PANEL_DIVERSITY_REQUIRED')
        if not x.get('independent_acceptance'):
            hold.append('HIGH_RISK_INDEPENDENT_ACCEPTANCE_REQUIRED')
    tests = x.get('tests')
    if not isinstance(tests, list) or not tests:
        hold.append('TEST_PLAN_MISSING')
        tests = []
    for t in tests:
        if not isinstance(t, dict) or not valid_ref(t.get('test_id')) or t.get('status') not in ('PASS', 'FAIL', 'HOLD', 'NOT_RUN'):
            fail.append('MALFORMED_TEST')
    if any(t.get('status') == 'FAIL' for t in tests if isinstance(t, dict)):
        hold.append('OBSERVED_TEST_FAILURE')
    if stage in ('REVIEW', 'PUBLIC_PREVIEW', 'OPERATE', 'RECOVER', 'RETIRE'):
        if not any(t.get('status') == 'PASS' and valid_ref(t.get('receipt_ref')) for t in tests if isinstance(t, dict)):
            hold.append('STAGE_REQUIRES_TEST_RECEIPT')
        if not x.get('rollback_ref'):
            hold.append('ROLLBACK_OR_EXIT_NOT_RECORDED')
    if stage in ('PUBLIC_PREVIEW', 'OPERATE', 'RECOVER', 'RETIRE'):
        if not valid_ref(x.get('security_privacy_review_ref')):
            hold.append('SECURITY_PRIVACY_REVIEW_NOT_BOUND')
    if stage in ('OPERATE', 'RECOVER', 'RETIRE'):
        if not x.get('receiver_ack') or not valid_ref(x.get('receiver_proof')):
            hold.append('INDEPENDENT_RECEIVER_READPROOF_REQUIRED')
        if not valid_ref(x.get('external_user_outcome_ref')):
            hold.append('RECEIVER_OUTCOME_NOT_BOUND')
    status = 'FAIL' if fail else 'HOLD' if hold else 'PASS_DECLARED_STRUCTURE_ONLY'
    return {'status': status, 'fail': sorted(set(fail)), 'hold': sorted(set(hold)),
            'effects': 0, 'scope': 'DECLARED_STRUCTURE_NOT_SOURCE_AUTHENTICATION_OR_EXTERNAL_ACCEPTANCE'}


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python gate.py <record.json>')
    try:
        record = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as err:
        raise SystemExit('FAIL_CLOSED_INPUT: ' + str(err))
    result = evaluate(record)
    print(json.dumps(result, sort_keys=True, indent=2))
    raise SystemExit(2 if result['status'] == 'FAIL' else 1 if result['status'] == 'HOLD' else 0)


if __name__ == '__main__':
    main()