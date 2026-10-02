#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/resilience/coexit_rights_data_erasure_r0.json")
def ready(s):
    return (
        s["unique_state"] is False
        and s["independent_reconstruction"] is True
        and s["billing_mapped"] is True
        and s["ownership_migrated"] is True
    )
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    for s in d["services"]:
        if ready(s) is not s["exit_ready"]:
            raise SystemExit("FAIL:"+s["id"])
    if any(d["destructive_effects"].values()):
        raise SystemExit("FAIL: destructive effect enabled")
    if len(d["claims"]) != 4:
        raise SystemExit("FAIL: claim boundary count")
    print("PASS: CoExitRights data-erasure and dependency-sunset policy")
if __name__=="__main__": main()
