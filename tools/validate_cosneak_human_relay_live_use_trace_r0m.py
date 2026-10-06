#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/cosneak_human_relay_live_use_trace_r0m.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if len(d["samples"]) != d["sample_count"]:
        raise SystemExit("FAIL:sample count")
    live=sum(1 for x in d["samples"] if x["live_human_relay_proven"])
    absent=sum(x["target_paths_checked_absent"] for x in d["samples"])
    if live != d["totals"]["proven_live_human_relay_dependencies"]:
        raise SystemExit("FAIL:live total")
    if absent != d["totals"]["referenced_paths_checked_absent"]:
        raise SystemExit("FAIL:absent path total")
    if live != 0 or absent != 3:
        raise SystemExit("FAIL:unexpected bounded evidence")
    if d["sampled_scope_closed"] is not True or d["global_census_complete"] is not False:
        raise SystemExit("FAIL:scope")
    if d["runtime_effect"] or d["public_effect"]:
        raise SystemExit("FAIL:effect")
    print("PASS: CoSneak Q10 human-relay live-use trace R0M")
if __name__=="__main__": main()
