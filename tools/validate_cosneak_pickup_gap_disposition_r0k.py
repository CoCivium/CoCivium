#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cosneak_pickup_gap_disposition_r0k.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if len(d["gaps"]) != 3:
        raise SystemExit("FAIL:gap count")
    if d["original_artifacts_rewritten"] or d["direct_pickup_retroactively_inferred"]:
        raise SystemExit("FAIL:historical rewrite/retroactive pickup")
    by={x["id"]:x for x in d["gaps"]}
    if by["coencounter_r0b"]["successor_pickup_proven"] is not True:
        raise SystemExit("FAIL:r0b successor")
    if by["coencounter_yield_r0a"]["successor_pickup_proven"] is not True:
        raise SystemExit("FAIL:r0a successor")
    if by["copulse_r0f"]["successor_pickup_proven"] is not False:
        raise SystemExit("FAIL:r0f overclaim")
    for x in d["gaps"]:
        if x["direct_pickup_original"] is not False:
            raise SystemExit("FAIL:direct pickup invented:"+x["id"])
        if x["current_blocker"] is not False:
            raise SystemExit("FAIL:blocker overclaim:"+x["id"])
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: CoSneak pickup-gap disposition R0K")
if __name__=="__main__": main()
