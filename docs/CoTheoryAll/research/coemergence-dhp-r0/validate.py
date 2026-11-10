#!/usr/bin/env python3
"""Source-level CoEmergence/DhP card validation; no credential, runtime, or human outcome claims."""
from pathlib import Path
import copy, json, sys

def validate(obj):
    cards=obj.get('cards',[])
    relations=obj.get('relations',[])
    ids=[c.get('id') for c in cards]
    public_keys={p.get('key') for p in obj.get('source_catalog',[])}
    required=['id','title','lane','epistemic_type','status','proposal','strongest_rival','baseline',
      'discriminator_or_challenge','failure_or_stop_condition','potential_receiver_benefit','nonclaim',
      'authority_ceiling','review_state','source_refs','source_gaps','credential_issued']
    checks={
      'schema_matches':obj.get('schema')=='CoEmergence.CoDhP.EvidenceFirstResearchBatch.R0',
      'cards_12':len(cards)==12,
      'relations_20':len(relations)==20,
      'unique_nonempty_ids':len(ids)==len(set(ids)) and all(ids),
      'required_fields':all(all(k in c and c[k] is not None and c[k]!='' for k in required) for c in cards),
      'all_cards_research_only':all(c.get('authority_ceiling')=='RESEARCH_ONLY_NO_EXTERNAL_EFFECT' for c in cards),
      'no_credential_issued':obj.get('proof_boundary',{}).get('credentials_issued')==0 and all(c.get('credential_issued') is False for c in cards),
      'no_review_claim':all(c.get('review_state')=='INDEPENDENT_REVIEW_NOT_DONE' for c in cards),
      'candidate_status_only':all(c.get('status')=='RESEARCH_CANDIDATE_NOT_VALIDATED' for c in cards),
      'source_refs_public_or_explicit_gaps':all((c.get('source_refs') or c.get('source_gaps')) and all(k in public_keys for k in c.get('source_refs',[])) for c in cards),
      'typed_noncausal_relations':all(r.get('relation_type') not in ('',None,'RELATES_TO') and r.get('status')=='PROPOSED_TYPED_RELATION_NOT_OBSERVED_CAUSALITY' and r.get('authority')=='NONE' for r in relations),
      'relation_targets_exist':all(r.get('from') in ids and r.get('to') in ids for r in relations),
    }
    return checks

def perturb(base,change):
    a=copy.deepcopy(base)
    c=a['cards'];e=a['relations']
    if change==0:c[0]['credential_issued']=True
    if change==1:c[0]['status']='PROVEN'
    if change==2:e[0]['to']='NONEXISTENT_CARD'
    if change==3:c[0]['authority_ceiling']='GOD_WANTS_THIS'
    if change==4:c[0]['review_state']='INSTITUTIONAL_PEER_REVIEW_PASS'
    if change==5:e[0]['authority']='OPERATE'
    if change==6:e[0]['relation_type']='RELATES_TO'
    if change==7:c[1]['id']=c[0]['id']
    return a

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('research_cards.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    checks=validate(data)
    negatives=[]
    for n in range(8):
        test=validate(perturb(data,n))
        negatives.append({'case':n+1,'rejected':not all(test.values()),'failed_checks':[k for k,v in test.items() if not v]})
    report={'schema':data['schema'],'work_id':data['work_id'],
      'status':'SOURCE_FIXTURE_ONLY__NOT_HUMAN_EXPERIMENT',
      'passed_structural_checks':sum(checks.values()),'total_structural_checks':len(checks),
      'rejected_seeded_invalid_cases':sum(x['rejected'] for x in negatives),'total_invalid_cases':len(negatives),
      'checks':checks,'negative_controls':negatives,
      'not_measured':['human reader accuracy','originality','utility vs well-designed Markdown','independent peer review','diploma or credential conferral','runtime adoption']}
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if all(checks.values()) and all(x['rejected'] for x in negatives) else 1
if __name__=='__main__':raise SystemExit(main())