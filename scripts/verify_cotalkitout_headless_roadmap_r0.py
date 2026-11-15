#!/usr/bin/env python3
"""Pure standard-library verifier of one public-safe CoTalkItOut CSV candidate.

Read-only source validation. Not an X2 probe, worker, account action,
independent receiver, provenance signature, CoEx or public deployment.
"""
import csv
import hashlib
import io
import pathlib
import re
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "ai/roadmaps/CoTalkItOut_CausalOps_R0_20261112.csv"
INDEX_PATH = ROOT / "docs/Operations/COTALKITOUT_HEADLESS_AUTONOMY_INDEX_R0.md"
WORKID = "CoTalkItOut.HeadlessScreenlessWorkContinuity.20261112.R0"
EXPECTED_SHA256 = "f9e2a3e926e834edb8e4e9eba49735f9ae0ffa8d634d5721da34a3408a580c97"
EXPECTED_TASKS, EXPECTED_EDGES, EXPECTED_LANES = 319, 511, 16
EXPECTED_HUMAN_GATES, EXPECTED_SOURCE_TESTED = 7, 29
FIELDS = [
    "work_id","task_id","topo","lane","title","operation","acceptance",
    "depends_on","priority","evidence_state","proof_ceiling","human_gate",
    "source_url","release_note"
]
KNOWN_STATES = {"HELD","PLANNED","SOURCE_TESTED_ONLY","OBSERVED_GAP","HUMAN_GATE"}
SECRET_PATTERNS = (
    re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?i)\b(?:sk-|ghp_|AKIA)[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)\b(?:password|api_key|client_secret)\s*[:=]\s*[^\s,]+"),
    re.compile(r"(?i)(?:[A-Z]:\\\\|\\\\\\\\)[^\s,]+")
)

def require(ok, why):
    if not ok: raise ValueError(why)

def validate(text, *, expected_sha=None, count_gate=False):
    if expected_sha is not None:
        require(hashlib.sha256(text.encode("utf-8")).hexdigest() == expected_sha, "DIGEST_DRIFT")
    require("\r" not in text, "NONCANONICAL_LINE_ENDINGS")
    for pattern in SECRET_PATTERNS:
        require(pattern.search(text) is None, "PRIVATE_OR_SECRET_SHAPED_PAYLOAD")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    require(reader.fieldnames == FIELDS, "SCHEMA_FIELDS_DRIFT")
    records = list(reader)
    ids = [r["task_id"] for r in records]
    require(len(ids)==len(set(ids)), "DUPLICATE_TASK_ID")
    id_to_row = dict(zip(ids,records))
    require(all(re.fullmatch(r"[A-Z][0-9]{2}",x) for x in ids), "INVALID_ID")
    require(all(r["work_id"]==WORKID for r in records), "WORKID_DRIFT")
    require(all(r["release_note"] == "SOURCE_ONLY_NOT_RUNTIME" for r in records), "RUNTIME_OVERCLAIM")
    require(all(r["evidence_state"] in KNOWN_STATES for r in records), "UNKNOWN_EVIDENCE_STATE")
    require(all(r["priority"] in {"P0","P1","P2"} for r in records), "UNKNOWN_PRIORITY")
    require(all(r["human_gate"] in {"YES","NO"} for r in records), "INVALID_HUMAN_GATE")
    require(all(r["source_url"].startswith("https://") for r in records), "UNVERIFIED_SOURCE_URL_CLASS")
    require(all(r["title"] and r["operation"] and r["acceptance"] for r in records), "EMPTY_CAUSAL_FIELD")
    ranks = {}
    for r in records:
        try: rank=int(r["topo"])
        except (ValueError,TypeError): raise ValueError("INVALID_TOPO_RANK")
        ranks[r["task_id"]]=rank
    require(sorted(ranks.values())==list(range(1,len(records)+1)), "NONUNIQUE_OR_MISSING_TOPO_RANK")
    edges=0
    for r in records:
        me=r["task_id"]
        deps=[x.strip() for x in r["depends_on"].split(",") if x.strip()]
        require(len(deps)==len(set(deps)), "DUPLICATED_DEPENDENCY")
        for d in deps:
            require(d in id_to_row, "MISSING_PREDECESSOR")
            require(ranks[d]<ranks[me], "CYCLE_OR_FALSE_TOPOLOGICAL_ORDER")
            edges+=1
    summary = {"tasks":len(records),"edges":edges,
               "lanes":len(set(r["lane"] for r in records)),
               "human_gates":sum(r["human_gate"]=="YES" for r in records),
               "source_tested":sum(r["evidence_state"]=="SOURCE_TESTED_ONLY" for r in records)}
    if count_gate:
        for key,expected in (("tasks",EXPECTED_TASKS),("edges",EXPECTED_EDGES),
                             ("lanes",EXPECTED_LANES),("human_gates",EXPECTED_HUMAN_GATES),
                             ("source_tested",EXPECTED_SOURCE_TESTED)):
            require(summary[key]==expected, "EXPECTED_"+key.upper()+"_DRIFT")
    return summary

