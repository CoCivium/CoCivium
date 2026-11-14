#!/usr/bin/env python3
"""Bounded synthetic comparison: exhaustive joins, factorized joins, and source-delta repair.

Pure standard library. No device, model, provider, mail, network, account, or process effects.
Only PUBLIC synthetic candidate projections are generated. Proposal != authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "CoAll.CoMixFactorBench.R0"
LENSES = ("EMPIRICAL", "FAITH", "PHILOSOPHY", "CULTURE", "FUTURE")
EVIDENCE = ("OBSERVED", "TESTABLE", "BELIEF", "INTERPRETIVE", "SPECULATIVE", "UNKNOWN")
MEDIA = ("TEXT", "MAP", "AUDIO", "PROTOTYPE")
TIMES = ("HISTORY", "CURRENT", "FORECAST")
PRIVACY = ("PUBLIC", "PRIVATE", "WITHHELD")
ACTIONS = ("PREVIEW", "CHALLENGE", "PUBLISH")
ALLOWED_EVIDENCE = {
    "EMPIRICAL": ("OBSERVED", "TESTABLE", "UNKNOWN"),
    "FAITH": ("BELIEF", "INTERPRETIVE", "UNKNOWN"),
    "PHILOSOPHY": ("TESTABLE", "INTERPRETIVE", "UNKNOWN"),
    "CULTURE": ("INTERPRETIVE", "SPECULATIVE", "UNKNOWN"),
    "FUTURE": ("TESTABLE", "SPECULATIVE", "UNKNOWN"),
}

@dataclass(frozen=True)
class Receiver:
    rid: str
    chosen_lenses: tuple[str, ...]
    supported_media: tuple[str, ...]

# Voluntary self-selected interests on PUBLIC SYNTHETIC fixtures, not inferred traits.
RECEIVERS = (
    Receiver("R01", ("EMPIRICAL", "PHILOSOPHY"), ("TEXT", "MAP")),
    Receiver("R02", ("FAITH", "CULTURE"), ("TEXT", "AUDIO")),
    Receiver("R03", ("EMPIRICAL", "FUTURE"), ("MAP", "PROTOTYPE")),
    Receiver("R04", ("PHILOSOPHY", "FUTURE"), ("TEXT", "PROTOTYPE")),
    Receiver("R05", ("FAITH", "PHILOSOPHY"), ("TEXT", "MAP")),
    Receiver("R06", ("CULTURE", "FUTURE"), ("AUDIO", "TEXT")),
    Receiver("R07", ("EMPIRICAL", "CULTURE"), ("MAP", "AUDIO")),
    Receiver("R08", ("PHILOSOPHY", "CULTURE"), ("TEXT", "AUDIO")),
)

PROJECTION_ACTIONS = ("PREVIEW", "CHALLENGE")  # CHALLENGE is local, UNSENT.


def sources(n: int, mutate_index: int | None = None) -> list[tuple[str, str]]:
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 48:
        raise ValueError("HOLD_SOURCE_COUNT_1_TO_48")
    if mutate_index is not None and (isinstance(mutate_index, bool) or not 0 <= mutate_index < n):
        raise ValueError("HOLD_MUTATION_INDEX")
    return [(f"S{i:03}", "v2" if mutate_index == i else "v1") for i in range(n)]


def admissible(receiver: Receiver, lens: str, evidence: str, medium: str,
               temporal: str, privacy: str, action: str) -> bool:
    if lens not in receiver.chosen_lenses:
        return False
    if evidence not in ALLOWED_EVIDENCE[lens]:
        return False
    if medium not in receiver.supported_media:
        return False
    if medium == "PROTOTYPE" and not (evidence == "TESTABLE" and lens in ("EMPIRICAL", "FUTURE")):
        return False
    if temporal == "FORECAST" and evidence == "OBSERVED":
        return False
    if privacy != "PUBLIC" or action not in PROJECTION_ACTIONS:
        return False
    return True


def exhaustive(source_list: list[tuple[str, str]]) -> list[tuple[str, ...]]:
    """Literal Cartesian baseline with qualification after tuple creation."""
    result: list[tuple[str, ...]] = []
    for (source_id, version), rec, lens, ev, media, temp, privacy, action in itertools.product(
            source_list, RECEIVERS, LENSES, EVIDENCE, MEDIA, TIMES, PRIVACY, ACTIONS):
        if admissible(rec, lens, ev, media, temp, privacy, action):
            result.append((source_id, version, rec.rid, lens, ev, media, temp, privacy, action))
    return result


def factorized(source_list: list[tuple[str, str]]) -> list[tuple[str, ...]]:
    """Push epistemic, consent, medium and action constraints before the join."""
    result: list[tuple[str, ...]] = []
    for source_id, version in source_list:
        for rec in RECEIVERS:
            for lens in rec.chosen_lenses:
                for ev in ALLOWED_EVIDENCE[lens]:
                    for medium in rec.supported_media:
                        if medium == "PROTOTYPE" and not (ev == "TESTABLE" and lens in ("EMPIRICAL", "FUTURE")):
                            continue
                        for temp in TIMES:
                            if temp == "FORECAST" and ev == "OBSERVED":
                                continue
                            for action in PROJECTION_ACTIONS:
                                # Public-only synthetic proposals. No permission upgrades.
                                result.append((source_id, version, rec.rid, lens, ev,
                                               medium, temp, "PUBLIC", action))
    return result


def manifest_hash(rows: list[tuple[str, ...]]) -> str:
    h = hashlib.sha256()
    for row in sorted(rows):
        h.update((json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8"))
    return h.hexdigest()


def indexed(source_list: list[tuple[str, str]]) -> dict[str, list[tuple[str, ...]]]:
    return {sid: factorized([(sid, version)]) for sid, version in source_list}


def incremental(index: dict[str, list[tuple[str, ...]]], sid: str, version: str):
    if sid not in index or version not in ("v1", "v2"):
        raise ValueError("HOLD_UNKNOWN_OR_UNQUALIFIED_DELTA")
    updated = dict(index)  # Copy-on-write; other exact source projections remain unmodified.
    updated[sid] = factorized([(sid, version)])
    return updated


def flatten(index: dict[str, list[tuple[str, ...]]]):
    return list(itertools.chain.from_iterable(index.values()))


def milliseconds(fn, repeat: int) -> dict[str, float | int]:
    durations = []
    count = -1
    for _ in range(repeat):
        start = time.perf_counter_ns()
        result = fn()
        durations.append((time.perf_counter_ns() - start) / 1_000_000)
        count = len(result)
    return {"median_ms": round(statistics.median(durations), 4),
            "p95_ms": round(sorted(durations)[math.ceil(0.95 * repeat) - 1], 4),
            "repetitions": repeat, "result_length": count}


def bench(sizes=(4, 16, 48), repeat=5) -> dict:
    if not 3 <= repeat <= 11 or isinstance(repeat, bool):
        raise ValueError("HOLD_REPETITIONS_3_TO_11")
    records = []
    for n in sizes:
        src = sources(n)
        base = exhaustive(src)
        fast = factorized(src)
        if len(base) != len(fast) or manifest_hash(base) != manifest_hash(fast):
            raise AssertionError("FAIL_EQUIVALENT_FULL_JOIN")
        if any(row[-2] != "PUBLIC" or row[-1] == "PUBLISH" for row in fast):
            raise AssertionError("FAIL_UNAUTHORIZED_OUTPUT")
        exhaustive_run = milliseconds(lambda: exhaustive(src), repeat)
        factor_run = milliseconds(lambda: factorized(src), repeat)
        change_i = n // 2
        sid = src[change_i][0]
        old_idx = indexed(src)
        next_src = sources(n, mutate_index=change_i)
        full_next = factorized(next_src)
        next_idx = incremental(old_idx, sid, "v2")
        if manifest_hash(flatten(next_idx)) != manifest_hash(full_next):
            raise AssertionError("FAIL_INCREMENTAL_PARITY")
        for old_sid in old_idx:
            if old_sid != sid and old_idx[old_sid] is not next_idx[old_sid]:
                raise AssertionError("FAIL_IDENTITY_PRESERVATION")
        if any(row[1] != "v2" for row in next_idx[sid]):
            raise AssertionError("FAIL_DELTA_VERSION")
        full_rebuild_run = milliseconds(lambda: factorized(next_src), repeat)
        delta_run = milliseconds(lambda: incremental(old_idx, sid, "v2"), repeat)
        # For downstream consumers, source-index swap costs are benchmarked;
        # materializing *the entire* result is deliberately not timed for delta refresh.
        records.append({
            "source_count": n,
            "syntactic_cartesian_count": n * len(RECEIVERS) * len(LENSES) * len(EVIDENCE) * len(MEDIA) * len(TIMES) * len(PRIVACY) * len(ACTIONS),
            "qualified_public_projection_count": len(fast),
            "source_fingerprint": manifest_hash(fast),
            "exhaustive": exhaustive_run,
            "constraint_first": factor_run,
            "same_output_full_join": True,
            "constraint_first_median_speedup": round(exhaustive_run["median_ms"] / max(factor_run["median_ms"], 1e-8), 2),
            "full_source_update_rebuild": full_rebuild_run,
            "incremental_index_update": delta_run,
            "delta_median_speedup_for_index_maintenance": round(full_rebuild_run["median_ms"] / max(delta_run["median_ms"], 1e-8), 2),
            "source_changed": sid,
            "changed_source_projection_count": len(next_idx[sid]),
            "unaffected_source_partitions_retained": n - 1,
            "same_output_after_delta_when_flattened": True,
        })
    return {
        "schema": SCHEMA,
        "state": "LOCAL_SYNTHETIC_BENCHMARK_ONLY",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "design": {"source_scope": "PUBLIC_SYNTHETIC", "authority": "NONE", "receiver_interest": "DECLARED_FIXTURE_ONLY",
                   "external_effects": 0, "active_workers": 0, "network_calls": 0,
                   "comparison": ["exhaustive_qualified_cartesian", "constraint_first_factorized", "one_source_delta_copy_on_write"],
                   "outcome": "STRUCTURAL_OUTPUT_EQUIVALENCE_NOT_USEFUL_HUMAN_RESULTS"},
        "runs": records,
        "nonclaims": ["LOGICAL_COMBINATIONS_NE_MATERIALIZED_WORKERS", "LATENCY_BENCH_NE_RECEIVER_BENEFIT",
                      "ONE_SOURCE_DELTA_NE_GLOBAL_CURRENTNESS", "INDEX_SWAP_NE_DURABLE_RECEIVER_ACK",
                      "PRIVATE_HELD_NE_CONSENT", "INTERPRETATION_NE_EMPIRICAL_PROOF", "READ_ONLY_NE_PUBLIC_SEND",
                      "LOCAL_CONTAINER_NE_X2_RUNTIME", "NO_LIVE_GLOBAL_BUS", "NO_COEX_OR_CANON"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = bench(repeat=args.repeat)
    data = (json.dumps(result, sort_keys=True, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    if args.output:
        with args.output.open("xb") as fh:
            fh.write(data)
        if args.output.read_bytes() != data:
            raise RuntimeError("FAIL_OUTPUT_READBACK")
        print("PASS_EXCLUSIVE_OUTPUT", args.output, hashlib.sha256(data).hexdigest())
    else:
        sys.stdout.buffer.write(data)


if __name__ == "__main__":
    main()
