#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/coquestion_reservoir_r0h.json")
FRONTIER = Path("fixtures/relations/coquestion_frontier_r0c.json")
SPACE = Path("fixtures/relations/coquestion_space_compiler_r0g.json")
COMPILER = Path("fixtures/relations/coinquiry_compiler_r0f.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    space = json.loads(SPACE.read_text(encoding="utf-8"))
    compiler = json.loads(COMPILER.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    for path_key, sha_key in [
        ("question_frontier_path", "question_frontier_blob_sha"),
        ("question_space_path", "question_space_blob_sha"),
        ("inquiry_compiler_path", "inquiry_compiler_blob_sha")
    ]:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    base_ids = sorted({qid for ids in frontier["categories"].values() for qid in ids})
    if len(base_ids) != frontier["question_count"]:
        fail("FAIL_FRONTIER_CORE_COUNT")
    if len(base_ids) != d["reservoir_contract"]["base_semantic_core_count"]:
        fail("FAIL_RESERVOIR_BASE_COUNT")
    if space["expected_raw_candidates"] != 10000:
        fail("FAIL_SOURCE_SPACE_SCALE")
    if compiler["expected"]["runtime_effect"] is not False:
        fail("FAIL_SOURCE_COMPILER_RUNTIME_EFFECT")

    ops = d["axes"]["transform_operators"]
    receivers = d["axes"]["receiver_contexts"]
    horizons = d["axes"]["time_horizons"]
    if len(ops) != len(set(ops)) or len(receivers) != len(set(receivers)) or len(horizons) != len(set(horizons)):
        fail("FAIL_DUPLICATE_AXIS_VALUE")

    ids = []
    samples = []
    transformed_cores = set()
    contract = d["reservoir_contract"]
    shard_sizes = [0] * contract["shard_count"]

    index = 0
    for seed in base_ids:
        for op in ops:
            transformed_cores.add((seed, op))
            for receiver in receivers:
                for horizon in horizons:
                    pid = f"Q{seed:02d}|{op}|{receiver}|{horizon}"
                    ids.append(pid)
                    shard_id = index // contract["expected_projection_count_per_shard"]
                    if shard_id >= len(shard_sizes):
                        fail("FAIL_SHARD_OVERFLOW")
                    shard_sizes[shard_id] += 1
                    if len(samples) < 10 or index in {999, 4999, 9999}:
                        samples.append({
                            "projection_id": pid,
                            "seed_question_id": seed,
                            "operator": op,
                            "receiver_context": receiver,
                            "time_horizon": horizon,
                            "shard_id": shard_id
                        })
                    index += 1

    expected = d["expected"]
    if len(ids) != expected["projection_count"]:
        fail("FAIL_PROJECTION_COUNT")
    if len(set(ids)) != expected["unique_projection_id_count"]:
        fail("FAIL_UNIQUE_PROJECTION_COUNT")
    if len(transformed_cores) != expected["transformed_core_count"]:
        fail("FAIL_TRANSFORMED_CORE_COUNT")
    if min(shard_sizes) != expected["min_shard_size"] or max(shard_sizes) != expected["max_shard_size"]:
        fail("FAIL_SHARD_SIZE")
    if len(shard_sizes) != expected["shard_count"]:
        fail("FAIL_SHARD_COUNT")

    product = (
        contract["base_semantic_core_count"]
        * contract["transform_operator_count"]
        * contract["receiver_context_count"]
        * contract["time_horizon_count"]
    )
    if product != contract["expected_projection_count"]:
        fail("FAIL_AXIS_PRODUCT")
    if contract["durable_full_projection_materialization_default"] is not False:
        fail("FAIL_MATERIALIZATION_DEFAULT")
    if contract["default_per_wave_materialization_budget"] > 64:
        fail("FAIL_WAVE_BUDGET")

    projection_digest = hashlib.sha256(
        ("\n".join(ids) + "\n").encode("utf-8")
    ).hexdigest().upper()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COQUESTION_RESERVOIR_R0H",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "base_semantic_core_count": len(base_ids),
        "transformed_core_count": len(transformed_cores),
        "projection_count": len(ids),
        "unique_projection_id_count": len(set(ids)),
        "projection_set_sha256": projection_digest,
        "shard_count": len(shard_sizes),
        "min_shard_size": min(shard_sizes),
        "max_shard_size": max(shard_sizes),
        "durable_full_projection_object_count": 0,
        "default_per_wave_materialization_budget": contract["default_per_wave_materialization_budget"],
        "sample_projections": samples,
        "runtime_effect": False,
        "public_effect": False,
        "rails": d["rails"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
