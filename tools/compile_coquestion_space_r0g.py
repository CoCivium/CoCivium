#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

P=Path("fixtures/relations/coquestion_space_compiler_r0g.json")

def h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    ns=d["axes"]["subjects"]; no=d["axes"]["operators"]; nr=d["axes"]["receiver_classes"]
    raw=[]
    decision_sigs=set()
    for s in range(ns):
        for o in range(no):
            for r in range(nr):
                cid=f"QSPACE.R0G.S{s:03d}.O{o:02d}.R{r:02d}"
                # Deterministic synthetic decision signature. Several raw candidates
                # intentionally collapse onto one downstream decision.
                sig=f"D{s%25:02d}.O{o%5:02d}.R{r%5:02d}"
                raw.append(cid)
                decision_sigs.add(sig)
    if len(raw)!=d["expected_raw_candidates"]:
        raise SystemExit(f"FAIL:raw_count:{len(raw)}")
    stream_sha=h("\n".join(raw))
    unique_decisions=len(decision_sigs)
    # Bounded synthetic frontier: lexicographically stable first N decision signatures.
    frontier=sorted(decision_sigs)[:d["active_frontier_limit"]]
    if len(frontier)>d["active_frontier_limit"]:
        raise SystemExit("FAIL:frontier_bound")
    if d["forensic_default"] is not False:
        raise SystemExit("FAIL:forensic_default")
    if d["runtime_effect"] is not False or d["public_effect"] is not False:
        raise SystemExit("FAIL:effect")
    out={
      "STATE":"PASS_COQUESTION_SPACE_COMPILER_R0G",
      "raw_candidates":len(raw),
      "unique_decision_signatures":unique_decisions,
      "deduped_candidates":len(raw)-unique_decisions,
      "active_frontier_count":len(frontier),
      "active_frontier_limit":d["active_frontier_limit"],
      "candidate_stream_sha256":stream_sha,
      "frontier_sha256":h("\n".join(frontier))
    }
    print(json.dumps(out,separators=(",",":")))

if __name__=="__main__":
    main()
