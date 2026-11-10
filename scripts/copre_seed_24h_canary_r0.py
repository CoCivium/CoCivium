#!/usr/bin/env python3
"""CoPre R0 survival canary: read-only verification, not an autonomous CoAll worker.

Emits a source-bound observation. A >24h survival verdict requires two independent
workflow observations with identical pinned content, separated by >=24h. A single
successful run, uptime assumption, local replay, or timestamp in a prompt is insufficient.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

PINNED_COMMIT = "63b41ead8797e5a781699f32bcbc77b78bdbd7af"
URL = "https://raw.githubusercontent.com/CoCivium/CoCivium/" + PINNED_COMMIT + "/CoPre.md"
MAINLINE_URL = "https://raw.githubusercontent.com/CoCivium/CoCivium/main/CoPre.md"
EXPECTED_SHA256 = "58f8c722bfbfc34cac41189c072d2effe4b19dbbe8a37be4f8687344d6b00b9a"
SCHEMA = "CoAll.CoPre.Seed24hObservation.R0"
MIN_SECONDS = 24 * 60 * 60

def parse_time(x):
    value = dt.datetime.fromisoformat(x.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("NAIVE_TIME")
    return value.astimezone(dt.timezone.utc)

def evaluate(current, prior=None):
    if current.get("schema") != SCHEMA or current.get("source_commit") != PINNED_COMMIT:
        raise ValueError("SOURCE_ID_MISMATCH")
    if current.get("sha256") != EXPECTED_SHA256 or current.get("state") != "PINNED_SOURCE_MATCH":
        return "HELD_SOURCE_UNVERIFIED"
    if prior is None:
        return "BASELINE_ONLY"
    if prior.get("schema") != SCHEMA or prior.get("source_commit") != PINNED_COMMIT:
        return "HELD_PRIOR_SOURCE_MISMATCH"
    if prior.get("sha256") != EXPECTED_SHA256 or prior.get("state") != "PINNED_SOURCE_MATCH":
        return "HELD_PRIOR_UNVERIFIED"
    if prior.get("workflow_run_id") == current.get("workflow_run_id"):
        return "HELD_SAME_RUN"
    elapsed = (parse_time(current["observed_at"]) - parse_time(prior["observed_at"])).total_seconds()
    if elapsed < MIN_SECONDS:
        return "HELD_LESS_THAN_24H" if elapsed >= 0 else "HELD_CLOCK_INVERSION"
    return "VERIFIED_SOURCE_REFETCH_24H_PLUS_NOT_RUNTIME_SURVIVAL"

def fetch_source(url=URL):
    req = urllib.request.Request(url, headers={"User-Agent": "CoCivium-CoPre-24h-Canary/1.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("SOURCE_TOO_LARGE")
        return r.status, hashlib.sha256(raw).hexdigest(), len(raw)

def classify_mainline(*, pinned_digest, mainline_status, mainline_digest):
    """Current HEAD comparison is a *separate* status from historical refetch."""
    if mainline_status != 200 or not mainline_digest:
        return "HELD_MAINLINE_UNAVAILABLE"
    if pinned_digest != EXPECTED_SHA256:
        return "HELD_PINNED_SOURCE_UNVERIFIED"
    return ("MATCHED_PINNED_AT_OBSERVATION" if mainline_digest == pinned_digest
            else "MAINLINE_DIVERGED_FROM_HISTORICAL_PIN")

def make_observation(*, status, digest, length, run_id, observed_at):
    valid = status == 200 and digest == EXPECTED_SHA256
    return {"schema":SCHEMA, "source_commit":PINNED_COMMIT, "source_url":URL,
            "observed_at":observed_at, "workflow_run_id":str(run_id),
            "http_status":status, "sha256":digest, "bytes":length,
            "state":"PINNED_SOURCE_MATCH" if valid else "HELD_SOURCE_UNVERIFIED"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--prior", type=Path)
    args=ap.parse_args()
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        status,digest,length=fetch_source()
        current=make_observation(status=status,digest=digest,length=length,
                                 run_id=os.getenv("GITHUB_RUN_ID","MANUAL_UNKNOWN"),observed_at=now)
    except (urllib.error.URLError,TimeoutError,OSError,ValueError) as error:
        current=make_observation(status=None,digest=None,length=None,
                                 run_id=os.getenv("GITHUB_RUN_ID","MANUAL_UNKNOWN"),observed_at=now)
        current["transport_error_class"]=type(error).__name__
    prior=None
    if args.prior is not None and args.prior.exists():
        try:
            prior=json.loads(args.prior.read_text(encoding="utf-8"))
        except (OSError,ValueError):
            prior={"schema":"MALFORMED"}
    # The historical survival observation must never substitute for the
    # live mainline-currentness question. Report both, even when they diverge.
    try:
        live_status,live_digest,live_length=fetch_source(MAINLINE_URL)
    except (urllib.error.URLError,TimeoutError,OSError,ValueError) as error:
        live_status,live_digest,live_length=None,None,None
        current["mainline_transport_error_class"]=type(error).__name__
    current["mainline"]={
        "source_url":MAINLINE_URL,"http_status":live_status,
        "sha256":live_digest,"bytes":live_length,
        "comparison":classify_mainline(
            pinned_digest=current["sha256"],
            mainline_status=live_status,mainline_digest=live_digest)
    }
    current["current_seed_synchronized"]=False
    current["qualification"]=evaluate(current,prior)
    current["receiver_ack"]=False
    current["cross_provider_sync"]=False
    current["coex"]=False
    current["exactly_once_effect_handoff"]=False
    current["nonclaims"]=["HISTORICAL_PIN_SURVIVAL_NE_CURRENT_MAINLINE_SYNC","MAINLINE_200_NE_MIRROR_DELIVERY","NO_INDEPENDENT_RECEIVER_ACK"]
    args.output.write_text(json.dumps(current,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(current["qualification"])
    if current["state"] != "PINNED_SOURCE_MATCH":
        raise SystemExit(1)

if __name__=="__main__":
    main()
