#!/usr/bin/env python3
"""Replay pinned public historical CoEvoDelta records against PatternGate R0.

Read-only schema/field-availability audit. Does NOT infer currentness, fill absent
metadata, observe a receiver, or use model reasoning to reinterpret historical
claims. No network requests, repository writes, or authorized side effects.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from CoEvoPatternTransitionR0 import evaluate


MANIFEST = "ai/pattern-gate/historical-public-replay-r0.json"
ALLOWED_PREFIX = "ai/evolution-deltas/"
REQUIRED_SOURCE_FIELDS = ("delta_id", "source_refs", "confidentiality", "epistemic_class")
REQUIRED_PATTERN_FIELDS = (
    "materiality", "currentness", "pattern_kind", "claim",
    "effect_classes", "authority_ceiling", "receiver_class",
    "bounded_test", "wake_condition", "expiry_condition",
    "counterexamples",
)


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def replay(repo):
    root = Path(repo).resolve()
    manifest_bytes = (root / MANIFEST).read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest["schema"] == "CoEvo.PatternHistoricalReplayManifest.R0.v0.1"
    seen = set()
    rows = []
    for entry in manifest["records"]:
        rel = entry["path"]
        path = (root / rel).resolve()
        assert path.is_relative_to(root), "PATH_ESCAPE"
        assert rel.startswith(ALLOWED_PREFIX) and rel.endswith(".json"), "NOT_EVOLUTION_DELTA"
        assert rel not in seen, "DUPLICATE_SOURCE"
        seen.add(rel)
        data = path.read_bytes()
        sha = git_blob_sha(data)
        assert sha == entry["blob_sha"], (rel, "SOURCE_BLOB_DRIFT", sha)
        original = json.loads(data)
        assert isinstance(original, dict)
        assert original.get("confidentiality") == "PUBLIC", "NOT_PUBLIC_SAFE"
        assert isinstance(original.get("delta_id"), str) and original["delta_id"]
        assert isinstance(original.get("source_refs"), list) and original["source_refs"]
        assert isinstance(original.get("epistemic_class"), str)
        # Do not assign newly invented classification, tests, currentness or actor permissions.
        # This audits the actual fields provided by these historical records.
        missing = [key for key in REQUIRED_PATTERN_FIELDS if key not in original]
        decision = evaluate(original)
        assert decision["effects_performed"] == 0
        assert decision["receiver_ack"] == "UNPROVEN"
        assert decision["authority_granted"] is False
        assert decision["disposition"] != "REVIEW_SHADOW_ONLY", "HISTORICAL_QUALIFIED_WITHOUT_EVIDENCE"
        assert decision["disposition"] != "CHALLENGE_READ_ONLY", "UNQUALIFIED_CONFLICT_ROUTING"
        rows.append({
            "path": rel,
            "blob_sha": sha,
            "delta_id": original["delta_id"],
            "epistemic_class": original["epistemic_class"],
            "historical_schema_fields_present": all(key in original for key in REQUIRED_SOURCE_FIELDS),
            "missing_pattern_fields": missing,
            "disposition": decision["disposition"],
            "reason": decision["reason"],
            "effects_performed": 0,
            "receiver_readproof": "UNPROVEN",
        })
    assert len(rows) == 7
    counts = Counter(row["disposition"] for row in rows)
    assert not counts.get("REVIEW_SHADOW_ONLY")
    assert all("currentness" in row["missing_pattern_fields"] for row in rows)
    return {
        "schema": "CoEvo.PatternHistoricalReplayReport.R0",
        "scope": "PINNED_PUBLIC_HISTORICAL_SOURCE_RECORDS_ONLY",
        "source_blob_count": len(rows),
        "manifest_git_blob_sha": git_blob_sha(manifest_bytes),
        "dispositions": dict(sorted(counts.items())),
        "receiver_useful_closures": "UNKNOWN",
        "no_gate_baseline": "NOT_MEASURED; historical schema-ready is not actual qualified benefit",
        "live_currentness": "UNKNOWN",
        "runtime": "NOT_TESTED",
        "effects_performed": 0,
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    print(json.dumps(replay(args.repo_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
