"""Independent standard-library checksum-chain verifier; not proof of authorship."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
def strict_object(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('DUPLICATE_KEY')
        d[k]=v
    return d
def verify(text,head):
    prev='0'*64;lines=text.splitlines()
    if not lines:raise ValueError('EMPTY_LEDGER')
    for i,line in enumerate(lines,1):
        r=json.loads(line,object_pairs_hook=strict_object)
        if r.get('seq')!=i or r.get('schema')!='CoScaleMorph.EvoEvent/R0' or r.get('prev_hash')!=prev:raise ValueError('BROKEN_CHAIN')
        d={k:v for k,v in r.items() if k!='event_hash'}
        b=json.dumps(d,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode()
        if hashlib.sha256(b).hexdigest()!=r.get('event_hash'):raise ValueError('TAMPERED_ROW')
        prev=r['event_hash']
    if prev!=head.strip():raise ValueError('HEAD_MISMATCH')
    return len(lines)
if __name__=='__main__':
    n=verify((OUT/'benchmark_evo.jsonl').read_text(),(OUT/'HEAD.sha256').read_text())
    print(f'PASS {n} hash-linked events verified against pinned head')
