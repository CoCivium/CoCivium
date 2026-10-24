#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/coq40_deterministic_probe_execution_r0u.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["probe_kind"]!="EXACT_CURRENTNESS_READ": raise SystemExit("FAIL:probe")
    if d["search_matches"]!=22: raise SystemExit("FAIL:matches")
    if d["current_receiver_binding_proven"] is not False: raise SystemExit("FAIL:binding overclaim")
    if d["live_receiver_reference_found"] is not False: raise SystemExit("FAIL:live reference overclaim")
    if any(d["effects"].values()): raise SystemExit("FAIL:effect")
    if d["persistent_machine_owned_worker_proven"] or d["chatgpt_independent_orchestration_proven"]:
        raise SystemExit("FAIL:autonomy overclaim")
    print("PASS: Q40 deterministic probe execution R0U")
if __name__=="__main__": main()
