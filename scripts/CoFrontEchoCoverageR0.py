#!/usr/bin/env python3
"""CoFront/CoEcho historical coverage audit R0. Pure bounded metadata; no fetch or promotion."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

STATES={"UNKNOWN","DISCOVERED","VERIFIED_SOURCE","REVIEW_REQUIRED","INTENTIONALLY_ISOLATED","SUPERSEDED","QUALIFIED"}
DISPOSITIONS={"KEEP","REVERIFY","REPLAY","REINTERPRET","REFACTOR","REPLACE","ARCHIVE_ONLY","UNKNOWN"}
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def audit(packet):
    if not isinstance(packet,dict) or packet.get("schema")!="CoFront.EchoCoverage.Input.R0":
        raise ValueError("INVALID_SCHEMA")
    windows=packet.get("windows"); items=packet.get("observations")
    if not isinstance(windows,list) or not isinstance(items,list) or len(windows)>100 or len(items)>2000:
        raise ValueError("BOUNDED_WINDOWS_OBSERVATIONS_REQUIRED")
    named={}; observed={}
    for w in windows:
        if not isinstance(w,dict) or set(w)!={"id","root_ref","from_time","until_time","completeness"}:
            raise ValueError("INVALID_WINDOW")
        if any(not isinstance(w[k],str) or not w[k] for k in ("id","root_ref","from_time","until_time")):
            raise ValueError("INVALID_WINDOW")
        if w["id"] in named or w["completeness"] not in ("PARTIAL","UNSCANNED","SCOPED_COMPLETE"):
            raise ValueError("DUPLICATE_OR_INVALID_WINDOW")
        if w["from_time"]>w["until_time"]:
            raise ValueError("INVALID_WINDOW_TIME")
        named[w["id"]]=w
    rows=[]; exact_replay=0; conflicts=[]; seen={}
    for i,obs in enumerate(items):
        if not isinstance(obs,dict):
            raise ValueError("INVALID_OBSERVATION")
        required=("front_id","window_id","source_ref","source_sha256","observed_at","state","disposition","visibility")
        if any(not isinstance(obs.get(k),str) or not obs[k] for k in required):
            raise ValueError("MISSING_OBSERVATION_FIELD")
        if obs["window_id"] not in named or obs["state"] not in STATES or obs["disposition"] not in DISPOSITIONS or obs["visibility"] not in ("PUBLIC","PRIVATE"):
            raise ValueError("INVALID_OBSERVATION_STATE")
        if len(obs["source_sha256"])!=64 or any(c not in "0123456789abcdef" for c in obs["source_sha256"]):
            raise ValueError("INVALID_SOURCE_HASH")
        if not named[obs["window_id"]]["from_time"]<=obs["observed_at"]<=named[obs["window_id"]]["until_time"]:
            raise ValueError("OUTSIDE_DECLARED_TIME_WINDOW")
        if obs["state"]=="QUALIFIED" and not obs.get("qualification_evidence_ref"):
            raise ValueError("QUALIFIED_WITHOUT_EVIDENCE")
        if obs["state"]=="SUPERSEDED" and not obs.get("successor_ref"):
            raise ValueError("SUPERSEDED_WITHOUT_SUCCESSOR")
        key=(obs["window_id"],obs["front_id"],obs["source_ref"],obs["observed_at"])
        stamp=digest(obs)
        if key in seen:
            if seen[key]!=stamp:
                conflicts.append({"window_id":obs["window_id"],"state":"CONFLICT_HELD"})
            else:
                exact_replay+=1
            continue
        seen[key]=stamp
        # Public report only includes source refs for source-qualified public observations.
        rows.append({"front_id":obs["front_id"] if obs["visibility"]=="PUBLIC" else "PRIVATE_REDACTED",
                     "window_id":obs["window_id"],"state":obs["state"],
                     "disposition":obs["disposition"],"source_ref":obs["source_ref"] if obs["visibility"]=="PUBLIC" else None,
                     "source_sha256":obs["source_sha256"] if obs["visibility"]=="PUBLIC" else None,
                     "receiver_pickup":"UNPROVEN","inferred_runtime":False})
    counts=Counter(x["state"] for x in rows)
    return {"schema":"CoFront.EchoCoverage.Report.R0",
            "state":"SOURCE_SCOPE_REPORT_NOT_HISTORICAL_CENSUS",
            "coverage":{"declared_windows":len(windows),"observed_objects":len(rows),
                        "exact_replays_suppressed":exact_replay,"conflicting_same_identity":len(conflicts),
                        "unscanned_window_ids":sorted(w["id"] for w in windows if w["completeness"]=="UNSCANNED"),
                        "global_history_complete":False},
            "state_counts":dict(sorted(counts.items())),"fronts":rows,"conflicts":conflicts,
            "next":"RECONCILE_SCOPED_HIGH_LOSS_RISK_GAPS_THEN_REQUEST_INDEPENDENT_RECEIVER_READPROOF",
            "nonclaims":["DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY","HASH_NE_SEMANTIC_VALIDATION",
                         "SOURCE_LANDED_NE_RECEIVER_PICKUP","OLD_SOURCE_NE_CURRENT_AUTHORITY",
                         "PRIVATE_METADATA_NE_PUBLIC_PROJECTION","REPEATED_ECHO_NE_NEW_FRONT",
                         "CHRONOLOGY_NE_PROVEN_COMPLETENESS"]}
