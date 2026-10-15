#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/ux/coux_refresh_trigger_canary_r0a.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if d["source_revision_after"] <= d["source_revision_before"]:
        raise SystemExit("FAIL:revision")
    for k in ["source_change_observed","projection_rebuilt","local_file_readback"]:
        if d[k] is not True:
            raise SystemExit("FAIL:"+k)
    for k in ["visible_ui_readback","persistent_watcher_installed","runtime_adoption"]:
        if d[k] is not False:
            raise SystemExit("FAIL:overclaim:"+k)
    if len(d["projection_sha256"]) != 64 or len(d["receipt_sha256"]) != 64:
        raise SystemExit("FAIL:sha")
    print("PASS: CoUX bounded refresh-trigger canary contract")
if __name__=="__main__": main()
