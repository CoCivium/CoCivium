"""Pure source-ingestion triage. Never runs, sends, promotes, or reveals input."""
from __future__ import annotations
import hashlib
import json
import re
from typing import Any

HASH = re.compile(r'^[a-f0-9]{64}$')
POLICY_VERSION = 'CoAll.FabricIngestion.R1.candidate'
CLASSIFY = {'SOURCE_REFERENCE','CODE_REFERENCE','DESIGN_NOTE','EXPERIMENT_RESULT',
            'MEDIA_REFERENCE','RELATION_HYPOTHESIS'}
TRANSFORMS = {'BACKTRACE','CONVERSE','NEGATION','MIRROR','TRUE_INVERSE',
              'COMPENSATION','ALTERNATIVE','NONE'}
DANGEROUS_SIGNALS = ('ignore previous instructions', 'reveal secret',
                     'disable safeguards', 'override system instructions')


def _hold(state: str, why: str, source_id: str | None = None) -> dict:
    return dict(policy=POLICY_VERSION, source_id=source_id, state=state,
                rewise=why, effect='NONE', delivery='NOT_ATTEMPTED',
                receiver_ack='NOT_PROVEN', human_relay='NOT_REQUIRED',
                next_action='QUALIFY_OR_REVIEW',)


def triage(obj: Any, prior_hashes=()) -> dict:
    """Return metadata-only classification; source content remains in caller custody.

    No network, filesystem mutation, credential validation, AI execution, or
    actual external tool access. An explicit classification is not authorization.
    """
    if not isinstance(obj, dict):
        return _hold('SOFT_QUARANTINE_BAD_ENVELOPE', 'The input is not a typed source envelope.')
    source_id = obj.get('source_id')
    if not isinstance(source_id, str) or not source_id or len(source_id) > 160:
        return _hold('SOFT_QUARANTINE_MISSING_ID', 'Stable source identity is absent.')
    raw = obj.get('raw')
    if not isinstance(raw, str) or not raw or len(raw.encode('utf-8')) > 128000:
        return _hold('SOFT_QUARANTINE_SOURCE_SIZE', 'Raw source is empty, unavailable, or beyond the bounded intake size.', source_id)
    computed_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    if obj.get('sha256') != computed_hash:
        return _hold('SOFT_QUARANTINE_HASH_MISMATCH', 'Exact source hash must match before interpretation.', source_id)
    if obj.get('source_type') not in CLASSIFY:
        return _hold('SOFT_QUARANTINE_UNKNOWN_TYPE', 'The source type needs an explicit adapter.', source_id)
    if obj.get('source_ref') is None or not isinstance(obj['source_ref'], str) or not obj['source_ref']:
        return _hold('SOFT_QUARANTINE_NO_PROVENANCE', 'A verifiable source pointer is required.', source_id)
    if obj.get('rights') != 'QUALIFIED':
        return _hold('SOFT_QUARANTINE_RIGHTS', 'Rights and retention must be qualified before use.', source_id)
    if obj.get('privacy') not in ('PUBLIC_SAFE', 'PRIVATE_SCOPED'):
        return _hold('SOFT_QUARANTINE_PRIVACY', 'Privacy class is unknown or inappropriate.', source_id)
    if obj.get('consent') != 'QUALIFIED':
        return _hold('SOFT_QUARANTINE_CONSENT', 'Applicable consent was not established.', source_id)
    if obj.get('untrusted_instructions') or any(t in raw.lower() for t in DANGEROUS_SIGNALS):
        return _hold('SOFT_QUARANTINE_INSTRUCTION_RISK', 'Untrusted source text must remain data, not a command.', source_id)
    if obj.get('auth_or_api_token'):
        return _hold('SOFT_QUARANTINE_SECRET', 'Credentials are never permitted inside work packets.', source_id)
    if obj.get('transform_kind') not in TRANSFORMS:
        return _hold('SOFT_QUARANTINE_TRANSFORM', 'Transformation type must be distinguished from inverses and negations.', source_id)
    if obj['transform_kind'] == 'TRUE_INVERSE' and not (obj.get('lossless_proven') is True and obj.get('transform_version')):
        return _hold('SOFT_QUARANTINE_NONINVERTIBLE', 'A reverse lookup is not proof of a true inverse.', source_id)
    if obj.get('replace_history'):
        return _hold('SOFT_QUARANTINE_HISTORY', 'Append a successor; never rewrite original evidence.', source_id)
    if obj.get('effect_authority') not in (None, 'NONE'):
        return _hold('SOFT_QUARANTINE_EFFECT_AUTHORITY', 'Ingestion never grants execution authority.', source_id)
    if computed_hash in prior_hashes:
        return dict(_hold('DEDUPED_EXISTING_SOURCE', 'Original source already recorded; reuse its immutable identity.', source_id), source_hash=computed_hash)
    return dict(policy=POLICY_VERSION, source_id=source_id, source_hash=computed_hash,
                state='SHADOW_REVIEW_READY', source_type=obj['source_type'],
                privacy=obj['privacy'], transform_kind=obj['transform_kind'],
                rewise='The source is traceable and eligible for bounded independent review, not execution.',
                effect='NONE', delivery='NOT_ATTEMPTED', receiver_ack='NOT_PROVEN',
                build='NOT_STARTED', ci='NOT_RUN', x2='NOT_VERIFIED',
                next_action='INDEPENDENT_REVIEW_AND_NEGATIVE_TESTS',
                human_relay='NOT_REQUIRED')


def fixture(raw='A candidate source with no instructions', **changes):
    obj=dict(source_id='synthetic-source-A',source_ref='synthetic://sample/A',
             raw=raw,sha256=hashlib.sha256(raw.encode('utf-8')).hexdigest(),
             source_type='DESIGN_NOTE',privacy='PUBLIC_SAFE',rights='QUALIFIED',
             consent='QUALIFIED',transform_kind='BACKTRACE',effect_authority='NONE')
    obj.update(changes)
    return obj