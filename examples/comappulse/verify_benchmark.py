#!/usr/bin/env python3
"""Verify CoMapPulse R0 append-only event chain with pinned digest.

Integrity check only, not author authentication, scientific truth or receiver ACK.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent

def no_dups(pairs):
    obj={}
    for key,val in pairs:
        if key in obj: raise ValueError('DUPLICATE_KEY')
        obj[key]=val
    return obj

def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def verify(path=None,head_path=None):
    path=path or ROOT/'benchmark_evo.jsonl'
    head_path=head_path or ROOT/'HEAD.sha256'
    prev='0'*64; counter={'PASS':0,'FAIL':0,'HOLD':0,'NOT_RUN':0}
    lines=Path(path).read_text(encoding='utf-8').splitlines()
    if not lines: raise ValueError('EMPTY_LEDGER')
    for i,line in enumerate(lines,1):
        evt=json.loads(line,object_pairs_hook=no_dups)
        if evt.get('schema')!='CoBenchmarkEvoEvent/1' or evt.get('seq')!=i: raise ValueError('BAD_SCHEMA_OR_SEQUENCE')
        if evt.get('prev_hash')!=prev: raise ValueError('BROKEN_CHAIN')
        if evt.get('status') not in counter: raise ValueError('BAD_STATUS')
        if evt.get('event_hash')!=digest({k:v for k,v in evt.items() if k!='event_hash'}): raise ValueError('BAD_EVENT_HASH')
        counter[evt['status']]+=1;prev=evt['event_hash']
    if prev!=Path(head_path).read_text(encoding='utf-8').strip(): raise ValueError('WRONG_HEAD')
    return {'events':len(lines),'head':prev,'counts':counter,'meaning':'Receipt integrity only. No external ACK or scientific truth implied.'}

if __name__=='__main__': print(json.dumps(verify(),indent=2))
