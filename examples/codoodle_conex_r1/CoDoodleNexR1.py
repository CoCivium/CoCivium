#!/usr/bin/env python3
"""CoDoodle/CoNex R1: deterministic, no-effect, addressable candidate frontier.

This deliberately NEVER launches workers, talks to models, reads devices or the
network, or infers truth from a story. Python 3.9+ standard library only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from functools import reduce
from operator import mul

SCHEMA = "CoDoodle.CoNex.CandidateFrontier.R1"
OPERATORS = (
    "ELSE", "NOT", "INVERSE", "COMPLEMENT", "NULL", "OUTSIDE", "COUNTERFACTUAL",
    "OBSERVER_SHIFT", "TIME_SHIFT", "RENDER_SHIFT", "SUBSTRATE_SHIFT", "SCALE_SHIFT",
    "PRIOR_COMPARE", "FALSIFIER", "ACCESSIBILITY", "RANDOM_MUTATION", "RECEIVER_SHIFT", "RECOVERY",
)
# Syntactic axes, not a roster of valid or meaningful experiments.
AXES = {
    "operator": OPERATORS,
    "observer": ("HUMAN", "MACHINE", "OUTSIDER", "FUTURE", "HISTORIAN", "SKEPTIC", "CHILD_ACCESSIBLE", "MULTI", "UNKNOWN"),
    "temporal": ("PAST", "PRESENT", "FORECAST", "COUNTERFACTUAL", "ANTI_HISTORY", "SUCCESSOR", "RECOVERY"),
    "surface": ("TEXT", "GRAPH", "ORB", "GLYPH", "AUDIO_PLAN", "VIDEO_STORYBOARD", "SPEC", "ACCESSIBLE_UI"),
    "substrate": ("DETERMINISTIC_LOCAL", "OLLAMA_LOCAL", "CLAUDE_API", "OPENAI_COMPATIBLE", "PI_ADAPTER", "HUMAN_REVIEW"),
    "challenge": ("NULL_BASELINE", "COUNTEREXAMPLE", "INVERSE", "REPLICATION", "RFI_CONTROL", "CONTRADICTION", "PRIVACY", "RECOVERY"),
    "scale": ("ONE", "TWO", "EIGHT", "THIRTY_TWO", "THOUSAND_LOGICAL", "MILLION_LOGICAL", "TRILLION_LOGICAL", "OPEN_ENDED"),
    "relation": ("IN", "OUT", "CONTAINS", "EXCLUDES", "SIMILAR", "DIFFERS", "PRECEDES", "FOLLOWS", "DEPENDS", "CHALLENGES", "VISUALIZES", "UNKNOWN"),
    "scenario": ("ENGINEERING_DEVICE", "INTERSTICE_UI", "ET_TECHNOSIGNATURE", "G_D_PHILOSOPHY", "SYNTHKIND_FICTION"),
    "audience": ("NEW_USER", "TECHNICAL", "ACCESSIBILITY", "RESEARCH", "CO_STEWARD", "EDUCATION", "PUBLIC"),
    "uncertainty": ("UNKNOWN", "OBSERVED", "HYPOTHETICAL", "CONTRADICTED", "WITHHELD", "NOT_APPLICABLE"),
    "salt": tuple(range(256)),
}
LOGICAL_TOTAL = math.prod(len(v) for v in AXES.values())
MAX_FRONTIER = 32
MAX_SAMPLE = 128
MAX_BENCHMARK = 50000
TURTLE_TEMPLATE = {"max_depth": 2, "max_review_rounds": 2,
                   "shared_parent_budget": True, "independent_reviewer_assigned": False,
                   "authority_inheritance": "NEVER_INCREASE"}
MUST_EXERCISE = (
    ("NULL", "ENGINEERING_DEVICE", "NULL_BASELINE"),
    ("INVERSE", "ENGINEERING_DEVICE", "COUNTEREXAMPLE"),
    ("FALSIFIER", "ET_TECHNOSIGNATURE", "RFI_CONTROL"),
    ("COUNTERFACTUAL", "G_D_PHILOSOPHY", "CONTRADICTION"),
    ("RENDER_SHIFT", "SYNTHKIND_FICTION", "PRIVACY"),
    ("ACCESSIBILITY", "INTERSTICE_UI", "PRIVACY"),
)
ROUTES = {
    "DETERMINISTIC_LOCAL": {"connection": "RUNNABLE_SHADOW_ONLY", "requires": "NONE", "external_effects": 0},
    "OLLAMA_LOCAL": {"connection": "HELD_NO_MODEL_HEALTH_PROOF", "requires": "CONSENTED_LOCAL_MODEL_AND_BUDGET", "external_effects": 0},
    "CLAUDE_API": {"connection": "HELD_NO_AUTHORIZED_API_CREDENTIAL", "requires": "USER_OWNED_API_KEY_VAULT_AND_SPEND_CAP", "external_effects": 0},
    "OPENAI_COMPATIBLE": {"connection": "HELD_NO_ADAPTER_OR_CAPABILITY_PROOF", "requires": "AUTHORIZED_ENDPOINT_AND_BUDGET", "external_effects": 0},
    "PI_ADAPTER": {"connection": "HELD_NO_ADAPTER_OR_IDENTITY_PROOF", "requires": "AUTHORIZED_ADAPTER_AND_BUDGET", "external_effects": 0},
    "HUMAN_REVIEW": {"connection": "HELD_NO_INDEPENDENT_REVIEWER_ASSIGNMENT", "requires": "OPT_IN_IDENTIFIED_REVIEWER", "external_effects": 0},
}
SCENARIOS = {
    "ENGINEERING_DEVICE": {"epistemic": "ENGINEERING_CANDIDATE", "proof": "BOUNDED_POLICY_TEST_ONLY"},
    "INTERSTICE_UI": {"epistemic": "ENGINEERING_CANDIDATE", "proof": "BOUNDED_POLICY_TEST_ONLY"},
    "ET_TECHNOSIGNATURE": {"epistemic": "EMPIRICAL_HYPOTHESIS", "proof": "HELD_NO_ACTUAL_DATA_OR_INDEPENDENT_REPLICATION"},
    "G_D_PHILOSOPHY": {"epistemic": "PHILOSOPHICAL_OR_METAPHORICAL", "proof": "NOT_AN_EMPIRICAL_ENTITY_FINDER"},
    "SYNTHKIND_FICTION": {"epistemic": "SPECULATIVE_STORY", "proof": "NO_VERIFIED_PRIMARY_DECLARATION_OR_FINISHED_MEDIA"},
}
NONCLAIMS = [
    "DESCRIPTOR_NE_ELIGIBLE_EXPERIMENT", "STORY_NE_OBSERVATION", "G_D_FRAME_NE_DETECTED_ENTITY",
    "ET_CANDIDATE_NE_ET_DETECTION", "CLAUDE_ACCOUNT_NE_ASSISTANT_IDENTITY", "ADAPTER_DESCRIPTOR_NE_LOGIN",
    "NO_SESSION_SPAWN", "NO_NETWORK_OR_PROVIDER_CALLS", "NO_DEVICE_INPUT_CAPTURE",
    "LOGICAL_POPULATION_NE_LIVE_WORKERS", "NO_INDEPENDENT_RECEIVER_ACK", "MICROSECOND_TARGET_NE_PROVEN_USER_BENEFIT",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(data) -> bytes:
    return (json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def validate_fixture(source):
    if not isinstance(source, dict) or source.get("schema") != "CoDoodle.SourcePublicSynthetic.R1":
        raise ValueError("HOLD_BAD_SOURCE_SCHEMA")
    if source.get("privacy") != "PUBLIC_SYNTHETIC" or source.get("authority") != "NONE":
        raise ValueError("HOLD_NO_PRIVATE_OR_EFFECTFUL_SOURCE")
    if not isinstance(source.get("summary"), str) or not 8 <= len(source["summary"]) <= 1200:
        raise ValueError("HOLD_BAD_SOURCE_SUMMARY")
    if not isinstance(source.get("source_id"), str) or len(source["source_id"]) > 96:
        raise ValueError("HOLD_BAD_SOURCE_ID")
    if source.get("credential_material") or source.get("raw_input"):
        raise ValueError("HOLD_NO_CREDENTIALS_OR_RAW_PRIVATE_INPUT")
    allowed = {"schema", "source_id", "privacy", "authority", "summary",
               "unverified_references", "promised_effects"}
    if set(source) - allowed:
        raise ValueError("HOLD_UNKNOWN_UNREVIEWED_SOURCE_FIELDS")
    if source.get("promised_effects", 0) != 0:
        raise ValueError("HOLD_SOURCE_EFFECT_AUTHORITY")
    if not isinstance(source.get("unverified_references", []), list):
        raise ValueError("HOLD_BAD_UNVERIFIED_REFERENCES")
    return source


def decode(index: int) -> dict:
    if not isinstance(index, int) or not 0 <= index < LOGICAL_TOTAL:
        raise ValueError("HOLD_DESCRIPTOR_INDEX_OUT_OF_RANGE")
    parts = {}
    for key, choices in reversed(list(AXES.items())):
        index, offset = divmod(index, len(choices))
        parts[key] = choices[offset]
    return {key: parts[key] for key in AXES}


def encode(parts: dict) -> int:
    if set(parts) != set(AXES):
        raise ValueError("HOLD_DESCRIPTOR_AXIS_MISMATCH")
    out = 0
    for name, choices in AXES.items():
        if parts[name] not in choices:
            raise ValueError("HOLD_UNKNOWN_AXIS_CHOICE")
        out = out * len(choices) + choices.index(parts[name])
    return out


def indices(seed: str, count: int):
    if not isinstance(count, int) or not 0 <= count <= MAX_SAMPLE:
        raise ValueError("HOLD_MAX_SAMPLE_128")
    entropy = int(sha(seed.encode("utf-8")), 16)
    start = entropy % LOGICAL_TOTAL
    stride = ((entropy >> 64) % (LOGICAL_TOTAL - 1)) + 1
    while math.gcd(stride, LOGICAL_TOTAL) != 1:
        stride += 1
    return [(start + stride * i) % LOGICAL_TOTAL for i in range(count)]


def select_candidates(source: dict, seed: str, limit: int) -> dict:
    validate_fixture(source)
    if not isinstance(limit, int) or limit < 0 or limit > MAX_FRONTIER:
        raise ValueError("HOLD_MAX_FRONTIER_32")
    src_digest = sha(canonical(source))
    # Materialize a bounded, seed-strided sample then score a small reserve.
    # This intentionally does not enumerate, validate, or execute the logical field.
    sample_size = min(MAX_SAMPLE, max(limit, 4 * limit))
    raw = indices(src_digest + ":" + seed, sample_size)
    # Reserve a few broad, negative and speculative branches even when random sampling misses them.
    if limit:
        base = decode(raw[0]); forced = []
        for op, scenario, challenge in MUST_EXERCISE[:limit]:
            variant = dict(base)
            variant.update(operator=op, scenario=scenario, challenge=challenge)
            if scenario in ("ENGINEERING_DEVICE", "INTERSTICE_UI"):
                variant["substrate"] = "DETERMINISTIC_LOCAL"
            if scenario in ("G_D_PHILOSOPHY", "SYNTHKIND_FICTION"):
                variant["uncertainty"] = "NOT_APPLICABLE"
            elif scenario == "ET_TECHNOSIGNATURE":
                variant["uncertainty"] = "HYPOTHETICAL"
            forced.append(encode(variant))
        raw = forced + raw
    seen = set(); items = []; duplicates = 0
    for idx in raw:
        if idx in seen:
            duplicates += 1; continue
        seen.add(idx)
        axis = decode(idx); scenario = SCENARIOS[axis["scenario"]]
        is_local = axis["scenario"] in ("ENGINEERING_DEVICE", "INTERSTICE_UI")
        route = ROUTES[axis["substrate"]]
        eligible = is_local and axis["substrate"] == "DETERMINISTIC_LOCAL"
        descriptor = {
            "candidate_id": sha((src_digest + ":" + str(idx)).encode())[:20],
            "logical_index": str(idx), "axes": axis,
            "epistemic_class": scenario["epistemic"], "proof_boundary": scenario["proof"],
            "provider_route": route["connection"],
            "micro_canary_eligible": eligible,
            "authority": "NONE", "effects": {"provider_calls": 0, "network": 0, "devices": 0, "emails": 0, "workers": 0},
            "review_state": "PASS_SHADOW_POLICY_ONLY" if eligible else "HELD_NO_QUALIFIED_EXECUTOR_OR_EMPIRICAL_EVIDENCE",
            "score": score_candidate(axis, eligible),
        }
        items.append(descriptor)
    forced_ids = {sha((src_digest + ":" + str(idx)).encode())[:20] for idx in raw[:min(limit, len(MUST_EXERCISE))]}
    protected = [x for x in items if x["candidate_id"] in forced_ids]
    extras = [x for x in items if x["candidate_id"] not in forced_ids]
    extras.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    items = (protected + extras)[:limit]
    return {"schema": SCHEMA, "source_sha256": src_digest, "seed": seed,
            "total_syntactic_descriptors": str(LOGICAL_TOTAL), "selected": items,
            "selected_count": len(items), "considered_sample_count": len(seen),
            "duplicates_seen": duplicates, "active_workers": 0, "operator_count": len(OPERATORS),
            "special_scenario_count": sum(x["axes"]["scenario"] in ("ET_TECHNOSIGNATURE", "G_D_PHILOSOPHY", "SYNTHKIND_FICTION") for x in items),
            "no_execution": True, "review_template": dict(TURTLE_TEMPLATE)}


def score_candidate(axis, eligible):
    # Heuristic only; scores do not qualify truth or spend. Fixed integer scale 0..100.
    base = 42
    if axis["operator"] in ("NULL", "INVERSE", "FALSIFIER", "PRIOR_COMPARE"):
        base += 17
    if axis["challenge"] in ("NULL_BASELINE", "COUNTEREXAMPLE", "RFI_CONTROL"):
        base += 12
    if axis["audience"] in ("NEW_USER", "ACCESSIBILITY"):
        base += 8
    if axis["substrate"] == "DETERMINISTIC_LOCAL":
        base += 8
    if not eligible:
        base -= 18
    if axis["scenario"] in ("G_D_PHILOSOPHY", "SYNTHKIND_FICTION"):
        base -= 14
    return max(0, min(100, base))


def turtle_admission(depth, rounds, parent_remaining, requested, authority="NONE"):
    """Pure shadow reviewer budget gate, not an instantiated panel."""
    if not all(isinstance(n, int) and not isinstance(n, bool) for n in
               (depth, rounds, parent_remaining, requested)):
        return {"status": "HELD", "reason": "UNKNOWN_BUDGET", "granted": 0}
    if authority != "NONE":
        return {"status": "HELD", "reason": "CHILD_MAY_NOT_RAISE_AUTHORITY", "granted": 0}
    if depth < 0 or depth > 2 or rounds < 0 or rounds > 2:
        return {"status": "HELD", "reason": "RECURSION_BOUND", "granted": 0}
    if parent_remaining < 0 or requested < 0 or requested > parent_remaining:
        return {"status": "HELD", "reason": "PARENT_BUDGET", "granted": 0}
    return {"status": "PASS_SHADOW", "reason": "BOUNDED_ONLY", "granted": requested}


def route_choice(name):
    if name not in ROUTES:
        raise ValueError("HOLD_UNKNOWN_ROUTE")
    return {"route": name, **ROUTES[name], "requested_calls": 0, "credentials_inspected": False}


def micro_canary(frontier):
    """Invariant evaluation only; zero data/model/device experiment execution."""
    selected = frontier["selected"]
    no_effects = all(all(v == 0 for v in x["effects"].values()) and x["authority"] == "NONE" for x in selected)
    unique = len({x["candidate_id"] for x in selected}) == len(selected)
    no_physics_promotion = all(x["review_state"].startswith("HELD") for x in selected if x["axes"]["scenario"] in ("ET_TECHNOSIGNATURE", "G_D_PHILOSOPHY", "SYNTHKIND_FICTION"))
    no_provider_claim = all(x["review_state"].startswith("HELD") for x in selected if x["axes"]["substrate"] != "DETERMINISTIC_LOCAL")
    tests = {"zero_outbound_or_device_effects": no_effects, "deduplicated_ids": unique,
             "no_story_or_ET_fact_promotion": no_physics_promotion,
             "non_local_adapters_held": no_provider_claim,
             "frontier_at_most_32": len(selected) <= MAX_FRONTIER,
             "descriptors_not_workers": frontier["active_workers"] == 0}
    return tests


def benchmark(rounds: int = 1200):
    if not isinstance(rounds, int) or not 16 <= rounds <= MAX_BENCHMARK:
        raise ValueError("HOLD_BENCHMARK_WORK_BUDGET")
    sample = indices("CoDoodle.Benchmark.R1", rounds if rounds <= 32 else 32)
    rawtimes = []; checksum = 0
    for i in range(rounds):
        idx = sample[i % len(sample)]
        start = time.perf_counter_ns()
        record = decode(idx)
        checksum += len(record["operator"])  # force materialization
        rawtimes.append(time.perf_counter_ns() - start)
    return {"op": "decode_one_mixed_radix_descriptor", "environment": platform.platform(),
            "python": platform.python_version(), "rounds": rounds,
            "median_ns": int(statistics.median(rawtimes)),
            "p95_ns": sorted(rawtimes)[math.ceil(0.95 * len(rawtimes)) - 1],
            "checksum": checksum,
            "not_measuring": ["real_model_throughput", "useful_experiments", "human_wall_time", "workers", "ET_data_processing"],
            "microsecond_target_met_for_this_decode_only": statistics.median(rawtimes) < 1000}


def exclusive(path: Path, data: bytes):
    with path.open("xb") as file:
        file.write(data)
        file.flush()
        os.fsync(file.fileno())
    if sha(path.read_bytes()) != sha(data):
        raise RuntimeError("HOLD_READBACK_MISMATCH")
    return sha(data)


def run(sourcefile: Path, seed: str, limit: int, root: Path, rounds: int):
    source = validate_fixture(json.loads(sourcefile.read_text(encoding="utf-8")))
    frontier = select_candidates(source, seed, limit)
    tests = micro_canary(frontier)
    same = select_candidates(source, seed, limit)
    tests["repeat_seed_same_bytes"] = canonical(frontier) == canonical(same)
    tests["different_seed_changed_frontier"] = (limit == 0 or canonical(frontier) != canonical(select_candidates(source, seed + ":other", limit)))
    tests["source_identity_sha_bound"] = frontier["source_sha256"] == sha(canonical(source))
    tests["nonempirical_g_d_stays_nonempirical"] = SCENARIOS["G_D_PHILOSOPHY"]["proof"] == "NOT_AN_EMPIRICAL_ENTITY_FINDER"
    tests["external_routes_held"] = all(route_choice(x)["requested_calls"] == 0 for x in ROUTES if x != "DETERMINISTIC_LOCAL")
    tests["no_active_workers"] = frontier["active_workers"] == 0
    tests["turtle_depth_cap"] = turtle_admission(3, 1, 2, 1)["status"] == "HELD"
    tests["turtle_budget_shared"] = turtle_admission(1, 1, 1, 2)["status"] == "HELD"
    tests["turtle_child_no_authority"] = turtle_admission(1, 1, 2, 1, "SEND")["status"] == "HELD"
    perf = benchmark(rounds)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = root / ("run_" + stamp + "_" + sha(seed.encode())[:6])
    path.mkdir(parents=True, exist_ok=False)
    source_sha = exclusive(path / "10_source.json", canonical(source))
    frontier_sha = exclusive(path / "20_frontier.json", canonical(frontier))
    perf_sha = exclusive(path / "30_benchmark.json", canonical(perf))
    pass_count = sum(bool(v) for v in tests.values())
    outcome = "PASS_SHADOW_LOCAL" if pass_count == len(tests) else "FAIL"
    event = {"schema": "CoAll.BenchmarkEvo.CoDoodleNex.R1", "observed_at": datetime.now(timezone.utc).isoformat(),
             "status": outcome, "test": "deterministic_generator_policy_only", "pass": pass_count, "total": len(tests),
             "source_sha256": source_sha, "frontier_sha256": frontier_sha,
             "benchmark_sha256": perf_sha, "logical_space": str(LOGICAL_TOTAL),
             "materialized_count": frontier["selected_count"], "active_workers": 0,
             "median_descriptor_decode_ns": perf["median_ns"], "scope": "isolated local deterministic benchmark", "nonclaims": NONCLAIMS}
    events = [event,
              {"schema": event["schema"], "observed_at": event["observed_at"], "status": "HELD", "test": "independent_X2_mouse_Claude_ET_feed_G_d_real_world_test", "hold_reason": "No authorized X2 bridge, provider credential, fresh scientific dataset/replication, or independent receiver in this no-effect run.", "nonclaims": NONCLAIMS},
              {"schema": event["schema"], "observed_at": event["observed_at"], "status": "HELD", "test": "time_to_first_useful_human_task", "hold_reason": "No independent participant performed the task or supplied human-time acceptance.", "nonclaims": NONCLAIMS}]
    e_sha = exclusive(path / "benchmark_evo.jsonl", ("".join(json.dumps(x, sort_keys=True) + "\n" for x in events)).encode())
    receipt = {"schema": "CoDoodle.CoNex.LocalReceipt.R1", "utc": event["observed_at"], "status": outcome,
               "checks": tests, "passes": pass_count, "total": len(tests),
               "source_sha256": source_sha, "frontier_sha256": frontier_sha, "benchmark_sha256": perf_sha,
               "events_sha256": e_sha, "runner_sha256": sha(Path(__file__).read_bytes()),
               "receiver_ack": False, "CoStead_landed": False, "independent_recovery": False,
               "no_external_effects": True, "actual_workers": 0, "nonclaims": NONCLAIMS}
    exclusive(path / "90_receipt.json", canonical(receipt))
    print(json.dumps({"state": outcome, "selected": frontier["selected_count"], "logical_space": str(LOGICAL_TOTAL),
                      "checks": pass_count, "total": len(tests), "median_decode_ns": perf["median_ns"],
                      "run": str(path), "sha256": frontier_sha, "external_calls": 0, "active_workers": 0}))
    if outcome != "PASS_SHADOW_LOCAL":
        raise SystemExit(2)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(Path(__file__).with_name("synthetic_source.json")))
    parser.add_argument("--seed", default="CoNex-R1-20261024")
    parser.add_argument("--limit", type=int, default=16)
    parser.add_argument("--output", default=str(Path(__file__).with_name("local_runs")))
    parser.add_argument("--bench-rounds", type=int, default=1200)
    args = parser.parse_args(argv)
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    run(Path(args.source), args.seed, args.limit, root, args.bench_rounds)

if __name__ == "__main__":
    main()
