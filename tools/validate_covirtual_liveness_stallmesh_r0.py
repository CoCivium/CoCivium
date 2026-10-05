#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/operations/covirtual_liveness_stallmesh_r0.json")

def classify(x):
    if x.get("successor"): return "SUPERSEDED"
    if x.get("progress"): return "PROGRESSING"
    if x.get("visible") and x.get("responsive") and x.get("heartbeat") and not x.get("progress"): return "STALLED"
    if x.get("recoverable") and not x.get("visible") and not x.get("heartbeat"): return "DORMANT"
    return "UNKNOWN"

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    for c in d["cases"]:
        got=classify(c)
        if got!=c["expected"]:
            raise SystemExit(f"FAIL:{c['id']}:{got}!={c['expected']}")
    r=d["recovery"]
    if r["simultaneous_actuators_per_lease"]!=1 or r["retry_storm_allowed"] is not False or r["backoff_required"] is not True:
        raise SystemExit("FAIL:recovery quorum")
    if d["runtime_adoption"] or d["provider_session_mutation"] or d["public_effect"]:
        raise SystemExit("FAIL:effect drift")
    print("PASS: CoVirtualLiveness + CoStallMesh R0")

if __name__=="__main__":
    main()
