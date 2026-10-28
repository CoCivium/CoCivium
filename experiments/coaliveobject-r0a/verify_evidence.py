#!/usr/bin/env python3
"""Offline integrity verifier; hash chain is not a digital signature."""
import json,hashlib
from pathlib import Path
from engine import digest, reject_duplicate_keys, CoAlive
ROOT=Path(__file__).parent;OUT=ROOT/'output'
rows=[json.loads(line,object_pairs_hook=reject_duplicate_keys) for line in (OUT/'benchmark_evo.jsonl').read_text().splitlines() if line]
head='0'*64
for i,row in enumerate(rows,1):
    assert row['schema']=='CoAliveBenchEvent/R0' and row['seq']==i and row['prev_hash']==head, 'BROKEN_SEQUENCE'
    assert row['event_hash']==digest({k:v for k,v in row.items() if k!='event_hash'}),'TAMPERED_ROW'
    head=row['event_hash']
assert head==(OUT/'HEAD.sha256').read_text().strip(),'WRONG_HEAD'
summary=json.loads((OUT/'SUMMARY.json').read_text(),object_pairs_hook=reject_duplicate_keys)
assert summary['head']==head and summary['event_count']==len(rows)
assert summary['source_sha256']==hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest()
snapshot=json.loads((OUT/'snapshot.json').read_text(),object_pairs_hook=reject_duplicate_keys)
restored=CoAlive((ROOT/'manifest.json').read_bytes(),snapshot)
assert restored.snapshot()==snapshot
assert summary['actual_workers']==0 and summary['remote_effects']==0
print('PASS',len(rows),'pinned synthetic events; exact source identity; snapshot recovery; head',head)
