#!/usr/bin/env python3
"""CoSpiff: bounded first-task path qualification, no network, AI, tracking, or external effects."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
ALLOWED_REPOS = {'CoCivium/CoCivium', 'CoCivium/CoAcademy'}
TOKENS = {
    'words': {'draft', 'writing', 'sentence', 'rewrite', 'proofread', 'edit', 'undo', 'cursor', 'phrase'},
    'civic': {'civic', 'election', 'elections', 'municipal', 'legislation', 'government', 'policy', 'ballot'},
    'relationships': {'map', 'graph', 'visualize', 'connection', 'connections', 'relationships', 'orb'},
    'play': {'game', 'satire', 'fiction', 'play', 'fictional'},
    'build': {'build', 'developer', 'code', 'api', 'repository', 'integration', 'tool', 'python'},
}
# Examples never require a visitor to supply private or regulated data.
SENSITIVE = {'password', 'passphrase', 'secret', 'private key', 'wallet seed', 'api key', 'bank account'}


def load_registry(path=ROOT / 'routes_snapshot.json'):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def audit_registry(registry):
    failures = []
    if registry.get('schema') != 'CoSpiff.FirstDoorReadback.R0': failures.append('BAD_SCHEMA')
    routes = registry.get('routes')
    if not isinstance(routes, list) or len(routes) != 6: return ['SIX_ROUTES_REQUIRED']
    ids = [r.get('id') for r in routes]
    if len(set(ids)) != len(ids): failures.append('DUPLICATE_ROUTE_ID')
    if ids.count(registry.get('default_route')) != 1: failures.append('MISSING_DEFAULT')
    if ids != ['one-task', 'words', 'civic', 'relationships', 'play', 'build']: failures.append('UNEXPECTED_ROUTE_IDS_OR_ORDER')
    for r in routes:
        if r.get('repository') not in ALLOWED_REPOS: failures.append('UNKNOWN_REPO:' + str(r.get('id')))
        if r.get('branch') not in {'main', 'master'}: failures.append('UNKNOWN_BRANCH:' + str(r.get('id')))
        if not re.fullmatch(r'[0-9a-f]{40}', r.get('git_blob', '')): failures.append('BAD_BLOB:' + str(r.get('id')))
        if r.get('role_required') is not False or r.get('authority') != 'NONE' or r.get('source_only') is not True:
            failures.append('IMPLIED_AUTHORITY:' + str(r.get('id')))
        path = r.get('path', '')
        if not path or any(p in {'..', '.', ''} for p in path.split('/')) or '?' in path: failures.append('BAD_PATH:' + str(r.get('id')))
        expected_url = f"https://github.com/{r.get('repository')}/blob/{r.get('branch')}/{path}"
        if r.get('source_url') != expected_url: failures.append('SOURCE_URL_MISMATCH:' + str(r.get('id')))
        if urlparse(r.get('source_url','')).hostname != 'github.com': failures.append('NON_GITHUB_ROUTE:' + str(r.get('id')))
    return failures


def propose_route(text):
    """Advisory only. Deliberately conservative and not a user profiler."""
    if not isinstance(text,str) or len(text) > 4000:
        return {'route':'one-task','state':'HOLD','reason':'INVALID_OR_OVERSIZED_INPUT'}
    lower=text.casefold()
    if any(k in lower for k in SENSITIVE):
        return {'route':'one-task','state':'HOLD','reason':'SENSITIVE_MATERIAL_NOT_NEEDED'}
    words=set(re.findall(r'[a-z]+',lower))
    candidates=sorted([route for route, triggers in TOKENS.items() if triggers & words])
    if not candidates:
        return {'route':'one-task','state':'DEFAULT','reason':'NO_SPECIALIST_SIGNAL'}
    if len(candidates)!=1:
        return {'route':'one-task','state':'ASK_OPTIONAL_CHOICE','reason':'MULTIPLE_INTERESTS_'+str(len(candidates))}
    return {'route':candidates[0], 'state':'SUGGEST_ONLY','reason':'ONE_EXPLICIT_TASK_SIGNAL'}


def hash_event(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')).hexdigest()


def write_ledger(events,path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    prior='0'*64
    with path.open('w',encoding='utf-8',newline='\n') as file:
        for seq,event in enumerate(events,1):
            row={'schema':'CoSpiff.BenchmarkEvo.R0','seq':seq,'prev_hash':prior,**event}
            row['event_hash']=hash_event(row)
            file.write(json.dumps(row,sort_keys=True,ensure_ascii=True,separators=(',',':'))+'\n')
            prior=row['event_hash']
    (path.parent / 'HEAD.sha256').write_text(prior+'\n',encoding='ascii')
    return prior


def verify_ledger(path, head):
    prev='0'*64
    lines=Path(path).read_text(encoding='utf-8').splitlines()
    if not lines: raise ValueError('EMPTY_LEDGER')
    for num,line in enumerate(lines,1):
        def no_duplicate(pairs):
            d={}
            for k,v in pairs:
                if k in d:raise ValueError('DUPLICATE_KEY')
                d[k]=v
            return d
        row=json.loads(line, object_pairs_hook=no_duplicate)
        if row.get('seq') != num or row.get('schema') != 'CoSpiff.BenchmarkEvo.R0' or row.get('prev_hash') != prev:
            raise ValueError('BAD_CHAIN_AT_'+str(num))
        recorded=row.pop('event_hash',None)
        if hash_event(row)!=recorded: raise ValueError('BAD_HASH_AT_'+str(num))
        prev=recorded
    if prev!=head: raise ValueError('WRONG_PINNED_HEAD')
    return len(lines)

# A tiny, authored task suite. This measures code behavior, not real people.
FIXTURES = [
 ('help with a writing draft','words'),
 ('edit a sentence','words'),
 ('preview next cursor phrase','words'),
 ('check an election claim','civic'),
 ('explore civic evidence','civic'),
 ('review municipal spending','civic'),
 ('view an orb graph','relationships'),
 ('map connections','relationships'),
 ('visualize relationships','relationships'),
 ('try a fictional game','play'),
 ('satire about elections','one-task'), # multi-interest: intentional opt-in
 ('learn with play','play'),
 ('build a python tool','build'),
 ('developer repository','build'),
 ('create an API','build'),
 ('just show me what this is','one-task'),
 ('research unknown topic','one-task'),
 ('find official sources about a housing bylaw','civic'), # legitimate civic task not covered by terms: preserve miss
 ('my API key is here','HOLD'),
 ('build an educational game','one-task'), # multiple interests, no assumed choice
]

def main():
    registry=load_registry()
    violations=audit_registry(registry)
    results=[]
    for phrase,expect in FIXTURES:
        result=propose_route(phrase)
        actual = 'HOLD' if result['state']=='HOLD' else result['route']
        results.append({'expected':expect,'actual':actual,'pass':actual==expect,'reason':result['reason']})
    source_event={'kind':'SOURCE_REGISTRY','status':'PASS' if not violations else 'FAIL','result':{'exact_github_blob_readbacks_reported':6,'registry_issues':violations,'limit':'Tool readbacks outside this script; not user uptake or HTTP Pages test.'}}
    events=[source_event]
    events += [{'kind':'ROUTE_FIXTURE','status':'PASS' if x['pass'] else 'FAIL','result':{'fixture_index':i,'expected':x['expected'],'actual':x['actual'],'reason':x['reason']}} for i,x in enumerate(results,1)]
    events += [
       {'kind':'HUMAN_FIRST_USE','status':'HOLD','result':{'reason':'No independent consenting newcomer task result or comprehension measurement.'}},
       {'kind':'BROWSER_VISUAL','status':'NOT_RUN','result':{'reason':'Headless Chromium screenshot attempt timed out; no visual or assistive-tech acceptance reported.'}},
       {'kind':'PUBLIC_HOST','status':'NOT_RUN','result':{'reason':'GitHub source readback does not prove custom-domain TLS, Pages browser reachability, or site uptime.'}},
       {'kind':'ANALYTICS','status':'HOLD','result':{'reason':'Connected analytics cannot establish CoCivium-wide visitors or conversion; tracking not enabled in this prototype.'}},
       {'kind':'ROUTE_AB_COMPARISON','status':'NOT_RUN','result':{'reason':'No independent participants for default-vs-specialist comparison.'}},
       {'kind':'EXTERNAL_DELIVERY','status':'HOLD','result':{'reason':'No approved recipient manifest or independently acknowledged CoVIA/Gmail/node transport.'}},
    ]
    path=ROOT/'output'/'benchmark_evo.jsonl'
    head=write_ledger(events,path)
    summary={'schema':'CoSpiff.Result.R0','registered_routes':6,'source_blob_matches_observed':6,'fixture_count':len(results),'fixture_pass':sum(x['pass'] for x in results),'fixture_fail':sum(not x['pass'] for x in results),'event_count':len(events),'event_outcomes':{s:sum(e['status']==s for e in events) for s in ['PASS','FAIL','HOLD','NOT_RUN']},'ledger_head':head,'nonclaims':['HAND_AUTHORED_FIXTURES_NOT_REAL_PEOPLE','SOURCE_MATCH_NOT_AUDIENCE','RANKING_IS_NOT_AUTHORITY','NO_AUTO_PROFILING','NO_NETWORK_RUNTIME']}
    (ROOT/'output'/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if violations: raise SystemExit(1)

if __name__ == '__main__':main()
