#!/usr/bin/env python3
"""Deterministic virtual-address sampler: zero live experiments, zero network."""
import argparse
import hashlib
import json

DIMENSIONS = 10
CHOICES = 16
MAX_SAMPLE = 1024


def sample(count=20, seed="CoStretch-R5-public"):
    if type(count) is not int or not 1 <= count <= MAX_SAMPLE:
        raise ValueError("representative sampling exceeds bounded cap")
    space = CHOICES ** DIMENSIONS
    ranks = []
    seen = set()
    counter = 0
    while len(ranks) < count:
        digest = hashlib.sha256((seed + ":" + str(counter)).encode("utf-8")).digest()
        rank = int.from_bytes(digest, "big") % space
        counter += 1
        if rank not in seen:
            seen.add(rank)
            ranks.append(rank)
    address_hash = hashlib.sha256(json.dumps(ranks, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"logical_address_space": str(space), "representatives_examined": len(ranks), "rank_sample_sha256": address_hash,
            "actual_workers": 0, "model_calls": 0, "external_effects": 0, "enumerated_all_options": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(sample(args.sample), sort_keys=True))