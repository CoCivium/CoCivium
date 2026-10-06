#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
P=Path("fixtures/theory/cogodlist_discovery_field_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    rows=[]
    for l in d["lenses"]:
        for o in d["operators"]:
            for s in d["scales"]:
                rows.append(f"{l}|{o}|{s}")
    if len(rows)!=d["expected_candidates"] or len(set(rows))!=1000:
        raise SystemExit("FAIL:1000x field")
    if d["active_compute_required"] or d["metaphysical_truth_claim"] or d["runtime_effect"] or d["public_effect"] or d["financial_effect"]:
        raise SystemExit("FAIL:effect/truth overclaim")
    print(json.dumps({
      "STATE":"PASS_COGODLIST_DISCOVERY_FIELD_R0",
      "candidate_count":len(rows),
      "candidate_set_sha256":hashlib.sha256("\n".join(rows).encode()).hexdigest().upper(),
      "active_compute_required":False
    },separators=(",",":")))
if __name__=="__main__": main()
