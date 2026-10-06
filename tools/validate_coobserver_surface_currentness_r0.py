#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/virtual-session/coobserver_surface_currentness_r0.json")

def fail(code):
    raise SystemExit(code)

def csha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def alive(state):
    return state in {"RECOVERABLE","WAKEABLE","MATERIALIZED","DORMANT"}

def surface_state(s):
    return "STALE_PROJECTION" if s["render_age_seconds"] > s["ttl_seconds"] else "FRESH_PROJECTION"

def semantic_disagreement(session):
    v = session["virtual_state"]
    virtual_alive = alive(v)
    for s in session["surfaces"]:
        claim = s["claim"]
        fresh = surface_state(s) == "FRESH_PROJECTION"
        if not fresh:
            return True
        if claim == "LIVE" and not virtual_alive:
            return True
        if claim == "DEAD" and virtual_alive:
            return True
    return False

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    observed = []
    for session in d["sessions"]:
        exp = session["expected"]
        if session["virtual_state"] != exp["display_virtual_state"]:
            fail("FAIL_VIRTUAL_STATE:" + session["id"])
        if alive(session["virtual_state"]) != exp["alive"]:
            fail("FAIL_ALIVE:" + session["id"])

        states = {s["id"]: surface_state(s) for s in session["surfaces"]}
        if states != exp["surface_states"]:
            fail("FAIL_SURFACE_STATE:" + session["id"])

        disagreement = semantic_disagreement(session)
        if disagreement != exp["projection_disagreement"]:
            fail("FAIL_DISAGREEMENT:" + session["id"])

        if session["virtual_state"] == "BLOCKED" and session["recovery_recipe_present"]:
            fail("FAIL_BLOCKED_WITH_RECOVERY_RECIPE:" + session["id"])

        observed.append({
            "id": session["id"],
            "logical_context_id": session["logical_context_id"],
            "virtual_state": session["virtual_state"],
            "alive": alive(session["virtual_state"]),
            "last_progress_age_seconds": session["last_progress_age_seconds"],
            "last_proof_age_seconds": session["last_proof_age_seconds"],
            "surface_states": states,
            "projection_disagreement": disagreement,
            "preferred_action": exp["preferred_action"]
        })

    if d["cluster_policy"]["do_not_count_tabs_as_independent_work"] is not True:
        fail("FAIL_TAB_COUNT_POLICY")

    head = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COOBSERVER_SURFACE_CURRENTNESS_R0",
        "checked_out_head_sha": head,
        "session_count": len(observed),
        "fixture_semantic_sha256": csha(d),
        "observed": observed,
        "cluster_policy": d["cluster_policy"],
        "ux_state": "UX_ACCEPTANCE_UNPROVEN",
        "x2_runtime_currentness": "UNPROVEN",
        "rails": d["rails"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
