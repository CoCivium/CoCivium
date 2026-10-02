#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cosneak_local_census_r0a.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["total_files"] != 265: raise SystemExit("FAIL:total")
    if d["stale_30d_count"] != 264: raise SystemExit("FAIL:stale")
    if d["latest_named_count"] != 216 or d["stale_latest_30d_count"] != 216:
        raise SystemExit("FAIL:latest")
    if d["causal_blocker_proven"] is not False or d["repair_performed"] is not False:
        raise SystemExit("FAIL:overclaim")
    if d["destructive_effects"] != 0: raise SystemExit("FAIL:effect")
    if len(d["receipt_sha256"]) != 64: raise SystemExit("FAIL:sha")
    print("PASS: CoSneak bounded local census R0A")
if __name__=="__main__": main()
