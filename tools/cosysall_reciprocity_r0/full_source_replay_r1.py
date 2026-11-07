#!/usr/bin/env python3
"""R1 CI-only real checked-in CoMap replay (source-pinned, no effects)."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from reciprocity import Held
from reciprocity_r1 import graph_digest, projection_triplet, bounded_feedback

# This is the exact prequalified public Git blob read back via GitHub connector.
# A source edition change must be separately checked and intentionally updated.
EXPECTED_GIT_BLOB = '9cc47926d2f61f439db1818702127382f78d693f'

def run(graph_path:Path, schema_path:Path, output_path:Path):
    actual_blob=subprocess.run(['git','hash-object',str(graph_path)],capture_output=True,text=True,check=True).stdout.strip()
    if actual_blob!=EXPECTED_GIT_BLOB:
        raise Held('Git source blob not qualified for R1 full-source replay; HOLD')
    graph=json.loads(graph_path.read_text(encoding='utf-8'))
    digest=graph_digest(graph)
    assert len(graph['nodes'])==56 and len(graph['edges'])==61, 'Unexpected source-edition object count'
    view=projection_triplet(graph,'domain:CoStrategy+',digest,limit=12)
    views=view['views']
    sig={k:views[k]['claims_sha256'] for k in ('visual_manifest','accessible_list','machine')}
    assert len(set(sig.values()))==1,'Cross-surface semantics diverged'
    assert view['included_relations']>=2, 'No meaningful source neighborhood'
    src=[e for e in views['machine']['claims']['edges'] if e['id'] in ('e1','e2')]
    assert len(src)==2 and all(e['from']=='domain:CoStrategy+' for e in src),'Edge orientation changed'
    record=bounded_feedback(graph,digest,'repo:CoCivium/MasterPlan','domain:CoStrategy+',
                            'repo:CoCivium/CoCivium',['e1','e2'],
                            'test:cosysall-r1-full-graph-source-pinned','2026-11-07T03:00:54Z',
                            {'reason':'Source-backed shared-neighbor view warrants review; not asserted truth',
                             'observation_scope':'LOCAL_FIXTURE'})
    schema=json.loads(schema_path.read_text(encoding='utf-8'))
    assert not (set(record)-set(schema['properties'])),'Unexpected CoEvoDelta field'
    assert all(k in record for k in schema['required']),'Missing CoEvoDelta required field'
    assert all(record[k] in p['enum'] for k,p in schema['properties'].items() if 'enum' in p),'Unqualified CoEvoDelta class'
    assert record['mutation_class']=='PROPOSE' and record['epistemic_class']=='HYPOTHESIS' and record['authority_ceiling']=='NO_EXTERNAL_EFFECTS__REVIEW_ONLY'
    # Tampering both provenance and direction must fail with pinned source digest.
    altered=copy.deepcopy(graph);a=altered['edges'][0];a['from'],a['to']=a['to'],a['from']
    tamper_held=False
    try:bounded_feedback(altered,digest,'repo:CoCivium/MasterPlan','domain:CoStrategy+',
                         'repo:CoCivium/CoCivium',['e1','e2'],'test:forged','2026-11-07T03:00:54Z',
                         {'reason':'forged test','observation_scope':'LOCAL_FIXTURE'})
    except Held:tamper_held=True
    assert tamper_held,'Forged edge was accepted'
    # Claim made by feedback is not a verified grant.
    forged_grant_held=False
    try:bounded_feedback(graph,digest,'repo:CoCivium/MasterPlan','domain:CoStrategy+',
                         'repo:CoCivium/CoCivium',['e1','e2'],'test:forged-auth','2026-11-07T03:00:54Z',
                         {'reason':'forged permission claim','observation_scope':'LOCAL_FIXTURE','authority_ceiling':'ALLOW_ALL'})
    except Held:forged_grant_held=True
    assert forged_grant_held,'Forged grant was accepted'
    report={
      'schema':'CoSysAll.CV01CV05.FullSourceReplay.R1',
      'status':'PASS_FOR_SOURCE_PINNED_LOCAL_CI_ONLY',
      'source_path':str(graph_path),'qualified_git_blob':EXPECTED_GIT_BLOB,
      'canonical_graph_sha256':digest,'source_nodes':len(graph['nodes']),'source_edges':len(graph['edges']),
      'focus':'domain:CoStrategy+',
      'projection_views':['visual_manifest','accessible_list','machine','none'],
      'parity_sha256':sig['machine'], 'identical_claim_digests':len(set(sig.values()))==1,
      'registered_example_edges':[{'id':e['id'],'from':e['from'],'to':e['to'],'state':e['epistemic_state'],'source_id':e['source_id']} for e in src],
      'candidate':{'delta_id':record['delta_id'],'mutation_class':record['mutation_class'],'epistemic_class':record['epistemic_class'],'authority_ceiling':record['authority_ceiling']},
      'negative_controls':{'reversed_edge_held':tamper_held,'forged_permission_held':forged_grant_held},
      'actual_remote_effects':0,'independent_reader_ack':'NOT_OBSERVED','X2_runtime':'NOT_OBSERVED',
      'meaning':'Same structured claims across three projected manifests, not independent human comprehension or three executed visual UIs',
      'next_gate':'Independent browser/reader witness and real consent/rights qualification'
    }
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graph',type=Path,default=Path('ai/comap-source-projection-r0.json'))
    p.add_argument('--schema',type=Path,default=Path('schemas/coevo-delta-v0.1.schema.json'))
    p.add_argument('--output',type=Path,default=Path('cosysall_r1_receipt.json'))
    a=p.parse_args()
    try:
        result=run(a.graph,a.schema,a.output)
    except (Held,AssertionError) as err:
        p.exit(2,'HOLD: '+str(err)+'\n')
    print(json.dumps(result,indent=2))