#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/resilience/codependency_census_triple_loss_r0.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["destructive_effects"] is not False:
        raise SystemExit("FAIL: destructive effect drift")
    for k in ["live_x2_census_claimed","live_account_census_claimed","current_offsite_custody_claimed"]:
        if d[k] is not False:
            raise SystemExit("FAIL: live claim drift:"+k)
    if len(d["scenarios"]) != 3:
        raise SystemExit("FAIL: scenario count")
    ids={c["id"] for c in d["capabilities"]}
    required={"PUBLIC_BOOTSTRAP","PRIVATE_DURABLE_CUSTODY","HUMAN_READABLE_RECOVERY","AUTHORITY_AND_SEMANTIC_DOCTRINE"}
    if not required.issubset(ids):
        raise SystemExit("FAIL: critical capability coverage")
    gaps=[c for c in d["capabilities"] if c["critical"] and c["disposition"]=="GAP"]
    if len(gaps) < 4:
        raise SystemExit("FAIL: expected critical gaps not surfaced")
    if len(d["priority_gaps"]) != 5:
        raise SystemExit("FAIL: priority gap count")
    print("PASS: documented triple-loss dependency census exposes continuity gaps without live-state overclaim")

if __name__=="__main__": main()
