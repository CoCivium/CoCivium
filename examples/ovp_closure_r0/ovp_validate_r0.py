#!/usr/bin/env python3
"""OVP R0: read-only synthetic closure validator, NOT an effect controller."""
import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = 'CoAll.OVP.CoObjectClosure.R0.synthetic'
REQUIRED_ROLES = frozenset(('entry','worker','state','view','receipt','recovery','permission','return'))
DIGEST = re.compile(r'sha256:[0-9a-f]{64}\Z')


def evaluate(manifest: dict[str, Any]) -> dict[str, Any]:
    errors: set[str] = set()
    holds: set[str] = set()
    notes: set[str] = set()
    if not isinstance(manifest, dict) or manifest.get('schema') != SCHEMA:
        return {'schema': 'CoAll.OVP.ClosureResult.R0', 'closure_class': 'SOURCE_INCOMPLETE_HELD', 'errors':['SCHEMA_INVALID'], 'holds':[], 'notes':[], 'live_effect_authorized':False, 'receiver_proof_verified':False}
    for field in ('work_id','set_id','receiver','task','scope','observation_time'):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            errors.add('MISSING_'+field.upper())
    if manifest.get('effect_request') != 'NONE':
        errors.add('EFFECT_REQUEST_NOT_PERMITTED_BY_SOURCE_VALIDATOR')
    if manifest.get('native_escape_declared') is not True:
        errors.add('NO_NATIVE_ESCAPE_CONTRACT')
    if manifest.get('read_only_text_fallback') is not True:
        errors.add('NO_READ_ONLY_TEXT_FALLBACK')
    if manifest.get('receiver_evidence') != 'NOT_OBSERVED':
        holds.add('RECEIVER_ASSERTION_UNAUTHENTICATED')
    else:
        holds.add('AWAITING_INDEPENDENT_RECEIVER_PROOF')
    if manifest.get('last_known_good_head') == 'UNKNOWN_NOT_INVENTED':
        holds.add('LAST_KNOWN_GOOD_HEAD_UNKNOWN')
    nodes = manifest.get('nodes')
    if not isinstance(nodes, list) or len(nodes) > 128:
        errors.add('BAD_NODE_LIST')
        nodes=[]
    ids: dict[str, dict[str, Any]] = {}
    roles: set[str] = set()
    graph: dict[str, list[str]] = {}
    degraded=False
    for node in nodes:
        if not isinstance(node,dict):
            errors.add('NON_OBJECT_NODE')
            continue
        id_ = node.get('id')
        if not isinstance(id_,str) or not re.fullmatch(r'[a-z][a-z0-9-]{1,63}',id_):
            errors.add('INVALID_NODE_ID')
            continue
        if id_ in ids:
            errors.add('DUPLICATE_NODE_ID')
            continue
        ids[id_]=node
        role=node.get('role')
        if isinstance(role,str):
            roles.add(role)
        else:
            errors.add('MISSING_ROLE')
        if not node.get('source_ref') or not node.get('revision'):
            errors.add('MISSING_SOURCE_IDENTITY')
        if not isinstance(node.get('source_digest'),str) or DIGEST.fullmatch(node['source_digest']) is None:
            errors.add('INVALID_SHA256_FORMAT')
        if node.get('digest_kind') != 'SYNTHETIC_FIXTURE_LABEL_NOT_REAL_SOURCE_BYTES':
            errors.add('UNSUPPORTED_SOURCE_DIGEST_PROVENANCE')
        if node.get('authority') != 'NONE_FROM_SOURCE':
            errors.add('SOURCE_ATTEMPTS_AUTHORITY_ESCALATION')
        if node.get('state') != 'SOURCE_TESTED_ONLY':
            errors.add('UNSUPPORTED_SOURCE_CLAIM')
        if node.get('currentness') != 'FRESH_FOR_FIXTURE':
            if node.get('required') is True:
                errors.add('REQUIRED_NODE_STALE_OR_UNKNOWN')
            else:
                degraded=True
                if node.get('fallback') != 'TEXT_VIEW':
                    errors.add('DEGRADED_NODE_WITHOUT_FALLBACK')
        dependencies=node.get('depends_on')
        if not isinstance(dependencies,list):
            errors.add('BAD_DEPENDENCY_LIST')
            graph[id_]=[]
        else:
            graph[id_]=[]
            for d in dependencies:
                if not isinstance(d,dict) or not isinstance(d.get('id'),str) or not isinstance(d.get('revision'),str):
                    errors.add('BAD_DEPENDENCY_PIN')
                    continue
                graph[id_].append(d['id'])
    for id_,node in ids.items():
        for d in node.get('depends_on',[]) if isinstance(node.get('depends_on'),list) else []:
            if not isinstance(d,dict) or not isinstance(d.get('id'),str):
                continue
            other=ids.get(d['id'])
            if other is None:
                errors.add('MISSING_PINNED_DEPENDENCY')
            elif d.get('revision')!=other.get('revision'):
                errors.add('INCOMPATIBLE_DEPENDENCY_REVISION')
    missing=REQUIRED_ROLES-roles
    if missing:
        errors.add('MISSING_REQUIRED_ROLES:'+','.join(sorted(missing)))
    if not any(n.get('role')=='entry' for n in ids.values()):
        errors.add('NO_ENTRY_ANCHOR')
    else:
        entry_ids=[i for i,n in ids.items() if n.get('role')=='entry']
        visited=set()
        def walk(n: str, active: set[str]) -> None:
            if n in active:
                errors.add('DEPENDENCY_CYCLE')
                return
            if n in visited or n not in graph:
                return
            active.add(n)
            for child in graph[n]:
                walk(child, active)
            active.remove(n)
            visited.add(n)
        for entry in entry_ids:
            walk(entry,set())
        for role in REQUIRED_ROLES:
            if not any(n.get('role')==role and i in visited for i,n in ids.items()):
                errors.add('REQUIRED_ROLE_NOT_IN_ENTRY_CLOSURE:'+role)
    if errors:
        c='SOURCE_INCOMPLETE_HELD'
    elif degraded:
        c='SOURCE_DEGRADED_READ_ONLY'
    else:
        c='SOURCE_BOUND_CLOSURE'
    notes.add('SOURCE_STRUCTURE_ONLY_NOT_INSTALLED_APP')
    notes.add('SOURCE_PINS_NOT_VERIFIED_AGAINST_REAL_BYTES')
    notes.add('NO_EXTERNAL_EFFECT_AUTHORIZED')
    notes.add('REAL_C3_C4_C5_REQUIRE_INDEPENDENT_OBSERVATION')
    return {'schema':'CoAll.OVP.ClosureResult.R0','closure_class':c,'real_product_class':'AWAITING_INDEPENDENT_RECEIVER_PROOF' if not errors else 'HELD_UNQUALIFIED','roles_present':sorted(roles),'required_roles_present':sorted(REQUIRED_ROLES & roles),'node_count':len(ids),'dependency_count':sum(map(len,graph.values())),'errors':sorted(errors),'holds':sorted(holds),'notes':sorted(notes),'live_effect_authorized':False,'receiver_proof_verified':False,'source_scope_only':True}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('fixture',type=Path)
    ns=ap.parse_args()
    m=json.loads(ns.fixture.read_text(encoding='utf-8'))
    report=evaluate(m)
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if not report['errors'] else 1

if __name__=='__main__':
    raise SystemExit(main())
