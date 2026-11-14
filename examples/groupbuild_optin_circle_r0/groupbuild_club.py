#!/usr/bin/env python3
"""GroupBuild synthetic opt-in matching, not a member database or sender."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import date
from itertools import combinations
from pathlib import Path

SCHEMA = 'GroupBuild.OptInCircle.PublicSynthetic.R0'
ROLES = ('consent_safety', 'independent_relevance', 'accessibility')
SAFE_SCOPE = 'PROJECT_CONTEXT_ONLY'
MAX_MEMBERS = 32
MAX_TAGS = 12


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(',', ':')) + '\n').encode('utf-8')


def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def validate(data):
    if not isinstance(data, dict) or set(data) != {'schema','as_of','circle','members','suppressions'}:
        raise ValueError('HOLD_SCHEMA')
    if data['schema'] != SCHEMA: raise ValueError('HOLD_SCHEMA')
    today = date.fromisoformat(data['as_of'])
    circle = data['circle']
    if set(circle) != {'id','purpose','moderator','status','affiliation_disclosed','public_signup_open'}:
        raise ValueError('HOLD_CIRCLE')
    if circle['status'] != 'SYNTHETIC_CANDIDATE' or circle['public_signup_open'] is not False or circle['affiliation_disclosed'] is not True:
        raise ValueError('HOLD_FALSE_PUBLIC_CLUB')
    members = data['members']
    if not isinstance(members,list) or not (2<=len(members)<=MAX_MEMBERS):raise ValueError('HOLD_MEMBER_LIMIT')
    ids=set()
    for m in members:
        if not isinstance(m,dict) or set(m) != {'id','synthetic','club_opt_in','offers','needs','topics','intro_consents'}:
            raise ValueError('HOLD_MEMBER_SCHEMA')
        mid=m['id']
        if not isinstance(mid,str) or not mid.startswith('test-') or mid in ids:
            raise ValueError('HOLD_ID_OR_DUPLICATE')
        ids.add(mid)
        if m['synthetic'] is not True or not isinstance(m['club_opt_in'],bool):
            raise ValueError('HOLD_REAL_PERSON')
        for key in ['offers','needs','topics']:
            vals=m[key]
            if not isinstance(vals,list) or len(vals)>MAX_TAGS or len(vals)!=len(set(vals)):
                raise ValueError('HOLD_TAGS')
            if any(not isinstance(v,str) or len(v)>32 or len(v)<3 or not all(c.islower() or c.isdigit() or c=='-' for c in v) for v in vals):
                raise ValueError('HOLD_PRIVATE_OR_UNSAFE_TAGS')
        if not isinstance(m['intro_consents'],list):raise ValueError('HOLD_CONSENT_SCHEMA')
        seen=set()
        for c in m['intro_consents']:
            if not isinstance(c,dict) or set(c)!={'partner_id','scope','expires_on','revoked'}:
                raise ValueError('HOLD_CONSENT_SCHEMA')
            if c['partner_id'] in seen or c['scope']!=SAFE_SCOPE or not isinstance(c['revoked'],bool):
                raise ValueError('HOLD_CONSENT_SCOPE')
            date.fromisoformat(c['expires_on'])
            seen.add(c['partner_id'])
    if not isinstance(data['suppressions'],list) or any(k not in ids for k in data['suppressions']):
        raise ValueError('HOLD_SUPPRESSION_SCHEMA')
    if len(data['suppressions'])!=len(set(data['suppressions'])):raise ValueError('HOLD_SUPPRESSION_DUPLICATE')
    for m in members:
        if any(c['partner_id'] not in ids or c['partner_id']==m['id'] for c in m['intro_consents']):
            raise ValueError('HOLD_CONSENT_TARGET')
    return today


def active_consent(m,other_id,today):
    return any(c['partner_id']==other_id and c['scope']==SAFE_SCOPE and c['revoked'] is False and date.fromisoformat(c['expires_on'])>=today for c in m['intro_consents'])


def propose(data):
    today=validate(data)
    members=sorted(data['members'],key=lambda m:m['id'])
    pairs=[]
    for a,b in combinations(members,2):
        a_to_b=sorted(set(a['offers']) & set(b['needs']))
        b_to_a=sorted(set(b['offers']) & set(a['needs']))
        # Relevance is offered help for stated needs, not a psychographic predictor.
        if not a_to_b or not b_to_a:continue
        topics=sorted(set(a['topics']) & set(b['topics']))
        held=[]
        if a['id'] in data['suppressions'] or b['id'] in data['suppressions']:held.append('DO_NOT_CONTACT')
        if not a['club_opt_in'] or not b['club_opt_in']:held.append('NOT_CLUB_MEMBER')
        if not active_consent(a,b['id'],today):held.append('A_INTRO_CONSENT_MISSING')
        if not active_consent(b,a['id'],today):held.append('B_INTRO_CONSENT_MISSING')
        if not topics:held.append('NO_SHARED_PROJECT_TOPIC')
        pair_id=hashlib.sha256((sha(data)+':'+a['id']+':'+b['id']).encode()).hexdigest()[:20]
        pairs.append({'pair_id':pair_id,'member_ids':[a['id'],b['id']],
          'why_a_could_help_b':a_to_b,'why_b_could_help_a':b_to_a,'shared_chosen_topics':topics,
          'state':'SHADOW_READY_FOR_REVIEW_NOT_SENT' if not held else 'HELD',
          'hold_reasons':held,'intro_sent':False,'identities_revealed':False,
          'expected_effort':'UNMEASURED','participant_acceptance':'UNPROVEN',
          'review_panel':{role:'NOT_ACTUALLY_ASSIGNED' for role in ROLES},
          'review_round_cap':2,'authority':'NONE'})
    return {'schema':'GroupBuild.OptInCircle.ShadowReport.R0','source_sha256':sha(data),
      'circle_id':data['circle']['id'],'status':'SYNTHETIC_SHADOW_ONLY_NO_REAL_CLUB',
      'pair_count':len(pairs),'ready_for_review':sum(x['state'].startswith('SHADOW_READY') for x in pairs),
      'pairs':pairs,'sent':0,'real_members':0,'staffed_reviewers':0,'external_effects':0,
      'metrics_for_later_real_canary':['consent_to_introduction_rate','first_useful_joint_task_completion','receiver_origin_readproof','participant_effort_minutes','coordination_minutes','unwanted_contact_count','opt_out_friction','reviewer_independence','baseline_comparison','return_visit'],
      'rails':['CANDIDATE_NE_MEMBER','MATCH_NE_INTRODUCTION','CLUB_OPT_IN_NE_INTRO_CONSENT','NO_INFERRED_RELATIONSHIPS','NO_UNSOLICITED_DISCLOSURE','SIMULATED_REVIEW_NE_STAFFED_PANEL','NO_PRIVATE_CONTACT_GRAPH','NOT_SENT_NE_DELIVERED','NO_REAL_CLUB_RUNTIME']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,default=Path(__file__).with_name('fixture.json'));p.add_argument('--output',type=Path);a=p.parse_args()
    report=propose(json.loads(a.fixture.read_text(encoding='utf-8')))
    out=canonical(report)
    if a.output:
        with a.output.open('xb') as f:f.write(out)
        if a.output.read_bytes()!=out:raise RuntimeError('HOLD_READBACK')
        print(hashlib.sha256(out).hexdigest())
    else:print(out.decode('utf-8'),end='')

if __name__=='__main__':main()
