#!/usr/bin/env python3
"""Check CoBook media-ops source-bound reference integrity without network writes."""
from pathlib import Path
import json
import sys

STATES = {"LANDED_MAIN","DRAFT_PR_NOT_MAIN","PROPOSED_NOT_EXECUTED"}
def check(root: Path) -> list[str]:
    errors=[]
    file=root/"ai"/"cobook-media-ops-r0.json"
    data=json.loads(file.read_text(encoding="utf-8"))
    if data.get("schema")!="CoBook.MediaOpsRegister.v0.1-candidate":
        errors.append("bad schema")
    if data.get("policy",{}).get("audio")!="SILENT_UNTIL_EXPLICIT_OPT_IN":
        errors.append("silent-first audio invariant missing")
    ids=set()
    for entry in data.get("references",[]):
        eid=entry.get("id")
        if not isinstance(eid,str) or not eid or eid in ids:
            errors.append("duplicate/missing reference ID")
        ids.add(eid)
        state=entry.get("state")
        if state not in STATES:
            errors.append("invalid state")
        if state=="LANDED_MAIN":
            p=entry.get("path")
            if not p or p.startswith("/") or ".." in Path(p).parts or not (root/p).is_file():
                errors.append("missing/unsafe main file: "+str(p))
        if state=="DRAFT_PR_NOT_MAIN" and not isinstance(entry.get("pr"),int):
            errors.append("draft without numeric PR")
    if not any(r.get("id")=="book:field-guide" and r.get("state")=="LANDED_MAIN" for r in data.get("references",[])):
        errors.append("existing public reader not linked")
    if not data.get("nonclaims"):
        errors.append("nonclaims missing")
    return errors

if __name__=="__main__":
    root=Path(__file__).resolve().parents[1]
    errors=check(root)
    print(json.dumps({"state":"FAIL" if errors else "PASS","errors":errors,"checked":"CoBook MediaOps candidate reference integrity"},indent=2))
    sys.exit(1 if errors else 0)
