#!/usr/bin/env python3
"""CoDoodle R0: opt-in, local-only routing hints; never perform effects."""
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = 'CoDoodle.Intake.R0'
MAX_BYTES = 65536
# Reference existing source contracts. These are routing hints, not implementations.
ROUTES = (
    ('INPUT', ('mouse', 'keyboard', 'perixx', 'thumb', 'keypress', 'pointer'),
     'docs/Architecture/COINTERSTICE_COINVERSION_COGLYPH_INPUT_FABRIC_R0_20261024.md',
     'Check one opted-in local preview with Escape/cancel; no global hooks.',
     'A passive key interval is not user consent.'),
    ('MEDIA', ('media', 'video', 'ffprobe', 'payload', 'paste', 'file'),
     'docs/Architecture/COEVOALL_LARGEST_PATHS_AUTOCYCLE_R1_20261024.md',
     'Check exact hash and one local non-sensitive media preview.',
     'A file pointer is not a transferred payload.'),
    ('VISUAL', ('diagram', 'comap', 'coorb', 'lens', 'render', 'glyph'),
     'docs/broadcasts/EVO_ALL_BETTERS_CONTEXT_GLYPHS_TELLS_R0_20261024.md',
     'Compare readable text and source-linked graphic for one claim.',
     'A pleasing visual does not validate an observation.'),
    ('INVERSION', ('inversion', 'inverse', 'coinv', 'counterfactual', 'nots'),
     'docs/Architecture/COINTERSTICE_COINVERSION_COGLYPH_INPUT_FABRIC_R0_20261024.md',
     'Record one falsifier or alternative interpretation beside its claim.',
     'Negation cannot turn unknown into observed absence.'),
    ('RECOVERY', ('stuck', 'session', 'cozombie', 'heartbeat', 'recovery', 'restart'),
     'docs/Operations/COFLEET_HUMAN_TIME_ACCELERATION_R0_20261024.md',
     'Cold-start one bounded task using a source-bound checkpoint.',
     'A pointer or same-host rehash is not an independent receiver ACK.'),
    ('PROVIDER', ('claude', 'ollama', 'llama', 'pi ', 'open source', 'provider'),
     'docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md',
     'Compare provider-neutral fixture with deterministic baseline before model calls.',
     'Provider availability does not imply authorization or quality parity.'),
    ('REPLAY', ('historical', 'older models', 'old llm', 'priors', 'redo'),
     'docs/Architecture/COEXPERIMENT_SELECTOR_R0.md',
     'Replay one pinned historical artifact with independent before/after evaluation.',
     'A newer model is not automatically better.'),
)
SENSITIVE = re.compile(r'(?i)\b(password|passphrase|private\s+key|api\s*key|secret\s+token|bank\s+login)\b')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def classify(payload):
    if not isinstance(payload, dict) or payload.get('schema') != SCHEMA:
        raise ValueError('expected schema CoDoodle.Intake.R0')
    raw = payload.get('raw_doodle')
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError('raw_doodle must be nonempty text')
    data = raw.encode('utf-8')
    if len(data) > MAX_BYTES:
        raise ValueError('input exceeds 65536 UTF-8 bytes')
    if type(payload.get('opt_in_local_review')) is not bool:
        raise ValueError('explicit opt_in_local_review required')
    if payload.get('scope') not in ('PUBLIC_SYNTHETIC', 'PRIVATE_LOCAL'):
        raise ValueError('scope must be PUBLIC_SYNTHETIC or PRIVATE_LOCAL')
    base = {'schema':'CoDoodle.Preview.R0', 'source_sha256':sha(data), 'source_bytes':len(data),
            'state':'HELD_NO_EFFECTS', 'effects':{'workers':0,'providers':0,'device_hooks':0,'external_sends':0},
            'routing':'KEYWORD_HINTS_NE_INTENT_OR_AUTHORITY', 'candidates':[],
            'selector':'EXPLICIT_EVIDENCE_LINKED_METRICS_REQUIRED_BEFORE_COEXPERIMENTSELECTOR',
            'nonclaims':['SHADOW_NE_RUNTIME','LOGICAL_NE_LIVE','METADATA_NE_CONSENT',
                         'SYMBOLIC_NE_EMPIRICAL_PROOF','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF']}
    if not payload['opt_in_local_review']:
        base['state'] = 'HELD_NO_OPT_IN'
        return base
    if SENSITIVE.search(raw):
        base['state'] = 'HELD_SENSITIVE_CONTEXT'
        return base
    lowered = raw.lower()
    for kind, terms, source, test, falsifier in ROUTES:
        if any(term in lowered for term in terms):
            base['candidates'].append({
                'candidate_id':'codoodle:'+sha((base['source_sha256']+'|'+kind).encode())[:24],
                'kind':kind, 'source_contract':source, 'micro_canary_proposal':test,
                'negative_control':falsifier, 'epistemic_state':'UNASSESSED',
                'authority':'NONE', 'effects':'NONE'})
    if base['candidates']:
        base['state']='CANDIDATE_PREVIEW_ONLY'
    return base


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path)
    args=p.parse_args()
    if args.input.stat().st_size > MAX_BYTES * 2:
        p.error('input file too large')
    try:
        result=classify(json.loads(args.input.read_text(encoding='utf-8')))
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    print(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False))

if __name__ == '__main__':
    main()
