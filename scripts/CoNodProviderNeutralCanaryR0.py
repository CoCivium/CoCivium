#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def require(cond: bool, msg: str):
    if not cond:
        raise SystemExit("FAIL:" + msg)

conod = load("ai/conod-dynamic-wave-r2.json")
aura = load("ai/coavnim-cognitive-aura-r0.json")
ui = load("ai/fixtures/conod-coaura-synthetic-r0.json")
failover = load("ai/fixtures/conod-provider-neutral-failover-r0.json")
github_surface = load("ai/github-relational-surface-r0.json")

require(conod["semantics"]["authority_expansion"] is False, "CONOD_AUTHORITY_EXPANSION")
require(conod["semantics"]["physical_width"] == "ADAPTIVE", "CONOD_PHYSICAL_WIDTH_NOT_ADAPTIVE")
require(conod["semantics"]["logical_parallelity"] == "ADAPTIVE_LARGE", "CONOD_LOGICAL_PARALLELITY")
require("RECURSIVE_IMPROVEMENT_NE_SELF_AUTHORITY" in conod["rails"], "CONOD_RECURSION_RAIL_MISSING")

seq = ui["wave"]["sequence"]
logical = ui["wave"]["logical_lanes"]
max_width = max(int(x["physical_width"]) for x in seq)
require(logical > max_width, "LOGICAL_PARALLELITY_NOT_GREATER_THAN_PHYSICAL_WIDTH")
require(seq[0]["state"] == "QUIET" and seq[-1]["state"] == "QUIET", "UI_WAVE_NOT_QUIESCENT_BOUNDED")
require("HIDDEN_CHAIN_OF_THOUGHT" in ui["forbidden_fields"], "UI_HIDDEN_COT_NOT_FORBIDDEN")
require("NO_HIDDEN_CHAIN_OF_THOUGHT_FIELD" in ui["acceptance"], "UI_HIDDEN_COT_ACCEPTANCE_MISSING")

privacy = set(aura["reasoning_privacy"])
require("COGNITIVE_PROJECTION_NE_HIDDEN_CHAIN_OF_THOUGHT" in privacy, "AURA_COT_RAIL_MISSING")
require(aura["collective_nonclaim"] == "COLLECTIVE_AURA_NE_COLLECTIVE_PERSON", "AURA_COLLECTIVE_NONCLAIM")
require(aura["observer_filter_required"] is True, "AURA_OBSERVER_FILTER_NOT_REQUIRED")

routes = failover["logical_wave"]["initial_routes"]
require(sum(int(v) for v in routes.values()) == int(failover["logical_wave"]["total_lanes"]), "FAILOVER_INITIAL_ROUTE_SUM")
sf = failover["synthetic_provider_failure"]
require(int(sf["already_completed"]) + int(sf["pending"]) == int(sf["provider_lanes"]), "FAILOVER_PROVIDER_ACCOUNTING")
require(sum(int(v) for v in sf["reroute"].values()) == int(sf["pending"]), "FAILOVER_REROUTE_ACCOUNTING")
require(sf["authority_expansion"] is False, "FAILOVER_AUTHORITY_EXPANSION")
require(int(sf["human_action_required"]) == 0, "FAILOVER_HUMAN_LOAD_BALANCING")
require("LOGICAL_LANE_IDENTITY_SURVIVES_ROUTE_FAILURE" in failover["expected_checks"], "FAILOVER_IDENTITY_CHECK_MISSING")
ep = failover["synthetic_externality_pacing"]
disp = ep["disposition"]
require(int(disp["materialize_now"]) <= int(ep["observed_receiver"]["max_safe_concurrency"]), "EXTERNALITY_IMMEDIATE_LOAD_EXCEEDS_BOUND")
require(sum(int(v) for v in disp.values()) == int(ep["planned_external_requests"]), "EXTERNALITY_DISPOSITION_ACCOUNTING")
require(float(ep["codoppler_candidate"]["apparent_rate_ratio"]) >= 1.0, "CODOPPLER_SYNTHETIC_RATIO")
require(ep["authority_expansion"] is False, "EXTERNALITY_AUTHORITY_EXPANSION")
require(int(ep["human_load_balancing_actions"]) == 0, "EXTERNALITY_HUMAN_LOAD_BALANCING")
require("CODOPPLER_RELATION_NE_PHYSICAL_DOPPLER_MECHANISM" in conod["rails"], "CODOPPLER_RAIL_MISSING")
require("UNKNOWN_EXTERNALITY_NE_ZERO_EXTERNALITY" in conod["rails"], "EXTERNALITY_UNKNOWN_RAIL_MISSING")
require("PACING_CONTROLLER_NE_FLAP" in conod["rails"], "EXTERNALITY_HYSTERESIS_RAIL_MISSING")

