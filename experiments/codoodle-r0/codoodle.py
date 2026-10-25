#!/usr/bin/env python3
"""CoDoodle -> typed experiment-descriptor adapter, synthetic shadow only.

No models, sensors, clipboard, keyboard hooks, network access, process spawn,
future prediction, scientific inference, or externally consequential effects.
Aims at CoExperimentSpacePreview/Selector interface, not a replacement scheduler.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import time
from pathlib import Path
from typing import Any

SCHEMA = "CoAll.CoDoodle.DescriptorAdapter.R0"
MAX_SOURCE_BYTES = 65_536
MAX_SAMPLE = 256
MAX_BENCH_ITERATIONS = 200_000
LANES = ("CHALLENGE", "EXPLORATION", "WEIRD", "REPLAY", "FAULT")
AXES = {
    "perspective": ("HUMAN_READER", "MODEL_SIMULATED", "ET_FICTIONAL", "ALTERNATE_OBSERVER"),
    "time_frame": ("HUMAN_ELAPSED", "EVENT_ORDER", "LOGICAL_ORDER", "HISTORICAL_REPLAY", "COUNTERFACTUAL_TIME"),
    "variation": ("ELSE", "NOT_ELSE", "INVERT", "BETTER", "CHALLENGE", "REPLAY"),
    "experiment_family": ("DEVICE_INPUT", "RELATIONAL_GRAPH", "RICH_MEDIA", "RESOURCE_ROUTING", "CLAIM_TEST", "ACCESSIBILITY"),
    "evidence_mode": ("SYNTHETIC_FIXTURE", "SOURCE_REPLAY", "NEGATIVE_CONTROL", "UNKNOWN"),
    "measurement": ("HUMAN_TIME", "FALSE_ACTIVATION", "CORRECTNESS", "PRIVACY", "RESOURCE_COST", "RECOVERY", "COMPREHENSION"),
    "projection": ("TEXT", "ORB", "MAP", "HEADLESS"),
    "fault_mode": ("NONE", "RECEIVER_UNAVAILABLE", "STALE_SOURCE", "MISSING_ACK", "PRIVACY_EXPOSURE"),
    "substrate": ("PURE_PYTHON", "STATIC_BROWSER", "SIMULATED_AGENT", "LOCAL_MODEL_CANDIDATE", "PROVIDER_CANDIDATE"),
}
TOPIC_KEYWORDS = {
    "DEVICE_INPUT": (r"\bkeyboard\b", r"\bmouse\b", r"\bthumb\b", r"\bperixx\b", r"\binput\b"),
    "RELATIONAL_GRAPH": (r"\bcomap\b", r"\brelations?\b", r"\bcoall\b"),
    "RICH_MEDIA": (r"\bmedia\b", r"\bdiagram\b", r"\borb\b", r"\bglyph\b"),
    "RESOURCE_ROUTING": (r"\bresource", r"\bparallel", r"\bworkers?\b", r"\bsessions?\b"),
    "CLAIM_TEST": (r"\bquantum\b", r"\bplanck\b", r"\bg_d\b", r"\btestab", r"\bcred", r"\bprovenance\b"),
    "ACCESSIBILITY": (r"\boptional\b", r"\baccessible\b", r"\bprivacy\b", r"\bwear\b"),
}
# Detect probable pasted credentials rather than merely mentioning credentials.
POTENTIAL_SECRET = re.compile(
    r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|"
    r"\b(?:password|api[_-]?key|client[_-]?secret)\s*[:=]\s*\S{6,}|"
    r"\bsk-[A-Za-z0-9_-]{20,}", re.IGNORECASE
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint(value: Any) -> str:
    return digest(canonical(value))


def parse_doodle(source: bytes) -> dict[str, Any]:
    if not isinstance(source, bytes) or not 0 < len(source) <= MAX_SOURCE_BYTES:
        raise ValueError("source must be 1..65536 bytes; no input truncation")
    try:
        content = source.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ValueError("source must be valid UTF-8") from exc
    if POTENTIAL_SECRET.search(content):
        raise ValueError("potential credential in input: held before transformation")
    folded = content.casefold()
    found = [name for name, patterns in TOPIC_KEYWORDS.items()
             if any(re.search(p, folded) for p in patterns)]
    symbolic = bool(re.search(r"\b(?:g_d|spiritual|aura|god|et|extraterrestrial)\b", folded))
    return {
        "schema": "CoAll.CoDoodle.ExplicitInputR0",
        "source_sha256": digest(source),
        "source_bytes": len(source),
        "topics_hint_only": found,
        "symbolic_or_speculative_terms_detected": symbolic,
        "semantic_certainty": "NONE_KEYWORD_HINTS_ONLY",
        "source_text_retained_in_output": False,
        "source_influence": "seed + topic hints; does not claim to understand prose",
        "authorization": "NONE",
    }


def logical_count(axes: dict[str, tuple[str, ...]] = AXES) -> int:
    return math.prod(len(x) for x in axes.values())


def encode_facets(facets: dict[str, str], axes: dict[str, tuple[str, ...]] = AXES) -> int:
    if set(facets) != set(axes):
        raise ValueError("facet dimensions do not match")
    rank = 0
    for name, values in axes.items():
        if facets[name] not in values:
            raise ValueError("facet value not in axis")
        rank = rank * len(values) + values.index(facets[name])
    return rank


def decode_rank(rank: int, axes: dict[str, tuple[str, ...]] = AXES) -> dict[str, str]:
    total = logical_count(axes)
    if type(rank) is not int or not 0 <= rank < total:
        raise ValueError("rank out of logical space")
    selected = {}
    for name, values in reversed(axes.items()):
        rank, offset = divmod(rank, len(values))
        selected[name] = values[offset]
    return {name: selected[name] for name in axes}


def sample_plan(parsed: dict[str, Any], seed: str = "0", axes: dict[str, tuple[str, ...]] = AXES) -> tuple[int, int, int]:
    if not isinstance(seed, str) or len(seed) > 512:
        raise ValueError("invalid seed")
    total = logical_count(axes)
    h = digest(canonical([SCHEMA, parsed["source_sha256"], seed, {k:len(v) for k,v in axes.items()}]))
    start = int(h[:32], 16) % total
    stride = int(h[32:], 16) % total or 1
    while math.gcd(stride, total) != 1:
        stride = (stride + 1) % total or 1
    return start, stride, total


def lane_for(facets: dict[str, str]) -> list[str]:
    result = []
    if facets["variation"] in ("INVERT", "NOT_ELSE", "CHALLENGE"):
        result.append("CHALLENGE")
    if facets["variation"] == "REPLAY" or facets["time_frame"] == "HISTORICAL_REPLAY":
        result.append("REPLAY")
    if facets["perspective"] == "ET_FICTIONAL" or facets["time_frame"] == "COUNTERFACTUAL_TIME":
        result.append("WEIRD")
    if facets["fault_mode"] != "NONE":
        result.append("FAULT")
    if facets["variation"] in ("ELSE", "BETTER"):
        result.append("EXPLORATION")
    return [lane for lane in LANES if lane in result]


def candidate(parsed: dict[str, Any], rank: int) -> dict[str, Any]:
    facets = decode_rank(rank)
    identity = fingerprint({"schema": SCHEMA, "source": parsed["source_sha256"], "facets": facets})
    is_fictional = facets["perspective"] == "ET_FICTIONAL"
    hypoth = (
        f"Could {facets['variation']} change {facets['experiment_family']} "
        f"under {facets['time_frame']} without degrading {facets['measurement']} "
        f"against a pinned baseline?"
    )
    return {
        "experiment_descriptor_id": "codoodle:" + identity,
        "source_sha256": parsed["source_sha256"],
        "filtered_rank": rank,
        "facets": facets,
        "lanes": lane_for(facets),
        "hypothesis_template": hypoth,
        "test_method_candidate": "PIN_BASELINE_THEN_COMPARE__NOT_YET_RUN",
        "epistemic_class": "FICTIONAL_VIEWPOINT" if is_fictional else "SYNTHETIC_CANDIDATE",
        "time_semantics": "LOGICAL_ORDER_IS_NOT_TIMELESS_PHYSICS",
        "scientific_claim_status": "UNVERIFIED",
        "estimated_benefits": None,
        "estimated_penalties": None,
        "novelty": "UNKNOWN",
        "receiver": None,
        "authority": "NONE",
        "external_effects": 0,
        "state": "DESCRIPTOR_ONLY__NOT_EXECUTED",
    }


def validate_candidate(c: dict[str, Any], expected_source: str) -> list[str]:
    problems = []
    try:
        facets = c["facets"]
        if facets not in (decode_rank(c["filtered_rank"]),):
            problems.append("RANK_FACET_MISMATCH")
        if c.get("source_sha256") != expected_source:
            problems.append("SOURCE_BINDING_MISMATCH")
        if c.get("authority") != "NONE" or c.get("external_effects") != 0:
            problems.append("EFFECT_AUTHORITY_ESCALATION")
        if c.get("state") != "DESCRIPTOR_ONLY__NOT_EXECUTED":
            problems.append("FALSE_EXECUTION_STATUS")
        if c.get("scientific_claim_status") != "UNVERIFIED":
            problems.append("UNJUSTIFIED_SCIENCE_CLAIM")
        if facets["perspective"] == "ET_FICTIONAL" and c.get("epistemic_class") != "FICTIONAL_VIEWPOINT":
            problems.append("FICTION_PRESENTED_AS_FACT")
        if c.get("time_semantics") != "LOGICAL_ORDER_IS_NOT_TIMELESS_PHYSICS":
            problems.append("TIME_ONTOLOGY_CLAIM")
        if set(c.get("lanes", [])) != set(lane_for(facets)):
            problems.append("LANE_MISMATCH")
        if any(x not in LANES for x in c.get("lanes", [])):
            problems.append("UNSUPPORTED_LANE")
        baseline_id = "codoodle:" + fingerprint({"schema": SCHEMA, "source": expected_source, "facets": facets})
        if c.get("experiment_descriptor_id") != baseline_id:
            problems.append("DESCRIPTOR_ID_MISMATCH")
    except (KeyError, TypeError, ValueError):
        problems.append("STRUCTURE_INVALID")
    return problems


def make_preview(parsed: dict[str, Any], limit: int = 24, seed: str = "0") -> dict[str, Any]:
    if type(limit) is not int or not 1 <= limit <= MAX_SAMPLE:
        raise ValueError("limit must be 1..256")
    # 3/4 source-topic guided + 1/4 open unusual/counterfactual paths.
    # Heuristics are neither comprehension nor relevance certification.
    hints = tuple(x for x in AXES["experiment_family"] if x in parsed["topics_hint_only"])
    focused_axes = {k: (hints if k == "experiment_family" and hints else v)
                    for k, v in AXES.items()}
    focused_target = (limit * 3 + 3) // 4 if hints else 0
    sample = []
    sampled_ids = set()
    bucket_counts = {"SOURCE_TOPIC_HINTS": 0, "OPEN_ELSE_SPACE": 0}
    strategy = []
    for bucket, axes, count in (
        ("SOURCE_TOPIC_HINTS", focused_axes, focused_target),
        ("OPEN_ELSE_SPACE", AXES, limit-focused_target),
    ):
        if not count:
            continue
        start, stride, total = sample_plan(parsed, seed + ":" + bucket, axes)
        strategy.append({"lane": bucket, "logical_space": total, "start": start, "stride": stride})
        for i in range(min(total, count * 8)):
            if bucket_counts[bucket] >= count:
                break
            rank = encode_facets(decode_rank((start+i*stride) % total, axes))
            c = candidate(parsed, rank)
            if c["experiment_descriptor_id"] in sampled_ids:
                continue
            if validate_candidate(c, parsed["source_sha256"]):
                raise AssertionError("internal static validation failed")
            c["sampling_bucket"] = bucket
            sample.append(c)
            sampled_ids.add(c["experiment_descriptor_id"])
            bucket_counts[bucket] += 1
    if len(sample) != limit:
        raise ValueError("sampling failed to fill bounded requested limit")
    return {
        "schema": SCHEMA,
        "source": parsed,
        "state": "SOURCE_BOUND_DESCRIPTOR_PREVIEW__NO_EXPERIMENT_EXECUTION",
        "logical_descriptor_count": logical_count(),
        "logical_count_is_candidate_addresses_only": True,
        "sample_count": len(sample),
        "sample_strategy": "SHA256_SEEDED_COPRIME_STRIDE_IN_FOCUSED_AND_OPEN_SPACES",
        "sample_buckets": bucket_counts,
        "sampling_lanes": strategy,
        "seed": seed,
        "sample": sample,
        "selector_handoff": {
            "schema_hint": "CoExperimentSelectorInputR0",
            "state": "HELD_UNSCORED",
            "reason": "CoExperimentSelector requires evidence-backed benefit/penalty estimates; parser MUST NOT fabricate them",
            "lanes": list(LANES),
        },
        "effects": {"workers_started": 0, "provider_sessions_created": 0,
                    "remote_requests": 0, "device_events": 0, "external_mutations": 0},
        "nonclaims": ["DESCRIPTOR_NE_EXPERIMENT", "FICTION_NE_ET_CONTACT",
                      "SPECULATION_NE_PHYSICS", "LOGICAL_TIME_NE_TIMELESS_PHYSICS",
                      "MICROKERNEL_SPEED_NE_TOOL_OR_MODEL_SPEED", "SOURCE_HASH_NE_SOURCE_AUTHENTICITY",
                      "RANDOM_SAMPLE_NE_HYPOTHESIS_QUALITY", "LOCAL_PREVIEW_NE_DEVICE_CONTROL"],
    }


def static_microcanary(preview: dict[str, Any]) -> dict[str, Any]:
    """Actually execute only immutable offline structural checks, not experiments."""
    sample = preview["sample"]
    source = preview["source"]["source_sha256"]
    checks = []
    def check(name: str, ok: bool) -> None:
        checks.append({"test": name, "status": "PASS" if ok else "FAIL"})
    check("all_descriptors_bind_same_source", all(c["source_sha256"] == source for c in sample))
    check("sample_has_no_collisions", len({c["experiment_descriptor_id"] for c in sample}) == len(sample))
    check("same_source_is_used_across_projection_views", all(
        c["source_sha256"] == source for c in sample if c["facets"]["projection"] in ("TEXT", "ORB", "MAP")))
    check("zero_side_effect_descriptors", all(c["external_effects"] == 0 and c["authority"] == "NONE" for c in sample))
    check("never_promotes_speculation_to_evidence", all(c["scientific_claim_status"] == "UNVERIFIED" for c in sample))
    check("fiction_is_labelled", all(c["epistemic_class"] == "FICTIONAL_VIEWPOINT" for c in sample if c["facets"]["perspective"] == "ET_FICTIONAL"))
    check("generated_candidates_static_validate", all(not validate_candidate(c, source) for c in sample))
    if sample:
        mutant = dict(sample[0]); mutant["authority"] = "UNLIMITED"
        check("negative_authority_mutant_rejected", "EFFECT_AUTHORITY_ESCALATION" in validate_candidate(mutant, source))
        mutant2 = dict(sample[0]); mutant2["source_sha256"] = "0"*64
        check("negative_source_mutant_rejected", "SOURCE_BINDING_MISMATCH" in validate_candidate(mutant2, source))
        mutant3 = dict(sample[0]); mutant3["scientific_claim_status"] = "CONFIRMED"
        check("negative_science_mutant_rejected", "UNJUSTIFIED_SCIENCE_CLAIM" in validate_candidate(mutant3, source))
        mutant4 = dict(sample[0]); mutant4["state"] = "RUNNING"
        check("negative_false_execution_rejected", "FALSE_EXECUTION_STATUS" in validate_candidate(mutant4, source))
    return {
        "schema": "CoAll.CoDoodle.StaticMicroCanary.R0",
        "test_class": "ACTUALLY_EXECUTED_LOCAL_STATIC_CHECKS",
        "checks": checks,
        "passed": sum(x["status"] == "PASS" for x in checks),
        "failed": sum(x["status"] == "FAIL" for x in checks),
        "promotions": 0,
        "external_experiments_executed": 0,
    }


def benchmark(parsed: dict[str, Any], iterations: int = 100_000, batches: int = 20) -> dict[str, Any]:
    """Amortized timing; overhead of Python loops/decoding, not IO or external work."""
    if type(iterations) is not int or not 100 <= iterations <= MAX_BENCH_ITERATIONS:
        raise ValueError("iterations must be 100..200000")
    if type(batches) is not int or not 3 <= batches <= 40:
        raise ValueError("batches must be 3..40")
    start, stride, total = sample_plan(parsed, seed="perf-fixture")
    warm = 3000
    guard = 0
    for i in range(warm):
        guard ^= len(decode_rank((start+i*stride) % total))
    per_batch = max(1, iterations // batches)
    pointer_durations = []
    for b in range(batches):
        t0 = time.perf_counter_ns()
        for j in range(per_batch):
            rank = (start + (b*per_batch+j)*stride) % total
            guard ^= rank & 7
        pointer_durations.append((time.perf_counter_ns()-t0)/per_batch)
    durations = []
    ids_processed = 0
    first = time.perf_counter_ns()
    for b in range(batches):
        t0 = time.perf_counter_ns()
        for j in range(per_batch):
            rank = (start + (b*per_batch+j)*stride) % total
            facets = decode_rank(rank)
            guard ^= len(facets["variation"])
        dt = time.perf_counter_ns() - t0
        durations.append(dt/per_batch)
        ids_processed += per_batch
    elapsed = time.perf_counter_ns() - first
    ordered = sorted(durations)
    ordered_pointer = sorted(pointer_durations)
    p95 = ordered[min(len(ordered)-1, math.ceil(0.95*len(ordered))-1)]
    preview_times = []
    for i in range(20):
        t0 = time.perf_counter_ns()
        value = make_preview(parsed, limit=24, seed=str(i))
        guard ^= len(value["sample"])
        preview_times.append(time.perf_counter_ns()-t0)
    return {
        "schema": "CoAll.CoDoodle.BenchmarkR0",
        "timer": "time.perf_counter_ns",
        "scope": "single Python process on shared container; no realtime scheduling or device hook",
        "measured_work": "mixed_radix_decode_plus_loop_plus_simple_string_access",
        "observations": ids_processed,
        "batches": batches,
        "address_only_amortized_batch_p50_us": round(statistics.median(pointer_durations)/1000, 4),
        "address_only_amortized_batch_p95_us": round(ordered_pointer[math.ceil(0.95*batches)-1]/1000, 4),
        "address_only_is_not_a_descriptor": True,
        "microkernel_amortized_mean_us": round(sum(durations)/len(durations)/1000, 4),
        "microkernel_amortized_batch_p50_us": round(statistics.median(durations)/1000, 4),
        "microkernel_amortized_batch_p95_us": round(p95/1000, 4),
        "microkernel_wall_total_ms": round(elapsed/1_000_000, 2),
        "descriptors_per_second_mixed_radix": round(ids_processed/(elapsed/1e9)),
        "complete_24_descriptor_preview_median_ms": round(statistics.median(preview_times)/1_000_000, 4),
        "complete_24_descriptor_preview_p95_ms": round(sorted(preview_times)[18]/1_000_000, 4),
        "guard": guard,
        "external_experiments": 0,
        "caution": "Batch measurements are amortized; individual latency tails, input parsing, IO, hashing, selectors, model calls and tests are not microsecond-certified",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--text-file", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=24)
    ap.add_argument("--seed", default="doodle-0")
    ap.add_argument("--bench", action="store_true")
    args = ap.parse_args()
    try:
        source = args.text_file.read_bytes()
        parsed = parse_doodle(source)
        preview = make_preview(parsed, limit=args.limit, seed=args.seed)
        canary = static_microcanary(preview)
        if canary["failed"]:
            raise ValueError("failed static micro-canary; no output promoted")
        b = benchmark(parsed) if args.bench else None
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out/"preview.json").write_text(json.dumps(
            preview, indent=2, ensure_ascii=True)+"\n", encoding="utf-8")
        (args.out/"candidates.jsonl").write_text("".join(json.dumps(
            item, sort_keys=True, ensure_ascii=True)+"\n" for item in preview["sample"]), encoding="utf-8")
        (args.out/"static_microcanary.json").write_text(json.dumps(canary, indent=2)+"\n", encoding="utf-8")
        if b is not None:
            (args.out/"benchmark.json").write_text(json.dumps(b, indent=2)+"\n", encoding="utf-8")
        print(json.dumps({"status":"DESCRIPTORS_GENERATED_LOCAL_ONLY",
              "source_sha256": parsed["source_sha256"], "logical_descriptors":preview["logical_descriptor_count"],
              "sample_count":len(preview["sample"]), "static_pass":canary["passed"],
              "static_fail":canary["failed"], "benchmark": b}, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        ap.exit(2, f"HELD: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
