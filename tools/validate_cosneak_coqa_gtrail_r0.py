#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/relations/cosneak_coqa_gtrail_r0.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    q=d["qa_loop"]; g=d["grail"]; t=d["gtrail"]
    if q["mandatory_infinite_loop"] is not False:
        raise SystemExit("FAIL: forced infinite loop")
    for k in ["stable_identity_required","currentness_required","provenance_required"]:
        if q[k] is not True:
            raise SystemExit("FAIL:"+k)
    if g["global_broadcast_required"] is not False:
        raise SystemExit("FAIL: global broadcast")
    if g["ownership_transferred_to_grail"] is not False:
        raise SystemExit("FAIL: GRAIL ownership")
    if t["established_repo_meaning_found"] is not False or t["candidate_only"] is not True:
        raise SystemExit("FAIL: GTRAIL lineage overclaim")
    if t["synonymous_with_grail"] is not False:
        raise SystemExit("FAIL: GTRAIL/GRAIL collapse")
    if t["trace_implies_truth"] is not False or t["path_implies_causation"] is not False:
        raise SystemExit("FAIL: trace epistemic overclaim")
    if len(d["cosneak_classes"]) < 8:
        raise SystemExit("FAIL: weak sneak coverage")
    print("PASS: CoSneak + CoQ&A loop + GTRAIL candidate relations R0")

if __name__=="__main__":
    main()