require("GITHUB_NE_COALL_TOTALITY" in github_surface["rails"], "GITHUB_TOTALITY_RAIL_MISSING")
require("GITHUB_NE_CUSTODY_ROOT" in github_surface["rails"], "GITHUB_CUSTODY_RAIL_MISSING")
require("REPOSITORY_NE_ONTOLOGY" in github_surface["rails"], "GITHUB_ONTOLOGY_RAIL_MISSING")
require("PR_NE_CANON" in github_surface["rails"], "GITHUB_PR_CANON_RAIL_MISSING")
require("CI_PASS_NE_RUNTIME" in github_surface["rails"], "GITHUB_CI_RUNTIME_RAIL_MISSING")
require(github_surface["conod_relation"]["role"] == "ONE_ADMISSIBLE_RECEIVER_OR_MATERIALIZATION_SURFACE", "GITHUB_CONOD_ROLE")
require("REPOSITORY" in github_surface["temporal_currentness"]["bind"] and "COMMIT_SHA" in github_surface["temporal_currentness"]["bind"], "GITHUB_CURRENTNESS_BIND_MISSING")
require(github_surface["projection_compilation"]["principle"] == "RELATION_OR_OBJECT_PRECEDES_ANY_ONE_GITHUB_PROJECTION", "GITHUB_RELATION_FIRST_PRINCIPLE")
require(github_surface["projection_compilation"]["reverse_navigation"].startswith("GITHUB_PROJECTION_SHOULD_POINT_BACK"), "GITHUB_REVERSE_NAVIGATION_MISSING")
require("RELATION_PERSISTS__BINDING_EVOLVES" in github_surface["projection_compilation"]["rails"], "GITHUB_REBIND_RAIL_MISSING")
require("PROJECTION_NE_SOURCE" in github_surface["projection_compilation"]["rails"], "GITHUB_PROJECTION_SOURCE_RAIL_MISSING")
require("REPO_BOUNDARY_NE_SEMANTIC_BOUNDARY" in github_surface["cross_repo_relation_graph"]["rails"], "GITHUB_CROSS_REPO_BOUNDARY_RAIL_MISSING")


print(json.dumps({
    "STATE":"PASS_BOUNDED_STATIC_CONOD_PROVIDER_NEUTRAL_CANARY",
    "LOGICAL_LANES":logical,
    "MAX_SYNTHETIC_PHYSICAL_WIDTH":max_width,
    "FAILOVER_TOTAL_LANES":failover["logical_wave"]["total_lanes"],
    "PROVIDER_PENDING_REROUTED_OR_HELD":sf["pending"],
    "AUTHORITY_EXPANSIONS":0,
    "HUMAN_LOAD_BALANCING_ACTIONS":0,
    "HIDDEN_CHAIN_OF_THOUGHT_FIELDS_ALLOWED":0,
    "GITHUB_RELATIONAL_SURFACE_INVARIANTS":"PASS",
    "EXTERNALITY_PACING_INVARIANTS":"PASS",
    "NEXT":"INDEPENDENT_RUNTIME_OR_X2_LOCAL_CANARY_WHEN_ROUTE_AVAILABLE"
}, separators=(",",":")))
