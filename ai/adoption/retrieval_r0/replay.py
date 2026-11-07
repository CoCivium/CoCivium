#!/usr/bin/env python3
"""Exact-source, read-only hosted retrieval benchmark. No external model involved."""
import argparse
import datetime
import json
import pathlib
import statistics
import time
from retrieval import DEFAULT_MANIFEST_PIN, verify_manifest, index_source, search, Refuse

# Public-source QA queries: source-to-question discoverability, not generative understanding.
QUERIES = [
    ('start-here','What is CoCivium research project here in sixty seconds'),
    ('evolution-fabric','CoAll Github evolution fabric session contribution domain bounded deltas'),
    ('coevo-schema','CoEvoDelta schema mutation_class epistemic_class receiver authority_ceiling'),
    ('comap-graph','CoAll CoMapProjection R0 56 registered objects 61 edges'),
    ('highlight-register','CoAll HighlightRegistry candidate highlights CoSalute RickBar'),
    ('cosysall-architecture','CoSysAll semantic zoom no rendering interstitial media payload'),
    ('hosted-ci-readproof','hosted_ci_readback workflow 42354438680 source replay 33 tests'),
]

def run(manifest_path,repo_root,output_path):
    manifest=verify_manifest(manifest_path,DEFAULT_MANIFEST_PIN)
    t0=time.perf_counter()
    index=index_source(manifest,repo_root)
    time_index_ms=round((time.perf_counter()-t0)*1000,3)
    results=[]
    for source_id,query in QUERIES:
        t=time.perf_counter()
        d=search(index,query,top_k=5)
        elapsed=(time.perf_counter()-t)*1000
        found=any(x['source_id']==source_id for x in d['results'])
        results.append({'target_source_id':source_id,'query':query,'target_found_in_top5':found,'top5_source_ids':[x['source_id'] for x in d['results']],
                        'latency_ms_local_runner':round(elapsed,3)})
    receipt={'schema':'CoAll.SourcePinnedRetrievalHostedReplay.R0','state':'LOCAL_CODE_REPLAY_NOT_EXTERNAL_MODEL_ADOPTION',
             'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'trusted_manifest_git_blob_sha1':DEFAULT_MANIFEST_PIN,'all_sources_byte_pin_verified':True,
             'source_count':len(index['sources']),'indexed_chunks':len(index['chunks']),
             'index_build_ms_local_runner':time_index_ms,
             'queries_count':len(results),'queries_target_source_in_top5':sum(z['target_found_in_top5'] for z in results),
             'questions':results,'network_requests':0,'model_invocations':0,'training_jobs':0,
             'external_model_receivers_verified':0,'independent_receiver_ack':'NOT_OBSERVED',
             'effect_authority_from_this_adapter':[],'rights_training':'NOT_GRANTED_BY_MANIFEST',
             'meaning':'lexical source discovery, not answer correctness, semantic understanding, model learning or anti-capture certification'}
    pathlib.Path(output_path).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--repo-root',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    try:
        r=run(a.manifest,a.repo_root,a.output)
        print(json.dumps({k:r[k] for k in ('state','source_count','indexed_chunks','queries_count','queries_target_source_in_top5','network_requests','model_invocations')}))
    except Refuse as exc:
        print(json.dumps({'state':'HOLD','reason':str(exc)}));raise SystemExit(2)
