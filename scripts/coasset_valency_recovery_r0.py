#!/usr/bin/env python3
"""CoAsset valency R0: derived backlinks + synthetic 2-of-3 byte recovery.

The exercise uses only public synthetic data.  The 3 shards are held in memory
with *declared* distinct failure domains, NOT real independent storage.
A typed edge is navigable in both directions but is not a symmetric fact.
"""
from __future__ import annotations
import base64
import hashlib
import json


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def adjacency(graph: dict) -> dict:
    """One source relation, derived forward/back navigation, no invented edge."""
    nodes = graph.get('nodes')
    relations = graph.get('relations')
    if not isinstance(nodes, list) or not isinstance(relations, list):
        raise ValueError('INVALID_GRAPH')
    ids = [n.get('id') for n in nodes]
    if not ids or any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError('INVALID_NODE_IDS')
    result = {ident: {'out': [], 'in': [], 'partners': set()} for ident in ids}
    seen = set()
    for edge in relations:
        if not isinstance(edge, dict) or not all(isinstance(edge.get(k), str) and edge[k]
                                                      for k in ('subject', 'relation', 'object', 'epistemic_class')):
            raise ValueError('INVALID_EDGE')
        source, kind, target = edge['subject'], edge['relation'], edge['object']
        if source not in result or target not in result:
            raise ValueError('DANGLING_LINK')
        if source == target:
            raise ValueError('SELF_LINK_NOT_PARTNER')
        key = (source, kind, target)
        if key in seen:
            raise ValueError('DUPLICATE_RELATION')
        seen.add(key)
        reference = {'source': source, 'relation': kind, 'target': target, 'epistemic_class': edge['epistemic_class']}
        result[source]['out'].append(reference)
        result[target]['in'].append(reference)
        result[source]['partners'].add(target)
        result[target]['partners'].add(source)
    return {k: {'out': v['out'], 'in': v['in'], 'partners': sorted(v['partners'])}
            for k, v in result.items()}


def orphan_nodes(graph: dict) -> list[str]:
    return sorted(node for node, entry in adjacency(graph).items() if not entry['partners'])


def encode_recovery_bundle(content: bytes, carriers: list[dict]) -> dict:
    """Create 2 data half-shards and their XOR parity.  Any 2 valid shards suffice.

    Encode and store the bundle *before* losing the original. This is not
    compression or a proof that existing semantic neighbours carry such data.
    """
    if not isinstance(content, bytes):
        raise ValueError('PAYLOAD_MUST_BE_BYTES')
    if not isinstance(carriers, list) or len(carriers) != 3:
        raise ValueError('NEEDS_THREE_CARRIERS')
    ids = [c.get('id') for c in carriers]
    domains = [c.get('failure_domain') for c in carriers]
    if (not all(isinstance(x, str) and x for x in ids + domains)
            or len(set(ids)) != 3 or len(set(domains)) != 3):
        raise ValueError('CARRIER_ID_OR_FAILURE_DOMAIN_NOT_DIVERSE')
    size = (len(content) + 1) // 2
    padded = content + b'\x00' * (size * 2 - len(content))
    a, b = padded[:size], padded[size:]
    parity = bytes(x ^ y for x, y in zip(a, b))
    roles = ['data0', 'data1', 'xor_parity']
    chunks = [a, b, parity]
    return {
        'schema': 'CoAll.AssetValency.RecoveryBundle.R0.SYNTHETIC',
        'asset_id': 'fixture:overlap-partner-recovery',
        'authority': 'READ_ONLY_SYNTHETIC_TEST',
        'original_sha256': sha(content),
        'original_size': len(content),
        'recovery_threshold': {'k': 2, 'n': 3, 'model': 'two_equal_halves_plus_xor_parity'},
        'carrier_independence': 'DECLARED_ONLY_NOT_PROVEN',
        'shards': {role: {'carrier_id': carriers[i]['id'],
                          'failure_domain': carriers[i]['failure_domain'],
                          'sha256': sha(chunks[i]),
                          'base64': base64.b64encode(chunks[i]).decode('ascii')}
                   for i, role in enumerate(roles)},
        'nonclaims': ['BACKLINK_NE_BYTE_RECOVERY', 'SYNTHETIC_DOMAIN_NE_REAL_INDEPENDENCE',
                      'HASH_NE_DATA', 'TWO_SHARDS_NE_UNIVERSAL_ERASURE_CODING',
                      'LOCAL_ROUNDTRIP_NE_REMOTE_DISASTER_RECOVERY',
                      'GRAPH_VALENCY_NE_COMPLETE_ASSET_CENSUS',
                      'RECONSTRUCTION_NE_RECEIVER_ACK_OR_CANON'],
    }


