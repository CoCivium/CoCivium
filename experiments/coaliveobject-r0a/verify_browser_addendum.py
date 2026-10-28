"""Verify append-only R0a ledger and parent prefix. No network or external trust asserted."""
from pathlib import Path
import hashlib,json
from engine import digest,reject_duplicate_keys
ROOT=Path(__file__).parent;OUT=ROOT/'output'
base=[json.loads(line,object_pairs_hook=reject_duplicate_keys) for line in (OUT/'benchmark_evo.jsonl').read_text().splitlines() if line]
rows=[json.loads(line,object_pairs_hook=reject_duplicate_keys) for line in (OUT/'benchmark_evo_R0a.jsonl').read_text().splitlines() if line]
assert rows[:len(base)]==base,'PARENT_OVERWRITTEN'
assert len(base)==20 and len(rows)==23
head='0'*64
for n,row in enumerate(rows,1):
 assert row.get('schema')=='CoAliveBenchEvent/R0' and row.get('seq')==n and row.get('prev_hash')==head
 assert row['event_hash']==digest({k:v for k,v in row.items() if k!='event_hash'})
 head=row['event_hash']
assert head==(OUT/'HEAD_R0a.sha256').read_text().strip()
assert rows[19]['event_hash']==(OUT/'HEAD.sha256').read_text().strip()
b=json.loads((OUT/'browser_check.json').read_text(),object_pairs_hook=reject_duplicate_keys)
assert b['view_source_sha256']==hashlib.sha256((ROOT/'CoAliveObject_Viewer.html').read_bytes()).hexdigest()
print('PASS 23 linked events; unchanged 20-event parent; exact viewer source',head)