def expect_failure(case,reason):
    try: validate(case)
    except ValueError as e:
        require(reason in str(e),"WRONG_FAILURE_"+reason+"_"+str(e))
        return
    raise AssertionError("NEGATIVE_CONTROL_FALSE_GREEN_"+reason)

def adversarial_selftest(source):
    # All mutations are in-memory; no source file writes, no X2 process starts.
    import copy
    rec=list(csv.DictReader(io.StringIO(source)))
    def materialize(items):
        b=io.StringIO()
        w=csv.DictWriter(b,fieldnames=FIELDS,lineterminator="\n")
        w.writeheader();w.writerows(items)
        return b.getvalue()
    trial=copy.deepcopy(rec);trial.append(copy.deepcopy(trial[0]))
    expect_failure(materialize(trial),"DUPLICATE_TASK_ID")
    trial=copy.deepcopy(rec);trial[1]["depends_on"]="MISSING99"
    expect_failure(materialize(trial),"MISSING_PREDECESSOR")
    trial=copy.deepcopy(rec);trial[0]["depends_on"]=rec[1]["task_id"]
    expect_failure(materialize(trial),"CYCLE_OR_FALSE_TOPOLOGICAL_ORDER")
    trial=copy.deepcopy(rec);trial[0]["release_note"]="LIVE_RUNTIME_VERIFIED"
    expect_failure(materialize(trial),"RUNTIME_OVERCLAIM")
    trial=copy.deepcopy(rec);trial[0]["operation"]="email secret@example.com"
    expect_failure(materialize(trial),"PRIVATE_OR_SECRET_SHAPED_PAYLOAD")
    trial=copy.deepcopy(rec);trial[0]["topo"]="3"
    expect_failure(materialize(trial),"NONUNIQUE_OR_MISSING_TOPO_RANK")
    trial=copy.deepcopy(rec);trial[0]["human_gate"]="APPROVED"
    expect_failure(materialize(trial),"INVALID_HUMAN_GATE")
    expect_failure(source.replace("SOURCE_ONLY_NOT_RUNTIME","SOURCE_ONLY_NOT_RUNTIME ",1).replace("\n","\r\n"),"NONCANONICAL_LINE_ENDINGS")
    print("PASS: 8 in-memory adversarial validation tests, no effects")

def main():
    raw=CSV_PATH.read_bytes()
    text=raw.decode("utf-8","strict")
    summary=validate(text,expected_sha=EXPECTED_SHA256,count_gate=True)
    index=INDEX_PATH.read_text(encoding="utf-8")
    require(WORKID in index,"INDEX_WORKID_MISSING")
    require(EXPECTED_SHA256 in index,"INDEX_DIGEST_MISSING")
    require("SOURCE CANDIDATE" in index,"INDEX_NONCLAIM_MISSING")
    require("PRIVATE" in index and "CAS" in index or "current source blob" in index,"INDEX_PUBLIC_PRIVATE_GUARD_MISSING")
    print("PASS: exact CSV SHA256, schema, 319 WorkIDs, 511 typed edges, 16 lanes, 7 human gates")
    print("PASS: no source-only rows accidentally promoted to accepted native effects")
    print("PASS: stable public index links exact source digest; private payloads absent")
    if "--selftest" in sys.argv:adversarial_selftest(text)
    print("NOT PROVEN: receiver ACK, CoBar adoption, X2 runtime, headless worker, publication/CoEx/canon")

if __name__ == "__main__":main()
