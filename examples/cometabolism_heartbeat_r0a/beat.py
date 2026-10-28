#!/usr/bin/env python3
"""Pure CoMetabolism heartbeat selector. Synthetic, no processes, IO or sends."""
import argparse, hashlib, json
from pathlib import Path

WEIGHT={'PRESSURE':90,'ACK_GAP':75,'SOURCE_DELTA':60,'NEW_EVIDENCE':30}
def stable(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def hashof(v):return hashlib.sha256(stable(v).encode()).hexdigest()

def elect(objects,events,policy):
    by={o['id']:o for o in objects}
    if len(by)!=len(objects):raise ValueError('duplicate object identity')
    if policy['budget']<policy['reserve'] or policy['width']<0:raise ValueError('invalid policy')
    seen,plans,held,observed={},{},[],[]
    signatures={}
    for event in events:signatures.setdefault(event['eid'],set()).add(hashof(event))
    collisions={eid for eid,values in signatures.items() if len(values)>1}
    stopped={e['obj'] for e in events if e['kind']=='STOP' and e.get('scope')=='READ_ONLY' and e.get('evidence')=='SYNTHETIC_VERIFIED' and e['obj'] in by and by[e['obj']]['privacy']=='PUBLIC' and e.get('privacy')==by[e['obj']]['privacy']}
    for e in sorted(events,key=lambda x:(x['seq'],x['eid'])):
        eid=e['eid']; fingerprint=hashof(e)
        if eid in collisions:
            held.append({'eid':eid,'why':'ID_COLLISION_NO_DISPATCH'});continue
        if eid in seen:
            state='REPLAY_DEDUPED' if seen[eid]==fingerprint else 'ID_COLLISION_HELD'
            observed.append({'eid':eid,'state':state});continue
        seen[eid]=fingerprint
        o=by.get(e['obj'])
        if not o:held.append({'eid':eid,'why':'UNKNOWN_OBJECT'});continue
        if o['privacy']!='PUBLIC' or e.get('privacy')!=o['privacy'] or e.get('scope')!='READ_ONLY':
            held.append({'eid':eid,'why':'AUTHORITY_OR_PRIVACY'});continue
        if e['kind']=='STOP': observed.append({'eid':eid,'state':'STOP_OBSERVED','obj':o['id']});continue
        if o['id'] in stopped:held.append({'eid':eid,'why':'STOPPED'});continue
        if e.get('depth',0)>2 or e.get('round',0)>2:
            held.append({'eid':eid,'why':'TURTLE_BUDGET'});continue
        if e.get('evidence')!='SYNTHETIC_VERIFIED':
            held.append({'eid':eid,'why':'UNVERIFIED'});continue
        k=e['kind']
        if k=='LEASE_BEAT':
            status=('SYNTHETIC_LEASE_FRESH' if e.get('last_tick',-1)+o['ttl']>=policy['tick'] else 'LEASE_STALE_RUNTIME_UNKNOWN')
            observed.append({'eid':eid,'state':status,'obj':o['id']});continue
        if k=='SOURCE_DELTA' and not isinstance(e.get('new_hash'),str):
            held.append({'eid':eid,'why':'MISSING_SOURCE_HASH'});continue
        if k=='SOURCE_DELTA' and e.get('new_hash')==o['source_hash']:
            observed.append({'eid':eid,'state':'NO_SOURCE_CHANGE','obj':o['id']});continue
        if k=='NEW_EVIDENCE' and o['epistemic'] in ('SYMBOLIC','HYPOTHESIS') and e.get('watts',0):
            held.append({'eid':eid,'why':'HYPOTHESIS_NOT_WATTS'});continue
        if k not in WEIGHT:held.append({'eid':eid,'why':'UNKNOWN_KIND'});continue
        if k=='NEW_EVIDENCE' and o['epistemic'] not in ('SYMBOLIC','HYPOTHESIS'):
            held.append({'eid':eid,'why':'INCOMPATIBLE_TYPE'});continue
        cost=e.get('cost',1)
        if cost<0:held.append({'eid':eid,'why':'INVALID_COST'});continue
        plan={'eid':eid,'obj':o['id'],'kind':k,'action':{'PRESSURE':'INSPECT_READ_ONLY','ACK_GAP':'CHECK_RECEIVER_PROOF','SOURCE_DELTA':'REVIEW_SOURCE_VERSION','NEW_EVIDENCE':'CHALLENGE_HYPOTHESIS'}[k],
              'cost':cost,'priority':WEIGHT[k],'result':'PROPOSAL_ONLY','source_hash':o['source_hash']}
        plans.setdefault(o['id'],[]).append(plan)
    candidates=[]
    for obj, xs in plans.items():
        xs.sort(key=lambda x:(-x['priority'],x['eid']));candidates.append(xs[0])
        held.extend({'eid':x['eid'],'why':'DUPLICATE_OBJECT_WAVE'} for x in xs[1:])
    candidates.sort(key=lambda x:(-x['priority'],x['eid']))
    remaining=policy['budget']-policy['reserve']; selected=[]
    for p in candidates:
        if len(selected)>=policy['width']:held.append({'eid':p['eid'],'why':'WIDTH_CAP'})
        elif p['cost']>remaining:held.append({'eid':p['eid'],'why':'BUDGET_RESERVE'})
        else:selected.append(p);remaining-=p['cost']
    result={'schema':'CoAll.CoMetabolism.BeatShadow.R0A','state':'SYNTHETIC_ONLY_NO_LIVE_BUS',
      'selected':selected,'held':sorted(held,key=lambda x:(x['eid'],x['why'])),
      'observed':sorted(observed,key=lambda x:(x['eid'],x['state'])),
      'budget':{'initial':policy['budget'],'reserved':policy['reserve'],'remaining_above_reserve':remaining},
      'effects':{'network':0,'os':0,'external_send':0,'process_spawn':0},
      'limits':['BEAT_NE_BENEFIT','STALE_NE_DEAD','ADDRESSABLE_NE_RUNNING','HYPOTHESIS_NE_ENERGY','NO_X2_HEALTH_OBSERVATION','NO_AUTONOMOUS_LOOP']}
    result['receipt_digest']=hashof(result);return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--output',type=Path)
    a=p.parse_args();j=json.loads(a.fixture.read_text());result=elect(j['objects'],j['events'],j['policy']);text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if a.output:
        with a.output.open('x',encoding='utf-8') as f:f.write(text)
    else:print(text,end='')
if __name__=='__main__':main()
