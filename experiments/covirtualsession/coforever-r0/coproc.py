#!/usr/bin/env python3
"""CoForever/CoOrbWare R0: bounded *demonstration*, never a daemon or effects controller."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = 'CoAll.CoProcessField.R0.candidate'
CHECKPOINT_SCHEMA = 'CoAll.CoProcessField.Checkpoint.v1'
AXES = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
DIGITS = 20
LOGICAL_SPACE = 16**DIGITS
MAX_ACTIVE = 2
MAX_TOUCH = 40
MAX_DEPTH = 2
SOURCE = {'schema':SCHEMA,'axes':AXES,'digits':DIGITS,'max_active':MAX_ACTIVE,'max_touch':MAX_TOUCH,'max_depth':MAX_DEPTH,'effect_authority':'NONE'}

def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('utf-8')

def digest(x):
    return hashlib.sha256(x if isinstance(x,bytes) else canonical(x)).hexdigest()

SPEC_SHA256 = digest(SOURCE)

def address(rank):
    if type(rank) is not int or not (0<=rank<LOGICAL_SPACE):
        raise ValueError('OUT_OF_BOUNDS')
    return format(rank,'020x')

def unaddress(s):
    if not isinstance(s,str) or len(s)!=DIGITS or any(c not in AXES for c in s):
        raise ValueError('INVALID_ADDRESS')
    return int(s,16)

def task(rank, priority=0, submitted=0, wake=0, privacy='PUBLIC_SYNTHETIC', depth=0, effect='NONE', source='PUBLIC_FIXTURE'):
    ident='vs-'+address(rank)
    return {'id':ident,'rank':rank,'priority':priority,'submitted':submitted,'wake':wake,
            'privacy':privacy,'depth':depth,'effect':effect,'source':source,
            'source_sha256':digest({'source':source,'rank':rank}),
            'state':'WAITING','lease':None,'receipt':None}

def valid(t):
    if not isinstance(t,dict) or set(t)!={'id','rank','priority','submitted','wake','privacy','depth','effect','source','source_sha256','state','lease','receipt'}:
        raise ValueError('INVALID_FIELDS')
    if t['id']!='vs-'+address(t['rank']) or t['source_sha256']!=digest({'source':t['source'],'rank':t['rank']}):
        raise ValueError('BAD_ID_OR_SOURCE')
    if any(type(t[z]) is not int or t[z]<0 for z in ['priority','submitted','wake','depth']):
        raise ValueError('INVALID_NUMERIC')
    if t['privacy'] not in ('PUBLIC_SYNTHETIC','PRIVATE','UNKNOWN'):
        raise ValueError('UNKNOWN_PRIVACY')
    if t['effect'] not in ('NONE','EXTERNAL'):
        raise ValueError('INVALID_EFFECT')
    if t['state'] not in ('WAITING','HELD','LEASED_SIMULATED','COMPLETE_SIMULATED'):
        raise ValueError('INVALID_STATE')
    return True

def empty():
    return {'schema':SCHEMA,'spec_sha256':SPEC_SHA256,'logical_space':str(LOGICAL_SPACE),
            'tick':0,'tasks':{},'events':[], 'effect_authority':'NONE','receiver_ack':'UNPROVEN'}

def admit(state,t):
    valid(t)
    if state.get('spec_sha256') != SPEC_SHA256:
        raise ValueError('SPEC_CHANGED')
    if len(state['tasks']) >= MAX_TOUCH and t['id'] not in state['tasks']:
        return 'TOUCH_BUDGET_HOLD'
    before=state['tasks'].get(t['id'])
    if before:
        return 'IDEMPOTENT' if before['source_sha256']==t['source_sha256'] else 'COLLISION_HOLD'
    candidate=t.copy()
    if candidate['effect']!='NONE' or candidate['depth']>MAX_DEPTH or candidate['privacy']=='UNKNOWN':
        candidate['state']='HELD'
    state['tasks'][t['id']]=candidate
    state['events'].append({'kind':'ADMITTED','id':t['id'],'tick':state['tick']})
    return 'ADMITTED'

def feasible(t,tick):
    if t['state']!='WAITING': return False
    if t['privacy']!='PUBLIC_SYNTHETIC' or t['effect']!='NONE' or t['depth']>MAX_DEPTH: return False
    return t['wake']<=tick

def rank_score(t,tick):
    # Aging avoids permanent starvation from a stream of recently admitted high-priority tasks.
    return min(t['priority'],4) + min(100, max(0,tick-t['submitted'])//2)

def elect(state,tick,pressure='LOW'):
    if type(tick) is not int or tick<state['tick']: raise ValueError('CLOCK_REGRESSION')
    if pressure not in ('LOW','MEDIUM','HIGH'): raise ValueError('INVALID_PRESSURE')
    state['tick']=tick
    permitted={'LOW':MAX_ACTIVE,'MEDIUM':1,'HIGH':0}[pressure]
    active=sum(1 for t in state['tasks'].values() if t['state']=='LEASED_SIMULATED')
    slots=max(0, permitted-active)
    eligible=sorted((t for t in state['tasks'].values() if feasible(t,tick)),
                    key=lambda t:(-rank_score(t,tick),t['submitted'],t['rank']))[:slots]
    for t in eligible:
        t['state']='LEASED_SIMULATED'
        t['lease']={'tick':tick,'until':tick+2,'proof':'SYNTHETIC_ONLY','receipt':'NOT_YET'}
        state['events'].append({'kind':'LEASED_SIMULATED','id':t['id'],'tick':tick})
    return [t['id'] for t in eligible]

def finish(state,tid,tick):
    t=state['tasks'].get(tid)
    if t is None or t['state']!='LEASED_SIMULATED' or tick>t['lease']['until']:
        raise ValueError('NO_VALID_LEASE')
    t['state']='COMPLETE_SIMULATED'
    t['receipt']={'id':digest({'task':tid,'spec':SPEC_SHA256}),'source_sha256':t['source_sha256'],
                  'outcome':'SIMULATED_ONLY','receiver_ack':'UNPROVEN','external_effects':0}
    t['lease']=None
    state['events'].append({'kind':'COMPLETED_SIMULATED','id':tid,'tick':tick})

def reap(state,tick):
    if tick<state['tick']:raise ValueError('CLOCK_REGRESSION')
    state['tick']=tick
    restored=[]
    for t in state['tasks'].values():
        if t['state']=='LEASED_SIMULATED' and tick>t['lease']['until']:
            t['state']='WAITING';t['lease']=None
            restored.append(t['id'])
            state['events'].append({'kind':'EXPIRED_NO_ACK_RETRYABLE','id':t['id'],'tick':tick})
    return restored

def checkpoint(state):
    if state.get('spec_sha256')!=SPEC_SHA256 or state.get('receiver_ack')!='UNPROVEN' or state.get('effect_authority')!='NONE':
        raise ValueError('CHECKPOINT_AUTHORITY_OR_SPEC')
    if len(state['tasks'])>MAX_TOUCH or len(state['events'])>MAX_TOUCH*10: raise ValueError('CHECKPOINT_TOO_LARGE')
    for t in state['tasks'].values():valid(t)
    payload={'schema':CHECKPOINT_SCHEMA,'spec_sha256':SPEC_SHA256,'state':state}
    return {'payload':payload,'sha256':digest(payload)}

def recover(cp):
    if not isinstance(cp,dict) or set(cp)!={'payload','sha256'} or cp['sha256']!=digest(cp['payload']):
        raise ValueError('TAMPERED_CHECKPOINT')
    if cp['payload'].get('schema')!=CHECKPOINT_SCHEMA or cp['payload'].get('spec_sha256')!=SPEC_SHA256:
        raise ValueError('STALE_NAMESPACE')
    # Deep copy, so resume cannot mutate its own historical checkpoint witness.
    state=json.loads(json.dumps(cp['payload']['state']))
    checkpoint(state)
    return state

def public_orb(state):
    if state.get('receiver_ack')!='UNPROVEN':raise ValueError('FALSE_ACK')
    safe=[t for t in state['tasks'].values() if t['privacy']=='PUBLIC_SYNTHETIC' and t['effect']=='NONE']
    # A public view cannot disclose even the COUNT of hidden private tasks.
    tiles=[]
    for t in sorted(safe,key=lambda a:a['rank']):
        tiles.append({'id':t['id'],'state':t['state'],'priority':t['priority'],
                      'evidence':'SYNTHETIC_ONLY','receiver_ack':'UNPROVEN',
                      'source_sha256':t['source_sha256']})
    return {'schema':'CoOrbWare.CandidateProjection.R0','spec_sha256':SPEC_SHA256,
            'logical_options':str(LOGICAL_SPACE),'observed_working_set':len(tiles),
            'tiles':tiles,'currentness':'BOUNDED_SNAPSHOT','execution':'NO_LIVE_WORKERS_FROM_ORB',
            'effect_authority':'NONE','receiver_ack':'UNPROVEN','hidden_counts':None,
            'comment':'This is a deterministic local dry-run. No live desktop service.'}

def worker(nonce):
    if not isinstance(nonce,str) or len(nonce)!=20 or any(c not in AXES for c in nonce):
        raise ValueError('INVALID_NONCE')
    # Short deterministic local computation, no network, no credentials.
    value=nonce.encode('ascii')
    for _ in range(5000):value=hashlib.sha256(value).digest()
    time.sleep(.08)
    return {'nonce':nonce,'result_sha256':value.hex(),'class':'LOCAL_ONLY_SYNTHETIC','receiver_ack':'UNPROVEN'}

def live_probe(count=4,cap=2):
    if not isinstance(count,int) or not 1<=count<=8 or cap not in (1,2):raise ValueError('PROBE_BOUNDS')
    queue=[address(i*87+3) for i in range(count)]
    children=[];receipts=[];peak=0;launched=0
    started=time.monotonic()
    try:
        while queue or children:
            while queue and len(children)<cap:
                nonce=queue.pop(0)
                p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'worker',nonce],
                     stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
                children.append((p,nonce));launched+=1
                peak=max(peak,len(children))
            new=[]
            for p,nonce in children:
                if p.poll() is None:
                    new.append((p,nonce));continue
                out,err=p.communicate(timeout=1)
                if p.returncode!=0:raise RuntimeError('WORKER_FAIL '+err[:100])
                v=json.loads(out)
                if v['nonce']!=nonce or v['result_sha256']!=worker_digest(nonce):raise RuntimeError('WORKER_MISMATCH')
                receipts.append({'nonce':nonce,'result_sha256':v['result_sha256'],'observed_exit_code':p.returncode,
                                 'evidence':'CHILD_PROCESS_COMPLETED_ON_THIS_HOST'})
            children=new
            if time.monotonic()-started>8:raise TimeoutError('PROBE_DEADLINE')
            time.sleep(.01)
    finally:
        for p,_ in children:
            if p.poll() is None:p.kill()
            p.communicate(timeout=1)
    return {'launched':launched,'completed':len(receipts),'peak_parent_observed_processes':peak,
            'remaining_children':len(children),'duration_ms':round((time.monotonic()-started)*1000,3),
            'receipts':receipts,'scope':'SAME_HOST_FINITE_SUBPROCESSES_ONLY','provider_calls':0,'external_effects':0}

def worker_digest(nonce):
    v=nonce.encode('ascii')
    for _ in range(5000):v=hashlib.sha256(v).digest()
    return v.hex()

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='worker':
        print(json.dumps(worker(sys.argv[2]),sort_keys=True))
    else: raise SystemExit('use: python coproc.py worker <20-hex-synthetic-nonce>')