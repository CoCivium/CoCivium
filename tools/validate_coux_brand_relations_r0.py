#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/ux/coux_brand_relations_r0.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    ux=d["ux"]; br=d["brand"]
    if ux["visible_state_observed_stale"] is not True:
        raise SystemExit("FAIL:staleness evidence")
    if ux["semantic_state_inferred_stale"] is not False:
        raise SystemExit("FAIL:semantic overclaim")
    if ux["automatic_refresh_proven"] is not False:
        raise SystemExit("FAIL:auto refresh overclaim")
    if br["exact_same_logo_required_everywhere"] is not False:
        raise SystemExit("FAIL:identity collapse")
    if br["unrelated_logos_required"] is not False:
        raise SystemExit("FAIL:family fragmentation")
    if br["shared_authority_inferred"] is not False:
        raise SystemExit("FAIL:authority collapse")
    if br["public_rebrand_authorized"] is not False:
        raise SystemExit("FAIL:public effect drift")
    if br["candidate_default"]!="SHARED_VISUAL_GRAMMAR_PLUS_CORE_SIGNET_PLUS_TYPED_DERIVATIVES":
        raise SystemExit("FAIL:brand relation")
    print("PASS: UX currentness and CoSignet family relation contract")

if __name__=="__main__":
    main()