def recover_from_partners(bundle: dict, surviving_roles: list[str]) -> bytes:
    """Reconstruct original without source bytes; reject damaged/missing proof."""
    if bundle.get('schema') != 'CoAll.AssetValency.RecoveryBundle.R0.SYNTHETIC':
        raise ValueError('UNKNOWN_RECOVERY_SCHEMA')
    if bundle.get('recovery_threshold') != {'k': 2, 'n': 3, 'model': 'two_equal_halves_plus_xor_parity'}:
        raise ValueError('UNKNOWN_RECOVERY_MODEL')
    if len(set(surviving_roles)) != len(surviving_roles):
        raise ValueError('DUPLICATE_ROLE')
    permitted = {'data0', 'data1', 'xor_parity'}
    if not set(surviving_roles) <= permitted:
        raise ValueError('UNKNOWN_ROLE')
    if len(surviving_roles) < 2:
        raise ValueError('INSUFFICIENT_SURVIVORS')
    surviving = {}
    domains = set()
    ids = set()
    for role in surviving_roles:
        item = bundle['shards'].get(role)
        if not isinstance(item, dict):
            raise ValueError('SHARD_NOT_PRESENT')
        if item.get('failure_domain') in domains or item.get('carrier_id') in ids:
            raise ValueError('NON_DISTINCT_CARRIERS')
        domains.add(item.get('failure_domain'))
        ids.add(item.get('carrier_id'))
        try:
            decoded = base64.b64decode(item['base64'], validate=True)
        except (KeyError, ValueError) as e:
            raise ValueError('INVALID_SHARD_ENCODING') from e
        if sha(decoded) != item.get('sha256'):
            raise ValueError('SHARD_HASH_MISMATCH')
        surviving[role] = decoded
    if len({len(c) for c in surviving.values()}) != 1:
        raise ValueError('SHARD_SIZE_MISMATCH')
    a, b, p = (surviving.get(k) for k in ('data0', 'data1', 'xor_parity'))
    if a is None:
        a = bytes(x ^ y for x, y in zip(b, p))
    if b is None:
        b = bytes(x ^ y for x, y in zip(a, p))
    if p is not None and bytes(x ^ y for x, y in zip(a, b)) != p:
        raise ValueError('PARITY_CONTRADICTION')
    size = bundle.get('original_size')
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError('INVALID_LENGTH')
    rebuilt = (a + b)[:size]
    if sha(rebuilt) != bundle.get('original_sha256'):
        raise ValueError('RECOVERY_HASH_MISMATCH')
    return rebuilt


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--graph', required=True)
    args = p.parse_args()
    with open(args.graph, encoding='utf-8') as f:
        graph = json.load(f)
    index = adjacency(graph)
    orphans = [x for x in index if not index[x]['partners']]
    if orphans:
        raise SystemExit('HOLD_ORPHANS_IN_SCOPED_GRAPH ' + json.dumps(orphans))
    content = b'CoLex / CoTermable\x00historical lineage\n' * 3 + b'R0\xff'
    carriers = [{'id': 'fixture:peer-A', 'failure_domain': 'simulated-a'},
                {'id': 'fixture:peer-B', 'failure_domain': 'simulated-b'},
                {'id': 'fixture:peer-C', 'failure_domain': 'simulated-c'}]
    bundle = encode_recovery_bundle(content, carriers)
    for pair in (['data0', 'data1'], ['data0', 'xor_parity'], ['data1', 'xor_parity']):
        if recover_from_partners(bundle, pair) != content:
            raise SystemExit('FAIL_ROUNDTRIP ' + str(pair))
    print(json.dumps({'result': 'PASS_SYNTHETIC_ONLY', 'graph_nodes': len(index),
                      'graph_relations': len(graph['relations']), 'orphan_nodes': orphans,
                      'asset_sha256': sha(content), 'two_of_three_pairs_passed': 3,
                      'real_independent_custody': 'NOT_TESTED',
                      'semantic_reconstruction': 'NOT_TESTED',
                      'receiver_pickup': 'NOT_OBSERVED'}, sort_keys=True))

if __name__ == '__main__':
    main()
