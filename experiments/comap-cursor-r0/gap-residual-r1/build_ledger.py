#!/usr/bin/env python3
"""No-network, no-clobber TAP -> CoStretch R5 JSONL + local file-hash receipt."""
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
script = root / 'conull-gdres-r1.mjs'
tests = root / 'conull-gdres-r1.test.mjs'
tapfile = root / 'test_results.tap'
doc = root / 'README.md'
text = tapfile.read_text(encoding='utf-8')
results = re.findall(r'^ok\s+(\d+)\s+-\s+(.+)$', text, flags=re.MULTILINE)
n = re.search(r'^# tests (\d+)$', text, flags=re.MULTILINE)
p = re.search(r'^# pass (\d+)$', text, flags=re.MULTILINE)
f = re.search(r'^# fail (\d+)$', text, flags=re.MULTILINE)
if not all([n,p,f]) or int(n.group(1)) != int(p.group(1)) or int(f.group(1)) or len(results) != int(n.group(1)) or len(set(i for i,_ in results)) != len(results):
    raise SystemExit('TAP_INCOMPLETE_OR_FAILURE')
for i, _ in results:
    if int(i) < 1 or int(i) > 100:
        raise SystemExit('TEST_ID_OUT_OF_BOUNDS')
ledger = root / 'benchmark_evo_r1.jsonl'
receipt = root / 'RECEIPT.json'
if ledger.exists() or receipt.exists():
    raise SystemExit('NO_CLOBBER_EXISTING_LEDGER_OR_RECEIPT')
artifact_sha=sha(script)
source = {"id":"CoNull_GdRes_R1_public_safe_local_fixture", "sha256": artifact_sha}
records=[]
for i, label in results:
    records.append({
      "schema":"CoStretch.BenchmarkEvo.Record.v1", "event_id":f"CONULL_GDRES_{int(i):03d}",
      "status":"PASS", "evidence_class":"LOCAL_RETEST", "claim":label,
      "source":source, "scope":"One local Node 22 synthetic/contract assertion; not a physical experiment",
      "metrics":{"assertion_passed":True},
      "limitations":["Local deterministic tests only; no independent real-world receiver",
                     "TAP recorder is not a real device, model or human-acceptance measurement"],
      "promotion_eligible":False,"external_effects":0,"privacy":"PUBLIC_SAFE"
    })
pending = [
 ('THUMB_HARDWARE_BINDING','OS middle/thumb mouse integration and undo, native click retained'),
 ('MEDIA_GT_300KB_THUMB','Released media >300KB and thumbnail decode/quality'),
 ('FFPROBE_BLACKDETECT','Released video ffprobe and zero black segments'),
 ('GITHUB_HTTP_LT_2S','Exact deployed URL HTTP 200 within two seconds'),
 ('GMAIL_PRIMARY_LT_60S','Consented recipient sees controlled mail in Primary within 60 seconds'),
 ('ACTOR_ID_LOGGED','Real external-effect actor and receiver identity receipt'),
 ('PI_COMPAT_LT_2S','Pi project packet parses and recovers on Andrew authorized device within 2 seconds'),
 ('CLAUDE_CREDENTIALS_LT_1S','Claude credential readiness checked on authorized receiver, without logging secrets'),
 ('OLLAMA_MODEL_PACKET_LT_3S','Real Ollama selected-model inference packet parses within 3 seconds'),
 ('COVIA_PICKUP','Independent CoVIA receiver exact-object pickup/readproof'),
 ('ANDREW_FIRST_USE','Andrew blind first task completes and explains result'),
 ('HISTORICAL_REPLAY','One real old-model asset requalified, original hash and claims preserved'),
 ('RETAINED_PROVIDER_EXIT','Cross-provider cold-start reconstruction verified before retiring paid accounts'),
 ('NODES_SITES_PICKUP','Authorized node/site receivers produce exact readproof'),
 ('PRIVATE_AMBIENT_BYSTANDER','Desktop/wallpaper privacy and ambient observer acceptance')
]
for label, description in pending:
    records.append({
      "schema":"CoStretch.BenchmarkEvo.Record.v1", "event_id":"CONULL_GATE_"+label,
      "status":"NOT_RUN","evidence_class":"PENDING_REAL_TEST", "claim":description,
      "source":source, "scope":"Requires qualified external, device or participant evidence",
      "metrics":{},"limitations":["No qualified receiver, test substrate, or source in this bounded code-only wave"],
      "promotion_eligible":False,"external_effects":0,"privacy":"PUBLIC_SAFE"
    })
with ledger.open('x', encoding='utf-8', newline='\n') as out:
    for rec in records:
        out.write(json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(',',':')) + '\n')
receipt_data={
 "schema":"CoNull.GdRes.R1.LocalReceipt.v1","created_utc":datetime.now(timezone.utc).isoformat(),
 "state":"VERIFIED_LOCAL_NOT_LANDED_NOT_PICKED_UP",
 "source_lineage":["CoCivium/CoCivium PR #215","CoCivium/CoCivium issue #214","CoCivium/CoCivium PR #216 (merged)","CoCivium/CoCivium PR #218 (draft)"],
 "files_sha256": {p.name:sha(p) for p in (script,tests,doc,root/'build_ledger.py',tapfile,ledger)},
 "tests_passed":len(results),"tests_failed":0,"not_run_gates":len(pending),"jsonl_sha256":sha(ledger),
 "receiver_readproof":None,"public_release":False,"provider_calls":0,"actual_workers_spawned":0,
 "external_messages_sent":0,"semantic_review":"R1 self-authored code and test contracts reviewed; no historical global corpus review",
 "ux_acceptance":"UX_NOT_EVALUATED"
}
with receipt.open('x',encoding='utf-8',newline='\n') as out:
    json.dump(receipt_data,out,sort_keys=True,indent=2)
    out.write('\n')
print(json.dumps({"status":"PASS","tests":len(results),"pending":len(pending),"ledger_hash":sha(ledger),"lifecycle":receipt_data['state']},sort_keys=True))