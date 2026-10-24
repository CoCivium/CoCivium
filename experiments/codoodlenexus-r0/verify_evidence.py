#!/usr/bin/env python3
"""Verify the hash-linked local CoDoodleNexus ledger; hash chain != signature."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def strict_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('DUPLICATE_KEY')
        out[k]=v
    return out

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=True,
                     separators=(',',':'),allow_nan=False).encode('ascii')).hexdigest()

def verify(lines,head):
    prior='0'*64
    if not lines:raise ValueError('EMPTY_LEDGER')
    for ix,line in enumerate(lines,1):
        row=json.loads(line,object_pairs_hook=strict_pairs)
        if row.get('schema')!='CoDoodleNexus.Receipt.R0':raise ValueError('BAD_SCHEMA')
        if row.get('seq')!=ix:raise ValueError('BAD_SEQUENCE')
        if row.get('prev_hash')!=prior:raise ValueError('BROKEN_LINK')
        if row.get('event_hash')!=digest({k:v for k,v in row.items() if k!='event_hash'}):
            raise ValueError('BAD_EVENT_HASH')
        prior=row['event_hash']
    if prior!=head:raise ValueError('HEAD_MISMATCH')
    return {'status':'PASS_CHAIN_INTEGRITY_ONLY','events':len(lines),'head':prior}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--ledger',type=Path,default=ROOT/'output/benchmark_evo.jsonl')
    p.add_argument('--head',type=Path,default=ROOT/'output/HEAD.sha256')
    args=p.parse_args()
    print(json.dumps(verify(args.ledger.read_text(encoding='utf-8').splitlines(),
                            args.head.read_text(encoding='utf-8').strip()),sort_keys=True))
if __name__=='__main__':main()
