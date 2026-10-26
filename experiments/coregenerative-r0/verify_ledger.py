"""Verify pinned ledger chain and regenerated content (integrity, not scientific truth)."""
from pathlib import Path
import json,hashlib
from build import canon
ROOT=Path(__file__).resolve().parent

def verify(root=ROOT):
    root=Path(root)
    lines=(root/'output/benchmark_evo.jsonl').read_text().splitlines()
    prior='0'*64
    for i,line in enumerate(lines,1):
        def obj_pairs(pairs):
            d={}
            for k,v in pairs:
                if k in d:raise AssertionError('DUPLICATE_KEY')
                d[k]=v
            return d
        row=json.loads(line,object_pairs_hook=obj_pairs)
        assert row.get('seq')==i and row.get('schema')=='CoRegenerative.Event.R0'
        assert row.get('prev_hash')==prior
        h=hashlib.sha256(canon({k:v for k,v in row.items() if k!='event_hash'})).hexdigest()
        assert row.get('event_hash')==h,'HASH_MISMATCH'
        prior=h
    assert len(lines)==13,'COUNT_MISMATCH'
    assert prior==(root/'output/HEAD.sha256').read_text().strip(),'PINNED_HEAD_MISMATCH'
    summary=json.loads((root/'output/summary.json').read_text())
    assert summary['ledger_head_sha256']==prior,'SUMMARY_HEAD_MISMATCH'
    for filename,pinned in summary['source_sha256'].items():
        assert hashlib.sha256((root/filename).read_bytes()).hexdigest()==pinned,'SOURCE_MISMATCH:'+filename
    return len(lines),prior

if __name__=='__main__':
    n,h=verify();print('PASS',n,'events, pinned head:',h)
