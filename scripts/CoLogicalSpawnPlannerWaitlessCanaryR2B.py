#!/usr/bin/env python3
from CoLogicalSpawnPlanner import compile_plan

LANES = {
    "domains": [
        ["CoSession+", ["CoCivium"], "VIRTUAL_AND_MATERIALIZED_SESSION_ECOLOGY"]
    ]
}
REPOS = {
    "repositories": [
        {"repo": "CoCivium/CoCivium", "visibility": "public"}
    ]
}

base = {
    "session_id": "WaitlessCanary",
    "observed_at": "2026-10-14T22:45:25Z",
    "domain": ["CoSession+"],
    "epistemic_class": "PLANNED",
    "source_refs": ["fixture:waitless-r2b"],
    "target_surfaces": ["CoCivium"],
    "authority_ceiling": "CANDIDATE_ONLY",
    "next_receiver": "CoSession waitless verifier",
}

effect_gated = dict(base)
effect_gated.update({
    "delta_id": "waitless-effect-gated",
    "subject": "held downstream effect",
    "relation": "VERIFY_WITHOUT_EXECUTING_EFFECT",
    "mutation_class": "EFFECT_GATED",
    "confidentiality": "PUBLIC",
})

confidentiality_collision = dict(base)
confidentiality_collision.update({
    "delta_id": "waitless-private-collision",
    "subject": "private payload targeting public surface",
    "relation": "MUST_FAIL_CLOSED",
    "mutation_class": "BRANCH_MUTATE",
    "confidentiality": "PRIVATE",
})

plan = compile_plan([effect_gated, confidentiality_collision], LANES, REPOS)
by_id = {c["recovery_pointer"]: c for c in plan["contracts"]}

shadow = by_id["waitless-effect-gated"]
blocked = by_id["waitless-private-collision"]

assert shadow["role"] == "VERIFIER"
assert shadow["materialization_state"] == "SHADOW"
assert shadow["lease"]["effect_lease"] == "NONE"
assert shadow["lease"]["mode"] == "SHADOW"
assert shadow["budget"]["max_effectful_mutations"] == 0

assert blocked["materialization_state"] == "BLOCKED"
assert "CONFIDENTIALITY_PUBLIC_TARGET_COLLISION:CoCivium" in blocked["uncertainty"]

assert plan["coverage"]["shadow_contracts"] == 1
assert plan["coverage"]["blocked_contracts"] == 1
assert plan["effects"]["authority_changes"] == 0
assert plan["effects"]["repo_mutations_executed"] == 0

print("SELFTEST=PASS_EFFECT_HELD_WORK_SHADOWABLE__VALIDATION_FAILURE_BLOCKED__ZERO_EFFECTS")
