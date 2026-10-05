#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/virtual-session/costallmesh_recovery_quorum_r0b.json")
def classify(x):
    if x.get("successor"): return "SUPERSEDED"
    if x.get("retry_count",0) >= 3: return "QUARANTINED"
    if x.get("progress"): return "ACTIVE"
    if x.get("heartbeat") and not x.get("progress"): return "STALLED"
    if x.get("recoverable") and not x.get("heartbeat"): return "DORMANT"
    return "UNKNOWN"
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    for c in d["cases"]:
        got=classify(c)
        if got!=c["expected"]: raise SystemExit(f"FAIL:{c['id']}:{got}")
    r=d["recovery"]
    if r["simultaneous_actuators_per_scope"] != 1 or r["nudge_per_lease"] != 1:
        raise SystemExit("FAIL:actuator quorum")
    if not r["backoff_required"] or not r["circuit_breaker_after_repeated_failure"]:
        raise SystemExit("FAIL:anti-storm")
    if r["restart_counts_as_recovery_success"] is not False:
        raise SystemExit("FAIL:restart overclaim")
    if d["runtime_actuation"] or d["provider_ui_mutation"] or d["persistent_watcher_installed"] or d["public_effect"]:
        raise SystemExit("FAIL:effect drift")
    print("PASS: CoStallMesh / CoRecoveryQuorum R0B")
if __name__=="__main__": main()
