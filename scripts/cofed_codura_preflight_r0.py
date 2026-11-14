#!/usr/bin/env python3
"""Read-only CoFed+/CoDura+ article placement evidence gate (R0 candidate).

Structural proof preflight, NOT a trust anchor or proof that a remote receiver exists.
No network, storage writes, publishing effects, or changes to source objects.
Usage: python3 cofed_codura_preflight_r0.py packet.json --source edition.md
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = 'CoAll.CoFedCoDura.PlacementEvidence.R0'
AXES = ('provider', 'account', 'site', 'power', 'credential_domain', 'key_custodian', 'operator')
HEX64 = re.compile(r'^[0-9a-f]{64}$')
CLASSES = ('PUBLIC_SAFE', 'PRIVATE', 'RESTRICTED', 'UNKNOWN')


def is_digest(v):
    return isinstance(v, str) and bool(HEX64.fullmatch(v))


def good_text(v):
    return isinstance(v, str) and bool(v.strip()) and v.strip().lower() not in ('unknown', 'none', 'null', 'tbd', 'unverified')


def has_fields(record, fields):
    return isinstance(record, dict) and all(good_text(record.get(k)) for k in fields)


def independence(a, b):
    """Conservative common-mode screen, not certification of physical independence."""
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    if not has_fields(a, AXES) or not has_fields(b, AXES):
        return False
    return all(a[k].strip().casefold() != b[k].strip().casefold() for k in AXES)


def review(packet, source_bytes=None):
    failures = []
    def hold(code, condition):
        if not condition and code not in failures:
            failures.append(code)

    if not isinstance(packet, dict):
        packet = {}
    hold('HOLD_SCHEMA', packet.get('schema') == SCHEMA)
    hold('HOLD_IDENTITY', has_fields(packet, ('work_id', 'edition_id')))
    cls = packet.get('classification')
    hold('HOLD_CLASSIFICATION', cls in CLASSES and cls != 'UNKNOWN')
    source = packet.get('source')
    source = source if isinstance(source, dict) else {}
    digest = source.get('sha256')
    hold('HOLD_SOURCE_IDENTITY', is_digest(digest) and has_fields(source, ('provenance_ref',)))
    hold('HOLD_SOURCE_BYTES_UNCHECKED', isinstance(source_bytes, bytes))
    if isinstance(source_bytes, bytes):
        hold('HOLD_SOURCE_HASH_MISMATCH', is_digest(digest) and hashlib.sha256(source_bytes).hexdigest() == digest)
    rights = packet.get('rights')
    rights = rights if isinstance(rights, dict) else {}
    hold('HOLD_RIGHTS', has_fields(rights, ('rightsholder', 'license', 'scope', 'review_ref')) and rights.get('review_state') == 'APPROVED' and rights.get('third_party_cleared') is True)
    hold('HOLD_PRIVACY', rights.get('privacy_approved') is True)
    # Rights to retain a private source are not an automatic license to publish.
    if cls == 'PUBLIC_SAFE':
        hold('HOLD_PUBLIC_RIGHTS', rights.get('public_distribution_allowed') is True)

    assets = packet.get('assets')
    hold('HOLD_ASSET_MANIFEST', isinstance(assets, list) and all(isinstance(x, dict) and has_fields(x, ('id',)) and is_digest(x.get('sha256')) for x in (assets if isinstance(assets, list) else [])))
    if isinstance(assets, list):
        hold('HOLD_DUPLICATE_ASSET_IDS', all(isinstance(x.get('id'), str) for x in assets if isinstance(x, dict)) and len([x.get('id') for x in assets if isinstance(x, dict)]) == len({x.get('id') for x in assets if isinstance(x, dict) and isinstance(x.get('id'), str)}))

    copies = packet.get('custody')
    copies = copies if isinstance(copies, list) else []
    hold('HOLD_COPIES', len(copies) >= 2 and all(isinstance(x, dict) for x in copies))
    copies = [x for x in copies if isinstance(x, dict)]
    ids = [x.get('copy_id') for x in copies]
    hold('HOLD_COPY_IDENTITIES', all(good_text(x) for x in ids) and len(ids) == len({x for x in ids if isinstance(x, str)}))
    origin_copy_id = packet.get('source_origin_copy_id')
    hold('HOLD_ORIGIN_COPY_ID', good_text(origin_copy_id) and origin_copy_id in ids)
    for c in copies:
        hold('HOLD_COPY_READBACK', is_digest(digest) and c.get('sha256') == digest and c.get('exact_readback') is True and has_fields(c, ('copy_id', 'receipt_ref', 'readback_actor')))
    paired = []
    for i, a in enumerate(copies):
        for b in copies[i + 1:]:
            if independence(a.get('failure_domain'), b.get('failure_domain')):
                paired.append((a, b))
    hold('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', bool(paired))

    restore = packet.get('restore')
    restore = restore if isinstance(restore, dict) else {}
    hold('HOLD_COLD_RESTORE', restore.get('cold_test') is True and restore.get('origin_device_unavailable') is True and restore.get('origin_provider_unavailable') is True and restore.get('key_recovery_independent') is True)
    hold('HOLD_RESTORED_EDITION', is_digest(digest) and restore.get('work_id') == packet.get('work_id') and restore.get('edition_id') == packet.get('edition_id') and restore.get('sha256') == digest)
    expected_assets = {x['id']: x.get('sha256') for x in assets if isinstance(x, dict) and isinstance(x.get('id'), str)} if isinstance(assets, list) else None
    hold('HOLD_RESTORED_ASSETS', expected_assets is not None and restore.get('restored_assets') == expected_assets)
    hold('HOLD_RESTORED_RIGHTS_METADATA', restore.get('rights_metadata_restored') is True and restore.get('lineage_restored') is True)
    receiver = restore.get('receiver')
    receiver = receiver if isinstance(receiver, dict) else {}
    hold('HOLD_RECEIVER_READPROOF', has_fields(receiver, ('receiver_id', 'origin_ref', 'readproof_ref', 'observed_at')) and receiver.get('exact_readback') is True and receiver.get('sha256') == digest)
    # Even an asserted readproof still needs independent, out-of-band origin check.
    hold('HOLD_RESTORE_INDEPENDENCE', any((a.get('copy_id') == origin_copy_id and b.get('copy_id') == receiver.get('receiver_id')) or (b.get('copy_id') == origin_copy_id and a.get('copy_id') == receiver.get('receiver_id')) for a, b in paired))
    hold('HOLD_RESTORE_RECONCILIATION', restore.get('duplicate_effects_observed') == 0 and restore.get('recovery_without_human_relay') is True)

    independent_structural = not failures
    return {
        'schema': 'CoAll.CoFedCoDura.PlacementPreflightResult.R0',
        'work_id': packet.get('work_id') if good_text(packet.get('work_id')) else None,
        'edition_id': packet.get('edition_id') if good_text(packet.get('edition_id')) else None,
        'state': 'EVIDENCE_FIELDS_READY__EXTERNAL_AUTHENTICATION_PENDING' if independent_structural else 'HOLD',
        'failure_codes': failures,
        'structural_fields_complete': independent_structural,
        'qualified_pair_count': len(paired),
        'durable_claim_accepted': False,
        'receiver_claim_accepted': False,
        'publication_authorized': False,
        'live_effects': 0,
        'next_deed': 'Independent external custodian must authenticate exact receiver readproof and reproduce cold restore without source provider/device.' if independent_structural else 'Repair only missing or contradictory evidence; do not publish, delete, or promote.',
        'nonclaims': [
            'LOCAL_IS_NOT_LANDED',
            'VALIDATION_IS_NOT_ACCEPTANCE',
            'COPIES_NE_FAILURE_DOMAIN_DIVERSITY',
            'SELF_REPORTED_RECEIPT_NE_INDEPENDENT_ACK',
            'NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF',
            'NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE',
            'HASHING_IS_NOT_SEMANTIC_INGESTION',
            'DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--source', type=Path, required=True, help='Explicit source file, read only; no glob or root scan')
    args = parser.parse_args(argv)
    try:
        packet = json.loads(args.packet.read_text(encoding='utf-8'))
        source = args.source.read_bytes()
        result = review(packet, source)
    except (OSError, UnicodeError, ValueError, TypeError) as e:
        result = {'schema': 'CoAll.CoFedCoDura.PlacementPreflightResult.R0', 'state': 'HOLD', 'failure_codes': ['HOLD_INPUT_UNREADABLE'], 'durable_claim_accepted': False, 'receiver_claim_accepted': False, 'publication_authorized': False, 'live_effects': 0, 'diagnostic': type(e).__name__}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['state'] == 'EVIDENCE_FIELDS_READY__EXTERNAL_AUTHENTICATION_PENDING' else 2


if __name__ == '__main__':
    raise SystemExit(main())
