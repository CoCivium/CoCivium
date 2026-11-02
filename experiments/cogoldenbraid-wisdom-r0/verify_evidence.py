#!/usr/bin/env python3
"""Verify pinned local ledger. Hash chains do not authenticate authors or scientific truth."""
import json
from pathlib import Path
from braid import ROOT, digest

def strict_keys(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError('DUPLICATE_KEY')
        out[k]=v
    return out

def verify(lines, expected):
    prev='0'*64
    if not lines:raise ValueError('EMPTY_LEDGER')
    for i,line in enumerate(lines,1):
        obj=json.loads(line,object_pairs_hook=strict_keys)
        if obj.get('schema')!='CoGoldenBraidEvidenceEvent/0.1': raise ValueError('INVALID_SCHEMA')
        if obj.get('seq')!=i or obj.get('prev_hash')!=prev:raise ValueError('BROKEN_ORDER_OR_LINK')
        if obj.get('status') not in {'PASS','FAIL','HOLD','NOT_RUN'}:raise ValueError('INVALID_STATUS')
        candidate={k:v for k,v in obj.items() if k!='event_hash'}
        if obj.get('event_hash')!=digest(candidate):raise ValueError('TAMPERED_EVENT')
        prev=obj['event_hash']
    if prev!=expected:raise ValueError('PINNED_HEAD_MISMATCH')
    return len(lines)

if __name__=='__main__':
    lines=(ROOT/'benchmark_evo.jsonl').read_text(encoding='utf-8').splitlines()
    expected=(ROOT/'HEAD.sha256').read_text(encoding='utf-8').strip()
    print('PASS',verify(lines,expected),'event hash links with externally pinned head',expected)
