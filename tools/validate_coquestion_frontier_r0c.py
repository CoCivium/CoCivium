#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/coquestion_frontier_r0c.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    ids=[]
    for vals in d["categories"].values(): ids.extend(vals)
    if len(ids)!=d["question_count"] or sorted(ids)!=list(range(1,51)):
        raise SystemExit("FAIL:question frontier coverage")
    if len(d["election_dimensions"]) < 8:
        raise SystemExit("FAIL:election dimensions")
    if d["runtime_effect"] is not False or d["public_effect"] is not False:
        raise SystemExit("FAIL:effect drift")
    if "SCORE_FOR_DECISION_DELTA" not in d["default_loop"]:
        raise SystemExit("FAIL:selection loop")
    print("PASS: CoQuestionFrontier R0C")
if __name__=="__main__": main()
