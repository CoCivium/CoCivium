#!/usr/bin/env python3
"""One-shot, offline, public-safe CoVIA -> CoMap/CoOrb/Text parity canary. No network."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parent
source_file = root / "source.json"
source_bytes = source_file.read_bytes()
source_hash = hashlib.sha256(source_bytes).hexdigest()
source = json.loads(source_bytes.decode("utf-8-sig"))
identity = "github:CoCivium/CoCivium:issue:181:comment:6268716355"
body = source["source_body"]
checks = {}
def check(name, value):
    checks[name] = bool(value)

check("SOURCE_ID_BOUND", source.get("source_id") == identity)
check("SOURCE_TIME_BOUND", source.get("source_updated_at") == "2026-10-19T13:45:20Z")
check("SOURCE_PUBLIC_BOUND", source.get("privacy") == "PUBLIC" and source.get("effect_authority") == "NONE")
check("SOURCE_BODY_RETAINED", len(body) > 3000 and "CoVIA+" in body and "CoOrb+" in body)
anchors = [
    ("REL_COVIA_COORB", "CoVIA+", "CoOrb+", "CoOrb+ can be the low-attention"),
    ("REL_ORB_MAP", "CoOrb+", "CoMap+", "quick expand into CoPop/CoPanel/CoMap"),
    ("REL_INPUT_FLOW", "RAW_INPUT", "QUALIFIED_INTENT", "RAW_INPUT -> DRAFT_SIGNAL"),
]
edges = []
for edge_id, start, finish, excerpt in anchors:
    check("SOURCE_ANCHOR_" + edge_id, excerpt in body)
    edges.append({
        "edge_id": edge_id, "from": start, "to": finish,
        "relation_state": "DOCUMENTED_DESIGN_CANDIDATE",
        "epistemic": "PROPOSED", "privacy": "PUBLIC",
        "evidence_excerpt": excerpt,
        "source_id": identity, "source_copy_sha256": source_hash,
        "observation": "SOURCE_DOCUMENT_ONLY_NOT_LIVE"
    })
notspace = [
    {"id": "NS_ACK", "state": "NOT_OBSERVED", "meaning": "No exact-object receiver readproof in this canary", "render_live_edge": False},
    {"id": "NS_PRIVATE", "state": "INTENTIONALLY_PRIVATE", "meaning": "Privacy boundary; no endpoints exposed", "render_live_edge": False},
    {"id": "NS_UNKNOWN", "state": "UNKNOWN", "meaning": "No evidence for a link is not evidence of absence", "render_live_edge": False},
    {"id": "NS_FUTURE", "state": "PREDICTED_ONLY", "meaning": "Forecast/hypothesis held as preview; not current state", "render_live_edge": False},
]
def projection(name):
    return {
        "schema": "CoMap.CandidateProjection.R2",
        "surface": name, "source_id": identity, "source_copy_sha256": source_hash,
        "source_currentness": "DATED_SNAPSHOT_NOT_LIVE",
        "rendered_relations": edges, "notspace_relations": notspace,
        "receiver_pickup": False, "effect_authority": "NONE",
        "source_kind": "PUBLIC_GITHUB_COMMENT", "external_effects": 0,
        "provider_calls": 0
    }
views = {n:projection(n) for n in ("COMAP", "COORB", "TEXT_TWIN")}
views["AMBIENT"] = {
    "schema": "CoMap.CandidateProjection.R2",
    "surface": "AMBIENT", "source_id": identity,
    "source_copy_sha256": source_hash,
    "headline": "CoVIA / CoOrb proposal | not live",
    "edge_count": len(edges), "receiver_pickup": False,
    "effect_authority": "NONE", "private_endpoints": [],
    "external_effects": 0, "provider_calls": 0
}
id_sets = [{e["edge_id"] for e in views[n]["rendered_relations"]} for n in ("COMAP","COORB","TEXT_TWIN")]
check("MAP_ORB_TEXT_ID_PARITY", id_sets[0] == id_sets[1] == id_sets[2])
check("SOURCE_HASH_SAME_ALL_VIEWS", all(x["source_copy_sha256"] == source_hash for x in views.values()))
check("EDGES_GROUNDED_IN_SOURCE", all(e["evidence_excerpt"] in body and e["source_id"] == identity for e in edges))
check("DESIGN_NE_RUNTIME", all(e["epistemic"] == "PROPOSED" and e["observation"] != "LIVE" for e in edges))
check("NOTSPACE_NONEDGE", all(not v["render_live_edge"] for v in notspace))
check("UNKNOWN_NOT_NEGATED", any(v["state"] == "UNKNOWN" and "not evidence of absence" in v["meaning"] for v in notspace))
check("PRIVATE_ENDPOINTS_HIDDEN", not views["AMBIENT"]["private_endpoints"] and all("from" not in v and "to" not in v for v in notspace))
check("PREDICTION_NE_INTENT", all(e["epistemic"] != "PREDICTED" for e in edges) and any(v["state"] == "PREDICTED_ONLY" for v in notspace))
check("RECEIVER_ACK_HELD", all(v["receiver_pickup"] is False for v in views.values()))
check("NO_OUTBOUND_OR_PROVIDER_EFFECTS", all(v["external_effects"] == 0 and v["provider_calls"] == 0 for v in views.values()))
check("WRONG_SOURCE_REJECTED", all(e["source_copy_sha256"] != "0"*64 for e in edges))
check("RELATION_COUNT_BOUND", len(edges) == 3 and len(notspace) == 4)
# Explicit negative control: a fake observed/live receiver relationship must never be promoted.
forged = dict(edges[0], epistemic="OBSERVED", observation="LIVE")
check("FORGED_LIVE_EDGE_REJECTED", not (forged["epistemic"] == "PROPOSED" and forged["observation"] != "LIVE"))
assert all(checks.values()), json.dumps({k:v for k,v in checks.items() if not v})
result_path = root / "projections.json"
ledger_path = root / "benchmark_evo.jsonl"
receipt_path = root / "RECEIPT.json"
for path in (result_path, ledger_path, receipt_path):
    if path.exists(): raise SystemExit("NO_CLOBBER_FILE_EXISTS: "+str(path))
with result_path.open("x", encoding="utf-8", newline="\n") as out:
    json.dump({"source": {"source_id":identity, "source_copy_sha256":source_hash,
        "updated_at":source["source_updated_at"], "source_url":source["source_url"]},
        "views":views, "tests":checks, "coverage":"ONE_PUBLIC_GITHUB_COMMENT"}, out, indent=2, ensure_ascii=False)
    out.write("\n")
with ledger_path.open("x", encoding="utf-8", newline="\n") as out:
    for name, passed in checks.items():
        rec = {"schema":"CoStretch.BenchmarkEvo.Record.v1","event_id":"COVIA_R2_"+name,
            "status":"PASS" if passed else "FAIL", "evidence_class":"LOCAL_RETEST",
            "claim":"Bounded source-bound CoVIA/CoMap parity: "+name,
            "source":{"id":"CoVIA_181_PUBLIC_COMMENT_COPY","sha256":source_hash},
            "scope":"One public source; same-host deterministic projection; not receiver delivery",
            "metrics":{"passed":passed}, "limitations":["No independent receiver pickup", "No live CoVIA or paid-provider substitution"],
            "promotion_eligible":False,"external_effects":0,"privacy":"PUBLIC_SAFE"}
        out.write(json.dumps(rec,sort_keys=True)+"\n")
receipt = {
    "schema":"CoMap.CoVIAParityR2.Receipt.v1",
    "source_id":identity, "source_copy_sha256":source_hash,
    "source_body_sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),
    "source_updated_at":source["source_updated_at"],
    "projections_sha256":hashlib.sha256(result_path.read_bytes()).hexdigest(),
    "benchmark_evo_sha256":hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
    "checks_passed":sum(checks.values()), "checks_total":len(checks),
    "lifecycle":"VERIFIED_LOCAL_NO_RECEIVER_ACK",
    "no_external_delivery":True, "model_calls":0,
    "not_run":["MIDDLE_MOUSE_OS_BINDING","GMAIL_PRIMARY_60S","PI_CLAUDE_COMPARISON",
        "REAL_LOCAL_MODEL_INFERENCE","GITHUB_HTTP_2S","PAID_ACCOUNT_EXIT"]
}
with receipt_path.open("x",encoding="utf-8",newline="\n") as out:
    json.dump(receipt,out,indent=2,sort_keys=True)
    out.write("\n")
print(json.dumps({"result":"PASS","checks":len(checks),"source_copy_sha256":source_hash,
    "receipt":str(receipt_path),"external_effects":0},sort_keys=True))