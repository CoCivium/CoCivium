#!/usr/bin/env python3
"""Read-only immutable artifact consistency checks. No file writes, network or subprocesses."""
import hashlib,json,sys
from pathlib import Path
from collections import Counter
import coproc as c
root=Path(__file__).resolve().parent
receipt=json.loads((root/'RECEIPT.json').read_bytes())
sha=lambda n:hashlib.sha256((root/n).read_bytes()).hexdigest()
checks={
    'spec_pinned':receipt['spec_sha256']==c.SPEC_SHA256,
    'demo_sha':receipt['demo_sha256']==sha('demo_state.json'),
    'ledger_sha':receipt['ledger_sha256']==sha('benchmark_evo.jsonl'),
    'html_sha':receipt['html_sha256']==sha('CoOrbWare_offline.html'),
    'children_bounded':receipt['actual_short_lived_children']==4 and receipt['peak_children']==2 and receipt['remaining_children']==0,
    'no_effect':receipt['external_effects']==0 and receipt['receiver_pickup']=='UNPROVEN'
}
rows=[json.loads(line) for line in (root/'benchmark_evo.jsonl').read_text().splitlines() if line]
counts=dict(Counter(r['status'] for r in rows))
checks['ledger_states']=counts=={'PASS':6,'NOT_RUN':6}
checks['no_promotion']=all(r['promotion_eligible'] is False and r['external_effects']==0 and r['source_spec_sha256']==c.SPEC_SHA256 for r in rows)
checks['not_run_has_no_fake_metrics']=all(r['metrics']=={} for r in rows if r['status']=='NOT_RUN')
demo=json.loads((root/'demo_state.json').read_bytes());page=(root/'CoOrbWare_offline.html').read_text()
checks['public_projection_parity']=demo['public_orb']['spec_sha256']==c.SPEC_SHA256 and demo['public_orb']['receiver_ack']=='UNPROVEN'
checks['private_suppression']='PRIVATE_NOT_FOR_DISPLAY' not in page and not any('PRIVATE_NOT_FOR_DISPLAY' in json.dumps(x) for x in demo['public_orb']['tiles'])
checks['zero_remote_claim']=demo['external_effects']==0 and demo['receiver_ack']=='UNPROVEN'
print(json.dumps({'checks':len(checks),'passed':sum(checks.values()),'failed':[k for k,v in checks.items() if not v],
                  'states':counts,'scope':'READ_ONLY_SAME_HOST_OBJECT_VERIFICATION'},sort_keys=True))
sys.exit(0 if all(checks.values()) else 1)
