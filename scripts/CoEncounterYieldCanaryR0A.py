#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

YIELD_TYPES={
"ORIENTATION_EVIDENCE","INTERPRETABILITY_EVIDENCE","USABILITY_FRICTION","QUESTION","CHALLENGE","CONTRADICTION","CAPABILITY_EVIDENCE","PROVENANCE","TRANSLATION","NOVELTY_CANDIDATE","NEGATIVE_KNOWLEDGE","BENEFIT_OBSERVATION","FUTURE_RELATION","EVIDENCED_NULL"
}
LOW_AUTH={"OBSERVE_ONLY","OBSERVE_AND_PROPOSE_ONLY"}
ATTR={"ORIGINATED_BY","NOTICED_BY","CHALLENGED_BY","REPAIRED_BY","TRANSLATED_BY","VERIFIED_BY","IMPLEMENTED_BY","REMIXED_BY","INDEPENDENTLY_REDISCOVERED_BY"}

def sha256(b:bytes)->str: return hashlib.sha256(b).hexdigest().upper()

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--fixture',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    fp=Path(a.fixture).resolve(); out=Path(a.output).resolve()
    if out.exists(): raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")
    raw=fp.read_bytes(); pack=json.loads(raw.decode('utf-8'))
    es=pack.get('encounters');
    if not isinstance(es,list) or len(es)!=3: raise SystemExit('FAIL_CLOSED__EXPECTED_THREE_ENCOUNTERS')
    ids=set(); modes=set(); classes=set(); contribution_count=0; benefit_count=0; null_count=0; wake_unauthorized=0
    for i,e in enumerate(es):
        req=['encounter_id','observed_at','participant_binding','participant_class','source_object_refs','encounter_mode','yields','authority_ceiling','confidentiality','contribution_delta_refs','open_relations','benefit_observations','wake_relations','next_receiver','nonclaims']
        missing=[k for k in req if k not in e]
        if missing: raise SystemExit(f"FAIL_CLOSED__MISSING_FIELDS_{i}={'/'.join(missing)}")
        eid=e['encounter_id']
        if eid in ids: raise SystemExit('FAIL_CLOSED__DUPLICATE_ENCOUNTER_ID')
        ids.add(eid); modes.add(e['encounter_mode']); classes.add(e['participant_class'])
        if e['authority_ceiling'] not in LOW_AUTH: raise SystemExit(f"FAIL_CLOSED__AUTHORITY_INFLATION={eid}")
        if e['confidentiality']!='PUBLIC': raise SystemExit(f"FAIL_CLOSED__NONPUBLIC_FIXTURE={eid}")
        ys=e['yields']
        if not isinstance(ys,list) or not ys: raise SystemExit(f"FAIL_CLOSED__NO_YIELD={eid}")
        for y in ys:
            if y.get('yield_type') not in YIELD_TYPES: raise SystemExit(f"FAIL_CLOSED__YIELD_TYPE={eid}")
        contribution_count += len(e['contribution_delta_refs'])
        for b in e['benefit_observations']:
            benefit_count += 1
            if 'counterfactual_confidence' not in b or 'attribution_uncertainty' not in b: raise SystemExit('FAIL_CLOSED__BENEFIT_CAUSAL_DISCIPLINE_MISSING')
        for ar in e.get('attribution_relations',[]):
            if ar.get('relation') not in ATTR: raise SystemExit('FAIL_CLOSED__ATTRIBUTION_TYPE')
        for wr in e['wake_relations']:
            if wr.get('participant_notification_authorized') is False:
                wake_unauthorized += 1
                if wr.get('communication_route_ref') is not None: raise SystemExit('FAIL_CLOSED__UNAUTHORIZED_NOTIFICATION_ROUTE')
        if e['encounter_mode']=='EVIDENCED_NULL':
            null_count += 1
            if e['contribution_delta_refs']: raise SystemExit('FAIL_CLOSED__NULL_WITH_CONTRIBUTION')
            if not any(y.get('yield_type')=='EVIDENCED_NULL' for y in ys): raise SystemExit('FAIL_CLOSED__NULL_WITHOUT_NULL_YIELD')
    if 'TEST' not in modes or 'CHALLENGE' not in modes or 'EVIDENCED_NULL' not in modes: raise SystemExit('FAIL_CLOSED__MODE_COVERAGE')
    if contribution_count!=1: raise SystemExit('FAIL_CLOSED__EXPECTED_ONE_CONTRIBUTION_CANDIDATE')
    if benefit_count!=1: raise SystemExit('FAIL_CLOSED__EXPECTED_ONE_BENEFIT_OBSERVATION')
    if null_count!=1: raise SystemExit('FAIL_CLOSED__EXPECTED_ONE_EVIDENCED_NULL')
    report={
      'schema':'CoEncounterYieldCanary.R0A.v0.1',
      'state':'PASS_R0A_MULTI_RECEIVER_ENCOUNTER_YIELD__NONMUTATING_VALUE__BOUNDED_CONTRIBUTION__EVIDENCED_NULL__NO_AUTHORITY_INFLATION',
      'fixture_sha256':sha256(raw),
      'coverage':{'encounters':len(es),'participant_classes':sorted(classes),'modes':sorted(modes),'contribution_candidates':contribution_count,'benefit_observations':benefit_count,'evidenced_null_encounters':null_count,'unauthorized_notification_relations_held':wake_unauthorized},
      'checks':{'nonmutating_interpretability_evidence':True,'bounded_contribution_candidate':True,'evidenced_null_preserved':True,'benefit_counterfactual_discipline':True,'typed_attribution':True,'authority_not_increased_by_participation':True,'no_notification_route_without_authorization':True},
      'effects':{'repo_mutations':0,'participant_notifications':0,'authority_changes':0,'provider_session_mutations':0},
      'next':'R0B_INDEPENDENT_RECEIVER_REVIEW_OF_ENCOUNTER_YIELD_AND_OPEN_RELATION_ROUTING',
      'nonclaims':['VALIDATION_IS_NOT_ACCEPTANCE','ENCOUNTER_YIELD_NE_TRUTH','BENEFIT_OBSERVED_NE_BENEFIT_CAUSED','SENSING_SCALE_NE_AUTHORITY_SCALE','LOCAL_CANARY_NE_RUNTIME_INTEGRATION','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF']
    }
    out.parent.mkdir(parents=True,exist_ok=True); enc=(json.dumps(report,indent=2)+"\n").encode(); out.write_bytes(enc)
    print(json.dumps({'STATE':report['state'],'OUTPUT':str(out),'OUTPUT_SHA256':sha256(enc),'FIXTURE_SHA256':report['fixture_sha256'],'ENCOUNTERS':3,'NEXT':report['next']},separators=(',',':')))
    return 0

if __name__=='__main__': raise SystemExit(main())
