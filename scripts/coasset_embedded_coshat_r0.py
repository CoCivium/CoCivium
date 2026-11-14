#!/usr/bin/env python3
"""CoAsset R0: in-file verification envelope with two overlap partners.

A *portable wrapper*, not a replacement for an arbitrary original file format.
The hash covers canonical JSON except its own digest field.  No sidecars.
This is a synthetic recovery fixture, NOT authentic signed metadata, a live
receiver, an independent failure domain or a v5.3 Seed survival result.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path

from coasset_valency_recovery_r0 import encode_recovery_bundle, recover_from_partners

SCHEMA = 'CoAll.EmbeddedCoSHAT.R0.SYNTHETIC'
ASSET_ID = 'fixture:recoverable-CoSeed'
VERSION = 'r0'
HASH_SCOPE = 'CANONICAL_JSON_EXCLUDING_ONLY_coSHAT.envelope_sha256'
ROLES = ('data0', 'data1', 'xor_parity')
CARRIERS = (
    ('capsule-A', 'declared-domain-A'),
    ('capsule-B', 'declared-domain-B'),
    ('capsule-C', 'declared-domain-C'),
)
REQUIRED = {'schema', 'coObject', 'coMeta', 'coMetaTrainable', 'coTime',
            'coValence', 'coSHAT', 'recovery', 'fragment_base64', 'nonclaims'}
NONCLAIMS = [
    'SELF_HASH_NE_AUTHENTICITY',
    'HASH_NE_SIGNATURE',
    'TWO_POINTERS_NE_SUFFICIENT_RECOVERY',
    'DECLARED_DOMAINS_NE_INDEPENDENT_PROVIDERS',
    'PORTABLE_WRAPPER_NE_IN_PLACE_FILE_METADATA',
    'SOURCE_BYTES_RECOVERED_NE_MEANING_RESTORED',
    'SYNTHETIC_RESTORE_NE_GT24H_COLD_HANDOFF',
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(obj: dict) -> bytes:
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, allow_nan=False,
                      separators=(',', ':')).encode('ascii')


def scoped_envelope_bytes(capsule: dict) -> bytes:
    body = copy.deepcopy(capsule)
    body['coSHAT'].pop('envelope_sha256', None)
    return canonical_bytes(body)


def seal(capsule: dict) -> dict:
    result = copy.deepcopy(capsule)
    result['coSHAT']['envelope_sha256'] = sha(scoped_envelope_bytes(result))
    return result


def build_capsules(content: bytes) -> list[dict]:
    """Package one original into three standalone JSON documents."""
    if not isinstance(content, bytes):
        raise ValueError('CONTENT_MUST_BE_BYTES')
    carriers = [{'id': ident, 'failure_domain': domain} for ident, domain in CARRIERS]
    bundle = encode_recovery_bundle(content, carriers)
    result = []
    for i, (ident, domain) in enumerate(CARRIERS):
        role = ROLES[i]
        fragment = bundle['shards'][role]
        record = {
            'schema': SCHEMA,
            'coObject': {'id': ASSET_ID, 'version': VERSION,
                         'source_type': 'application/octet-stream',
                         'epistemic_class': 'SYNTHETIC_FIXTURE'},
            'coMeta': {'authority': 'READ_ONLY_SYNTHETIC_TEST',
                       'privacy': 'PUBLIC_SYNTHETIC', 'effect': 'NONE'},
            'coMetaTrainable': {'state': 'FROZEN', 'learning_signal': 'NONE',
                                'evolution': 'VERSIONED_REVIEW_ONLY'},
            'coTime': {'fixture_epoch': 'r0', 'valid_time': 'FIXTURE_ONLY',
                       'source_observation': 'SYNTHETIC_NOT_LIVE'},
            'coValence': {'self_id': ident,
                          'partner_ids': sorted(k for k, _ in CARRIERS if k != ident),
                          'recovery_role': role,
                          'failure_domain': domain,
                          'independence': 'DECLARED_NOT_VERIFIED'},
            'coSHAT': {'algorithm': 'sha256', 'scope': HASH_SCOPE,
                       'source_payload_sha256': bundle['original_sha256'],
                       'fragment_sha256': fragment['sha256'],
                       'envelope_sha256': ''},
            'recovery': {'model': 'TWO_EQUAL_HALVES_PLUS_XOR_PARITY',
                          'threshold_k': 2, 'total_n': 3,
                          'original_size': bundle['original_size']},
            'fragment_base64': fragment['base64'],
            'nonclaims': list(NONCLAIMS),
        }
        result.append(seal(record))
    return result


def verify_capsule(capsule: dict) -> bytes:
    """Validate the fixture contract and content integrity, NOT authenticity."""
    if not isinstance(capsule, dict) or set(capsule) != REQUIRED:
        raise ValueError('INVALID_CAPSULE_FIELDS')
    if capsule['schema'] != SCHEMA:
        raise ValueError('INVALID_SCHEMA')
    for key in ('coObject', 'coMeta', 'coMetaTrainable', 'coTime',
                'coValence', 'coSHAT', 'recovery'):
        if not isinstance(capsule[key], dict):
            raise ValueError('INVALID_FIELD_' + key)
    o, m, t, when, v, h, rec = (capsule[key] for key in
        ('coObject', 'coMeta', 'coMetaTrainable', 'coTime',
         'coValence', 'coSHAT', 'recovery'))
    if o != {'id': ASSET_ID, 'version': VERSION,
             'source_type': 'application/octet-stream',
             'epistemic_class': 'SYNTHETIC_FIXTURE'}:
        raise ValueError('ASSET_IDENTITY_MISMATCH')
    if m != {'authority': 'READ_ONLY_SYNTHETIC_TEST',
              'privacy': 'PUBLIC_SYNTHETIC', 'effect': 'NONE'}:
        raise ValueError('AUTHORITY_BOUNDARY_BROKEN')
    if t != {'state': 'FROZEN', 'learning_signal': 'NONE',
              'evolution': 'VERSIONED_REVIEW_ONLY'}:
        raise ValueError('TRAINABILITY_BOUNDARY_BROKEN')
    if when != {'fixture_epoch': 'r0', 'valid_time': 'FIXTURE_ONLY',
                'source_observation': 'SYNTHETIC_NOT_LIVE'}:
        raise ValueError('TIME_SCOPE_MISMATCH')
    if h.get('algorithm') != 'sha256' or h.get('scope') != HASH_SCOPE:
        raise ValueError('INVALID_HASH_SCOPE')
    try:
        computed = sha(scoped_envelope_bytes(capsule))
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError('INVALID_CANONICAL_ENVELOPE') from exc
    if h.get('envelope_sha256') != computed:
        raise ValueError('ENVELOPE_DIGEST_MISMATCH')
    role = v.get('recovery_role')
    if role not in ROLES:
        raise ValueError('INVALID_ROLE')
    i = ROLES.index(role)
    ident, domain = CARRIERS[i]
    if v != {'self_id': ident,
             'partner_ids': sorted(k for k, _ in CARRIERS if k != ident),
             'recovery_role': role, 'failure_domain': domain,
             'independence': 'DECLARED_NOT_VERIFIED'}:
        raise ValueError('UNQUALIFIED_OR_MISSING_PARTNERS')
    if rec.get('model') != 'TWO_EQUAL_HALVES_PLUS_XOR_PARITY' or \
            rec.get('threshold_k') != 2 or rec.get('total_n') != 3:
        raise ValueError('INVALID_RECOVERY_MODEL')
    if type(rec.get('original_size')) is not int or rec['original_size'] < 0:
        raise ValueError('INVALID_ORIGINAL_SIZE')
    if not isinstance(h.get('source_payload_sha256'), str) or \
            len(h['source_payload_sha256']) != 64:
        raise ValueError('INVALID_SOURCE_DIGEST')
    if not isinstance(capsule['nonclaims'], list) or \
            capsule['nonclaims'] != NONCLAIMS:
        raise ValueError('MISSING_NONCLAIMS')
    try:
        b = base64.b64decode(capsule['fragment_base64'], validate=True)
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError('INVALID_EMBEDDED_FRAGMENT') from exc
    if sha(b) != h.get('fragment_sha256'):
        raise ValueError('FRAGMENT_DIGEST_MISMATCH')
    return b


def reconstruct(capsules: list[dict]) -> bytes:
    """Recover from 2+ intact peer documents and no source payload."""
    if not isinstance(capsules, list) or len(capsules) not in (2, 3):
        raise ValueError('REQUIRES_TWO_OR_THREE_PARTNERS')
    shards, source_hashes, sizes, ids, domains = {}, set(), set(), set(), set()
    for x in capsules:
        raw = verify_capsule(x)
        val, h, rec = x['coValence'], x['coSHAT'], x['recovery']
        ident, role, domain = val['self_id'], val['recovery_role'], val['failure_domain']
        if ident in ids or role in shards or domain in domains:
            raise ValueError('DUPLICATE_CARRIER_OR_DOMAIN')
        ids.add(ident)
        domains.add(domain)
        source_hashes.add(h['source_payload_sha256'])
        sizes.add(rec['original_size'])
        shards[role] = {'carrier_id': ident, 'failure_domain': domain,
                        'sha256': h['fragment_sha256'],
                        'base64': x['fragment_base64']}
    if len(source_hashes) != 1 or len(sizes) != 1:
        raise ValueError('SOURCE_VERSION_CONFLICT')
    bundle = {'schema': 'CoAll.AssetValency.RecoveryBundle.R0.SYNTHETIC',
              'original_sha256': next(iter(source_hashes)),
              'original_size': next(iter(sizes)),
              'recovery_threshold': {'k': 2, 'n': 3,
                                     'model': 'two_equal_halves_plus_xor_parity'},
              'shards': shards}
    return recover_from_partners(bundle, list(shards))


def write_capsules(capsules: list[dict], directory: Path) -> list[Path]:
    """Safe fixture output: fail rather than clobber an existing file."""
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for c in capsules:
        p = directory / (c['coValence']['self_id'] + '.coasset.json')
        with p.open('xb') as f:
            f.write(canonical_bytes(c) + b'\n')
        paths.append(p)
    return paths


def _reject_duplicate_keys(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def read_capsule(path: Path) -> dict:
    record = json.loads(path.read_text('ascii'), object_pairs_hook=_reject_duplicate_keys)
    verify_capsule(record)
    return record


def main():
    import tempfile
    content = b'Public synthetic CoSeed\x00metadata travels with shards\xff\n' * 4
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        original = folder / 'original.bin'
        original.write_bytes(content)
        records = build_capsules(original.read_bytes())
        paths = write_capsules(records, folder)
        original.unlink()
        outcomes = [
            reconstruct([read_capsule(paths[i]) for i in pair]) == content
            for pair in ((0, 1), (0, 2), (1, 2))
        ]
        if not all(outcomes) or original.exists():
            raise SystemExit('FAIL_RECOVERY')
        print(json.dumps({'result': 'PASS_SYNTHETIC_ONLY', 'source_sha256': sha(content),
             'exact_recovery_pairs': sum(outcomes), 'distinct_files': len(paths),
             'original_absent_during_restore': True, 'sidecar_hash_files': 0,
             'receiver_origin_ack': 'NOT_OBSERVED',
             'independent_provider_domains': 'NOT_TESTED',
             'seed_gt24h': 'NOT_TESTED'}, sort_keys=True))


if __name__ == '__main__':
    main()
