#!/usr/bin/env python3
"""Build the opt-in CoMap R1 source graph from pinned CoLocal evidence.

This is a PUBLIC-SOURCE document/graph consumer, not runtime agent pickup,
CoAll admission, receiver ACK, durable offsite custody, or live deployment.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ai/comap-source-projection-r0.json'
SEED = 'docs/CoLocal/CoLocal2601109_CoRelGRAILS_CoSeed_R0.md'
CI = 'ai/currentness/colocal-cospeedo-currentness-ci-r0-20261112.json'
OUT = 'ai/comap-colocal-currentness-projection-r1.json'
PINS = {
    BASE: '9cc47926d2f61f439db1818702127382f78d693f',
    SEED: 'c9c6dd3a4d6074a5a34e3decdbeb56f574d9f200',
    CI: 'b86ec3d7a30a9c1bb6e96c75fd242a3fe8c5cc97',
}
REPO = 'https://github.com/CoCivium/CoCivium/blob/'
SEED_COMMIT = '311fd21f2fbfeca1c70af023dc5fcd0c7ff3e539'
CI_COMMIT = '1c10b2e3ac63f9ed14a346cd0210323ececfa082'
SEED_SOURCE = 'source:CoLocal2601109_CoRelGRAILS_R0'
CI_SOURCE = 'source:CoLocalCurrentnessCI_R0'
SEED_NODE = 'doc:' + SEED
CI_NODE = 'doc:' + CI


def blob_sha1(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def safe_read(root, relative, expected_hash):
    p = (Path(root) / relative).resolve()
    if not p.is_relative_to(Path(root).resolve()):
        raise ValueError('HOLD_UNSAFE_SOURCE_PATH')
    b = p.read_bytes()
    if blob_sha1(b) != expected_hash:
        raise ValueError('HOLD_SOURCE_BLOB_DRIFT: ' + relative)
    return b


def validate_ci(ci):
    if not isinstance(ci, dict) or ci.get('schema') != 'CoAll.CoLocal.CurrentnessSourceCIReceipt.R0':
        raise ValueError('HOLD_UNKNOWN_RECEIPT_SCHEMA')
    if ci.get('classification') != 'PUBLIC_SOURCE_CI_EXECUTION_RECEIPT_NOT_DEVICE_RUNTIME':
        raise ValueError('HOLD_EVIDENCE_BOUNDARY')
    if ci.get('state') != 'PASS_SOURCE_REGRESSION_ONLY':
        raise ValueError('HOLD_UNQUALIFIED_CI_STATE')
    if ci.get('source', {}).get('commit_sha') != '995c10c96e91dc8fa7e4e7d26c1de2c3b462046b':
        raise ValueError('HOLD_CI_SOURCE_COMMIT')
    if ci.get('source', {}).get('evaluator_git_blob_sha1') != '49089f20a3871a1315f47490d6e237320df0114b':
        raise ValueError('HOLD_CI_EVALUATOR_DRIFT')
    execution = ci.get('execution', {})
    if execution.get('run_id') != 43128120567 or execution.get('conclusion') != 'success' or execution.get('tests_passed') != 15 or execution.get('tests_failed') != 0:
        raise ValueError('HOLD_CI_RUN_UNQUALIFIED')
    if ci.get('independent_review', {}).get('independent_receiver_readproof') is not False:
        raise ValueError('HOLD_ACK_INFERENCE')
    gates = ci.get('gates', {})
    if gates.get('X2_LIVE_RECEIVER') != 'UNVERIFIED' or gates.get('PRODUCTION_GENERATOR_ADOPTION') != 'NOT_PERFORMED':
        raise ValueError('HOLD_RUNTIME_CLAIM')
    return True


def build_projection(base, ci):
    validate_ci(ci)
    if base.get('schema') != 'CoAll.CoMapProjection.R0':
        raise ValueError('HOLD_BASE_SCHEMA')
    nodes = base.get('nodes')
    edges = base.get('edges')
    if not isinstance(nodes, list) or not isinstance(edges, list) or (len(nodes), len(edges)) != (56, 61):
        raise ValueError('HOLD_BASE_COVERAGE')
    node_ids = [n['id'] for n in nodes]
    edge_ids = [e['id'] for e in edges]
    if len(node_ids) != len(set(node_ids)) or len(edge_ids) != len(set(edge_ids)):
        raise ValueError('HOLD_BASE_COLLISION')
    if not {'view:CoMap+', 'domain:CoNodeMesh+/GRAIL+', 'domain:CoAutoEvo+/CoEvo+'}.issubset(node_ids):
        raise ValueError('HOLD_MISSING_DOMAIN_ENDPOINT')
    for edge in edges:
        if edge['from'] not in node_ids or edge['to'] not in node_ids:
            raise ValueError('HOLD_BAD_BASE_EDGE')
    if any(n in node_ids for n in [SEED_NODE, CI_NODE]) or any('e'+str(i) in edge_ids for i in range(62, 67)):
        raise ValueError('HOLD_OVERLAY_COLLISION')

    result = copy.deepcopy(base)
    result['schema'] = 'CoAll.CoMapProjection.R1_CoLocalSourceOverlay'
    result['state'] = 'PUBLIC_SOURCE_BOUND_CANDIDATE_GRAPH_NOT_CANON_OR_RUNTIME'
    result['candidate_date'] = '2026-11-12'
    result['predecessor'] = {'path': BASE, 'git_blob_sha1': PINS[BASE], 'nodes': 56, 'edges': 61, 'preserved': True}
    result['overlay_evidence'] = {
        'status': 'SOURCE_CI_PASS_ONLY', 'source_commit': ci['source']['commit_sha'],
        'ci_run_id': ci['execution']['run_id'], 'ci_tests_passed': ci['execution']['tests_passed'],
        'x2_runtime': 'UNVERIFIED', 'external_receiver_ack': False,
        'sources_pinned': {SEED: PINS[SEED], CI: PINS[CI]},
        'consumer_scope': 'REPRODUCIBLE_PUBLIC_SOURCE_GRAPH_ONLY',
    }
    result['sources'].extend([
        {'id': SEED_SOURCE, 'path': SEED, 'url': REPO + SEED_COMMIT + '/' + SEED, 'blob_sha': PINS[SEED], 'kind': 'public_design_candidate'},
        {'id': CI_SOURCE, 'path': CI, 'url': REPO + CI_COMMIT + '/' + CI, 'blob_sha': PINS[CI], 'kind': 'verified_source_ci_only'},
    ])
    result['nodes'].extend([
        {'id': SEED_NODE, 'label': 'CoLocal CoRelGRAILS candidate Seed', 'kind': 'source_document', 'status': 'PUBLIC_CANDIDATE_NOT_CANON', 'source': SEED_SOURCE, 'url': REPO + SEED_COMMIT + '/' + SEED},
        {'id': CI_NODE, 'label': 'CoCurrentnessGate R0 CI (15 synthetic tests)', 'kind': 'source_document', 'status': 'PASS_SOURCE_CI_ONLY_NOT_RECEIVER', 'source': CI_SOURCE, 'url': REPO + CI_COMMIT + '/' + CI},
    ])
    result['edges'].extend([
        {'id': 'e62', 'from': 'view:CoMap+', 'to': SEED_NODE, 'relation': 'PUBLIC_CANDIDATE_SOURCE_FOR_REVIEW', 'source': SEED_SOURCE, 'state': 'SOURCE_REFERENCED_NOT_ADOPTED'},
        {'id': 'e63', 'from': 'domain:CoNodeMesh+/GRAIL+', 'to': SEED_NODE, 'relation': 'RELATED_RELATIONAL_DESIGN_CANDIDATE', 'source': SEED_SOURCE, 'state': 'CONTEXTUAL_LINK'},
        {'id': 'e64', 'from': 'domain:CoAutoEvo+/CoEvo+', 'to': CI_NODE, 'relation': 'CURRENTNESS_SOURCE_CI_PROOF_REFERENCE', 'source': CI_SOURCE, 'state': 'PASS_SOURCE_CI_ONLY'},
        {'id': 'e65', 'from': 'view:CoMap+', 'to': CI_NODE, 'relation': 'SOURCE_CI_EVIDENCE_REFERENCE', 'source': CI_SOURCE, 'state': 'PASS_SOURCE_CI_ONLY'},
        {'id': 'e66', 'from': SEED_NODE, 'to': CI_NODE, 'relation': 'RELATED_COLOCAL_WORKSTREAM', 'source': CI_SOURCE, 'state': 'CONTEXTUAL_LINK_NOT_SEED_VALIDATION'},
    ])
    result['rails'] = list(dict.fromkeys(list(base.get('rails', [])) + [
        'CI_NE_RECEIVER_ACK', 'LOCAL_IS_NOT_LANDED', 'SOURCE_GRAPH_NE_RUNTIME',
        'CANDIDATE_NE_CANON', 'HASHING_NE_SEMANTIC_VALIDATION'
    ]))
    result['coverage'] = dict(base.get('coverage', {}))
    result['coverage']['colocal_overlay'] = {'source_document_candidates': 2, 'contextual_or_source_ci_edges': 5, 'not_represented': 'Live X2, CoStead pickup, user outcome, independent receiver acceptance'}
    return result


def load_and_build(root=ROOT):
    base = json.loads(safe_read(root, BASE, PINS[BASE]))
    _ = safe_read(root, SEED, PINS[SEED])
    ci = json.loads(safe_read(root, CI, PINS[CI]))
    return build_projection(base, ci)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write', action='store_true', help='Explicitly write the versioned successor')
    parser.add_argument('--check', action='store_true', help='Compare committed successor semantics')
    opts = parser.parse_args()
    if opts.write and opts.check:
        parser.error('choose --write or --check')
    try:
        out = load_and_build(opts.root)
        out_path = opts.root / OUT
        if opts.write:
            if out_path.exists():
                raise ValueError('HOLD_NO_CLOBBER_OUTPUT_EXISTS')
            out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            state = 'WROTE_CANDIDATE_GRAPH_NOT_RUNTIME'
        elif opts.check:
            if json.loads(out_path.read_text(encoding='utf-8')) != out:
                raise ValueError('HOLD_DERIVED_GRAPH_SEMANTIC_DRIFT')
            state = 'PASS_EXACT_SOURCE_PINS_AND_GRAPH_SEMANTICS'
        else:
            state = 'PASS_SOURCE_PINS_OUTPUT_NOT_WRITTEN'
        print(json.dumps({'state': state, 'schema': out['schema'], 'nodes': len(out['nodes']), 'edges': len(out['edges']), 'receiver_ack': False}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'state': 'HOLD_SOURCE_GRAPH', 'reason': str(exc), 'receiver_ack': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
