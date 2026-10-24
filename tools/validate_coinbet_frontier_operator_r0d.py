#!/usr/bin/env python3
import copy
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cotime/coinbet_frontier_operator_r0d.json")
REQUIRED = {
    "transition_id","domain","from_state","in_between_state","destination_candidate",
    "blocker","wake_condition","wake_satisfied","forbidden_jump","authority_ceiling",
    "evidence_status","next_safe_action"
}

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest().upper()

def valid_frontier(f):
    if not REQUIRED.issubset(f):
        return False
    if any(f[k] in ("", None) for k in REQUIRED - {"wake_satisfied"}):
        return False
    if not isinstance(f["wake_satisfied"], bool):
        return False
    if not f["wake_satisfied"] and f["next_safe_action"].startswith("ADVANCE"):
        return False
    if (
        f["wake_satisfied"]
        and f["blocker"] == "NONE"
        and f["next_safe_action"] == "HOLD_NOOP_UNTIL_WAKE"
    ):
        return False
    return True

def mutate(base, kind):
    x = copy.deepcopy(base)
    if kind == "drop_transition_id":
        x.pop("transition_id",None)
    elif kind == "drop_blocker":
        x.pop("blocker",None)
    elif kind == "drop_wake_condition":
        x.pop("wake_condition",None)
    elif kind == "drop_forbidden_jump":
        x.pop("forbidden_jump",None)
    elif kind == "drop_authority_ceiling":
        x.pop("authority_ceiling",None)
    elif kind == "drop_evidence_status":
        x.pop("evidence_status",None)
    elif kind == "wake_false_but_advance":
        x["wake_satisfied"] = False
        x["next_safe_action"] = "ADVANCE_TO_DESTINATION"
    elif kind == "empty_in_between":
        x["in_between_state"] = ""
    elif kind == "noop_despite_clear_wake":
        x["wake_satisfied"] = True
        x["blocker"] = "NONE"
        x["next_safe_action"] = "HOLD_NOOP_UNTIL_WAKE"
    else:
        fail("FAIL_UNKNOWN_MUTATION:" + kind)
    return x

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    src=d["source_bindings"]
    if git_blob(src["coinbet_doc_path"]) != src["coinbet_doc_blob_sha"]:
        fail("FAIL_COINBET_SOURCE_BIND")
    if git_blob(src["temporal_braid_doc_path"]) != src["temporal_braid_doc_blob_sha"]:
        fail("FAIL_TEMPORAL_BRAID_SOURCE_BIND")

    fs=d["frontiers"]
    if len({f["transition_id"] for f in fs}) != len(fs):
        fail("FAIL_DUPLICATE_TRANSITION_ID")
    if len({f["domain"] for f in fs}) != d["expected"]["domain_count"]:
        fail("FAIL_DOMAIN_COUNT")
    if len(fs) != d["expected"]["frontier_count"]:
        fail("FAIL_FRONTIER_COUNT")

    for f in fs:
        if not valid_frontier(f):
            fail("FAIL_VALID_FRONTIER:" + f.get("transition_id","UNKNOWN"))

    base=fs[0]
    negatives=d["negative_cases"]
    if len(negatives) != d["expected"]["negative_case_count"]:
        fail("FAIL_NEGATIVE_COUNT")
    for n in negatives:
        got=valid_frontier(mutate(base,n["mutation"]))
        if got is not n["expected_valid"]:
            fail("FAIL_NEGATIVE:" + n["id"])

    pr139=next(f for f in fs if f["transition_id"]=="F01_PR139_REAL_HOLDOUT")
    if pr139["next_safe_action"] != d["expected"]["pr139_frontier_action"]:
        fail("FAIL_PR139_FRONTIER_ACTION")

    held=sum(1 for f in fs if not f["wake_satisfied"])
    if held != d["expected"]["held_frontier_count"]:
        fail("FAIL_HELD_COUNT")

    if d["expected"]["effect_authority_changes"] != 0:
        fail("FAIL_AUTHORITY_EXPECTATION")

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    out={
      "STATE":"PASS_COINBET_FRONTIER_OPERATOR_R0D",
      "checked_out_head_sha":head,
      "fixture_semantic_sha256":canonical_sha(d),
      "domain_count":len({f["domain"] for f in fs}),
      "frontier_count":len(fs),
      "negative_case_count":len(negatives),
      "total_tests":len(fs)+len(negatives),
      "held_frontier_count":held,
      "effect_authority_changes":0,
      "pr139_real_holdout_frontier":{
        "in_between_state":pr139["in_between_state"],
        "blocker":pr139["blocker"],
        "wake_condition":pr139["wake_condition"],
        "next_safe_action":pr139["next_safe_action"]
      },
      "rails":d["rails"]
    }
    print(json.dumps(out,separators=(",",":")))

if __name__=="__main__":
    main()
