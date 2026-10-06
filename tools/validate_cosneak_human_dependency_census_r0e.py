#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cosneak_human_dependency_census_r0e.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["files_scanned"] != 263:
        raise SystemExit("FAIL:files")
    expected={"COPYPASTE":(8,21),"DOWNLOAD":(14,48),"MANUAL":(11,37),"REFRESH":(11,25),"RICK_ACTION":(0,0),"HUMAN_GATE":(0,0)}
    for k,(f,m) in expected.items():
        if d["counts"][k]["files"]!=f or d["counts"][k]["mentions"]!=m:
            raise SystemExit("FAIL:"+k)
    for k in ["live_dependency_proven","causal_blocker_proven","repair_performed"]:
        if d[k] is not False:
            raise SystemExit("FAIL:overclaim:"+k)
    if len(d["receipt_sha256"]) != 64:
        raise SystemExit("FAIL:sha")
    print("PASS: CoSneak human dependency signal census R0E")
if __name__=="__main__": main()
