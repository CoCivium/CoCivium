#!/usr/bin/env python3
"""Check self-contained research receipt consistency. A hash chain is NOT authentication."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')


def verify(lines, expected_head):
    prev='0'*64
    for i,line in enumerate(lines, 1):
        rec=json.loads(line)
        assert rec['seq']==i, f'sequence {i}'
        assert rec['prev_hash']==prev, f'previous hash {i}'
        assert rec['status'] in ['PASS','FAIL','HOLD','NOT_RUN'], f'unknown status {i}'
        pay={k:v for k,v in rec.items() if k!='event_hash'}
        assert rec['event_hash']==sha(canonical(pay)), f'bad event {i}'
        prev=rec['event_hash']
    assert prev==expected_head, 'pinned head mismatch'
    return len(lines)

if __name__=='__main__':
    lines=[l for l in (ROOT/'benchmark_evo.jsonl').read_text().splitlines() if l]
    head=(ROOT/'HEAD.sha256').read_text().strip()
    count=verify(lines,head)
    print('PASS',count,'research policy events, pinned ledger head',head)
