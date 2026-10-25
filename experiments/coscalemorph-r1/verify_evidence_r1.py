#!/usr/bin/env python3
"""Independent strict R1 chain verification and binding to prior R0 head."""
import json
from pathlib import Path
from coscalemorph import canonical, sha
from verify_ledger import verify as verify_r0

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
SCHEMA='CoScaleMorph.EvoEvent/R1'
ALLOWED={'PASS','FAIL','HOLD','NOT_RUN'}


def strict_pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('DUPLICATE_KEY')
        d[k]=v
    return d


def verify(text:str,head:str,r0head:str) -> dict:
    rows=[json.loads(line,object_pairs_hook=strict_pairs) for line in text.splitlines()]
    if not rows:raise ValueError('EMPTY_R1_LEDGER')
    prev='0'*64
    for i,row in enumerate(rows,1):
        if row.get('schema')!=SCHEMA or type(row.get('seq')) is not int or row['seq']!=i:
            raise ValueError('R1_SCHEMA_OR_SEQUENCE')
        if row.get('parent_r0_head')!=r0head or row.get('prev_hash')!=prev:
            raise ValueError('R1_PARENT_OR_LINK_CHANGED')
        if row.get('outcome') not in ALLOWED or not isinstance(row.get('detail'),dict):
            raise ValueError('R1_INVALID_EVENT')
        body={k:v for k,v in row.items() if k!='event_hash'}
        if sha(canonical(body))!=row.get('event_hash'):
            raise ValueError('R1_EVENT_HASH_CHANGED')
        prev=row['event_hash']
    if prev!=head.strip():raise ValueError('R1_PINNED_HEAD_MISMATCH')
    return {'events':len(rows),'statuses':{k:sum(x['outcome']==k for x in rows) for k in sorted(ALLOWED)},'head':prev}


def main():
    r0head=(OUT/'HEAD.sha256').read_text().strip()
    verify_r0((OUT/'benchmark_evo.jsonl').read_text(),r0head)
    result=verify((OUT/'benchmark_evo_R1.jsonl').read_text(),(OUT/'HEAD_R1.sha256').read_text(),r0head)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
