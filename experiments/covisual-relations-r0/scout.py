#!/usr/bin/env python3
"""Offline CoVisual scout: source-page relations, not image scraping or publication.

Python stdlib only. This script performs no network requests, image downloads,
clipboard reads, scheduling, model invocation, or external communication.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
ALLOWED_HOSTS = {
    'reactflow.dev', 'js.cytoscape.org', 'www.sigmajs.org',
    'openverse.org', 'commons.wikimedia.org', 'www.si.edu', 'github.com'
}
KEYS = {'id', 'label', 'kind', 'url', 'use_case', 'candidate_test', 'fit',
        'evidence', 'inspection_cost', 'rights', 'relation'}
KINDS = {'UI_REFERENCE', 'MEDIA_CATALOG', 'COCIVIUM_PRIOR'}


def canonical_url(url):
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.username or parts.password or parts.port:
        raise ValueError('PUBLIC_HTTPS_REQUIRED')
    host = (parts.hostname or '').lower()
    if host not in ALLOWED_HOSTS or parts.query or parts.fragment:
        raise ValueError('UNQUALIFIED_HOST_OR_TRACKING_URL')
    if not parts.path.startswith('/') or '..' in parts.path:
        raise ValueError('INVALID_SOURCE_PATH')
    return f'https://{host}{parts.path.rstrip("/") or "/"}'


def validate(d):
    if d.get('schema') != 'CoCivium.VisualResearchRelations.R0':
        raise ValueError('UNKNOWN_SCHEMA')
    entries = d.get('entries')
    if not isinstance(entries, list) or not (1 <= len(entries) <= 24):
        raise ValueError('BOUNDED_ENTRIES_REQUIRED')
    ids, urls = set(), set()
    for item in entries:
        if set(item) != KEYS or item['kind'] not in KINDS:
            raise ValueError('UNDECLARED_FIELD_OR_KIND')
        if not isinstance(item['id'], str) or not item['id'].isascii() or not item['id'].replace('-', '').isalnum():
            raise ValueError('BAD_ID')
        if item['id'] in ids:
            raise ValueError('DUPLICATE_ID')
        ids.add(item['id'])
        url = canonical_url(item['url'])
        if url in urls:
            raise ValueError('DUPLICATE_SOURCE')
        urls.add(url)
        for key in ('fit','evidence','inspection_cost'):
            value = item[key]
            if type(value) is not int or not (1 <= value <= 5):
                raise ValueError('UNQUALIFIED_SCORE')
        for key in ('label','use_case','candidate_test','rights','relation'):
            if not isinstance(item[key], str) or not (2 <= len(item[key]) <= 250):
                raise ValueError('MISSING_DESCRIPTION')
    return entries


def rank(entries, slots=3):
    if type(slots) is not int or not (1 <= slots <= 3):
        raise ValueError('MATERIALIZATION_BUDGET_EXCEEDED')
    # Selection is a hypothesis, not empirical usefulness or image rights.
    return sorted(entries, key=lambda x: (-2*x['fit'] - x['evidence'] + x['inspection_cost'], x['id']))[:slots]


def eligible_to_embed(asset):
    """An individual asset must have rights proof, public privacy and exact scope.

    This R0 scout has no actual individual assets meeting the conditions.
    """
    return (asset.get('asset_rights') == 'EXACT_ITEM_VERIFIED'
            and asset.get('privacy') == 'PUBLIC'
            and asset.get('allowed_use') == 'EXPLICITLY_PERMITTED'
            and asset.get('exact_source')
            and asset.get('reviewed_by')
            and asset.get('external_effect_authority') == 'SPECIFIC_PUBLIC_RELEASE_GRANTED') is True


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('utf-8')


def make_report():
    path = ROOT / 'sources.json'
    raw = path.read_bytes()
    entries = validate(json.loads(raw))
    selected = rank(entries)
    return {
        'schema': 'CoCivium.CoVisualSourceReport.R0',
        'source_sha256': sha(raw),
        'source_candidates': len(entries),
        'selected_reference_ids': [e['id'] for e in selected],
        'image_assets_reused': 0,
        'third_party_image_bytes_downloaded': 0,
        'executed_model_workers': 0,
        'network_requests': 0,
        'broadcast_messages': 0,
        'recipient_acks': 0,
        'status': 'OFFLINE_REFERENCE_ONLY',
        'note': 'Ranked hypotheses and source links. No live visitor, device, licensing or image-level acceptance.'
    }


def ledger_events(report):
    observations = [
      ('SOURCE_SCHEMA_AND_BOUNDEDNESS', 'PASS', {'source_candidates':report['source_candidates']}),
      ('PUBLIC_HTTPS_AND_DEDUP', 'PASS', {'count':report['source_candidates']}),
      ('RANK_REPRODUCIBILITY', 'PASS', {'selected':report['selected_reference_ids']}),
      ('THIRD_PARTY_IMAGE_LICENSES', 'HOLD', {'reason':'No individual image file has been qualified'}),
      ('EXTERNAL_IMAGE_SCRAPE', 'NOT_RUN', {'reason':'Not authorized and unnecessary for a source-reference index'}),
      ('BROWSER_USER_COMPREHENSION', 'NOT_RUN', {'reason':'No independent first-use subject'}),
      ('PUBLIC_BROADCAST', 'HOLD', {'reason':'No exact opt-in receivers or asset-specific permissions'}),
    ]
    prior = '0'*64
    lines = []
    for i, (kind, status, detail) in enumerate(observations, 1):
        obj={'schema':'CoBenchmarkEvoEvent/VisualR0','seq':i,'kind':kind,'status':status,
             'detail':detail,'prev_hash':prior}
        obj['event_hash'] = sha(canonical(obj))
        prior = obj['event_hash']
        lines.append(canonical(obj).decode('utf-8'))
    return '\n'.join(lines)+'\n', prior


def verify_ledger(raw, head):
    prior='0'*64
    rows=raw.splitlines()
    for i, line in enumerate(rows,1):
        row=json.loads(line)
        if row.get('seq') != i or row.get('prev_hash') != prior:
            raise ValueError('BROKEN_CHAIN')
        orig={k:v for k,v in row.items() if k!='event_hash'}
        if row.get('event_hash') != sha(canonical(orig)):
            raise ValueError('TAMPERED_EVENT')
        prior = row['event_hash']
    if prior != head or len(rows) != 7:
        raise ValueError('INCORRECT_HEAD_OR_COUNT')
    return True


if __name__ == '__main__':
    r=make_report()
    (ROOT/'REPORT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    entries,head=ledger_events(r)
    (ROOT/'benchmark_evo.jsonl').write_text(entries,encoding='utf-8')
    (ROOT/'HEAD.sha256').write_text(head+'\n',encoding='utf-8')
    assert verify_ledger(entries,head)
    print(json.dumps(r,indent=2))
